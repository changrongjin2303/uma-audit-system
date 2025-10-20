#!/bin/bash

echo "🛠️  造价材料审计系统 - 清理并启动"
echo "================================="

# 进入项目目录
cd "$(dirname "$0")"

echo "🧹 清理旧的容器和服务..."

# 停止所有Docker服务
docker-compose down 2>/dev/null
docker-compose -f docker-compose.local.yml down 2>/dev/null

# 停止相关容器
docker stop uma_audit_db uma_audit_redis uma_audit_backend 2>/dev/null
docker rm uma_audit_db uma_audit_redis uma_audit_backend 2>/dev/null

echo "✅ 清理完成"

echo "🚀 启动数据库服务..."

# 启动数据库服务
docker-compose -f docker-compose.local.yml up -d

echo "⏳ 等待数据库启动（30秒）..."
sleep 30

# 检查服务状态
echo "📊 服务状态检查："
docker-compose -f docker-compose.local.yml ps

if docker-compose -f docker-compose.local.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 数据库服务启动成功！"
    echo "================================="
    echo "📋 服务信息："
    echo "   • PostgreSQL: localhost:5432"
    echo "   • Redis: localhost:6380"
    echo ""
    echo "💡 下一步：启动API服务"
    echo "   cd backend"
    echo "   python -m pip install -r requirements.txt"
    echo "   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
else
    echo "❌ 服务启动失败"
    docker-compose -f docker-compose.local.yml logs
fi

echo ""
echo "按任意键退出..."
read -n 1