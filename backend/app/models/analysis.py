from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AnalysisStatus(str, enum.Enum):
    """分析状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PriceAnalysis(Base):
    """价格分析表"""
    __tablename__ = "price_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("project_materials.id", ondelete="CASCADE"), nullable=False, comment="项目材料ID")
    
    # 分析状态
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, comment="分析状态")
    
    # AI分析结果
    predicted_price_min = Column(Float, nullable=True, comment="预测价格下限")
    predicted_price_max = Column(Float, nullable=True, comment="预测价格上限")
    predicted_price_avg = Column(Float, nullable=True, comment="预测平均价格")
    confidence_score = Column(Float, nullable=True, comment="置信度评分")
    
    # 价格合理性分析
    is_reasonable = Column(Boolean, nullable=True, comment="价格是否合理")
    price_variance = Column(Float, nullable=True, comment="价格偏差百分比")
    risk_level = Column(String(20), nullable=True, comment="风险等级")
    
    # AI分析详情
    analysis_model = Column(String(50), nullable=True, comment="使用的AI模型")
    analysis_prompt = Column(Text, nullable=True, comment="分析提示词")
    api_response = Column(JSON, nullable=True, comment="API完整响应")
    
    # 数据源信息
    data_sources = Column(JSON, nullable=True, comment="数据源列表")
    market_data = Column(JSON, nullable=True, comment="市场价格数据")
    reference_prices = Column(JSON, nullable=True, comment="参考价格列表")
    
    # 分析说明
    analysis_reasoning = Column(Text, nullable=True, comment="分析推理过程")
    risk_factors = Column(Text, nullable=True, comment="风险因素说明")
    recommendations = Column(Text, nullable=True, comment="建议措施")
    
    # 成本和性能指标
    analysis_cost = Column(Float, nullable=True, comment="分析成本")
    analysis_time = Column(Float, nullable=True, comment="分析耗时（秒）")
    retry_count = Column(Integer, default=0, comment="重试次数")
    
    # 人工审核
    is_reviewed = Column(Boolean, default=False, comment="是否人工审核")
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="审核用户ID")
    review_notes = Column(Text, nullable=True, comment="审核备注")
    reviewed_at = Column(DateTime(timezone=True), nullable=True, comment="审核时间")
    
    # 关联关系
    material = relationship("ProjectMaterial", back_populates="analysis")
    reviewer = relationship("User")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    analyzed_at = Column(DateTime(timezone=True), nullable=True, comment="分析完成时间")
    
    __table_args__ = (
        Index('ix_price_analyses_material', 'material_id'),
        Index('ix_price_analyses_status', 'status'),
    )


class AuditReport(Base):
    """审计报告表"""
    __tablename__ = "audit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, comment="项目ID")
    
    # 报告信息
    report_title = Column(String(200), nullable=False, comment="报告标题")
    report_type = Column(String(50), default="price_analysis", comment="报告类型")
    
    # 报告统计
    total_materials_count = Column(Integer, nullable=False, comment="材料总数")
    problematic_materials_count = Column(Integer, nullable=False, comment="问题材料数量")
    total_price_variance = Column(Float, nullable=True, comment="总价格偏差")
    estimated_savings = Column(Float, nullable=True, comment="预估节约金额")
    
    # 文件信息
    report_filename = Column(String(500), nullable=True, comment="报告文件名")
    report_file_path = Column(Text, nullable=True, comment="报告文件路径")
    file_size = Column(Integer, nullable=True, comment="文件大小")
    
    # 报告内容
    executive_summary = Column(Text, nullable=True, comment="执行摘要")
    key_findings = Column(JSON, nullable=True, comment="关键发现")
    recommendations = Column(Text, nullable=True, comment="建议措施")
    appendices = Column(JSON, nullable=True, comment="附件信息")
    
    # 生成信息
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="生成用户ID")
    template_version = Column(String(20), nullable=True, comment="模板版本")
    generation_time = Column(Float, nullable=True, comment="生成耗时（秒）")
    
    # 状态和审核
    is_final = Column(Boolean, default=False, comment="是否最终版本")
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="审批用户ID")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="审批时间")
    
    # 关联关系
    project = relationship("Project", back_populates="reports")
    generator = relationship("User", foreign_keys=[generated_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index('ix_audit_reports_project', 'project_id'),
        Index('ix_audit_reports_created', 'created_at'),
    )


# 更新关联关系
from app.models.project import ProjectMaterial, Project

ProjectMaterial.analysis = relationship("PriceAnalysis", back_populates="material", uselist=False, cascade="all, delete-orphan")
Project.reports = relationship("AuditReport", back_populates="project", cascade="all, delete-orphan")