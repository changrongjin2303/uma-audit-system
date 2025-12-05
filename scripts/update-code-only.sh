#!/bin/bash
# 仅更新代码（不重新构建镜像）
# 适用于：代码更新但不需要重新构建镜像的情况
# 注意：这种方式需要容器内代码是通过volume挂载的，否则无效

set -e

SERVER="root@8.136.59.48"
PROJECT_DIR="/opt/uma-audit-system"
SSH_PASS="1326598767Qq"

echo "📦 仅更新代码（不重新构建镜像）..."
echo "⚠️  注意：如果代码是打包在镜像内的，此方法无效，需要使用 build-and-deploy.sh"
echo ""

sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no $SERVER << ENDSSH
cd $PROJECT_DIR

echo "📥 从Git拉取最新代码..."
git pull origin main

echo "🔄 重启服务..."
docker-compose restart backend frontend

echo ""
echo "✅ 代码更新完成！"
echo ""
docker-compose ps
ENDSSH

echo ""
echo "🎉 更新完成！"
