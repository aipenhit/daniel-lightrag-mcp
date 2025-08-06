#!/usr/bin/env python3
"""
Minimal version of our MCP server to test the issue.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("minimal-lightrag-mcp")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    logger.info("Listing available MCP tools")
    
    tools = [
        Tool(
            name="insert_text",
            description="Insert text content into LightRAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to insert"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="query_text",
            description="Query LightRAG with text",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query text"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Query mode",
                        "enum": ["naive", "local", "global", "hybrid"],
                        "default": "hybrid"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_health",
            description="Check LightRAG server health",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]
    
    logger.info(f"Created {len(tools)} tools")
    
    # Debug: Check each tool before creating result
    for i, tool in enumerate(tools):
        logger.info(f"Tool {i}: {type(tool)} with name '{getattr(tool, 'name', 'NO_NAME')}'")
        if not hasattr(tool, 'name'):
            logger.error(f"Tool {i} is missing 'name' attribute: {tool}")
            raise ValueError(f"Tool {i} is not a proper Tool object")
    
    result = ListToolsResult(tools=tools)
    logger.info(f"ListToolsResult created successfully with {len(result.tools)} tools")
    return result

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    tool_name = request.params.name
    arguments = request.params.arguments or {}
    
    logger.info(f"Handling tool call: {tool_name}")
    
    if tool_name == "insert_text":
        text = arguments.get("text", "")
        result = {"status": "success", "message": f"Inserted text: {text[:50]}..."}
    elif tool_name == "query_text":
        query = arguments.get("query", "")
        mode = arguments.get("mode", "hybrid")
        result = {"status": "success", "query": query, "mode": mode, "response": "Mock response"}
    elif tool_name == "get_health":
        result = {"status": "healthy", "server": "LightRAG MCP Server"}
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {tool_name}")],
            isError=True
        )
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(result, indent=2))]
    )

async def main():
    """Main entry point for the minimal MCP server."""
    logger.info("Starting minimal LightRAG MCP server")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Minimal MCP server initialized, starting communication loop")
            
            capabilities = server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
            logger.info(f"Server capabilities initialized")
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="minimal-lightrag-mcp",
                    server_version="0.1.0",
                    capabilities=capabilities,
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal server error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    asyncio.run(main())