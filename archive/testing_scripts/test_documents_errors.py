#!/usr/bin/env python3

import asyncio
import json
from src.daniel_lightrag_mcp.client import LightRAGClient

async def test_documents_errors():
    """Test the two get_documents tools to show exact current errors."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🔍 TESTING GET_DOCUMENTS TOOLS - CURRENT ERRORS")
    print("=" * 60)
    
    # 1. Test get_documents
    print("1. Testing get_documents...")
    print("-" * 30)
    try:
        result = await client.get_documents()
        print(f"✅ get_documents SUCCESS: {result}")
    except Exception as e:
        print(f"❌ get_documents FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try raw API call to see server response
        try:
            print("   Raw API call:")
            raw_response = await client._make_request("GET", "/documents")
            print(f"   Raw response: {json.dumps(raw_response, indent=2)}")
        except Exception as raw_e:
            print(f"   Raw API also failed: {raw_e}")
    
    print()
    
    # 2. Test get_documents_paginated
    print("2. Testing get_documents_paginated...")
    print("-" * 30)
    try:
        result = await client.get_documents_paginated(page=1, page_size=10)
        print(f"✅ get_documents_paginated SUCCESS: {result}")
    except Exception as e:
        print(f"❌ get_documents_paginated FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try raw API call to see server response
        try:
            print("   Raw API call:")
            raw_response = await client._make_request("POST", "/documents/paginated", {
                "page": 1,
                "page_size": 10
            })
            print(f"   Raw response: {json.dumps(raw_response, indent=2)}")
        except Exception as raw_e:
            print(f"   Raw API also failed: {raw_e}")
    
    print()
    print("=" * 60)
    print("SUMMARY OF CURRENT ERRORS")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_documents_errors())