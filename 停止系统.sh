#!/bin/bash

echo "🛑 停止造价材料审计系统"
echo "======================================"

# 获取脚本所在目录
cd "$(dirname "$0")"

echo "1️⃣  停止前端服务..."
# 查找并停止前端进程
FRONTEND_PIDS=$(lsof -ti:3000 2>/dev/null)
if [ -n "$FRONTEND_PIDS" ]; then
    echo "   找到前端进程: $FRONTEND_PIDS"
    kill $FRONTEND_PIDS 2>/dev/null
    sleep 2
    echo "   ✅ 前端服务已停止"
else
    echo "   ℹ️  前端服务未运行"
fi

echo ""
echo "2️⃣  停止后端服务（数据库 + API）..."
docker-compose -f docker-compose.dev.yml down

echo ""
echo "======================================"
echo "✅ 系统已完全停止"
echo ""
echo "💡 提示："
echo "   • 使用 ./启动系统.sh 重新启动系统"
echo "   • 使用 ./检查状态.sh 查看运行状态"
echo ""
