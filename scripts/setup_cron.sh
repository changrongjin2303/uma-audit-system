#!/bin/bash

# 设置定时任务脚本
echo "🔧 设置造价审计系统定时任务..."

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs/cron"

# 备份现有的crontab
crontab -l > "$PROJECT_DIR/logs/cron/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true

# 生成新的crontab内容
CRON_FILE="/tmp/uma_audit_crontab"

cat > "$CRON_FILE" << EOF
# 造价材料审计系统定时任务
# 每天凌晨2点执行数据库备份
0 2 * * * cd "$PROJECT_DIR" && /usr/bin/python3 scripts/backup_database.py create >> logs/cron/backup.log 2>&1

# 每周日凌晨3点清理过期备份（保留30天，最多10个）
0 3 * * 0 cd "$PROJECT_DIR" && /usr/bin/python3 scripts/backup_database.py cleanup --keep-days 30 --keep-count 10 >> logs/cron/cleanup.log 2>&1

# 每5分钟执行系统监控
*/5 * * * * cd "$PROJECT_DIR" && /usr/bin/python3 scripts/monitor_system.py --once >> logs/cron/monitor.log 2>&1

# 每小时清理应用日志（保留最近100MB）
0 * * * * find "$PROJECT_DIR/backend/logs" -name "*.log" -size +100M -exec truncate -s 50M {} \; >> logs/cron/log_cleanup.log 2>&1

# 每天凌晨4点重启应用（可选，用于内存清理）
# 0 4 * * * cd "$PROJECT_DIR" && ./stop.sh && sleep 30 && ./start.sh >> logs/cron/restart.log 2>&1

EOF

echo "📋 将要设置的定时任务:"
echo "================================"
cat "$CRON_FILE"
echo "================================"

# 询问是否确认设置
read -p "是否确认设置这些定时任务？(y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 安装新的crontab
    crontab "$CRON_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ 定时任务设置成功！"
        echo ""
        echo "📊 当前定时任务列表:"
        crontab -l
        echo ""
        echo "📁 日志文件位置:"
        echo "   备份日志: logs/cron/backup.log"
        echo "   清理日志: logs/cron/cleanup.log" 
        echo "   监控日志: logs/cron/monitor.log"
        echo "   应用重启日志: logs/cron/restart.log"
        echo ""
        echo "🔧 管理命令:"
        echo "   查看定时任务: crontab -l"
        echo "   编辑定时任务: crontab -e"
        echo "   删除所有定时任务: crontab -r"
        echo "   查看cron服务状态: systemctl status cron"
        
        # 创建定时任务管理脚本
        MANAGE_SCRIPT="$SCRIPT_DIR/manage_cron.sh"
        cat > "$MANAGE_SCRIPT" << 'MANAGE_EOF'
#!/bin/bash

case "$1" in
    status)
        echo "📊 定时任务状态:"
        crontab -l
        ;;
    logs)
        echo "📋 最近的定时任务日志:"
        echo ""
        echo "=== 备份日志 ==="
        tail -20 logs/cron/backup.log 2>/dev/null || echo "无备份日志"
        echo ""
        echo "=== 监控日志 ==="
        tail -20 logs/cron/monitor.log 2>/dev/null || echo "无监控日志"
        ;;
    disable)
        echo "🚫 禁用定时任务..."
        crontab -r
        echo "定时任务已禁用"
        ;;
    enable)
        echo "🔄 重新启用定时任务..."
        cd "$(dirname "$0")"/..
        ./scripts/setup_cron.sh
        ;;
    *)
        echo "用法: $0 {status|logs|disable|enable}"
        echo "  status  - 查看定时任务状态"
        echo "  logs    - 查看最近的日志"
        echo "  disable - 禁用所有定时任务"
        echo "  enable  - 重新启用定时任务"
        ;;
esac
MANAGE_EOF

        chmod +x "$MANAGE_SCRIPT"
        echo "   管理脚本: scripts/manage_cron.sh {status|logs|disable|enable}"
        
    else
        echo "❌ 定时任务设置失败！"
        exit 1
    fi
else
    echo "❌ 用户取消了设置"
    exit 1
fi

# 清理临时文件
rm -f "$CRON_FILE"

echo ""
echo "💡 注意事项:"
echo "   1. 确保Python和相关依赖已正确安装"
echo "   2. 确保脚本具有适当的执行权限"
echo "   3. 监控日志文件大小，定期清理"
echo "   4. 备份文件会占用磁盘空间，注意清理策略"
echo ""
echo "🎉 定时任务设置完成！"