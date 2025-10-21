#!/bin/bash
# 镜像包上传脚本
# 用于将本地镜像包传输到阿里云服务器

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 服务器配置
SERVER_IP="8.136.59.48"
SERVER_USER="root"
REMOTE_PATH="/root/"

# 查找最新的镜像包
IMAGE_FILE=$(ls -t uma-audit5-docker-images-*.tar.gz 2>/dev/null | head -1)

if [ -z "$IMAGE_FILE" ]; then
    print_error "未找到镜像包文件"
    echo "请先运行: ./deployment/prebuild-images.sh"
    exit 1
fi

print_info "=========================================="
print_info "  镜像包上传到阿里云服务器"
print_info "=========================================="
echo ""
print_info "服务器信息:"
print_info "  IP地址: ${SERVER_IP}"
print_info "  用户名: ${SERVER_USER}"
print_info "  目标路径: ${REMOTE_PATH}"
echo ""
print_info "镜像包信息:"
print_info "  文件名: ${IMAGE_FILE}"
print_info "  大小: $(du -h "$IMAGE_FILE" | cut -f1)"
print_info "  MD5: $(md5 "$IMAGE_FILE" | awk '{print $4}')"
echo ""

# 提示用户确认
read -p "确认开始上传? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warn "取消上传"
    exit 0
fi

print_info "开始上传（需要输入服务器密码）..."
echo ""

# 使用 SCP 上传
if scp -v "$IMAGE_FILE" ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}; then
    echo ""
    print_info "=========================================="
    print_info "✓ 上传完成！"
    print_info "=========================================="
    echo ""
    print_info "下一步操作："
    print_info "1. SSH 登录服务器："
    echo "   ssh ${SERVER_USER}@${SERVER_IP}"
    echo ""
    print_info "2. 验证文件已上传："
    echo "   ls -lh /root/${IMAGE_FILE}"
    echo "   md5sum /root/${IMAGE_FILE}"
    echo ""
    print_info "3. 克隆或更新代码："
    echo "   git clone git@github.com:changrongjin2303/uma-audit-system.git /opt/uma-audit5"
    echo "   # 或如果已存在："
    echo "   cd /opt/uma-audit5 && git pull origin main"
    echo ""
    print_info "4. 加载镜像并部署："
    echo "   cd /opt/uma-audit5"
    echo "   bash deployment/server-load-images.sh /root/${IMAGE_FILE}"
    echo ""
else
    echo ""
    print_error "上传失败！"
    echo ""
    print_info "可能的原因："
    print_info "1. SSH 密码错误"
    print_info "2. 服务器防火墙限制"
    print_info "3. 网络连接问题"
    echo ""
    print_info "替代方案："
    print_info "1. 使用阿里云 OSS 传输（推荐）"
    print_info "2. 手动从阿里云控制台上传"
    print_info "3. 使用其他云存储中转"
    exit 1
fi
