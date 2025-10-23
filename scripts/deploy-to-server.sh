#!/bin/bash
# 部署脚本：上传镜像到服务器并重启服务
# 在本地运行此脚本来部署到生产服务器

SERVER="root@8.136.59.48"
PROJECT_DIR="/opt/uma-audit-system"

set -e

echo "📤 上传镜像到服务器..."
echo ""

if [ -f uma-audit5-backend-amd64.tar ]; then
    echo "上传后端镜像..."
    scp uma-audit5-backend-amd64.tar $SERVER:$PROJECT_DIR/
else
    echo "❌ 未找到后端镜像文件，请先运行 ./scripts/build-images.sh"
    exit 1
fi

if [ -f uma-audit5-frontend-amd64.tar ]; then
    echo "上传前端镜像..."
    scp uma-audit5-frontend-amd64.tar $SERVER:$PROJECT_DIR/
else
    echo "❌ 未找到前端镜像文件，请先运行 ./scripts/build-images.sh"
    exit 1
fi

echo ""
echo "🔄 在服务器上加载镜像并重启服务..."
ssh $SERVER << 'ENDSSH'
cd /opt/uma-audit-system

echo "📦 加载后端镜像..."
docker load -i uma-audit5-backend-amd64.tar

echo "📦 加载前端镜像..."
docker load -i uma-audit5-frontend-amd64.tar

echo "🚀 重启服务..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "✅ 部署完成！"
echo ""
docker-compose -f docker-compose.prod.yml ps
ENDSSH

echo ""
echo "🎉 部署成功！"
