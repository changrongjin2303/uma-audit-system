from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta
from loguru import logger
import asyncio
import re

from app.models.project import ProjectMaterial, Project
from app.models.analysis import PriceAnalysis, PriceAnalysisHistory, AnalysisStatus
from app.services.ai_analysis import AIServiceManager, PriceAnalysisResult, AIProvider
from app.core.config import settings


class PriceAnalysisService:
    """价格分析服务"""
    
    def __init__(self):
        self.ai_manager = AIServiceManager()
        self.max_concurrent_analyses = 20  # 最大并发分析数
        self.analysis_timeout = 60  # 默认单个分析超时时间（秒）
        self.provider_timeout_overrides = {
            AIProvider.DOUBAO: 150  # 豆包响应较慢，额外放宽超时时间
        }
    
    async def analyze_project_materials(
        self,
        db: AsyncSession,
        project_id: int,
        material_ids: Optional[List[int]] = None,
        batch_size: int = 20,
        force_reanalyze: bool = False,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """分析项目材料价格"""

        # 获取项目基期信息价日期
        project_base_date = await self._get_project_base_date(db, project_id)

        # 获取需要分析的材料
        materials_to_analyze = await self._get_materials_for_analysis(
            db, project_id, material_ids, force_reanalyze
        )
        
        if not materials_to_analyze:
            return {
                'project_id': project_id,
                'total_materials': 0,
                'analyzed_count': 0,
                'success_count': 0,
                'failed_count': 0,
                'skipped_count': 0
            }
        
        logger.info(f"开始分析项目 {project_id} 的 {len(materials_to_analyze)} 个材料")
        
        # 统计结果
        analyzed_count = 0
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        # 分批处理材料
        for i in range(0, len(materials_to_analyze), batch_size):
            batch = materials_to_analyze[i:i + batch_size]
            
            # 并发分析批次材料
            batch_results = await self._analyze_material_batch(db, batch, project_base_date, preferred_provider)
            
            for result in batch_results:
                analyzed_count += 1
                if result['success']:
                    success_count += 1
                elif result['skipped']:
                    skipped_count += 1
                else:
                    failed_count += 1
        
        # 更新项目统计
        await self._update_project_analysis_statistics(db, project_id)
        
        return {
            'project_id': project_id,
            'total_materials': len(materials_to_analyze),
            'analyzed_count': analyzed_count,
            'success_count': success_count,
            'failed_count': failed_count,
            'skipped_count': skipped_count
        }
    
    async def analyze_single_material(
        self,
        db: AsyncSession,
        material_id: int,
        preferred_provider: Optional[AIProvider] = None,
        force_reanalyze: bool = False
    ) -> Dict[str, Any]:
        """分析单个材料价格"""
        
        from sqlalchemy.orm import selectinload
        
        # 获取材料信息，预加载项目关系以便获取地区信息
        stmt = select(ProjectMaterial).options(
            selectinload(ProjectMaterial.project)
        ).where(ProjectMaterial.id == material_id)
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise ValueError(f"材料 {material_id} 不存在")
        
        # 检查是否需要重新分析
        if not force_reanalyze:
            existing_analysis = await self._get_existing_analysis(db, material_id)
            if existing_analysis and existing_analysis.status == AnalysisStatus.COMPLETED:
                return {
                    'material_id': material_id,
                    'status': 'already_analyzed',
                    'analysis': self._format_analysis_result(existing_analysis)
                }
        
        try:
            # 获取项目基期信息价日期
            project_base_date = await self._get_project_base_date(db, material.project_id)
            # 执行AI分析
            ai_result = await self._perform_ai_analysis(
                material, project_base_date, preferred_provider
            )
            
            # 保存分析结果
            analysis = await self._save_analysis_result(db, material, ai_result)
            await db.commit()
            await db.refresh(analysis)
            
            return {
                'material_id': material_id,
                'status': 'success',
                'analysis': self._format_analysis_result(analysis)
            }
        
        except Exception as e:
            logger.error(f"分析材料 {material_id} 失败: {e}")
            
            # 记录失败的分析
            await self._save_failed_analysis(db, material, str(e))
            await db.commit()
            
            return {
                'material_id': material_id,
                'status': 'failed',
                'error': str(e)
            }
    
    async def get_analysis_results(
        self,
        db: AsyncSession,
        project_id: int,
        status: Optional[AnalysisStatus] = None,
        is_reasonable: Optional[bool] = None,
        risk_level: Optional[str] = None,
        material_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取分析结果"""

        from sqlalchemy.orm import selectinload

        # 基础查询
        base_stmt = select(PriceAnalysis).options(
            selectinload(PriceAnalysis.material)
        ).join(ProjectMaterial).where(
            ProjectMaterial.project_id == project_id
        )

        if status:
            base_stmt = base_stmt.where(PriceAnalysis.status == status)
        if is_reasonable is not None:
            base_stmt = base_stmt.where(PriceAnalysis.is_reasonable == is_reasonable)
        if material_name:
            base_stmt = base_stmt.where(ProjectMaterial.material_name.ilike(f"%{material_name}%"))

        # 如果未指定风险等级，走数据库分页
        if not risk_level:
            stmt = base_stmt.offset(skip).limit(limit).order_by(PriceAnalysis.created_at.desc())
            result = await db.execute(stmt)
            analyses = result.scalars().all()
            return [self._format_analysis_result_with_material(a) for a in analyses]

        # 指定了风险等级：为了兼容旧数据（risk_level 为空），在内存中按“偏差阈值”兜底过滤
        # 这里取全量（该项目量级通常较小 < 几千），再做切片
        result = await db.execute(base_stmt.order_by(PriceAnalysis.created_at.desc()))
        all_analyses = result.scalars().all()

        def infer_level(a: PriceAnalysis) -> str:
            if a.risk_level:
                return a.risk_level
            try:
                v = abs(a.price_variance or 0)
                # 更新风险等级划分标准
                if v == 0:
                    return 'normal'
                elif v <= 15:
                    return 'low'
                elif v <= 30:
                    return 'medium'
                elif v <= 50:
                    return 'high'
                else:
                    return 'critical'
            except Exception:
                return 'low'

        filtered = [a for a in all_analyses if infer_level(a) == risk_level]
        page_items = filtered[skip: skip + limit]
        return [self._format_analysis_result_with_material(a) for a in page_items]
    
    async def get_analysis_statistics(
        self,
        db: AsyncSession,
        project_id: int
    ) -> Dict[str, Any]:
        """获取分析统计信息"""
        
        # 获取项目所有材料的分析状态（需要预加载 analysis 关系，避免异步懒加载报错）
        from sqlalchemy.orm import selectinload
        stmt = select(ProjectMaterial).options(
            selectinload(ProjectMaterial.analysis),
            selectinload(ProjectMaterial.project)
        ).where(
            ProjectMaterial.project_id == project_id
        )
        result = await db.execute(stmt)
        materials = result.scalars().all()
        
        # 统计分析状态（只统计未匹配的材料，即无信息价材料）
        unpriced_materials = [m for m in materials if not m.is_matched]
        total_unpriced = len(unpriced_materials)
        analyzed_materials = 0
        reasonable_materials = 0
        unreasonable_materials = 0
        pending_materials = 0
        failed_materials = 0
        
        for material in unpriced_materials:
            try:
                # 安全地访问 analysis 关系
                analysis = getattr(material, 'analysis', None)
                if analysis is not None:
                    analyzed_materials += 1
                    if analysis.status == AnalysisStatus.COMPLETED:
                        if analysis.is_reasonable is True:
                            reasonable_materials += 1
                        elif analysis.is_reasonable is False:
                            unreasonable_materials += 1
                    elif analysis.status == AnalysisStatus.FAILED:
                        failed_materials += 1
                    else:
                        pending_materials += 1
            except Exception as e:
                # 如果访问关系属性时出错，记录日志但继续处理
                logger.warning(f"访问材料 {material.id} 的分析关系时出错: {e}")
                continue
        
        not_analyzed = total_unpriced - analyzed_materials
        
        return {
            'project_id': project_id,
            'total_materials': len(materials),  # 项目总材料数
            'total_unpriced_materials': total_unpriced,  # 无信息价材料总数
            'analyzed_materials': analyzed_materials,  # 已分析的无信息价材料数
            'not_analyzed': not_analyzed,  # 未分析的无信息价材料数
            'reasonable_materials': reasonable_materials,  # 价格合理的材料数
            'unreasonable_materials': unreasonable_materials,  # 价格不合理的材料数  
            'pending_materials': pending_materials,  # 分析中的材料数
            'failed_materials': failed_materials,  # 分析失败的材料数
            'analysis_rate': analyzed_materials / total_unpriced if total_unpriced > 0 else 0,  # 分析完成率
            'reasonable_rate': reasonable_materials / analyzed_materials if analyzed_materials > 0 else 0  # 合理率
        }
    
    async def _get_materials_for_analysis(
        self,
        db: AsyncSession,
        project_id: int,
        material_ids: Optional[List[int]] = None,
        force_reanalyze: bool = False
    ) -> List[ProjectMaterial]:
        """获取需要分析的材料"""
        
        from sqlalchemy.orm import selectinload
        
        # 预加载相关的分析数据和项目关系，避免惰性加载导致的异步问题
        # 项目关系用于获取地区信息
        stmt = select(ProjectMaterial).options(
            selectinload(ProjectMaterial.analysis),
            selectinload(ProjectMaterial.project)
        ).where(
            ProjectMaterial.project_id == project_id
        )
        
        if material_ids:
            stmt = stmt.where(ProjectMaterial.id.in_(material_ids))
        
        result = await db.execute(stmt)
        all_materials = result.scalars().all()
        
        if force_reanalyze:
            return all_materials
        
        # 过滤出需要分析的材料（未分析或分析失败的）
        materials_to_analyze = []
        
        for material in all_materials:
            # 只分析未匹配的材料（无信息价材料）
            if not material.is_matched:
                needs_analysis = True
                
                # 检查是否已经分析过
                if hasattr(material, 'analysis') and material.analysis:
                    if material.analysis.status == AnalysisStatus.COMPLETED:
                        if not force_reanalyze:
                            needs_analysis = False
                    elif material.analysis.status == AnalysisStatus.PROCESSING:
                        # 检查是否超时
                        if (datetime.utcnow() - material.analysis.created_at).total_seconds() < 300:
                            needs_analysis = False
                
                if needs_analysis:
                    materials_to_analyze.append(material)
        
        return materials_to_analyze
    
    async def _analyze_material_batch(
        self,
        db: AsyncSession,
        materials: List[ProjectMaterial],
        project_base_date: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> List[Dict[str, Any]]:
        """批量分析材料 - 支持并行和串行处理"""
        
        # 如果材料数量较少，使用串行处理
        if len(materials) <= 2:
            return await self._analyze_material_batch_serial(db, materials, project_base_date, preferred_provider)

        # 对于较多材料，使用并行处理
        return await self._analyze_material_batch_parallel(db, materials, project_base_date, preferred_provider)
    
    async def _analyze_material_batch_serial(
        self,
        db: AsyncSession,
        materials: List[ProjectMaterial],
        project_base_date: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> List[Dict[str, Any]]:
        """串行处理材料分析 - 避免数据库冲突"""

        batch_results = []

        for material in materials:
            try:
                result = await self._analyze_single_material_task(db, material, project_base_date, preferred_provider)
                batch_results.append(result)
            except Exception as e:
                logger.error(f"材料 {material.id} 分析异常: {e}")
                batch_results.append({
                    'material_id': material.id,
                    'success': False,
                    'skipped': False,
                    'error': str(e)
                })
        
        return batch_results
    
    async def _analyze_material_batch_parallel(
        self,
        db: AsyncSession,
        materials: List[ProjectMaterial],
        project_base_date: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> List[Dict[str, Any]]:
        """并行处理材料分析 - 提升处理速度"""

        # 创建分析任务
        tasks = []
        for material in materials:
            task = self._analyze_single_material_parallel(material, project_base_date, preferred_provider)
            tasks.append(task)
        
        # 并发执行分析任务（限制并发数量）
        semaphore = asyncio.Semaphore(self.max_concurrent_analyses)  # 限制最大并发数
        
        async def run_with_semaphore(task):
            async with semaphore:
                return await task
        
        # 执行所有任务
        results = await asyncio.gather(
            *[run_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # 处理结果，保存到数据库
        batch_results = []
        for i, result in enumerate(results):
            material = materials[i]
            
            if isinstance(result, Exception):
                logger.error(f"材料 {material.id} 并行分析异常: {result}")
                batch_results.append({
                    'material_id': material.id,
                    'success': False,
                    'skipped': False,
                    'error': str(result)
                })
            else:
                # 保存分析结果到数据库
                try:
                    if result.get('success'):
                        analysis = await self._save_analysis_result_from_ai_result(
                            db, material, result['ai_result']
                        )
                        await db.commit()
                        await db.refresh(analysis)
                        
                        batch_results.append({
                            'material_id': material.id,
                            'success': True,
                            'skipped': False,
                            'analysis': self._format_analysis_result(analysis)
                        })
                    else:
                        batch_results.append(result)
                except Exception as e:
                    logger.error(f"保存材料 {material.id} 分析结果失败: {e}")
                    batch_results.append({
                        'material_id': material.id,
                        'success': False,
                        'skipped': False,
                        'error': f"保存结果失败: {str(e)}"
                    })
        
        return batch_results
    
    async def _analyze_single_material_parallel(
        self,
        material: ProjectMaterial,
        project_base_date: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """并行分析单个材料 - 不涉及数据库操作"""

        try:
            # 执行AI分析（不涉及数据库会话）
            ai_result = await self._perform_ai_analysis(material, project_base_date, preferred_provider)
            
            return {
                'material_id': material.id,
                'success': True,
                'skipped': False,
                'ai_result': ai_result
            }
            
        except Exception as e:
            logger.error(f"并行分析材料 {material.id} 失败: {e}")
            return {
                'material_id': material.id,
                'success': False,
                'skipped': False,
                'error': str(e)
            }
    
    async def _analyze_single_material_task(
        self,
        db: AsyncSession,
        material: ProjectMaterial,
        project_base_date: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """单个材料分析任务"""

        try:
            # 创建或更新分析记录为处理中状态
            analysis = await self._create_processing_analysis(db, material)
            await db.commit()  # 提交处理中状态

            # 执行AI分析
            timeout = self._resolve_analysis_timeout(preferred_provider)
            ai_result = await asyncio.wait_for(
                self._perform_ai_analysis(material, project_base_date, preferred_provider),
                timeout=timeout
            )
            
            # 更新分析结果
            await self._update_analysis_result(db, analysis, ai_result)
            await db.commit()  # 提交分析结果
            
            return {
                'material_id': material.id,
                'success': True,
                'skipped': False,
                'analysis_id': analysis.id
            }
        
        except asyncio.TimeoutError:
            logger.warning(f"材料 {material.id} 分析超时")
            await db.rollback()  # 回滚之前可能的错误事务
            await self._save_failed_analysis(db, material, "分析超时")
            await db.commit()  # 提交失败状态
            return {
                'material_id': material.id,
                'success': False,
                'skipped': False,
                'error': '分析超时'
            }
        
        except Exception as e:
            logger.error(f"材料 {material.id} 分析失败: {e}")
            try:
                await db.rollback()  # 回滚之前可能的错误事务
            except:
                pass  # 如果回滚也失败，忽略错误继续处理
            await self._save_failed_analysis(db, material, str(e))
            await db.commit()  # 提交失败状态
            return {
                'material_id': material.id,
                'success': False,
                'skipped': False,
                'error': str(e)
            }
    
    async def _get_project_base_date(self, db: AsyncSession, project_id: int) -> Optional[str]:
        """获取项目的基期信息价日期"""
        try:
            stmt = select(Project.base_price_date).where(Project.id == project_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.warning(f"获取项目 {project_id} 基期信息价日期失败: {e}")
            return None

    async def _perform_ai_analysis(
        self,
        material: ProjectMaterial,
        project_base_date: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None
    ) -> PriceAnalysisResult:
        """执行AI分析"""

        # 准备context参数
        context = {}
        if project_base_date:
            context['base_date'] = project_base_date

        region = self._resolve_analysis_region(material)
        if region and project_base_date:
            context['base_region'] = region

        return await self.ai_manager.analyze_material_price(
            material_name=material.material_name,
            specification=material.specification or "",
            unit=material.unit,
            region=region,
            context=context,
            preferred_provider=preferred_provider
        )

    def _resolve_analysis_region(self, material: ProjectMaterial) -> str:
        """根据项目基期信息价地区确定分析区域"""
        from app.utils.region_mapping import resolve_region_from_codes

        try:
            project = getattr(material, 'project', None)
        except Exception:
            project = None

        if project:
            # 使用地区编码映射服务将编码转换为名称
            region = resolve_region_from_codes(
                project.base_price_province,
                project.base_price_city,
                project.base_price_district
            )

            # 如果解析结果不是默认值且不为空，使用解析结果
            if region and region != "全国":
                return region

            # 回退到项目地点
            if project.location:
                location = project.location.strip()
                if location:
                    return location

        return "全国"

    def _resolve_analysis_timeout(
        self,
        preferred_provider: Optional[AIProvider]
    ) -> int:
        """根据指定的AI服务提供商决定超时时间"""
        if preferred_provider and preferred_provider in self.provider_timeout_overrides:
            return max(
                self.analysis_timeout,
                self.provider_timeout_overrides[preferred_provider]
            )
        return self.analysis_timeout
    
    async def _create_processing_analysis(
        self,
        db: AsyncSession,
        material: ProjectMaterial
    ) -> PriceAnalysis:
        """创建处理中的分析记录"""
        
        # 查看是否已有分析记录
        stmt = select(PriceAnalysis).where(
            PriceAnalysis.material_id == material.id
        )
        result = await db.execute(stmt)
        existing_analysis = result.scalar_one_or_none()
        
        if existing_analysis:
            # 如果现有分析是完成状态，始终尝试归档（防止数据丢失）
            if existing_analysis.status == AnalysisStatus.COMPLETED:
                try:
                    # 检查历史表中是否已有内容完全相同的记录
                    # 我们比较核心字段来判断是否已经归档过
                    stmt_check = select(PriceAnalysisHistory).where(
                        PriceAnalysisHistory.material_id == material.id,
                        PriceAnalysisHistory.status == existing_analysis.status,
                        PriceAnalysisHistory.predicted_price_min == existing_analysis.predicted_price_min,
                        PriceAnalysisHistory.predicted_price_max == existing_analysis.predicted_price_max,
                        # 也可以比较模型，增加准确性
                        PriceAnalysisHistory.analysis_model == existing_analysis.analysis_model
                    ).limit(1)
                    
                    result_check = await db.execute(stmt_check)
                    existing_history = result_check.scalar_one_or_none()
                    
                    # 如果没有找到相同的历史记录，则进行归档
                    if not existing_history:
                        logger.info(f"材料 {material.id} 的当前分析结果未归档，正在备份到历史表")
                        history_entry = PriceAnalysisHistory(
                            material_id=existing_analysis.material_id,
                            status=existing_analysis.status,
                            predicted_price_min=existing_analysis.predicted_price_min,
                            predicted_price_max=existing_analysis.predicted_price_max,
                            confidence_score=existing_analysis.confidence_score,
                            risk_level=existing_analysis.risk_level,
                            analysis_model=existing_analysis.analysis_model,
                            analysis_cost=existing_analysis.analysis_cost,
                            analysis_time=existing_analysis.analysis_time,
                            analysis_reasoning=existing_analysis.analysis_reasoning,
                            # 保持原始分析时间
                            created_at=existing_analysis.analyzed_at or existing_analysis.created_at
                        )
                        db.add(history_entry)
                        # 注意：这里不需要commit，因为后续会commit status update
                    else:
                        logger.info(f"材料 {material.id} 的当前分析结果已存在于历史表中，跳过备份")
                        
                except Exception as e:
                    logger.warning(f"归档旧分析记录失败: {e}")

            # 更新状态为处理中
            existing_analysis.status = AnalysisStatus.PROCESSING
            return existing_analysis
        else:
            # 创建新的分析记录
            analysis = PriceAnalysis(
                material_id=material.id,
                status=AnalysisStatus.PROCESSING
            )
            db.add(analysis)
            return analysis
    
    async def _update_analysis_result(
        self,
        db: AsyncSession,
        analysis: PriceAnalysis,
        ai_result: PriceAnalysisResult
    ):
        """更新分析结果"""
        
        # 先获取材料信息，用于日志和后续计算
        stmt = select(ProjectMaterial).where(ProjectMaterial.id == analysis.material_id)
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        material_name = material.material_name if material else ai_result.material_name
        
        analysis.status = AnalysisStatus.COMPLETED
        base_predicted_min = ai_result.predicted_price_min
        base_predicted_max = ai_result.predicted_price_max
        analysis.predicted_price_avg = None  # 不再使用加权平均价
        analysis.confidence_score = ai_result.confidence_score
        analysis.analysis_model = ai_result.provider
        analysis.analysis_prompt = ai_result.analysis_prompt
        # 保存API响应和参考网址
        api_response = ai_result.raw_response.copy() if ai_result.raw_response else {}
        if ai_result.reference_urls:
            api_response['reference_urls'] = ai_result.reference_urls
        analysis.api_response = api_response
        # 验证并处理数据源，确保每个来源都有价格区间
        data_sources = ai_result.data_sources or []
        logger.info(f"材料 {material_name} 的原始数据源数量: {len(data_sources)}")
        validated_sources = []
        for idx, source in enumerate(data_sources):
            if isinstance(source, dict):
                logger.debug(f"数据源 {idx+1}: {source.get('source_type', '未知')}, 包含字段: {list(source.keys())}")
                
                # 规范化价格区间字段名，兼容AI可能返回的不同字段名
                if 'min_price' in source and 'price_range_min' not in source:
                    source['price_range_min'] = source['min_price']
                if 'max_price' in source and 'price_range_max' not in source:
                    source['price_range_max'] = source['max_price']
                if 'price_min' in source and 'price_range_min' not in source:
                    source['price_range_min'] = source['price_min']
                if 'price_max' in source and 'price_range_max' not in source:
                    source['price_range_max'] = source['price_max']
                
                # 检查是否有价格区间，如果没有则记录警告并补充
                has_min = 'price_range_min' in source and source['price_range_min'] is not None
                has_max = 'price_range_max' in source and source['price_range_max'] is not None
                
                if not has_min or not has_max:
                    logger.warning(
                        f"材料 {material_name} 的数据源 {source.get('source_type', '未知')} "
                        f"缺少价格区间信息 (has_min={has_min}, has_max={has_max})，"
                        f"将使用综合价格区间作为默认值"
                    )
                    # 如果没有价格区间，使用综合价格区间作为默认值
                    if ai_result.predicted_price_min and ai_result.predicted_price_max:
                        if not has_min:
                            source['price_range_min'] = ai_result.predicted_price_min
                        if not has_max:
                            source['price_range_max'] = ai_result.predicted_price_max
                        logger.info(
                            f"已为数据源 {source.get('source_type', '未知')} 补充价格区间: "
                            f"{source['price_range_min']} ~ {source['price_range_max']}"
                        )
                    else:
                        logger.error(
                            f"材料 {material_name} 的综合价格区间也为空，无法补充数据源价格区间"
                        )
                else:
                    logger.info(
                        f"数据源 {source.get('source_type', '未知')} 已有价格区间: "
                        f"{source['price_range_min']} ~ {source['price_range_max']}"
                    )
                validated_sources.append(source)
            else:
                logger.warning(f"数据源 {idx+1} 不是字典格式: {type(source)}")
                validated_sources.append(source)
        
        logger.info(f"验证后的数据源数量: {len(validated_sources)}")
        # 记录每个数据源的最终状态
        for idx, source in enumerate(validated_sources):
            if isinstance(source, dict):
                logger.info(
                    f"数据源 {idx+1} 最终状态: source_type={source.get('source_type')}, "
                    f"price_range_min={source.get('price_range_min')}, "
                    f"price_range_max={source.get('price_range_max')}"
                )
        weighted_min, weighted_max, weighting_note = self._calculate_weighted_price_range(
            validated_sources,
            base_predicted_min,
            base_predicted_max
        )

        if weighted_min is not None and weighted_max is not None:
            analysis.predicted_price_min = weighted_min
            analysis.predicted_price_max = weighted_max
        else:
            analysis.predicted_price_min = base_predicted_min
            analysis.predicted_price_max = base_predicted_max

        analysis.data_sources = validated_sources
        analysis.reference_prices = validated_sources  # 兼容字段
        reasoning_text = ai_result.reasoning or ""
        if weighting_note:
            reasoning_text = f"{reasoning_text}\n\n[系统综合权重说明]\n{weighting_note}".strip()
        analysis.analysis_reasoning = reasoning_text
        analysis.risk_factors = "; ".join(ai_result.risk_factors)
        analysis.recommendations = "; ".join(ai_result.recommendations)
        analysis.analysis_cost = ai_result.analysis_cost
        analysis.analysis_time = ai_result.analysis_time
        analysis.analyzed_at = datetime.utcnow()
        
        # 判断价格合理性
        if material and material.unit_price:
            analysis.is_reasonable = self._check_price_reasonability(
                material.unit_price,
                analysis.predicted_price_min,
                analysis.predicted_price_max
            )

            # 修改偏差率计算逻辑 - 只使用最低价和最高价
            analysis.price_variance = self._calculate_price_variance(
                material.unit_price,
                None,  # 不再使用加权平均价
                analysis.predicted_price_min,
                analysis.predicted_price_max
            )

            # 根据新的偏差率计算风险等级
            analysis.risk_level = self._calculate_risk_level(analysis.price_variance)
        else:
            # 如果没有材料或单价信息，设置默认值
            analysis.is_reasonable = None
            analysis.price_variance = None
            analysis.risk_level = 'low'

        # 将本次分析结果写入历史表（用于时间线展示）
        try:
            history_entry = PriceAnalysisHistory(
                material_id=analysis.material_id,
                status=analysis.status,
                predicted_price_min=analysis.predicted_price_min,
                predicted_price_max=analysis.predicted_price_max,
                confidence_score=analysis.confidence_score,
                risk_level=analysis.risk_level,
                analysis_model=analysis.analysis_model,
                analysis_cost=analysis.analysis_cost,
                analysis_time=analysis.analysis_time,
                analysis_reasoning=analysis.analysis_reasoning,
            )
            db.add(history_entry)
        except Exception as e:
            # 历史记录写入失败不影响主流程，只记录日志
            logger.warning(f"写入价格分析历史记录失败(analysis_id={analysis.id}): {e}")
    
    async def _save_failed_analysis(
        self,
        db: AsyncSession,
        material: ProjectMaterial,
        error_message: str
    ):
        """保存失败的分析"""
        
        stmt = select(PriceAnalysis).where(
            PriceAnalysis.material_id == material.id
        )
        result = await db.execute(stmt)
        analysis = result.scalar_one_or_none()
        
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.analysis_reasoning = error_message
        else:
            analysis = PriceAnalysis(
                material_id=material.id,
                status=AnalysisStatus.FAILED,
                analysis_reasoning=error_message
            )
            db.add(analysis)

        # 记录失败历史
        try:
            history_entry = PriceAnalysisHistory(
                material_id=material.id,
                status=AnalysisStatus.FAILED,
                analysis_reasoning=error_message
            )
            db.add(history_entry)
        except Exception as e:
            logger.warning(f"写入失败分析历史记录失败(material_id={material.id}): {e}")

    def _parse_reliability_score(self, reliability: Optional[str]) -> float:
        """将可靠性字符串转换为0-1权重"""
        if reliability is None:
            return 0.5

        star_weights = {
            "★★★★★": 1.0,
            "★★★★☆": 0.9,
            "★★★★": 0.85,
            "★★★☆☆": 0.75,
            "★★★": 0.7,
            "★★☆☆☆": 0.55,
            "★★": 0.5,
            "★☆☆☆☆": 0.35,
            "★": 0.3
        }

        text = str(reliability).strip()
        if text in star_weights:
            return star_weights[text]

        if "★" in text:
            filled = text.count("★")
            return min(1.0, max(0.2, filled / 5))

        match = re.search(r"(\d+(\.\d+)?)", text)
        if match:
            value = float(match.group(1))
            if value > 1:
                # 支持百分比或十分制
                if value > 100:
                    value = value / 1000
                elif value > 10:
                    value = value / 100
                else:
                    value = value / 10
            return min(1.0, max(0.1, value))

        return 0.5

    def _calculate_weighted_price_range(
        self,
        data_sources: List[Dict[str, Any]],
        fallback_min: Optional[float],
        fallback_max: Optional[float]
    ) -> (Optional[float], Optional[float], str):
        """根据数据源可靠性计算加权价格区间"""
        weighted_min_sum = 0.0
        weighted_max_sum = 0.0
        total_weight = 0.0
        details = []

        for source in data_sources:
            if not isinstance(source, dict):
                continue
            try:
                source_min = float(source.get("price_range_min"))
                source_max = float(source.get("price_range_max"))
            except (TypeError, ValueError):
                continue

            if source_min is None or source_max is None:
                continue

            reliability = self._parse_reliability_score(source.get("reliability"))
            if reliability <= 0:
                continue

            weighted_min_sum += source_min * reliability
            weighted_max_sum += source_max * reliability
            total_weight += reliability

            source_type = source.get("source_type") or "未知来源"
            platform = source.get("platform_examples") or ""
            details.append(
                f"- {source_type}（{platform}）：{source_min:.2f}~{source_max:.2f}，权重 {reliability:.2f}"
            )

        if total_weight <= 0:
            return fallback_min, fallback_max, ""

        weighted_min = round(weighted_min_sum / total_weight, 2)
        weighted_max = round(weighted_max_sum / total_weight, 2)

        if weighted_min > weighted_max:
            weighted_min, weighted_max = weighted_max, weighted_min

        details.append(f"综合区间：{weighted_min:.2f} ~ {weighted_max:.2f}")
        weighting_note = "\n".join(details)

        return weighted_min, weighted_max, weighting_note

    def _calculate_price_variance(
        self,
        project_price: float,
        predicted_avg: Optional[float],
        predicted_min: Optional[float] = None,
        predicted_max: Optional[float] = None
    ) -> Optional[float]:
        """
        计算价格偏差率：
        - 当报审价格小于价格区间最低价时：偏差率 = (AI分析最低价-报审价格) / AI分析最低价 × 100%
        - 当报审价格大于价格区间最高价时：偏差率 = (报审价格-AI分析最高价) / AI分析最高价 × 100%
        - 当报审价格在区间内则偏差率为0
        """

        if not predicted_min or not predicted_max:
            return None

        # 报审价格小于最低价
        if project_price < predicted_min:
            return (predicted_min - project_price) / predicted_min * 100

        # 报审价格大于最高价
        elif project_price > predicted_max:
            return (project_price - predicted_max) / predicted_max * 100

        # 报审价格在区间内
        else:
            return 0.0

    def _calculate_risk_level(self, variance: Optional[float]) -> str:
        """根据偏差率计算风险等级"""

        if variance is None:
            return 'low'

        abs_variance = abs(variance)

        # 新的风险等级划分标准
        if abs_variance == 0:
            return 'normal'  # 正常
        elif abs_variance <= 15:
            return 'low'     # 低风险
        elif abs_variance <= 30:
            return 'medium'  # 中风险
        elif abs_variance <= 50:
            return 'high'    # 高风险
        else:
            return 'critical'  # 严重风险

    def _check_price_reasonability(
        self,
        original_price: float,
        predicted_min: Optional[float],
        predicted_max: Optional[float]
    ) -> Optional[bool]:
        """检查价格合理性"""

        if not predicted_min or not predicted_max:
            return None

        # 价格在预测区间内认为是合理的
        return predicted_min <= original_price <= predicted_max
    
    async def _get_existing_analysis(
        self,
        db: AsyncSession,
        material_id: int
    ) -> Optional[PriceAnalysis]:
        """获取现有分析"""
        
        stmt = select(PriceAnalysis).where(
            PriceAnalysis.material_id == material_id
        ).order_by(PriceAnalysis.analyzed_at.desc(), PriceAnalysis.created_at.desc())
        result = await db.execute(stmt)
        row = result.first()
        return row[0] if row else None
    
    def _format_analysis_result(self, analysis: PriceAnalysis) -> Dict[str, Any]:
        """格式化分析结果"""
        
        return {
            'id': analysis.id,
            'material_id': analysis.material_id,
            'status': analysis.status.value,
            'predicted_price_min': analysis.predicted_price_min,
            'predicted_price_max': analysis.predicted_price_max,
            # 'predicted_price_avg': analysis.predicted_price_avg,  # 不再显示加权平均价
            'confidence_score': analysis.confidence_score,
            'is_reasonable': analysis.is_reasonable,
            'price_variance': analysis.price_variance,
            'risk_level': analysis.risk_level,
            'analysis_model': analysis.analysis_model,
            'data_sources': analysis.data_sources,
            'analysis_reasoning': analysis.analysis_reasoning,
            'risk_factors': analysis.risk_factors,
            'recommendations': analysis.recommendations,
            'analysis_cost': analysis.analysis_cost,
            'analysis_time': analysis.analysis_time,
            'created_at': analysis.created_at,
            'analyzed_at': analysis.analyzed_at
        }
    
    def _format_analysis_result_detailed(self, analysis: PriceAnalysis) -> Dict[str, Any]:
        """格式化详细分析结果，包含AI提示词和响应"""
        
        result = self._format_analysis_result(analysis)
        
        # 添加AI对话信息
        result.update({
            'analysis_prompt': analysis.analysis_prompt,
            'api_response': analysis.api_response,
            'market_data': analysis.market_data,
            'reference_prices': analysis.reference_prices,
            'retry_count': analysis.retry_count,
            'is_reviewed': analysis.is_reviewed,
            'review_notes': analysis.review_notes,
            'reviewed_at': analysis.reviewed_at
        })
        
        return result
    
    def _format_analysis_result_with_material(self, analysis: PriceAnalysis) -> Dict[str, Any]:
        """格式化分析结果（包含材料信息）"""
        
        result = self._format_analysis_result(analysis)
        
        # 添加材料信息
        if hasattr(analysis, 'material') and analysis.material:
            material = analysis.material
            result.update({
                'material_name': material.material_name,
                'specification': material.specification,
                'unit': material.unit,
                'project_price': material.unit_price,
                'quantity': material.quantity
            })
        
        return result
    
    async def _save_analysis_result(
        self,
        db: AsyncSession,
        material: ProjectMaterial,
        ai_result: PriceAnalysisResult
    ) -> PriceAnalysis:
        """保存分析结果"""
        
        # 查找现有分析
        stmt = select(PriceAnalysis).where(
            PriceAnalysis.material_id == material.id
        )
        result = await db.execute(stmt)
        existing_analyses = result.scalars().all()
        
        analysis = None
        if existing_analyses:
            # 使用第一条记录
            analysis = existing_analyses[0]
            # 删除重复的分析记录
            if len(existing_analyses) > 1:
                logger.warning(f"发现材料 {material.id} 有 {len(existing_analyses)} 条分析记录，将删除多余记录")
                for duplicate in existing_analyses[1:]:
                    await db.delete(duplicate)
        else:
            # 创建新记录
            analysis = PriceAnalysis(
                material_id=material.id,
                status=AnalysisStatus.PROCESSING
            )
            db.add(analysis)
        
        # 更新分析结果
        await self._update_analysis_result(db, analysis, ai_result)
        
        return analysis
    
    async def _save_analysis_result_from_ai_result(
        self,
        db: AsyncSession,
        material: ProjectMaterial,
        ai_result: PriceAnalysisResult
    ) -> PriceAnalysis:
        """从AI结果保存分析结果 - 用于并行处理"""
        return await self._save_analysis_result(db, material, ai_result)
    
    async def _update_project_analysis_statistics(
        self,
        db: AsyncSession,
        project_id: int
    ):
        """更新项目分析统计"""
        # 这里可以更新项目表中的分析统计字段
        # 暂时省略具体实现
        pass
