# 🚀 简化部署指南

## 在阿里云服务器上执行以下命令

### 1️⃣ SSH登录服务器
```bash
ssh root@8.136.59.48
```

### 2️⃣ 进入项目目录
```bash
cd /opt/uma-audit5
```

### 3️⃣ 检查文件（确认上传成功）
```bash
ls -lh uma-audit5-docker-images-*.tar.gz
ls -lh .env
ls -lh docker-compose.yml
```

### 4️⃣ 执行一键部署脚本
```bash
bash deployment/final-deploy.sh
```

**脚本会自动完成：**
- ✅ 检查必要文件
- ✅ 加载Docker镜像
- ✅ 启动所有服务（数据库、Redis、后端）
- ✅ 验证服务健康状态

### 5️⃣ 查看服务状态
```bash
docker-compose ps
```

**预期输出（所有服务应该是 Up 状态）：**
```
NAME                 STATUS         PORTS
uma_audit_backend    Up x seconds  0.0.0.0:8000->8000/tcp
uma_audit_db         Up x seconds  5432/tcp
uma_audit_redis      Up x seconds  6379/tcp
```

### 6️⃣ 测试API
```bash
# 本地测试
curl http://localhost:8000/api/v1/health

# 外部访问测试
curl http://8.136.59.48:8000/api/v1/health
```

**预期返回：**
```json
{"status":"healthy","timestamp":"2025-01-20T..."}
```

---

## 🔍 如果遇到问题

### 查看日志
```bash
# 查看后端日志
docker-compose logs backend

# 实时跟踪日志
docker-compose logs -f backend

# 查看最近50行
docker-compose logs backend --tail=50
```

### 重启服务
```bash
docker-compose restart backend
```

### 完全重启
```bash
docker-compose down
docker-compose up -d
```

---

## ✅ 部署成功验证

访问以下地址：
- **API健康检查**: http://8.136.59.48:8000/api/v1/health
- **API文档**: http://8.136.59.48:8000/docs

---

## 📝 重要提醒

如果无法从外部访问，需要在阿里云控制台开放端口：
1. 进入 ECS 控制台
2. 安全组 → 配置规则
3. 添加入方向规则：
   - 端口：8000
   - 授权对象：0.0.0.0/0
   - 协议：TCP

---

**服务器**: 8.136.59.48
**项目目录**: /opt/uma-audit5
**API端口**: 8000
