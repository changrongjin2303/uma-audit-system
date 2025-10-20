# 造价审计系统 - 阿里云部署资源包

## 📦 部署文档和脚本说明

本目录包含了将造价审计系统部署到阿里云服务器所需的所有文档和自动化脚本。

---

## 📚 文档清单

### 1. 📖 阿里云部署指南.md
**完整的部署教程,专为非技术人员编写**

包含内容:
- ✅ 如何购买和配置阿里云服务器
- ✅ 详细的SSH连接步骤 (Windows/Mac)
- ✅ 逐步的安装和配置说明
- ✅ 域名和HTTPS配置教程
- ✅ 日常维护和故障排查指南
- ✅ 数据备份和恢复方法

**适合**: 第一次部署,需要详细步骤指导

### 2. 📋 部署快速参考.md
**快速查询手册,适合日常维护**

包含内容:
- ⚡ 常用命令速查表
- ⚡ 故障排查快速指南
- ⚡ 监控和维护命令
- ⚡ 紧急情况处理流程

**适合**: 已经部署完成,日常运维使用

---

## 🛠️ 自动化脚本

### 1. deploy-to-aliyun.sh
**一键部署脚本**

功能:
- ✅ 自动检查和安装Docker环境
- ✅ 生成安全的密码和密钥
- ✅ 创建生产环境配置文件
- ✅ 构建Docker镜像并启动所有服务
- ✅ 初始化数据库

使用方法:
```bash
cd /opt/uma-audit5
./deploy-to-aliyun.sh
```

### 2. backup-data.sh
**数据备份脚本**

功能:
- ✅ 备份PostgreSQL数据库
- ✅ 备份上传文件
- ✅ 备份配置文件
- ✅ 自动清理30天前的旧备份

使用方法:
```bash
cd /opt/uma-audit5
./backup-data.sh
```

设置自动备份:
```bash
crontab -e
# 添加: 0 2 * * * /opt/uma-audit5/backup-data.sh
```

### 3. health-check.sh
**系统健康检查脚本**

功能:
- ✅ 检查Docker服务状态
- ✅ 检查所有容器运行情况
- ✅ 检查端口监听
- ✅ 检查数据库和Redis连接
- ✅ 检查磁盘和内存使用
- ✅ 检查错误日志

使用方法:
```bash
cd /opt/uma-audit5
./health-check.sh
```

设置定时检查:
```bash
crontab -e
# 添加: */30 * * * * /opt/uma-audit5/health-check.sh >> /var/log/uma-health.log
```

---

## 🚀 快速开始

### 准备工作

1. **购买阿里云ECS服务器**
   - 配置: 4核8G内存 (推荐) 或 2核4G (最低)
   - 操作系统: Ubuntu 22.04 64位
   - 带宽: 3-5Mbps
   - 记录服务器IP和root密码

2. **配置安全组**
   - 开放端口: 22, 80, 443, 8000
   - 在阿里云控制台设置

3. **准备项目代码**
   - 将整个项目文件夹上传到服务器 `/opt/uma-audit5` 目录

### 部署步骤

#### 方式一: 使用一键部署脚本 (推荐)

```bash
# 1. SSH连接到服务器
ssh root@你的服务器IP

# 2. 进入项目目录
cd /opt/uma-audit5

# 3. 运行部署脚本
./deploy-to-aliyun.sh

# 4. 按照提示输入必要信息
# 5. 等待部署完成
# 6. 访问 http://你的服务器IP
```

#### 方式二: 手动部署

请参考 `阿里云部署指南.md` 中的详细步骤。

---

## 📋 部署后检查清单

部署完成后,请逐项检查:

- [ ] 所有Docker容器都在运行
  ```bash
  docker-compose -f docker-compose.prod.yml ps
  ```

- [ ] 可以访问前端页面
  ```
  http://你的服务器IP
  ```

- [ ] 可以访问后端API文档
  ```
  http://你的服务器IP:8000/docs
  ```

- [ ] 可以正常登录系统

- [ ] 数据库连接正常
  ```bash
  docker exec uma_audit_db_prod pg_isready -U postgres
  ```

- [ ] Redis缓存正常
  ```bash
  docker exec uma_audit_redis_prod redis-cli ping
  ```

- [ ] 运行健康检查
  ```bash
  ./health-check.sh
  ```

- [ ] 设置自动备份
  ```bash
  crontab -e
  # 添加: 0 2 * * * /opt/uma-audit5/backup-data.sh
  ```

---

## 🔧 日常运维

### 每日检查

```bash
# 1. 查看系统健康状态
./health-check.sh

# 2. 查看服务运行状态
docker-compose -f docker-compose.prod.yml ps

# 3. 查看错误日志
docker-compose -f docker-compose.prod.yml logs | grep -i error
```

### 每周维护

```bash
# 1. 检查磁盘空间
df -h

# 2. 检查备份文件
ls -lh /opt/backups/uma-audit/

# 3. 清理Docker缓存
docker system prune -a
```

### 每月维护

```bash
# 1. 更新系统
apt update && apt upgrade -y

# 2. 检查SSL证书有效期
certbot certificates

# 3. 查看系统资源使用趋势

# 4. 检查日志文件大小
du -sh ./backend/logs
```

---

## 🆘 常见问题

### Q1: 部署脚本执行失败怎么办?

**A**: 查看错误信息,常见原因:
- Docker未安装: 手动安装 `curl -fsSL https://get.docker.com | bash`
- 端口被占用: 停止占用端口的服务
- 权限不足: 使用root用户执行

### Q2: 网站访问不了怎么办?

**A**: 检查步骤:
```bash
# 1. 检查容器是否运行
docker ps

# 2. 检查端口是否监听
netstat -tuln | grep 80

# 3. 检查防火墙
ufw status

# 4. 检查阿里云安全组设置
```

### Q3: 如何查看详细日志?

**A**:
```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs

# 查看后端日志
docker-compose -f docker-compose.prod.yml logs backend

# 实时查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### Q4: 如何备份数据?

**A**:
```bash
# 使用备份脚本
./backup-data.sh

# 手动备份数据库
docker exec uma_audit_db_prod pg_dump -U postgres uma_audit > backup.sql
```

### Q5: 如何更新系统?

**A**:
```bash
# 拉取最新代码 (Git)
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 运行数据库迁移
docker exec -it uma_audit_backend_prod python -m alembic upgrade head
```

### Q6: 内存或磁盘不足怎么办?

**A**:
```bash
# 清理Docker
docker system prune -a --volumes

# 清理日志
find ./backend/logs -name "*.log" -mtime +7 -delete

# 清理旧备份
find /opt/backups -mtime +30 -delete

# 如仍不够,在阿里云控制台扩容
```

---

## 📞 获取支持

### 查看文档

1. 详细部署步骤: `阿里云部署指南.md`
2. 快速参考: `部署快速参考.md`
3. 项目文档: `CLAUDE.md`
4. API文档: `http://服务器IP:8000/docs`

### 诊断信息收集

遇到问题时,请收集以下信息:

```bash
# 1. 系统信息
uname -a
cat /etc/os-release

# 2. Docker信息
docker --version
docker-compose --version

# 3. 容器状态
docker ps -a

# 4. 服务日志
docker-compose -f docker-compose.prod.yml logs --tail=100

# 5. 资源使用
free -h
df -h

# 6. 错误信息
docker-compose -f docker-compose.prod.yml logs | grep -i error
```

---

## 🎯 部署目标

- ✅ 系统稳定运行,可用性 >99%
- ✅ 支持多用户并发访问
- ✅ 数据安全,定期自动备份
- ✅ 快速响应,页面加载 <3秒
- ✅ 易于维护,问题快速定位
- ✅ 可扩展,支持未来升级

---

## 📊 性能指标

### 服务器配置对应能力

**2核4G配置**:
- 并发用户: 20-50人
- 处理材料: 10,000条/次
- 适合场景: 小团队使用

**4核8G配置** (推荐):
- 并发用户: 50-100人
- 处理材料: 50,000条/次
- 适合场景: 中小企业

**8核16G配置**:
- 并发用户: 100-200人
- 处理材料: 100,000条/次
- 适合场景: 大型企业

---

## 🔐 安全建议

1. **及时更新密码**
   - 定期修改数据库密码
   - 定期修改Redis密码
   - 定期修改管理员账号密码

2. **配置HTTPS**
   - 申请SSL证书
   - 强制HTTPS访问
   - 定期续期证书

3. **限制访问**
   - 配置防火墙规则
   - 仅开放必要端口
   - 使用VPN或堡垒机

4. **数据备份**
   - 每日自动备份
   - 异地备份存储
   - 定期测试恢复

5. **监控告警**
   - 设置资源监控
   - 配置错误告警
   - 定期查看日志

---

## 📝 更新记录

**v1.0** (2025-01-20)
- ✅ 创建完整部署指南
- ✅ 开发一键部署脚本
- ✅ 创建备份和健康检查脚本
- ✅ 编写快速参考手册

---

**祝您部署顺利! 🎉**

如有任何问题,请查阅详细文档或查看系统日志进行排查。
