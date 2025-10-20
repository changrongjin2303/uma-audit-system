#!/bin/bash
# 造价审计系统 - 健康检查脚本
# 使用方法: ./health-check.sh

echo "======================================"
echo "  系统健康检查"
echo "======================================"
echo ""

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 计数器
PASS=0
FAIL=0
WARN=0

# 检查函数
check_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗ $1${NC}"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARN++))
}

# 1. 检查Docker服务
echo "检查 1/8: Docker服务"
echo "----------------------------------------"
if systemctl is-active --quiet docker; then
    check_pass "Docker服务运行正常"
else
    check_fail "Docker服务未运行"
fi

# 2. 检查容器状态
echo ""
echo "检查 2/8: 容器运行状态"
echo "----------------------------------------"

containers=("uma_audit_db_prod" "uma_audit_redis_prod" "uma_audit_backend_prod" "uma_audit_frontend_prod")
for container in "${containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        status=$(docker inspect --format='{{.State.Status}}' $container)
        if [ "$status" = "running" ]; then
            check_pass "$container: 运行中"
        else
            check_fail "$container: 状态异常 ($status)"
        fi
    else
        check_fail "$container: 未运行"
    fi
done

# 3. 检查端口监听
echo ""
echo "检查 3/8: 端口监听"
echo "----------------------------------------"

ports=("80:前端" "443:HTTPS" "8000:后端API" "5432:PostgreSQL" "6379:Redis")
for port_info in "${ports[@]}"; do
    port="${port_info%%:*}"
    name="${port_info##*:}"
    if netstat -tuln 2>/dev/null | grep -q ":${port} " || ss -tuln 2>/dev/null | grep -q ":${port} "; then
        check_pass "端口 $port ($name) 正在监听"
    else
        if [ "$port" = "443" ]; then
            check_warn "端口 $port ($name) 未监听 (HTTPS未配置)"
        else
            check_fail "端口 $port ($name) 未监听"
        fi
    fi
done

# 4. 检查数据库连接
echo ""
echo "检查 4/8: 数据库连接"
echo "----------------------------------------"
if docker exec uma_audit_db_prod pg_isready -U postgres &>/dev/null; then
    check_pass "PostgreSQL数据库连接正常"

    # 检查数据库大小
    db_size=$(docker exec uma_audit_db_prod psql -U postgres -d uma_audit -t -c "SELECT pg_size_pretty(pg_database_size('uma_audit'));" 2>/dev/null | xargs)
    if [ -n "$db_size" ]; then
        echo "  数据库大小: $db_size"
    fi
else
    check_fail "PostgreSQL数据库连接失败"
fi

# 5. 检查Redis连接
echo ""
echo "检查 5/8: Redis缓存"
echo "----------------------------------------"
if docker exec uma_audit_redis_prod redis-cli ping 2>/dev/null | grep -q "PONG"; then
    check_pass "Redis缓存连接正常"

    # 检查Redis内存使用
    redis_mem=$(docker exec uma_audit_redis_prod redis-cli INFO memory 2>/dev/null | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    if [ -n "$redis_mem" ]; then
        echo "  内存使用: $redis_mem"
    fi
else
    check_fail "Redis缓存连接失败"
fi

# 6. 检查后端API
echo ""
echo "检查 6/8: 后端API服务"
echo "----------------------------------------"
if curl -s http://localhost:8000/docs > /dev/null; then
    check_pass "后端API服务响应正常"
else
    check_fail "后端API服务无响应"
fi

# 7. 检查磁盘空间
echo ""
echo "检查 7/8: 磁盘空间"
echo "----------------------------------------"
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    check_pass "磁盘空间充足 (已使用 ${disk_usage}%)"
elif [ "$disk_usage" -lt 90 ]; then
    check_warn "磁盘空间紧张 (已使用 ${disk_usage}%)"
else
    check_fail "磁盘空间不足 (已使用 ${disk_usage}%)"
fi

# 显示详细磁盘使用
echo ""
df -h / | head -2

# 8. 检查内存使用
echo ""
echo "检查 8/8: 内存使用"
echo "----------------------------------------"
mem_usage=$(free | awk '/Mem:/ {printf("%.0f", $3/$2 * 100)}')
if [ "$mem_usage" -lt 80 ]; then
    check_pass "内存使用正常 (已使用 ${mem_usage}%)"
elif [ "$mem_usage" -lt 90 ]; then
    check_warn "内存使用较高 (已使用 ${mem_usage}%)"
else
    check_fail "内存使用过高 (已使用 ${mem_usage}%)"
fi

# 显示详细内存使用
echo ""
free -h

# 9. 检查容器日志错误
echo ""
echo "检查最近的错误日志:"
echo "----------------------------------------"
error_count=$(docker-compose -f docker-compose.prod.yml logs --tail=100 2>&1 | grep -i "error" | wc -l)
if [ "$error_count" -eq 0 ]; then
    check_pass "最近无错误日志"
else
    check_warn "发现 $error_count 条错误日志"
    echo "  使用以下命令查看详细日志:"
    echo "  docker-compose -f docker-compose.prod.yml logs --tail=100 | grep -i error"
fi

# 总结
echo ""
echo "======================================"
echo "  健康检查总结"
echo "======================================"
echo ""
echo -e "${GREEN}通过: $PASS${NC}"
echo -e "${YELLOW}警告: $WARN${NC}"
echo -e "${RED}失败: $FAIL${NC}"
echo ""

if [ "$FAIL" -eq 0 ]; then
    if [ "$WARN" -eq 0 ]; then
        echo -e "${GREEN}✓ 系统运行正常!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ 系统基本正常,但有警告项需要注意${NC}"
        exit 0
    fi
else
    echo -e "${RED}✗ 系统存在问题,请检查失败项${NC}"
    echo ""
    echo "常见问题解决:"
    echo "  1. 容器未运行: docker-compose -f docker-compose.prod.yml up -d"
    echo "  2. 查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  3. 重启服务: docker-compose -f docker-compose.prod.yml restart"
    exit 1
fi
