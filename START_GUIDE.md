# 职位推荐平台 - 启动指南

## 系统要求

- Python 3.10+
- Node.js 18+
- npm 9+

当前环境：
- Python: 3.10.12 ✅
- Node.js: v22.17.1 ✅
- npm: 10.9.2 ✅

---

## 快速启动

### 方式一：使用两个终端窗口（推荐）

#### 终端1 - 启动后端
```bash
# 进入项目根目录
cd /home/leyang/workplace/bishe

# 启动Django后端服务器
python3 manage.py runserver
```

后端将运行在：`http://localhost:8000`

#### 终端2 - 启动前端
```bash
# 进入前端目录
cd /home/leyang/workplace/bishe/frontend

# 启动Next.js开发服务器
npm run dev
```

前端将运行在：`http://localhost:3000`

---

### 方式二：使用后台运行

#### 1. 后台启动后端
```bash
cd /home/leyang/workplace/bishe
nohup python3 manage.py runserver > backend.log 2>&1 &
echo $! > backend.pid
```

#### 2. 后台启动前端
```bash
cd /home/leyang/workplace/bishe/frontend
nohup npm run dev > frontend.log 2>&1 &
echo $! > frontend.pid
```

#### 3. 查看进程
```bash
# 查看后端进程
ps aux | grep "manage.py runserver"

# 查看前端进程
ps aux | grep "next dev"
```

#### 4. 停止服务
```bash
# 停止后端
kill $(cat /home/leyang/workplace/bishe/backend.pid)

# 停止前端
kill $(cat /home/leyang/workplace/bishe/frontend/frontend.pid)

# 或者直接使用pkill
pkill -f "manage.py runserver"
pkill -f "next dev"
```

---

## 首次安装（如果需要）

### 后端依赖安装

```bash
cd /home/leyang/workplace/bishe

# 安装Python依赖
pip3 install -r requirements.txt

# 数据库迁移（如果需要）
python3 manage.py migrate

# 创建超级用户（可选）
python3 manage.py createsuperuser
```

### 前端依赖安装

```bash
cd /home/leyang/workplace/bishe/frontend

# 安装Node.js依赖
npm install
```

---

## 访问应用

启动成功后，在浏览器中访问：

### 前端应用
- **首页**: http://localhost:3000
- **数据分析页面**: http://localhost:3000/analytics
- **职位列表**: http://localhost:3000/jobs
- **职位详情**: http://localhost:3000/jobs/[id]

### 后端API
- **API根路径**: http://localhost:8000/api/
- **职位列表API**: http://localhost:8000/api/jobs/jobs/
- **统计数据API**: http://localhost:8000/api/jobs/jobs/statistics/
- **Django管理后台**: http://localhost:8000/admin/

---

## 验证启动

### 1. 验证后端
```bash
# 测试后端API是否正常
curl http://localhost:8000/api/jobs/jobs/statistics/
```

应该返回JSON格式的统计数据。

### 2. 验证前端
在浏览器中访问：http://localhost:3000

应该看到职位推荐平台的首页。

### 3. 验证数据分析页面
在浏览器中访问：http://localhost:3000/analytics

应该看到包含11个图表的数据分析页面。

---

## 常见问题

### 端口被占用

**问题**: `Error: bind: Address already in use`

**解决方案**:

```bash
# 查找占用端口的进程
# 后端端口8000
lsof -i :8000

# 前端端口3000
lsof -i :3000

# 杀死占用端口的进程
kill -9 <PID>

# 或者使用不同端口启动
# 后端
python3 manage.py runserver 8001

# 前端（修改package.json中的dev脚本）
npm run dev -- -p 3001
```

### 前端API代理配置

前端已配置API代理，所有 `/api/*` 请求会自动转发到后端 `http://localhost:8000`。

配置文件：`frontend/next.config.js`

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

### CORS问题

后端已配置CORS允许前端访问。

配置文件：`job_platform/settings.py`

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
```

---

## 开发模式特性

### 后端热重载
Django开发服务器支持代码热重载，修改Python文件后会自动重启。

### 前端热更新
Next.js支持快速刷新（Fast Refresh），修改React组件后会立即在浏览器中更新。

---

## 生产环境部署（参考）

### 后端
```bash
# 收集静态文件
python3 manage.py collectstatic

# 使用Gunicorn运行
gunicorn job_platform.wsgi:application --bind 0.0.0.0:8000
```

### 前端
```bash
# 构建生产版本
npm run build

# 启动生产服务器
npm run start
```

---

## 日志查看

### 后台运行日志
```bash
# 后端日志
tail -f /home/leyang/workplace/bishe/backend.log

# 前端日志
tail -f /home/leyang/workplace/bishe/frontend/frontend.log
```

### 实时查看
如果使用方式一（终端窗口），日志会直接显示在终端中。

---

## 停止服务

### 前台运行
在运行服务的终端窗口按 `Ctrl + C`

### 后台运行
```bash
# 停止所有相关进程
pkill -f "manage.py runserver"
pkill -f "next dev"
```

---

## 测试数据

如果数据库为空，可以运行以下脚本生成测试数据：

```bash
cd /home/leyang/workplace/bishe

# 生成模拟数据
python3 generate_mock_data.py

# 或导入真实数据
python3 import_jobs_data.py
```

---

## 一键启动脚本（可选）

创建启动脚本方便使用：

### start.sh
```bash
#!/bin/bash

echo "启动职位推荐平台..."

# 启动后端
cd /home/leyang/workplace/bishe
nohup python3 manage.py runserver > backend.log 2>&1 &
echo $! > backend.pid
echo "后端启动在 http://localhost:8000"

# 启动前端
cd /home/leyang/workplace/bishe/frontend
nohup npm run dev > frontend.log 2>&1 &
echo $! > frontend.pid
echo "前端启动在 http://localhost:3000"

echo "启动完成！"
echo "访问 http://localhost:3000 查看应用"
echo "访问 http://localhost:3000/analytics 查看数据分析"
```

### stop.sh
```bash
#!/bin/bash

echo "停止职位推荐平台..."

# 停止后端
if [ -f /home/leyang/workplace/bishe/backend.pid ]; then
    kill $(cat /home/leyang/workplace/bishe/backend.pid)
    rm /home/leyang/workplace/bishe/backend.pid
    echo "后端已停止"
fi

# 停止前端
if [ -f /home/leyang/workplace/bishe/frontend/frontend.pid ]; then
    kill $(cat /home/leyang/workplace/bishe/frontend/frontend.pid)
    rm /home/leyang/workplace/bishe/frontend/frontend.pid
    echo "前端已停止"
fi

# 备用方案
pkill -f "manage.py runserver"
pkill -f "next dev"

echo "停止完成！"
```

使用方法：
```bash
# 赋予执行权限
chmod +x start.sh stop.sh

# 启动
./start.sh

# 停止
./stop.sh
```

---

## 快速命令参考

```bash
# 启动后端
cd /home/leyang/workplace/bishe && python3 manage.py runserver

# 启动前端
cd /home/leyang/workplace/bishe/frontend && npm run dev

# 查看后端日志
tail -f /home/leyang/workplace/bishe/backend.log

# 查看前端日志
tail -f /home/leyang/workplace/bishe/frontend/frontend.log

# 停止所有服务
pkill -f "manage.py runserver" && pkill -f "next dev"
```

---

祝你使用愉快！如有问题，请查看日志文件或联系开发者。
