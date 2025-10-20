#!/usr/bin/env python3
"""
通义千问API测试脚本
用于验证API密钥和连接是否正常
"""
import os
import asyncio
from openai import AsyncOpenAI

async def test_dashscope():
    """测试通义千问API"""
    
    # 从环境变量或直接设置API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("❌ 错误：未找到DASHSCOPE_API_KEY环境变量")
        print("请在 .env 文件中设置：DASHSCOPE_API_KEY=你的API密钥")
        return
    
    print(f"🔑 使用API密钥: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        print("🚀 正在测试通义千问API连接...")
        
        # 测试基本对话
        response = await client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': '你是一名专业的造价工程师，擅长建筑材料价格分析。'},
                {'role': 'user', 'content': '请分析混凝土C30的市场价格，并给出价格区间。'}
            ],
            temperature=0.3,
            max_tokens=1000,
            extra_body={
                "enable_search": True  # 启用联网搜索
            }
        )
        
        print("✅ API调用成功！")
        print(f"📝 模型响应: {response.model}")
        print(f"💰 使用情况: {response.usage}")
        print(f"📄 回答内容:\n{response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API调用失败: {str(e)}")
        print("\n可能的解决方案:")
        print("1. 检查API密钥是否正确")
        print("2. 检查网络连接")
        print("3. 确认阿里云账户有足够的余额")
        print("4. 检查API密钥是否有调用权限")
        return False

if __name__ == "__main__":
    # 加载环境变量
    from pathlib import Path
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # 运行测试
    asyncio.run(test_dashscope())