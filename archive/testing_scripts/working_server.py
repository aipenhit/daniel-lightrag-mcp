#!/usr/bin/env python3
"""
Working MCP server with minimal tools to test Kiro compatibility.
"""

import asyncio
import json
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("working-lightrag-mcp")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    logger.info("Listing available MCP tools")
    
    # Create just a few tools to test
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
        )
    ]
    
    logger.info(f"Created {len(tools)} tools")
    
    # Validate tools
    for i, tool in enumerate(tools):
        if not isinstance(tool, Tool):
            raise ValueError(f"Tool {i} is not a Tool instance: {type(tool)}")
        logger.info(f"Tool {i}: {tool.name} - OK")
    
    # Create result - try the most basic approach
    result = ListToolsResult(tools=tools)
    logger.info(f"ListToolsResult created successfully with {len(result.tools)} tools")
    
    return result

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    tool_name = request.params.name
    arguments = request.params.arguments or {}
    
    logger.info(f"Handling tool call: {tool_name}")
    
    # Simple responses for testing
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
    """Main entry point for the working MCP server."""
    logger.info("Starting working LightRAG MCP server")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Working MCP server initialized, starting communication loop")
            
            from mcp.server import NotificationOptions
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="working-lightrag-mcp",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Fatal server error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    asyncio.run(main())