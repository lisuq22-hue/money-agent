@echo off
echo =============================
echo 🤖 启动赚钱Agent
echo =============================

cd /d "%~dp0"

echo.
echo [检查] 宪法文件...
if not exist constitution.md (
    echo ❌ 宪法文件缺失！
    pause
    exit /b 1
)

echo [检查] 配置文件...
if not exist .env (
    echo ❌ 未找到.env文件，请先复制.env.example并填入配置
    pause
    exit /b 1
)

echo [启动] Agent...
echo.

python -m agent.main

echo.
echo Agent已停止。
pause
