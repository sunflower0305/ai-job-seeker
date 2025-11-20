# 职位推荐平台 - 前端

基于 Next.js 14 + TypeScript + Tailwind CSS 构建的现代化职位推荐平台前端应用，提供智能职位推荐、职位搜索、用户管理等完整功能。

## ✨ 功能特性

### 核心功能
- 🏠 **精美首页** - 展示平台核心功能和数据统计
- 💼 **职位列表** - 支持搜索、筛选和分页的职位浏览
- 📋 **职位详情** - 完整的职位信息展示和投递功能
- 🤖 **智能推荐** - 基于AI算法的个性化职位推荐
- ⭐ **职位收藏** - 保存感兴趣的职位
- 👤 **用户中心** - 个人信息管理和投递记录查看

### 用户体验
- 🎨 **现代化UI设计** - 采用 Tailwind CSS，界面美观流畅
- 📱 **响应式布局** - 完美适配桌面端和移动端
- ⚡ **快速加载** - Next.js 14 App Router，性能优异
- 🔍 **智能搜索** - 实时搜索和多维度筛选
- ✨ **流畅动画** - 精心设计的过渡效果和交互反馈

## 🛠 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Next.js | 14.2.0 | React 框架，App Router 架构 |
| React | 18.3.0 | UI 组件库 |
| TypeScript | 5.x | 类型安全 |
| Tailwind CSS | 3.4.0 | 原子化 CSS 框架 |
| ESLint | 8.x | 代码检查 |

## 📁 项目结构

```
frontend/
├── src/
│   ├── app/                      # App Router 页面
│   │   ├── layout.tsx           # 根布局（导航栏+页脚）
│   │   ├── page.tsx             # 首页
│   │   ├── globals.css          # 全局样式
│   │   ├── jobs/                # 职位相关页面
│   │   │   ├── page.tsx        # 职位列表
│   │   │   └── [id]/           # 职位详情（动态路由）
│   │   │       └── page.tsx
│   │   ├── recommendations/     # 智能推荐页面
│   │   │   └── page.tsx
│   │   ├── collections/         # 收藏页面
│   │   │   └── page.tsx
│   │   ├── login/              # 登录页面
│   │   │   └── page.tsx
│   │   ├── register/           # 注册页面
│   │   │   └── page.tsx
│   │   └── profile/            # 个人中心
│   │       └── page.tsx
│   ├── components/              # 可复用组件
│   │   ├── layout/             # 布局组件
│   │   │   ├── Navbar.tsx      # 导航栏
│   │   │   └── Footer.tsx      # 页脚
│   │   └── ui/                 # UI 组件
│   │       ├── JobCard.tsx     # 职位卡片
│   │       ├── LoadingSpinner.tsx  # 加载动画
│   │       └── EmptyState.tsx  # 空状态
│   ├── lib/                    # 工具库
│   │   └── api.ts             # API 请求封装
│   └── types/                  # TypeScript 类型定义
│       └── index.ts           # 通用类型
├── public/                     # 静态资源
├── next.config.js             # Next.js 配置
├── tsconfig.json              # TypeScript 配置
├── tailwind.config.ts         # Tailwind CSS 配置
├── postcss.config.js          # PostCSS 配置
├── .eslintrc.json            # ESLint 配置
└── package.json              # 项目依赖
```

## 🚀 快速开始

### 环境要求

- Node.js 18+
- npm 9+

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用

### 构建生产版本

```bash
npm run build
```

### 启动生产服务器

```bash
npm start
```

### 代码检查

```bash
npm run lint
```

## 🔧 配置说明

### API 代理配置

前端通过 Next.js rewrites 功能代理后端 API，配置位于 `next.config.js`:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ];
}
```

### 环境变量

创建 `.env.local` 文件配置环境变量：

```bash
# 后端 API 地址
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📖 开发指南

### 创建新页面

在 `src/app` 下创建新目录和 `page.tsx`：

```typescript
// src/app/about/page.tsx
export default function AboutPage() {
  return (
    <div className="container mx-auto">
      <h1>关于我们</h1>
    </div>
  );
}
```

### 创建新组件

在 `src/components` 下创建组件：

```typescript
// src/components/ui/Button.tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
}

export default function Button({ label, onClick }: ButtonProps) {
  return (
    <button onClick={onClick} className="btn-primary">
      {label}
    </button>
  );
}
```

### 使用路径别名

项目配置了 `@/*` 指向 `src/*`：

```typescript
import Navbar from '@/components/layout/Navbar';
import { api } from '@/lib/api';
import { Job } from '@/types';
```

### API 调用示例

```typescript
import { api } from '@/lib/api';

// 获取职位列表
const jobs = await api.jobs.list({ location: '北京' });

// 获取职位详情
const job = await api.jobs.get(1);

// 搜索职位
const results = await api.jobs.search('前端工程师');
```

### 自定义样式类

全局 CSS 提供了以下工具类：

```css
/* 按钮 */
.btn-primary      /* 主要按钮 */
.btn-secondary    /* 次要按钮 */

/* 表单 */
.input-field      /* 输入框 */

/* 卡片 */
.card            /* 卡片容器 */

/* 文本截断 */
.line-clamp-1    /* 单行截断 */
.line-clamp-2    /* 两行截断 */
.line-clamp-3    /* 三行截断 */

/* 动画 */
.animate-fade-in  /* 淡入动画 */
```

## 🎨 主要页面

### 1. 首页 (/)
- Hero 区域with搜索功能
- 数据统计展示
- 核心功能介绍
- 使用流程说明

### 2. 职位列表 (/jobs)
- 搜索框和筛选条件
- 职位卡片展示
- 分页功能
- 收藏和投递操作

### 3. 职位详情 (/jobs/[id])
- 完整职位信息
- 公司介绍
- 相似职位推荐
- 投递和收藏功能

### 4. 智能推荐 (/recommendations)
- AI 推荐职位列表
- 推荐理由展示
- 匹配度显示

### 5. 我的收藏 (/collections)
- 收藏职位列表
- 取消收藏功能

### 6. 用户中心 (/profile)
- 基本信息管理
- 简历上传
- 投递记录
- 收藏列表

### 7. 登录/注册 (/login, /register)
- 表单验证
- 错误提示
- 自动跳转

## 🔌 与后端集成

### 后端要求

确保后端 Django 服务运行在 `http://localhost:8000`

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/jobs/jobs/` | GET | 获取职位列表 |
| `/api/jobs/jobs/:id/` | GET | 获取职位详情 |
| `/api/jobs/companies/` | GET | 获取公司列表 |
| `/api/recommendations/users/:id/recommendations/` | GET | 获取推荐职位 |
| `/api/jobs/collections/` | GET/POST | 收藏列表 |
| `/api/jobs/applications/` | GET/POST | 投递记录 |
| `/api/users/login/` | POST | 用户登录 |
| `/api/users/register/` | POST | 用户注册 |

## 🐛 常见问题

### 1. API 请求失败

检查后端服务是否启动：
```bash
# 在项目根目录
python manage.py runserver 8000
```

### 2. 显示示例数据

如果看到"无法连接到服务器，显示示例职位"提示，说明：
- 后端未启动，或
- 数据库中暂无数据

运行爬虫获取真实数据：
```bash
python run_crawler.py
```

### 3. 页面样式异常

清除缓存重新构建：
```bash
rm -rf .next
npm run dev
```

## 📝 待办事项

- [ ] 集成真实用户认证系统
- [ ] 添加职位筛选的更多维度
- [ ] 实现简历在线编辑功能
- [ ] 添加实时消息通知
- [ ] 集成数据可视化图表
- [ ] 添加暗黑模式支持
- [ ] 优化移动端体验
- [ ] 添加单元测试

## 📄 许可证

本项目仅用于学习和研究目的。

## 🙏 致谢

- [Next.js](https://nextjs.org/) - React 框架
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- [TypeScript](https://www.typescriptlang.org/) - 类型系统

---

**开发者**: 职位推荐平台团队
**版本**: 1.0.0
**更新时间**: 2024
