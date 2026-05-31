#!/bin/bash

echo "=========================================="
echo "  启动职位推荐平台"
echo "=========================================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
RUNTIME_DIR="$PROJECT_ROOT/runtime"
mkdir -p "$RUNTIME_DIR"

# 检查后端端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口8000已被占用"
    echo "   运行以下命令停止: pkill -f 'manage.py runserver'"
    exit 1
fi

# 检查前端端口是否被占用
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口3000已被占用"
    echo "   运行以下命令停止: pkill -f 'next dev'"
    exit 1
fi

# 启动后端
echo "🚀 启动后端服务..."
cd "$PROJECT_ROOT"
nohup python3 manage.py runserver > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$RUNTIME_DIR/backend.pid"
echo "   ✅ 后端已启动 (PID: $BACKEND_PID)"
echo "   📍 地址: http://localhost:8000"
echo ""

# 等待后端启动
sleep 2

# 启动前端
echo "🚀 启动前端服务..."
cd "$PROJECT_ROOT/frontend"
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$RUNTIME_DIR/frontend.pid"
echo "   ✅ 前端已启动 (PID: $FRONTEND_PID)"
echo "   📍 地址: http://localhost:3000"
echo ""

# 等待前端启动
sleep 3

echo "=========================================="
echo "  ✅ 启动完成！"
echo "=========================================="
echo ""
echo "📱 应用访问地址:"
echo "   • 首页:       http://localhost:3000"
echo "   • 数据分析:   http://localhost:3000/analytics"
echo "   • 职位列表:   http://localhost:3000/jobs"
echo "   • API接口:    http://localhost:8000/api/"
echo ""
echo "📊 查看日志:"
echo "   • 后端日志:   tail -f backend.log"
echo "   • 前端日志:   tail -f frontend/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   运行: ./stop.sh"
echo "   或者: pkill -f 'manage.py runserver' && pkill -f 'next dev'"
echo ""
echo "=========================================="
