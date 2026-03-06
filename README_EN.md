# Burp Suite Montoya API MCP Server

[English Documention](README_EN.md) | [中文文档](README.md)

FastAPI-based MCP (Model Context Protocol) server for querying Burp Suite Montoya API documentation.

## ✨ Features

- 📚 **Complete API Coverage** - All 186 interfaces and 820 methods from Burp Suite Montoya API
- 🗄️ **SQLite Storage** - Pre-parsed and indexed for fast queries
- 🔌 **MCP Protocol Support** - Standard MCP tool interfaces, compatible with all MCP clients
- 🌐 **HTTP SSE Mode** - Compatible with any MCP client supporting HTTP SSE transport
- 🔍 **Smart Search** - Search by interface, method, or package names
- 🚀 **One-Click Start** - Launch scripts for Windows, Linux, and Mac

## 📊 Statistics

- **Packages**: 48
- **Interfaces**: 186  
- **Methods**: 820
- **Database Size**: ~540KB

## 🛠️ Available MCP Tools

| Tool Name | Description |
|-----------|-------------|
| `search_api` | Search API - Search interfaces, methods, or packages by name |
| `get_interface` | Get Interface Details - Includes all methods, inheritance, and documentation |
| `list_interfaces` | List All Interfaces - Filter by package name |
| `get_method_signature` | Get Method Signature - Includes parameters, return values, and exceptions |
| `get_package_info` | Get Package Info - List all interfaces within a package |

## 🚀 Quick Start

### Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

#### Option 1: Using Launch Scripts (Recommended)

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

The scripts automatically:
1. ✅ Check if uv is installed
2. ✅ Create virtual environment
3. ✅ Install dependencies
4. ✅ Check if database exists (auto-build if missing)
5. ✅ Check if port is in use
6. ✅ Start MCP server

#### Option 2: Manual Installation

```bash
# Enter project directory
cd burp-api-mcp

# Install dependencies
uv sync

# Build database (first time only)
uv run python scripts/parse_and_import.py

# Start server
uv run python scripts/run_server.py
```

## 📡 Server Address

After starting, the server runs at: **http://localhost:8000**

### HTTP Endpoints

| Endpoint | Function |
|----------|----------|
| `GET /` | Server info |
| `GET /health` | Health check |
| `GET /sse` | **MCP SSE Endpoint** |

## 🔧 Usage Examples

### MCP Tool Call Examples

#### 1. Search API
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

#### 2. Get Interface Details
```json
{
  "name": "get_interface",
  "arguments": {
    "name": "HttpRequest"
  }
}
```

#### 3. List Interfaces by Package
```json
{
  "name": "list_interfaces",
  "arguments": {
    "package": "burp.api.montoya.http",
    "limit": 20
  }
}
```

#### 4. Get Method Signature
```json
{
  "name": "get_method_signature",
  "arguments": {
    "interface": "HttpRequest",
    "method": "withBody"
  }
}
```

## 🔗 Connecting MCP Clients

### Claude Desktop Configuration

Edit `claude_desktop_config.json`:

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

**Or use HTTP SSE Mode:**

If your MCP client supports HTTP SSE, connect directly:
```
http://localhost:8000/sse
```

### Other MCP Clients

Any MCP-compatible client can connect via SSE:
- Cursor
- Continue
- Other MCP-supporting IDE plugins

## 📁 Project Structure

```
burp-api-mcp/
├── 📄 start.bat              # Windows CMD launch script
├── 📄 start.ps1              # PowerShell launch script
├── 📄 start.sh               # Linux/Mac launch script
├── 📄 LICENSE                # Apache 2.0 License
├── 📄 README.md              # Chinese documentation
├── 📄 README_EN.md           # English documentation (this file)
├── 🗄️  burp_api.db           # SQLite database (auto-generated)
├── 📂 src/burp_api_mcp/
│   ├── __init__.py
│   ├── main.py              # FastAPI + MCP server
│   ├── models.py            # SQLAlchemy data models
│   └── parser.py            # Java interface parser
├── 📂 scripts/
│   ├── parse_and_import.py  # Parse Java files to SQLite
│   └── run_server.py        # Server entry point
└── 📄 pyproject.toml        # uv project configuration
```

## 🔍 Core Modules

### Java Parser (`parser.py`)
- Parse Java interface files
- Extract Javadoc comments
- Analyze method signatures, parameters, return values
- Handle inheritance relationships

### Data Models (`models.py`)
- Package: Package structure
- Interface: Interface definitions
- Method: Method details
- Import: Import statements

### MCP Server (`main.py`)
- FastAPI web framework
- MCP protocol implementation
- 5 core query tools
- SSE transport support

## 🛠️ Development Guide

### Rebuild Database

If you modified the parser or need to refresh data:

```bash
# Delete old database
rm burp_api.db

# Rebuild
uv run python scripts/parse_and_import.py
```

### Running Tests

```bash
# Test database connection
uv run python -c "from src.burp_api_mcp.models import init_db, get_session; engine = init_db('burp_api.db'); session = get_session(engine); print('Database connected!')"

# Test parser
uv run python -c "from src.burp_api_mcp.parser import JavaInterfaceParser; from pathlib import Path; p = JavaInterfaceParser(Path('api')); print('Parser works!')"
```

### Debug Mode

```bash
# Verbose logging
uv run python scripts/run_server.py --log-level debug
```

## ⚠️ Troubleshooting

### Database Not Found

If the server shows `"database": "Not initialized"`:

1. Ensure `burp_api.db` exists in project root
2. Check file permissions
3. Rebuild: `rm burp_api.db && uv run python scripts/parse_and_import.py`

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Change port (modify port parameter in scripts/run_server.py)
```

### Import Errors

Ensure you're using the virtual environment:

```bash
# Check current Python path
which python  # Linux/Mac
where python  # Windows

# Should point to .venv/Scripts/python

# Activate manually
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### uv Not Installed

If uv is not installed:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

## 📜 License

This project is licensed under the [Apache License 2.0](LICENSE).

```
Copyright 2024 Burp API MCP Server Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

## 🤝 Contributing

This is a community tool, not an official project. Issues and PRs welcome!

### Submitting Issues

- 🐛 Bug Reports: Provide reproduction steps and environment info
- ✨ Feature Requests: Describe use case and expected functionality
- 📖 Documentation: Point out specific issues or improvement suggestions

### Submitting PRs

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

## 📮 Contact

- **Repository**: [GitHub Repository]
- **Issue Tracker**: [GitHub Issues]
- **Email**: [your-email@example.com]

## 🙏 Acknowledgments

- [Burp Suite](https://portswigger.net/burp) - Montoya API documentation
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [uv](https://docs.astral.sh/uv/) - Python package manager
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM framework

## 📌 Disclaimer

This project is a community-developed unofficial tool, not affiliated with PortSwigger. Burp Suite is a registered trademark of PortSwigger Ltd.

The API information queried by this tool is for reference only. For actual development, please refer to the [Burp Suite official documentation](https://portswigger.net/burp/extender/api/).

---

**Made with ❤️ by the Security Community**
