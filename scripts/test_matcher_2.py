
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_path))

from app.utils.matcher import MaterialMatcher
import numpy as np

def test_similarity(name1, name2):
    matcher = MaterialMatcher()
    
    # 打印原始名称
    print(f"Name 1: {name1}")
    print(f"Name 2: {name2}")
    
    # 文本预处理
    name1_clean = matcher._clean_text(name1)
    name2_clean = matcher._clean_text(name2)
    print(f"Cleaned 1: {name1_clean}")
    print(f"Cleaned 2: {name2_clean}")
    
    from fuzzywuzzy import fuzz
    import difflib
    
    # 1. 编辑距离相似度 (30%)
    edit_score = fuzz.ratio(name1_clean, name2_clean) / 100.0
    
    # 2. 部分字符串匹配 (20%)
    partial_score = fuzz.partial_ratio(name1_clean, name2_clean) / 100.0
    
    # 3. 关键词匹配 (30%)
    keywords1 = matcher._extract_keywords(name1_clean)
    keywords2 = matcher._extract_keywords(name2_clean)
    keyword_score = matcher._calculate_keyword_similarity(keywords1, keywords2)
    
    # 4. 序列匹配 (20%)
    sequence_score = difflib.SequenceMatcher(None, name1_clean, name2_clean).ratio()
    
    print("-" * 20)
    print("Breakdown:")
    print(f"Edit Score (30%): {edit_score:.4f}")
    print(f"Partial Score (20%): {partial_score:.4f}")
    print(f"Keyword Score (30%): {keyword_score:.4f}")
    print(f"  Keywords 1: {keywords1}")
    print(f"  Keywords 2: {keywords2}")
    print(f"Sequence Score (20%): {sequence_score:.4f}")
    
    weighted_score = np.average([edit_score, partial_score, keyword_score, sequence_score], weights=[0.3, 0.2, 0.3, 0.2])
    print("-" * 20)
    print(f"Calculated Weighted Score: {weighted_score:.4f}")

if __name__ == "__main__":
    test_similarity("聚合物水泥基复合防水涂料", "JS聚合物水泥基防水涂料")
