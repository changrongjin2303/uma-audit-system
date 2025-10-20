# 通过 GitHub + 镜像传输部署到阿里云服务器

## 概述

由于 Docker Hub 在中国大陆访问受限，本指南提供通过 GitHub 同步代码 + 离线传输 Docker 镜像的完整部署方案。

### 部署流程图

```
本地开发环境 (有VPN)
  ↓
  1. GitHub Push 代码
  ↓
阿里云服务器
  ↓
  2. GitHub Pull 代码
  ↓
  3. 镜像传输 (3种方式任选一种)
  ↓
  4. 启动服务
```

---

## 准备工作

### 本地环境要求
- ✅ Docker Desktop 已安装并配置镜像加速器
- ✅ VPN 连接（用于拉取 Docker 镜像）
- ✅ Git 已配置并连接到 GitHub

### 服务器环境要求
- ✅ Docker 和 Docker Compose 已安装
- ✅ Git 已安装并配置 SSH 密钥
- ✅ 足够的磁盘空间（至少 10GB 可用）

---

## 完整部署步骤

### 第一部分：本地准备（在有VPN的环境执行）

#### 步骤 1：生成 Docker 镜像包

```bash
# 进入项目目录
cd /Users/crj/Documents/code/uma-audit5

# 执行预构建脚本（需要VPN）
./deployment/prebuild-images.sh
```

**执行过程**：
1. 拉取基础镜像（python:3.11-slim, postgres:15, redis:7, nginx:alpine）
2. 构建项目镜像（后端、前端）
3. 打包所有镜像到 `uma-audit5-docker-images-YYYYMMDD.tar.gz`

**预计时间**：5-15分钟（取决于网络速度）

**生成文件**：
```
uma-audit5-docker-images-20250120.tar.gz  (~1.5-2GB)
```

#### 步骤 2：提交代码到 GitHub

```bash
# 确保镜像包不会被提交（已在.gitignore中配置）
git add .
git commit -m "Update deployment scripts and documentation"
git push origin main
```

---

### 第二部分：传输镜像到服务器（3种方式任选）

#### 方式 1：直接 SCP 传输（推荐，最简单）

```bash
# 替换为你的服务器信息
scp uma-audit5-docker-images-*.tar.gz root@your-server-ip:/root/
```

**优点**：简单直接
**缺点**：如果网络不稳定可能中断
**适用**：网络稳定，服务器可直接SSH访问

---

#### 方式 2：通过云存储中转（推荐，最稳定）

##### 使用阿里云 OSS（对象存储）

**步骤 2.1：上传到 OSS**

```bash
# 安装 ossutil（如果还没安装）
# macOS
brew install ossutil

# 配置 OSS
ossutil config

# 上传文件
ossutil cp uma-audit5-docker-images-*.tar.gz oss://your-bucket-name/
```

**步骤 2.2：在服务器下载**

```bash
# 登录服务器
ssh root@your-server-ip

# 从 OSS 下载（内网下载，速度快）
ossutil cp oss://your-bucket-name/uma-audit5-docker-images-*.tar.gz /root/

# 或使用 wget（获取公网URL）
wget "https://your-bucket.oss-cn-hangzhou.aliyuncs.com/uma-audit5-docker-images-*.tar.gz"
```

**优点**：
- 内网传输速度快（几十MB/s）
- 可断点续传
- 不占用本地上传带宽

**缺点**：需要开通阿里云 OSS 服务（有一定费用）

---

##### 使用其他云存储

**百度网盘/Google Drive/Dropbox**

```bash
# 本地上传到网盘
# 在服务器上下载（需要安装对应的CLI工具或使用网页）

# 示例：使用 wget 下载分享链接
wget -O uma-audit5-docker-images.tar.gz "分享链接"
```

---

#### 方式 3：使用 rsync 断点续传（网络不稳定时推荐）

```bash
# 支持断点续传，适合大文件和不稳定网络
rsync -avz --progress \
  uma-audit5-docker-images-*.tar.gz \
  root@your-server-ip:/root/

# 如果中断，重新运行相同命令即可继续传输
```

**优点**：
- 支持断点续传
- 传输失败可以重试
- 显示进度条

---

### 第三部分：服务器部署

#### 步骤 1：拉取代码

```bash
# 登录服务器
ssh root@your-server-ip

# 克隆代码（首次）
git clone git@github.com:your-username/uma-audit5.git /opt/uma-audit5

# 或更新代码（已克隆）
cd /opt/uma-audit5
git pull origin main
```

#### 步骤 2：加载 Docker 镜像

```bash
# 将镜像包移动到项目目录
mv /root/uma-audit5-docker-images-*.tar.gz /opt/uma-audit5/

# 进入项目目录
cd /opt/uma-audit5

# 执行加载脚本
bash deployment/server-load-images.sh uma-audit5-docker-images-*.tar.gz

# 或自动检测最新镜像包
bash deployment/server-load-images.sh
```

**脚本会自动：**
1. 解压镜像包
2. 加载所有镜像到 Docker
3. 显示加载结果
4. 清理临时文件

#### 步骤 3：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
vim .env
```

**关键配置项**：

```bash
# 数据库配置
POSTGRES_USER=uma_audit
POSTGRES_PASSWORD=your_strong_password_here  # 修改为强密码
POSTGRES_DB=uma_audit

# Redis配置
REDIS_PASSWORD=your_redis_password_here      # 修改为强密码

# 应用配置
SECRET_KEY=your_secret_key_here              # 生成随机密钥
API_BASE_URL=http://your-server-ip:8000

# AI服务配置（可选）
OPENAI_API_KEY=your_openai_api_key
QIANWEN_API_KEY=your_qianwen_api_key
```

**生成安全密钥**：

```bash
# 生成随机密钥
openssl rand -hex 32
# 或
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 步骤 4：启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

**预期输出**：

```
NAME                    COMMAND                  SERVICE    STATUS
uma-audit5-backend      "uvicorn app.main:ap…"   backend    Up
uma-audit5-postgres     "docker-entrypoint.s…"   postgres   Up
uma-audit5-redis        "docker-entrypoint.s…"   redis      Up
```

#### 步骤 5：验证部署

```bash
# 检查后端 API
curl http://localhost:8000/api/v1/health

# 应返回：
# {"status":"healthy","timestamp":"..."}

# 检查数据库连接
docker-compose exec backend python -c "from app.core.database import engine; print('DB OK')"

# 查看服务日志
docker-compose logs backend --tail=50
```

#### 步骤 6：配置防火墙和域名（可选）

```bash
# 开放端口
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp  # API端口
ufw allow 3000/tcp  # 前端端口（如果有）

# 配置 Nginx 反向代理（推荐）
# 参考 deployment/nginx.conf
```

---

## 更新部署

### 代码更新

```bash
# 在服务器上执行
cd /opt/uma-audit5
git pull origin main
docker-compose restart backend
```

### 镜像更新（有代码变更时）

```bash
# 本地重新构建和打包
./deployment/prebuild-images.sh

# 传输到服务器
scp uma-audit5-docker-images-*.tar.gz root@server:/opt/uma-audit5/

# 服务器加载新镜像
cd /opt/uma-audit5
bash deployment/server-load-images.sh

# 重启服务
docker-compose down
docker-compose up -d
```

---

## 故障排查

### 问题 1：镜像加载失败

**现象**：`docker load` 报错

**解决**：
```bash
# 检查文件完整性
md5sum uma-audit5-docker-images-*.tar.gz

# 重新解压查看内容
tar -tzf uma-audit5-docker-images-*.tar.gz | head -20

# 手动加载单个镜像测试
tar -xzf uma-audit5-docker-images-*.tar.gz -C /tmp/
docker load -i /tmp/python_3.11-slim.tar
```

### 问题 2：服务启动失败

**现象**：`docker-compose ps` 显示服务 Exit 或 Restarting

**解决**：
```bash
# 查看详细日志
docker-compose logs backend --tail=100

# 检查环境变量
cat .env

# 检查端口占用
netstat -tlnp | grep 8000

# 重新启动
docker-compose down
docker-compose up -d
```

### 问题 3：数据库连接失败

**现象**：后端日志显示数据库连接错误

**解决**：
```bash
# 检查 PostgreSQL 服务
docker-compose exec postgres psql -U uma_audit -d uma_audit -c "SELECT 1;"

# 重置数据库（慎用！会删除所有数据）
docker-compose down -v
docker-compose up -d

# 运行数据库迁移
docker-compose exec backend alembic upgrade head
```

### 问题 4：传输中断

**解决**：
```bash
# 使用 rsync 断点续传
rsync -avz --partial --progress \
  uma-audit5-docker-images-*.tar.gz \
  root@server:/root/

# 或使用 scp 的替代工具（如果服务器支持）
# 安装 lrzsz
yum install -y lrzsz  # CentOS
apt install -y lrzsz  # Ubuntu

# 使用 rz/sz 命令传输（通过SSH会话）
```

---

## 文件大小优化建议

### 如果镜像包太大（>2GB）

**方法 1：只传输必要的镜像**

编辑 `deployment/prebuild-images.sh`，注释掉不需要的镜像：

```bash
BASE_IMAGES=(
    "python:3.11-slim"
    "postgres:15"
    "redis:7"
    # "nginx:alpine"  # 如果不使用 nginx，注释掉
)
```

**方法 2：使用更小的基础镜像**

修改 `backend/Dockerfile`：

```dockerfile
# 使用 alpine 版本（更小，但可能有兼容性问题）
FROM python:3.11-alpine

# 当前使用 slim 版本（推荐平衡点）
FROM python:3.11-slim
```

**方法 3：压缩优化**

```bash
# 使用更高的压缩率
tar -czf uma-audit5-docker-images.tar.gz --use-compress-program='gzip -9' *.tar

# 或使用 xz 压缩（压缩率更高，但速度慢）
tar -cJf uma-audit5-docker-images.tar.xz *.tar
```

---

## 自动化脚本

### 一键本地打包脚本

创建 `deployment/pack-for-deploy.sh`：

```bash
#!/bin/bash
set -e

echo "=== 一键打包部署 ==="

# 1. 构建镜像
echo "步骤 1/3: 构建 Docker 镜像..."
./deployment/prebuild-images.sh

# 2. 提交代码
echo "步骤 2/3: 提交代码到 GitHub..."
read -p "输入提交信息: " commit_msg
git add .
git commit -m "$commit_msg" || true
git push origin main

# 3. 显示传输命令
echo "步骤 3/3: 镜像包已准备完成"
echo ""
echo "传输命令（替换为你的服务器IP）："
echo "scp $(ls -t uma-audit5-docker-images-*.tar.gz | head -1) root@SERVER_IP:/root/"
```

### 一键服务器部署脚本

创建 `deployment/server-deploy.sh`：

```bash
#!/bin/bash
set -e

echo "=== 服务器一键部署 ==="

# 1. 拉取代码
echo "步骤 1/4: 拉取最新代码..."
git pull origin main

# 2. 加载镜像
if [ -f uma-audit5-docker-images-*.tar.gz ]; then
    echo "步骤 2/4: 加载 Docker 镜像..."
    bash deployment/server-load-images.sh
else
    echo "警告：未找到镜像包，跳过镜像加载"
fi

# 3. 配置环境（如果是首次部署）
if [ ! -f .env ]; then
    echo "步骤 3/4: 配置环境变量..."
    cp .env.example .env
    echo "请编辑 .env 文件后重新运行此脚本"
    exit 1
fi

# 4. 启动服务
echo "步骤 4/4: 启动服务..."
docker-compose down
docker-compose up -d

# 5. 显示状态
echo ""
echo "=== 部署完成 ==="
docker-compose ps
echo ""
echo "查看日志: docker-compose logs -f"
echo "健康检查: curl http://localhost:8000/api/v1/health"
```

---

## 快速参考

### 常用命令

```bash
# 本地操作
./deployment/prebuild-images.sh              # 构建镜像包
scp *.tar.gz root@server:/root/              # 传输到服务器

# 服务器操作
git pull                                      # 更新代码
bash deployment/server-load-images.sh        # 加载镜像
docker-compose up -d                          # 启动服务
docker-compose logs -f                        # 查看日志
docker-compose ps                             # 查看状态
docker-compose restart backend                # 重启后端
docker-compose down                           # 停止所有服务
```

### 目录结构

```
uma-audit5/
├── deployment/
│   ├── DEPLOY_WITH_GITHUB.md          # 本文档
│   ├── ALIYUN_DEPLOYMENT_GUIDE.md     # 阿里云部署总指南
│   ├── prebuild-images.sh             # 本地打包脚本
│   ├── server-load-images.sh          # 服务器加载脚本
│   └── setup-docker-mirrors.sh        # 镜像加速器配置
├── backend/                            # 后端代码
├── frontend/                           # 前端代码（如有）
├── docker-compose.yml                  # Docker 编排配置
├── .env.example                        # 环境变量模板
└── .gitignore                          # Git 忽略规则
```

---

## 注意事项

1. **镜像包不要提交到 Git**：已在 `.gitignore` 中配置，但仍需注意
2. **环境变量安全**：`.env` 文件包含敏感信息，不要提交到 Git
3. **定期备份**：定期备份数据库和重要文件
4. **监控日志**：定期查看 `docker-compose logs` 排查问题
5. **更新及时性**：代码更新后要同步更新服务器

---

## 总结

通过 GitHub + 镜像离线传输的方式，你可以：

✅ **代码管理**：通过 GitHub 版本控制和同步代码
✅ **镜像传输**：通过 SCP/OSS 等方式传输 Docker 镜像
✅ **灵活部署**：不依赖 Docker Hub，完全离线部署
✅ **更新方便**：代码通过 Git 更新，镜像按需传输

**推荐部署流程**：
1. 本地开发 → 2. Git Push → 3. 构建镜像包 → 4. 传输镜像 → 5. 服务器 Git Pull + 加载镜像 → 6. 启动服务

---

**文档更新**：2025-01-20
**适用版本**：uma-audit5 v1.0
**作者**：Claude AI Assistant
