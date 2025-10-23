#!/bin/bash
# 本地构建 AMD64 架构的 Docker 镜像
# 在 Mac 上运行此脚本来构建适用于服务器的镜像

set -e

echo "🏗️  开始构建 AMD64 架构的 Docker 镜像..."
echo ""

echo "📦 构建后端镜像..."
docker build --platform linux/amd64 -t uma-audit5-backend:latest ./backend

echo ""
echo "📦 构建前端镜像..."
docker build --platform linux/amd64 -t uma-audit5-frontend:latest ./frontend

echo ""
echo "💾 保存镜像为 tar 文件..."
docker save uma-audit5-backend:latest -o uma-audit5-backend-amd64.tar
docker save uma-audit5-frontend:latest -o uma-audit5-frontend-amd64.tar

echo ""
echo "✅ 镜像构建完成！"
echo ""
ls -lh uma-audit5-*-amd64.tar
