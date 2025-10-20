from typing import Dict, List, Any, Optional, Tuple
import math
from dataclasses import dataclass
from enum import Enum
import statistics
from datetime import datetime, timedelta
from loguru import logger
import numpy as np


class RiskLevel(str, Enum):
    """风险等级枚举"""
    LOW = "low"          # 低风险
    MEDIUM = "medium"    # 中风险  
    HIGH = "high"        # 高风险
    CRITICAL = "critical" # 严重风险


class PriceStatus(str, Enum):
    """价格状态枚举"""
    REASONABLE = "reasonable"      # 合理
    UNDERPRICED = "underpriced"   # 价格偏低
    OVERPRICED = "overpriced"     # 价格偏高
    ABNORMAL = "abnormal"         # 异常价格
    UNKNOWN = "unknown"           # 无法判断


@dataclass
class PriceReasonabilityResult:
    """价格合理性分析结果"""
    material_id: int
    material_name: str
    original_price: float
    predicted_price_min: Optional[float]
    predicted_price_max: Optional[float]
    predicted_price_avg: Optional[float]
    
    # 合理性分析
    price_status: PriceStatus
    risk_level: RiskLevel
    price_variance: float  # 价格偏差百分比
    
    # 分析详情
    analysis_details: Dict[str, Any]
    risk_factors: List[str]
    recommendations: List[str]
    
    # 统计信息
    confidence_score: float
    analysis_method: str
    created_at: datetime


class PriceReasonabilityAnalyzer:
    """价格合理性分析器"""
    
    # 价格偏差阈值配置
    VARIANCE_THRESHOLDS = {
        'reasonable': 15.0,      # ±15%内认为合理
        'moderate': 30.0,        # ±30%内认为中等风险
        'high': 50.0,           # ±50%内认为高风险
        'critical': 100.0       # 超过±100%认为严重异常
    }
    
    # 置信度阈值
    CONFIDENCE_THRESHOLDS = {
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4
    }
    
    def __init__(self):
        """初始化分析器"""
        self.analysis_methods = [
            'ai_prediction_comparison',
            'statistical_analysis',
            'market_trend_analysis',
            'historical_comparison'
        ]
    
    def analyze_price_reasonability(
        self,
        material_id: int,
        material_name: str,
        original_price: float,
        ai_analysis_result: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
        market_context: Optional[Dict[str, Any]] = None
    ) -> PriceReasonabilityResult:
        """综合分析价格合理性"""
        
        # 提取AI分析结果
        predicted_min = ai_analysis_result.get('predicted_price_min')
        predicted_max = ai_analysis_result.get('predicted_price_max')
        predicted_avg = ai_analysis_result.get('predicted_price_avg')
        ai_confidence = ai_analysis_result.get('confidence_score', 0.5)
        
        # 执行多维度分析
        analysis_results = []
        
        # 1. AI预测区间对比分析
        if predicted_min and predicted_max:
            ai_result = self._analyze_against_ai_prediction(
                original_price, predicted_min, predicted_max, predicted_avg
            )
            analysis_results.append(ai_result)
        
        # 2. 统计学异常检测
        if historical_data:
            statistical_result = self._statistical_analysis(
                original_price, historical_data
            )
            analysis_results.append(statistical_result)
        
        # 3. 市场趋势分析
        if market_context:
            trend_result = self._market_trend_analysis(
                original_price, market_context
            )
            analysis_results.append(trend_result)
        
        # 综合判断
        final_result = self._synthesize_analysis_results(
            material_id, material_name, original_price,
            predicted_min, predicted_max, predicted_avg,
            analysis_results, ai_confidence
        )
        
        return final_result
    
    def _analyze_against_ai_prediction(
        self,
        original_price: float,
        predicted_min: float,
        predicted_max: float,
        predicted_avg: Optional[float]
    ) -> Dict[str, Any]:
        """基于AI预测区间分析"""
        
        analysis = {
            'method': 'ai_prediction_comparison',
            'weight': 0.6  # AI分析权重最高
        }
        
        # 判断价格是否在预测区间内
        if predicted_min <= original_price <= predicted_max:
            analysis['status'] = PriceStatus.REASONABLE
            analysis['risk_level'] = RiskLevel.LOW
            analysis['variance'] = 0  # 区间内认为无偏差
        else:
            # 计算偏差程度
            if predicted_avg:
                variance = abs(original_price - predicted_avg) / predicted_avg * 100
            else:
                # 使用区间中点计算
                mid_price = (predicted_min + predicted_max) / 2
                variance = abs(original_price - mid_price) / mid_price * 100
            
            analysis['variance'] = variance
            
            # 判断偏高还是偏低
            if original_price > predicted_max:
                analysis['status'] = PriceStatus.OVERPRICED
                analysis['direction'] = 'high'
            else:
                analysis['status'] = PriceStatus.UNDERPRICED  
                analysis['direction'] = 'low'
            
            # 根据偏差程度确定风险等级
            analysis['risk_level'] = self._calculate_risk_level(variance)
        
        return analysis
    
    def _statistical_analysis(
        self,
        original_price: float,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """统计学分析"""
        
        analysis = {
            'method': 'statistical_analysis',
            'weight': 0.3
        }
        
        if len(historical_data) < 3:
            analysis['status'] = PriceStatus.UNKNOWN
            analysis['risk_level'] = RiskLevel.MEDIUM
            return analysis
        
        # 提取历史价格数据
        prices = [item.get('price', 0) for item in historical_data if item.get('price')]
        if not prices:
            analysis['status'] = PriceStatus.UNKNOWN
            analysis['risk_level'] = RiskLevel.MEDIUM
            return analysis
        
        # 计算统计指标
        mean_price = statistics.mean(prices)
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # Z-score分析
        if std_dev > 0:
            z_score = abs(original_price - mean_price) / std_dev
            analysis['z_score'] = z_score
            
            # 基于Z-score判断异常程度
            if z_score <= 1.96:  # 95%置信区间
                analysis['status'] = PriceStatus.REASONABLE
                analysis['risk_level'] = RiskLevel.LOW
            elif z_score <= 2.58:  # 99%置信区间
                analysis['status'] = PriceStatus.OVERPRICED if original_price > mean_price else PriceStatus.UNDERPRICED
                analysis['risk_level'] = RiskLevel.MEDIUM
            else:
                analysis['status'] = PriceStatus.ABNORMAL
                analysis['risk_level'] = RiskLevel.HIGH
            
            # 计算偏差百分比
            analysis['variance'] = abs(original_price - mean_price) / mean_price * 100
        else:
            # 标准差为0，所有历史价格相同
            if abs(original_price - mean_price) / mean_price * 100 < 5:
                analysis['status'] = PriceStatus.REASONABLE
                analysis['risk_level'] = RiskLevel.LOW
            else:
                analysis['status'] = PriceStatus.ABNORMAL
                analysis['risk_level'] = RiskLevel.HIGH
            
            analysis['variance'] = abs(original_price - mean_price) / mean_price * 100
        
        return analysis
    
    def _market_trend_analysis(
        self,
        original_price: float,
        market_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """市场趋势分析"""
        
        analysis = {
            'method': 'market_trend_analysis',
            'weight': 0.1
        }
        
        # 获取市场信息
        market_trend = market_context.get('trend', 'stable')  # stable/rising/falling
        inflation_rate = market_context.get('inflation_rate', 0)  # 通胀率
        season_factor = market_context.get('season_factor', 1.0)  # 季节因子
        
        # 基于市场趋势调整判断
        trend_adjustment = 0
        
        if market_trend == 'rising':
            trend_adjustment = 5  # 上涨趋势，价格偏高5%内可接受
        elif market_trend == 'falling':
            trend_adjustment = -5  # 下跌趋势，价格偏低5%内可接受
        
        # 考虑通胀因素
        inflation_adjustment = inflation_rate * 100  # 转换为百分比
        
        # 总体市场调整
        total_adjustment = trend_adjustment + inflation_adjustment
        
        analysis['trend_adjustment'] = total_adjustment
        analysis['market_trend'] = market_trend
        analysis['inflation_rate'] = inflation_rate
        
        # 简化的市场趋势判断
        analysis['status'] = PriceStatus.REASONABLE  # 市场趋势分析权重较低
        analysis['risk_level'] = RiskLevel.LOW
        analysis['variance'] = 0
        
        return analysis
    
    def _synthesize_analysis_results(
        self,
        material_id: int,
        material_name: str,
        original_price: float,
        predicted_min: Optional[float],
        predicted_max: Optional[float],
        predicted_avg: Optional[float],
        analysis_results: List[Dict[str, Any]],
        ai_confidence: float
    ) -> PriceReasonabilityResult:
        """综合分析结果"""
        
        if not analysis_results:
            # 无法进行分析
            return PriceReasonabilityResult(
                material_id=material_id,
                material_name=material_name,
                original_price=original_price,
                predicted_price_min=predicted_min,
                predicted_price_max=predicted_max,
                predicted_price_avg=predicted_avg,
                price_status=PriceStatus.UNKNOWN,
                risk_level=RiskLevel.MEDIUM,
                price_variance=0,
                analysis_details={},
                risk_factors=["数据不足，无法进行准确分析"],
                recommendations=["建议人工核实价格信息"],
                confidence_score=0.3,
                analysis_method="insufficient_data",
                created_at=datetime.utcnow()
            )
        
        # 加权计算综合结果
        total_weight = sum(result.get('weight', 0) for result in analysis_results)
        weighted_variance = 0
        status_votes = {}
        
        for result in analysis_results:
            weight = result.get('weight', 0) / total_weight if total_weight > 0 else 1 / len(analysis_results)
            variance = result.get('variance', 0)
            weighted_variance += variance * weight
            
            # 收集状态投票
            status = result.get('status', PriceStatus.UNKNOWN)
            status_votes[status] = status_votes.get(status, 0) + weight
        
        # 确定最终状态
        final_status = max(status_votes.keys(), key=lambda k: status_votes[k])

        # 方案A：基于偏差平滑+不确定度+置信度的风险评分
        # v: 绝对偏差（%）；w: 区间相对宽度；c: AI置信度；方向加成：偏高更谨慎
        v = abs(weighted_variance)

        # 预测均价作为基准
        denom = None
        if predicted_avg:
            denom = predicted_avg
        elif predicted_min is not None and predicted_max is not None:
            denom = (predicted_min + predicted_max) / 2 if (predicted_min + predicted_max) else None

        w = 0.0
        if denom and denom != 0 and predicted_min is not None and predicted_max is not None:
            try:
                w = max(0.0, (predicted_max - predicted_min) / denom)
            except Exception:
                w = 0.0

        c = ai_confidence or 0.5
        # 原价相对基准的方向（高价更高权重）
        base = denom if denom else 0
        direction_factor = 1.15 if (base and original_price > base) else 0.95

        # 平滑函数（偏差）
        g = 1.0 / (1.0 + math.exp(-(v - 15.0) / 7.0))  # 约15%拐点，>30%接近1
        # 不确定度（区间宽度）
        h = min(1.0, max(0.0, w / 0.30))  # 30%视为高不确定

        final_risk_score = direction_factor * (0.6 * g + 0.2 * (1.0 - c) + 0.2 * h)
        final_risk_level = self._score_to_risk_level(final_risk_score)
        
        # 生成分析详情
        analysis_details = {
            'analysis_results': analysis_results,
            'weighted_variance': weighted_variance,
            'final_risk_score': final_risk_score,
            'status_votes': status_votes,
            'ai_confidence': ai_confidence,
            'scheme': 'A',
            'uncertainty': {
                'v_abs_variance': v,
                'range_width_ratio': w,
                'direction_factor': direction_factor,
                'g_variance_component': g,
                'h_uncertainty_component': h
            }
        }
        
        # 生成风险因素和建议
        risk_factors = self._generate_risk_factors(
            final_status, final_risk_level, weighted_variance, ai_confidence
        )
        
        recommendations = self._generate_recommendations(
            final_status, final_risk_level, weighted_variance
        )
        
        # 计算最终置信度
        final_confidence = self._calculate_final_confidence(
            ai_confidence, len(analysis_results), final_risk_level
        )
        
        return PriceReasonabilityResult(
            material_id=material_id,
            material_name=material_name,
            original_price=original_price,
            predicted_price_min=predicted_min,
            predicted_price_max=predicted_max,
            predicted_price_avg=predicted_avg,
            price_status=final_status,
            risk_level=final_risk_level,
            price_variance=weighted_variance,
            analysis_details=analysis_details,
            risk_factors=risk_factors,
            recommendations=recommendations,
            confidence_score=final_confidence,
            analysis_method="综合分析",
            created_at=datetime.utcnow()
        )
    
    def _calculate_risk_level(self, variance: float) -> RiskLevel:
        """根据偏差程度计算风险等级"""
        if variance <= self.VARIANCE_THRESHOLDS['reasonable']:
            return RiskLevel.LOW
        elif variance <= self.VARIANCE_THRESHOLDS['moderate']:
            return RiskLevel.MEDIUM
        elif variance <= self.VARIANCE_THRESHOLDS['high']:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _risk_level_to_score(self, risk_level: RiskLevel) -> float:
        """风险等级转评分"""
        mapping = {
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 1.0
        }
        return mapping.get(risk_level, 0.5)
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """评分转风险等级（方案A阈值：0.25/0.5/0.75）"""
        if score <= 0.25:
            return RiskLevel.LOW
        elif score <= 0.5:
            return RiskLevel.MEDIUM
        elif score <= 0.75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_risk_factors(
        self,
        status: PriceStatus,
        risk_level: RiskLevel,
        variance: float,
        ai_confidence: float
    ) -> List[str]:
        """生成风险因素说明"""
        
        factors = []
        
        if status == PriceStatus.OVERPRICED:
            factors.append(f"价格偏高{variance:.1f}%，存在成本超支风险")
            if risk_level == RiskLevel.HIGH:
                factors.append("价格严重偏离市场水平，建议重新询价")
        
        elif status == PriceStatus.UNDERPRICED:
            factors.append(f"价格偏低{variance:.1f}%，可能存在质量风险")
            if risk_level == RiskLevel.HIGH:
                factors.append("价格异常偏低，需警惕材料质量问题")
        
        elif status == PriceStatus.ABNORMAL:
            factors.append("价格异常，偏离正常市场范围")
            factors.append("建议详细核实材料规格和供应商资质")
        
        if ai_confidence < 0.5:
            factors.append("AI分析置信度较低，建议人工复核")
        
        if risk_level == RiskLevel.CRITICAL:
            factors.append("价格风险等级为严重，需立即关注")
        
        return factors or ["暂无特殊风险因素"]
    
    def _generate_recommendations(
        self,
        status: PriceStatus,
        risk_level: RiskLevel,
        variance: float
    ) -> List[str]:
        """生成处理建议"""
        
        recommendations = []
        
        if status == PriceStatus.REASONABLE:
            recommendations.append("价格在合理范围内，可以接受")
        
        elif status == PriceStatus.OVERPRICED:
            recommendations.append("建议与供应商协商降价")
            if variance > 30:
                recommendations.append("建议寻找替代供应商")
        
        elif status == PriceStatus.UNDERPRICED:
            recommendations.append("核实材料规格是否符合要求")
            recommendations.append("确认供应商资质和产品质量")
        
        elif status == PriceStatus.ABNORMAL:
            recommendations.append("立即核实价格信息来源")
            recommendations.append("重新获取市场询价")
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("建议暂停采购，详细调研后再决定")
        
        return recommendations or ["建议进一步核实相关信息"]
    
    def _calculate_final_confidence(
        self,
        ai_confidence: float,
        analysis_count: int,
        risk_level: RiskLevel
    ) -> float:
        """计算最终分析置信度"""
        
        # 基础置信度来自AI分析
        base_confidence = ai_confidence
        
        # 分析方法数量加成
        method_bonus = min(0.2, analysis_count * 0.1)
        
        # 风险等级调整
        if risk_level == RiskLevel.CRITICAL:
            risk_penalty = -0.1  # 严重风险降低置信度
        elif risk_level == RiskLevel.LOW:
            risk_bonus = 0.1     # 低风险提高置信度
        else:
            risk_penalty = 0
            risk_bonus = 0
        
        final_confidence = base_confidence + method_bonus + risk_bonus + risk_penalty
        
        # 限制在0-1范围内
        return max(0.0, min(1.0, final_confidence))
    
    def batch_analyze_materials(
        self,
        materials_data: List[Dict[str, Any]],
        market_context: Optional[Dict[str, Any]] = None
    ) -> List[PriceReasonabilityResult]:
        """批量分析材料价格合理性"""
        
        results = []
        
        for material_data in materials_data:
            try:
                result = self.analyze_price_reasonability(
                    material_id=material_data['material_id'],
                    material_name=material_data['material_name'],
                    original_price=material_data['original_price'],
                    ai_analysis_result=material_data['ai_analysis_result'],
                    historical_data=material_data.get('historical_data'),
                    market_context=market_context
                )
                results.append(result)
            
            except Exception as e:
                logger.error(f"分析材料 {material_data.get('material_id')} 时出错: {e}")
                # 创建错误结果
                error_result = PriceReasonabilityResult(
                    material_id=material_data['material_id'],
                    material_name=material_data['material_name'],
                    original_price=material_data['original_price'],
                    predicted_price_min=None,
                    predicted_price_max=None,
                    predicted_price_avg=None,
                    price_status=PriceStatus.UNKNOWN,
                    risk_level=RiskLevel.MEDIUM,
                    price_variance=0,
                    analysis_details={"error": str(e)},
                    risk_factors=[f"分析过程出错: {str(e)}"],
                    recommendations=["建议人工审核"],
                    confidence_score=0.1,
                    analysis_method="error_handling",
                    created_at=datetime.utcnow()
                )
                results.append(error_result)
        
        return results


class PriceAnomalyDetector:
    """价格异常检测器"""
    
    def __init__(self):
        self.detection_methods = [
            'statistical_outlier',
            'isolation_forest',
            'local_outlier_factor'
        ]
    
    def detect_price_anomalies(
        self,
        project_materials: List[Dict[str, Any]],
        detection_sensitivity: float = 0.1  # 异常检测敏感度
    ) -> List[Dict[str, Any]]:
        """检测项目中的价格异常"""
        
        if len(project_materials) < 5:
            logger.warning("材料数量不足，无法进行有效的异常检测")
            return []
        
        anomalies = []
        
        # 按材料类别分组检测
        material_groups = self._group_materials_by_category(project_materials)
        
        for category, materials in material_groups.items():
            if len(materials) < 3:
                continue
            
            # 提取价格数据
            prices = [m['unit_price'] for m in materials if m.get('unit_price')]
            if not prices:
                continue
            
            # 统计学异常检测
            category_anomalies = self._statistical_outlier_detection(
                materials, prices, detection_sensitivity
            )
            
            anomalies.extend(category_anomalies)
        
        return anomalies
    
    def _group_materials_by_category(
        self,
        materials: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """按类别分组材料"""
        
        groups = {}
        
        for material in materials:
            category = material.get('category', '未分类')
            if category not in groups:
                groups[category] = []
            groups[category].append(material)
        
        return groups
    
    def _statistical_outlier_detection(
        self,
        materials: List[Dict[str, Any]],
        prices: List[float],
        sensitivity: float
    ) -> List[Dict[str, Any]]:
        """统计学异常检测"""
        
        if len(prices) < 3:
            return []
        
        # 计算四分位数和IQR
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1
        
        # 计算异常边界
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # 根据敏感度调整边界
        range_adjustment = iqr * sensitivity
        lower_bound -= range_adjustment
        upper_bound += range_adjustment
        
        anomalies = []
        
        for material in materials:
            price = material.get('unit_price')
            if price and (price < lower_bound or price > upper_bound):
                anomaly = {
                    'material_id': material['id'],
                    'material_name': material['material_name'],
                    'unit_price': price,
                    'anomaly_type': 'price_outlier',
                    'severity': 'high' if (price < lower_bound * 0.5 or price > upper_bound * 2) else 'medium',
                    'bounds': {
                        'lower': lower_bound,
                        'upper': upper_bound
                    },
                    'category': material.get('category', '未分类')
                }
                anomalies.append(anomaly)
        
        return anomalies
