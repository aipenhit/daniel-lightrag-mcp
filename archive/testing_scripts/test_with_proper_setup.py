#!/usr/bin/env python3

import asyncio
import json
from src.daniel_lightrag_mcp.client import LightRAGClient

async def test_all_tools_properly():
    """Test all tools with proper setup - no delete operations."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🧪 TESTING ALL TOOLS WITH PROPER SETUP")
    print("=" * 60)
    print("⚠️  NO DELETE OPERATIONS WILL BE PERFORMED")
    print("📁 Using test file: /Users/danielsimpkins/Documents/Cline/VSCode_Projects/daniel-lightrag-mcp/test.txt")
    print("📊 Database has 3 documents")
    print()
    
    results = {}
    
    # 1. UPLOAD_DOCUMENT - Using the provided test file
    print("1. Testing upload_document with real file...")
    try:
        result = await client.upload_document("/Users/danielsimpkins/Documents/Cline/VSCode_Projects/daniel-lightrag-mcp/test.txt")
        print(f"✅ upload_document SUCCESS: {result}")
        results["upload_document"] = "SUCCESS"
    except Exception as e:
        print(f"❌ upload_document FAILED: {e}")
        results["upload_document"] = f"FAILED: {e}"
    
    # 2. GET_DOCUMENTS - Should work now with documents in database
    print("\n2. Testing get_documents with populated database...")
    try:
        result = await client.get_documents()
        print(f"✅ get_documents SUCCESS: Found {len(result.statuses)} status groups")
        for status, docs in result.statuses.items():
            print(f"   - {status}: {len(docs)} documents")
        results["get_documents"] = "SUCCESS"
    except Exception as e:
        print(f"❌ get_documents FAILED: {e}")
        results["get_documents"] = f"FAILED: {e}"
    
    # 3. GET_DOCUMENTS_PAGINATED - Should work now
    print("\n3. Testing get_documents_paginated...")
    try:
        result = await client.get_documents_paginated(page=1, page_size=10)
        print(f"✅ get_documents_paginated SUCCESS: Found {len(result.documents)} documents")
        print(f"   - Total count: {result.pagination.total_count}")
        print(f"   - Status counts: {result.status_counts}")
        results["get_documents_paginated"] = "SUCCESS"
    except Exception as e:
        print(f"❌ get_documents_paginated FAILED: {e}")
        results["get_documents_paginated"] = f"FAILED: {e}"
    
    # 4. GET_KNOWLEDGE_GRAPH - Check what entities exist
    print("\n4. Testing get_knowledge_graph to see available entities...")
    try:
        result = await client.get_knowledge_graph()
        print(f"✅ get_knowledge_graph SUCCESS: Found {len(result.entities)} entities")
        if result.entities:
            print("   Available entities:")
            for i, entity in enumerate(result.entities[:5]):  # Show first 5
                entity_info = entity if isinstance(entity, dict) else str(entity)
                print(f"     {i+1}. {entity_info}")
            if len(result.entities) > 5:
                print(f"     ... and {len(result.entities) - 5} more")
        results["get_knowledge_graph"] = "SUCCESS"
        
        # Store entities for later testing
        available_entities = result.entities
        
    except Exception as e:
        print(f"❌ get_knowledge_graph FAILED: {e}")
        results["get_knowledge_graph"] = f"FAILED: {e}"
        available_entities = []
    
    # 5. TEST ENTITY OPERATIONS with real entities (if any exist)
    if available_entities:
        print(f"\n5. Testing entity operations with real entities...")
        try:
            # Get first entity details
            first_entity = available_entities[0]
            if isinstance(first_entity, dict):
                entity_id = first_entity.get('id', str(first_entity))
                entity_name = first_entity.get('name', str(first_entity))
            else:
                entity_id = str(first_entity)
                entity_name = str(first_entity)
            
            print(f"   Using entity: ID='{entity_id}', Name='{entity_name}'")
            
            # Test check_entity_exists with real entity
            exists_result = await client.check_entity_exists(entity_name)
            print(f"✅ check_entity_exists SUCCESS: {exists_result}")
            results["check_entity_exists"] = "SUCCESS"
            
            # Test update_entity with real entity (NO DELETE - just update)
            update_result = await client.update_entity(entity_id, {"test_property": "test_value"}, entity_name)
            print(f"✅ update_entity SUCCESS: {update_result}")
            results["update_entity"] = "SUCCESS"
            
        except Exception as e:
            print(f"❌ Entity operations FAILED: {e}")
            results["update_entity"] = f"FAILED: {e}"
            results["check_entity_exists"] = f"FAILED: {e}"
    else:
        print("\n5. No entities available for testing entity operations")
        results["update_entity"] = "NO_ENTITIES_AVAILABLE"
        results["check_entity_exists"] = "NO_ENTITIES_AVAILABLE"
    
    # 6. TEST OTHER WORKING TOOLS (quick verification)
    print("\n6. Quick verification of other tools...")
    
    # insert_text
    try:
        result = await client.insert_text("Test verification text")
        print("✅ insert_text verified")
        results["insert_text"] = "SUCCESS"
    except Exception as e:
        print(f"❌ insert_text: {e}")
        results["insert_text"] = f"FAILED: {e}"
    
    # query_text
    try:
        result = await client.query_text("test query")
        print("✅ query_text verified")
        results["query_text"] = "SUCCESS"
    except Exception as e:
        print(f"❌ query_text: {e}")
        results["query_text"] = f"FAILED: {e}"
    
    # get_health
    try:
        result = await client.get_health()
        print("✅ get_health verified")
        results["get_health"] = "SUCCESS"
    except Exception as e:
        print(f"❌ get_health: {e}")
        results["get_health"] = f"FAILED: {e}"
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for result in results.values() if result == "SUCCESS")
    total_tested = len(results)
    
    print(f"✅ SUCCESS: {success_count}/{total_tested} tools working")
    print()
    
    for tool, result in results.items():
        status_icon = "✅" if result == "SUCCESS" else "❌" if "FAILED" in result else "⚠️"
        print(f"{status_icon} {tool}: {result}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_tools_properly())