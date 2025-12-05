from pydantic import BaseModel, Field, validator
from typing import Optional, List, Tuple
from datetime import datetime


class BaseMaterialBase(BaseModel):
    """基准材料基础模式"""
    material_code: Optional[str] = Field(None, max_length=50, description="材料编码")
    name: str = Field(..., min_length=1, max_length=200, description="材料名称")
    specification: Optional[str] = Field(None, description="规格型号")
    unit: str = Field(..., min_length=1, max_length=20, description="计量单位")
    
    # 新分类系统
    category_id: Optional[int] = Field(None, description="所属分类ID")
    
    # 保留原分类字段（兼容性）
    category: Optional[str] = Field(None, max_length=100, description="材料分类")
    subcategory: Optional[str] = Field(None, max_length=100, description="材料子分类")
    price: float = Field(..., gt=0, description="单价")
    price_including_tax: Optional[float] = Field(None, gt=0, description="含税信息价")
    price_excluding_tax: Optional[float] = Field(None, gt=0, description="除税信息价")
    currency: str = Field(default="CNY", max_length=10, description="货币单位")
    region: str = Field(default="全国", max_length=100, description="适用地区")
    excel_region: Optional[str] = Field(None, max_length=100, description="Excel原始地区信息")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    version: Optional[str] = Field(None, max_length=50, description="版本号")
    effective_date: datetime = Field(..., description="生效日期")
    source: Optional[str] = Field(None, max_length=100, description="数据来源")
    source_url: Optional[str] = Field(None, description="来源链接")
    
    # 信息价类型相关字段
    price_type: Optional[str] = Field(None, max_length=20, description="信息价类型 (provincial/municipal)")
    price_date: Optional[str] = Field(None, max_length=10, description="信息价期数 (YYYY-MM)")
    price_source: Optional[str] = Field(None, max_length=50, description="信息价来源描述")


class BaseMaterialCreate(BaseMaterialBase):
    """创建基准材料模式"""
    pass


class BaseMaterialUpdate(BaseModel):
    """更新基准材料模式"""
    material_code: Optional[str] = Field(None, max_length=50, description="材料编码")
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="材料名称")
    specification: Optional[str] = Field(None, description="规格型号")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="计量单位")
    
    # 新分类系统
    category_id: Optional[int] = Field(None, description="所属分类ID")
    
    # 保留原分类字段（兼容性）
    category: Optional[str] = Field(None, max_length=100, description="材料分类")
    subcategory: Optional[str] = Field(None, max_length=100, description="材料子分类")
    price: Optional[float] = Field(None, gt=0, description="单价")
    price_including_tax: Optional[float] = Field(None, gt=0, description="含税信息价")
    price_excluding_tax: Optional[float] = Field(None, gt=0, description="除税信息价")
    currency: Optional[str] = Field(None, max_length=10, description="货币单位")
    region: Optional[str] = Field(None, min_length=1, max_length=100, description="适用地区")
    excel_region: Optional[str] = Field(None, max_length=100, description="Excel原始地区信息")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    version: Optional[str] = Field(None, max_length=50, description="版本号")
    effective_date: Optional[datetime] = Field(None, description="生效日期")
    source: Optional[str] = Field(None, max_length=100, description="数据来源")
    source_url: Optional[str] = Field(None, description="来源链接")
    
    # 信息价类型相关字段
    price_type: Optional[str] = Field(None, max_length=20, description="信息价类型 (provincial/municipal)")
    price_date: Optional[str] = Field(None, max_length=10, description="信息价期数 (YYYY-MM)")
    price_source: Optional[str] = Field(None, max_length=50, description="信息价来源描述")
    
    is_verified: Optional[bool] = Field(None, description="是否验证")
    verification_notes: Optional[str] = Field(None, description="验证备注")


class BaseMaterialResponse(BaseMaterialBase):
    """基准材料响应模式"""
    id: int
    is_verified: bool
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # 从category字段解析出的期刊信息（省/市期刊）
    journal_type: Optional[str] = Field(None, description="期刊类型（省/市期刊）")
    # 从category字段解析出的期数信息（日期）
    issue_period: Optional[str] = Field(None, description="期数（年月日期）")

    class Config:
        from_attributes = True
    
    @validator('journal_type', pre=True, always=True)
    def parse_journal_type(cls, v, values):
        """从price_type字段解析期刊类型"""
        if v is not None:
            return v
        
        # 优先使用price_type字段
        price_type = values.get('price_type')
        if price_type:
            return "省期刊" if price_type == 'provincial' else "市期刊"
        
        # 兼容旧的category字段
        category = values.get('category')
        if category:
            journal_type, _ = cls._parse_category(category)
            return journal_type
        return None
    
    @validator('issue_period', pre=True, always=True)  
    def parse_issue_period(cls, v, values):
        """从price_date字段解析期数信息"""
        if v is not None:
            return v
        
        # 优先使用price_date字段
        price_date = values.get('price_date')
        if price_date:
            # 将YYYY-MM格式转换为YYYY年MM月格式
            try:
                year, month = price_date.split('-')
                return f"{year}年{month.zfill(2)}月"
            except:
                return price_date
        
        # 兼容旧的category字段
        category = values.get('category')
        if category:
            _, issue_period = cls._parse_category(category)
            return issue_period
        return None
    
    @staticmethod
    def _parse_category(category: str) -> Tuple[Optional[str], Optional[str]]:
        """
        解析category字段，提取期刊类型和期数信息
        
        示例格式：
        - "municipal-杭州-2025-07" -> ("市期刊", "2025年07月")
        - "provincial-浙江-2024-12" -> ("省期刊", "2024年12月")
        - "municipal-2025-02" -> ("市期刊", "2025年02月")
        """
        if not category:
            return None, None
        
        try:
            # 解析category字段
            parts = category.split('-')
            if len(parts) >= 3:
                source_type = parts[0]
                
                # 转换期刊类型
                journal_type = "市期刊" if source_type == 'municipal' else "省期刊"
                
                # 根据部分数量确定年月位置
                if len(parts) == 3:
                    # 格式: municipal-2025-07
                    year = parts[1]
                    month = parts[2]
                elif len(parts) == 4:
                    # 格式: municipal-杭州-2025-07
                    year = parts[2]
                    month = parts[3]
                else:
                    # 尝试找到年月信息（最后两个数字部分）
                    year_month_parts = [p for p in parts[-2:] if p.isdigit() and len(p) >= 2]
                    if len(year_month_parts) >= 2:
                        year = year_month_parts[0]
                        month = year_month_parts[1]
                    else:
                        return journal_type, None
                
                # 格式化期数
                issue_period = f"{year}年{month.zfill(2)}月"
                
                return journal_type, issue_period
            else:
                # 如果不符合预期格式，尝试其他解析方式或直接返回原始值
                return None, category
        except Exception:
            return None, category


class MaterialAliasBase(BaseModel):
    """材料别名基础模式"""
    alias_name: str = Field(..., min_length=1, max_length=200, description="别名")
    alias_specification: Optional[str] = Field(None, description="别名规格")
    similarity_score: float = Field(default=1.0, ge=0, le=1, description="相似度评分")


class MaterialAliasCreate(MaterialAliasBase):
    """创建材料别名模式"""
    base_material_id: int = Field(..., description="基准材料ID")


class MaterialAliasResponse(MaterialAliasBase):
    """材料别名响应模式"""
    id: int
    base_material_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BaseMaterialImportRequest(BaseModel):
    """基准材料导入请求模式"""
    sheet_name: Optional[str] = Field(None, description="工作表名称")
    column_mapping: dict = Field(..., description="列映射关系")
    start_row: int = Field(default=1, ge=1, description="开始行号")
    batch_size: int = Field(default=1000, ge=1, le=10000, description="批量处理大小")
    
    @validator('column_mapping')
    def validate_column_mapping(cls, v):
        required_fields = ['name', 'unit', 'price', 'region', 'effective_date']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'缺少必需的字段映射: {field}')
        return v


class BaseMaterialImportResponse(BaseModel):
    """基准材料导入响应模式"""
    imported_count: int
    skipped_count: int
    error_count: int
    validation_errors: List[str] = []
    sample_materials: List[BaseMaterialResponse] = []


class BaseMaterialSearchRequest(BaseModel):
    """基准材料搜索请求模式"""
    query: Optional[str] = Field(None, description="搜索关键词")
    specification: Optional[str] = Field(None, description="规格型号关键词")
    category: Optional[str] = Field(None, description="材料分类")
    category_id: Optional[int] = Field(None, description="分类ID")
    region: Optional[str] = Field(None, description="适用地区")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    price_min: Optional[float] = Field(None, ge=0, description="价格下限")
    price_max: Optional[float] = Field(None, ge=0, description="价格上限")
    effective_date_start: Optional[datetime] = Field(None, description="生效日期开始")
    effective_date_end: Optional[datetime] = Field(None, description="生效日期结束")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    
    # 信息价类型相关字段
    price_type: Optional[str] = Field(None, description="信息价类型 (provincial/municipal)")
    price_date: Optional[str] = Field(None, description="信息价期数 (YYYY-MM)")
    price_source: Optional[str] = Field(None, description="信息价来源")
    
    @validator('price_max')
    def validate_price_range(cls, v, values):
        if v is not None and 'price_min' in values and values['price_min'] is not None:
            if v < values['price_min']:
                raise ValueError('价格上限不能小于价格下限')
        return v


class BaseMaterialPeriodDeleteRequest(BaseModel):
    """按期数批量删除基准材料请求"""
    price_date: Optional[str] = Field(None, description="信息价期数 (YYYY-MM)，为空表示未填写期数的数据")
    price_type: Optional[str] = Field(None, description="信息价类型 (provincial/municipal)")
    region: Optional[str] = Field(None, description="地区或区县")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")

    @validator('price_date', 'price_type', 'region', 'province', 'city', pre=True)
    def normalize_text_field(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            value = v.strip()
            if not value or value.lower() in {"none", "null"}:
                return None
            return value
        return str(v)


class BaseMaterialBatchOperation(BaseModel):
    """基准材料批量操作模式"""
    material_ids: List[int] = Field(..., min_items=1, description="材料ID列表")
    operation: str = Field(..., description="操作类型: verify/unverify/delete")
    verification_notes: Optional[str] = Field(None, description="验证备注")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['verify', 'unverify', 'delete']
        if v not in allowed_operations:
            raise ValueError(f'无效的操作类型，允许的操作: {", ".join(allowed_operations)}')
        return v
