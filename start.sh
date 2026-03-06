#!/bin/bash

# =====================================================
# Burp Suite Montoya API MCP Server - Linux/Mac Launcher
# =====================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR=".venv"
PYTHON_CMD="$VENV_DIR/bin/python"
UV_CMD="uv"
DB_FILE="burp_api.db"
SERVER_PORT=8000

# Change to script directory
cd "$SCRIPT_DIR"

# Print banner
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║${NC}   ${BOLD}Burp Suite Montoya API MCP Server Launcher${NC}             ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}   一键启动脚本 - Linux/Mac 版本                            ${BLUE}║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if uv is installed
print_status "检查 uv 安装..."
if ! command -v $UV_CMD &> /dev/null; then
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║${NC}  ⚠️  错误：未检测到 uv 包管理器                          ${YELLOW}║${NC}"
    echo -e "${YELLOW}║                                                            ║${NC}"
    echo -e "${YELLOW}║${NC}  请先安装 uv：                                           ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}                                                            ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}  ${BOLD}Linux/Mac:${NC}                                               ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}  curl -LsSf https://astral.sh/uv/install.sh | sh        ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}                                                            ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}  或访问：                                                  ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}  https://docs.astral.sh/uv/getting-started/             ${YELLOW}║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi
print_ok "uv 已安装 ($($UV_CMD --version))"

# Check/create virtual environment
print_status "检查虚拟环境..."
if [ ! -d "$VENV_DIR" ]; then
    print_status "虚拟环境不存在，正在创建..."
    $UV_CMD venv
    if [ $? -ne 0 ]; then
        print_error "创建虚拟环境失败"
        exit 1
    fi
    print_ok "虚拟环境创建完成"
else
    print_ok "虚拟环境已存在"
fi

# Check Python
if [ ! -f "$PYTHON_CMD" ]; then
    print_error "虚拟环境中的 Python 不存在"
    print_status "尝试重新创建虚拟环境..."
    rm -rf "$VENV_DIR"
    $UV_CMD venv
fi

# Install/update dependencies
print_status "安装/更新依赖..."
$UV_CMD sync
if [ $? -ne 0 ]; then
    print_error "依赖安装失败"
    exit 1
fi
print_ok "依赖安装完成"

# Check database
print_status "检查数据库文件..."
if [ ! -f "$DB_FILE" ]; then
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║${NC}  🗄️  数据库文件不存在，需要构建                          ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}  这将解析所有 Java API 文件并创建索引...                 ${YELLOW}║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_status "正在构建数据库，请稍候..."
    
    $UV_CMD run python scripts/parse_and_import.py
    
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║${NC}  ❌ 数据库构建失败                                        ${RED}║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  ✅ 数据库构建完成！                                      ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
else
    print_ok "数据库文件已存在: $DB_FILE"
fi

# Check if port is in use
print_status "检查端口 $SERVER_PORT 是否被占用..."
if lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t > /dev/null 2>&1; then
    PID=$(lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t)
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║${NC}  ⚠️  警告：端口 $SERVER_PORT 已被占用                    ${YELLOW}║${NC}"
    echo -e "${YELLOW}║                                                            ║${NC}"
    echo -e "${YELLOW}║${NC}  占用进程 PID: $PID                                      ${YELLOW}║${NC}"
    echo -e "${YELLOW}║                                                            ║${NC}"
    echo -e "${YELLOW}║${NC}  请：                                                     ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}  1. 关闭占用该端口的程序                                  ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}  2. 或修改 scripts/run_server.py 中的端口配置           ${YELLOW}║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi
print_ok "端口 $SERVER_PORT 可用"

# Start server
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  🚀 启动 MCP Server...                                    ${GREEN}║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║${NC}  服务地址: http://localhost:$SERVER_PORT                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  MCP SSE:  http://localhost:$SERVER_PORT/sse             ${GREEN}║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║${NC}  按 Ctrl+C 停止服务                                      ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Trap Ctrl+C to show exit message
trap 'echo ""; echo -e "${BLUE}[INFO]${NC} 服务已停止"; echo ""; exit 0' INT

# Start the server
$UV_CMD run python scripts/run_server.py

# If server exits with error
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║${NC}  ❌ 服务器异常退出                                        ${RED}║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_error "错误代码: $EXIT_CODE"
    exit $EXIT_CODE
fi
