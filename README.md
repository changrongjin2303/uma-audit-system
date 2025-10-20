# 造价材料审计系统 - 快速启动指南

## 系统要求
- Windows 10/11 或 macOS 10.15+ 
- 至少4GB内存
- 至少5GB硬盘空间

## 第一次启动前的准备

### 1. 安装必需软件
请按顺序安装以下软件：

#### 1.1 安装Python 3.9+
- 访问 https://www.python.org/downloads/
- 下载最新的Python 3.9或更高版本
- 安装时**务必勾选**"Add Python to PATH"选项
- 安装完成后，打开命令行输入 `python --version` 验证

#### 1.2 安装PostgreSQL数据库
- 访问 https://www.postgresql.org/download/
- 下载适合你操作系统的版本
- 安装时设置密码为：`password`（后面会用到）
- 记住安装端口（默认5432）

#### 1.3 安装Redis（可选，推荐）
- Windows用户：下载Redis for Windows
- macOS用户：可通过Homebrew安装 `brew install redis`
- 或者跳过此步骤，系统会使用简化模式

### 2. 配置环境文件
复制 `.env.example` 文件并重命名为 `.env`，然后修改以下配置：

```
# 数据库配置（修改这里的password为你设置的数据库密码）
DATABASE_URL=postgresql://postgres:password@localhost:5432/uma_audit

# 如果你有AI服务的API密钥，可以填写（可选）
OPENAI_API_KEY=你的OpenAI密钥
DASHSCOPE_API_KEY=你的通义千问密钥

# 其他配置保持默认即可
```

## 快速启动步骤

### 第1步：打开终端/命令行
- Windows：按Win+R，输入`cmd`，按回车
- macOS：按Cmd+空格，输入`Terminal`，按回车

### 第2步：进入项目目录
```bash
cd /Users/crj/Documents/code/uma-audit4/backend
```

### 第3步：安装依赖包
```bash
pip install -r requirements.txt
```
这一步可能需要几分钟，请耐心等待。

### 第4步：创建数据库
```bash
# 首先创建数据库
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', user='postgres', password='password', port=5432)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('CREATE DATABASE uma_audit;')
print('数据库创建成功！')
cursor.close()
conn.close()
"
```

### 第5步：初始化数据库表
```bash
python -c "
import asyncio
from app.core.database import create_tables
asyncio.run(create_tables())
print('数据库表创建成功！')
"
```

### 第6步：启动系统
```bash
python main.py
```

如果看到以下信息，说明启动成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

## 系统访问方式

启动成功后，你可以通过以下方式访问系统：

### 1. API文档界面（推荐新手使用）
打开浏览器访问：http://localhost:8000/api/docs

这里可以看到所有功能接口，并且可以直接测试。

### 2. 系统健康检查
访问：http://localhost:8000/health
如果看到 `{"status": "healthy"}` 说明系统正常运行。

### 3. API根地址
访问：http://localhost:8000/api/v1/
可以看到系统版本信息。

## 基本功能测试流程

### 测试1：用户注册和登录
1. 在API文档页面找到"认证"部分
2. 先调用 `/auth/register` 接口创建用户账号
3. 再调用 `/auth/login` 接口获取登录令牌
4. 将令牌复制保存，后续接口都需要用到

### 测试2：上传Excel文件
1. 准备一个包含材料清单的Excel文件
2. 使用 `/projects/` 接口创建新项目
3. 使用 `/projects/{project_id}/upload-excel` 上传文件
4. 使用 `/projects/{project_id}/import-materials` 导入材料数据

### 测试3：材料匹配
1. 首先上传一些基准材料数据到 `/base-materials/`
2. 使用 `/matching/{project_id}/match-materials` 进行材料匹配
3. 查看匹配结果

### 测试4：AI价格分析（需要API密钥）
1. 使用 `/analysis/{project_id}/analyze` 进行价格分析
2. 查看分析结果

## 常见问题解决

### 问题1：Python命令不识别
- 确保安装Python时勾选了"Add to PATH"
- 尝试使用 `python3` 而不是 `python`

### 问题2：数据库连接失败
- 确保PostgreSQL服务正在运行
- 检查用户名密码是否正确
- 确认端口号是否为5432

### 问题3：端口被占用
如果8000端口被占用，可以修改 `main.py` 文件的端口号：
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### 问题4：缺少某些依赖包
如果提示缺少包，可以单独安装：
```bash
pip install 包名
```

## 停止系统
在运行系统的命令行窗口按 `Ctrl+C` 即可停止系统。

## 获得帮助
如果遇到问题，请：
1. 查看命令行的错误信息
2. 确认所有软件都正确安装
3. 检查网络连接是否正常
4. 联系技术支持

---
祝你测试顺利！🎉