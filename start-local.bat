@echo off
chcp 65001 >nul
setlocal
title 研英智学 · 本地启动

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [错误] 没有找到 .venv 虚拟环境，请先执行：
  echo     python -m venv .venv
  echo     .venv\Scripts\python.exe -m pip install -r server\requirements.txt
  echo     cd server ^&^& ..\.venv\Scripts\python.exe scripts\setup_team.py
  pause
  exit /b 1
)

echo [1/3] 启动后端 FastAPI：http://127.0.0.1:8000
start "kaoyan-backend" /D "%~dp0server" cmd /k "..\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000"

echo [2/3] 等待后端就绪 ...
timeout /t 4 /nobreak >nul

echo [3/3] 启动前端 Vite：http://localhost:5173
start "kaoyan-web" /D "%~dp0web" cmd /k "npm run dev"

timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo 已打开浏览器。两个命令行窗口分别是后端和前端，关闭窗口即停止服务。
echo 后端接口文档：http://127.0.0.1:8000/docs
echo.
pause
