#!/usr/bin/env python3
"""
Test script for the Daniel LightRAG MCP server.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from daniel_lightrag_mcp.client import LightRAGClient, LightRAGError


async def test_lightrag_connection():
    """Test basic connection to LightRAG server."""
    print("Testing LightRAG connection...")
    
    client = LightRAGClient()
    
    try:
        # Test health check
        print("1. Testing health check...")
        health = await client.health_check()
        print(f"   Health check result: {json.dumps(health, indent=2)}")
        
        # Test simple query
        print("\n2. Testing simple query...")
        query_result = await client.query("What is LightRAG?", mode="hybrid")
        print(f"   Query result: {json.dumps(query_result, indent=2)}")
        
        print("\n✅ All tests passed! LightRAG server is accessible.")
        return True
        
    except LightRAGError as e:
        print(f"\n❌ LightRAG error: {e}")
        print("\n⚠️  LightRAG server is not accessible. Please ensure:")
        print("   1. LightRAG server is running on http://localhost:9621")
        print("   2. The server is properly configured")
        print("   3. No firewall is blocking the connection")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


async def test_mcp_server_functions():
    """Test MCP server handler functions directly."""
    print("\n" + "="*50)
    print("Testing MCP Server Functions")
    print("="*50)
    
    # Import MCP server components
    from daniel_lightrag_mcp.server import handle_list_tools, handle_call_tool
    from mcp.types import CallToolRequest
    
    success = True
    
    try:
        # Test list tools
        print("1. Testing list_tools...")
        tools_result = await handle_list_tools()
        print(f"   Found {len(tools_result.tools)} tools:")
        for tool in tools_result.tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Test health_check tool
        print("\n2. Testing health_check tool...")
        health_request = CallToolRequest(
            method="tools/call",
            params={"name": "health_check", "arguments": {}}
        )
        health_result = await handle_call_tool(health_request)
        
        if health_result.isError:
            print(f"   ❌ Health check failed: {health_result.content[0].text}")
            success = False
        else:
            print(f"   ✅ Health check passed")
            # Parse and display the result nicely
            try:
                health_data = json.loads(health_result.content[0].text)
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Core Version: {health_data.get('core_version', 'unknown')}")
            except:
                print(f"   Raw result: {health_result.content[0].text}")
        
        # Test query tool
        print("\n3. Testing query tool...")
        query_request = CallToolRequest(
            method="tools/call",
            params={
                "name": "query", 
                "arguments": {"query": "What is LightRAG?", "mode": "hybrid"}
            }
        )
        query_result = await handle_call_tool(query_request)
        
        if query_result.isError:
            print(f"   ❌ Query failed: {query_result.content[0].text}")
            success = False
        else:
            print(f"   ✅ Query passed")
            # Parse and display the result nicely
            try:
                query_data = json.loads(query_result.content[0].text)
                response = query_data.get('response', 'No response')
                print(f"   Response preview: {response[:100]}...")
            except:
                print(f"   Raw result: {query_result.content[0].text[:100]}...")
        
        if success:
            print("\n✅ MCP server functions are working correctly!")
        else:
            print("\n❌ Some MCP server function tests failed.")
            
        return success
        
    except Exception as e:
        print(f"\n❌ MCP server error: {e}")
        return False


async def main():
    """Main test function."""
    print("Daniel LightRAG MCP Server Test")
    print("="*40)
    
    # Test LightRAG connection first
    lightrag_ok = await test_lightrag_connection()
    
    if not lightrag_ok:
        print("\n❌ Cannot proceed with MCP tests - LightRAG server is not accessible.")
        return
    
    # Test MCP server functions
    mcp_ok = await test_mcp_server_functions()
    
    if lightrag_ok and mcp_ok:
        print("\n🎉 All tests passed! The MCP server is ready to use.")
        print("\nTo use the MCP server:")
        print("1. Install it: pip install -e .")
        print("2. Add to your MCP client configuration:")
        print("   {")
        print('     "mcpServers": {')
        print('       "daniel-lightrag-mcp": {')
        print('         "command": "daniel-lightrag-mcp"')
        print('       }')
        print('     }')
        print("   }")
        print("\n3. Test the CLI:")
        print("   daniel-lightrag-mcp")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
