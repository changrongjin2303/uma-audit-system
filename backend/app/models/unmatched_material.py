from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base


class UnmatchedMaterial(Base):
    """无市场信息价材料表（需要AI分析定价的特殊材料）"""
    __tablename__ = "unmatched_materials"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(50), index=True, nullable=True, comment="序号")
    name = Column(String(200), nullable=False, comment="材料名称")
    specification = Column(Text, nullable=True, comment="规格型号")
    brand = Column(String(100), nullable=True, comment="品牌")
    unit = Column(String(20), nullable=True, comment="计量单位")

    # 材料分类
    category = Column(String(100), nullable=True, comment="材料分类")
    subcategory = Column(String(100), nullable=True, comment="材料子分类")

    # 价格信息（除税价）
    price_excluding_tax = Column(Float, nullable=True, comment="价格（除税价）")
    currency = Column(String(10), default="CNY", comment="货币单位")

    # 时间信息
    date = Column(DateTime(timezone=True), nullable=True, comment="日期")

    # 数据来源
    source = Column(String(100), nullable=True, comment="数据来源")
    source_url = Column(Text, nullable=True, comment="来源链接")

    # 备注说明
    notes = Column(Text, nullable=True, comment="备注说明")

    # 质量控制
    is_verified = Column(Boolean, default=False, comment="是否验证")
    verification_notes = Column(Text, nullable=True, comment="验证备注")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 复合索引
    __table_args__ = (
        Index('ix_unmatched_materials_name_spec', 'name', 'specification'),
        Index('ix_unmatched_materials_date', 'date'),
        Index('ix_unmatched_materials_category', 'category', 'subcategory'),
    )
