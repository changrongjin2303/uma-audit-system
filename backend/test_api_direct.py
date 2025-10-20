#!/usr/bin/env python3
"""
直接测试AI分析API
"""
import asyncio
import os
from openai import AsyncOpenAI

async def test_ai_direct():
    """直接测试AI分析功能"""
    
    # 使用环境变量中的API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY", "sk-cfea46e9f36c4aaba4a9030d2c618284")
    
    print(f"🔑 测试API密钥: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 简单的材料价格分析测试
        prompt = """
作为一名专业的造价工程师，请帮我分析以下建筑材料的市场价格：

材料信息：
- 名称：钢筋HRB400
- 规格：直径12mm
- 单位：吨
- 地区：全国

请提供合理的价格区间分析，并返回JSON格式：
{
    "price_range": {
        "min_price": <数值>,
        "max_price": <数值>,
        "avg_price": <数值>
    },
    "confidence_score": <0-1之间的置信度>,
    "reasoning": "<分析推理过程>"
}
        """
        
        print("🚀 正在调用通义千问API...")
        
        response = await client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一名专业的造价工程师，擅长建筑材料价格分析。请基于最新的网络搜索信息提供准确的价格分析。"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            extra_body={
                "enable_search": True  # 启用联网搜索
            }
        )
        
        print("✅ API调用成功！")
        print(f"📝 模型: {response.model}")
        print(f"💰 Token使用: {response.usage}")
        print(f"📄 AI分析结果:\n{response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API调用失败: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_ai_direct())