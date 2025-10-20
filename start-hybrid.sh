#!/bin/bash

echo "🚀 造价材料审计系统 - 混合模式启动"
echo "============================================="
echo "📦 后端服务：Docker容器化部署"
echo "💻 前端服务：本地开发模式"
echo "============================================="

# 检查Docker是否安装和运行
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未检测到Docker，请先安装Docker Desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ 错误：Docker未运行，请启动Docker Desktop"
    exit 1
fi

# 检查Node.js环境
if ! command -v npm &> /dev/null; then
    echo "❌ 错误：未检测到Node.js，请先安装Node.js"
    exit 1
fi

echo "✅ 环境检查通过"

# 进入项目目录
cd "$(dirname "$0")"

echo "🔧 启动后端服务（数据库 + API）..."
docker-compose -f docker-compose-backend-only.yml down --remove-orphans 2>/dev/null
docker-compose -f docker-compose-backend-only.yml up -d --build

echo "⏳ 等待后端服务启动..."
sleep 20

# 检查后端健康状态
backend_ok=false
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端API服务正常"
    backend_ok=true
else
    echo "❌ 后端API服务异常"
fi

if [ "$backend_ok" = true ]; then
    echo ""
    echo "🌐 启动前端开发服务器..."
    cd frontend
    
    # 检查是否需要安装依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 安装前端依赖..."
        npm install
    fi
    
    echo ""
    echo "🎉 系统启动成功！"
    echo "============================================="
    echo "📋 访问地址："
    echo "   🌐 前端界面：http://localhost:3000"
    echo "   📚 API文档：http://localhost:8000/api/docs"
    echo "   ❤️  健康检查：http://localhost:8000/health"
    echo ""
    echo "🔧 管理命令："
    echo "   • 查看后端日志：docker-compose -f ../docker-compose-backend-only.yml logs -f"
    echo "   • 停止后端：docker-compose -f ../docker-compose-backend-only.yml down"
    echo "   • 前端热重载：自动启用"
    echo ""
    
    # 自动打开浏览器
    if command -v open &> /dev/null; then
        echo "🌐 正在打开系统界面..."
        sleep 2
        open http://localhost:3000 &
        open http://localhost:8000/api/docs &
    fi
    
    echo "▶️  前端开发服务器启动中..."
    echo "   按 Ctrl+C 停止前端服务"
    echo "============================================="
    
    # 启动前端开发服务器
    npm run dev
else
    echo "❌ 后端启动失败，请检查错误信息："
    docker-compose -f docker-compose-backend-only.yml logs
fi