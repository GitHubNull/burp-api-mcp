# Burp Suite Montoya API MCP 服务端

[English Documention](README_EN.md) | [中文文档](README.md)

基于 FastAPI 和 MCP（Model Context Protocol）协议的 Burp Suite Montoya API 文档查询服务端。

## ✨ 功能特性

- 📚 **完整 API 覆盖** - 收录所有 186 个接口和 820 个方法
- 🗄️ **SQLite 存储** - 预解析并建立索引，查询速度快
- 🔌 **MCP 协议支持** - 标准 MCP 工具接口，支持所有 MCP 客户端
- 🌐 **HTTP SSE 模式** - 兼容支持 HTTP SSE 传输的任何 MCP 客户端
- 🔍 **智能搜索** - 支持接口、方法、包名搜索
- 🚀 **一键启动** - 提供 Windows、Linux、Mac 启动脚本

## 📊 数据统计

- **包 (Packages)**: 48 个
- **接口 (Interfaces)**: 186 个  
- **方法 (Methods)**: 820 个
- **数据文件大小**: ~540KB

## 🛠️ 可用 MCP 工具

| 工具名 | 功能描述 |
|--------|----------|
| `search_api` | 搜索 API - 可按名称搜索接口、方法或包 |
| `get_interface` | 获取接口详情 - 包含所有方法、继承关系、文档说明 |
| `list_interfaces` | 列出所有接口 - 可按包名筛选 |
| `get_method_signature` | 获取方法签名 - 包含参数、返回值、异常说明 |
| `get_package_info` | 获取包信息 - 包含包内所有接口列表 |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 包管理器

### 安装步骤

#### 方式一：使用启动脚本（推荐）

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

脚本会自动完成：
1. ✅ 检查 uv 是否安装
2. ✅ 创建虚拟环境
3. ✅ 安装依赖
4. ✅ 检查数据库是否存在（不存在则自动构建）
5. ✅ 检查端口是否被占用
6. ✅ 启动 MCP 服务端

#### 方式二：手动安装

```bash
# 进入项目目录
cd burp-api-mcp

# 安装依赖
uv sync

# 构建数据库（首次使用需要）
uv run python scripts/parse_and_import.py

# 启动服务器
uv run python scripts/run_server.py
```

## 📡 服务端地址

启动后，服务运行在：**http://localhost:8000**

### HTTP 端点

| 端点 | 功能 |
|------|------|
| `GET /` | 服务信息 |
| `GET /health` | 健康检查 |
| `GET /sse` | **MCP SSE 端点** |

## 🔧 使用示例

### MCP 工具调用示例

#### 1. 搜索 API
```json
{
  "name": "search_api",
  "arguments": {
    "query": "HttpRequest",
    "type": "interface",
    "limit": 5
  }
}
```

#### 2. 获取接口详情
```json
{
  "name": "get_interface",
  "arguments": {
    "name": "HttpRequest"
  }
}
```

#### 3. 按包名列出接口
```json
{
  "name": "list_interfaces",
  "arguments": {
    "package": "burp.api.montoya.http",
    "limit": 20
  }
}
```

#### 4. 获取方法签名
```json
{
  "name": "get_method_signature",
  "arguments": {
    "interface": "HttpRequest",
    "method": "withBody"
  }
}
```

## 🔗 连接 MCP 客户端

### Claude Desktop 配置

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "burp-api": {
      "command": "uv",
      "args": [
        "run",
        "--cwd",
        "C:\\path\\to\\burp-api-mcp",
        "python",
        "scripts/run_server.py"
      ]
    }
  }
}
```

**或者使用 HTTP SSE 模式：**

如果你的 MCP 客户端支持 HTTP SSE，直接连接：
```
http://localhost:8000/sse
```

### 其他 MCP 客户端

任何支持 MCP 协议的客户端都可以通过 SSE 连接：
- Cursor
- Continue
- 其他支持 MCP 的 IDE 插件

## 📁 项目结构

```
burp-api-mcp/
├── 📄 start.bat              # Windows CMD 启动脚本
├── 📄 start.ps1              # PowerShell 启动脚本
├── 📄 start.sh               # Linux/Mac 启动脚本
├── 📄 LICENSE                # Apache 2.0 许可证
├── 📄 README.md              # 中文文档（本文档）
├── 📄 README_EN.md           # 英文文档
├── 🗄️  burp_api.db           # SQLite 数据库（自动生成）
├── 📂 src/burp_api_mcp/
│   ├── __init__.py
│   ├── main.py              # FastAPI + MCP 服务端
│   ├── models.py            # SQLAlchemy 数据模型
│   └── parser.py            # Java 接口解析器
├── 📂 scripts/
│   ├── parse_and_import.py  # 解析 Java 文件到 SQLite
│   └── run_server.py        # 服务端入口
└── 📄 pyproject.toml        # uv 项目配置
```

## 🔍 核心模块说明

### Java 解析器 (`parser.py`)
- 解析 Java 接口文件
- 提取 Javadoc 注释
- 分析方法签名、参数、返回值
- 处理继承关系

### 数据模型 (`models.py`)
- Package：包结构
- Interface：接口定义
- Method：方法详情
- Import：导入语句

### MCP 服务端 (`main.py`)
- FastAPI Web 框架
- MCP 协议实现
- 5 个核心查询工具
- SSE 传输支持

## 🛠️ 开发指南

### 重新构建数据库

如果修改了解析器或需要刷新数据：

```bash
# 删除旧数据库
rm burp_api.db

# 重新构建
uv run python scripts/parse_and_import.py
```

### 运行测试

```bash
# 测试数据库连接
uv run python -c "from src.burp_api_mcp.models import init_db, get_session; engine = init_db('burp_api.db'); session = get_session(engine); print('数据库连接成功！')"

# 测试解析器
uv run python -c "from src.burp_api_mcp.parser import JavaInterfaceParser; from pathlib import Path; p = JavaInterfaceParser(Path('api')); print('解析器工作正常！')"
```

### 调试模式

```bash
# 详细日志输出
uv run python scripts/run_server.py --log-level debug
```

## ⚠️ 故障排除

### 数据库未找到

如果服务器显示 `"database": "Not initialized"`：

1. 确保 `burp_api.db` 存在于项目根目录
2. 检查文件权限
3. 重新构建：`rm burp_api.db && uv run python scripts/parse_and_import.py`

### 端口被占用

如果提示端口 8000 被占用：

```bash
# 查找占用端口的进程
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# 修改端口（修改 scripts/run_server.py 中的 port 参数）
```

### 导入错误

确保使用虚拟环境：

```bash
# 查看当前 Python 路径
which python  # Linux/Mac
where python  # Windows

# 应该指向 .venv/Scripts/python

# 手动激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### uv 未安装

如果提示 uv 未安装：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

## 📜 开源协议

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

```
Copyright 2024 Burp API MCP Server Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

## 🤝 贡献指南

这是一个社区工具，非官方项目。欢迎提交 Issue 和 PR！

### 提交 Issue

- 🐛 Bug 报告：请提供复现步骤和环境信息
- ✨ 功能请求：请描述使用场景和期望功能
- 📖 文档改进：请指出具体问题或改进建议

### 提交 PR

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📮 联系方式

- **项目地址**: [GitHub Repository]
- **Issue 追踪**: [GitHub Issues]
- **邮件**: [your-email@example.com]

## 🙏 致谢

- [Burp Suite](https://portswigger.net/burp) - 提供 Montoya API 文档
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [uv](https://docs.astral.sh/uv/) - Python 包管理器
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM 框架

## 📌 免责声明

本项目是社区开发的非官方工具，与 PortSwigger 公司无任何关联。Burp Suite 是 PortSwigger 公司的注册商标。

使用本工具查询的 API 信息仅供参考，实际开发请参考 [Burp Suite 官方文档](https://portswigger.net/burp/extender/api/)。

---

**Made with ❤️ by the Security Community**
