#!/bin/bash

echo "🚀 造价材料审计系统 - 离线启动脚本"
echo "================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未检测到Docker，请先安装Docker Desktop"
    echo "📥 下载地址：https://www.docker.com/products/docker-desktop/"
    read -p "按任意键退出..."
    exit 1
fi

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误：Docker未运行，请启动Docker Desktop"
    read -p "按任意键退出..."
    exit 1
fi

echo "✅ Docker环境检查通过"

# 进入项目目录
cd "$(dirname "$0")"

echo "🔧 正在启动数据库服务..."

# 仅启动数据库服务
docker-compose -f docker-compose.local.yml up -d

echo "⏳ 等待数据库启动（大约20秒）..."
sleep 20

# 检查服务状态
if docker-compose -f docker-compose.local.yml ps | grep -q "Up"; then
    echo ""
    echo "✅ 数据库服务启动成功！"
    echo "================================="
    echo "📋 服务状态："
    echo "   • PostgreSQL: 运行在 localhost:5432"
    echo "   • Redis: 运行在 localhost:6379"
    echo ""
    echo "💡 下一步："
    echo "   现在可以本地启动Python服务了"
    echo "   cd backend && python -m uvicorn main:app --reload"
    echo ""
else
    echo "❌ 服务启动失败，请检查错误信息："
    docker-compose -f docker-compose.local.yml logs
fi

echo ""
echo "按任意键退出..."
read -n 1