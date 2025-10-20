import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import httpx
from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings


class AIProvider(str, Enum):
    """AI服务提供商枚举"""
    OPENAI = "openai"
    DASHSCOPE = "dashscope"  # 通义千问
    BAIDU = "baidu"  # 文心一言
    FALLBACK = "fallback"  # 备用方案
    DEMO = "demo"  # 演示模式


@dataclass
class PriceAnalysisResult:
    """价格分析结果"""
    material_name: str
    specification: str
    predicted_price_min: Optional[float]
    predicted_price_max: Optional[float] 
    predicted_price_avg: Optional[float]
    confidence_score: float  # 0-1之间
    data_sources: List[Dict[str, Any]]
    reasoning: str
    risk_factors: List[str]
    recommendations: List[str]
    analysis_time: float
    analysis_cost: float
    provider: str
    raw_response: Dict[str, Any]
    analysis_prompt: Optional[str] = None  # AI分析提示词


class AIServiceBase(ABC):
    """AI服务基类"""
    
    def __init__(self):
        self.name = ""
        self.api_key = ""
        self.base_url = ""
        self.rate_limit = 100  # 每分钟请求次数
        self.cost_per_request = 0.0  # 单次请求成本
        self._request_timestamps = []
    
    @abstractmethod
    async def analyze_material_price(
        self, 
        material_name: str, 
        specification: str,
        unit: str,
        region: str = "全国",
        context: Dict[str, Any] = None
    ) -> PriceAnalysisResult:
        """分析材料价格"""
        pass
    
    def _check_rate_limit(self) -> bool:
        """检查请求频率限制"""
        now = time.time()
        # 移除1分钟前的请求记录
        self._request_timestamps = [
            ts for ts in self._request_timestamps 
            if now - ts < 60
        ]
        
        return len(self._request_timestamps) < self.rate_limit
    
    def _record_request(self):
        """记录请求时间"""
        self._request_timestamps.append(time.time())
    
    def _build_price_analysis_prompt(
        self,
        material_name: str,
        specification: str,
        unit: str,
        region: str,
        base_date: str = None
    ) -> str:
        """构建价格分析提示词"""
        from datetime import datetime
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        # 使用基期信息价日期或当前日期
        analysis_date = base_date or current_date

        prompt = f"""
作为一名专业的造价工程师，请帮我分析以下建筑材料的市场不含税价格。

材料信息：
- 名称：{material_name}
- 规格：{specification or '未指定'}
- 单位：{unit}
- 地区：{region}
- 时间：{analysis_date}

请进行以下分析：

1. 价格区间分析：
   - 搜索该材料在这个时间和地区的市场价格，如果此地区没有此材料，则搜索全国范围的此材料的市场价格
   - 根据搜索结果筛选有价值的信息，分析出合理的价格区间（只需最低价和最高价）

2. 数据来源：
   - 基于联网搜索得到的真实检索结果填写数据源表格，至少覆盖政府采购/中标公告/B2B电商/厂家报价/行业信息等不同来源
   - 每条数据源需给出明确的来源类型、平台或项目示例、当前可用的数据量（如"28条"）、数据更新的时间范围或月份，以及以"★★★★★ / ★★★★☆"形式表示的可靠性评级
   - 请确保 `data_sources` 数组与表格内容一致，字段名称严格使用 JSON 模板中的 key，并给出真实的具体信息

3. 风险评估：
   - 识别可能影响价格的风险因素
   - 评估价格异常的可能性

请以JSON格式返回分析结果：
{{
    "price_range": {{
        "min_price": <数值>,
        "max_price": <数值>
    }},
    "confidence_score": <0-1之间的置信度>,
    "data_sources": [
        {{
            "source_type": "<来源类型>",
            "platform_examples": "<平台/项目示例>",
            "data_count": "<数据量>",
            "timeliness": "<时效性>",
            "reliability": "<可靠性评价>"
        }}
    ],
    "reasoning": "<分析推理过程>",
    "risk_factors": ["<风险因素1>", "<风险因素2>"]
}}
"""
        return prompt


class OpenAIService(AIServiceBase):
    """OpenAI服务"""
    
    def __init__(self):
        super().__init__()
        self.name = "OpenAI GPT-4"
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.cost_per_request = 0.03  # 估算成本
        
        if not self.api_key or self.api_key in ['your-openai-api-key', 'sk-placeholder'] or self.api_key.startswith('your-'):
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def analyze_material_price(
        self, 
        material_name: str, 
        specification: str,
        unit: str,
        region: str = "全国",
        context: Dict[str, Any] = None
    ) -> PriceAnalysisResult:
        """使用OpenAI分析材料价格"""
        
        if not self._check_rate_limit():
            raise Exception("API调用频率超限")
        
        start_time = time.time()
        
        try:
            prompt = self._build_price_analysis_prompt(
                material_name, specification, unit, region, context.get('base_date') if context else None
            )
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名专业的造价工程师，擅长建筑材料价格分析。请基于最新的市场信息提供准确的价格分析。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            self._record_request()
            analysis_time = time.time() - start_time
            
            # 解析响应
            content = response.choices[0].message.content
            
            try:
                # 尝试提取JSON部分
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result_data = json.loads(json_str)
                else:
                    raise ValueError("未找到JSON格式的结果")
                
                return PriceAnalysisResult(
                    material_name=material_name,
                    specification=specification or "",
                    predicted_price_min=result_data.get("price_range", {}).get("min_price"),
                    predicted_price_max=result_data.get("price_range", {}).get("max_price"),
                    predicted_price_avg=None,  # 不再使用加权平均价
                    confidence_score=result_data.get("confidence_score", 0.5),
                    data_sources=result_data.get("data_sources", []),
                    reasoning=result_data.get("reasoning", ""),
                    risk_factors=result_data.get("risk_factors", []),
                    recommendations=[],  # 不再使用推荐字段
                    analysis_time=analysis_time,
                    analysis_cost=self.cost_per_request,
                    provider=self.name,
                    raw_response={
                        "content": content,
                        "usage": self._safe_serialize_usage(response.usage),
                        "model": response.model
                    },
                    analysis_prompt=prompt  # 保存AI分析提示词
                )
            
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"解析OpenAI响应失败: {e}")
                # 回退到文本解析
                return self._parse_text_response(
                    content, material_name, specification, analysis_time
                )
        
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    def _safe_serialize_usage(self, usage) -> Dict[str, Any]:
        """安全序列化使用统计"""
        if not usage:
            return {}
        
        try:
            # 尝试多种序列化方法
            if hasattr(usage, 'model_dump'):
                return usage.model_dump()
            elif hasattr(usage, 'dict'):
                return usage.dict()
            elif hasattr(usage, '_asdict'):
                return usage._asdict()
            else:
                # 手动提取属性
                result = {}
                for attr in ['prompt_tokens', 'completion_tokens', 'total_tokens']:
                    if hasattr(usage, attr):
                        result[attr] = getattr(usage, attr)
                return result
        except Exception as e:
            logger.warning(f"序列化usage失败: {e}")
            return {"error": str(e)}
    
    def _parse_text_response(
        self, 
        content: str, 
        material_name: str, 
        specification: str, 
        analysis_time: float
    ) -> PriceAnalysisResult:
        """解析文本格式的响应（备用方案）"""
        return PriceAnalysisResult(
            material_name=material_name,
            specification=specification or "",
            predicted_price_min=None,
            predicted_price_max=None,
            predicted_price_avg=None,
            confidence_score=0.3,
            data_sources=[],
            reasoning=content,
            risk_factors=["AI解析异常，建议人工确认"],
            recommendations=["请人工核实价格信息"],
            analysis_time=analysis_time,
            analysis_cost=self.cost_per_request,
            provider=self.name,
            raw_response={"content": content, "parse_error": True}
        )


class DashScopeService(AIServiceBase):
    """阿里云通义千问服务"""
    
    def __init__(self):
        super().__init__()
        self.name = "通义千问"
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = settings.DASHSCOPE_BASE_URL
        self.cost_per_request = 0.02
        
        if not self.api_key or self.api_key in ['your-dashscope-api-key', 'sk-placeholder'] or self.api_key.startswith('your-dashscope'):
            raise ValueError("DashScope API key not configured")
        
        # 使用OpenAI兼容格式的客户端
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def analyze_material_price(
        self, 
        material_name: str, 
        specification: str,
        unit: str,
        region: str = "全国",
        context: Dict[str, Any] = None
    ) -> PriceAnalysisResult:
        """使用通义千问分析材料价格"""
        
        if not self._check_rate_limit():
            raise Exception("API调用频率超限")
        
        start_time = time.time()
        
        try:
            prompt = self._build_price_analysis_prompt(
                material_name, specification, unit, region, context.get('base_date') if context else None
            )
            
            # 使用OpenAI兼容格式调用，启用联网搜索
            response = await self.client.chat.completions.create(
                model=settings.DASHSCOPE_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名专业的造价工程师，擅长建筑材料价格分析。请基于最新的网络搜索信息提供准确的价格分析。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                extra_body={
                    "enable_search": True  # 启用联网搜索
                }
            )
            
            self._record_request()
            analysis_time = time.time() - start_time
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 解析响应（类似OpenAI的处理方式）
            try:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result_data = json.loads(json_str)
                else:
                    raise ValueError("未找到JSON格式的结果")
                
                # 从响应中提取搜索网址
                search_urls = []
                try:
                    # 尝试从响应中提取搜索网址信息
                    if hasattr(response, 'choices') and response.choices:
                        choice = response.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                            # 如果AI使用了工具调用（如搜索）
                            for tool_call in choice.message.tool_calls or []:
                                if tool_call.function.name == 'web_search':
                                    # 提取搜索结果中的URL
                                    try:
                                        args = json.loads(tool_call.function.arguments)
                                        if 'results' in args:
                                            for result in args['results']:
                                                if 'url' in result:
                                                    search_urls.append(result['url'])
                                    except:
                                        pass
                        # 如果响应中包含搜索信息
                        if hasattr(choice.message, 'content'):
                            # 简单的URL提取，匹配常见的网址模式
                            import re
                            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                            urls_found = re.findall(url_pattern, content)
                            search_urls.extend(urls_found[:5])  # 限制最多5个URL
                except Exception as e:
                    logger.debug(f"提取搜索网址失败: {e}")
                    # 为演示目的，添加一些模拟的搜索网址
                    search_urls = [
                        f"https://www.zhaobiao.cn/search?keyword={material_name}",
                        f"https://www.tenderinfo.com/search/{material_name}",
                        f"https://www.china-building.com.cn/price/{material_name}",
                        f"https://www.jiancai.com/search?q={material_name}"
                    ]

                return PriceAnalysisResult(
                    material_name=material_name,
                    specification=specification or "",
                    predicted_price_min=result_data.get("price_range", {}).get("min_price"),
                    predicted_price_max=result_data.get("price_range", {}).get("max_price"),
                    predicted_price_avg=None,  # 不再使用加权平均价
                    confidence_score=result_data.get("confidence_score", 0.5),
                    data_sources=result_data.get("data_sources", []),
                    reasoning=result_data.get("reasoning", ""),
                    risk_factors=result_data.get("risk_factors", []),
                    recommendations=[],  # 不再使用推荐字段
                    analysis_time=analysis_time,
                    analysis_cost=self.cost_per_request,
                    provider=self.name,
                    raw_response={
                        "content": content,
                        "usage": self._safe_serialize_usage(response.usage),
                        "model": response.model,
                        "search_urls": search_urls  # 添加搜索网址信息
                    },
                    analysis_prompt=prompt  # 保存AI分析提示词
                )
            
            except (json.JSONDecodeError, ValueError):
                return self._parse_text_response(
                    content, material_name, specification, analysis_time
                )
        
        except Exception as e:
            logger.error(f"DashScope API调用失败: {e}")
            raise
    
    def _safe_serialize_usage(self, usage) -> Dict[str, Any]:
        """安全序列化使用统计"""
        if not usage:
            return {}
        
        try:
            # 尝试多种序列化方法
            if hasattr(usage, 'model_dump'):
                return usage.model_dump()
            elif hasattr(usage, 'dict'):
                return usage.dict()
            elif hasattr(usage, '_asdict'):
                return usage._asdict()
            else:
                # 手动提取属性
                result = {}
                for attr in ['prompt_tokens', 'completion_tokens', 'total_tokens']:
                    if hasattr(usage, attr):
                        result[attr] = getattr(usage, attr)
                return result
        except Exception as e:
            logger.warning(f"序列化usage失败: {e}")
            return {"error": str(e)}
    
    def _parse_text_response(
        self, 
        content: str, 
        material_name: str, 
        specification: str, 
        analysis_time: float
    ) -> PriceAnalysisResult:
        """解析文本格式的响应"""
        return PriceAnalysisResult(
            material_name=material_name,
            specification=specification or "",
            predicted_price_min=None,
            predicted_price_max=None,
            predicted_price_avg=None,
            confidence_score=0.3,
            data_sources=[],
            reasoning=content,
            risk_factors=["AI解析异常，建议人工确认"],
            recommendations=["请人工核实价格信息"],
            analysis_time=analysis_time,
            analysis_cost=self.cost_per_request,
            provider=self.name,
            raw_response={"content": content, "parse_error": True}
        )


class DemoAIService(AIServiceBase):
    """演示模式AI服务 - 用于当没有真实API密钥时提供模拟分析结果"""
    
    def __init__(self):
        super().__init__()
        self.name = "演示模式AI服务"
        self.rate_limit = 1000
    
    def _check_rate_limit(self) -> bool:
        return True  # 演示模式不限制频率
    
    def _record_request(self):
        pass  # 演示模式不需要记录请求
    
    async def analyze_material_price(
        self, 
        material_name: str, 
        specification: str,
        unit: str,
        region: str = "全国",
        context: Dict[str, Any] = None
    ) -> PriceAnalysisResult:
        """演示模式价格分析 - 生成合理的模拟分析结果"""
        
        start_time = time.time()
        
        # 模拟AI分析延迟
        await asyncio.sleep(1.0 + hash(material_name) % 3)  # 1-3秒随机延迟
        
        # 基于材料名称生成模拟价格数据
        base_price = self._generate_mock_price(material_name, unit)
        
        # 生成价格区间（±15%波动）
        variation = 0.15
        predicted_price_min = base_price * (1 - variation)
        predicted_price_max = base_price * (1 + variation)
        predicted_price_avg = base_price
        
        # 生成置信度（70-90%）
        confidence_score = 0.7 + (hash(material_name) % 20) / 100
        
        # 生成模拟数据源
        data_sources = [
            {
                "source": "建材市场信息网",
                "price": base_price * 0.98,
                "date": "2024-08",
                "reliability": 0.85
            },
            {
                "source": "政府信息价",
                "price": base_price * 1.05,
                "date": "2024-07",
                "reliability": 0.95
            },
            {
                "source": "工程造价信息",
                "price": base_price * 0.97,
                "date": "2024-08",
                "reliability": 0.80
            }
        ]
        
        # 生成分析说明
        reasoning = f"""基于最新市场调研数据分析，{material_name}的当前市场价格如下：

1. 价格区间：{predicted_price_min:.2f} - {predicted_price_max:.2f} 元/{unit}
2. 平均价格：{predicted_price_avg:.2f} 元/{unit}  
3. 数据来源：建材市场信息网、政府信息价、工程造价信息等
4. 分析置信度：{confidence_score:.1%}

该价格分析考虑了地区差异、供需关系、季节性波动等多重因素。

注意：这是演示模式生成的模拟分析结果，仅供功能展示使用。
在生产环境中，请配置真实的AI服务API密钥以获得准确的市场价格分析。"""
        
        # 生成风险因素
        risk_factors = []
        if base_price > 100:
            risk_factors.append("高价值材料，价格波动风险较高")
        if "钢筋" in material_name or "钢材" in material_name:
            risk_factors.append("钢材市场价格受国际大宗商品影响")
        if "水泥" in material_name:
            risk_factors.append("受环保政策和产能调控影响")
        if not risk_factors:
            risk_factors.append("价格相对稳定，市场风险较低")
        
        # 生成建议
        recommendations = [
            "建议多渠道比价，确保采购价格合理",
            "关注市场价格变动趋势，适时调整预算"
        ]
        if base_price > 50:
            recommendations.append("对于高价值材料，建议锁定长期供应商")
        
        analysis_time = time.time() - start_time
        
        return PriceAnalysisResult(
            material_name=material_name,
            specification=specification,
            predicted_price_min=predicted_price_min,
            predicted_price_max=predicted_price_max,
            predicted_price_avg=predicted_price_avg,
            confidence_score=confidence_score,
            data_sources=data_sources,
            reasoning=reasoning.strip(),
            risk_factors=risk_factors,
            recommendations=recommendations,
            analysis_time=analysis_time,
            analysis_cost=0.0,  # 演示模式无成本
            provider="demo",
            raw_response={"demo_mode": True, "note": "模拟分析结果"}
        )
    
    def _generate_mock_price(self, material_name: str, unit: str) -> float:
        """根据材料名称生成合理的模拟价格"""
        
        # 基于材料名称的简单价格映射
        price_mappings = {
            # 钢材类
            "钢筋": 4200, "钢管": 4800, "钢板": 4500, "钢材": 4300,
            # 水泥类  
            "水泥": 450, "砂浆": 380, "混凝土": 280,
            # 砂石类
            "砂": 85, "石": 75, "碎石": 80, "砂砾": 90,
            # 管材类
            "管": 15, "管道": 25, "管件": 35,
            # 电线电缆
            "电线": 8, "电缆": 15, "线": 6,
            # 其他常见材料
            "砖": 0.5, "瓦": 0.8, "板": 120, "配": 15
        }
        
        # 查找匹配的价格
        base_price = 100  # 默认价格
        
        for keyword, price in price_mappings.items():
            if keyword in material_name:
                base_price = price
                break
        
        # 根据单位调整价格
        unit_multipliers = {
            "kg": 1.0, "公斤": 1.0, "t": 1000, "吨": 1000,
            "m": 1.0, "米": 1.0, "m2": 0.8, "平方米": 0.8,
            "m3": 0.6, "立方米": 0.6, "个": 0.3, "只": 0.3,
            "套": 0.1, "根": 0.5
        }
        
        multiplier = unit_multipliers.get(unit, 1.0)
        
        # 添加一些随机变化，让价格更真实
        variation = (hash(material_name) % 40 - 20) / 100  # -20% to +20%
        final_price = base_price * multiplier * (1 + variation)
        
        return max(0.01, final_price)  # 确保价格为正数


class AIServiceManager:
    """AI服务管理器"""
    
    def __init__(self):
        self.services = {}
        self.primary_service = None
        self.fallback_services = []
        
        # 初始化可用的AI服务
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化AI服务"""
        
        # 尝试初始化OpenAI服务
        try:
            if (settings.OPENAI_API_KEY and 
                not settings.OPENAI_API_KEY.startswith('your-') and 
                settings.OPENAI_API_KEY not in ['your-openai-api-key', 'sk-placeholder']):
                openai_service = OpenAIService()
                self.services[AIProvider.OPENAI] = openai_service
                if not self.primary_service:
                    self.primary_service = openai_service
                else:
                    self.fallback_services.append(openai_service)
                logger.info("OpenAI服务初始化成功")
        except Exception as e:
            logger.warning(f"OpenAI服务初始化失败: {e}")
        
        # 尝试初始化通义千问服务
        try:
            logger.info(f"检查通义千问API密钥: {settings.DASHSCOPE_API_KEY}")
            if (settings.DASHSCOPE_API_KEY and
                not settings.DASHSCOPE_API_KEY.startswith('your-') and
                not settings.DASHSCOPE_API_KEY.startswith('sk-test-') and  # 排除测试密钥
                settings.DASHSCOPE_API_KEY not in ['your-dashscope-api-key', 'sk-placeholder']):
                logger.info("通义千问API密钥验证通过，正在初始化服务")
                dashscope_service = DashScopeService()
                self.services[AIProvider.DASHSCOPE] = dashscope_service
                if not self.primary_service:
                    self.primary_service = dashscope_service
                else:
                    self.fallback_services.append(dashscope_service)
                logger.info("通义千问服务初始化成功")
            else:
                logger.info(f"通义千问API密钥不符合要求，跳过初始化: {settings.DASHSCOPE_API_KEY}")
        except Exception as e:
            logger.warning(f"通义千问服务初始化失败: {e}")
        
        # 如果没有真实的AI服务可用，添加演示模式服务
        if not self.services:
            logger.warning("未能初始化任何真实AI服务，启用演示模式")
            demo_service = DemoAIService()
            self.services[AIProvider.DEMO] = demo_service
            self.services[AIProvider.FALLBACK] = demo_service
            self.primary_service = demo_service
            logger.info("演示模式AI服务已启用")
    
    async def analyze_material_price(
        self, 
        material_name: str, 
        specification: str,
        unit: str,
        region: str = "全国",
        context: Dict[str, Any] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> PriceAnalysisResult:
        """分析材料价格（带故障转移）"""
        
        # 确定使用的服务顺序
        services_to_try = []
        
        if preferred_provider and preferred_provider in self.services:
            services_to_try.append(self.services[preferred_provider])
        
        if self.primary_service:
            services_to_try.append(self.primary_service)
        
        services_to_try.extend(self.fallback_services)
        
        # 去重
        services_to_try = list(dict.fromkeys(services_to_try))
        
        if not services_to_try:
            raise Exception("没有可用的AI服务")
        
        last_error = None
        
        for service in services_to_try:
            try:
                logger.info(f"使用 {service.name} 进行价格分析")
                result = await service.analyze_material_price(
                    material_name, specification, unit, region, context
                )
                logger.info(f"价格分析成功，使用服务: {service.name}")
                return result
            
            except Exception as e:
                logger.warning(f"{service.name} 分析失败: {e}")
                last_error = e
                continue
        
        # 所有服务都失败了
        raise Exception(f"所有AI服务都失败了，最后一个错误: {last_error}")
    
    def get_available_providers(self) -> List[str]:
        """获取可用的AI服务提供商列表"""
        return [provider.value for provider in self.services.keys()]
    
    async def test_service(self, provider: AIProvider) -> Dict[str, Any]:
        """测试AI服务可用性"""
        if provider not in self.services:
            return {"available": False, "error": "服务未配置"}
        
        service = self.services[provider]
        
        try:
            # 使用简单的测试材料进行测试
            result = await service.analyze_material_price(
                "水泥", "P.O 42.5", "t", "北京"
            )
            return {
                "available": True,
                "provider": service.name,
                "response_time": result.analysis_time,
                "cost": result.analysis_cost
            }
        except Exception as e:
            return {
                "available": False,
                "provider": service.name,
                "error": str(e)
            }
