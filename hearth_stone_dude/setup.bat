@echo off
echo ========================================
echo 炉石传说记牌器 - 环境设置脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查虚拟环境...
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
) else (
    echo [信息] 虚拟环境已存在
)

echo.
echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [3/4] 安装 Python 依赖...
pip install -r requirements.txt

echo.
echo [4/4] 安装 Node.js 依赖...
cd overlay
call npm install
cd ..

echo.
echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 启动后端: start_backend.bat
echo 启动前端: start_overlay.bat
echo.
pause
