#!/bin/bash

echo "===================================="
echo "    Docker网络问题修复工具"
echo "===================================="
echo

echo "🔍 检查Docker状态..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装或未启动"
    echo "请先启动Docker Desktop"
    exit 1
fi

echo "✅ Docker已安装"

echo "📝 备份当前Docker配置..."
if [ -f ~/.docker/daemon.json ]; then
    cp ~/.docker/daemon.json ~/.docker/daemon.json.backup
    echo "✅ 配置文件已备份"
fi

echo "🇨🇳 配置国内Docker镜像源..."
mkdir -p ~/.docker

cat > ~/.docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://registry.docker-cn.com",
    "https://mirror.baidubce.com"
  ],
  "insecure-registries": [],
  "debug": false,
  "experimental": false
}
EOF

echo "✅ Docker镜像源配置完成"

echo "🔄 重启Docker服务..."
echo "请手动重启Docker Desktop，然后按回车继续..."
read

echo "🧪 测试Docker连接..."
echo "正在拉取测试镜像..."
if docker pull hello-world; then
    echo "✅ Docker网络修复成功！"
    echo "现在可以运行 ./start.sh 启动系统了"
else
    echo "❌ 镜像拉取失败，可能需要配置VPN"
    echo "请继续下一步配置"
fi

echo
echo "===================================="
echo "修复步骤："
echo "1. ✅ 配置国内镜像源"
echo "2. 🔄 需要重启Docker Desktop"
echo "3. 🧪 测试连接"
echo "===================================="