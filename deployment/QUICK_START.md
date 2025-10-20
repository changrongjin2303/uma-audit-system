# 快速部署参考

## ✅ 本地准备完成

- **镜像包**: `uma-audit5-docker-images-20251020.tar.gz` (1.1 GB)
- **MD5 校验**: `4d2f26ee82ec28023ba4d86a864a629c`
- **代码提交**: 已推送到 GitHub (commit: df16ca4)

---

## 📦 下一步：传输镜像到服务器

### 方式 1: 直接 SCP 传输（推荐）

```bash
# 替换为你的服务器信息
scp uma-audit5-docker-images-20251020.tar.gz root@YOUR_SERVER_IP:/root/
```

### 方式 2: 通过阿里云 OSS

```bash
# 1. 上传到 OSS
ossutil cp uma-audit5-docker-images-20251020.tar.gz oss://YOUR_BUCKET/

# 2. 在服务器下载
ssh root@YOUR_SERVER_IP
ossutil cp oss://YOUR_BUCKET/uma-audit5-docker-images-20251020.tar.gz /root/
```

### 方式 3: rsync 断点续传

```bash
rsync -avz --progress \
  uma-audit5-docker-images-20251020.tar.gz \
  root@YOUR_SERVER_IP:/root/
```

---

## 🚀 服务器部署步骤

```bash
# 1. SSH 登录服务器
ssh root@YOUR_SERVER_IP

# 2. 克隆或更新代码
git clone git@github.com:changrongjin2303/uma-audit-system.git /opt/uma-audit5
# 或更新已有代码
cd /opt/uma-audit5 && git pull origin main

# 3. 移动镜像包到项目目录
mv /root/uma-audit5-docker-images-20251020.tar.gz /opt/uma-audit5/

# 4. 加载 Docker 镜像
cd /opt/uma-audit5
bash deployment/server-load-images.sh uma-audit5-docker-images-20251020.tar.gz

# 5. 验证镜像加载成功
docker images | grep -E "python|postgres|redis|nginx|uma-audit"

# 6. 配置环境变量（首次部署）
cp .env.example .env
vim .env  # 修改以下配置：
```

### 必须修改的环境变量

```bash
# 数据库配置
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE

# Redis配置
REDIS_PASSWORD=YOUR_REDIS_PASSWORD_HERE

# 应用密钥（生成方法：openssl rand -hex 32）
SECRET_KEY=YOUR_SECRET_KEY_HERE

# API地址
API_BASE_URL=http://YOUR_SERVER_IP:8000

# AI服务配置（可选）
OPENAI_API_KEY=your_openai_api_key
QIANWEN_API_KEY=your_qianwen_api_key
```

```bash
# 7. 启动服务
docker-compose up -d

# 8. 查看服务状态
docker-compose ps

# 9. 查看日志
docker-compose logs -f backend

# 10. 验证服务
curl http://localhost:8000/api/v1/health
# 应返回: {"status":"healthy","timestamp":"..."}
```

---

## 🔧 常用命令

```bash
# 查看所有容器
docker-compose ps

# 查看日志
docker-compose logs -f          # 所有服务
docker-compose logs -f backend  # 只看后端

# 重启服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 重新启动所有服务
docker-compose up -d

# 进入容器内部
docker-compose exec backend bash
docker-compose exec postgres psql -U uma_audit -d uma_audit

# 查看镜像
docker images

# 清理未使用的镜像
docker system prune -a
```

---

## 📊 验证清单

- [ ] 镜像传输到服务器完成
- [ ] 代码从 GitHub 拉取完成
- [ ] Docker 镜像加载成功（4 个基础镜像 + 1 个项目镜像）
- [ ] .env 文件配置完成
- [ ] 数据库密码已修改
- [ ] Redis 密码已修改
- [ ] SECRET_KEY 已生成并配置
- [ ] 服务启动成功（docker-compose ps 显示 Up）
- [ ] 健康检查通过（/api/v1/health 返回成功）
- [ ] 前端可访问（如有）
- [ ] 防火墙端口已开放（80, 443, 8000, 3000）

---

## ❌ 故障排查

### 镜像加载失败
```bash
# 检查文件完整性
md5sum uma-audit5-docker-images-20251020.tar.gz
# 应为: 4d2f26ee82ec28023ba4d86a864a629c

# 重新解压查看
tar -tzf uma-audit5-docker-images-20251020.tar.gz | head -20
```

### 服务启动失败
```bash
# 查看详细日志
docker-compose logs backend --tail=100

# 检查端口占用
netstat -tlnp | grep 8000

# 重置所有容器
docker-compose down -v
docker-compose up -d
```

### 数据库连接失败
```bash
# 测试数据库连接
docker-compose exec postgres psql -U uma_audit -d uma_audit -c "SELECT 1;"

# 检查环境变量
cat .env | grep POSTGRES

# 重启数据库
docker-compose restart postgres
```

---

## 📚 详细文档

- 完整部署指南: `deployment/DEPLOY_WITH_GITHUB.md`
- 阿里云部署总览: `deployment/ALIYUN_DEPLOYMENT_GUIDE.md`

---

## 📞 需要帮助？

如果遇到问题：
1. 查看详细日志：`docker-compose logs -f`
2. 检查容器状态：`docker-compose ps`
3. 查看详细文档：`deployment/DEPLOY_WITH_GITHUB.md`
4. 确认网络连接：`ping YOUR_SERVER_IP`

---

**创建时间**: 2025-01-20
**镜像包版本**: 20251020
**Git Commit**: df16ca4
