#!/bin/bash
# 服务器端镜像加载脚本
# 用于在阿里云服务器上加载从本地传输过来的Docker镜像

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

# 检查是否提供了镜像包文件名
ARCHIVE_FILE=""
if [ $# -eq 0 ]; then
    # 自动查找最新的镜像包
    ARCHIVE_FILE=$(ls -t uma-audit5-docker-images-*.tar.gz 2>/dev/null | head -1)
    if [ -z "$ARCHIVE_FILE" ]; then
        print_error "未找到镜像包文件"
        echo "使用方法: $0 [镜像包文件名]"
        echo "或将 uma-audit5-docker-images-*.tar.gz 放在当前目录"
        exit 1
    fi
else
    ARCHIVE_FILE=$1
fi

# 验证文件存在
if [ ! -f "$ARCHIVE_FILE" ]; then
    print_error "文件不存在: $ARCHIVE_FILE"
    exit 1
fi

print_step "阿里云服务器 Docker 镜像加载脚本"
print_info "镜像包文件: $ARCHIVE_FILE"
print_info "文件大小: $(du -h "$ARCHIVE_FILE" | cut -f1)"

# 解压缩
TEMP_DIR="docker-images-temp"
print_step "步骤 1/3: 解压镜像包"
print_info "创建临时目录: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

print_info "解压中..."
if tar -xzf "$ARCHIVE_FILE" -C "$TEMP_DIR"; then
    print_info "✓ 解压完成"
else
    print_error "解压失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 加载镜像
print_step "步骤 2/3: 加载 Docker 镜像"
cd "$TEMP_DIR"

SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_FILES=$(ls -1 *.tar 2>/dev/null | wc -l)

if [ "$TOTAL_FILES" -eq 0 ]; then
    print_error "未找到任何 .tar 镜像文件"
    cd ..
    rm -rf "$TEMP_DIR"
    exit 1
fi

print_info "找到 $TOTAL_FILES 个镜像文件"
echo ""

for tar_file in *.tar; do
    if [ -f "$tar_file" ]; then
        print_info "加载: $tar_file"
        if docker load -i "$tar_file"; then
            print_info "✓ 加载成功"
            ((SUCCESS_COUNT++))
        else
            print_error "✗ 加载失败: $tar_file"
            ((FAIL_COUNT++))
        fi
        echo ""
    fi
done

cd ..

# 清理临时文件
print_step "步骤 3/3: 清理临时文件"
print_info "删除临时目录..."
rm -rf "$TEMP_DIR"

# 显示结果
print_step "加载完成"
echo ""
print_info "成功加载: ${SUCCESS_COUNT}/${TOTAL_FILES} 个镜像"
if [ "$FAIL_COUNT" -gt 0 ]; then
    print_warn "失败: $FAIL_COUNT 个镜像"
fi

echo ""
print_step "已加载的镜像列表"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
print_step "下一步操作"
print_info "1. 进入项目目录"
print_info "   cd /path/to/uma-audit5"
echo ""
print_info "2. 配置环境变量"
print_info "   cp .env.example .env"
print_info "   vim .env  # 修改数据库密码等配置"
echo ""
print_info "3. 启动服务"
print_info "   docker-compose up -d"
echo ""
print_info "4. 查看日志"
print_info "   docker-compose logs -f"
echo ""
