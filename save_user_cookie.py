"""
保存用户提供的Cookie
"""

import json

# 用户提供的完整Cookie字符串
cookie_string = "'__snaker__id=bjDT5gyPQQ141wsG; ab_guid=80dde8b9-78ca-4ba9-9f25-f2cfd41ae720; __g=-; __l=l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjob%3Fquery%3DPython%26city%3D101010100&r=&g=&s=3&friend_source=0; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1763606922; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1763606922; HMACCOUNT=3ABD5BE86D64D4C7; bst=V2R94hE-L801lvVtRuyRkcLSm47DrRwS0~|R94hE-L801lvVtRuyRkcLSm47DrVwSk~; __c=1763606917; __a=31197815.1763606917..1763606917.3.1.3.3; __zp_stoken__=61effPTzDosOBwpLCukksChAXDQpGLT48L8KGRT0wRzpJPTw9PEc9PEUaPS3DpsK8w5rCviBkw44NPjA8PUk%2BPUY9OkMgPEnFgMK9PD0yw7fCv8OdwrwgYsONClUKw7DCvQrEhsK%2BDRbCvQsywrorKyHCvUE9Rj8Wwr3CvcOHR8K6w4HDhEbCu8K%2Bw4g9Pj8%2BN0FbWlpbQT5QT1wLUGROYmVUEVdYVDA%2FSTs%2BIcODw741QAoLCg0RDQwNCg4XFhcRDQ0MDQoODA0MCw81PMKnw4HCncS4w6Jsw7DEn8KfW8K5SsK4wqjEgMKawrTCm8O9c8O8acKbwrDCsMK7wrnDg8KvccOBwrvCn8KHw4llcmNZWMOGU8OATktKUkp6S21pE2RiCxlBFlYdw4s%3D; SERVERID=606144fb348bc19e48aededaa626f54e|1763607111|1763606908'"

# 清理字符串（移除首尾的单引号）
cookie_string = cookie_string.strip("'")

print("\n" + "="*60)
print("保存用户Cookie")
print("="*60)

# 解析Cookie
cookies = []
cookie_pairs = cookie_string.split('; ')

print(f"\n检测到 {len(cookie_pairs)} 个Cookie")

for pair in cookie_pairs:
    if '=' in pair:
        name, value = pair.split('=', 1)
        cookie = {
            'name': name.strip(),
            'value': value.strip(),
            'domain': '.zhipin.com',
            'path': '/',
            'expires': -1,
            'httpOnly': False,
            'secure': True,
            'sameSite': 'Lax'
        }
        cookies.append(cookie)

# 保存
filename = 'data/cookies.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(cookies, f, indent=2, ensure_ascii=False)

print(f"\n✓ Cookie已保存: {filename}")
print(f"✓ 共保存 {len(cookies)} 个Cookie\n")

print("重要Cookie:")
important_cookies = ['__zp_stoken__', '__snaker__id', 'bst', '__a', '__c']
for cookie in cookies:
    if cookie['name'] in important_cookies:
        print(f"  ✓ {cookie['name']}: {cookie['value'][:30]}...")

print("\n" + "="*60)
print("Cookie保存成功！现在可以开始爬取了")
print("="*60)
print("\n推荐命令:")
print("  # 小规模测试（20条）")
print("  python run_smart_crawler.py --cities 北京 --keywords Python --total 20 --headless")
print("\n  # 正式爬取（100条）")
print("  python run_smart_crawler.py --cities 北京 上海 --keywords Python Java --total 100 --headless")
print("="*60)
