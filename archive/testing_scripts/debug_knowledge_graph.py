#!/usr/bin/env python3

import asyncio
import json
from src.daniel_lightrag_mcp.client import LightRAGClient

async def debug_knowledge_graph():
    """Debug knowledge graph access."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🔍 DEBUGGING KNOWLEDGE GRAPH ACCESS")
    print("=" * 50)
    
    # 1. Check available labels
    print("1. Getting available labels...")
    try:
        labels = await client.get_graph_labels()
        print(f"✅ Available labels: {labels}")
    except Exception as e:
        print(f"❌ Labels error: {e}")
    
    # 2. Try different label parameters
    test_labels = ["all", "", "entity", "relation", "ENTITY", "RELATION"]
    
    for label in test_labels:
        print(f"\n2. Testing knowledge graph with label='{label}'...")
        try:
            result = await client.get_knowledge_graph(label)
            print(f"✅ Label '{label}': Found {len(result.entities)} entities, {len(result.relations)} relations")
            if result.entities:
                print(f"   Sample entities: {result.entities[:3]}")
        except Exception as e:
            print(f"❌ Label '{label}' error: {e}")
    
    # 3. Try raw API call to see actual response
    print(f"\n3. Raw API call to /graphs...")
    try:
        response_data = await client._make_request("GET", "/graphs", params={"label": "all"})
        print(f"Raw response: {json.dumps(response_data, indent=2)}")
    except Exception as e:
        print(f"❌ Raw API error: {e}")
    
    # 4. Try without label parameter
    print(f"\n4. Raw API call without label parameter...")
    try:
        response_data = await client._make_request("GET", "/graphs")
        print(f"Raw response: {json.dumps(response_data, indent=2)}")
    except Exception as e:
        print(f"❌ Raw API error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_knowledge_graph())