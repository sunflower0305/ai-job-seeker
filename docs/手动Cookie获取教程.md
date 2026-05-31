# Boss直聘手动Cookie获取教程

## 方法一：通过开发者工具（推荐）

### 步骤1：打开开发者工具
1. 在Boss直聘页面按 `F12` 键
2. 或右键点击 -> 检查

### 步骤2：获取Cookie
1. 切换到 `Console` (控制台) 标签
2. 输入以下命令并回车：
   ```javascript
   document.cookie
   ```
3. 复制输出的整个字符串

### 步骤3：保存Cookie
1. 运行Python脚本：
   ```bash
   python scripts/crawlers/save_cookies_manual.py
   ```
2. 粘贴刚才复制的Cookie字符串
3. 按回车完成保存

### 步骤4：使用Cookie爬取
```bash
python scripts/crawlers/run_smart_crawler.py --total 50
```

---

## 方法二：通过Application标签

### 步骤1：打开开发者工具
按 `F12` 打开开发者工具

### 步骤2：查看Cookie
1. 切换到 `Application` (应用) 标签
2. 左侧展开 `Cookies`
3. 点击 `https://www.zhipin.com`

### 步骤3：重要的Cookie

需要的关键Cookie：
- `__zp_stoken__` - 最重要，登录凭证
- `_uab_collina` - 用户标识
- `Hm_lvt_*` - 访问时间
- `Hm_lpvt_*` - 页面访问

### 步骤4：手动复制

1. 点击每个Cookie
2. 双击 `Value` 值复制
3. 按照格式保存到文件：

```json
[
  {
    "name": "__zp_stoken__",
    "value": "你的token值",
    "domain": ".zhipin.com",
    "path": "/",
    "expires": -1,
    "httpOnly": false,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

---

## 方法三：使用浏览器扩展

### Chrome扩展：EditThisCookie

1. 安装 EditThisCookie 扩展
2. 点击扩展图标
3. 点击 "Export" 导出Cookie
4. 保存为 `data/cookies.json`

---

## 验证Cookie是否有效

运行测试脚本：

```python
import json
from playwright.sync_api import sync_playwright

# 加载Cookie
with open('data/cookies.json', 'r') as f:
    cookies = json.load(f)

# 测试
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    context.add_cookies(cookies)

    page = context.new_page()
    page.goto('https://www.zhipin.com/')

    input("检查是否已登录？按回车关闭...")
    browser.close()
```

---

## 常见问题

### Q1: Cookie多久过期？
A: 通常7-30天，过期后需要重新登录

### Q2: Cookie保存在哪里？
A: `data/cookies.json`

### Q3: 如何更新Cookie？
A: 重新运行 `scripts/crawlers/save_cookies_manual.py`

### Q4: Cookie格式错误怎么办？
A: 确保粘贴的是完整的 `document.cookie` 输出

---

## 安全提示

⚠️ **重要**：
- Cookie包含登录信息，不要分享给他人
- 不要提交到Git仓库（已在.gitignore中）
- 定期更换密码会使Cookie失效

---

## 快速开始

1. **登录Boss直聘**
   ```
   访问：https://www.zhipin.com
   完成登录
   ```

2. **获取Cookie**
   ```bash
   # F12 -> Console -> 输入 document.cookie
   # 复制输出
   ```

3. **保存Cookie**
   ```bash
   python scripts/crawlers/save_cookies_manual.py
   # 粘贴Cookie字符串
   ```

4. **开始爬取**
   ```bash
   python scripts/crawlers/run_smart_crawler.py \
     --cities 北京 \
     --keywords Python \
     --total 50
   ```

完成！
