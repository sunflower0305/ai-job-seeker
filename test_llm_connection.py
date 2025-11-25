"""
测试 LLM API 连接
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# 加载 .env 文件
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 从环境变量读取配置
api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL", "qwen-plus")

print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not found")
print(f"Base URL: {base_url}")
print(f"Model: {model}")

# 测试连接
try:
    llm = ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0.3,
        timeout=30
    )

    messages = [
        SystemMessage(content="你是一个测试助手"),
        HumanMessage(content="请回复：连接成功")
    ]

    print("\n开始测试连接...")
    response = llm.invoke(messages)
    print(f"✅ 连接成功！")
    print(f"响应: {response.content}")

except Exception as e:
    print(f"❌ 连接失败！")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误: {e}")
    import traceback
    print(f"详细信息:\n{traceback.format_exc()}")

