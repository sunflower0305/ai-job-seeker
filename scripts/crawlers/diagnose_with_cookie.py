"""
使用Cookie诊断页面
查找正确的职位列表选择器
"""

from _bootstrap import PROJECT_ROOT

import sys
import os

from playwright.sync_api import sync_playwright
import json
import time


def diagnose_with_cookie():
    """使用Cookie诊断"""
    print("\n" + "="*60)
    print("使用Cookie诊断Boss直聘页面")
    print("="*60)

    # 加载Cookie
    try:
        with open('data/cookies.json', 'r') as f:
            cookies = json.load(f)
        print(f"✓ Cookie已加载: {len(cookies)}个")
    except:
        print("✗ Cookie文件不存在")
        return

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)  # 有头模式，可以看到
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        # 添加Cookie
        context.add_cookies(cookies)

        page = context.new_page()

        # 访问搜索页
        url = "https://www.zhipin.com/web/geek/job?query=Python&city=101010100"
        print(f"\n访问: {url}")

        page.goto(url, wait_until='domcontentloaded')

        # 等待页面完全加载
        print("等待页面加载...")
        time.sleep(8)

        # 保存完整HTML
        html = page.content()
        with open('data/boss_page_full.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ 完整HTML已保存: data/boss_page_full.html")

        # 截图
        page.screenshot(path='data/boss_screenshot.png', full_page=True)
        print(f"✓ 截图已保存: data/boss_screenshot.png")

        # 检查页面标题
        title = page.title()
        print(f"\n页面标题: {title}")

        # 检查登录状态
        print("\n检查登录状态:")
        login_indicators = [
            '.user-nav',
            '.user-name',
            '[class*="avatar"]',
            '.btn-sign-up',
            '.btns',
        ]

        for selector in login_indicators:
            elem = page.query_selector(selector)
            if elem:
                text = elem.inner_text() if elem else ''
                print(f"  ✓ {selector}: {text[:50]}")

        # 查找职位相关的元素
        print("\n查找职位元素:")

        # 尝试多种可能的选择器
        selectors_to_try = [
            'ul.job-list-box',
            'div.job-list-box',
            '[class*="job-list"]',
            '[class*="job-card"]',
            'li.job-primary',
            'div.job-primary',
            'ul[class*="job"]',
            'div[class*="recommend"]',
        ]

        found_selector = None
        for selector in selectors_to_try:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"  ✓ {selector}: 找到 {len(elements)} 个元素")
                if not found_selector:
                    found_selector = selector
            else:
                print(f"  ✗ {selector}: 未找到")

        # 获取所有包含"job"的class
        print("\n所有包含'job'的元素:")
        job_elements = page.evaluate('''
            () => {
                const elements = document.querySelectorAll('[class*="job"]');
                const result = [];
                elements.forEach((el, i) => {
                    if (i < 10) {  // 只取前10个
                        result.push({
                            tag: el.tagName,
                            classes: Array.from(el.classList).join(' '),
                            text: el.innerText ? el.innerText.substring(0, 50) : ''
                        });
                    }
                });
                return result;
            }
        ''')

        for i, elem in enumerate(job_elements, 1):
            print(f"\n  {i}. <{elem['tag']}> class=\"{elem['classes']}\"")
            if elem['text']:
                print(f"     文本: {elem['text'][:50]}...")

        # 尝试执行JavaScript查找职位
        print("\n\n尝试用JavaScript查找职位列表:")
        job_data = page.evaluate('''
            () => {
                // 方法1: 查找包含职位信息的元素
                const containers = document.querySelectorAll('[class*="job"]');
                const jobs = [];

                containers.forEach(el => {
                    const text = el.innerText;
                    // 如果包含薪资信息，可能是职位卡片
                    if (text && (text.includes('k') || text.includes('K') || text.includes('元'))) {
                        jobs.push({
                            html: el.outerHTML.substring(0, 200),
                            text: text.substring(0, 100)
                        });
                    }
                });

                return jobs.slice(0, 5);  // 只返回前5个
            }
        ''')

        print(f"找到 {len(job_data)} 个可能的职位元素:")
        for i, job in enumerate(job_data, 1):
            print(f"\n  职位 {i}:")
            print(f"  文本: {job['text'][:80]}...")

        # 等待用户查看
        print("\n" + "="*60)
        print("浏览器将保持打开10秒，请查看页面...")
        print("="*60)
        time.sleep(10)

        browser.close()

        print("\n诊断完成！")
        print("\n请检查:")
        print("  1. data/boss_page_full.html - 完整的页面HTML")
        print("  2. data/boss_screenshot.png - 页面截图")
        print("\n如果看到职位列表，说明Cookie有效，只是选择器需要更新")


if __name__ == '__main__':
    diagnose_with_cookie()
