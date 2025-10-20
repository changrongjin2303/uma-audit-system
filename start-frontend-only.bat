@echo off
echo ====================================
echo     造价审计系统 - 前端演示启动
echo ====================================
echo.

echo 📁 进入前端目录...
cd frontend

echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js环境正常

echo 📦 安装前端依赖包...
call npm install

echo 🚀 启动前端服务...
echo.
echo ====================================
echo  🎉 前端服务启动成功！
echo  🌐 请在浏览器中打开：
echo     http://localhost:3000
echo ====================================
echo.
echo 💡 可以体验的功能：
echo  - 图表演示 (访问 /charts)
echo  - 移动端演示 (访问 /mobile) 
echo  - 系统测试 (访问 /test)
echo  - 所有页面UI界面
echo.
echo ⚠️  注意：这是前端演示模式
echo     使用模拟数据，不连接真实后端
echo.

call npm run dev

pause