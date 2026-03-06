# 快速上手指南

**预计时间**: 5 分钟  
**目标**: 启动 MCP 服务端并成功查询 API 文档

---

## 📋 前置要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 包管理器

### 安装 uv

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 🚀 一键启动

### 1. 进入项目目录

```bash
cd burp-api-mcp
```

### 2. 运行启动脚本

根据你的系统选择对应的脚本：

**Windows (CMD):**
```bash
start.bat
```

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Linux / Mac:**
```bash
chmod +x start.sh
./start.sh
```

### 3. 等待启动完成

你会看到类似输出：

```
╔══════════════════════════════════════════════════════════════╗
║  🚀 启动 MCP Server...                                       ║
║                                                              ║
║  服务地址: http://0.0.0.0:8000                               ║
║  MCP SSE:  http://0.0.0.0:8000/sse                          ║
╚══════════════════════════════════════════════════════════════╝

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**✅ 成功！** 服务已在 http://localhost:8000 运行

---

## 🧪 验证服务

打开浏览器或使用 curl 测试：

```bash
# 检查服务状态
curl http://localhost:8000/

# 预期输出：
# {
#   "service": "Burp Suite Montoya API MCP Server",
#   "version": "1.0.0",
#   "sse_endpoint": "/sse",
#   "database": "D:\\...\\burp_api.db"
# }
```

```bash
# 健康检查
curl http://localhost:8000/health

# 预期输出：
# {"status": "healthy", "database": "connected"}
```

---

## 🔍 首次查询测试

### 方法 1: 使用浏览器访问 SSE 端点

打开浏览器访问：
```
http://localhost:8000/sse
```

### 方法 2: 使用 MCP Inspector（推荐）

安装 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 进行交互式测试：

```bash
npx @modelcontextprotocol/inspector node build/index.js
```

### 方法 3: 直接调用工具（示例）

使用任何支持 SSE 的 HTTP 客户端发送 JSON-RPC 请求。

---

## 📚 下一步

- 🔗 连接 [Claude Desktop](MCP_CLIENT_SETUP.md#claude-desktop)
- 🔗 连接 [Cursor](MCP_CLIENT_SETUP.md#cursor)
- 🔗 学习 [API 查询方法](API_USAGE.md)
- 🔗 查看 [故障排除](TROUBLESHOOTING.md)

---

## ⚡ 常用命令速查

```bash
# 手动启动（不使用脚本）
uv run python scripts/run_server.py

# 重新构建数据库
rm burp_api.db
uv run python scripts/parse_and_import.py

# 停止服务
# 按 Ctrl+C
```

---

## 🎉 恭喜！

你现在已经成功启动了 Burp Suite Montoya API MCP Server！

接下来可以：
1. 连接你常用的 MCP 客户端
2. 开始查询 Burp Suite API 文档
3. 开发你的 Burp Suite 扩展

---

**需要帮助？** 查看 [故障排除指南](TROUBLESHOOTING.md) 或提交 Issue。
