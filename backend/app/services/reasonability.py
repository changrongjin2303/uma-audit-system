from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta
from loguru import logger

from app.models.project import ProjectMaterial
from app.models.analysis import PriceAnalysis, AnalysisStatus
from app.models.material import BaseMaterial
from app.utils.price_reasonability import (
    PriceReasonabilityAnalyzer, PriceAnomalyDetector, 
    PriceReasonabilityResult, RiskLevel, PriceStatus
)


class ReasonabilityAnalysisService:
    """价格合理性分析服务"""
    
    def __init__(self):
        self.analyzer = PriceReasonabilityAnalyzer()
        self.anomaly_detector = PriceAnomalyDetector()
    
    async def analyze_project_price_reasonability(
        self,
        db: AsyncSession,
        project_id: int,
        force_reanalyze: bool = False,
        detection_sensitivity: float = 0.1
    ) -> Dict[str, Any]:
        """分析项目材料价格合理性"""
        
        logger.info(f"开始分析项目 {project_id} 的价格合理性")
        
        # 获取项目已完成AI分析的材料
        analyzed_materials = await self._get_analyzed_materials(db, project_id)
        
        if not analyzed_materials:
            return {
                'project_id': project_id,
                'message': '没有已完成AI分析的材料',
                'total_materials': 0,
                'analyzed_count': 0,
                'reasonable_count': 0,
                'unreasonable_count': 0,
                'high_risk_count': 0
            }
        
        # 准备分析数据
        materials_data = []
        for material, analysis in analyzed_materials:
            if not material.unit_price:
                continue  # 跳过没有原始价格的材料
            
            material_data = {
                'material_id': material.id,
                'material_name': material.material_name,
                'original_price': material.unit_price,
                'ai_analysis_result': {
                    'predicted_price_min': analysis.predicted_price_min,
                    'predicted_price_max': analysis.predicted_price_max,
                    'predicted_price_avg': analysis.predicted_price_avg,
                    'confidence_score': analysis.confidence_score or 0.5
                },
                'historical_data': await self._get_historical_data(db, material.material_name, material.unit)
            }
            materials_data.append(material_data)
        
        if not materials_data:
            return {
                'project_id': project_id,
                'message': '没有可分析的有价格材料',
                'total_materials': len(analyzed_materials),
                'analyzed_count': 0,
                'reasonable_count': 0,
                'unreasonable_count': 0,
                'high_risk_count': 0
            }
        
        # 获取市场环境信息
        market_context = await self._get_market_context(db, project_id)
        
        # 执行合理性分析
        reasonability_results = self.analyzer.batch_analyze_materials(
            materials_data, market_context
        )
        
        # 执行异常检测
        anomaly_results = self.anomaly_detector.detect_price_anomalies(
            [{'id': m['material_id'], 'material_name': m['material_name'], 
              'unit_price': m['original_price'], 'category': 'default'} 
             for m in materials_data],
            detection_sensitivity
        )
        
        # 更新数据库中的分析结果
        await self._update_reasonability_results(db, reasonability_results, anomaly_results)
        
        # 统计结果
        stats = self._calculate_analysis_statistics(reasonability_results)
        
        return {
            'project_id': project_id,
            'total_materials': len(reasonability_results),
            'analyzed_count': len(reasonability_results),
            'reasonable_count': stats['reasonable_count'],
            'unreasonable_count': stats['unreasonable_count'],
            'high_risk_count': stats['high_risk_count'],
            'critical_risk_count': stats['critical_risk_count'],
            'anomaly_count': len(anomaly_results),
            'average_confidence': stats['average_confidence'],
            'price_variance_stats': stats['variance_stats']
        }
    
    async def get_unreasonable_materials(
        self,
        db: AsyncSession,
        project_id: int,
        risk_level: Optional[RiskLevel] = None,
        price_status: Optional[PriceStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取价格不合理的材料列表"""
        
        # 构建查询
        stmt = (
            select(ProjectMaterial, PriceAnalysis)
            .join(PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id)
            .where(ProjectMaterial.project_id == project_id)
        )
        
        # 添加过滤条件
        if risk_level:
            stmt = stmt.where(PriceAnalysis.risk_level == risk_level.value)
        
        if price_status:
            # 根据价格状态过滤
            if price_status == PriceStatus.REASONABLE:
                stmt = stmt.where(PriceAnalysis.is_reasonable == True)
            elif price_status in [PriceStatus.OVERPRICED, PriceStatus.UNDERPRICED, PriceStatus.ABNORMAL]:
                stmt = stmt.where(PriceAnalysis.is_reasonable == False)
        
        stmt = stmt.offset(skip).limit(limit).order_by(PriceAnalysis.updated_at.desc())
        
        result = await db.execute(stmt)
        materials_analyses = result.all()
        
        # 格式化结果
        unreasonable_materials = []
        for material, analysis in materials_analyses:
            material_info = {
                'material_id': material.id,
                'material_name': material.material_name,
                'specification': material.specification,
                'unit': material.unit,
                'original_price': material.unit_price,
                'predicted_price_min': analysis.predicted_price_min,
                'predicted_price_max': analysis.predicted_price_max,
                'predicted_price_avg': analysis.predicted_price_avg,
                'is_reasonable': analysis.is_reasonable,
                'price_variance': analysis.price_variance,
                'risk_level': analysis.risk_level,
                'confidence_score': analysis.confidence_score,
                'risk_factors': analysis.risk_factors,
                'recommendations': analysis.recommendations,
                'analysis_reasoning': analysis.analysis_reasoning,
                'created_at': analysis.created_at,
                'updated_at': analysis.updated_at
            }
            unreasonable_materials.append(material_info)
        
        return unreasonable_materials
    
    async def get_project_risk_summary(
        self,
        db: AsyncSession,
        project_id: int
    ) -> Dict[str, Any]:
        """获取项目风险汇总"""
        
        # 获取所有分析结果
        stmt = (
            select(ProjectMaterial, PriceAnalysis)
            .join(PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id)
            .where(
                and_(
                    ProjectMaterial.project_id == project_id,
                    PriceAnalysis.status == AnalysisStatus.COMPLETED
                )
            )
        )
        
        result = await db.execute(stmt)
        materials_analyses = result.all()
        
        if not materials_analyses:
            return {
                'project_id': project_id,
                'total_materials': 0,
                'risk_summary': {},
                'financial_impact': {},
                'top_risks': []
            }
        
        # 风险统计
        risk_stats = {
            'low': 0,
            'medium': 0, 
            'high': 0,
            'critical': 0
        }
        
        # 财务影响统计
        total_amount = 0
        potential_savings = 0
        potential_overspend = 0
        
        high_risk_materials = []
        
        for material, analysis in materials_analyses:
            # 统计风险等级
            risk_level = analysis.risk_level or 'medium'
            risk_stats[risk_level] = risk_stats.get(risk_level, 0) + 1
            
            # 计算财务影响
            if material.unit_price and material.quantity:
                material_total = material.unit_price * material.quantity
                total_amount += material_total
                
                # 计算潜在节约或超支
                if analysis.predicted_price_avg and analysis.price_variance:
                    variance_amount = material_total * (abs(analysis.price_variance) / 100)
                    
                    if analysis.price_variance > 0:  # 价格偏高
                        potential_savings += variance_amount
                    else:  # 价格偏低（可能质量风险）
                        potential_overspend += variance_amount
            
            # 收集高风险材料
            if risk_level in ['high', 'critical']:
                high_risk_materials.append({
                    'material_name': material.material_name,
                    'risk_level': risk_level,
                    'price_variance': analysis.price_variance,
                    'amount': material.unit_price * material.quantity if material.unit_price and material.quantity else 0
                })
        
        # 按金额排序高风险材料
        high_risk_materials.sort(key=lambda x: x['amount'], reverse=True)
        
        return {
            'project_id': project_id,
            'total_materials': len(materials_analyses),
            'risk_summary': {
                'distribution': risk_stats,
                'high_risk_rate': (risk_stats['high'] + risk_stats['critical']) / len(materials_analyses) * 100
            },
            'financial_impact': {
                'total_amount': total_amount,
                'potential_savings': potential_savings,
                'potential_overspend': potential_overspend,
                'risk_ratio': (potential_savings + potential_overspend) / total_amount * 100 if total_amount > 0 else 0
            },
            'top_risks': high_risk_materials[:10]  # 前10个高风险材料
        }
    
    async def manual_adjust_reasonability(
        self,
        db: AsyncSession,
        material_id: int,
        is_reasonable: bool,
        risk_level: RiskLevel,
        notes: str,
        user_id: int
    ) -> bool:
        """人工调整合理性判断"""
        
        # 获取分析记录
        stmt = select(PriceAnalysis).where(PriceAnalysis.material_id == material_id)
        result = await db.execute(stmt)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            return False
        
        # 更新分析结果
        analysis.is_reasonable = is_reasonable
        analysis.risk_level = risk_level.value
        analysis.is_reviewed = True
        analysis.reviewed_by = user_id
        analysis.review_notes = notes
        analysis.reviewed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(analysis)
        
        logger.info(f"用户 {user_id} 调整了材料 {material_id} 的合理性判断")
        
        return True
    
    async def _get_analyzed_materials(
        self,
        db: AsyncSession,
        project_id: int
    ) -> List[tuple]:
        """获取已完成AI分析的材料"""
        
        stmt = (
            select(ProjectMaterial, PriceAnalysis)
            .join(PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id)
            .where(
                and_(
                    ProjectMaterial.project_id == project_id,
                    PriceAnalysis.status == AnalysisStatus.COMPLETED
                )
            )
        )
        
        result = await db.execute(stmt)
        return result.all()
    
    async def _get_historical_data(
        self,
        db: AsyncSession,
        material_name: str,
        unit: str,
        days_back: int = 365
    ) -> List[Dict[str, Any]]:
        """获取历史价格数据"""
        
        # 从基准材料库获取相似材料的历史数据
        stmt = select(BaseMaterial).where(
            and_(
                BaseMaterial.name.ilike(f"%{material_name}%"),
                BaseMaterial.unit == unit,
                BaseMaterial.effective_date >= datetime.utcnow() - timedelta(days=days_back)
            )
        ).limit(20)
        
        result = await db.execute(stmt)
        base_materials = result.scalars().all()
        
        historical_data = []
        for bm in base_materials:
            historical_data.append({
                'price': bm.price,
                'date': bm.effective_date,
                'region': bm.region,
                'source': bm.source
            })
        
        return historical_data
    
    async def _get_market_context(
        self,
        db: AsyncSession,
        project_id: int
    ) -> Dict[str, Any]:
        """获取市场环境信息"""
        
        # 简化的市场环境信息，实际应用中可以从外部数据源获取
        return {
            'trend': 'stable',        # 市场趋势：stable/rising/falling
            'inflation_rate': 0.03,   # 通胀率
            'season_factor': 1.0,     # 季节因子
            'region': '全国',         # 地区
            'analysis_date': datetime.utcnow()
        }
    
    async def _update_reasonability_results(
        self,
        db: AsyncSession,
        reasonability_results: List[PriceReasonabilityResult],
        anomaly_results: List[Dict[str, Any]]
    ):
        """更新合理性分析结果到数据库"""
        
        # 创建异常材料ID集合，用于标记
        anomaly_material_ids = {anomaly['material_id'] for anomaly in anomaly_results}
        
        for result in reasonability_results:
            # 获取对应的分析记录
            stmt = select(PriceAnalysis).where(
                PriceAnalysis.material_id == result.material_id
            )
            db_result = await db.execute(stmt)
            analysis = db_result.scalar_one_or_none()
            
            if not analysis:
                continue
            
            # 更新合理性分析结果
            analysis.is_reasonable = (result.price_status == PriceStatus.REASONABLE)
            analysis.price_variance = result.price_variance
            analysis.risk_level = result.risk_level.value
            analysis.risk_factors = "; ".join(result.risk_factors)
            analysis.recommendations = "; ".join(result.recommendations)
            
            # 如果是异常检测到的材料，特别标记
            if result.material_id in anomaly_material_ids:
                analysis.risk_level = RiskLevel.HIGH.value
                existing_factors = analysis.risk_factors or ""
                analysis.risk_factors = f"{existing_factors}; 统计学异常检测标记"
        
        await db.commit()
        logger.info(f"更新了 {len(reasonability_results)} 个材料的合理性分析结果")
    
    def _calculate_analysis_statistics(
        self,
        results: List[PriceReasonabilityResult]
    ) -> Dict[str, Any]:
        """计算分析统计信息"""
        
        if not results:
            return {
                'reasonable_count': 0,
                'unreasonable_count': 0,
                'high_risk_count': 0,
                'critical_risk_count': 0,
                'average_confidence': 0,
                'variance_stats': {}
            }
        
        reasonable_count = sum(1 for r in results if r.price_status == PriceStatus.REASONABLE)
        unreasonable_count = len(results) - reasonable_count
        high_risk_count = sum(1 for r in results if r.risk_level == RiskLevel.HIGH)
        critical_risk_count = sum(1 for r in results if r.risk_level == RiskLevel.CRITICAL)
        
        # 计算平均置信度
        average_confidence = sum(r.confidence_score for r in results) / len(results)
        
        # 计算价格偏差统计
        variances = [r.price_variance for r in results if r.price_variance]
        if variances:
            variance_stats = {
                'mean': sum(variances) / len(variances),
                'min': min(variances),
                'max': max(variances),
                'count': len(variances)
            }
        else:
            variance_stats = {}
        
        return {
            'reasonable_count': reasonable_count,
            'unreasonable_count': unreasonable_count,
            'high_risk_count': high_risk_count,
            'critical_risk_count': critical_risk_count,
            'average_confidence': average_confidence,
            'variance_stats': variance_stats
        }