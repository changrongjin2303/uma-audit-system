from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class MaterialCategory(Base):
    """材料分类表（支持层级分类）"""
    __tablename__ = "material_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    code = Column(String(50), nullable=False, comment="分类代码")
    level = Column(Integer, nullable=False, comment="层级 (1=信息来源类型, 2=年月, 3=具体分类)")
    parent_id = Column(Integer, ForeignKey("material_categories.id"), nullable=True, comment="父分类ID")
    
    # 层级相关字段
    source_type = Column(String(50), nullable=True, comment="信息来源类型 (municipal/provincial)")
    year_month = Column(String(10), nullable=True, comment="年月 (YYYY-MM)")
    
    # 排序和状态
    sort_order = Column(Integer, default=0, comment="排序序号")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="分类描述")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    parent = relationship("MaterialCategory", remote_side=[id], back_populates="children")
    children = relationship("MaterialCategory", back_populates="parent")
    materials = relationship("BaseMaterial", back_populates="category_rel")
    
    __table_args__ = (
        Index('ix_material_categories_level_parent', 'level', 'parent_id'),
        Index('ix_material_categories_source_type', 'source_type'),
        Index('ix_material_categories_year_month', 'year_month'),
        Index('ix_material_categories_code', 'code'),
    )


class BaseMaterial(Base):
    """基准材料表（市场信息价材料基准数据库）"""
    __tablename__ = "base_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    material_code = Column(String(50), index=True, nullable=True, comment="材料编码")
    name = Column(String(200), nullable=False, comment="材料名称")
    specification = Column(Text, nullable=True, comment="规格型号")
    unit = Column(String(20), nullable=False, comment="计量单位")
    
    # 新的分类系统
    category_id = Column(Integer, ForeignKey("material_categories.id"), nullable=True, comment="所属分类ID")
    
    # 保留原有分类字段（兼容性）
    category = Column(String(100), nullable=True, comment="材料分类")
    subcategory = Column(String(100), nullable=True, comment="材料子分类")
    
    # 价格信息
    price = Column(Float, nullable=False, comment="单价")
    price_including_tax = Column(Float, nullable=True, comment="含税信息价")
    price_excluding_tax = Column(Float, nullable=True, comment="除税信息价")
    currency = Column(String(10), default="CNY", comment="货币单位")
    
    # 地区和时间信息
    region = Column(String(100), nullable=False, comment="适用地区")
    excel_region = Column(String(100), nullable=True, comment="Excel原始地区信息")
    province = Column(String(50), nullable=True, comment="省份")
    city = Column(String(50), nullable=True, comment="城市")
    version = Column(String(50), nullable=True, comment="版本号")
    effective_date = Column(DateTime(timezone=True), nullable=False, comment="生效日期")
    
    # 数据来源
    source = Column(String(100), nullable=True, comment="数据来源")
    source_url = Column(Text, nullable=True, comment="来源链接")
    
    # 信息价类型相关字段
    price_type = Column(String(20), nullable=True, comment="信息价类型 (provincial/municipal)")
    price_date = Column(String(10), nullable=True, comment="信息价期数 (YYYY-MM)")
    price_source = Column(String(50), nullable=True, comment="信息价来源描述")
    
    # 质量控制
    is_verified = Column(Boolean, default=False, comment="是否验证")
    verification_notes = Column(Text, nullable=True, comment="验证备注")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 复合索引
    __table_args__ = (
        Index('ix_base_materials_name_spec', 'name', 'specification'),
        Index('ix_base_materials_region_date', 'region', 'effective_date'),
        Index('ix_base_materials_category', 'category', 'subcategory'),
        Index('ix_base_materials_price_type_date', 'price_type', 'price_date'),
    )


class MaterialAlias(Base):
    """材料别名表（用于提高匹配准确率）"""
    __tablename__ = "material_aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    base_material_id = Column(Integer, ForeignKey("base_materials.id"), nullable=False, comment="基准材料ID")
    alias_name = Column(String(200), nullable=False, comment="别名")
    alias_specification = Column(Text, nullable=True, comment="别名规格")
    similarity_score = Column(Float, default=1.0, comment="相似度评分")
    
    # 关联关系
    base_material = relationship("BaseMaterial", back_populates="aliases")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    __table_args__ = (
        Index('ix_material_aliases_name', 'alias_name'),
    )


# 更新BaseMaterial模型以包含关联关系
BaseMaterial.aliases = relationship("MaterialAlias", back_populates="base_material")
BaseMaterial.category_rel = relationship("MaterialCategory", back_populates="materials")