#!/bin/bash
# 服务器更新脚本
# 在服务器上运行此脚本来更新后端代码

set -e

echo "📦 从 Git 拉取最新代码..."

# 暂存生产配置文件
if [ -f docker-compose.prod.yml ]; then
    echo "💾 备份生产配置..."
    cp docker-compose.prod.yml docker-compose.prod.yml.backup
fi

# 拉取最新代码
git pull origin main

# 恢复生产配置
if [ -f docker-compose.prod.yml.backup ]; then
    echo "📝 恢复生产配置..."
    mv docker-compose.prod.yml.backup docker-compose.prod.yml
fi

echo "🔄 重启后端服务..."
# docker-compose -f docker-compose.prod.yml restart backend
# 使用 --build 确保重建镜像
docker-compose -f docker-compose.prod.yml up -d --build backend

echo ""
echo "✅ 更新完成！"
echo ""
docker-compose -f docker-compose.prod.yml ps
