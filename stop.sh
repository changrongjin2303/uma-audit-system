#!/bin/bash

echo "🛑 造价材料审计系统 - 停止服务"
echo "================================="

# 进入项目目录
cd "$(dirname "$0")"

echo "🔧 正在停止所有服务..."

# 停止所有服务
docker-compose down

echo "✅ 系统已停止"

echo ""
echo "💡 提示："
echo "   • 重新启动系统：双击 start.sh"
echo "   • 查看服务状态：docker-compose ps"
echo ""

echo "按任意键退出..."
read -n 1