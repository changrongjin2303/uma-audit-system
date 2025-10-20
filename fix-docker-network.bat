@echo off
echo ====================================
echo     Docker网络问题修复工具
echo ====================================
echo.

echo 🔍 检查Docker状态...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装或未启动
    echo 请先启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker已安装

echo 📝 备份当前Docker配置...
if exist "%USERPROFILE%\.docker\daemon.json" (
    copy "%USERPROFILE%\.docker\daemon.json" "%USERPROFILE%\.docker\daemon.json.backup"
    echo ✅ 配置文件已备份
)

echo 🇨🇳 配置国内Docker镜像源...
if not exist "%USERPROFILE%\.docker" mkdir "%USERPROFILE%\.docker"

echo {> "%USERPROFILE%\.docker\daemon.json"
echo   "registry-mirrors": [>> "%USERPROFILE%\.docker\daemon.json"
echo     "https://docker.mirrors.ustc.edu.cn",>> "%USERPROFILE%\.docker\daemon.json"
echo     "https://hub-mirror.c.163.com",>> "%USERPROFILE%\.docker\daemon.json"
echo     "https://registry.docker-cn.com",>> "%USERPROFILE%\.docker\daemon.json"
echo     "https://mirror.baidubce.com">> "%USERPROFILE%\.docker\daemon.json"
echo   ],>> "%USERPROFILE%\.docker\daemon.json"
echo   "insecure-registries": [],>> "%USERPROFILE%\.docker\daemon.json"
echo   "debug": false,>> "%USERPROFILE%\.docker\daemon.json"
echo   "experimental": false>> "%USERPROFILE%\.docker\daemon.json"
echo }>> "%USERPROFILE%\.docker\daemon.json"

echo ✅ Docker镜像源配置完成

echo 🔄 重启Docker服务...
echo 请手动重启Docker Desktop，然后按任意键继续...
pause

echo 🧪 测试Docker连接...
echo 正在拉取测试镜像...
docker pull hello-world

if errorlevel 1 (
    echo ❌ 镜像拉取失败，可能需要配置VPN
    echo 请继续下一步配置
) else (
    echo ✅ Docker网络修复成功！
    echo 现在可以运行 start.bat 启动系统了
)

echo.
echo ====================================
echo 修复步骤：
echo 1. ✅ 配置国内镜像源
echo 2. 🔄 需要重启Docker Desktop
echo 3. 🧪 测试连接
echo ====================================

pause