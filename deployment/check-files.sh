#!/bin/bash
# 检查服务器上的文件位置

echo "========================================="
echo "  检查部署文件"
echo "========================================="
echo ""

echo "当前目录: $(pwd)"
echo ""

echo "1. 检查项目目录下的文件："
ls -lh /opt/uma-audit5/*.tar.gz 2>/dev/null || echo "   项目目录下无.tar.gz文件"
echo ""

echo "2. 检查root目录下的文件："
ls -lh /root/*.tar.gz 2>/dev/null || echo "   root目录下无.tar.gz文件"
echo ""

echo "3. 检查所有可能的位置："
find /root /opt/uma-audit5 -name "*.tar.gz" -type f 2>/dev/null
echo ""

echo "4. 检查.env文件："
ls -lh /opt/uma-audit5/.env 2>/dev/null || echo "   .env文件不存在"
echo ""

echo "========================================="
