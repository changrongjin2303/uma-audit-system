#!/bin/bash

echo "🚀 造价材料审计系统 - 完整系统启动脚本"
echo "============================================="

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

echo "🔧 正在构建和启动完整系统..."
echo "   • 数据库服务 (PostgreSQL + Redis)"
echo "   • 后端API服务 (FastAPI)"  
echo "   • 前端Web服务 (Vue.js + Nginx)"

# 清理之前的容器和镜像
echo "🧹 清理旧容器..."
docker-compose down --remove-orphans 2>/dev/null

# 构建并启动所有服务
docker-compose up -d --build

echo "⏳ 等待所有服务启动（大约60-90秒）..."

# 分阶段检查服务启动
echo "🔍 检查数据库服务..."
sleep 15

echo "🔍 检查后端API服务..."
sleep 20

echo "🔍 检查前端Web服务..."  
sleep 25

# 检查服务状态
echo "📊 检查服务健康状态..."
services_status=$(docker-compose ps --format "table {{.Name}}\t{{.Status}}")
echo "$services_status"

# 检查关键端口是否可访问
check_service() {
    local url=$1
    local name=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name 服务正常"
        return 0
    else
        echo "❌ $name 服务异常"
        return 1
    fi
}

echo ""
echo "🔗 检查服务可访问性..."
backend_ok=false
frontend_ok=false

if check_service "http://localhost:8000/health" "后端API"; then
    backend_ok=true
fi

if check_service "http://localhost:3000" "前端Web"; then
    frontend_ok=true
fi

# 显示启动结果
echo ""
echo "============================================="
if $backend_ok && $frontend_ok; then
    echo "🎉 完整系统启动成功！"
    echo ""
    echo "📋 访问地址："
    echo "   🌐 前端界面：http://localhost:3000"
    echo "   📚 API文档：http://localhost:8000/docs"
    echo "   ❤️  健康检查：http://localhost:8000/health"
    echo "   🔧 API根地址：http://localhost:8000/api/v1/"
    echo ""
    echo "🔧 管理命令："
    echo "   • 查看日志：docker-compose logs -f [service_name]"
    echo "   • 停止系统：docker-compose down"
    echo "   • 重启系统：docker-compose restart"
    echo "   • 查看状态：docker-compose ps"
    echo ""
    
    # 自动打开浏览器
    echo "🌐 正在打开系统界面..."
    if command -v open &> /dev/null; then
        sleep 2
        open http://localhost:3000
        sleep 1  
        open http://localhost:8000/docs
    elif command -v xdg-open &> /dev/null; then
        sleep 2
        xdg-open http://localhost:3000
        sleep 1
        xdg-open http://localhost:8000/docs
    else
        echo "💡 请手动在浏览器打开："
        echo "   前端界面：http://localhost:3000"
        echo "   API文档：http://localhost:8000/api/docs"
    fi
    
elif $backend_ok; then
    echo "⚠️  后端启动成功，前端启动异常"
    echo "   可访问API文档：http://localhost:8000/api/docs"
    echo "   前端服务异常，请检查日志：docker-compose logs frontend"
else
    echo "❌ 系统启动异常，请检查错误信息："
    echo ""
    docker-compose logs --tail=20
    echo ""
    echo "🔧 故障排除建议："
    echo "   1. 检查端口占用：lsof -i :3000,8000,5432,6379"
    echo "   2. 查看详细日志：docker-compose logs -f"
    echo "   3. 重新构建：docker-compose up -d --build --force-recreate"
fi

echo ""
echo "📖 详细使用说明请参考项目文档"
echo "============================================="
echo ""
