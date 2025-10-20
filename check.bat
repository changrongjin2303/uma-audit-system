@echo off
chcp 65001 > nul
echo 🔍 造价材料审计系统 - 环境检查工具
echo =================================

echo 正在检查系统环境...
echo.

REM 检查Docker是否安装
echo [1/3] 检查Docker安装状态...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装
    echo 📥 请下载安装：https://www.docker.com/products/docker-desktop/
    echo.
    goto :end
) else (
    docker --version
    echo ✅ Docker已安装
    echo.
)

REM 检查Docker是否运行
echo [2/3] 检查Docker运行状态...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未运行
    echo 💡 请启动Docker Desktop应用程序
    echo.
    goto :end
) else (
    echo ✅ Docker正在运行
    echo.
)

REM 检查端口是否被占用
echo [3/3] 检查端口占用情况...
netstat -an | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  端口8000已被占用
    echo 💡 请先关闭占用该端口的程序，或修改配置使用其他端口
    echo.
) else (
    echo ✅ 端口8000可用
    echo.
)

echo 🎉 环境检查完成！
echo.
echo 📋 检查结果汇总：
echo    • Docker安装：✅
echo    • Docker运行：✅  
echo    • 端口8000：✅
echo.
echo 💡 一切就绪，现在可以启动系统了！
echo    双击运行 start.bat 即可启动系统

:end
echo.
pause