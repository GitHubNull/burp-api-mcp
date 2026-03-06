# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future features and improvements

## [1.0.1] - 2024-03-06

### Fixed
- Fixed virtual environment creation issue in GitHub Actions CI workflow
- Ensured wheel package builds correctly in CI environment
- Added `uv venv` step before installing build tools in release workflow

## [1.0.0] - 2024-03-06

### Added
- 🎉 Initial stable release
- Complete Burp Suite Montoya API coverage (186 interfaces, 820 methods)
- FastAPI-based MCP server with HTTP SSE support
- SQLite database with pre-parsed and indexed data for fast queries
- 5 MCP tools for comprehensive API documentation queries:
  - `search_api`: Search interfaces, methods, or packages
  - `get_interface`: Get detailed interface information
  - `list_interfaces`: List all interfaces with package filtering
  - `get_method_signature`: Get method details and signatures
  - `get_package_info`: Get package structure and interfaces
- Java interface parser with Javadoc extraction
- SQLAlchemy ORM models for database management
- Cross-platform launch scripts:
  - `start.bat` for Windows CMD with ASCII UI
  - `start.sh` for Linux/Mac with color output
  - `start.ps1` for PowerShell with advanced features
- Comprehensive documentation:
  - Chinese README with full setup guide
  - English README with bilingual support
  - Quick start guide (5-minute tutorial)
  - MCP client configuration guide (Claude, Cursor, etc.)
  - API usage tutorials with examples
  - Troubleshooting guide with solutions
- Apache License 2.0
- GitHub Actions CI/CD for automated releases
- Semantic versioning support with pre-release versions
- Wheel package support for pip installation
- Complete ZIP package with database and documentation

### Features
- 📚 Complete API Coverage - 186 interfaces, 820 methods
- 🗄️ SQLite Storage - Pre-parsed and indexed for fast queries
- 🔌 MCP Protocol Support - Standard MCP tool interfaces
- 🌐 HTTP SSE Mode - Compatible with any MCP client
- 🔍 Smart Search - Search by interface, method, or package names
- 🚀 One-Click Start - Launch scripts for Windows, Linux, and Mac
- 📝 Comprehensive Documentation - Chinese and English
- 🔄 Automated Releases - GitHub Actions workflow

### Technical Details
- Built with FastAPI and uv
- Python 3.11+ required
- Uses SQLAlchemy for database ORM
- MCP protocol implementation with SSE transport
- Java source code parser for API extraction
- Git LFS support for database file

[Unreleased]: https://github.com/yourusername/burp-api-mcp/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/yourusername/burp-api-mcp/releases/tag/v1.0.1
[1.0.0]: https://github.com/yourusername/burp-api-mcp/releases/tag/v1.0.0
