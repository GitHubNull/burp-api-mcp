@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: =====================================================
:: Burp Suite Montoya API MCP Server - Windows Launcher
:: =====================================================

title Burp API MCP Server Launcher

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║                                                       ║
echo ║   Burp Suite Montoya API MCP Server Launcher         ║
echo ║   一键启动脚本 - Windows CMD 版本                    ║
echo ║                                                       ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 配置
echo [INFO] 正在检查配置...
set "VENV_DIR=.venv"
set "PYTHON_CMD=%VENV_DIR%\Scripts\python.exe"
set "UV_CMD=uv"
set "DB_FILE=burp_api.db"
set "SERVER_PORT=8000"

:: 检查 uv 是否安装
echo [INFO] 检查 uv 安装...
where %UV_CMD% >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║  ⚠️  错误：未检测到 uv 包管理器                      ║
    echo ║                                                       ║
    echo ║  请先安装 uv：                                        ║
    echo ║  PowerShell:                                          ║
    echo ║  irm https://astral.sh/uv/install.ps1 | iex        ║
    echo ║                                                       ║
    echo ║  或访问：https://docs.astral.sh/uv/getting-started/ ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)
echo [OK] uv 已安装

:: 检查虚拟环境
echo [INFO] 检查虚拟环境...
if not exist "%VENV_DIR%" (
    echo [INFO] 虚拟环境不存在，正在创建...
    %UV_CMD% venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [OK] 虚拟环境创建完成
) else (
    echo [OK] 虚拟环境已存在
)

:: 检查 Python
if not exist "%PYTHON_CMD%" (
    echo [ERROR] 虚拟环境中的 Python 不存在
    echo [INFO] 尝试重新创建虚拟环境...
    rmdir /s /q "%VENV_DIR%"
    %UV_CMD% venv
)

:: 安装依赖
echo [INFO] 安装/更新依赖...
%UV_CMD% sync
if %ERRORLEVEL% neq 0 (
    echo [ERROR] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖安装完成

:: 检查数据库
echo [INFO] 检查数据库文件...
if not exist "%DB_FILE%" (
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║  🗄️  数据库文件不存在，需要构建                      ║
    echo ║  这将解析所有 Java API 文件并创建索引...             ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
    echo [INFO] 正在构建数据库，请稍候...
    
    %UV_CMD% run python scripts\parse_and_import.py
    
    if %ERRORLEVEL% neq 0 (
        echo.
        echo ╔═══════════════════════════════════════════════════════╗
        echo ║  ❌ 数据库构建失败                                    ║
        echo ╚═══════════════════════════════════════════════════════╝
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║  ✅ 数据库构建完成！                                  ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
) else (
    echo [OK] 数据库文件已存在: %DB_FILE%
)

:: 检查端口占用
echo [INFO] 检查端口 %SERVER_PORT% 是否被占用...
netstat -ano | findstr ":%SERVER_PORT%" | findstr "LISTENING" >nul
if %ERRORLEVEL% equ 0 (
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║  ⚠️  警告：端口 %SERVER_PORT% 已被占用               ║
    echo ║                                                       ║
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%SERVER_PORT%" ^| findstr "LISTENING"') do (
        echo ║  占用进程 PID: %%a                                    ║
    )
    echo ║                                                       ║
    echo ║  请：                                                ║
    echo ║  1. 关闭占用该端口的程序                             ║
    echo ║  2. 或修改 scripts\run_server.py 中的端口配置        ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)
echo [OK] 端口 %SERVER_PORT% 可用

:: 启动服务器
echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║  🚀 启动 MCP Server...                                ║
echo ║                                                       ║
echo ║  服务地址: http://localhost:%SERVER_PORT%             ║
echo ║  MCP SSE:  http://localhost:%SERVER_PORT%/sse        ║
echo ║                                                       ║
echo ║  按 Ctrl+C 停止服务                                  ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

:: 启动服务器
%UV_CMD% run python scripts\run_server.py

:: 如果服务器异常退出
if %ERRORLEVEL% neq 0 (
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║  ❌ 服务器异常退出                                    ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
    echo [INFO] 错误代码: %ERRORLEVEL%
    pause
)

echo.
echo [INFO] 服务已停止
echo.

endlocal
