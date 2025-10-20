#!/bin/bash
# 阿里云服务器 Docker 镜像加速配置脚本
# 适用于 Ubuntu/Debian/CentOS 系统

set -e

echo "=========================================="
echo "Docker 镜像加速器配置脚本"
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
    echo "检测到操作系统: $OS $VERSION"
else
    echo "无法检测操作系统类型"
    exit 1
fi

# 创建Docker配置目录
mkdir -p /etc/docker

# 备份现有配置
if [ -f /etc/docker/daemon.json ]; then
    echo "备份现有配置到 /etc/docker/daemon.json.backup"
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
fi

# 写入新配置
cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.sjtug.sjtu.edu.cn",
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "insecure-registries": []
}
EOF

echo "✓ Docker配置文件已更新"

# 重启Docker服务
echo "重启 Docker 服务..."
systemctl daemon-reload
systemctl restart docker

# 检查Docker状态
if systemctl is-active --quiet docker; then
    echo "✓ Docker 服务运行正常"
else
    echo "✗ Docker 服务启动失败"
    exit 1
fi

# 验证配置
echo ""
echo "=========================================="
echo "当前镜像加速器配置:"
echo "=========================================="
docker info | grep -A 10 "Registry Mirrors" || echo "无镜像加速器信息"

echo ""
echo "=========================================="
echo "测试镜像拉取 (拉取小型测试镜像)..."
echo "=========================================="
if docker pull hello-world; then
    echo "✓ 镜像拉取测试成功！"
    docker rmi hello-world 2>/dev/null || true
else
    echo "✗ 镜像拉取测试失败，可能需要尝试其他镜像源"
fi

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo "如果仍然无法拉取镜像，请尝试以下操作："
echo "1. 检查服务器网络连接"
echo "2. 尝试使用阿里云个人镜像加速器 (需要登录阿里云控制台获取)"
echo "3. 考虑使用离线镜像传输方案"
echo "=========================================="
