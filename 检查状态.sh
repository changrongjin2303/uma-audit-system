#!/bin/bash

echo "📊 系统状态检查"
echo "======================================"

# 检查Docker是否运行
echo "🔍 检查Docker状态..."
if docker info &> /dev/null; then
    echo "   ✅ Docker运行正常"
else
    echo "   ❌ Docker未运行"
    exit 1
fi

echo ""
echo "🔍 检查后端服务（Docker容器）..."
BACKEND_STATUS=$(docker-compose -f docker-compose.dev.yml ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null | grep -v "NAME")

if [ -z "$BACKEND_STATUS" ]; then
    echo "   ❌ 后端服务未运行"
    echo ""
    echo "💡 使用 ./启动系统.sh 启动系统"
    exit 0
fi

echo "$BACKEND_STATUS" | while read line; do
    if echo "$line" | grep -q "Up"; then
        echo "   ✅ $line"
    else
        echo "   ❌ $line"
    fi
done

echo ""
echo "🔍 检查前端服务..."
FRONTEND_PORT=$(lsof -ti:3000 2>/dev/null)
if [ -n "$FRONTEND_PORT" ]; then
    echo "   ✅ 前端服务运行中 (端口3000)"
else
    echo "   ❌ 前端服务未运行"
fi

echo ""
echo "🔍 检查服务可访问性..."

# 检查后端API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "   ✅ 后端API: http://localhost:8000"
    echo "      状态: $(echo $HEALTH | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
    echo "      运行时间: $(echo $HEALTH | grep -o '"uptime_seconds":[^,]*' | cut -d':' -f2) 秒"
else
    echo "   ❌ 后端API无法访问 (http://localhost:8000)"
fi

# 检查前端服务
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ 前端服务: http://localhost:3000"
else
    echo "   ❌ 前端服务无法访问 (http://localhost:3000)"
fi

echo ""
echo "======================================"
echo "📋 快速链接："
echo "   🌐 前端界面：http://localhost:3000"
echo "   📚 API文档：http://localhost:8000/docs"
echo "   ❤️  健康检查：http://localhost:8000/health"
echo ""
echo "👤 登录信息："
echo "   用户名：admin"
echo "   密码：admin123"
echo ""
