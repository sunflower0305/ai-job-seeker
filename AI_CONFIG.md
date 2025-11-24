# AI 智能职位推荐系统 - 配置指南

## 通义千问 API 配置

本项目已集成通义千问（Qwen）大语言模型，支持智能简历分析和职位推荐功能。

### 1. 获取 API Key

1. 访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)
2. 登录并开通通义千问服务
3. 在控制台获取 API Key

### 2. 配置环境变量

复制 `.env.example` 文件并重命名为 `.env`:

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入你的 API Key:

```env
# 通义千问 API 配置
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

### 3. 安装依赖

```bash
pip install -r requirements_ai.txt
```

### 4. 测试配置

运行测试脚本验证配置是否正确：

```bash
python test_llm_config.py
```

如果看到 "✓ API 调用成功！"，说明配置正确。

### 5. 启动服务

```bash
# 启动后端
python manage.py runserver

# 启动前端（另一个终端）
cd frontend
npm run dev
```

### 6. 使用 AI 推荐功能

1. 访问 http://localhost:3000
2. 点击导航栏中的 "AI推荐"
3. 上传你的简历文档（支持 PDF、Word、TXT）
4. AI 会自动分析简历并推荐合适的职位
5. 你可以与 AI 对话，询问关于职位的任何问题

## 功能特性

### 简历分析
- 自动提取技能、工作年限、学历等信息
- 识别期望职位和薪资
- 总结核心优势和工作经历

### 智能推荐
- 基于简历内容推荐匹配职位
- 使用 Function Call 技术实现精准搜索
- 支持多种搜索条件（技能、薪资、城市等）

### 对话式交互
- 多轮对话，支持深度咨询
- 获取职位详细信息
- 个性化职业建议

## API 端点

### 简历分析
```
POST /api/jobs/resume-analysis/analyze/
Content-Type: multipart/form-data

Body:
- file: 简历文件
```

### 对话接口
```
POST /api/jobs/ai-assistant/chat/
Content-Type: application/json

Body:
{
  "message": "用户消息",
  "session_id": "会话ID（可选）",
  "resume_context": "简历分析结果（可选）"
}
```

### 重置会话
```
POST /api/jobs/ai-assistant/reset/
Content-Type: application/json

Body:
{
  "session_id": "会话ID"
}
```

## 支持的模型

默认使用 `qwen-plus` 模型，你也可以在 `.env` 中修改为其他模型：
- `qwen-turbo`: 更快速，成本更低
- `qwen-plus`: 平衡性能和成本（推荐）
- `qwen-max`: 最强性能

## 故障排查

### API 调用失败
1. 检查 API Key 是否正确
2. 确认账户余额充足
3. 验证网络连接

### 依赖安装失败
```bash
pip install --upgrade pip
pip install -r requirements_ai.txt --no-cache-dir
```

### 环境变量未加载
确保在项目根目录下有 `.env` 文件，并且 Django 设置中已加载 dotenv。

## 技术栈

- **后端**: Django + DRF
- **AI 框架**: LangChain 1.0
- **LLM**: 通义千问 (Qwen)
- **前端**: Next.js + TypeScript + Tailwind CSS
- **文档解析**: PyPDF2, python-docx, pdfplumber

## 注意事项

⚠️ **重要**:
- 不要将 `.env` 文件提交到 Git 仓库
- API Key 应该保密，不要分享给他人
- 生产环境应该使用更安全的密钥管理方案

## 许可证

MIT License
