# MCP 客户端配置教程

本教程介绍如何将 Burp API MCP Server 连接到各种 MCP 客户端。

---

## 📋 前置条件

- MCP 服务端已启动并运行在 http://localhost:8000
- 支持的 MCP 客户端

---

## 🖥️ Claude Desktop

### 配置方法

1. **打开 Claude Desktop 配置文件**

   **Windows:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

   **Mac:**
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

   **Linux:**
   ```
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **编辑配置文件**

   添加以下配置（替换为你的实际路径）：

   ```json
   {
     "mcpServers": {
       "burp-api": {
         "command": "uv",
         "args": [
           "run",
           "--cwd",
           "C:\\Users\\YourName\\path\\to\\burp-api-mcp",
           "python",
           "scripts/run_server.py"
         ]
       }
     }
   }
   ```

3. **重启 Claude Desktop**

4. **验证连接**

   在 Claude 中输入：
   ```
   请帮我搜索 Burp Suite API 中关于 HttpRequest 的接口
   ```

### HTTP SSE 模式（如果 Claude 支持）

如果 Claude Desktop 支持 HTTP SSE 传输：

```json
{
  "mcpServers": {
    "burp-api": {
      "transport": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

---

## 🖥️ Cursor

### 配置方法

1. **打开 Cursor 设置**

   点击左下角齿轮图标 → MCP Servers

2. **添加 MCP Server**

   点击 "Add MCP Server"

3. **填写配置**

   - **Name**: `burp-api`
   - **Type**: `sse`
   - **URL**: `http://localhost:8000/sse`

4. **保存并测试**

   在 Cursor 聊天框中测试：
   ```
   @burp-api 帮我找一下 HttpRequest 接口的所有方法
   ```

---

## 🖥️ Continue

### 配置方法

1. **打开 Continue 配置文件**

   点击左侧面板 Continue 图标 → 设置 → config.json

2. **添加 MCP 配置**

   ```json
   {
     "models": [...],
     "contextProviders": [...],
     "mcpServers": [
       {
         "name": "burp-api",
         "transport": "sse",
         "url": "http://localhost:8000/sse"
       }
     ]
   }
   ```

3. **重新加载 Continue**

4. **使用方式**

   在对话中使用 `@burp-api` 调用工具

---

## 🖥️ 其他支持 MCP 的 IDE

### VS Code + MCP 扩展

安装 MCP 扩展后，在设置中添加：

```json
{
  "mcp.servers": [
    {
      "name": "burp-api",
      "url": "http://localhost:8000/sse"
    }
  ]
}
```

### 通用 SSE 连接方式

任何支持 HTTP SSE 的客户端都可以直接连接：

```
Endpoint: http://localhost:8000/sse
Method: GET
Transport: Server-Sent Events (SSE)
```

---

## 🔌 STDIO 模式（备用）

如果客户端不支持 HTTP SSE，可以使用 STDIO 模式：

### 配置示例

```json
{
  "mcpServers": {
    "burp-api": {
      "command": "uv",
      "args": [
        "run",
        "--cwd",
        "/path/to/burp-api-mcp",
        "python",
        "scripts/run_server.py"
      ]
    }
  }
}
```

**注意**：STDIO 模式会在每次连接时重新启动服务器，HTTP SSE 模式更推荐。

---

## 🧪 连接测试

配置完成后，使用以下提示词测试连接：

### 测试 1：基础查询
```
请帮我搜索 Burp Suite API 中关于 HttpRequest 的接口信息
```

### 测试 2：获取详情
```
请详细介绍一下 HttpRequest 接口的所有方法
```

### 测试 3：方法签名
```
我想知道 HttpRequest 接口中 withBody 方法的参数和返回值
```

---

## ⚠️ 常见问题

### 连接失败

**现象**: 客户端提示无法连接到 MCP server

**解决方案**:
1. 确认服务端已启动：`curl http://localhost:8000/health`
2. 检查端口是否被占用
3. 检查防火墙设置

### 权限错误

**现象**: Windows 提示权限不足

**解决方案**:
- 以管理员身份运行终端
- 检查文件路径是否正确

### uv 未找到

**现象**: 提示 'uv' 不是内部或外部命令

**解决方案**:
1. 确认 uv 已安装：`uv --version`
2. 将 uv 添加到系统 PATH
3. 使用完整路径：`C:\Users\...\.cargo\bin\uv.exe`

---

## 📚 相关文档

- [快速上手指南](QUICKSTART.md)
- [API 使用教程](API_USAGE.md)
- [故障排除指南](TROUBLESHOOTING.md)

---

## 🤝 支持的客户端

目前已测试通过的客户端：

- ✅ Claude Desktop
- ✅ Cursor
- ✅ Continue
- ✅ 任何支持 HTTP SSE 的 MCP 客户端

如果你在其他客户端上成功连接，欢迎提交 PR 补充！
