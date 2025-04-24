@echo off
echo 正在启动日本签证材料清单生成器...

:: 检查Python是否已安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.7或更高版本。
    pause
    exit /b 1
)

:: 检查是否存在虚拟环境
if not exist venv (
    echo 正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 错误: 创建虚拟环境失败。
        pause
        exit /b 1
    )
)

:: 激活虚拟环境并安装依赖
echo 正在准备环境...
call venv\Scripts\activate
pip install -r requirements.txt

:: 启动应用
echo 正在启动应用...
python app.py

:: 如果应用异常退出
if %errorlevel% neq 0 (
    echo 应用异常退出，退出代码: %errorlevel%
    pause
)

:: 退出虚拟环境
call venv\Scripts\deactivate.bat 