#!/usr/bin/env python3
"""
Entry point for running the Burp API MCP Server.
Ensures correct database path and starts the server.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set working directory to project root for correct DB path
project_root = Path(__file__).parent.parent
import os

os.chdir(project_root)

import uvicorn
from burp_api_mcp.main import app

if __name__ == "__main__":
    print(f"Starting Burp API MCP Server...")
    print(f"Project root: {project_root}")
    print(f"Database: {project_root / 'burp_api.db'}")
    print(f"Server will run on: http://0.0.0.0:8000")
    print(f"SSE endpoint: http://0.0.0.0:8000/sse")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=True)
