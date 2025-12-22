from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """报告类型枚举"""
    PRICE_ANALYSIS = "price_analysis"
    COMPREHENSIVE = "comprehensive"
    SUMMARY = "summary"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """报告状态枚举"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportConfigSchema(BaseModel):
    """报告配置模式"""
    report_type: ReportType = ReportType.PRICE_ANALYSIS
    include_charts: bool = True
    include_detailed_analysis: bool = True
    include_recommendations: bool = True
    include_appendices: bool = True
    chart_types: List[str] = Field(default_factory=lambda: ["price_distribution", "risk_levels", "price_variance"])
    custom_sections: Dict[str, Any] = Field(default_factory=dict)


class ReportGenerationRequest(BaseModel):
    """报告生成请求"""
    project_id: int
    report_title: Optional[str] = None
    config: Optional[ReportConfigSchema] = Field(default_factory=ReportConfigSchema)
    include_materials: Optional[List[int]] = None  # 包含特定材料ID，None表示全部
    chart_images: Optional[Dict[str, str]] = None  # 前端生成的图表图片(base64)
    report_id: Optional[int] = None  # 如果提供，则更新现有报告而不是创建新报告
    is_draft: bool = False  # 是否仅创建草稿/记录



class ReportResponse(BaseModel):
    """报告响应"""
    report_id: int
    project_id: int
    report_title: str
    project_name: Optional[str] = None
    report_type: ReportType
    status: ReportStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generation_time: Optional[float] = None
    created_at: datetime
    download_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportStatistics(BaseModel):
    """报告统计信息"""
    total_materials: int
    analyzed_materials: int
    problematic_materials: int
    unreasonable_count: int
    analysis_coverage: float
    problem_rate: float
    avg_price_variance: float
    estimated_savings: float
    risk_distribution: Dict[str, int]


class ReportListResponse(BaseModel):
    """报告列表响应"""
    reports: List[ReportResponse]
    total: int
    page: int
    size: int
    
    
class ChartDataResponse(BaseModel):
    """图表数据响应"""
    chart_type: str
    data: Dict[str, Any]
    image_url: Optional[str] = None


class ReportPreviewResponse(BaseModel):
    """报告预览响应"""
    project_id: int
    project_name: str
    statistics: ReportStatistics
    chart_data: List[ChartDataResponse]
    sample_problematic_materials: List[Dict[str, Any]]
    analysis_materials: Optional[List[Dict[str, Any]]] = None
    guidance_price_materials: Optional[List[Dict[str, Any]]] = None

class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    report_ids: List[int]
