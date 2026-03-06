# 故障排除指南

本指南帮助你解决使用 Burp API MCP Server 时可能遇到的问题。

---

## 🔍 问题分类

- [启动问题](#启动问题)
- [数据库问题](#数据库问题)
- [端口问题](#端口问题)
- [客户端连接问题](#客户端连接问题)
- [查询问题](#查询问题)
- [性能问题](#性能问题)

---

## 启动问题

### ❌ 问题：uv 未安装

**错误信息**：
```
'uv' 不是内部或外部命令，也不是可运行的程序或批处理文件。
```

**解决方案**：

1. **安装 uv**

   **Windows (PowerShell):**
   ```powershell
   irm https://astral.sh/uv/install.ps1 | iex
   ```

   **Linux/Mac:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **重启终端**

3. **验证安装**
   ```bash
   uv --version
   ```

4. **添加到 PATH**（如果仍找不到）

   检查 uv 安装位置并添加到系统 PATH：
   - Windows: `%USERPROFILE%\.cargo\bin`
   - Linux/Mac: `~/.cargo/bin`

---

### ❌ 问题：Python 版本不兼容

**错误信息**：
```
requires-python: ">=3.11"
```

**解决方案**：

1. **检查 Python 版本**
   ```bash
   python --version
   ```

2. **安装 Python 3.11+**

   uv 会自动安装，但如果你想使用系统 Python：
   - 下载地址：https://www.python.org/downloads/

3. **使用 uv 安装 Python**
   ```bash
   uv python install 3.11
   ```

---

### ❌ 问题：依赖安装失败

**错误信息**：
```
ERROR: Failed to install dependencies
```

**解决方案**：

1. **清理并重新安装**
   ```bash
   # 删除虚拟环境
   rm -rf .venv  # Linux/Mac
   rmdir /s /q .venv  # Windows CMD
   
   # 重新同步
   uv sync
   ```

2. **检查网络连接**
   - 确保能访问 PyPI
   - 如果使用代理，配置环境变量

3. **手动安装关键依赖**
   ```bash
   uv add fastapi mcp sqlalchemy aiosqlite uvicorn
   ```

---

## 数据库问题

### ❌ 问题：数据库未找到

**现象**：
```json
{
  "database": "Not initialized"
}
```

**解决方案**：

1. **检查数据库文件是否存在**
   ```bash
   ls burp_api.db  # Linux/Mac
   dir burp_api.db  # Windows
   ```

2. **重新构建数据库**
   ```bash
   rm burp_api.db  # 删除旧数据库
   uv run python scripts/parse_and_import.py
   ```

3. **检查权限**
   - 确保有写入权限
   - 检查磁盘空间

---

### ❌ 问题：数据库损坏

**现象**：
```
sqlite3.DatabaseError: database disk image is malformed
```

**解决方案**：

1. **删除并重建**
   ```bash
   rm burp_api.db
   uv run python scripts/parse_and_import.py
   ```

2. **如果重建失败**
   - 检查 Java 源文件是否完整
   - 查看解析日志中的错误

---

### ❌ 问题：数据库构建太慢

**现象**：构建过程超过 5 分钟

**解决方案**：

1. **这是正常的**
   - 首次构建需要解析 186 个接口
   - 通常耗时 1-2 分钟

2. **加快构建**
   - 确保使用 SSD
   - 关闭其他占用资源的程序

---

## 端口问题

### ❌ 问题：端口 8000 被占用

**错误信息**：
```
Address already in use: localhost:8000
```

**解决方案**：

**方法 1：查找并关闭占用进程**

**Windows:**
```powershell
# 查找占用进程
netstat -ano | findstr :8000

# 结束进程（将 <PID> 替换为实际 PID）
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# 查找占用进程
lsof -i :8000

# 结束进程
kill -9 <PID>
```

**方法 2：使用其他端口**

编辑 `scripts/run_server.py`，修改端口：
```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # 改为 8080
```

**方法 3：PowerShell 脚本参数**
```powershell
.\start.ps1 -Port 8080
```

---

### ❌ 问题：防火墙阻止连接

**现象**：服务启动但外部无法访问

**解决方案**：

1. **检查防火墙设置**
   - Windows: 允许 Python 通过防火墙
   - Linux: `sudo ufw allow 8000`

2. **使用 localhost 访问**
   ```
   http://127.0.0.1:8000
   ```

3. **检查绑定地址**
   - 默认绑定 `0.0.0.0`（所有接口）
   - 如需仅本地访问，改为 `127.0.0.1`

---

## 客户端连接问题

### ❌ 问题：Claude Desktop 无法连接

**现象**：Claude 提示无法连接到 MCP server

**解决方案**：

1. **检查配置文件路径**
   ```
   Windows: %APPDATA%\Claude\claude_desktop_config.json
   Mac: ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **验证 JSON 格式**
   - 使用 JSON 验证器检查语法
   - 注意路径中的转义符（Windows 需双反斜杠）

3. **检查路径**
   ```json
   {
     "mcpServers": {
       "burp-api": {
         "command": "uv",
         "args": [
           "run",
           "--cwd",
           "C:\\Users\\YourName\\path\\to\\burp-api-mcp",  // 确保路径正确
           "python",
           "scripts/run_server.py"
         ]
       }
     }
   }
   ```

4. **重启 Claude Desktop**
   - 完全退出（包括系统托盘图标）
   - 重新启动

5. **查看日志**
   ```
   Windows: %APPDATA%\Claude\logs\mcp-server-burp-api.log
   Mac: ~/Library/Logs/Claude/mcp-server-burp-api.log
   ```

---

### ❌ 问题：Cursor 无法连接

**现象**：Cursor 提示 MCP server 连接失败

**解决方案**：

1. **确认使用 SSE 模式**
   ```
   Type: sse
   URL: http://localhost:8000/sse
   ```

2. **检查服务是否运行**
   ```bash
   curl http://localhost:8000/health
   ```

3. **重启 Cursor**

---

### ❌ 问题：连接后立即断开

**现象**：客户端显示连接成功但马上断开

**可能原因**：
1. **uv 路径问题**
   - 使用完整路径指定 uv
   ```json
   "command": "C:\\Users\\...\\.cargo\\bin\\uv.exe"
   ```

2. **权限问题**
   - 以管理员身份运行

3. **Python 环境问题**
   - 确保虚拟环境已创建
   - 重新运行启动脚本

---

## 查询问题

### ❌ 问题：搜索结果为空

**现象**：搜索返回 "No results found"

**解决方案**：

1. **使用模糊搜索**
   ```json
   {
     "query": "request",  // 使用小写关键词
     "type": "all"
   }
   ```

2. **检查数据库**
   ```bash
   # 验证数据库包含数据
   sqlite3 burp_api.db "SELECT COUNT(*) FROM interfaces;"
   # 应返回 186
   ```

3. **扩大搜索范围**
   - 增加 `limit` 参数
   - 使用 `type: "all"`

---

### ❌ 问题：接口未找到

**现象**：`get_interface` 返回 "not found"

**解决方案**：

1. **使用简单名称**
   ```json
   { "name": "HttpRequest" }  // 而不是全限定名
   ```

2. **先搜索确认存在**
   ```json
   {
     "query": "HttpRequest",
     "type": "interface"
   }
   ```

---

### ❌ 问题：查询结果格式错误

**现象**：返回的内容格式混乱

**解决方案**：

这是已知问题，不影响实际使用。如果影响使用：
1. 重新构建数据库
2. 检查 Python 版本（需要 3.11+）

---

## 性能问题

### ❌ 问题：查询响应慢

**现象**：查询需要数秒才能返回

**解决方案**：

1. **这是正常的**
   - 数据库已建立索引
   - 通常查询 < 100ms

2. **检查磁盘性能**
   - 使用 SSD
   - 确保磁盘未满

3. **减少结果数量**
   ```json
   {
     "limit": 5  // 而不是 50
   }
   ```

---

### ❌ 问题：服务启动慢

**现象**：启动需要很长时间

**解决方案**：

1. **首次启动**
   - 首次启动会创建虚拟环境
   - 后续启动会很快

2. **跳过依赖检查**
   ```powershell
   .\start.ps1 -SkipDbCheck
   ```

---

## 🛠️ 调试技巧

### 查看详细日志

```bash
# 启动时显示详细日志
uv run python scripts/run_server.py --log-level debug
```

### 手动测试查询

```bash
# 测试搜索
curl -X POST http://localhost:8000/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "search_api",
      "arguments": {
        "query": "HttpRequest"
      }
    }
  }'
```

### 检查服务状态

```bash
# 健康检查
curl http://localhost:8000/health

# 服务信息
curl http://localhost:8000/
```

---

## 📞 获取帮助

如果以上方案都无法解决问题：

1. **查看日志**
   - 服务端日志
   - 客户端日志

2. **提交 Issue**
   - 描述问题现象
   - 提供错误信息
   - 说明已尝试的解决方案
   - 提供环境信息（OS、Python 版本等）

3. **社区求助**
   - 在 MCP 社区寻求帮助
   - 在 Burp Suite 社区讨论

---

## 🔗 相关文档

- [快速上手指南](QUICKSTART.md)
- [MCP 客户端配置](MCP_CLIENT_SETUP.md)
- [API 使用教程](API_USAGE.md)

---

## ✅ 自检清单

遇到问题时，先检查：

- [ ] uv 已正确安装
- [ ] Python 版本 >= 3.11
- [ ] 虚拟环境已创建
- [ ] 依赖已安装
- [ ] 数据库文件存在
- [ ] 端口未被占用
- [ ] 服务已启动
- [ ] 客户端配置正确
- [ ] 配置文件 JSON 格式正确
- [ ] 路径使用绝对路径
