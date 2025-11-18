from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, cast, String
from sqlalchemy.orm import selectinload
from pathlib import Path

from app.models.project import Project, ProjectMaterial, ProjectStatus
from app.models.user import User
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectMaterialCreate, 
    MaterialImportRequest
)
from app.utils.excel import ExcelProcessor
from loguru import logger


class ProjectService:
    """项目服务类"""
    
    @staticmethod
    async def create_project(
        db: AsyncSession,
        project_data: ProjectCreate,
        user
    ) -> Project:
        """创建项目"""
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            project_code=project_data.project_code,
            project_type=project_data.project_type,
            location=project_data.location,
            owner=project_data.owner,
            contractor=project_data.contractor,
            budget_amount=project_data.budget_amount,
            price_base_date=project_data.price_base_date,
            analysis_precision=project_data.analysis_precision,
            contract_start_date=project_data.contract_start_date,
            contract_end_date=project_data.contract_end_date,
            # 分析设置字段
            base_price_date=project_data.base_price_date,
            base_price_province=project_data.base_price_province,
            base_price_city=project_data.base_price_city,
            base_price_district=project_data.base_price_district,
            support_price_adjustment=project_data.support_price_adjustment,
            price_adjustment_range=project_data.price_adjustment_range,
            audit_scope=project_data.audit_scope,
            created_by=user.id,
            status=ProjectStatus.DRAFT
        )

        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project
    
    @staticmethod
    async def get_project_by_id(
        db: AsyncSession, 
        project_id: int, 
        user = None
    ) -> Optional[Project]:
        """根据ID获取项目"""
        stmt = select(Project).where(Project.id == project_id)
        
        # 如果提供了用户信息，添加权限检查
        if user and hasattr(user, 'role'):
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            if role_value not in ['ADMIN', 'admin']:
                stmt = stmt.where(Project.created_by == user.id)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_project_by_code(
        db: AsyncSession, 
        project_code: str
    ) -> Optional[Project]:
        """根据项目代码获取项目"""
        stmt = select(Project).where(Project.project_code == project_code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_project_with_materials(
        db: AsyncSession, 
        project_id: int, 
        user = None
    ) -> Optional[Project]:
        """获取项目及其材料信息"""
        stmt = select(Project).options(
            selectinload(Project.materials)
        ).where(Project.id == project_id)
        
        if user and hasattr(user, 'role'):
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            if role_value not in ['ADMIN', 'admin']:
                stmt = stmt.where(Project.created_by == user.id)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_projects(
        db: AsyncSession,
        user: User,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProjectStatus] = None,
        search: Optional[str] = None,
        project_type: Optional[str] = None
    ) -> List[Project]:
        """获取项目列表"""
        stmt = select(Project)
        
        # 权限过滤
        if hasattr(user, 'role'):
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            if role_value.lower() not in ['admin']:
                stmt = stmt.where(Project.created_by == user.id)
        
        # 状态过滤
        if status:
            stmt = stmt.where(Project.status == status)
        
        # 项目类型过滤
        if project_type:
            stmt = stmt.where(Project.project_type == project_type)
        
        # 搜索过滤
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Project.name.ilike(search_term),
                    Project.description.ilike(search_term),
                    Project.project_code.ilike(search_term)
                )
            )
        
        stmt = stmt.offset(skip).limit(limit).order_by(Project.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_projects_count(
        db: AsyncSession,
        user: User,
        status: Optional[ProjectStatus] = None,
        search: Optional[str] = None,
        project_type: Optional[str] = None
    ) -> int:
        """获取项目总数"""
        stmt = select(func.count(Project.id))
        
        # 权限过滤
        if hasattr(user, 'role'):
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            if role_value.lower() not in ['admin']:
                stmt = stmt.where(Project.created_by == user.id)
        
        # 状态过滤
        if status:
            stmt = stmt.where(Project.status == status)
        
        # 项目类型过滤
        if project_type:
            stmt = stmt.where(Project.project_type == project_type)
        
        # 搜索过滤
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Project.name.ilike(search_term),
                    Project.description.ilike(search_term),
                    Project.project_code.ilike(search_term)
                )
            )
        
        result = await db.execute(stmt)
        return result.scalar() or 0
    
    @staticmethod
    async def update_project(
        db: AsyncSession, 
        project: Project, 
        project_data: ProjectUpdate
    ) -> Project:
        """更新项目"""
        update_data = project_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await db.commit()
        await db.refresh(project)
        return project
    
    @staticmethod
    async def delete_project(db: AsyncSession, project: Project) -> bool:
        """删除项目"""
        try:
            await db.delete(project)
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"删除项目失败: {e}")
            await db.rollback()
            return False
    
    @staticmethod
    async def add_materials_to_project(
        db: AsyncSession,
        project: Project,
        materials_data: List[Dict[str, Any]]
    ) -> List[ProjectMaterial]:
        """向项目添加材料"""
        materials = []
        
        for material_data in materials_data:
            db_material = ProjectMaterial(
                project_id=project.id,
                serial_number=material_data.get('serial_number'),
                material_name=material_data['material_name'],
                specification=material_data.get('specification'),
                unit=material_data['unit'],
                quantity=material_data.get('quantity'),
                unit_price=material_data.get('unit_price'),
                total_price=material_data.get('total_price'),
                category=material_data.get('category'),
                subcategory=material_data.get('subcategory'),
                notes=material_data.get('notes'),
                row_number=material_data.get('row_number')
            )
            materials.append(db_material)
        
        db.add_all(materials)
        
        # 更新项目统计
        project.total_materials = len(materials)
        project.status = ProjectStatus.PROCESSING
        
        await db.commit()
        
        # 刷新所有材料对象
        for material in materials:
            await db.refresh(material)
        
        return materials
    
    @staticmethod
    async def get_project_stats(db: AsyncSession, project_id: int) -> Dict[str, int]:
        """获取项目统计信息"""
        from sqlalchemy import func, text
        
        # 查询项目材料统计
        result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_materials,
                    COUNT(CASE WHEN unit_price > 0 THEN 1 END) as priced_materials,
                    COUNT(CASE WHEN unit_price = 0 OR unit_price IS NULL THEN 1 END) as unpriced_materials,
                    COUNT(CASE WHEN is_problematic = true THEN 1 END) as problematic_materials,
                    COUNT(CASE WHEN is_matched = true AND matched_material_id IS NOT NULL THEN 1 END) as matched_materials,
                    COUNT(CASE WHEN is_analyzed = true THEN 1 END) as analyzed_materials
                FROM project_materials 
                WHERE project_id = :project_id
            """),
            {"project_id": project_id}
        )
        
        row = result.fetchone()
        if row:
            return {
                'total_materials': row.total_materials or 0,
                'priced_materials': row.priced_materials or 0,
                'unpriced_materials': row.unpriced_materials or 0,
                'problematic_materials': row.problematic_materials or 0,
                'matched_materials': row.matched_materials or 0,
                'analyzed_materials': row.analyzed_materials or 0
            }
        
        return {
            'total_materials': 0,
            'priced_materials': 0,
            'unpriced_materials': 0,
            'problematic_materials': 0,
            'matched_materials': 0,
            'analyzed_materials': 0
        }
    
    @staticmethod
    async def get_project_materials(
        db: AsyncSession,
        project_id: int,
        skip: int = 0,
        limit: int = 100,
        is_matched: Optional[bool] = None,
        is_problematic: Optional[bool] = None
    ) -> List[ProjectMaterial]:
        """获取项目材料列表"""
        stmt = select(ProjectMaterial).where(
            ProjectMaterial.project_id == project_id
        )
        
        if is_matched is not None:
            stmt = stmt.where(ProjectMaterial.is_matched == is_matched)
        
        if is_problematic is not None:
            stmt = stmt.where(ProjectMaterial.is_problematic == is_problematic)
        
        stmt = stmt.offset(skip).limit(limit).order_by(ProjectMaterial.id)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def update_project_statistics(
        db: AsyncSession, 
        project: Project
    ) -> Project:
        """更新项目统计信息"""
        # 统计材料数量
        total_stmt = select(func.count(ProjectMaterial.id)).where(
            ProjectMaterial.project_id == project.id
        )
        total_result = await db.execute(total_stmt)
        project.total_materials = total_result.scalar() or 0
        
        # 统计匹配的材料
        matched_stmt = select(func.count(ProjectMaterial.id)).where(
            and_(
                ProjectMaterial.project_id == project.id,
                ProjectMaterial.is_matched == True
            )
        )
        matched_result = await db.execute(matched_stmt)
        project.priced_materials = matched_result.scalar() or 0
        
        # 统计未匹配的材料
        project.unpriced_materials = project.total_materials - project.priced_materials
        
        # 统计问题材料
        problematic_stmt = select(func.count(ProjectMaterial.id)).where(
            and_(
                ProjectMaterial.project_id == project.id,
                ProjectMaterial.is_problematic == True
            )
        )
        problematic_result = await db.execute(problematic_stmt)
        project.problematic_materials = problematic_result.scalar() or 0
        
        await db.commit()
        await db.refresh(project)
        return project


class ProjectFileService:
    """项目文件服务类"""
    
    def __init__(self):
        self.excel_processor = ExcelProcessor()
    
    async def process_excel_upload(
        self,
        db: AsyncSession,
        project: Project,
        file_path: str,
        import_request: MaterialImportRequest
    ) -> Dict[str, Any]:
        """处理Excel文件导入"""
        try:
            # 读取Excel文件
            df = self.excel_processor.read_excel_file(
                file_path, 
                import_request.sheet_name
            )
            
            # 解析材料数据
            materials_data = self.excel_processor.parse_material_data(
                df, 
                import_request.column_mapping
            )
            
            # 验证数据质量
            validation_result = self.excel_processor.validate_material_data(
                materials_data
            )
            
            # 过滤有效数据
            valid_materials = [
                material for material in materials_data
                if material.get('material_name')
            ]
            
            # 导入到数据库
            db_materials = await ProjectService.add_materials_to_project(
                db, project, valid_materials
            )
            
            # 更新项目统计
            await ProjectService.update_project_statistics(db, project)
            
            return {
                'imported_count': len(db_materials),
                'skipped_count': len(materials_data) - len(valid_materials),
                'validation_result': validation_result,
                'materials': db_materials
            }
        
        except Exception as e:
            logger.error(f"处理Excel文件失败: {e}")
            raise ValueError(f"处理Excel文件失败: {str(e)}")
    
    async def analyze_excel_file(self, file_path: str) -> Dict[str, Any]:
        """分析Excel文件结构"""
        try:
            # 获取工作表名称
            sheet_names = self.excel_processor.get_sheet_names(file_path)
            
            # 读取第一个工作表进行分析
            df = self.excel_processor.read_excel_file(file_path, sheet_names[0])
            
            # 分析列结构
            analysis = self.excel_processor.analyze_columns(df)
            analysis['sheet_names'] = sheet_names
            
            return analysis
        
        except Exception as e:
            logger.error(f"分析Excel文件失败: {e}")
            raise ValueError(f"分析Excel文件失败: {str(e)}")
    
    def cleanup_file(self, file_path: str) -> bool:
        """清理上传的文件"""
        try:
            file_obj = Path(file_path)
            if file_obj.exists():
                file_obj.unlink()
                return True
        except Exception as e:
            logger.error(f"清理文件失败: {e}")
        return False
    
    @staticmethod
    async def batch_delete_materials(
        db: AsyncSession,
        project_id: int, 
        material_ids: List[int]
    ) -> int:
        """批量删除项目材料 - 用于提高大批量删除性能"""
        try:
            # 删除指定的材料
            stmt = select(ProjectMaterial).where(
                and_(
                    ProjectMaterial.project_id == project_id,
                    ProjectMaterial.id.in_(material_ids)
                )
            )
            result = await db.execute(stmt)
            materials_to_delete = result.scalars().all()
            
            # 执行删除
            deleted_count = 0
            for material in materials_to_delete:
                await db.delete(material)
                deleted_count += 1
            
            await db.commit()
            logger.info(f"批量删除项目材料成功: 项目ID={project_id}, 删除数量={deleted_count}")
            
            return deleted_count
            
        except Exception as e:
            await db.rollback()
            logger.error(f"批量删除项目材料失败: {e}")
            raise e
