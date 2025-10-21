#!/bin/bash
# 一键部署脚本 - 在阿里云服务器上运行

set -e

echo "========================================="
echo "  造价审计系统 - 最终部署"
echo "========================================="
echo ""

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 进入项目目录
cd /opt/uma-audit5

# 步骤1: 检查文件
echo -e "${YELLOW}[1/5] 检查必要文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: .env 文件不存在！${NC}"
    exit 1
fi
if [ ! -f "uma-audit5-docker-images-20251020.tar.gz" ]; then
    echo -e "${RED}错误: Docker镜像包不存在！${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 文件检查完成${NC}\n"

# 步骤2: 加载Docker镜像
echo -e "${YELLOW}[2/5] 加载Docker镜像（这可能需要1-2分钟，请耐心等待）...${NC}"
if docker images | grep -q "uma-audit5-backend"; then
    echo "镜像已存在，跳过加载"
else
    echo "正在解压并加载镜像包（1.2GB），请稍候..."
    # 忽略Mac文件属性警告，显示加载进度
    docker load -i uma-audit5-docker-images-20251020.tar.gz 2>&1 | grep -v "xattr" || true
    echo "镜像加载处理完成"
fi
echo -e "${GREEN}✓ 镜像加载完成${NC}\n"

# 步骤3: 验证镜像
echo -e "${YELLOW}[3/5] 验证镜像...${NC}"
docker images | grep -E "python|postgres|redis|uma-audit"
echo -e "${GREEN}✓ 镜像验证完成${NC}\n"

# 步骤4: 停止旧服务并启动新服务
echo -e "${YELLOW}[4/5] 启动服务...${NC}"
docker-compose down 2>/dev/null || true
docker-compose up -d
echo -e "${GREEN}✓ 服务启动完成${NC}\n"

# 步骤5: 等待并验证
echo -e "${YELLOW}[5/5] 验证服务健康状态...${NC}"
sleep 15

docker-compose ps

echo -e "\n测试健康检查..."
if curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; then
    echo -e "${GREEN}✓✓✓ 部署成功！服务运行正常！ ✓✓✓${NC}"
else
    echo -e "${YELLOW}⚠️  健康检查未通过，查看日志...${NC}"
    docker-compose logs backend --tail=50
fi

echo ""
echo "========================================="
echo "  部署完成"
echo "========================================="
echo "访问地址: http://8.136.59.48:8000"
echo "健康检查: http://8.136.59.48:8000/api/v1/health"
echo ""
echo "查看日志: docker-compose logs -f backend"
echo "查看状态: docker-compose ps"
echo ""
