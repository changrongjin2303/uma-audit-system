
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_path))

from app.utils.matcher import MaterialMatcher
import numpy as np

def test_config():
    matcher = MaterialMatcher()
    
    print("-" * 30)
    print("当前配置检查:")
    print(f"HIGH_MATCH_THRESHOLD (from matcher.py): {matcher.THRESHOLDS['high']}")
    print(f"MEDIUM_MATCH_THRESHOLD (from matcher.py): {matcher.THRESHOLDS['medium']}")
    print(f"LOW_MATCH_THRESHOLD (from matcher.py): {matcher.THRESHOLDS['low']}")
    
    print(f"Name Weight: {matcher.WEIGHTS['name']}")
    print(f"Specification Weight: {matcher.WEIGHTS['specification']}")
    print("-" * 30)

if __name__ == "__main__":
    test_config()
