#!/bin/bash
# 完整的构建和部署脚本
# 功能：本地构建镜像 -> 上传到服务器 -> 部署
# 注意：构建过程需要联网下载依赖

set -e

SERVER="root@8.136.59.48"
PROJECT_DIR="/opt/uma-audit-system"
SSH_PASS="1326598767Qq"

echo "🚀 开始构建和部署流程..."
echo ""
echo "⚠️  注意：构建过程需要联网下载以下内容："
echo "   - Docker基础镜像（python:3.11-slim, node:18-alpine, nginx:alpine）"
echo "   - Python依赖包（从PyPI下载）"
echo "   - Node.js依赖包（从npm registry下载）"
echo ""

# 步骤1：构建镜像
echo "📦 步骤1：构建Docker镜像..."
echo ""

echo "构建后端镜像..."
docker build --platform linux/amd64 -t uma-audit5-backend:latest ./backend

echo ""
echo "构建前端镜像..."
docker build --platform linux/amd64 -t uma-audit5-frontend:latest ./frontend

echo ""
echo "💾 保存镜像为tar文件..."
docker save uma-audit5-backend:latest -o uma-audit5-backend-amd64.tar
docker save uma-audit5-frontend:latest -o uma-audit5-frontend-amd64.tar

echo ""
echo "✅ 镜像构建完成！"
ls -lh uma-audit5-*-amd64.tar
echo ""

# 步骤2：上传镜像
echo "📤 步骤2：上传镜像到服务器..."
echo ""

if [ -f uma-audit5-backend-amd64.tar ]; then
    echo "上传后端镜像..."
    sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no uma-audit5-backend-amd64.tar $SERVER:$PROJECT_DIR/
else
    echo "❌ 未找到后端镜像文件"
    exit 1
fi

if [ -f uma-audit5-frontend-amd64.tar ]; then
    echo "上传前端镜像..."
    sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no uma-audit5-frontend-amd64.tar $SERVER:$PROJECT_DIR/
else
    echo "❌ 未找到前端镜像文件"
    exit 1
fi

echo ""
echo "✅ 镜像上传完成！"
echo ""

# 步骤3：在服务器上部署
echo "🔄 步骤3：在服务器上加载镜像并重启服务..."
echo ""

sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no $SERVER << ENDSSH
cd $PROJECT_DIR

echo "📦 加载后端镜像..."
docker load -i uma-audit5-backend-amd64.tar

echo "📦 加载前端镜像..."
docker load -i uma-audit5-frontend-amd64.tar

echo "🚀 重启服务..."
docker-compose restart backend frontend

echo ""
echo "✅ 部署完成！"
echo ""
docker-compose ps
ENDSSH

echo ""
echo "🎉 构建和部署成功完成！"
echo ""
echo "💡 提示：如果只需要更新代码，可以只运行："
echo "   bash scripts/update-code-only.sh"
