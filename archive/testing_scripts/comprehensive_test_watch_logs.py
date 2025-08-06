#!/usr/bin/env python3

import asyncio
import json
from src.daniel_lightrag_mcp.client import LightRAGClient

async def comprehensive_test():
    """Run comprehensive tests - watch server logs to identify problematic command."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🧪 COMPREHENSIVE TEST - WATCH SERVER LOGS FOR CORRUPTION")
    print("=" * 70)
    print("⚠️  Watch the server logs to identify which command causes file_path=null")
    print()
    
    # Test 1: Document operations
    print("1. Testing document operations...")
    print("-" * 40)
    
    try:
        print("   1.1 insert_text...")
        result = await client.insert_text("Test document for log watching")
        print(f"   ✅ insert_text: {result.status}")
    except Exception as e:
        print(f"   ❌ insert_text: {e}")
    
    try:
        print("   1.2 insert_texts...")
        result = await client.insert_texts([
            {"title": "Test 1", "content": "Content 1"},
            {"title": "Test 2", "content": "Content 2"}
        ])
        print(f"   ✅ insert_texts: {result.status}")
    except Exception as e:
        print(f"   ❌ insert_texts: {e}")
    
    try:
        print("   1.3 scan_documents...")
        result = await client.scan_documents()
        print(f"   ✅ scan_documents: {result.status}")
    except Exception as e:
        print(f"   ❌ scan_documents: {e}")
    
    # Test 2: Check documents after each operation
    print("\n2. Checking documents after document operations...")
    print("-" * 40)
    
    try:
        result = await client.get_documents()
        print(f"   ✅ get_documents still works: {len(result.statuses)} status groups")
    except Exception as e:
        print(f"   ❌ get_documents BROKEN after document operations: {e}")
        return  # Stop here if broken
    
    # Test 3: Knowledge graph operations
    print("\n3. Testing knowledge graph operations...")
    print("-" * 40)
    
    try:
        print("   3.1 get_knowledge_graph...")
        result = await client.get_knowledge_graph("*")
        print(f"   ✅ get_knowledge_graph: {len(result.entities)} entities")
        
        if result.entities:
            first_entity = result.entities[0]
            entity_id = first_entity['id']
            entity_name = first_entity['id']
            
            print("   3.2 check_entity_exists...")
            exists_result = await client.check_entity_exists(entity_name)
            print(f"   ✅ check_entity_exists: {exists_result.exists}")
            
            print("   3.3 update_entity...")
            update_result = await client.update_entity(entity_id, {"test_prop": "test_val"}, entity_name)
            print(f"   ✅ update_entity: {update_result.status}")
            
    except Exception as e:
        print(f"   ❌ Knowledge graph operations: {e}")
    
    # Test 4: Check documents after knowledge graph operations
    print("\n4. Checking documents after knowledge graph operations...")
    print("-" * 40)
    
    try:
        result = await client.get_documents()
        print(f"   ✅ get_documents still works: {len(result.statuses)} status groups")
    except Exception as e:
        print(f"   ❌ get_documents BROKEN after knowledge graph operations: {e}")
        return  # Stop here if broken
    
    # Test 5: System operations
    print("\n5. Testing system operations...")
    print("-" * 40)
    
    try:
        print("   5.1 get_pipeline_status...")
        result = await client.get_pipeline_status()
        print(f"   ✅ get_pipeline_status: busy={result.busy}")
    except Exception as e:
        print(f"   ❌ get_pipeline_status: {e}")
    
    try:
        print("   5.2 get_document_status_counts...")
        result = await client.get_document_status_counts()
        print(f"   ✅ get_document_status_counts: {result.status_counts}")
    except Exception as e:
        print(f"   ❌ get_document_status_counts: {e}")
    
    try:
        print("   5.3 clear_cache...")
        result = await client.clear_cache()
        print(f"   ✅ clear_cache: {result.status}")
    except Exception as e:
        print(f"   ❌ clear_cache: {e}")
    
    # Test 6: Final check
    print("\n6. Final document check...")
    print("-" * 40)
    
    try:
        result = await client.get_documents()
        print(f"   ✅ get_documents FINAL: {len(result.statuses)} status groups")
        print("   🎉 No corruption detected!")
    except Exception as e:
        print(f"   ❌ get_documents BROKEN at end: {e}")
        print("   🔍 Check server logs to see which operation caused corruption!")

if __name__ == "__main__":
    asyncio.run(comprehensive_test())