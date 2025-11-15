#!/bin/bash

echo "🚀 启动造价材料审计系统"
echo "======================================"

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi

echo "✅ Docker运行正常"
echo ""

# 获取脚本所在目录
cd "$(dirname "$0")"

# 清理可能存在的冲突容器
echo "🧹 清理旧容器和网络..."
docker-compose -f docker-compose.dev.yml down 2>/dev/null
docker ps -a | grep uma_audit | awk '{print $1}' | xargs docker rm -f 2>/dev/null
docker network prune -f > /dev/null 2>&1

echo ""
echo "📦 启动后端服务（数据库 + API）..."
docker-compose -f docker-compose.dev.yml up -d --build

echo ""
echo "⏳ 等待后端服务启动（约30秒）..."
sleep 30

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端API启动成功"
else
    echo "⚠️  后端API启动较慢，继续等待..."
    sleep 10
fi

echo ""
echo "🌐 启动前端服务..."
cd frontend
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
echo "前端进程ID: $FRONTEND_PID"

echo ""
echo "⏳ 等待前端服务启动（约10秒）..."
sleep 10

# 检查前端是否启动成功
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 前端服务启动成功"
else
    echo "⚠️  前端服务可能需要更多时间启动"
fi

echo ""
echo "======================================"
echo "🎉 系统启动完成！"
echo ""
echo "📋 访问地址："
echo "   🌐 前端界面：http://localhost:3000"
echo "   📚 API文档：http://localhost:8000/docs"
echo "   ❤️  健康检查：http://localhost:8000/health"
echo ""
echo "👤 登录信息："
echo "   用户名：admin"
echo "   密码：admin123"
echo ""
echo "💡 提示："
echo "   • 使用 ./停止系统.sh 关闭系统"
echo "   • 使用 ./检查状态.sh 查看运行状态"
echo ""

# 打开浏览器（macOS）
if command -v open &> /dev/null; then
    echo "🌐 正在打开浏览器..."
    sleep 2
    open http://localhost:3000 2>/dev/null
fi
