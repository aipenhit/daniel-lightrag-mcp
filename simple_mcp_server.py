#!/usr/bin/env python3
"""
Extremely simple MCP server to test basic connectivity with Kiro.
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
server = Server("simple-mcp-test")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    logger.info("=== LISTING TOOLS ===")
    
    # Create exactly ONE simple tool
    tool = Tool(
        name="hello",
        description="Say hello",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet"
                }
            },
            "required": ["name"]
        }
    )
    
    logger.info(f"Created tool: {tool.name} (type: {type(tool)})")
    
    # Create the result with just this one tool
    tools_list = [tool]
    logger.info(f"Tools list: {len(tools_list)} tools")
    
    # Create ListToolsResult
    result = ListToolsResult(tools=tools_list)
    logger.info(f"ListToolsResult created: {type(result)}")
    logger.info(f"Result.tools: {len(result.tools)} tools")
    
    # Log the first tool to verify
    if result.tools:
        first_tool = result.tools[0]
        logger.info(f"First tool: name='{first_tool.name}', type={type(first_tool)}")
    
    logger.info("=== RETURNING RESULT ===")
    return result

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    tool_name = request.params.name
    arguments = request.params.arguments or {}
    
    logger.info(f"Tool called: {tool_name}")
    
    if tool_name == "hello":
        name = arguments.get("name", "World")
        result = {"message": f"Hello, {name}!"}
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result))]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {tool_name}")],
            isError=True
        )

async def main():
    """Main entry point."""
    logger.info("Starting simple MCP server")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server started, waiting for connections...")
            
            # For MCP 1.0.0, try without capabilities first
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="simple-mcp-test",
                    server_version="1.0.0",
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())