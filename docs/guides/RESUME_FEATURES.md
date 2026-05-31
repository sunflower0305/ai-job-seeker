# 简历优化和文档导出功能使用指南

## 📋 功能概览

本系统新增了以下三大核心功能：

1. **🚀 AI 智能简历优化** - 使用 AI 自动优化简历内容
2. **📄 分析报告导出** - 导出 Word 格式的分析报告
3. **💾 简历文档导出** - 导出优化后的简历文档

---

## 🎯 功能详解

### 1. AI 智能简历优化

**功能说明：**
- AI 自动分析并优化简历内容
- 量化工作成果，添加具体数据和指标
- 突出与目标职位相关的技能和经验
- 使用动作动词开头，增强表现力
- 优化内容结构，精简冗余信息

**使用步骤：**
1. 上传简历并完成分析
2. 点击左侧面板的 **"🚀 AI 优化简历"** 按钮
3. 等待 AI 处理（通常需要 10-30 秒）
4. 查看优化建议和修改说明

**优化结果包含：**
- 结构化的简历数据（个人信息、技能、工作经历等）
- 详细的修改说明（每处修改的原因和示例）
- 整体优化总结

**API 端点：**
```
POST /api/jobs/resume-optimize/

请求体：
{
  "resume_text": "原始简历文本",
  "analysis_data": {...简历分析数据...},
  "target_position": "目标职位",
  "optimization_goals": ["优化目标1", "优化目标2"]  // 可选
}

响应：
{
  "success": true,
  "optimized_resume": {...优化后的简历数据...},
  "changes": [...修改说明列表...],
  "optimization_summary": "整体优化说明"
}
```

---

### 2. 分析报告导出

**功能说明：**
- 生成专业的 Word 格式分析报告
- 包含简历分析摘要、技能清单、核心优势等
- 可选包含 AI 对话记录

**报告内容：**
1. 封面（标题、生成时间）
2. 简历分析摘要（基本信息表格）
3. 技能清单
4. 核心优势
5. 工作经历摘要
6. AI 职位推荐（如果有）
7. AI 对话记录（如果有）

**使用步骤：**
1. 完成简历分析后
2. 点击 **"📄 导出分析报告"** 按钮
3. 系统自动下载 `简历分析报告.docx` 文件

**API 端点：**
```
POST /api/jobs/export-report/

请求体：
{
  "analysis_data": {...简历分析数据...},
  "recommendations": "AI推荐内容",  // 可选
  "chat_history": [...]  // 可选
}

响应：
Word 文档文件流（application/vnd.openxmlformats-officedocument.wordprocessingml.document）
```

---

### 3. 简历文档导出

**功能说明：**
- 导出 Word 格式的简历文档
- 支持两种模式：
  - **基础模式**：基于分析数据生成简单格式简历
  - **专业模式**：基于优化后的结构化数据生成专业简历

**支持的简历结构：**
- 个人信息（姓名、联系方式、地址）
- 求职意向（期望职位、期望薪资、工作地点）
- 教育背景
- 专业技能（支持分类或简单列表）
- 工作经历（公司、职位、时间、职责描述）
- 项目经验（项目名称、时间、描述、技术栈、成果）
- 个人评价

**使用步骤：**

**方式一：导出原始简历**
1. 完成简历分析后
2. 点击 **"💾 导出简历文档"** 按钮
3. 系统下载 `简历.docx` 文件

**方式二：导出优化后简历**
1. 先点击 **"🚀 AI 优化简历"** 进行优化
2. 优化完成后，点击 **"✨ 导出优化后简历"** 按钮
3. 系统下载 `优化后的简历.docx` 文件

**API 端点：**
```
POST /api/jobs/export-resume/

请求体：
{
  "resume_data": {...简历数据...},
  "template_style": "modern",  // 或 "classic"，可选
  "format": "word",
  "optimized_content": "优化后的文本"  // 可选
}

响应：
Word 文档文件流
```

---

## 🔧 技术实现

### 后端模块

1. **document_generator.py**
   - `ReportGenerator` - 生成分析报告
   - `ResumeDocumentGenerator` - 生成简历文档

2. **ai_analyzer.py**
   - `ResumeOptimizer` - 简历优化器
   - 使用 LangChain + Qwen LLM

3. **views.py**
   - `optimize_resume()` - 优化简历 API
   - `export_analysis_report()` - 导出报告 API
   - `export_resume_document()` - 导出简历 API
   - `get_improvement_suggestions()` - 获取改进建议 API

### 前端组件

**文件：** `frontend/src/app/ai-recommend/page.tsx`

**新增功能：**
- 优化简历按钮和处理逻辑
- 导出报告按钮和下载逻辑
- 导出简历按钮（支持原始/优化版本）
- 优化结果展示区域

---

## 📊 使用流程图

```
用户上传简历
    ↓
AI 分析简历内容
    ↓
展示分析结果
    ↓
┌─────────────┬─────────────┬─────────────┐
│             │             │             │
│  导出报告   │  优化简历   │  导出简历   │
│   (Word)    │   (AI)      │   (Word)    │
│             │             │             │
└─────────────┴─────────────┴─────────────┘
                    ↓
              优化完成后
                    ↓
          导出优化后的简历
              (Word)
```

---

## 🎨 UI 设计

### 操作按钮布局

```
┌─────────────────────────────┐
│  🚀 AI 优化简历              │ ← 紫粉渐变色
├─────────────────────────────┤
│  📄 导出分析报告             │ ← 蓝色
├─────────────────────────────┤
│  💾 导出简历文档             │ ← 绿色
├─────────────────────────────┤
│  ✨ 导出优化后简历 (条件显示) │ ← 绿蓝渐变色
└─────────────────────────────┘
```

### 优化结果展示

```
┌────────────────────────────┐
│  ✨ 优化建议                │
├────────────────────────────┤
│  整体优化说明...            │
│                            │
│  技能: 添加具体的技能水平... │
│  经验: 量化工作成果...      │
│  项目: 突出技术亮点...      │
└────────────────────────────┘
```

---

## 🚀 使用示例

### 示例 1：完整优化流程

```javascript
// 1. 用户上传简历
// 2. 系统分析并展示结果
// 3. 用户点击优化按钮

const handleOptimizeResume = async () => {
  const response = await fetch('http://localhost:8000/api/jobs/resume-optimize/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_text: resumeText,
      analysis_data: resumeAnalysis,
      target_position: resumeAnalysis.desired_position,
    }),
  })

  const result = await response.json()
  if (result.success) {
    setOptimizationResult(result)
    alert('简历优化完成！')
  }
}
```

### 示例 2：导出分析报告

```javascript
const handleExportReport = async () => {
  const response = await fetch('http://localhost:8000/api/jobs/export-report/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      analysis_data: resumeAnalysis,
      format: 'word',
    }),
  })

  const blob = await response.blob()
  // 下载文件
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '简历分析报告.docx'
  a.click()
}
```

---

## ⚠️ 注意事项

1. **性能考虑**
   - 简历优化需要调用 LLM，响应时间约 10-30 秒
   - 建议添加加载状态提示

2. **数据安全**
   - 当前实现为内存存储，简历数据不持久化
   - 如需保存，建议添加数据库模型

3. **文档格式**
   - 导出的 Word 文档需要 `python-docx` 库
   - 中文显示需要 SimSun 字体支持

4. **错误处理**
   - 优化失败时会返回错误信息
   - 建议添加重试机制

---

## 🔮 未来扩展

### 可选功能（未实现）

1. **简历历史版本管理**
   - 保存多个版本的简历
   - 支持版本对比和回滚

2. **交互式修改建议**
   - 逐条展示修改建议
   - 支持一键应用/拒绝

3. **多种简历模板**
   - 现代简约风
   - 经典商务风
   - 创意设计风

4. **PDF 导出支持**
   - 使用 reportlab 或 weasyprint
   - 支持自定义样式

5. **简历评分功能**
   - AI 评估简历质量
   - 给出分项评分和改进建议

---

## 📚 相关文件

### 后端文件
- `jobs/document_generator.py` - 文档生成器（新建）
- `jobs/ai_analyzer.py` - AI 分析器（新增 ResumeOptimizer）
- `jobs/views.py` - API 视图（新增 4 个端点）
- `jobs/urls.py` - URL 路由配置（新增路由）

### 前端文件
- `frontend/src/app/ai-recommend/page.tsx` - AI 推荐页面（重大更新）
- `frontend/src/components/ui/ResumeUploader.tsx` - 简历上传组件（小改动）

---

## 💡 使用技巧

1. **优化建议：** 先查看优化建议，再决定是否导出
2. **多次优化：** 可以针对不同目标职位多次优化
3. **保存报告：** 导出分析报告保存为参考资料
4. **对比效果：** 导出原始和优化版本进行对比

---

## 📞 问题反馈

如有问题或建议，请联系开发团队或提交 Issue。

---

**版本：** v1.0
**更新时间：** 2025-11-25
**作者：** AI 智能招聘系统开发团队
