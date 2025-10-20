# 阿里云服务器部署指南

## 问题说明

由于 Docker Hub (docker.io) 在中国大陆访问受限，直接在阿里云服务器上拉取镜像会失败。本指南提供了三种解决方案。

---

## 方案对比

| 方案 | 优点 | 缺点 | 推荐场景 |
|-----|-----|-----|---------|
| **方案一：镜像加速器** | 最简单，无需传输文件 | 依赖镜像源稳定性 | 首选方案 |
| **方案二：离线镜像传输** | 最可靠，不依赖网络 | 需要传输大文件(~2GB) | 镜像源失效时 |
| **方案三：阿里云个人镜像仓库** | 速度快，稳定 | 需要配置阿里云账号 | 企业长期使用 |

---

## 方案一：配置 Docker 镜像加速器（推荐）

### 1. 在阿里云服务器上执行

将 `setup-docker-mirrors.sh` 脚本传输到服务器：

```bash
# 本地执行（将脚本传输到服务器）
scp deployment/setup-docker-mirrors.sh root@your-server-ip:/root/

# 登录服务器
ssh root@your-server-ip

# 执行配置脚本
sudo bash /root/setup-docker-mirrors.sh
```

### 2. 验证配置

```bash
# 查看镜像加速器配置
docker info | grep -A 5 "Registry Mirrors"

# 测试拉取镜像
docker pull python:3.11-slim
```

### 3. 部署项目

```bash
# 克隆或上传项目代码
cd /path/to/uma-audit5

# 启动项目
docker-compose up -d
```

### 常用国内镜像源

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.sjtug.sjtu.edu.cn",  // 上海交大
    "https://mirror.ccs.tencentyun.com",         // 腾讯云
    "https://docker.mirrors.ustc.edu.cn",        // 中科大
    "https://hub-mirror.c.163.com",              // 网易
    "https://mirror.baidubce.com"                // 百度云
  ]
}
```

---

## 方案二：离线镜像传输（最可靠）

### 步骤 1：在本地（有VPN的环境）打包镜像

```bash
# 在项目根目录执行
cd /Users/crj/Documents/code/uma-audit5

# 运行预构建脚本（拉取所有镜像并打包）
./deployment/prebuild-images.sh
```

这个脚本会：
1. 拉取所有基础镜像（python、postgres、redis、nginx）
2. 构建项目镜像（后端、前端）
3. 将所有镜像打包成 `uma-audit5-docker-images-YYYYMMDD.tar.gz`

生成的文件大小约 1-2GB。

### 步骤 2：传输镜像包到服务器

```bash
# 使用 scp 传输（替换为你的服务器信息）
scp uma-audit5-docker-images-*.tar.gz root@your-server-ip:/root/

# 或使用其他传输方式（如阿里云OSS、FTP等）
```

### 步骤 3：在服务器上加载镜像

```bash
# 登录服务器
ssh root@your-server-ip

# 解压镜像包
mkdir -p docker-images-import
tar -xzf uma-audit5-docker-images-*.tar.gz -C docker-images-import

# 加载所有镜像
cd docker-images-import
for img in *.tar; do
    echo "Loading $img..."
    docker load -i $img
done

# 验证镜像已加载
docker images

# 清理临时文件
cd ..
rm -rf docker-images-import
```

### 步骤 4：启动项目

```bash
# 进入项目目录
cd /path/to/uma-audit5

# 确保环境配置正确
cp .env.example .env
vim .env  # 修改配置

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 方案三：使用阿里云个人镜像仓库

### 1. 获取阿里云镜像加速地址

1. 登录阿里云控制台
2. 访问 **容器镜像服务** > **镜像工具** > **镜像加速器**
3. 获取你的专属加速地址（格式：`https://xxxxx.mirror.aliyuncs.com`）

### 2. 配置镜像加速器

```bash
# 在服务器上创建或编辑配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://你的加速器地址.mirror.aliyuncs.com"]
}
EOF

# 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 3. 验证并部署

```bash
# 测试拉取镜像
docker pull python:3.11-slim

# 部署项目
cd /path/to/uma-audit5
docker-compose up -d
```

---

## 常见问题排查

### 问题 1：配置镜像加速器后仍然拉取失败

**可能原因**：
- 镜像源暂时不可用
- 网络防火墙限制
- Docker 配置未生效

**解决方法**：
```bash
# 1. 验证 Docker 配置
docker info | grep -A 5 "Registry Mirrors"

# 2. 测试不同镜像源
# 编辑 /etc/docker/daemon.json，更换镜像源

# 3. 检查网络连接
curl -I https://docker.mirrors.sjtug.sjtu.edu.cn

# 4. 如果都失败，使用方案二（离线传输）
```

### 问题 2：镜像传输文件太大

**解决方法**：
```bash
# 1. 只保存必需的镜像
# 编辑 prebuild-images.sh，删除不需要的镜像

# 2. 使用增量传输
rsync -avz --progress uma-audit5-docker-images-*.tar.gz root@server:/root/

# 3. 使用云存储中转（如阿里云OSS）
# 本地上传 -> OSS -> 服务器下载（内网速度快）
```

### 问题 3：Docker 构建时失败

**可能原因**：
- 基础镜像未加载
- Dockerfile 路径错误

**解决方法**：
```bash
# 1. 检查基础镜像
docker images | grep python

# 2. 手动构建测试
cd backend
docker build -t uma-audit5-backend:latest .

# 3. 查看构建日志
docker-compose build --no-cache
```

---

## 部署后验证

### 1. 检查服务状态

```bash
# 查看所有容器
docker-compose ps

# 应该看到 4 个容器在运行：
# - uma-audit5-backend
# - uma-audit5-postgres
# - uma-audit5-redis
# - uma-audit5-nginx (如果有)
```

### 2. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f postgres
```

### 3. 测试 API

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 应返回：
# {"status":"healthy","timestamp":"..."}
```

### 4. 访问前端

在浏览器访问：
```
http://your-server-ip:3000
```

---

## 自动化部署脚本

### 完整部署脚本（服务器端）

创建 `deploy.sh`：

```bash
#!/bin/bash
set -e

echo "=== 阿里云服务器部署脚本 ==="

# 1. 配置镜像加速器
if [ -f setup-docker-mirrors.sh ]; then
    echo "配置 Docker 镜像加速器..."
    sudo bash setup-docker-mirrors.sh
fi

# 2. 如果有离线镜像包，则加载
if [ -f uma-audit5-docker-images-*.tar.gz ]; then
    echo "加载离线镜像..."
    mkdir -p docker-images-import
    tar -xzf uma-audit5-docker-images-*.tar.gz -C docker-images-import
    cd docker-images-import
    for img in *.tar; do docker load -i $img; done
    cd ..
    rm -rf docker-images-import
fi

# 3. 配置环境变量
if [ ! -f .env ]; then
    echo "创建环境配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置数据库密码等参数"
    exit 1
fi

# 4. 启动服务
echo "启动 Docker 服务..."
docker-compose up -d

# 5. 等待服务就绪
echo "等待服务启动..."
sleep 10

# 6. 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 7. 显示日志
echo "查看服务日志..."
docker-compose logs --tail=50

echo ""
echo "=== 部署完成 ==="
echo "访问地址: http://$(curl -s ifconfig.me):3000"
echo "API 文档: http://$(curl -s ifconfig.me):8000/docs"
```

---

## 推荐部署流程

### 新服务器（首次部署）

```bash
# 1. 本地准备镜像包（一次性）
./deployment/prebuild-images.sh

# 2. 传输到服务器
scp uma-audit5-docker-images-*.tar.gz root@server:/root/
scp -r deployment/* root@server:/root/uma-audit5/deployment/

# 3. 在服务器上执行
ssh root@server
cd /root/uma-audit5
bash deployment/setup-docker-mirrors.sh  # 配置加速器（可选）
bash deploy.sh  # 执行部署
```

### 已有镜像源配置的服务器

```bash
# 直接部署
ssh root@server
cd /path/to/uma-audit5
docker-compose up -d
```

---

## 性能优化建议

### 1. 使用 Docker 卷挂载

```yaml
# docker-compose.yml 中配置持久化存储
volumes:
  - postgres_data:/var/lib/postgresql/data
  - redis_data:/data
  - ./backend/uploads:/app/uploads
```

### 2. 配置资源限制

```yaml
# 限制容器资源使用
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### 3. 启用日志轮转

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
```

---

## 安全建议

### 1. 配置防火墙

```bash
# 只开放必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### 2. 使用 HTTPS

```bash
# 使用 Let's Encrypt 免费证书
apt install certbot
certbot certonly --standalone -d your-domain.com
```

### 3. 定期备份

```bash
# 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose exec postgres pg_dump -U uma_audit uma_audit > backup-$DATE.sql
```

---

## 监控和维护

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 清理未使用的镜像和容器
docker system prune -a
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 查看日志确认
docker-compose logs -f
```

---

## 联系支持

如果遇到问题，请提供以下信息：

1. 操作系统版本：`cat /etc/os-release`
2. Docker 版本：`docker --version`
3. 错误日志：`docker-compose logs`
4. 网络测试：`curl -I https://docker.mirrors.sjtug.sjtu.edu.cn`

---

**文档更新日期**：2025-01-20
**适用版本**：uma-audit5 v1.0
