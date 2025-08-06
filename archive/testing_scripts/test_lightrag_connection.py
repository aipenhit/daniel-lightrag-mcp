#!/usr/bin/env python3
"""
Test script to diagnose LightRAG server connectivity and available endpoints.
"""

import asyncio
import sys
import os
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daniel_lightrag_mcp.client import LightRAGClient, LightRAGError

async def test_lightrag_connection():
    """Test LightRAG server connection and endpoints."""
    
    base_url = os.getenv("LIGHTRAG_BASE_URL", "http://localhost:9621")
    api_key = os.getenv("LIGHTRAG_API_KEY")
    print(f"Testing LightRAG server at: {base_url}")
    print(f"Using API key: {api_key[:10] + '...' if api_key else 'None'}")
    print("=" * 50)
    
    client = LightRAGClient(base_url=base_url, api_key=api_key)
    
    # Test basic connectivity
    print("1. Testing basic connectivity...")
    try:
        health_result = await client.get_health()
        print(f"✅ Health check successful: {health_result}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("   Make sure LightRAG server is running on", base_url)
        return
    
    # Test each endpoint category
    test_cases = [
        # Document Management
        ("insert_text", lambda: client.insert_text("Test document for connectivity check")),
        ("get_documents", lambda: client.get_documents()),
        ("scan_documents", lambda: client.scan_documents()),
        ("get_documents_paginated", lambda: client.get_documents_paginated(1, 10)),
        
        # Query Operations  
        ("query_text", lambda: client.query_text("test query", mode="hybrid")),
        
        # Knowledge Graph
        ("get_knowledge_graph", lambda: client.get_knowledge_graph()),
        ("get_graph_labels", lambda: client.get_graph_labels()),
        ("check_entity_exists", lambda: client.check_entity_exists("test_entity")),
        
        # System Management
        ("get_pipeline_status", lambda: client.get_pipeline_status()),
        ("get_document_status_counts", lambda: client.get_document_status_counts()),
        ("clear_cache", lambda: client.clear_cache()),
    ]
    
    print("\n2. Testing individual endpoints...")
    working_endpoints = []
    failing_endpoints = []
    
    for endpoint_name, test_func in test_cases:
        try:
            print(f"   Testing {endpoint_name}...", end=" ")
            result = await test_func()
            print("✅ SUCCESS")
            working_endpoints.append(endpoint_name)
            
            # Show a preview of the result
            if hasattr(result, 'model_dump'):
                result_preview = str(result.model_dump())[:100]
            else:
                result_preview = str(result)[:100]
            print(f"      Preview: {result_preview}...")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failing_endpoints.append((endpoint_name, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"✅ Working endpoints ({len(working_endpoints)}): {', '.join(working_endpoints)}")
    print(f"❌ Failing endpoints ({len(failing_endpoints)}):")
    for endpoint, error in failing_endpoints:
        print(f"   - {endpoint}: {error}")
    
    # Cleanup
    await client.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(test_lightrag_connection())