# 服务器端部署命令清单

## 📋 在阿里云服务器 8.136.59.48 上执行以下命令

### 第一步：SSH登录服务器
```bash
ssh root@8.136.59.48
```

---

### 第二步：进入项目目录并检查文件
```bash
cd /opt/uma-audit5

# 检查必要文件是否存在
echo "检查文件..."
ls -lh uma-audit5-docker-images-*.tar.gz  # 检查镜像包
ls -lh .env                                # 检查配置文件
ls -lh docker-compose.yml                  # 检查docker-compose配置

# 查看.env文件内容（确认配置正确）
head -20 .env
```

---

### 第三步：加载Docker镜像
```bash
# 方法1：使用提供的脚本（推荐）
bash deployment/server-load-images.sh uma-audit5-docker-images-20251020.tar.gz

# 方法2：手动加载
docker load -i uma-audit5-docker-images-20251020.tar.gz
```

**预期输出：**
```
Loaded image: postgres:15-alpine
Loaded image: redis:7-alpine
Loaded image: python:3.11-slim
Loaded image: nginx:alpine
Loaded image: uma-audit5-backend:latest
```

---

### 第四步：验证镜像加载成功
```bash
docker images | grep -E "python|postgres|redis|nginx|uma-audit"
```

**预期输出：**
```
uma-audit5-backend    latest    xxxxx    x days ago    xxx MB
python                3.11-slim xxxxx    x days ago    xxx MB
postgres              15-alpine xxxxx    x days ago    xxx MB
redis                 7-alpine  xxxxx    x days ago    xxx MB
nginx                 alpine    xxxxx    x days ago    xxx MB
```

---

### 第五步：检查docker-compose配置
```bash
# 查看docker-compose配置
cat docker-compose.yml

# 验证配置文件语法
docker-compose config
```

---

### 第六步：启动所有服务
```bash
# 停止可能存在的旧容器
docker-compose down

# 启动所有服务（后台运行）
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

**按 Ctrl+C 退出日志查看**

---

### 第七步：检查服务状态
```bash
# 查看所有容器状态
docker-compose ps

# 预期输出（所有服务都应该是 Up 状态）
# NAME                   STATUS              PORTS
# uma-audit5-backend     Up x seconds       0.0.0.0:8000->8000/tcp
# uma-audit5-postgres    Up x seconds       5432/tcp
# uma-audit5-redis       Up x seconds       6379/tcp
```

---

### 第八步：验证服务健康状态
```bash
# 等待服务完全启动（约10-15秒）
sleep 15

# 测试健康检查接口
curl http://localhost:8000/api/v1/health

# 预期输出：
# {"status":"healthy","timestamp":"2025-01-20T..."}

# 从外部访问测试
curl http://8.136.59.48:8000/api/v1/health
```

---

### 第九步：查看详细日志（如有问题）
```bash
# 查看后端服务日志
docker-compose logs backend

# 查看最近100行日志
docker-compose logs --tail=100 backend

# 实时跟踪日志
docker-compose logs -f backend

# 查看数据库日志
docker-compose logs postgres

# 查看Redis日志
docker-compose logs redis
```

---

### 第十步：验证数据库连接
```bash
# 进入数据库容器
docker-compose exec postgres psql -U uma_audit -d uma_audit

# 在psql中执行
\l              # 列出所有数据库
\dt             # 列出所有表
\q              # 退出
```

---

## 🔧 故障排查

### 问题1：容器启动失败
```bash
# 查看详细错误日志
docker-compose logs backend

# 检查端口占用
netstat -tlnp | grep 8000

# 重新构建并启动
docker-compose down
docker-compose up -d --build
```

### 问题2：数据库连接失败
```bash
# 检查数据库容器是否运行
docker-compose ps postgres

# 测试数据库连接
docker-compose exec postgres pg_isready -U uma_audit

# 查看数据库日志
docker-compose logs postgres
```

### 问题3：.env配置错误
```bash
# 检查.env文件中的密码是否匹配
grep POSTGRES_PASSWORD .env
grep REDIS_PASSWORD .env

# 确保没有多余的空格或特殊字符
cat -A .env | grep PASSWORD
```

---

## 🎯 部署成功验证清单

- [ ] Docker镜像加载成功（5个镜像）
- [ ] .env文件配置正确
- [ ] docker-compose.yml配置验证通过
- [ ] 所有容器启动成功（docker-compose ps 显示 Up）
- [ ] 健康检查接口返回成功
- [ ] 数据库连接正常
- [ ] 可以从外部访问 http://8.136.59.48:8000
- [ ] 防火墙端口已开放（8000, 3000）

---

## 🌐 防火墙配置（阿里云安全组）

如果无法从外部访问，需要在阿里云控制台配置安全组规则：

1. 登录阿里云控制台
2. 进入 ECS 实例 → 安全组
3. 添加入方向规则：
   - 端口：8000/8000 (后端API)
   - 端口：3000/3000 (前端，如有)
   - 授权对象：0.0.0.0/0
   - 协议：TCP

---

## 📞 常用管理命令

```bash
# 查看所有容器
docker-compose ps

# 重启某个服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 启动所有服务
docker-compose up -d

# 查看资源使用情况
docker stats

# 进入后端容器
docker-compose exec backend bash

# 清理未使用的镜像和容器
docker system prune -a
```

---

**部署文档生成时间：** 2025-01-20
**服务器IP：** 8.136.59.48
**项目目录：** /opt/uma-audit5
