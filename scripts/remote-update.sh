#!/bin/bash
# 远程更新脚本：从本地执行，在服务器上更新代码
# 使用方式：bash scripts/remote-update.sh

SERVER="root@8.136.59.48"
PROJECT_DIR="/opt/uma-audit-system"

set -e

echo "🚀 开始更新服务器代码..."
echo ""

# 在服务器上执行更新
ssh $SERVER << 'ENDSSH'
cd /opt/uma-audit-system

echo "📦 从 Git 拉取最新代码..."

# 暂存生产配置文件（如果存在）
if [ -f docker-compose.prod.yml ]; then
    echo "💾 备份生产配置..."
    cp docker-compose.prod.yml docker-compose.prod.yml.backup
fi

# 拉取最新代码
git pull origin main

# 恢复生产配置（如果存在）
if [ -f docker-compose.prod.yml.backup ]; then
    echo "📝 恢复生产配置..."
    mv docker-compose.prod.yml.backup docker-compose.prod.yml
fi

echo "🔄 重启后端服务..."
docker-compose restart backend

echo ""
echo "✅ 更新完成！"
echo ""
docker-compose ps
ENDSSH

echo ""
echo "🎉 服务器更新成功！"
