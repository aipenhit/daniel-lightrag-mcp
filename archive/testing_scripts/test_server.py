#!/usr/bin/env python3
"""
Test script to verify the MCP server functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daniel_lightrag_mcp.server import main

async def test_server():
    """Test the MCP server startup."""
    print("Testing MCP server startup...")
    try:
        # This will start the server - we'll need to interrupt it
        await main()
    except KeyboardInterrupt:
        print("Server started successfully and was interrupted.")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    print("Daniel LightRAG MCP Server Test")
    print("================================")
    print("This will start the MCP server. Press Ctrl+C to stop.")
    print()
    
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        print("\nTest completed successfully!")
