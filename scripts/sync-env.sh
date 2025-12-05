#!/bin/bash
# 同步敏感配置文件到服务器
# 这些文件不在 git 中，需要单独同步

SERVER="root@8.136.59.48"
PROJECT_DIR="/opt/uma-audit-system"

echo "📤 同步配置文件到服务器..."

# 同步后端 .env 文件
if [ -f backend/.env ]; then
    echo "上传 backend/.env..."
    scp backend/.env $SERVER:$PROJECT_DIR/.env
    echo "✅ .env 已同步"
else
    echo "⚠️  backend/.env 不存在，跳过"
fi

echo ""
echo "🎉 配置同步完成！"
echo ""
echo "提示：如果修改了 .env，需要重启服务才能生效："
echo "  ssh $SERVER 'cd $PROJECT_DIR && docker-compose restart backend'"
