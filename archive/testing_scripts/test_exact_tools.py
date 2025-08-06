#!/usr/bin/env python3
"""
Test the exact tool definitions from our server.
"""

from mcp.types import Tool, ListToolsResult

def test_tools():
    """Test creating the exact tools from our server."""
    try:
        tools = [
            # Document Management Tools (8 tools)
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
                        },
                        "only_need_context": {
                            "type": "boolean",
                            "description": "Whether to only return context without generation",
                            "default": False
                        }
                    },
                    "required": ["query"]
                }
            ),
        ]
        
        print(f"✅ Created {len(tools)} tools successfully")
        
        # Test each tool individually
        for i, tool in enumerate(tools):
            print(f"Tool {i}: name='{tool.name}', type={type(tool)}")
            if not hasattr(tool, 'name'):
                print(f"❌ Tool {i} missing 'name' attribute!")
                return False
        
        # Test ListToolsResult
        result = ListToolsResult(tools=tools)
        print(f"✅ ListToolsResult created successfully with {len(result.tools)} tools")
        
        # Test accessing tools from result
        for i, tool in enumerate(result.tools):
            print(f"Result tool {i}: name='{tool.name}', type={type(tool)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tools()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")