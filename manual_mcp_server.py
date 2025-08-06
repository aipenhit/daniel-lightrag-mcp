#!/usr/bin/env python3
"""
Manual MCP server that handles the protocol directly.
"""

import asyncio
import json
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_request(request_data):
    """Handle MCP requests manually."""
    try:
        request = json.loads(request_data)
        logger.info(f"Received request: {request.get('method', 'unknown')}")
        
        if request.get("method") == "tools/list":
            # Return tools list manually
            tools = [
                {
                    "name": "hello",
                    "description": "Say hello",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name to greet"
                            }
                        },
                        "required": ["name"]
                    }
                }
            ]
            
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": tools
                }
            }
            
            logger.info(f"Returning {len(tools)} tools")
            return json.dumps(response)
            
        elif request.get("method") == "tools/call":
            # Handle tool calls
            tool_name = request.get("params", {}).get("name")
            arguments = request.get("params", {}).get("arguments", {})
            
            if tool_name == "hello":
                name = arguments.get("name", "World")
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"message": f"Hello, {name}!"})
                        }
                    ]
                }
            else:
                result = {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Unknown tool: {tool_name}"
                        }
                    ],
                    "isError": True
                }
            
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": result
            }
            
            return json.dumps(response)
            
        elif request.get("method") == "initialize":
            # Handle initialization
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "manual-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            return json.dumps(response)
            
        else:
            # Unknown method
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {request.get('method')}"
                }
            }
            return json.dumps(response)
            
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", None),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        return json.dumps(response)

async def main():
    """Main server loop."""
    logger.info("Starting manual MCP server")
    
    try:
        while True:
            # Read from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            logger.info(f"Received: {line[:100]}...")
            
            # Handle the request
            response = await handle_request(line)
            
            # Write to stdout
            print(response, flush=True)
            logger.info(f"Sent: {response[:100]}...")
            
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())