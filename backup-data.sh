#!/bin/bash
# 造价审计系统 - 数据备份脚本
# 使用方法: ./backup-data.sh

set -e

echo "======================================"
echo "  数据备份工具"
echo "======================================"
echo ""

# 配置
BACKUP_DIR="/opt/backups/uma-audit"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=30

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "备份时间: $DATE"
echo "备份目录: $BACKUP_DIR"
echo ""

# 1. 备份数据库
echo "步骤 1/3: 备份PostgreSQL数据库..."
echo "----------------------------------------"
docker exec uma_audit_db_prod pg_dump -U postgres uma_audit > $BACKUP_DIR/database_$DATE.sql
if [ $? -eq 0 ]; then
    DB_SIZE=$(du -sh $BACKUP_DIR/database_$DATE.sql | cut -f1)
    echo -e "${GREEN}✓ 数据库备份完成 (大小: $DB_SIZE)${NC}"
else
    echo -e "${RED}✗ 数据库备份失败${NC}"
fi

# 2. 备份上传文件
echo ""
echo "步骤 2/3: 备份上传文件..."
echo "----------------------------------------"
if [ -d "./backend/uploads" ]; then
    tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz ./backend/uploads
    UPLOAD_SIZE=$(du -sh $BACKUP_DIR/uploads_$DATE.tar.gz | cut -f1)
    echo -e "${GREEN}✓ 上传文件备份完成 (大小: $UPLOAD_SIZE)${NC}"
else
    echo -e "${YELLOW}⚠ 上传目录不存在,跳过${NC}"
fi

# 3. 备份配置文件
echo ""
echo "步骤 3/3: 备份配置文件..."
echo "----------------------------------------"
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env.production docker-compose.prod.yml
CONFIG_SIZE=$(du -sh $BACKUP_DIR/config_$DATE.tar.gz | cut -f1)
echo -e "${GREEN}✓ 配置文件备份完成 (大小: $CONFIG_SIZE)${NC}"

# 4. 清理旧备份
echo ""
echo "清理旧备份 (保留${KEEP_DAYS}天)..."
echo "----------------------------------------"
find $BACKUP_DIR -name "*.sql" -mtime +$KEEP_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$KEEP_DAYS -delete
echo -e "${GREEN}✓ 清理完成${NC}"

# 5. 备份列表
echo ""
echo "当前备份列表:"
echo "----------------------------------------"
ls -lh $BACKUP_DIR | tail -10

# 6. 总结
echo ""
echo "======================================"
echo -e "${GREEN}  备份完成! ✓${NC}"
echo "======================================"
echo ""
echo "备份文件:"
echo "  - 数据库: $BACKUP_DIR/database_$DATE.sql"
echo "  - 上传文件: $BACKUP_DIR/uploads_$DATE.tar.gz"
echo "  - 配置文件: $BACKUP_DIR/config_$DATE.tar.gz"
echo ""
echo "恢复数据:"
echo "  docker exec -i uma_audit_db_prod psql -U postgres uma_audit < $BACKUP_DIR/database_$DATE.sql"
echo ""
