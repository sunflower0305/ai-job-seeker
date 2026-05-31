#!/bin/bash

echo "=========================================="
echo "  停止职位推荐平台"
echo "=========================================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
RUNTIME_DIR="$PROJECT_ROOT/runtime"

# 停止后端
echo "🛑 停止后端服务..."
if [ -f "$RUNTIME_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$RUNTIME_DIR/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "   ✅ 后端已停止 (PID: $BACKEND_PID)"
    else
        echo "   ⚠️  后端进程不存在"
    fi
    rm "$RUNTIME_DIR/backend.pid"
else
    echo "   ⚠️  未找到后端PID文件"
fi

# 停止前端
echo "🛑 停止前端服务..."
if [ -f "$RUNTIME_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$RUNTIME_DIR/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "   ✅ 前端已停止 (PID: $FRONTEND_PID)"
    else
        echo "   ⚠️  前端进程不存在"
    fi
    rm "$RUNTIME_DIR/frontend.pid"
else
    echo "   ⚠️  未找到前端PID文件"
fi

# 备用方案：强制杀死相关进程
echo ""
echo "🔍 清理残留进程..."
pkill -f "manage.py runserver" 2>/dev/null && echo "   ✅ 清理了后端残留进程"
pkill -f "next dev" 2>/dev/null && echo "   ✅ 清理了前端残留进程"

echo ""
echo "=========================================="
echo "  ✅ 停止完成！"
echo "=========================================="
echo ""
