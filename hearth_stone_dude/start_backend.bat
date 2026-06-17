@echo off
echo 正在启动炉石传说记牌器后端...
echo.

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 启动服务
python -m backend.api_server

pause
