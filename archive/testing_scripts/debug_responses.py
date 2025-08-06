#!/usr/bin/env python3
"""
Debug script to see actual response formats from LightRAG server.
"""

import asyncio
import httpx
import json
import os

async def debug_responses():
    """Debug actual response formats."""
    
    base_url = "http://localhost:9621"
    api_key = "lightragsecretkey"
    
    headers = {"X-API-Key": api_key}
    
    async with httpx.AsyncClient(headers=headers) as client:
        
        # Test endpoints that are failing with response parsing
        endpoints_to_test = [
            ("GET", "/graph/label/list", None, "get_graph_labels"),
            ("POST", "/documents/scan", {}, "scan_documents"),
            ("GET", "/documents/pipeline_status", None, "get_pipeline_status"),
            ("POST", "/documents/clear_cache", {}, "clear_cache"),
            ("POST", "/query", {"query": "test", "mode": "hybrid"}, "query_text"),
        ]
        
        for method, endpoint, data, name in endpoints_to_test:
            try:
                print(f"\n=== {name} ({method} {endpoint}) ===")
                
                if method == "GET":
                    response = await client.get(f"{base_url}{endpoint}")
                else:
                    response = await client.post(f"{base_url}{endpoint}", json=data)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"Response type: {type(response_data)}")
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                else:
                    print(f"Error: {response.text}")
                    
            except Exception as e:
                print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_responses())