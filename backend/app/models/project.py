from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum


class ProjectStatus(str, enum.Enum):
    """项目状态枚举"""
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectType(str, enum.Enum):
    """项目类型枚举"""
    BUILDING = "building"
    DECORATION = "decoration"
    MUNICIPAL = "municipal"
    LANDSCAPE = "landscape"
    HIGHWAY = "highway"
    OTHER = "other"


class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True, index=True, comment="项目UUID")
    name = Column(String(200), nullable=False, comment="项目名称")
    description = Column(Text, nullable=True, comment="项目描述")
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, comment="项目状态")
    
    # 项目信息
    project_code = Column(String(100), nullable=True, comment="项目编号")
    project_type = Column(SQLEnum(ProjectType), default=ProjectType.OTHER, comment="项目类型")
    location = Column(String(200), nullable=True, comment="项目地点")
    owner = Column(String(200), nullable=True, comment="业主单位")
    contractor = Column(String(200), nullable=True, comment="承包单位")
    budget_amount = Column(Float, nullable=True, comment="工程造价(万元)")
    price_base_date = Column(String(20), nullable=True, comment="价格基准日期")
    analysis_precision = Column(String(20), default="standard", comment="分析精度")

    # 分析设置信息
    base_price_date = Column(String(20), nullable=True, comment="基期信息价日期")
    base_price_province = Column(String(20), nullable=True, comment="基期信息价省份")
    base_price_city = Column(String(20), nullable=True, comment="基期信息价城市")
    base_price_district = Column(String(20), nullable=True, comment="基期信息价区县")
    support_price_adjustment = Column(Boolean, default=True, comment="是否支持调价")
    price_adjustment_range = Column(Float, default=5.0, comment="调价范围(%)")
    audit_scope = Column(JSON, nullable=True, comment="分析范围")
    
    # 用户关联
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建用户ID")
    
    # 文件信息
    original_filename = Column(String(500), nullable=True, comment="原始文件名")
    file_path = Column(Text, nullable=True, comment="文件存储路径")
    file_size = Column(Integer, nullable=True, comment="文件大小")
    
    # 处理统计
    total_materials = Column(Integer, default=0, comment="材料总数")
    priced_materials = Column(Integer, default=0, comment="市场信息价材料数量")
    unpriced_materials = Column(Integer, default=0, comment="无信息价材料数量")
    problematic_materials = Column(Integer, default=0, comment="问题材料数量")
    
    # 时间信息
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    processed_at = Column(DateTime(timezone=True), nullable=True, comment="处理完成时间")


class ProjectMaterial(Base):
    """项目材料表"""
    __tablename__ = "project_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, comment="项目ID")
    
    # 原始材料信息
    serial_number = Column(String(50), nullable=True, comment="序号")
    material_name = Column(String(200), nullable=False, comment="材料名称")
    specification = Column(Text, nullable=True, comment="规格型号")
    unit = Column(String(20), nullable=False, comment="计量单位")
    quantity = Column(Float, nullable=True, comment="数量")
    unit_price = Column(Float, nullable=True, comment="单价")
    total_price = Column(Float, nullable=True, comment="总价")
    
    # 分类信息
    category = Column(String(100), nullable=True, comment="材料分类")
    subcategory = Column(String(100), nullable=True, comment="材料子分类")
    
    # 匹配状态
    is_matched = Column(Boolean, default=False, comment="是否已匹配")
    matched_material_id = Column(Integer, ForeignKey("base_materials.id"), nullable=True, comment="匹配的基准材料ID")
    match_score = Column(Float, nullable=True, comment="匹配得分")
    match_method = Column(String(50), nullable=True, comment="匹配方法")
    
    # 价格分析状态
    is_analyzed = Column(Boolean, default=False, comment="是否已分析")
    is_problematic = Column(Boolean, default=False, comment="是否存在问题")
    
    # 备注信息
    notes = Column(Text, nullable=True, comment="备注")
    row_number = Column(Integer, nullable=True, comment="Excel行号")
    
    # 关联关系
    project = relationship("Project", back_populates="materials")
    matched_material = relationship("BaseMaterial")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    __table_args__ = (
        Index('ix_project_materials_project', 'project_id'),
        Index('ix_project_materials_name', 'material_name'),
    )


# 更新Project模型以包含关联关系
Project.materials = relationship("ProjectMaterial", back_populates="project", cascade="all, delete-orphan")