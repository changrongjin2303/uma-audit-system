#!/bin/bash
# 造价审计系统 - 阿里云一键部署脚本
# 使用方法: ./deploy-to-aliyun.sh

set -e  # 遇到错误立即退出

echo "======================================"
echo "  造价审计系统 - 阿里云部署助手"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

echo "步骤 1/8: 检查系统环境..."
echo "----------------------------------------"

# 检查操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "操作系统: $NAME $VERSION"
else
    echo -e "${YELLOW}警告: 无法检测操作系统版本${NC}"
fi

# 检查Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker 已安装: $(docker --version)${NC}"
else
    echo -e "${RED}✗ Docker 未安装${NC}"
    echo "正在安装 Docker..."
    curl -fsSL https://get.docker.com | bash
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}✓ Docker 安装完成${NC}"
fi

# 检查Docker Compose
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose 已安装: $(docker-compose --version)${NC}"
else
    echo -e "${RED}✗ Docker Compose 未安装${NC}"
    echo "正在安装 Docker Compose..."
    apt update
    apt install docker-compose -y
    echo -e "${GREEN}✓ Docker Compose 安装完成${NC}"
fi

echo ""
echo "步骤 2/8: 配置生产环境..."
echo "----------------------------------------"

# 检查是否存在生产环境配置
if [ -f ".env.production" ]; then
    echo -e "${YELLOW}已存在 .env.production 配置文件${NC}"
    read -p "是否覆盖? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "保留现有配置文件"
    else
        cp .env .env.production
        echo -e "${GREEN}✓ 已创建新的生产环境配置${NC}"
    fi
else
    cp .env .env.production
    echo -e "${GREEN}✓ 已创建生产环境配置文件${NC}"
fi

# 生成随机密码
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

echo ""
echo "正在生成安全密钥..."
echo "数据库密码: $DB_PASSWORD"
echo "Redis密码: $REDIS_PASSWORD"
echo ""

# 更新配置文件
sed -i "s|password@localhost|${DB_PASSWORD}@postgres|g" .env.production
sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD}|g" .env.production
sed -i "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|g" .env.production
sed -i "s|DEBUG=true|DEBUG=false|g" .env.production

echo -e "${GREEN}✓ 安全配置已更新${NC}"

# 询问服务器IP
echo ""
read -p "请输入服务器公网IP地址: " SERVER_IP
if [ -n "$SERVER_IP" ]; then
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=[\"http://${SERVER_IP}\",\"http://${SERVER_IP}:8000\",\"https://${SERVER_IP}\"]|g" .env.production
    echo -e "${GREEN}✓ CORS配置已更新${NC}"
fi

echo ""
echo "步骤 3/8: 创建生产环境Docker配置..."
echo "----------------------------------------"

# 检查是否存在生产环境docker-compose文件
if [ ! -f "docker-compose.prod.yml" ]; then
    cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: uma_audit_db_prod
    environment:
      POSTGRES_DB: uma_audit
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: uma_audit_redis_prod
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: uma_audit_backend_prod
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/uma_audit
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - DEBUG=false
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/logs:/app/logs
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: uma_audit_frontend_prod
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always

volumes:
  postgres_data:
  redis_data:
EOF
    echo -e "${GREEN}✓ 已创建 docker-compose.prod.yml${NC}"
else
    echo -e "${YELLOW}docker-compose.prod.yml 已存在,跳过${NC}"
fi

echo ""
echo "步骤 4/8: 创建前端生产环境配置..."
echo "----------------------------------------"

# 创建前端生产Dockerfile
if [ ! -f "frontend/Dockerfile.prod" ]; then
    cat > frontend/Dockerfile.prod << 'EOF'
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
    echo -e "${GREEN}✓ 已创建前端生产Dockerfile${NC}"
else
    echo -e "${YELLOW}前端生产Dockerfile已存在,跳过${NC}"
fi

# 创建Nginx配置
if [ ! -f "frontend/nginx.conf" ]; then
    cat > frontend/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/json application/javascript;

    server {
        listen 80;
        server_name _;

        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend:8000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 7d;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF
    echo -e "${GREEN}✓ 已创建Nginx配置文件${NC}"
else
    echo -e "${YELLOW}Nginx配置文件已存在,跳过${NC}"
fi

echo ""
echo "步骤 5/8: 构建Docker镜像..."
echo "----------------------------------------"
echo "这可能需要5-10分钟,请耐心等待..."
echo ""

# 导出密码到环境变量
export DB_PASSWORD=$DB_PASSWORD
export REDIS_PASSWORD=$REDIS_PASSWORD

# 构建镜像
docker-compose -f docker-compose.prod.yml build

echo ""
echo -e "${GREEN}✓ Docker镜像构建完成${NC}"

echo ""
echo "步骤 6/8: 启动所有服务..."
echo "----------------------------------------"

# 启动容器
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "服务状态:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "步骤 7/8: 初始化数据库..."
echo "----------------------------------------"

# 等待数据库完全启动
echo "等待数据库初始化..."
sleep 15

# 运行数据库迁移
echo "运行数据库迁移..."
docker exec -it uma_audit_backend_prod python -m alembic upgrade head || {
    echo -e "${YELLOW}警告: 数据库迁移可能失败,请手动检查${NC}"
}

echo ""
echo "步骤 8/8: 创建管理员账号..."
echo "----------------------------------------"

read -p "是否创建管理员账号? (y/n): " create_admin
if [ "$create_admin" = "y" ]; then
    read -p "管理员用户名: " admin_username
    read -s -p "管理员密码: " admin_password
    echo ""

    # 这里需要你在backend/scripts目录创建create_admin.py脚本
    # docker exec -it uma_audit_backend_prod python scripts/create_admin.py "$admin_username" "$admin_password"
    echo -e "${YELLOW}请手动进入系统创建管理员账号${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}  部署完成! 🎉${NC}"
echo "======================================"
echo ""
echo "访问信息:"
echo "----------------------------------------"
echo "前端地址: http://${SERVER_IP}"
echo "后端API文档: http://${SERVER_IP}:8000/docs"
echo ""
echo "安全信息 (请妥善保管):"
echo "----------------------------------------"
echo "数据库密码: $DB_PASSWORD"
echo "Redis密码: $REDIS_PASSWORD"
echo ""
echo "常用命令:"
echo "----------------------------------------"
echo "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "重启服务: docker-compose -f docker-compose.prod.yml restart"
echo "停止服务: docker-compose -f docker-compose.prod.yml stop"
echo "启动服务: docker-compose -f docker-compose.prod.yml start"
echo ""
echo "下一步:"
echo "----------------------------------------"
echo "1. 在浏览器访问 http://${SERVER_IP}"
echo "2. 检查系统是否正常运行"
echo "3. 配置域名和HTTPS (可选)"
echo "4. 设置定期备份"
echo ""
echo "详细文档请查看: 阿里云部署指南.md"
echo ""
