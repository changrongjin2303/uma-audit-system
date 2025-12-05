from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from loguru import logger

from app.core.database import get_db
from app.core.simple_auth import get_current_active_user, require_admin, require_auditor, SimpleUser
from app.models.user import User
from app.schemas.material import (
    BaseMaterialCreate, BaseMaterialUpdate, BaseMaterialResponse,
    BaseMaterialSearchRequest, BaseMaterialImportRequest, BaseMaterialImportResponse,
    BaseMaterialBatchOperation, MaterialAliasCreate, MaterialAliasResponse,
    BaseMaterialPeriodDeleteRequest
)
from app.services.material import BaseMaterialService, MaterialImportService
from app.utils.excel import ExcelProcessor

router = APIRouter()


@router.post("/", response_model=BaseMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_base_material(
    material_data: BaseMaterialCreate,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """创建基准材料"""
    material = await BaseMaterialService.create_material(db, material_data)
    return BaseMaterialResponse.model_validate(material)


@router.get("/")
async def get_base_materials(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=2000, description="每页记录数"),
    name: Optional[str] = Query(None, description="材料名称搜索"),
    specification: Optional[str] = Query(None, description="规格型号搜索"),
    category: Optional[str] = Query(None, description="材料分类"),
    region: Optional[str] = Query(None, description="适用地区"),
    price_min: Optional[str] = Query(None, description="价格下限"),
    price_max: Optional[str] = Query(None, description="价格上限"),
    is_verified: Optional[bool] = Query(None, description="是否已验证"),
    # 新增信息价类型相关筛选参数
    price_type: Optional[str] = Query(None, description="信息价类型 (provincial/municipal)"),
    price_date: Optional[str] = Query(None, description="信息价期数 (YYYY-MM)"),
    price_source: Optional[str] = Query(None, description="信息价来源"),
    # 暂时移除认证要求，方便调试
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取基准材料列表"""
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
    
    search_params = BaseMaterialSearchRequest(
        query=name,  # 使用name参数
        specification=specification,
        category=category,
        region=region,
        price_min=price_min_float,
        price_max=price_max_float,
        is_verified=is_verified,
        price_type=price_type,
        price_date=price_date,
        price_source=price_source
    )
    
    # 计算skip
    skip = (page - 1) * page_size
    
    materials = await BaseMaterialService.get_materials(
        db, skip=skip, limit=page_size, search_params=search_params
    )
    
    # 获取总数
    total = await BaseMaterialService.get_materials_count(db, search_params)
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": [BaseMaterialResponse.model_validate(material) for material in materials],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/count")
async def get_base_materials_count(
    query: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="材料分类"),
    region: Optional[str] = Query(None, description="适用地区"),
    price_min: Optional[float] = Query(None, ge=0, description="价格下限"),
    price_max: Optional[float] = Query(None, ge=0, description="价格上限"),
    is_verified: Optional[bool] = Query(None, description="是否已验证"),
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取基准材料总数"""
    search_params = BaseMaterialSearchRequest(
        query=query,
        category=category,
        region=region,
        price_min=price_min,
        price_max=price_max,
        is_verified=is_verified
    )
    
    count = await BaseMaterialService.get_materials_count(db, search_params)
    return {"total": count}


@router.get("/template")
async def download_base_material_template(
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """下载基准材料Excel模板"""
    from fastapi.responses import FileResponse
    from app.utils.template_generator import MaterialTemplateGenerator
    
    try:
        # 生成模板文件
        generator = MaterialTemplateGenerator()
        template_path = generator.generate_base_material_template()
        
        # 返回文件下载响应
        import urllib.parse
        encoded_filename = urllib.parse.quote("基准材料导入模板.xlsx".encode('utf-8'))
        return FileResponse(
            path=template_path,
            filename="base_material_template.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=base_material_template.xlsx; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成模板文件失败: {str(e)}"
        )


@router.post("/get-preview-data")
async def get_preview_data(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
    max_rows: Optional[int] = Form(2000),
    # TODO: 生产环境需要恢复认证
    # current_user: SimpleUser = Depends(get_current_active_user)
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
            file_like, file.filename, sheet_name=sheet_name, max_preview_rows=100  # 预览只显示100行
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
    sheet_name: Optional[str] = Form(None),
    # TODO: 生产环境需要恢复认证
    # current_user: SimpleUser = Depends(get_current_active_user)
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
        
        # 分析文件结构，传递指定的工作表名称
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
async def import_base_materials(
    import_request: dict,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """导入基础材料数据"""
    try:
        materials_data = import_request.get('materials', [])
        field_mapping = import_request.get('field_mapping', {})
        import_options = import_request.get('import_options', {})
        
        if not materials_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有要导入的材料数据"
            )
        
        # 使用材料导入服务
        import_service = MaterialImportService()
        
        # 如果没有field_mapping或为空，说明前端已经处理好了结构化数据
        if not field_mapping:
            result = await import_service.import_structured_materials(
                db, materials_data, import_options
            )
        else:
            # 使用原有的字段映射方式
            result = await import_service.import_base_materials(
                db, materials_data, field_mapping, import_options
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
        logger.error(f"基础材料导入失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"材料导入失败: {str(e)}"
        )


@router.get("/periods")
async def get_material_periods(
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取材料期数列表"""
    periods = await BaseMaterialService.get_material_periods(db)
    return {
        "code": 200,
        "message": "获取成功",
        "data": periods
    }


@router.post("/periods/delete")
async def delete_materials_by_period(
    delete_request: BaseMaterialPeriodDeleteRequest,
    # current_user: SimpleUser = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """删除某一期数下的所有材料"""
    try:
        result = await BaseMaterialService.delete_materials_by_period(db, delete_request)
        return {
            "code": 200,
            "message": f"成功删除 {result['deleted_count']} 条材料数据",
            "data": result
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"删除期数材料失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除期数材料失败"
        )


@router.get("/{material_id}", response_model=BaseMaterialResponse)
async def get_base_material(
    material_id: int,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取基准材料详情"""
    material = await BaseMaterialService.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="基准材料不存在"
        )
    return BaseMaterialResponse.model_validate(material)


@router.put("/{material_id}", response_model=BaseMaterialResponse)
async def update_base_material(
    material_id: int,
    material_data: BaseMaterialUpdate,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """更新基准材料"""
    material = await BaseMaterialService.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="基准材料不存在"
        )
    
    updated_material = await BaseMaterialService.update_material(
        db, material, material_data
    )
    return BaseMaterialResponse.model_validate(updated_material)


@router.delete("/{material_id}")
async def delete_base_material(
    material_id: int,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """删除基准材料"""
    material = await BaseMaterialService.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="基准材料不存在"
        )
    
    success = await BaseMaterialService.delete_material(db, material)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除基准材料失败"
        )
    
    return {"message": "基准材料删除成功"}


@router.post("/upload", response_model=dict)
async def upload_base_materials_file(
    file: UploadFile = File(...),
    current_user: SimpleUser = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """上传基准材料Excel文件"""
    try:
        excel_processor = ExcelProcessor()
        file_path, filename = await excel_processor.save_file(file)
        
        # 分析Excel文件
        analysis = await MaterialImportService().analyze_excel_file(file_path)
        
        return {
            "message": "文件上传成功",
            "file_info": {
                "filename": filename,
                "original_filename": file.filename,
                "size": file.size,
                "path": file_path
            },
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import", response_model=BaseMaterialImportResponse)
async def import_base_materials(
    import_request: BaseMaterialImportRequest,
    file_path: str,
    current_user: SimpleUser = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """导入基准材料数据"""
    try:
        import_service = MaterialImportService()
        result = await import_service.import_materials_from_excel(
            db, file_path, import_request
        )
        
        return BaseMaterialImportResponse(
            imported_count=result['imported_count'],
            skipped_count=result['skipped_count'],
            error_count=result['error_count'],
            validation_errors=result['validation_errors'],
            sample_materials=[
                BaseMaterialResponse.model_validate(material) 
                for material in result['materials']
            ]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/batch-operation")
async def batch_operation_materials(
    operation_data: BaseMaterialBatchOperation,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """批量操作基准材料"""
    try:
        if operation_data.operation == "verify":
            count = await BaseMaterialService.batch_verify_materials(
                db, operation_data.material_ids, True, operation_data.verification_notes
            )
            return {"message": f"成功验证 {count} 个材料"}
        
        elif operation_data.operation == "unverify":
            count = await BaseMaterialService.batch_verify_materials(
                db, operation_data.material_ids, False, operation_data.verification_notes
            )
            return {"message": f"成功取消验证 {count} 个材料"}
        
        elif operation_data.operation == "delete":
            count = await BaseMaterialService.batch_delete_materials(
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
    categories = await BaseMaterialService.get_categories(db)
    return {"categories": categories}


@router.get("/regions/list")
async def get_material_regions(
    price_type: Optional[str] = Query(None, description="期刊类型 (provincial/municipal)"),
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """根据期刊类型获取对应的地区选项"""
    regions = await BaseMaterialService.get_regions_by_price_type(db, price_type)
    return {"regions": regions}


@router.get("/search-similar")
async def search_similar_materials(
    material_name: str = Query(..., description="材料名称"),
    specification: Optional[str] = Query(None, description="规格型号"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """搜索相似材料"""
    materials = await BaseMaterialService.search_similar_materials(
        db, material_name, specification, limit
    )
    return [BaseMaterialResponse.model_validate(material) for material in materials]
