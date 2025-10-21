#!/bin/bash
# .env配置文件生成助手
# 用途：交互式生成服务器端的.env配置文件

set -e

echo "========================================="
echo "  环境配置文件生成助手"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 获取服务器IP
echo -e "${BLUE}请输入你的阿里云服务器公网IP地址:${NC}"
read -p "服务器IP: " SERVER_IP

# 生成密钥
echo ""
echo -e "${YELLOW}正在生成安全密钥...${NC}"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
SECRET_KEY=$(openssl rand -hex 32)

echo -e "${GREEN}✓ 密钥生成完成${NC}"
echo ""

# 显示生成的配置
echo "========================================="
echo "  生成的配置信息"
echo "========================================="
echo -e "${YELLOW}数据库密码:${NC} $DB_PASSWORD"
echo -e "${YELLOW}Redis密码:${NC} $REDIS_PASSWORD"
echo -e "${YELLOW}JWT密钥:${NC} $SECRET_KEY"
echo -e "${YELLOW}服务器IP:${NC} $SERVER_IP"
echo ""

# 询问AI服务配置
echo -e "${BLUE}是否配置OpenAI服务? (y/n)${NC}"
read -p "> " -n 1 -r USE_OPENAI
echo
if [[ $USE_OPENAI =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}请输入OpenAI API Key:${NC}"
    read -p "> " OPENAI_KEY
else
    OPENAI_KEY="your-openai-api-key-if-needed"
fi

# 生成.env文件
ENV_FILE=".env"
echo ""
echo -e "${YELLOW}正在生成 $ENV_FILE 文件...${NC}"

cat > "$ENV_FILE" << EOF
# 造价材料审计系统 - 阿里云服务器生产环境配置
# 自动生成时间: $(date '+%Y-%m-%d %H:%M:%S')
# 服务器IP: $SERVER_IP

# ========== 数据库配置 ==========
DATABASE_URL=postgresql://uma_audit:${DB_PASSWORD}@postgres:5432/uma_audit
POSTGRES_USER=uma_audit
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=uma_audit
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# ========== Redis配置 ==========
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}

# ========== Celery配置 ==========
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/2

# ========== JWT安全配置 ==========
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ========== 系统安全配置 ==========
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["http://${SERVER_IP}","http://${SERVER_IP}:8000","http://${SERVER_IP}:3000","https://${SERVER_IP}"]
ALLOWED_HOSTS=["*"]

# ========== API访问限制 ==========
API_RATE_LIMIT=100
API_BURST_LIMIT=20
MAX_CONCURRENT_REQUESTS=50

# ========== 文件上传配置 ==========
MAX_FILE_SIZE=52428800
UPLOAD_DIR=/app/uploads
ALLOWED_EXTENSIONS=["xlsx","xls","csv","pdf","doc","docx"]

# ========== AI服务配置 ==========
# OpenAI配置
OPENAI_API_KEY=${OPENAI_KEY}
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# 通义千问配置
DASHSCOPE_API_KEY=sk-cfea46e9f36c4aaba4a9030d2c618284
DASHSCOPE_MODEL=qwen-max

# 百度AI配置
BAIDU_API_KEY=your-baidu-api-key-if-needed
BAIDU_SECRET_KEY=your-baidu-secret-key-if-needed

# AI分析配置
AI_TIMEOUT=30
AI_RETRY_TIMES=3
AI_MAX_CONCURRENT=5
AI_COST_LIMIT=0.1

# ========== 数据安全配置 ==========
DATA_ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-43)
BACKUP_ENCRYPTION=true
AUDIT_LOG_RETENTION_DAYS=365

# ========== 监控和日志配置 ==========
ENABLE_METRICS=true
METRICS_PORT=9090
LOG_FILE_MAX_SIZE=100MB
LOG_FILE_BACKUP_COUNT=10

# ========== API基础URL ==========
API_BASE_URL=http://${SERVER_IP}:8000
EOF

echo -e "${GREEN}✓ .env 文件生成成功!${NC}"
echo ""

# 显示文件内容
echo "========================================="
echo "  生成的 .env 文件内容预览"
echo "========================================="
head -30 "$ENV_FILE"
echo "..."
echo ""

# 保存密钥备份
BACKUP_FILE="deployment/.env.backup.$(date '+%Y%m%d_%H%M%S').txt"
cat > "$BACKUP_FILE" << EOF
# 密钥备份 - 请妥善保管
生成时间: $(date '+%Y-%m-%d %H:%M:%S')
服务器IP: $SERVER_IP

数据库密码: $DB_PASSWORD
Redis密码: $REDIS_PASSWORD
JWT密钥: $SECRET_KEY
OpenAI Key: $OPENAI_KEY
EOF

echo -e "${GREEN}✓ 密钥备份已保存到: $BACKUP_FILE${NC}"
echo -e "${YELLOW}⚠️  请妥善保管此文件，不要提交到代码仓库!${NC}"
echo ""

echo "========================================="
echo "  下一步操作"
echo "========================================="
echo "1. 将 .env 文件上传到服务器的项目目录"
echo "   scp .env root@${SERVER_IP}:/opt/uma-audit5/"
echo ""
echo "2. 或者将以下内容手动复制到服务器的 .env 文件中"
echo ""
echo "3. 在服务器上运行部署脚本:"
echo "   bash deployment/quick-deploy-on-server.sh"
echo ""
