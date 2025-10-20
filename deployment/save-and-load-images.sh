#!/bin/bash
# Docker 镜像离线打包和传输工具
# 用于在无法访问Docker Hub的服务器上部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 项目相关的所有镜像
IMAGES=(
    "python:3.11-slim"
    "postgres:15"
    "redis:7"
    "nginx:alpine"
)

OUTPUT_DIR="./docker-images-offline"
ARCHIVE_NAME="uma-audit-images.tar.gz"

# 模式选择
MODE=$1

show_usage() {
    echo "使用方法:"
    echo "  $0 save    - 保存所有镜像到本地文件"
    echo "  $0 load    - 从本地文件加载所有镜像"
    echo "  $0 build   - 构建项目镜像并保存"
    echo "  $0 check   - 检查镜像状态"
    echo ""
    echo "示例:"
    echo "  # 在有VPN的本地机器上执行"
    echo "  $0 save"
    echo ""
    echo "  # 将生成的 $ARCHIVE_NAME 传输到服务器后执行"
    echo "  $0 load"
}

# 保存镜像
save_images() {
    print_info "开始保存 Docker 镜像到本地文件..."

    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"

    # 拉取所有基础镜像
    print_info "拉取基础镜像..."
    for image in "${IMAGES[@]}"; do
        print_info "拉取: $image"
        if docker pull "$image"; then
            print_info "✓ $image 拉取成功"
        else
            print_error "✗ $image 拉取失败"
            exit 1
        fi
    done

    # 保存镜像到tar文件
    print_info "保存镜像到文件..."
    cd "$OUTPUT_DIR"

    for image in "${IMAGES[@]}"; do
        filename=$(echo "$image" | sed 's/[:/]/_/g')
        print_info "保存: $image -> ${filename}.tar"
        docker save -o "${filename}.tar" "$image"
    done

    # 压缩所有tar文件
    print_info "压缩镜像文件..."
    tar -czf "../$ARCHIVE_NAME" *.tar
    cd ..

    # 显示文件信息
    file_size=$(du -h "$ARCHIVE_NAME" | cut -f1)
    print_info "✓ 镜像打包完成: $ARCHIVE_NAME (大小: $file_size)"
    print_info "请将此文件传输到阿里云服务器，然后运行: $0 load"

    # 清理临时文件
    rm -rf "$OUTPUT_DIR"
}

# 加载镜像
load_images() {
    print_info "开始从文件加载 Docker 镜像..."

    # 检查归档文件是否存在
    if [ ! -f "$ARCHIVE_NAME" ]; then
        print_error "找不到镜像归档文件: $ARCHIVE_NAME"
        print_info "请先在本地运行 '$0 save' 并将生成的文件传输到此服务器"
        exit 1
    fi

    # 解压缩
    print_info "解压缩镜像文件..."
    mkdir -p "$OUTPUT_DIR"
    tar -xzf "$ARCHIVE_NAME" -C "$OUTPUT_DIR"

    # 加载所有镜像
    print_info "加载镜像到 Docker..."
    for tar_file in "$OUTPUT_DIR"/*.tar; do
        if [ -f "$tar_file" ]; then
            print_info "加载: $(basename $tar_file)"
            if docker load -i "$tar_file"; then
                print_info "✓ 加载成功"
            else
                print_error "✗ 加载失败: $tar_file"
            fi
        fi
    done

    # 清理临时文件
    print_info "清理临时文件..."
    rm -rf "$OUTPUT_DIR"

    print_info "✓ 镜像加载完成！"
    print_info "运行 'docker images' 查看已加载的镜像"
}

# 构建项目镜像
build_project_images() {
    print_info "构建项目 Docker 镜像..."

    # 检查docker-compose.yml是否存在
    if [ ! -f "docker-compose.yml" ]; then
        print_error "找不到 docker-compose.yml 文件"
        print_info "请在项目根目录下运行此脚本"
        exit 1
    fi

    # 首先确保基础镜像已经存在
    print_info "检查基础镜像..."
    for image in "${IMAGES[@]}"; do
        if docker image inspect "$image" >/dev/null 2>&1; then
            print_info "✓ $image 已存在"
        else
            print_warn "✗ $image 不存在，尝试拉取..."
            docker pull "$image" || {
                print_error "无法拉取 $image，请先运行 '$0 save' 和 '$0 load'"
                exit 1
            }
        fi
    done

    # 构建项目镜像
    print_info "构建应用镜像..."
    docker-compose build --no-cache

    print_info "✓ 项目镜像构建完成！"

    # 可选：保存构建的镜像
    read -p "是否保存构建的镜像用于传输? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PROJECT_IMAGES=(
            "uma-audit5-backend:latest"
            "uma-audit5-frontend:latest"
        )

        mkdir -p "$OUTPUT_DIR"
        cd "$OUTPUT_DIR"

        for image in "${PROJECT_IMAGES[@]}"; do
            if docker image inspect "$image" >/dev/null 2>&1; then
                filename=$(echo "$image" | sed 's/[:/]/_/g')
                print_info "保存: $image -> ${filename}.tar"
                docker save -o "${filename}.tar" "$image"
            fi
        done

        cd ..
        tar -czf "uma-audit-project-images.tar.gz" -C "$OUTPUT_DIR" .
        rm -rf "$OUTPUT_DIR"

        print_info "✓ 项目镜像已保存到: uma-audit-project-images.tar.gz"
    fi
}

# 检查镜像状态
check_images() {
    print_info "检查 Docker 镜像状态..."
    echo ""

    for image in "${IMAGES[@]}"; do
        if docker image inspect "$image" >/dev/null 2>&1; then
            size=$(docker image inspect "$image" --format='{{.Size}}' | awk '{print int($1/1024/1024) "MB"}')
            print_info "✓ $image (大小: $size)"
        else
            print_warn "✗ $image (未找到)"
        fi
    done

    echo ""
    print_info "所有 Docker 镜像:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
}

# 主逻辑
case "$MODE" in
    save)
        save_images
        ;;
    load)
        load_images
        ;;
    build)
        build_project_images
        ;;
    check)
        check_images
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
