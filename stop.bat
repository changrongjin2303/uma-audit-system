@echo off
chcp 65001 > nul
echo 🛑 造价材料审计系统 - 停止服务
echo =================================

REM 进入脚本所在目录
cd /d "%~dp0"

echo 🔧 正在停止所有服务...

REM 停止所有服务
docker-compose down

echo ✅ 系统已停止

echo.
echo 💡 提示：
echo    • 重新启动系统：双击 start.bat
echo    • 查看服务状态：docker-compose ps
echo.

pause