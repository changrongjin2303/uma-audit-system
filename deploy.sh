#!/bin/bash
# 一键部署脚本：本地提交 + 服务器更新
# 使用方式：
#   bash deploy.sh "提交说明"           # 只更新后端（最快）
#   bash deploy.sh "提交说明" --frontend # 同时更新前端
#   bash deploy.sh --frontend           # 自动提交说明 + 更新前端

set -e

# 服务器配置
SERVER="root@8.136.59.48"
SERVER_PASSWORD="1326598767Qq"
PROJECT_DIR="/opt/uma-audit-system"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 解析参数
UPDATE_FRONTEND=false
COMMIT_MSG=""

for arg in "$@"; do
    if [ "$arg" = "--frontend" ] || [ "$arg" = "-f" ]; then
        UPDATE_FRONTEND=true
    elif [ -z "$COMMIT_MSG" ] && [ "$arg" != "--frontend" ] && [ "$arg" != "-f" ]; then
        COMMIT_MSG="$arg"
    fi
done

echo ""
echo -e "${GREEN}🚀 开始一键部署...${NC}"
if [ "$UPDATE_FRONTEND" = true ]; then
    echo -e "${BLUE}📦 包含前端更新（本地构建 + 同步）${NC}"
fi
echo ""

# ============ 第1步：本地构建前端（如果需要） ============
if [ "$UPDATE_FRONTEND" = true ]; then
    echo -e "${YELLOW}🎨 第1步：本地构建前端...${NC}"
    cd frontend
    npm run build
    cd ..
    echo -e "${GREEN}✅ 前端构建完成${NC}"
    echo ""
fi

# ============ 第2步：本地 Git 提交 ============
if [ "$UPDATE_FRONTEND" = true ]; then
    echo -e "${YELLOW}📝 第2步：检查本地更改...${NC}"
else
    echo -e "${YELLOW}📝 第1步：检查本地更改...${NC}"
fi

# 检查是否有未提交的更改
if git diff --quiet && git diff --staged --quiet; then
    echo "没有需要提交的更改，跳过提交步骤"
else
    # 添加所有更改
    git add -A
    
    # 获取提交说明
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="更新: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    echo "提交说明: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
    
    echo -e "${GREEN}✅ 本地提交完成${NC}"
fi

# ============ 第3步：推送到 GitHub ============
echo ""
if [ "$UPDATE_FRONTEND" = true ]; then
    echo -e "${YELLOW}📤 第3步：推送到 GitHub...${NC}"
else
    echo -e "${YELLOW}📤 第2步：推送到 GitHub...${NC}"
fi
git push origin main
echo -e "${GREEN}✅ 推送完成${NC}"

# ============ 第3.5步：上传前端构建文件（如果需要） ============
if [ "$UPDATE_FRONTEND" = true ]; then
    echo ""
    echo -e "${YELLOW}📤 第3.5步：上传前端构建文件到服务器...${NC}"
    
    # 进入前端目录并压缩dist
    cd frontend
    if [ ! -d "dist" ]; then
        echo -e "${RED}❌ 错误：dist 目录不存在，请先构建前端${NC}"
        exit 1
    fi
    
    echo "压缩 dist 目录..."
    tar -czf dist.tar.gz dist
    
    # 上传到服务器
    echo "上传到服务器..."
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no dist.tar.gz $SERVER:$PROJECT_DIR/frontend/
    
    # 清理本地压缩包
    rm dist.tar.gz
    cd ..
    
    # 在服务器上解压
    echo "在服务器上解压..."
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "cd $PROJECT_DIR/frontend && rm -rf dist && tar -xzf dist.tar.gz && rm dist.tar.gz"
    
    echo -e "${GREEN}✅ 前端文件上传完成${NC}"

    # 上传 Nginx 配置并更新到容器
    echo "更新 Nginx 配置..."
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no frontend/nginx.conf $SERVER:$PROJECT_DIR/frontend/nginx.conf
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "docker cp $PROJECT_DIR/frontend/nginx.conf uma_audit_frontend:/etc/nginx/conf.d/default.conf"
    echo -e "${GREEN}✅ Nginx 配置更新完成${NC}"
fi

# ============ 第4步：服务器拉取代码 ============
echo ""
if [ "$UPDATE_FRONTEND" = true ]; then
    echo -e "${YELLOW}📦 第4步：服务器拉取最新代码...${NC}"
else
    echo -e "${YELLOW}📦 第3步：服务器拉取最新代码...${NC}"
fi

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "cd $PROJECT_DIR && git pull origin main"

echo -e "${GREEN}✅ 代码拉取完成${NC}"

# ============ 第5步：重启后端服务 ============
echo ""
if [ "$UPDATE_FRONTEND" = true ]; then
    echo -e "${YELLOW}🔄 第5步：重启后端服务...${NC}"
else
    echo -e "${YELLOW}🔄 第4步：重启后端服务...${NC}"
fi

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "docker restart uma_audit_backend"

echo -e "${GREEN}✅ 后端重启完成${NC}"

# ============ 第6步：重启前端服务（如果需要） ============
if [ "$UPDATE_FRONTEND" = true ]; then
    echo ""
    echo -e "${YELLOW}🎨 第6步：重启前端服务...${NC}"
    
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "docker restart uma_audit_frontend"
    
    echo -e "${GREEN}✅ 前端重启完成${NC}"
fi

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo -e "${YELLOW}📊 服务状态：${NC}"
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'backend|frontend'"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "访问地址: http://8.136.59.48"
echo ""
