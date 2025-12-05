#!/bin/bash
# 全流程部署脚本：Git同步 -> 本地构建 -> 上传 -> 服务器重启
# 解决阿里云拉取镜像失败的问题，通过本地构建上传的方式更新

SERVER_IP="8.136.59.48"
SERVER_USER="root"
SERVER_PASS="1326598767Qq"
PROJECT_DIR="/opt/uma-audit-system"

set -e

# 检查 sshpass 是否安装
if ! command -v sshpass &> /dev/null; then
    echo "❌ 错误: 未找到 sshpass 工具"
    echo "请先安装 sshpass: brew install sshpass"
    exit 1
fi

echo "========================================"
echo "🚀 开始全流程部署"
echo "========================================"

# 1. Git 同步
echo ""
echo "🔄 [1/5] 同步 Git 代码..."
# 确保忽略 .tar 文件
if ! grep -q "*.tar" .gitignore; then
    echo "*.tar" >> .gitignore
fi

git add .
# 检查是否有变更需要提交
if ! git diff-index --quiet HEAD --; then
    read -p "📝 检测到未提交的更改，请输入提交信息 (默认: 'Update and deploy'): " commit_msg
    commit_msg=${commit_msg:-"Update and deploy"}
    git commit -m "$commit_msg"
    echo "✅ 代码已提交"
else
    echo "✨ 没有需要提交的更改"
fi

echo "⬆️ 推送到远程仓库..."
git push || echo "⚠️ Git 推送失败，可能是网络问题或未配置上游分支，但不影响后续部署"

# 2. 本地构建镜像
echo ""
echo "🏗️  [2/5] 构建 AMD64 架构 Docker 镜像..."
echo "📦 构建后端镜像..."
docker build --platform linux/amd64 -t uma-audit5-backend:latest ./backend
echo "📦 构建前端镜像..."
docker build --platform linux/amd64 -t uma-audit5-frontend:latest ./frontend

# 3. 保存镜像
echo ""
echo "💾 [3/5] 保存镜像为 tar 文件..."
docker save uma-audit5-backend:latest -o uma-audit5-backend-amd64.tar
docker save uma-audit5-frontend:latest -o uma-audit5-frontend-amd64.tar

# 4. 上传文件
echo ""
echo "📤 [4/5] 上传文件到服务器..."
echo "   服务器: $SERVER_USER@$SERVER_IP"
echo "   目录: $PROJECT_DIR"

# 使用 sshpass 自动输入密码进行 scp
export SSHPASS=$SERVER_PASS

echo "   上传后端镜像..."
sshpass -e scp -o StrictHostKeyChecking=no uma-audit5-backend-amd64.tar $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

echo "   上传前端镜像..."
sshpass -e scp -o StrictHostKeyChecking=no uma-audit5-frontend-amd64.tar $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

echo "   上传配置文件 (docker-compose.yml)..."
sshpass -e scp -o StrictHostKeyChecking=no docker-compose.yml $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

echo "   上传环境变量 (.env)..."
if [ -f .env ]; then
    sshpass -e scp -o StrictHostKeyChecking=no .env $SERVER_USER@$SERVER_IP:$PROJECT_DIR/
else
    echo "⚠️ 本地未找到 .env 文件，跳过上传"
fi

# 5. 服务器端操作
echo ""
echo "🔄 [5/5] 在服务器上应用更新..."
sshpass -e ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << ENDSSH
cd /opt/uma-audit-system

echo "📦 加载后端镜像..."
docker load -i uma-audit5-backend-amd64.tar

echo "📦 加载前端镜像..."
docker load -i uma-audit5-frontend-amd64.tar

echo "🚀 重启服务 (强制重新创建容器以应用新镜像)..."
# 使用 --force-recreate 确保使用新加载的镜像重建容器
docker-compose up -d --force-recreate backend frontend

echo "🧹 清理未使用的镜像..."
docker image prune -f

echo "✅ 服务器端操作完成！"
docker-compose ps
ENDSSH

echo ""
echo "🎉🎉🎉 部署全部完成！"
