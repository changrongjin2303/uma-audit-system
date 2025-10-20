from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
from loguru import logger

from app.models.project import ProjectMaterial
from app.models.material import BaseMaterial
from app.utils.matcher import MaterialMatcher, MatchResult
from app.services.material import BaseMaterialService


class MaterialMatchingService:
    """材料匹配服务"""
    
    def __init__(self):
        self.matcher = MaterialMatcher()
    
    async def match_project_materials(
        self,
        db: AsyncSession,
        project_id: int,
        batch_size: int = 100,
        auto_match_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """匹配项目中的所有材料"""
        
        # 获取项目中未匹配的材料
        unmatched_materials = await self._get_unmatched_materials(db, project_id)
        
        if not unmatched_materials:
            return {
                'total_materials': 0,
                'matched_count': 0,
                'unmatched_count': 0,
                'auto_matched': 0,
                'manual_review_required': 0
            }
        
        logger.info(f"开始匹配项目 {project_id} 的 {len(unmatched_materials)} 个材料")
        
        # 获取基准材料数据
        base_materials = await self._get_base_materials_for_matching(db)
        base_materials_dict = [
            {
                'id': bm.id,
                'name': bm.name,
                'specification': bm.specification,
                'unit': bm.unit,
                'category': bm.category,
                'subcategory': bm.subcategory,
                'region': bm.region,
                'price': bm.price
            } for bm in base_materials
        ]
        
        # 统计结果
        matched_count = 0
        auto_matched = 0
        manual_review_required = 0
        
        # 分批处理材料匹配
        for i in range(0, len(unmatched_materials), batch_size):
            batch = unmatched_materials[i:i + batch_size]
            
            for project_material in batch:
                try:
                    # 执行材料匹配
                    match_results = await self._match_single_material(
                        db, project_material, base_materials_dict
                    )

                    if match_results:
                        best_match = match_results[0]

                        # 只有相似度达到阈值才标记为匹配
                        if best_match.similarity_score >= auto_match_threshold:
                            # 更新匹配结果
                            await self._update_material_match(
                                db, project_material, best_match
                            )

                            matched_count += 1
                            auto_matched += 1
                        else:
                            # 相似度不够，不匹配，记录为需要人工审核
                            manual_review_required += 1
                            logger.debug(f"材料 '{project_material.material_name}' 最佳匹配相似度 {best_match.similarity_score:.3f} 低于阈值 {auto_match_threshold}，不匹配")

                except Exception as e:
                    logger.error(f"匹配材料 {project_material.id} 时出错: {e}")
                    continue
        
        # 更新项目统计
        await self._update_project_statistics(db, project_id)
        
        return {
            'total_materials': len(unmatched_materials),
            'matched_count': matched_count,
            'unmatched_count': len(unmatched_materials) - matched_count,
            'auto_matched': auto_matched,
            'manual_review_required': manual_review_required
        }
    
    async def match_single_material_interactive(
        self,
        db: AsyncSession,
        material_id: int,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """交互式匹配单个材料，返回候选匹配结果"""
        
        # 获取项目材料
        stmt = select(ProjectMaterial).where(ProjectMaterial.id == material_id)
        result = await db.execute(stmt)
        project_material = result.scalar_one_or_none()
        
        if not project_material:
            raise ValueError("材料不存在")
        
        # 获取基准材料
        base_materials = await self._get_base_materials_for_matching(db)
        base_materials_dict = [
            {
                'id': bm.id,
                'name': bm.name,
                'specification': bm.specification,
                'unit': bm.unit,
                'category': bm.category,
                'subcategory': bm.subcategory,
                'region': bm.region,
                'price': bm.price
            } for bm in base_materials
        ]
        
        # 执行匹配
        project_material_dict = {
            'material_name': project_material.material_name,
            'specification': project_material.specification,
            'unit': project_material.unit,
            'category': project_material.category,
        }
        
        match_results = self.matcher.find_best_matches(
            project_material_dict, base_materials_dict, top_k
        )
        
        # 格式化结果
        formatted_results = []
        for match_result in match_results:
            base_material = next(
                (bm for bm in base_materials if bm.id == match_result.base_material_id),
                None
            )
            
            if base_material:
                formatted_results.append({
                    'base_material_id': match_result.base_material_id,
                    'base_material': {
                        'name': base_material.name,
                        'specification': base_material.specification,
                        'unit': base_material.unit,
                        'category': base_material.category,
                        'price': base_material.price,
                        'region': base_material.region
                    },
                    'similarity_score': round(match_result.similarity_score, 4),
                    'confidence_level': match_result.confidence_level,
                    'match_details': {
                        'name_score': round(match_result.name_score, 4),
                        'spec_score': round(match_result.spec_score, 4),
                        'unit_score': round(match_result.unit_score, 4),
                        'category_score': round(match_result.category_score, 4)
                    },
                    'explanation': self.matcher.get_match_explanation(match_result)
                })
        
        return formatted_results
    
    async def confirm_material_match(
        self,
        db: AsyncSession,
        material_id: int,
        base_material_id: int,
        user_confirmed: bool = True
    ) -> bool:
        """确认材料匹配"""
        
        # 获取项目材料
        stmt = select(ProjectMaterial).where(ProjectMaterial.id == material_id)
        result = await db.execute(stmt)
        project_material = result.scalar_one_or_none()
        
        if not project_material:
            return False
        
        # 验证基准材料存在
        base_material = await BaseMaterialService.get_material_by_id(db, base_material_id)
        if not base_material:
            return False
        
        # 更新匹配信息
        project_material.is_matched = True
        project_material.matched_material_id = base_material_id
        project_material.match_method = "user_confirmed" if user_confirmed else "auto_matched"
        project_material.match_score = 1.0 if user_confirmed else project_material.match_score
        
        await db.commit()
        await db.refresh(project_material)
        
        # 更新项目统计
        await self._update_project_statistics(db, project_material.project_id)
        
        return True
    
    async def unmatch_material(
        self,
        db: AsyncSession,
        material_id: int
    ) -> bool:
        """取消材料匹配"""
        
        stmt = select(ProjectMaterial).where(ProjectMaterial.id == material_id)
        result = await db.execute(stmt)
        project_material = result.scalar_one_or_none()
        
        if not project_material:
            return False
        
        # 清除匹配信息
        project_material.is_matched = False
        project_material.matched_material_id = None
        project_material.match_method = None
        project_material.match_score = None
        
        await db.commit()
        
        # 更新项目统计
        await self._update_project_statistics(db, project_material.project_id)
        
        return True
    
    async def get_matching_statistics(
        self,
        db: AsyncSession,
        project_id: int
    ) -> Dict[str, Any]:
        """获取匹配统计信息"""
        
        # 总材料数
        total_stmt = select(ProjectMaterial).where(
            ProjectMaterial.project_id == project_id
        )
        total_result = await db.execute(total_stmt)
        total_materials = total_result.scalars().all()
        
        # 统计各种状态的材料
        matched_materials = [m for m in total_materials if m.is_matched]
        unmatched_materials = [m for m in total_materials if not m.is_matched]
        
        # 按匹配方法分类
        auto_matched = [m for m in matched_materials if m.match_method == "auto_matched"]
        user_confirmed = [m for m in matched_materials if m.match_method == "user_confirmed"]
        
        # 按置信度分类
        high_confidence = [m for m in matched_materials if m.match_score and m.match_score >= 0.85]
        medium_confidence = [m for m in matched_materials if m.match_score and 0.65 <= m.match_score < 0.85]
        low_confidence = [m for m in matched_materials if m.match_score and m.match_score < 0.65]
        
        return {
            'total_materials': len(total_materials),
            'matched_materials': len(matched_materials),
            'unmatched_materials': len(unmatched_materials),
            'matching_rate': len(matched_materials) / len(total_materials) if total_materials else 0,
            'auto_matched': len(auto_matched),
            'user_confirmed': len(user_confirmed),
            'high_confidence': len(high_confidence),
            'medium_confidence': len(medium_confidence),
            'low_confidence': len(low_confidence),
        }
    
    async def _get_unmatched_materials(
        self,
        db: AsyncSession,
        project_id: int
    ) -> List[ProjectMaterial]:
        """获取未匹配的项目材料"""
        
        stmt = select(ProjectMaterial).where(
            and_(
                ProjectMaterial.project_id == project_id,
                ProjectMaterial.is_matched == False
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def _get_base_materials_for_matching(
        self,
        db: AsyncSession,
        limit: int = 10000
    ) -> List[BaseMaterial]:
        """获取用于匹配的基准材料"""
        
        # 优先获取已验证的基准材料
        stmt = select(BaseMaterial).where(
            BaseMaterial.is_verified == True
        ).limit(limit)
        
        result = await db.execute(stmt)
        verified_materials = result.scalars().all()
        
        # 如果已验证的材料不够，补充未验证的材料
        if len(verified_materials) < limit:
            remaining = limit - len(verified_materials)
            unverified_stmt = select(BaseMaterial).where(
                BaseMaterial.is_verified == False
            ).limit(remaining)
            
            unverified_result = await db.execute(unverified_stmt)
            unverified_materials = unverified_result.scalars().all()
            
            return verified_materials + unverified_materials
        
        return verified_materials
    
    async def _match_single_material(
        self,
        db: AsyncSession,
        project_material: ProjectMaterial,
        base_materials: List[Dict[str, Any]]
    ) -> List[MatchResult]:
        """匹配单个材料"""
        
        project_material_dict = {
            'material_name': project_material.material_name,
            'specification': project_material.specification,
            'unit': project_material.unit,
            'category': project_material.category,
        }
        
        # 预过滤：根据关键词快速筛选候选材料
        candidates = await self._prefilter_candidates(
            project_material_dict, base_materials
        )
        
        if not candidates:
            return []
        
        # 执行详细匹配
        match_results = self.matcher.find_best_matches(
            project_material_dict, candidates, top_k=5
        )
        
        return match_results
    
    async def _prefilter_candidates(
        self,
        project_material: Dict[str, Any],
        base_materials: List[Dict[str, Any]],
        max_candidates: int = 1000
    ) -> List[Dict[str, Any]]:
        """预过滤候选材料"""
        
        material_name = project_material.get('material_name', '').lower()
        material_unit = project_material.get('unit', '').lower()
        
        if not material_name:
            return base_materials[:max_candidates]
        
        candidates = []
        name_keywords = material_name.split()[:3]  # 取前3个词
        
        for base_material in base_materials:
            base_name = base_material.get('name', '').lower()
            base_unit = base_material.get('unit', '').lower()
            
            # 单位必须匹配或可转换
            if material_unit and base_unit:
                std_unit1 = self.matcher._standardize_unit(material_unit)
                std_unit2 = self.matcher._standardize_unit(base_unit)
                if std_unit1 != std_unit2 and not self.matcher._are_convertible_units(std_unit1, std_unit2):
                    continue
            
            # 名称关键词匹配
            if any(keyword in base_name for keyword in name_keywords if len(keyword) > 1):
                candidates.append(base_material)
            
            if len(candidates) >= max_candidates:
                break
        
        return candidates
    
    async def _update_material_match(
        self,
        db: AsyncSession,
        project_material: ProjectMaterial,
        match_result: MatchResult
    ):
        """更新材料匹配结果"""
        
        project_material.is_matched = True
        project_material.matched_material_id = match_result.base_material_id
        project_material.match_score = match_result.similarity_score
        project_material.match_method = match_result.match_method
        
        await db.commit()
    
    async def _update_project_statistics(self, db: AsyncSession, project_id: int):
        """更新项目统计信息"""
        from app.services.project import ProjectService
        from app.models.project import Project
        
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if project:
            await ProjectService.update_project_statistics(db, project)

    async def hierarchical_match_project_materials(
        self,
        db: AsyncSession,
        project_id: int,
        batch_size: int = 100,
        auto_match_threshold: float = 0.85,
        base_price_date: Optional[str] = None,
        base_price_province: Optional[str] = None,
        base_price_city: Optional[str] = None,
        base_price_district: Optional[str] = None
    ) -> Dict[str, Any]:
        """三级地理层次材料匹配"""

        logger.info(f"开始三级匹配项目 {project_id} 的材料")
        logger.info(f"基期信息价参数: 日期={base_price_date}, 省={base_price_province}, 市={base_price_city}, 区={base_price_district}")

        # 获取项目中未匹配的材料
        unmatched_materials = await self._get_unmatched_materials(db, project_id)

        if not unmatched_materials:
            return {
                'total_materials': 0,
                'matched_count': 0,
                'unmatched_count': 0,
                'district_matched': 0,
                'city_matched': 0,
                'province_matched': 0,
                'auto_matched': 0,
                'manual_review_required': 0
            }

        total_materials = len(unmatched_materials)
        district_matched = 0
        city_matched = 0
        province_matched = 0
        auto_matched = 0
        manual_review_required = 0

        # 三级匹配：区县级 -> 市级 -> 省级
        remaining_materials = unmatched_materials.copy()

        # 第一级：区县级匹配
        if base_price_district:
            logger.info(f"开始区县级匹配，区县: {base_price_district}")
            district_base_materials = await self._get_base_materials_by_region(
                db, base_price_date, "district", base_price_district
            )

            remaining_materials, matched_count = await self._match_materials_with_base(
                db, remaining_materials, district_base_materials, auto_match_threshold, "district"
            )
            district_matched = matched_count
            logger.info(f"区县级匹配完成，匹配 {district_matched} 个材料")

        # 第二级：市级匹配
        if base_price_city and remaining_materials:
            logger.info(f"开始市级匹配，城市: {base_price_city}")
            city_base_materials = await self._get_base_materials_by_region(
                db, base_price_date, "municipal", base_price_city
            )

            remaining_materials, matched_count = await self._match_materials_with_base(
                db, remaining_materials, city_base_materials, auto_match_threshold, "city"
            )
            city_matched = matched_count
            logger.info(f"市级匹配完成，匹配 {city_matched} 个材料")

        # 第三级：省级匹配
        if base_price_province and remaining_materials:
            logger.info(f"开始省级匹配，省份: {base_price_province}")
            province_base_materials = await self._get_base_materials_by_region(
                db, base_price_date, "provincial", base_price_province
            )

            remaining_materials, matched_count = await self._match_materials_with_base(
                db, remaining_materials, province_base_materials, auto_match_threshold, "province"
            )
            province_matched = matched_count
            logger.info(f"省级匹配完成，匹配 {province_matched} 个材料")

        # 统计结果
        total_matched = district_matched + city_matched + province_matched
        unmatched_count = len(remaining_materials)
        auto_matched = total_matched  # 所有匹配都是自动的

        logger.info(f"三级匹配完成: 总计 {total_materials} 个材料, 匹配 {total_matched} 个, 未匹配 {unmatched_count} 个")
        logger.info(f"匹配分布: 区县级 {district_matched}, 市级 {city_matched}, 省级 {province_matched}")

        # 更新项目统计
        await self._update_project_statistics(db, project_id)

        return {
            'total_materials': total_materials,
            'matched_count': total_matched,
            'unmatched_count': unmatched_count,
            'district_matched': district_matched,
            'city_matched': city_matched,
            'province_matched': province_matched,
            'auto_matched': auto_matched,
            'manual_review_required': manual_review_required
        }

    async def _get_base_materials_by_region(
        self,
        db: AsyncSession,
        base_price_date: Optional[str],
        price_type: str,
        region_code: str
    ) -> List[Dict[str, Any]]:
        """根据地区和时间获取基准材料"""

        stmt = select(BaseMaterial)
        conditions = []

        # 时间筛选
        if base_price_date:
            # 假设 base_price_date 格式为 "YYYY-MM"
            conditions.append(BaseMaterial.price_date == base_price_date)

        # 地区筛选
        if price_type == "district":
            # 区县级：精确匹配区县代码
            conditions.append(BaseMaterial.region == region_code)
            conditions.append(BaseMaterial.price_type == "municipal")  # 区县属于市刊
        elif price_type == "municipal":
            # 市级：匹配城市代码
            conditions.append(BaseMaterial.region == region_code)
            conditions.append(BaseMaterial.price_type == "municipal")
        elif price_type == "provincial":
            # 省级：匹配省份代码
            conditions.append(BaseMaterial.province == region_code)
            conditions.append(BaseMaterial.price_type == "provincial")

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        base_materials = result.scalars().all()

        logger.info(f"获取 {price_type} 级基准材料: {len(base_materials)} 个")

        return [
            {
                'id': bm.id,
                'name': bm.name,
                'specification': bm.specification,
                'unit': bm.unit,
                'category': bm.category,
                'region': bm.region,
                'price_type': bm.price_type
            }
            for bm in base_materials
        ]

    async def _match_materials_with_base(
        self,
        db: AsyncSession,
        materials: List[ProjectMaterial],
        base_materials: List[Dict[str, Any]],
        threshold: float,
        level: str
    ) -> Tuple[List[ProjectMaterial], int]:
        """将材料与基准材料进行匹配"""

        if not base_materials:
            return materials, 0

        matched_count = 0
        remaining_materials = []

        for material in materials:
            # 尝试匹配
            match_result = self.matcher.find_best_match(
                {
                    'name': material.material_name,
                    'specification': material.specification,
                    'unit': material.unit
                },
                base_materials
            )

            if match_result and match_result.similarity_score >= threshold:
                # 更新匹配信息
                material.is_matched = True
                material.matched_material_id = match_result.base_material_id
                material.match_score = match_result.similarity_score
                material.match_method = f"hierarchical_{level}"

                await db.commit()
                matched_count += 1
                logger.debug(f"材料 '{material.material_name}' 在 {level} 级匹配成功，相似度: {match_result.similarity_score:.3f}")
            else:
                remaining_materials.append(material)

        return remaining_materials, matched_count