import re
import difflib
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from loguru import logger

import jieba
import jieba.analyse
from fuzzywuzzy import fuzz, process
import numpy as np


@dataclass
class MatchResult:
    """匹配结果类"""
    base_material_id: int
    similarity_score: float
    match_method: str
    name_score: float
    spec_score: float
    unit_score: float
    category_score: float
    confidence_level: str


class MaterialMatcher:
    """材料匹配器"""
    
    # 匹配阈值设定
    THRESHOLDS = {
        'high': 0.85,      # 高匹配度，自动匹配
        'medium': 0.65,    # 中匹配度，需要人工确认
        'low': 0.45        # 低匹配度，标记为疑似
    }
    
    # 权重配置
    WEIGHTS = {
        'name': 0.4,       # 名称权重
        'specification': 0.3,  # 规格权重
        'category': 0.2,   # 分类权重
        'unit': 0.1        # 单位权重
    }
    
    def __init__(self):
        """初始化材料匹配器"""
        # 初始化jieba分词
        jieba.initialize()
        
        # 加载自定义词典（建材相关词汇）
        self._load_custom_dict()
        
        # 预处理正则表达式
        self.spec_patterns = [
            r'(\d+\.?\d*)[×xX*](\d+\.?\d*)[×xX*](\d+\.?\d*)',  # 尺寸规格
            r'φ?(\d+\.?\d*)',  # 直径
            r'(\d+\.?\d*)mm',  # 毫米
            r'(\d+\.?\d*)m',   # 米
            r'(\d+\.?\d*)kg',  # 千克
            r'C(\d+)',         # 混凝土标号
            r'Q(\d+)',         # 钢材牌号
        ]
        
        # 单位标准化映射
        self.unit_mapping = {
            '个': ['个', '只', '件', 'pcs'],
            'm': ['m', '米', 'M'],
            'm²': ['m²', '㎡', 'm2', '平方米', '平米'],
            'm³': ['m³', 'm3', '立方米', '立米'],
            'kg': ['kg', 'KG', '公斤', '千克'],
            't': ['t', 'T', '吨'],
            '套': ['套', 'set'],
            'L': ['L', 'l', '升', '公升'],
        }
    
    def _load_custom_dict(self):
        """加载自定义建材词典"""
        # 这里可以加载专门的建材词典文件
        building_materials = [
            "钢筋", "混凝土", "水泥", "砂浆", "砖块", "钢管", "型钢", "板材",
            "防水材料", "保温材料", "装饰材料", "管道", "阀门", "电缆", "开关",
            "灯具", "五金", "涂料", "胶粘剂", "密封材料"
        ]
        
        for word in building_materials:
            jieba.add_word(word)
    
    def calculate_similarity(
        self,
        project_material: Dict[str, Any],
        base_material: Dict[str, Any]
    ) -> MatchResult:
        """计算两个材料的相似度"""
        
        # 计算各维度得分
        name_score = self._calculate_name_similarity(
            project_material.get('material_name', ''),
            base_material.get('name', '')
        )
        
        spec_score = self._calculate_specification_similarity(
            project_material.get('specification', ''),
            base_material.get('specification', '')
        )
        
        unit_score = self._calculate_unit_similarity(
            project_material.get('unit', ''),
            base_material.get('unit', '')
        )
        
        category_score = self._calculate_category_similarity(
            project_material.get('category', ''),
            base_material.get('category', '')
        )
        
        # 加权计算总分
        total_score = (
            name_score * self.WEIGHTS['name'] +
            spec_score * self.WEIGHTS['specification'] +
            category_score * self.WEIGHTS['category'] +
            unit_score * self.WEIGHTS['unit']
        )
        
        # 确定置信度等级
        confidence_level = self._determine_confidence_level(total_score)
        
        return MatchResult(
            base_material_id=base_material.get('id'),
            similarity_score=total_score,
            match_method='weighted_similarity',
            name_score=name_score,
            spec_score=spec_score,
            unit_score=unit_score,
            category_score=category_score,
            confidence_level=confidence_level
        )
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """计算名称相似度"""
        if not name1 or not name2:
            return 0.0
        
        # 文本预处理
        name1_clean = self._clean_text(name1)
        name2_clean = self._clean_text(name2)
        
        # 多种相似度算法的组合
        scores = []
        
        # 1. 编辑距离相似度
        edit_score = fuzz.ratio(name1_clean, name2_clean) / 100.0
        scores.append(edit_score)
        
        # 2. 部分字符串匹配
        partial_score = fuzz.partial_ratio(name1_clean, name2_clean) / 100.0
        scores.append(partial_score)
        
        # 3. 分词后的关键词匹配
        keywords1 = self._extract_keywords(name1_clean)
        keywords2 = self._extract_keywords(name2_clean)
        keyword_score = self._calculate_keyword_similarity(keywords1, keywords2)
        scores.append(keyword_score)
        
        # 4. 序列匹配
        sequence_score = difflib.SequenceMatcher(None, name1_clean, name2_clean).ratio()
        scores.append(sequence_score)
        
        # 返回加权平均
        weights = [0.3, 0.2, 0.3, 0.2]
        return np.average(scores, weights=weights)
    
    def _calculate_specification_similarity(self, spec1: str, spec2: str) -> float:
        """计算规格相似度"""
        if not spec1 and not spec2:
            return 1.0  # 都为空，完全匹配
        if not spec1 or not spec2:
            return 0.5  # 一个为空，部分匹配
        
        spec1_clean = self._clean_text(spec1)
        spec2_clean = self._clean_text(spec2)
        
        # 提取数值参数
        params1 = self._extract_parameters(spec1_clean)
        params2 = self._extract_parameters(spec2_clean)
        
        # 计算参数相似度
        param_score = self._calculate_parameter_similarity(params1, params2)
        
        # 计算文本相似度
        text_score = fuzz.token_sort_ratio(spec1_clean, spec2_clean) / 100.0
        
        # 综合得分
        return (param_score + text_score) / 2
    
    def _calculate_unit_similarity(self, unit1: str, unit2: str) -> float:
        """计算单位相似度"""
        if not unit1 or not unit2:
            return 0.0
        
        # 标准化单位
        std_unit1 = self._standardize_unit(unit1)
        std_unit2 = self._standardize_unit(unit2)
        
        if std_unit1 == std_unit2:
            return 1.0
        
        # 检查单位转换关系
        if self._are_convertible_units(std_unit1, std_unit2):
            return 0.8
        
        return 0.0
    
    def _calculate_category_similarity(self, cat1: str, cat2: str) -> float:
        """计算分类相似度"""
        if not cat1 and not cat2:
            return 1.0
        if not cat1 or not cat2:
            return 0.5
        
        cat1_clean = self._clean_text(cat1)
        cat2_clean = self._clean_text(cat2)
        
        # 直接匹配
        if cat1_clean == cat2_clean:
            return 1.0
        
        # 部分匹配
        return fuzz.partial_ratio(cat1_clean, cat2_clean) / 100.0
    
    def _clean_text(self, text: str) -> str:
        """文本清理和标准化"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 统一标点符号
        text = text.replace('（', '(').replace('）', ')')
        text = text.replace('【', '[').replace('】', ']')
        
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 使用jieba进行分词和关键词提取
        keywords = jieba.analyse.extract_tags(text, topK=10, withWeight=False)
        
        # 过滤停用词
        stopwords = {'的', '和', '与', '或', '及', '等', '型', '类', '种'}
        keywords = [kw for kw in keywords if kw not in stopwords and len(kw) > 1]
        
        return keywords
    
    def _calculate_keyword_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """计算关键词相似度"""
        if not keywords1 or not keywords2:
            return 0.0
        
        # 计算交集比例
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        intersection = set1 & set2
        union = set1 | set2
        
        if not union:
            return 0.0
        
        jaccard_score = len(intersection) / len(union)
        
        # 考虑部分匹配的关键词
        partial_matches = 0
        for kw1 in keywords1:
            for kw2 in keywords2:
                if kw1 in kw2 or kw2 in kw1:
                    partial_matches += 1
                    break
        
        partial_score = partial_matches / max(len(keywords1), len(keywords2))
        
        return (jaccard_score + partial_score) / 2
    
    def _extract_parameters(self, spec: str) -> Dict[str, List[float]]:
        """从规格中提取数值参数"""
        parameters = {
            'dimensions': [],
            'diameter': [],
            'length': [],
            'weight': [],
            'grade': []
        }
        
        for pattern in self.spec_patterns:
            matches = re.findall(pattern, spec, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 多维尺寸
                    try:
                        values = [float(v) for v in match if v]
                        parameters['dimensions'].extend(values)
                    except ValueError:
                        continue
                else:
                    # 单一数值
                    try:
                        value = float(match)
                        if 'φ' in pattern or 'diameter' in pattern.lower():
                            parameters['diameter'].append(value)
                        elif 'mm' in pattern or 'm' in pattern:
                            parameters['length'].append(value)
                        elif 'kg' in pattern:
                            parameters['weight'].append(value)
                        elif 'C' in pattern or 'Q' in pattern:
                            parameters['grade'].append(value)
                    except ValueError:
                        continue
        
        return parameters
    
    def _calculate_parameter_similarity(self, params1: Dict, params2: Dict) -> float:
        """计算参数相似度"""
        if not params1 and not params2:
            return 1.0
        
        scores = []
        
        for param_type in ['dimensions', 'diameter', 'length', 'weight', 'grade']:
            values1 = params1.get(param_type, [])
            values2 = params2.get(param_type, [])
            
            if not values1 and not values2:
                continue
            
            if not values1 or not values2:
                scores.append(0.0)
                continue
            
            # 计算数值相似度
            score = self._calculate_numeric_similarity(values1, values2)
            scores.append(score)
        
        return np.mean(scores) if scores else 0.5
    
    def _calculate_numeric_similarity(self, values1: List[float], values2: List[float]) -> float:
        """计算数值相似度"""
        if not values1 or not values2:
            return 0.0
        
        # 对比最接近的值
        max_score = 0.0
        for v1 in values1:
            for v2 in values2:
                # 计算相对误差
                if max(v1, v2) > 0:
                    relative_error = abs(v1 - v2) / max(v1, v2)
                    similarity = max(0, 1 - relative_error)
                    max_score = max(max_score, similarity)
        
        return max_score
    
    def _standardize_unit(self, unit: str) -> str:
        """标准化单位"""
        unit_clean = unit.strip().lower()
        
        for std_unit, variants in self.unit_mapping.items():
            if unit_clean in [v.lower() for v in variants]:
                return std_unit
        
        return unit_clean
    
    def _are_convertible_units(self, unit1: str, unit2: str) -> bool:
        """判断两个单位是否可以转换"""
        # 长度单位
        length_units = {'m', 'mm', 'cm', 'km'}
        if unit1 in length_units and unit2 in length_units:
            return True
        
        # 面积单位
        area_units = {'m²', 'cm²', 'mm²'}
        if unit1 in area_units and unit2 in area_units:
            return True
        
        # 体积单位
        volume_units = {'m³', 'L', 'cm³'}
        if unit1 in volume_units and unit2 in volume_units:
            return True
        
        # 重量单位
        weight_units = {'kg', 't', 'g'}
        if unit1 in weight_units and unit2 in weight_units:
            return True
        
        return False
    
    def _determine_confidence_level(self, score: float) -> str:
        """确定置信度等级"""
        if score >= self.THRESHOLDS['high']:
            return 'high'
        elif score >= self.THRESHOLDS['medium']:
            return 'medium'
        elif score >= self.THRESHOLDS['low']:
            return 'low'
        else:
            return 'very_low'
    
    def find_best_matches(
        self,
        project_material: Dict[str, Any],
        base_materials: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[MatchResult]:
        """找到最佳匹配的基准材料"""

        matches = []

        for base_material in base_materials:
            try:
                match_result = self.calculate_similarity(project_material, base_material)
                matches.append(match_result)
            except Exception as e:
                logger.warning(f"匹配计算失败: {e}")
                continue

        # 按相似度排序，返回前k个
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches[:top_k]

    def find_best_match(
        self,
        project_material: Dict[str, Any],
        base_materials: List[Dict[str, Any]]
    ) -> Optional[MatchResult]:
        """找到最佳匹配的单个基准材料"""

        best_matches = self.find_best_matches(project_material, base_materials, top_k=1)
        return best_matches[0] if best_matches else None
    
    def is_material_matched(self, match_result: MatchResult) -> bool:
        """判断材料是否匹配成功"""
        return match_result.confidence_level in ['high', 'medium']
    
    def get_match_explanation(self, match_result: MatchResult) -> str:
        """获取匹配结果的解释"""
        explanations = []
        
        if match_result.name_score > 0.8:
            explanations.append("名称高度相似")
        elif match_result.name_score > 0.6:
            explanations.append("名称部分相似")
        
        if match_result.spec_score > 0.8:
            explanations.append("规格高度匹配")
        elif match_result.spec_score > 0.6:
            explanations.append("规格部分匹配")
        
        if match_result.unit_score == 1.0:
            explanations.append("单位完全匹配")
        elif match_result.unit_score > 0.7:
            explanations.append("单位可转换")
        
        if match_result.category_score > 0.8:
            explanations.append("分类匹配")
        
        return "; ".join(explanations) if explanations else "低相似度匹配"