"""
手动保存Cookie工具
用户在浏览器登录后，从浏览器导出Cookie并保存
"""

import json


def save_cookies_from_browser():
    """
    从浏览器手动获取Cookie并保存
    """
    print("\n" + "="*60)
    print("手动保存Cookie工具")
    print("="*60)
    print("\n步骤1: 在浏览器中获取Cookie")
    print("-" * 60)
    print("1. 打开浏览器开发者工具 (F12)")
    print("2. 切换到 'Application' 或 '应用' 标签")
    print("3. 左侧选择 'Cookies' -> 'https://www.zhipin.com'")
    print("4. 找到以下重要的Cookie:")
    print("   - __zp_stoken__")
    print("   - _uab_collina")
    print("   - Hm_lpvt_*")
    print("   - Hm_lvt_*")
    print("")
    print("或者更简单的方法:")
    print("1. F12 -> Console (控制台)")
    print("2. 输入: document.cookie")
    print("3. 复制整个输出的字符串")
    print("="*60)

    print("\n步骤2: 输入Cookie字符串")
    print("-" * 60)
    print("请粘贴从浏览器复制的Cookie字符串:")
    print("(直接粘贴 document.cookie 的输出，按回车结束)")
    print("")

    cookie_string = input("Cookie字符串: ").strip()

    if not cookie_string:
        print("\n✗ Cookie字符串为空")
        return

    # 解析Cookie字符串
    cookies = []

    try:
        # 按分号分割
        cookie_pairs = cookie_string.split(';')

        for pair in cookie_pairs:
            pair = pair.strip()
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

        # 保存到文件
        filename = 'data/cookies.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        print("\n" + "="*60)
        print(f"✓ Cookie已保存！")
        print("="*60)
        print(f"文件位置: {filename}")
        print(f"Cookie数量: {len(cookies)}")
        print("\n保存的Cookie:")
        for cookie in cookies[:5]:  # 只显示前5个
            print(f"  - {cookie['name']}: {cookie['value'][:20]}...")
        if len(cookies) > 5:
            print(f"  ... 还有 {len(cookies)-5} 个Cookie")

        print("\n下一步:")
        print("  运行: python run_smart_crawler.py")
        print("  爬虫将使用保存的Cookie自动登录")
        print("="*60)

    except Exception as e:
        print(f"\n✗ Cookie解析失败: {e}")
        print("请确保粘贴的是完整的Cookie字符串")


if __name__ == '__main__':
    save_cookies_from_browser()
