# 🍎 Mac用户启动指南

## 快速启动方法

### 方法一：终端命令启动（推荐）
1. 打开终端（Applications > Utilities > Terminal）
2. 复制粘贴以下命令：
```bash
cd /Users/crj/Documents/code/uma-audit4
chmod +x start.sh
./start.sh
```

### 方法二：一键启动命令
如果方法一有问题，直接运行：
```bash
cd /Users/crj/Documents/code/uma-audit4
docker-compose up -d
```

### 方法三：检查系统状态
```bash
cd /Users/crj/Documents/code/uma-audit4
chmod +x check.sh
./check.sh
```

## 访问系统

启动成功后，在浏览器打开：
- **API文档**: http://localhost:8000/api/docs
- **系统健康检查**: http://localhost:8000/health

## 常用管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止系统
docker-compose down

# 重启系统  
docker-compose restart
```

## 故障排除

如果启动失败，请检查：
1. Docker Desktop是否安装并运行
2. 端口8000是否被占用
3. 网络连接是否正常

运行检查脚本可以帮您诊断问题：
```bash
./check.sh
```