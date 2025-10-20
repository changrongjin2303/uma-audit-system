#!/bin/bash
# 本地预构建所有镜像（包括基础镜像和项目镜像）
# 适合在有VPN的本地环境运行，然后打包传输到服务器

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}===================================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}===================================================${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    print_error "请在项目根目录运行此脚本"
    exit 1
fi

print_step "步骤 1/4: 拉取基础镜像"
BASE_IMAGES=(
    "python:3.11-slim"
    "postgres:15"
    "redis:7"
    "nginx:alpine"
)

for image in "${BASE_IMAGES[@]}"; do
    print_info "拉取: $image"
    if docker pull "$image"; then
        print_info "✓ $image 拉取成功"
    else
        print_error "✗ $image 拉取失败，请检查网络连接或VPN"
        exit 1
    fi
done

print_step "步骤 2/4: 构建项目镜像"

# 构建后端镜像
print_info "构建后端镜像..."
docker build -t uma-audit5-backend:latest -f backend/Dockerfile backend/

# 构建前端镜像（如果有）
if [ -f "frontend/Dockerfile" ]; then
    print_info "构建前端镜像..."
    docker build -t uma-audit5-frontend:latest -f frontend/Dockerfile frontend/
fi

print_step "步骤 3/4: 保存所有镜像"

OUTPUT_DIR="./docker-images-export"
mkdir -p "$OUTPUT_DIR"

# 保存基础镜像
print_info "保存基础镜像..."
for image in "${BASE_IMAGES[@]}"; do
    filename=$(echo "$image" | sed 's/[:/]/_/g')
    print_info "保存: $image"
    docker save -o "$OUTPUT_DIR/${filename}.tar" "$image"
done

# 保存项目镜像
print_info "保存项目镜像..."
docker save -o "$OUTPUT_DIR/uma-audit5-backend.tar" uma-audit5-backend:latest

if docker image inspect uma-audit5-frontend:latest >/dev/null 2>&1; then
    docker save -o "$OUTPUT_DIR/uma-audit5-frontend.tar" uma-audit5-frontend:latest
fi

print_step "步骤 4/4: 压缩打包"

ARCHIVE_NAME="uma-audit5-docker-images-$(date +%Y%m%d).tar.gz"
print_info "创建压缩包: $ARCHIVE_NAME"
tar -czf "$ARCHIVE_NAME" -C "$OUTPUT_DIR" .

# 清理临时文件
rm -rf "$OUTPUT_DIR"

# 显示结果
file_size=$(du -h "$ARCHIVE_NAME" | cut -f1)
print_step "完成！"
echo ""
print_info "✓ 所有镜像已打包完成"
print_info "  文件名: $ARCHIVE_NAME"
print_info "  大小: $file_size"
echo ""
print_info "下一步操作："
print_info "1. 将 $ARCHIVE_NAME 传输到阿里云服务器"
print_info "   scp $ARCHIVE_NAME user@your-server:/path/to/project/"
echo ""
print_info "2. 在服务器上解压并加载镜像"
print_info "   tar -xzf $ARCHIVE_NAME -C docker-images-import"
print_info "   cd docker-images-import"
print_info "   for img in *.tar; do docker load -i \$img; done"
echo ""
print_info "3. 启动项目"
print_info "   docker-compose up -d"
echo ""
