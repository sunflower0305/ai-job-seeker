"""
从token创建Cookie文件
"""

from _bootstrap import PROJECT_ROOT

import json

# 用户提供的token
token_value = "V2R94hE-L801lvVtRuyRkcLSm47DrRwS0~|R94hE-L801lvVtRuyRkcLSm47DrVwSk~"

print("\n" + "="*60)
print("从Token创建Cookie")
print("="*60)

# 创建Cookie列表
cookies = [
    {
        "name": "__zp_stoken__",
        "value": token_value,
        "domain": ".zhipin.com",
        "path": "/",
        "expires": -1,
        "httpOnly": False,
        "secure": True,
        "sameSite": "Lax"
    }
]

# 保存
filename = 'data/cookies.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(cookies, f, indent=2, ensure_ascii=False)

print(f"\n✓ Cookie已保存到: {filename}")
print(f"✓ Token: {token_value[:30]}...")
print("\n现在可以运行爬虫了！")
print("\n测试命令:")
print("  python scripts/crawlers/run_smart_crawler.py --cities 北京 --keywords Python --total 20 --headless")
print("="*60)
