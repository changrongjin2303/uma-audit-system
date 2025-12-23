
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_path))

from app.utils.matcher import MaterialMatcher

def test_similarity(name1, name2):
    matcher = MaterialMatcher()
    score = matcher._calculate_name_similarity(name1, name2)
    print(f"Name 1: {name1}")
    print(f"Name 2: {name2}")
    print(f"Similarity Score: {score}")
    
    # Also print the breakdown
    name1_clean = matcher._clean_text(name1)
    name2_clean = matcher._clean_text(name2)
    
    from fuzzywuzzy import fuzz
    import difflib
    import numpy as np
    
    edit_score = fuzz.ratio(name1_clean, name2_clean) / 100.0
    partial_score = fuzz.partial_ratio(name1_clean, name2_clean) / 100.0
    
    keywords1 = matcher._extract_keywords(name1_clean)
    keywords2 = matcher._extract_keywords(name2_clean)
    keyword_score = matcher._calculate_keyword_similarity(keywords1, keywords2)
    
    sequence_score = difflib.SequenceMatcher(None, name1_clean, name2_clean).ratio()
    
    print("-" * 20)
    print("Breakdown:")
    print(f"Cleaned 1: {name1_clean}")
    print(f"Cleaned 2: {name2_clean}")
    print(f"Edit Score (30%): {edit_score}")
    print(f"Partial Score (20%): {partial_score}")
    print(f"Keyword Score (30%): {keyword_score}")
    print(f"Keywords 1: {keywords1}")
    print(f"Keywords 2: {keywords2}")
    print(f"Sequence Score (20%): {sequence_score}")
    
    weighted_score = np.average([edit_score, partial_score, keyword_score, sequence_score], weights=[0.3, 0.2, 0.3, 0.2])
    print(f"Calculated Weighted Score: {weighted_score}")

if __name__ == "__main__":
    test_similarity("钢化玻璃", "10厚固定钢化玻璃")
