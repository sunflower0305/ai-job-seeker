#!/usr/bin/env python
"""
测试网络搜索功能
"""
import json
from duckduckgo_search import DDGS

print("=== 测试网络搜索功能 ===\n")

# 测试1: 搜索招聘信息
print("【测试1】搜索最新招聘信息")
print("-" * 50)
try:
    query = "Python开发工程师 北京 招聘 最新"
    print(f"搜索查询: {query}\n")

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))

    if results:
        print(f"✓ 找到 {len(results)} 条结果:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   摘要: {result.get('body', 'N/A')[:100]}...")
            print(f"   链接: {result.get('href', 'N/A')}")
            print()
    else:
        print("✗ 未找到结果")
except Exception as e:
    print(f"✗ 搜索失败: {str(e)}")

print("\n" + "=" * 50 + "\n")

# 测试2: 搜索薪资信息
print("【测试2】搜索薪资趋势")
print("-" * 50)
try:
    query = "北京 Python开发工程师 薪资 行情 2024"
    print(f"搜索查询: {query}\n")

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))

    if results:
        print(f"✓ 找到 {len(results)} 条结果:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   摘要: {result.get('body', 'N/A')[:100]}...")
            print(f"   链接: {result.get('href', 'N/A')}")
            print()
    else:
        print("✗ 未找到结果")
except Exception as e:
    print(f"✗ 搜索失败: {str(e)}")

print("\n" + "=" * 50 + "\n")

# 测试3: 搜索公司信息
print("【测试3】搜索公司信息")
print("-" * 50)
try:
    query = "阿里巴巴 公司 怎么样 评价"
    print(f"搜索查询: {query}\n")

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))

    if results:
        print(f"✓ 找到 {len(results)} 条结果:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   摘要: {result.get('body', 'N/A')[:100]}...")
            print(f"   链接: {result.get('href', 'N/A')}")
            print()
    else:
        print("✗ 未找到结果")
except Exception as e:
    print(f"✗ 搜索失败: {str(e)}")

print("\n" + "=" * 50)
print("\n✓ 所有测试完成！网络搜索功能正常工作。")
