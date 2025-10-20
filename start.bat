@echo off
chcp 65001 > nul
echo 🚀 造价材料审计系统 - 一键启动脚本
echo =================================

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未检测到Docker，请先安装Docker Desktop
    echo 📥 下载地址：https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

REM 检查Docker是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：Docker未运行，请启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过

REM 进入脚本所在目录
cd /d "%~dp0"

echo 🔧 正在启动系统组件...

REM 启动所有服务
docker-compose up -d

echo ⏳ 等待服务启动（大约30-60秒）...

REM 等待服务启动
timeout /t 30 /nobreak >nul

echo.
echo 🎉 系统启动成功！
echo =================================
echo 📋 访问地址：
echo    • API文档界面：http://localhost:8000/api/docs
echo    • 系统健康检查：http://localhost:8000/health
echo    • API根地址：http://localhost:8000/api/v1/
echo.
echo 🔧 管理命令：
echo    • 查看日志：docker-compose logs -f
echo    • 停止系统：docker-compose down
echo    • 重启系统：docker-compose restart
echo.
echo 📖 使用说明请参考 README.md 文件
echo.

REM 尝试自动打开浏览器
echo 🌐 正在打开API文档界面...
start http://localhost:8000/api/docs

echo.
pause