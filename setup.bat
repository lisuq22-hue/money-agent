@echo off
echo =============================
echo 赚钱Agent - 一键安装
echo =============================

echo.
echo [1/3] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.12+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python已就绪

echo.
echo [2/3] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

echo.
echo [3/3] 创建.env文件...
if not exist .env (
    copy .env.example .env
    echo ⚠️ 请编辑 .env 文件，填入你的Token和密钥
    echo    文件位置: %CD%\.env
) else (
    echo ✅ .env 已存在
)

echo.
echo =============================
echo ✅ 安装完成！
echo.
echo 下一步:
echo   1. 编辑 .env 文件，填入你的配置
echo   2. 运行 run.bat 启动Agent
echo =============================
pause
