from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.project import ProjectStatus, ProjectType


class ProjectMaterialBase(BaseModel):
    """项目材料基础模式"""
    serial_number: Optional[str] = Field(None, description="序号")
    material_name: str = Field(..., description="材料名称")
    specification: Optional[str] = Field(None, description="规格型号")
    unit: str = Field(..., description="计量单位")
    quantity: Optional[float] = Field(None, ge=0, description="数量")
    unit_price: Optional[float] = Field(None, ge=0, description="单价")
    total_price: Optional[float] = Field(None, ge=0, description="总价")
    category: Optional[str] = Field(None, description="材料分类")
    subcategory: Optional[str] = Field(None, description="材料子分类")
    notes: Optional[str] = Field(None, description="备注")


class ProjectMaterialCreate(ProjectMaterialBase):
    """创建项目材料模式"""
    row_number: Optional[int] = Field(None, description="Excel行号")


class ProjectMaterialUpdate(BaseModel):
    """更新项目材料模式"""
    material_name: Optional[str] = Field(None, description="材料名称")
    specification: Optional[str] = Field(None, description="规格型号")
    unit: Optional[str] = Field(None, description="计量单位")
    quantity: Optional[float] = Field(None, ge=0, description="数量")
    unit_price: Optional[float] = Field(None, ge=0, description="单价")
    total_price: Optional[float] = Field(None, ge=0, description="总价")
    category: Optional[str] = Field(None, description="材料分类")
    notes: Optional[str] = Field(None, description="备注")


class ProjectMaterialResponse(ProjectMaterialBase):
    """项目材料响应模式"""
    id: int
    project_id: int
    is_matched: bool
    matched_material_id: Optional[int] = None
    match_score: Optional[float] = None
    match_method: Optional[str] = None
    is_analyzed: bool
    is_problematic: bool
    row_number: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """项目基础模式"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    project_code: Optional[str] = Field(None, max_length=100, description="项目编号")
    project_type: Optional[ProjectType] = Field(ProjectType.OTHER, description="项目类型")
    location: Optional[str] = Field(None, max_length=200, description="项目地点")
    owner: Optional[str] = Field(None, max_length=200, description="业主单位")
    contractor: Optional[str] = Field(None, max_length=200, description="承包单位")
    budget_amount: Optional[float] = Field(None, ge=0, description="工程造价(万元)")
    price_base_date: Optional[str] = Field(None, description="价格基准日期")
    analysis_precision: Optional[str] = Field("standard", description="分析精度")

    # 合同工期（月精度，格式 YYYY-MM）
    contract_start_date: Optional[str] = Field(None, description="合同工期开始 (YYYY-MM)")
    contract_end_date: Optional[str] = Field(None, description="合同工期结束 (YYYY-MM)")

    # 分析设置信息
    base_price_date: Optional[str] = Field(None, description="基期信息价日期")
    base_price_province: Optional[str] = Field(None, description="基期信息价省份")
    base_price_city: Optional[str] = Field(None, description="基期信息价城市")
    base_price_district: Optional[str] = Field(None, description="基期信息价区县")
    support_price_adjustment: Optional[bool] = Field(True, description="是否支持调价")
    price_adjustment_range: Optional[float] = Field(5.0, ge=0, le=100, description="调价范围(%)")
    audit_scope: Optional[List[str]] = Field(None, description="分析范围")


class ProjectCreate(ProjectBase):
    """创建项目模式"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    project_code: Optional[str] = Field(None, max_length=100, description="项目编号")
    project_type: Optional[ProjectType] = Field(None, description="项目类型")
    location: Optional[str] = Field(None, max_length=200, description="项目地点")
    owner: Optional[str] = Field(None, max_length=200, description="业主单位")
    contractor: Optional[str] = Field(None, max_length=200, description="承包单位")
    budget_amount: Optional[float] = Field(None, ge=0, description="工程造价(万元)")
    price_base_date: Optional[str] = Field(None, description="价格基准日期")
    analysis_precision: Optional[str] = Field(None, description="分析精度")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")

    # 合同工期（月精度，格式 YYYY-MM）
    contract_start_date: Optional[str] = Field(None, description="合同工期开始 (YYYY-MM)")
    contract_end_date: Optional[str] = Field(None, description="合同工期结束 (YYYY-MM)")

    # 分析设置信息
    base_price_date: Optional[str] = Field(None, description="基期信息价日期")
    base_price_province: Optional[str] = Field(None, description="基期信息价省份")
    base_price_city: Optional[str] = Field(None, description="基期信息价城市")
    base_price_district: Optional[str] = Field(None, description="基期信息价区县")
    support_price_adjustment: Optional[bool] = Field(None, description="是否支持调价")
    price_adjustment_range: Optional[float] = Field(None, ge=0, le=100, description="调价范围(%)")
    audit_scope: Optional[List[str]] = Field(None, description="分析范围")


class ProjectResponse(ProjectBase):
    """项目响应模式"""
    id: int
    project_uuid: str
    status: ProjectStatus
    created_by: int
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    total_materials: int
    priced_materials: int
    unpriced_materials: int
    problematic_materials: int
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None


    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """项目详情响应模式"""
    materials: List[ProjectMaterialResponse] = []


class FileUploadResponse(BaseModel):
    """文件上传响应模式"""
    message: str
    file_info: Dict[str, Any]
    analysis: Dict[str, Any]


class ExcelAnalysisResponse(BaseModel):
    """Excel分析响应模式"""
    total_rows: int
    total_columns: int
    column_info: List[Dict[str, Any]]
    suggested_mapping: Dict[str, str]


class MaterialImportRequest(BaseModel):
    """材料导入请求模式"""
    project_id: int
    sheet_name: Optional[str] = Field(None, description="工作表名称")
    column_mapping: Dict[str, str] = Field(..., description="列映射关系")
    start_row: Optional[int] = Field(1, ge=1, description="开始行号")
    
    @validator('column_mapping')
    def validate_column_mapping(cls, v):
        required_fields = ['material_name', 'unit']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'缺少必需的字段映射: {field}')
        return v


class MaterialImportResponse(BaseModel):
    """材料导入响应模式"""
    project_id: int
    imported_count: int
    skipped_count: int
    validation_result: Dict[str, Any]
    materials: List[ProjectMaterialResponse] = []
