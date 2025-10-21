#!/bin/bash
# 阿里云服务器快速部署脚本
# 用途：在服务器上一键完成环境配置和服务启动

set -e  # 遇到错误立即退出

echo "========================================="
echo "  造价材料审计系统 - 服务器快速部署"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="/opt/uma-audit5"

# 步骤1: 检查项目目录
echo -e "${YELLOW}[1/8] 检查项目目录...${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误: 项目目录 $PROJECT_DIR 不存在${NC}"
    echo "请先执行: git clone <仓库地址> $PROJECT_DIR"
    exit 1
fi
cd "$PROJECT_DIR"
echo -e "${GREEN}✓ 项目目录存在${NC}"
echo ""

# 步骤2: 检查Docker镜像包
echo -e "${YELLOW}[2/8] 检查Docker镜像包...${NC}"
IMAGE_FILE=$(ls uma-audit5-docker-images-*.tar.gz 2>/dev/null | head -1)
if [ -z "$IMAGE_FILE" ]; then
    echo -e "${RED}错误: 未找到Docker镜像包${NC}"
    echo "请先上传 uma-audit5-docker-images-*.tar.gz 到项目目录"
    exit 1
fi
echo -e "${GREEN}✓ 找到镜像包: $IMAGE_FILE${NC}"
echo ""

# 步骤3: 加载Docker镜像
echo -e "${YELLOW}[3/8] 加载Docker镜像...${NC}"
if [ -f "deployment/server-load-images.sh" ]; then
    bash deployment/server-load-images.sh "$IMAGE_FILE"
else
    echo "直接加载镜像..."
    docker load -i "$IMAGE_FILE"
fi
echo -e "${GREEN}✓ Docker镜像加载完成${NC}"
echo ""

# 步骤4: 验证镜像
echo -e "${YELLOW}[4/8] 验证Docker镜像...${NC}"
docker images | grep -E "python|postgres|redis|nginx|uma-audit"
echo -e "${GREEN}✓ 镜像验证完成${NC}"
echo ""

# 步骤5: 配置环境变量
echo -e "${YELLOW}[5/8] 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    if [ -f "deployment/.env.server" ]; then
        echo "从模板创建 .env 文件..."
        cp deployment/.env.server .env
        echo -e "${YELLOW}⚠️  请立即编辑 .env 文件,修改以下配置:${NC}"
        echo "   - YOUR_DB_PASSWORD (数据库密码)"
        echo "   - YOUR_REDIS_PASSWORD (Redis密码)"
        echo "   - YOUR_SECRET_KEY (JWT密钥)"
        echo "   - YOUR_SERVER_IP (服务器IP)"
        echo ""
        echo -e "${YELLOW}生成密钥命令:${NC}"
        echo "   SECRET_KEY: openssl rand -hex 32"
        echo "   密码: openssl rand -base64 32"
        echo ""
        read -p "按回车键继续编辑 .env 文件..." dummy
        ${EDITOR:-vim} .env
    else
        echo -e "${RED}错误: 未找到 .env 模板文件${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
    read -p "是否要重新编辑 .env 文件? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-vim} .env
    fi
fi
echo ""

# 步骤6: 检查必要配置
echo -e "${YELLOW}[6/8] 检查环境配置...${NC}"
if grep -q "YOUR_DB_PASSWORD" .env || grep -q "YOUR_SERVER_IP" .env; then
    echo -e "${RED}⚠️  警告: .env 文件中仍有占位符未替换${NC}"
    echo "请确认是否已正确配置所有参数"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo -e "${GREEN}✓ 环境配置检查完成${NC}"
echo ""

# 步骤7: 启动服务
echo -e "${YELLOW}[7/8] 启动Docker服务...${NC}"
docker-compose down 2>/dev/null || true  # 停止旧服务
docker-compose up -d
echo -e "${GREEN}✓ 服务启动完成${NC}"
echo ""

# 步骤8: 等待服务就绪并验证
echo -e "${YELLOW}[8/8] 等待服务就绪...${NC}"
sleep 10

# 检查容器状态
echo "检查容器状态..."
docker-compose ps

# 测试健康检查
echo ""
echo "测试服务健康状态..."
if curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; then
    echo -e "${GREEN}✓✓✓ 部署成功! 服务运行正常 ✓✓✓${NC}"
else
    echo -e "${YELLOW}⚠️  健康检查未通过,请查看日志${NC}"
    echo "查看日志命令: docker-compose logs -f backend"
fi

echo ""
echo "========================================="
echo "  🎉 部署完成!"
echo "========================================="
echo ""
echo "📋 后续操作:"
echo "  1. 查看服务状态: docker-compose ps"
echo "  2. 查看日志: docker-compose logs -f"
echo "  3. 测试API: curl http://localhost:8000/api/v1/health"
echo "  4. 访问系统: http://YOUR_SERVER_IP:8000"
echo ""
echo "🔧 常用命令:"
echo "  - 重启服务: docker-compose restart"
echo "  - 停止服务: docker-compose down"
echo "  - 查看后端日志: docker-compose logs -f backend"
echo "  - 进入容器: docker-compose exec backend bash"
echo ""
