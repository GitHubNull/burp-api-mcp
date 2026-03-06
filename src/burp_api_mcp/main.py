"""
FastAPI MCP Server for Burp Suite Montoya API documentation.
"""

import json
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker, Session

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from burp_api_mcp.models import Package, Interface, Method

# Database configuration - look for db in project root
# When running from src/burp_api_mcp, go up 2 levels to project root
DB_PATH = (Path(__file__).parent.parent.parent / "burp_api.db").resolve()
if not DB_PATH.exists():
    # Fallback: check current working directory
    DB_PATH = (Path.cwd() / "burp_api.db").resolve()
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MCP Server instance
mcp_server = Server("burp-api-mcp")


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_api",
            description="Search the Burp Suite Montoya API documentation for interfaces, methods, or packages. Returns matching results with descriptions and signatures.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - can be interface name, method name, or package name",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["interface", "method", "package", "all"],
                        "description": "Type of entity to search for",
                        "default": "all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_interface",
            description="Get detailed information about a specific interface including all its methods, inheritance, and documentation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Interface name (e.g., 'HttpRequest') or fully qualified name (e.g., 'burp.api.montoya.http.message.requests.HttpRequest')",
                    }
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="list_interfaces",
            description="List all interfaces in the API, optionally filtered by package name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Package name to filter by (e.g., 'burp.api.montoya.http')",
                        "default": None,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 50,
                    },
                },
            },
        ),
        Tool(
            name="get_method_signature",
            description="Get detailed signature and documentation for a specific method, including parameters and return type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface": {
                        "type": "string",
                        "description": "Interface name containing the method",
                    },
                    "method": {
                        "type": "string",
                        "description": "Method name to look up",
                    },
                },
                "required": ["interface", "method"],
            },
        ),
        Tool(
            name="get_package_info",
            description="Get information about a package and list all interfaces within it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Package name (e.g., 'burp.api.montoya.http')",
                    }
                },
                "required": ["name"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    db = get_db()
    try:
        if name == "search_api":
            return await handle_search_api(db, arguments)
        elif name == "get_interface":
            return await handle_get_interface(db, arguments)
        elif name == "list_interfaces":
            return await handle_list_interfaces(db, arguments)
        elif name == "get_method_signature":
            return await handle_get_method_signature(db, arguments)
        elif name == "get_package_info":
            return await handle_get_package_info(db, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    finally:
        db.close()


async def handle_search_api(db: Session, arguments: dict) -> list[TextContent]:
    """Handle search_api tool call."""
    query = arguments.get("query", "").lower()
    search_type = arguments.get("type", "all")
    limit = arguments.get("limit", 10)

    if not query:
        return [TextContent(type="text", text="Please provide a search query")]

    results = []

    # Search interfaces
    if search_type in ["all", "interface"]:
        interfaces = (
            db.query(Interface)
            .filter(
                or_(
                    Interface.name.ilike(f"%{query}%"),
                    Interface.fully_qualified_name.ilike(f"%{query}%"),
                    Interface.description.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
            .all()
        )

        for iface in interfaces:
            results.append(
                f"**Interface**: `{iface.fully_qualified_name}`\n{iface.description or 'No description'}"
            )

    # Search methods
    if search_type in ["all", "method"]:
        methods = (
            db.query(Method)
            .filter(
                or_(
                    Method.name.ilike(f"%{query}%"),
                    Method.description.ilike(f"%{query}%"),
                    Method.signature.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
            .all()
        )

        for method in methods:
            interfaces_str = ", ".join([i.name for i in method.interfaces[:3]])
            results.append(
                f"**Method**: `{method.name}` in [{interfaces_str}]\n{method.description or 'No description'}\nSignature: `{method.signature}`"
            )

    # Search packages
    if search_type in ["all", "package"]:
        packages = (
            db.query(Package)
            .filter(Package.name.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )

        for pkg in packages:
            interface_count = len(pkg.interfaces)
            results.append(
                f"**Package**: `{pkg.name}`\nContains {interface_count} interfaces"
            )

    if not results:
        return [TextContent(type="text", text=f"No results found for query: '{query}'")]

    return [TextContent(type="text", text="\n\n---\n\n".join(results[:limit]))]


async def handle_get_interface(db: Session, arguments: dict) -> list[TextContent]:
    """Handle get_interface tool call."""
    name = arguments.get("name", "")

    # Try to find by fully qualified name first, then by simple name
    interface = (
        db.query(Interface).filter(Interface.fully_qualified_name == name).first()
    )

    if not interface:
        interface = db.query(Interface).filter(Interface.name == name).first()

    if not interface:
        return [TextContent(type="text", text=f"Interface '{name}' not found")]

    # Build response
    lines = [
        f"# Interface: {interface.name}",
        f"**Package**: `{interface.package.name}`",
        f"**Fully Qualified Name**: `{interface.fully_qualified_name}`",
        "",
    ]

    if interface.description:
        lines.append(f"## Description\n{interface.description}\n")

    if interface.javadoc:
        lines.append(f"## Javadoc\n```\n{interface.javadoc}\n```\n")

    if interface.extends:
        extends_str = ", ".join([f"`{e.name}`" for e in interface.extends])
        lines.append(f"**Extends**: {extends_str}\n")

    if interface.methods:
        lines.append(f"## Methods ({len(interface.methods)})\n")
        for method in interface.methods:
            params_str = ""
            if method.parameters:
                try:
                    params = json.loads(method.parameters)
                    params_str = ", ".join([f"{p['type']} {p['name']}" for p in params])
                except:
                    params_str = method.parameters

            lines.append(f"### {method.name}")
            lines.append(f"```java")
            lines.append(f"{method.return_type or 'void'} {method.name}({params_str})")
            lines.append(f"```")
            if method.description:
                lines.append(f"{method.description}")
            lines.append("")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_list_interfaces(db: Session, arguments: dict) -> list[TextContent]:
    """Handle list_interfaces tool call."""
    package = arguments.get("package")
    limit = arguments.get("limit", 50)

    query = db.query(Interface)

    if package:
        query = query.join(Package).filter(Package.name.ilike(f"%{package}%"))

    interfaces = query.limit(limit).all()

    if not interfaces:
        filter_msg = f" in package '{package}'" if package else ""
        return [TextContent(type="text", text=f"No interfaces found{filter_msg}")]

    lines = [f"# Interfaces ({len(interfaces)} shown)\n"]

    for iface in interfaces:
        method_count = len(iface.methods)
        lines.append(
            f"- **{iface.name}** (`{iface.package.name}`) - {method_count} methods"
        )
        if iface.description:
            desc = (
                iface.description[:100] + "..."
                if len(iface.description) > 100
                else iface.description
            )
            lines.append(f"  {desc}")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_get_method_signature(
    db: Session, arguments: dict
) -> list[TextContent]:
    """Handle get_method_signature tool call."""
    interface_name = arguments.get("interface", "")
    method_name = arguments.get("method", "")

    # Find interface
    interface = db.query(Interface).filter(Interface.name == interface_name).first()

    if not interface:
        return [
            TextContent(type="text", text=f"Interface '{interface_name}' not found")
        ]

    # Find method in interface
    method = (
        db.query(Method)
        .filter(Method.name == method_name, Method.interfaces.any(id=interface.id))
        .first()
    )

    if not method:
        return [
            TextContent(
                type="text",
                text=f"Method '{method_name}' not found in interface '{interface_name}'",
            )
        ]

    # Build response
    lines = [
        f"# Method: {method.name}",
        f"**Interface**: `{interface.fully_qualified_name}`",
        "",
    ]

    lines.append("## Signature")
    lines.append(f"```java")
    lines.append(method.signature)
    lines.append(f"```")
    lines.append("")

    if method.description:
        lines.append(f"## Description\n{method.description}\n")

    if method.parameters:
        lines.append("## Parameters")
        try:
            params = json.loads(method.parameters)
            for param in params:
                desc = (
                    f" - {param.get('description', '')}"
                    if param.get("description")
                    else ""
                )
                lines.append(f"- `{param['type']} {param['name']}`{desc}")
        except:
            lines.append(method.parameters)
        lines.append("")

    if method.return_type:
        lines.append(f"**Return Type**: `{method.return_type}`\n")

    if method.exceptions:
        try:
            exceptions = json.loads(method.exceptions)
            if exceptions:
                lines.append(f"**Throws**: {', '.join(exceptions)}\n")
        except:
            pass

    if method.javadoc:
        lines.append(f"## Full Javadoc\n```\n{method.javadoc}\n```")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_get_package_info(db: Session, arguments: dict) -> list[TextContent]:
    """Handle get_package_info tool call."""
    package_name = arguments.get("name", "")

    package = db.query(Package).filter(Package.name == package_name).first()

    if not package:
        return [TextContent(type="text", text=f"Package '{package_name}' not found")]

    lines = [f"# Package: {package.name}", ""]

    if package.description:
        lines.append(f"## Description\n{package.description}\n")

    if package.interfaces:
        lines.append(f"## Interfaces ({len(package.interfaces)})\n")
        for iface in package.interfaces:
            method_count = len(iface.methods)
            lines.append(f"### {iface.name}")
            lines.append(f"- Methods: {method_count}")
            lines.append(f"- FQN: `{iface.fully_qualified_name}`")
            if iface.description:
                lines.append(f"- {iface.description}")
            lines.append("")
    else:
        lines.append("No interfaces found in this package.")

    return [TextContent(type="text", text="\n".join(lines))]


# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    if not DB_PATH.exists():
        print(f"Warning: Database not found at {DB_PATH}")
        print("Please run: uv run python scripts/parse_and_import.py")
    else:
        print(f"Connected to database: {DB_PATH}")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Burp Suite Montoya API MCP Server",
    description="MCP Server for querying Burp Suite Montoya API documentation",
    version="1.0.0",
    lifespan=lifespan,
)

# Create SSE transport
sse = SseServerTransport("/messages/")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Burp Suite Montoya API MCP Server",
        "version": "1.0.0",
        "sse_endpoint": "/sse",
        "database": str(DB_PATH) if DB_PATH.exists() else "Not initialized",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    db_status = "connected" if DB_PATH.exists() else "disconnected"
    return {"status": "healthy", "database": db_status}


@app.get("/sse")
async def handle_sse(request):
    """SSE endpoint for MCP communication."""
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        await mcp_server.run(
            read_stream, write_stream, mcp_server.create_initialization_options()
        )


# Mount the message handler
app.mount("/messages", sse.handle_post_message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
