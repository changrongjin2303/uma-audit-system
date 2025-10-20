#!/usr/bin/env python3
"""
测试新的风险等级推断逻辑
"""

def test_risk_level_logic():
    """测试风险等级推断逻辑"""
    
    # 新的风险等级逻辑
    def infer_risk_level(price_variance):
        """根据价格偏差推断风险等级"""
        if price_variance is None:
            return 'unknown'
        
        v = abs(price_variance)
        if v >= 60:
            return 'severe'
        if v >= 40:
            return 'high'
        if v >= 20:
            return 'medium'
        return 'low'
    
    def get_risk_level_text(risk_level):
        """获取风险等级中文描述"""
        risk_map = {
            'low': '正常',
            'medium': '中风险',
            'high': '高风险',
            'severe': '严重风险',
            'unknown': '未知'
        }
        return risk_map.get(risk_level, risk_level)
    
    # 测试用例
    test_cases = [
        (0, '正常'),       # 0% 偏差
        (5, '正常'),       # 5% 偏差
        (15, '正常'),      # 15% 偏差
        (19.9, '正常'),    # 19.9% 偏差
        (20, '中风险'),    # 20% 偏差
        (25, '中风险'),    # 25% 偏差
        (35, '中风险'),    # 35% 偏差
        (39.9, '中风险'),  # 39.9% 偏差
        (40, '高风险'),    # 40% 偏差
        (50, '高风险'),    # 50% 偏差
        (59.9, '高风险'),  # 59.9% 偏差
        (60, '严重风险'),  # 60% 偏差
        (80, '严重风险'),  # 80% 偏差
        (100, '严重风险'), # 100% 偏差
        (-25, '中风险'),   # -25% 偏差（负值）
        (-65, '严重风险'), # -65% 偏差（负值）
        (None, '未知'),    # 空值
    ]
    
    print("🧪 风险等级推断逻辑测试")
    print("=" * 60)
    print(f"{'价格偏差':<12} {'预期结果':<8} {'实际结果':<8} {'测试结果':<8}")
    print("-" * 60)
    
    all_passed = True
    
    for variance, expected in test_cases:
        risk_level = infer_risk_level(variance)
        risk_text = get_risk_level_text(risk_level)
        passed = risk_text == expected
        status = "✅ 通过" if passed else "❌ 失败"
        
        if not passed:
            all_passed = False
        
        variance_str = f"{variance}%" if variance is not None else "None"
        print(f"{variance_str:<12} {expected:<8} {risk_text:<8} {status:<8}")
    
    print("-" * 60)
    
    if all_passed:
        print("🎉 所有测试通过！新的风险等级逻辑工作正常")
    else:
        print("⚠️ 部分测试失败，请检查逻辑")
    
    print("\n📋 新的风险等级分级标准:")
    print("  0%  - 19.9%: 正常")
    print(" 20% - 39.9%: 中风险") 
    print(" 40% - 59.9%: 高风险")
    print(" 60% - 100%+: 严重风险")
    
    return all_passed


if __name__ == "__main__":
    test_risk_level_logic()