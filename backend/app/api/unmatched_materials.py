from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from loguru import logger

from app.core.database import get_db
from app.core.simple_auth import get_current_active_user, require_admin, SimpleUser
from app.schemas.unmatched_material import (
    UnmatchedMaterialCreate, UnmatchedMaterialUpdate, UnmatchedMaterialResponse,
    UnmatchedMaterialSearchRequest, UnmatchedMaterialImportRequest, UnmatchedMaterialImportResponse,
    UnmatchedMaterialBatchOperation
)
from app.services.unmatched_material import UnmatchedMaterialService, UnmatchedMaterialImportService
from app.utils.excel import ExcelProcessor

router = APIRouter()


@router.post("/", response_model=UnmatchedMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_unmatched_material(
    material_data: UnmatchedMaterialCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建无市场信息价材料"""
    material = await UnmatchedMaterialService.create_material(db, material_data)
    return UnmatchedMaterialResponse.model_validate(material)


@router.get("/")
async def get_unmatched_materials(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=2000, description="每页记录数"),
    name: Optional[str] = Query(None, description="材料名称搜索"),
    category: Optional[str] = Query(None, description="材料分类"),
    price_min: Optional[str] = Query(None, description="价格下限"),
    price_max: Optional[str] = Query(None, description="价格上限"),
    is_verified: Optional[bool] = Query(None, description="是否已验证"),
    db: AsyncSession = Depends(get_db)
):
    """获取无市场信息价材料列表"""
    # 处理价格参数转换
    price_min_float = None
    price_max_float = None

    if price_min and price_min.strip():
        try:
            price_min_float = float(price_min)
        except ValueError:
            pass

    if price_max and price_max.strip():
        try:
            price_max_float = float(price_max)
        except ValueError:
            pass

    search_params = UnmatchedMaterialSearchRequest(
        query=name,
        category=category,
        price_min=price_min_float,
        price_max=price_max_float,
        is_verified=is_verified
    )

    # 计算skip
    skip = (page - 1) * page_size

    materials = await UnmatchedMaterialService.get_materials(
        db, skip=skip, limit=page_size, search_params=search_params
    )

    # 获取总数
    total = await UnmatchedMaterialService.get_materials_count(db, search_params)

    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": [UnmatchedMaterialResponse.model_validate(material) for material in materials],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.post("/get-preview-data")
async def get_preview_data(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
    max_rows: Optional[int] = Form(2000)
):
    """获取Excel文件预览数据用于导入"""
    try:
        # 验证文件类型
        allowed_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'application/vnd.ms-excel', 'text/csv']
        if file.content_type not in allowed_types and not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传Excel或CSV文件"
            )

        # 验证文件大小 (50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小不能超过50MB"
            )

        # 获取预览数据
        excel_processor = ExcelProcessor()

        # 重置文件指针
        import io
        file_like = io.BytesIO(content)

        # 获取完整数据用于导入
        import_result = excel_processor.get_full_data_for_import(
            file_like, file.filename, sheet_name=sheet_name, max_preview_rows=100
        )

        # 清理不能JSON序列化的值
        def clean_for_json(obj):
            import numpy as np
            import pandas as pd
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, int)):
                return int(obj)
            elif isinstance(obj, (np.floating, float)):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            elif pd.isna(obj):
                return None
            else:
                return obj

        cleaned_result = clean_for_json(import_result)

        return {
            "code": 200,
            "message": f"数据获取成功，共{cleaned_result['totalRows']}行数据，预览{cleaned_result['previewRows']}行",
            "data": cleaned_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取预览数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预览数据失败: {str(e)}"
        )


@router.post("/parse-excel")
async def parse_excel_structure(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None)
):
    """解析Excel文件结构"""
    try:
        # 验证文件类型
        allowed_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'application/vnd.ms-excel', 'text/csv']
        if file.content_type not in allowed_types and not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传Excel或CSV文件"
            )

        # 验证文件大小 (50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小不能超过50MB"
            )

        # 解析文件结构
        excel_processor = ExcelProcessor()

        # 重置文件指针
        import io
        file_like = io.BytesIO(content)

        # 分析文件结构
        analysis_result = excel_processor.analyze_file_structure(file_like, file.filename, sheet_name=sheet_name)

        # 清理不能JSON序列化的值
        def clean_for_json(obj):
            import numpy as np
            import pandas as pd
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, int)):
                return int(obj)
            elif isinstance(obj, (np.floating, float)):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            elif pd.isna(obj):
                return None
            else:
                return obj

        cleaned_result = clean_for_json(analysis_result)

        return {
            "code": 200,
            "message": "文件解析成功",
            "data": cleaned_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Excel文件解析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件解析失败: {str(e)}"
        )


@router.post("/import-materials")
async def import_unmatched_materials(
    import_request: dict,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """导入无市场信息价材料数据"""
    try:
        materials_data = import_request.get('materials', [])
        import_options = import_request.get('import_options', {})

        if not materials_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有要导入的材料数据"
            )

        # 使用材料导入服务
        import_service = UnmatchedMaterialImportService()

        result = await import_service.import_structured_materials(
            db, materials_data, import_options
        )

        return {
            "code": 200,
            "message": "材料导入成功",
            "data": {
                "total_count": result["total_count"],
                "success_count": result["success_count"],
                "failed_count": result["failed_count"],
                "skipped_count": result["skipped_count"],
                "errors": result.get("errors", [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"无市场信息价材料导入失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"材料导入失败: {str(e)}"
        )


@router.get("/{material_id}", response_model=UnmatchedMaterialResponse)
async def get_unmatched_material(
    material_id: int,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取无市场信息价材料详情"""
    material = await UnmatchedMaterialService.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无市场信息价材料不存在"
        )
    return UnmatchedMaterialResponse.model_validate(material)


@router.put("/{material_id}", response_model=UnmatchedMaterialResponse)
async def update_unmatched_material(
    material_id: int,
    material_data: UnmatchedMaterialUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新无市场信息价材料"""
    material = await UnmatchedMaterialService.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无市场信息价材料不存在"
        )

    updated_material = await UnmatchedMaterialService.update_material(
        db, material, material_data
    )
    return UnmatchedMaterialResponse.model_validate(updated_material)


@router.delete("/{material_id}")
async def delete_unmatched_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除无市场信息价材料"""
    material = await UnmatchedMaterialService.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无市场信息价材料不存在"
        )

    success = await UnmatchedMaterialService.delete_material(db, material)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除无市场信息价材料失败"
        )

    return {"message": "无市场信息价材料删除成功"}


@router.post("/batch-operation")
async def batch_operation_materials(
    operation_data: UnmatchedMaterialBatchOperation,
    db: AsyncSession = Depends(get_db)
):
    """批量操作无市场信息价材料"""
    try:
        if operation_data.operation == "verify":
            count = await UnmatchedMaterialService.batch_verify_materials(
                db, operation_data.material_ids, True, operation_data.verification_notes
            )
            return {"message": f"成功验证 {count} 个材料"}

        elif operation_data.operation == "unverify":
            count = await UnmatchedMaterialService.batch_verify_materials(
                db, operation_data.material_ids, False, operation_data.verification_notes
            )
            return {"message": f"成功取消验证 {count} 个材料"}

        elif operation_data.operation == "delete":
            count = await UnmatchedMaterialService.batch_delete_materials(
                db, operation_data.material_ids
            )
            return {"message": f"成功删除 {count} 个材料"}

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的操作类型"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量操作失败: {str(e)}"
        )


@router.get("/categories/list")
async def get_material_categories(
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有材料分类"""
    categories = await UnmatchedMaterialService.get_categories(db)
    return {"categories": categories}


@router.get("/search-similar")
async def search_similar_materials(
    material_name: str = Query(..., description="材料名称"),
    specification: Optional[str] = Query(None, description="规格型号"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """搜索相似材料"""
    materials = await UnmatchedMaterialService.search_similar_materials(
        db, material_name, specification, limit
    )
    return [UnmatchedMaterialResponse.model_validate(material) for material in materials]
