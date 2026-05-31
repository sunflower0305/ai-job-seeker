"""
诊断Boss直聘页面结构
查看实际的HTML以更新选择器
"""

from _bootstrap import PROJECT_ROOT

import sys
import os

from playwright.sync_api import sync_playwright
import time


def diagnose():
    """诊断页面"""
    print("\n" + "="*60)
    print("Boss直聘页面诊断")
    print("="*60)

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        # 访问搜索页
        url = "https://www.zhipin.com/web/geek/job?query=Python&city=101010100"
        print(f"\n访问: {url}")

        page.goto(url, wait_until='domcontentloaded')
        time.sleep(5)

        # 保存页面HTML
        html = page.content()
        with open('data/boss_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ 页面HTML已保存到: data/boss_page_debug.html")

        # 截图
        page.screenshot(path='data/boss_page_screenshot.png', full_page=True)
        print(f"✓ 页面截图已保存到: data/boss_page_screenshot.png")

        # 检查常见选择器
        print("\n检查选择器:")
        selectors = [
            '.job-list-box',
            '.job-card-wrapper',
            '.job-list',
            '[class*="job"]',
            '[class*="list"]',
            'ul.job-list-box',
            'div.job-list-box',
        ]

        for selector in selectors:
            elem = page.query_selector(selector)
            if elem:
                print(f"  ✓ {selector}")
            else:
                print(f"  ✗ {selector}")

        # 获取页面标题
        title = page.title()
        print(f"\n页面标题: {title}")

        # 检查是否有验证码
        captcha_keywords = ['验证', 'verify', 'captcha', '安全验证']
        page_text = page.inner_text('body')

        print(f"\n检查验证码:")
        for keyword in captcha_keywords:
            if keyword in page_text or keyword in html:
                print(f"  ⚠️  检测到关键词: {keyword}")

        # 查找所有class包含job的元素
        print(f"\n所有包含'job'的class:")
        job_classes = page.evaluate('''
            () => {
                const elements = document.querySelectorAll('[class*="job"]');
                const classes = new Set();
                elements.forEach(el => {
                    el.classList.forEach(c => {
                        if (c.includes('job')) classes.add(c);
                    });
                });
                return Array.from(classes).slice(0, 20);
            }
        ''')
        for cls in job_classes:
            print(f"  - {cls}")

        browser.close()

        print("\n" + "="*60)
        print("诊断完成")
        print("="*60)
        print("\n建议:")
        print("  1. 查看 data/boss_page_debug.html 了解页面结构")
        print("  2. 查看 data/boss_page_screenshot.png 了解页面显示")
        print("  3. 根据实际结构更新选择器")


if __name__ == '__main__':
    diagnose()
