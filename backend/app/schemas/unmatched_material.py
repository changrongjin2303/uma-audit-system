from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class UnmatchedMaterialBase(BaseModel):
    """无市场信息价材料基础模式"""
    serial_number: Optional[str] = Field(None, max_length=50, description="序号")
    name: str = Field(..., min_length=1, max_length=200, description="材料名称")
    specification: Optional[str] = Field(None, description="规格型号")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    category: Optional[str] = Field(None, max_length=100, description="材料分类")
    subcategory: Optional[str] = Field(None, max_length=100, description="材料子分类")
    price_excluding_tax: Optional[float] = Field(None, gt=0, description="价格（除税价）")
    currency: str = Field(default="CNY", max_length=10, description="货币单位")
    date: Optional[datetime] = Field(None, description="日期")
    source: Optional[str] = Field(None, max_length=100, description="数据来源")
    source_url: Optional[str] = Field(None, description="来源链接")
    notes: Optional[str] = Field(None, description="备注说明")


class UnmatchedMaterialCreate(UnmatchedMaterialBase):
    """创建无市场信息价材料模式"""
    pass


class UnmatchedMaterialUpdate(BaseModel):
    """更新无市场信息价材料模式"""
    serial_number: Optional[str] = Field(None, max_length=50, description="序号")
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="材料名称")
    specification: Optional[str] = Field(None, description="规格型号")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="计量单位")
    category: Optional[str] = Field(None, max_length=100, description="材料分类")
    subcategory: Optional[str] = Field(None, max_length=100, description="材料子分类")
    price_excluding_tax: Optional[float] = Field(None, gt=0, description="价格（除税价）")
    currency: Optional[str] = Field(None, max_length=10, description="货币单位")
    date: Optional[datetime] = Field(None, description="日期")
    source: Optional[str] = Field(None, max_length=100, description="数据来源")
    source_url: Optional[str] = Field(None, description="来源链接")
    notes: Optional[str] = Field(None, description="备注说明")
    is_verified: Optional[bool] = Field(None, description="是否验证")
    verification_notes: Optional[str] = Field(None, description="验证备注")


class UnmatchedMaterialResponse(UnmatchedMaterialBase):
    """无市场信息价材料响应模式"""
    id: int
    is_verified: bool
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UnmatchedMaterialImportRequest(BaseModel):
    """无市场信息价材料导入请求模式"""
    sheet_name: Optional[str] = Field(None, description="工作表名称")
    column_mapping: dict = Field(..., description="列映射关系")
    start_row: int = Field(default=1, ge=1, description="开始行号")
    batch_size: int = Field(default=1000, ge=1, le=10000, description="批量处理大小")

    @validator('column_mapping')
    def validate_column_mapping(cls, v):
        required_fields = ['name']  # 只有名称是必需的
        for field in required_fields:
            if field not in v:
                raise ValueError(f'缺少必需的字段映射: {field}')
        return v


class UnmatchedMaterialImportResponse(BaseModel):
    """无市场信息价材料导入响应模式"""
    imported_count: int
    skipped_count: int
    error_count: int
    validation_errors: List[str] = []
    sample_materials: List[UnmatchedMaterialResponse] = []


class UnmatchedMaterialSearchRequest(BaseModel):
    """无市场信息价材料搜索请求模式"""
    query: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="材料分类")
    price_min: Optional[float] = Field(None, ge=0, description="价格下限")
    price_max: Optional[float] = Field(None, ge=0, description="价格上限")
    date_start: Optional[datetime] = Field(None, description="日期开始")
    date_end: Optional[datetime] = Field(None, description="日期结束")
    is_verified: Optional[bool] = Field(None, description="是否已验证")

    @validator('price_max')
    def validate_price_range(cls, v, values):
        if v is not None and 'price_min' in values and values['price_min'] is not None:
            if v < values['price_min']:
                raise ValueError('价格上限不能小于价格下限')
        return v


class UnmatchedMaterialBatchOperation(BaseModel):
    """无市场信息价材料批量操作模式"""
    material_ids: List[int] = Field(..., min_items=1, description="材料ID列表")
    operation: str = Field(..., description="操作类型: verify/unverify/delete")
    verification_notes: Optional[str] = Field(None, description="验证备注")

    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['verify', 'unverify', 'delete']
        if v not in allowed_operations:
            raise ValueError(f'无效的操作类型，允许的操作: {", ".join(allowed_operations)}')
        return v
