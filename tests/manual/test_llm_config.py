#!/usr/bin/env python
"""
测试通义千问 API 配置
"""

from _bootstrap import PROJECT_ROOT
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=== 环境变量配置检查 ===\n")

# 检查必需的环境变量
required_vars = {
    'LLM_API_KEY': '通义千问 API Key',
    'LLM_BASE_URL': '通义千问 Base URL',
    'LLM_MODEL': '使用的模型'
}

all_set = True
for var_name, description in required_vars.items():
    value = os.getenv(var_name)
    if value:
        # 隐藏 API Key 的大部分内容
        if 'KEY' in var_name and len(value) > 10:
            display_value = value[:10] + '...' + value[-4:]
        else:
            display_value = value
        print(f"✓ {description} ({var_name}): {display_value}")
    else:
        print(f"✗ {description} ({var_name}): 未设置")
        all_set = False

print()

if all_set:
    print("✓ 所有配置已正确设置！")

    # 测试 API 连接
    print("\n=== 测试 API 连接 ===\n")
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=os.getenv('LLM_MODEL'),
            openai_api_key=os.getenv('LLM_API_KEY'),
            openai_api_base=os.getenv('LLM_BASE_URL'),
            temperature=0.3
        )

        print("正在测试 API 调用...")
        response = llm.invoke("你好，请简单介绍一下你自己。")
        print(f"\n✓ API 调用成功！")
        print(f"响应: {response.content[:100]}...")

    except Exception as e:
        print(f"\n✗ API 调用失败: {str(e)}")
else:
    print("✗ 请在 .env 文件中设置所有必需的环境变量")
    print("参考 .env.example 文件")
