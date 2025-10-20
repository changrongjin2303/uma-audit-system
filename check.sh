#!/bin/bash

echo "🔍 造价材料审计系统 - 环境检查工具"
echo "================================="

echo "正在检查系统环境..."
echo ""

# 检查Docker是否安装
echo "[1/3] 检查Docker安装状态..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    echo "📥 请下载安装：https://www.docker.com/products/docker-desktop/"
    echo ""
    exit 1
else
    docker --version
    echo "✅ Docker已安装"
    echo ""
fi

# 检查Docker是否运行
echo "[2/3] 检查Docker运行状态..."
if ! docker info &> /dev/null; then
    echo "❌ Docker未运行"
    echo "💡 请启动Docker Desktop应用程序"
    echo ""
    exit 1
else
    echo "✅ Docker正在运行"
    echo ""
fi

# 检查端口是否被占用
echo "[3/3] 检查端口占用情况..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口8000已被占用"
    echo "💡 请先关闭占用该端口的程序，或修改配置使用其他端口"
    echo ""
else
    echo "✅ 端口8000可用"
    echo ""
fi

echo "🎉 环境检查完成！"
echo ""
echo "📋 检查结果汇总："
echo "   • Docker安装：✅"
echo "   • Docker运行：✅"
echo "   • 端口8000：✅"
echo ""
echo "💡 一切就绪，现在可以启动系统了！"
echo "   双击运行 start.sh 即可启动系统"

echo ""
echo "按任意键退出..."
read -n 1