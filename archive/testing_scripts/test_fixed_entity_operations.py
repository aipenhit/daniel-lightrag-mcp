#!/usr/bin/env python3

import asyncio
import json
from src.daniel_lightrag_mcp.client import LightRAGClient

async def test_fixed_entity_operations():
    """Test entity operations with proper entity name extraction."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🧪 TESTING FIXED ENTITY OPERATIONS")
    print("=" * 50)
    
    # Get entities with wildcard
    print("1. Getting entities with wildcard...")
    try:
        graph_result = await client.get_knowledge_graph("*")
        print(f"✅ Found {len(graph_result.entities)} entities, {len(graph_result.relations)} relations")
    except Exception as e:
        print(f"❌ Failed to get graph: {e}")
        return
    
    if not graph_result.entities:
        print("❌ No entities found")
        return
    
    # Get first entity and extract proper ID/name
    first_entity = graph_result.entities[0]
    print(f"\n2. Using entity: {first_entity}")
    
    # FIXED: Extract just the ID, not the whole dict
    entity_id = first_entity['id']  # "AWS"
    entity_name = first_entity['id']  # Use ID as name
    
    print(f"   Entity ID: '{entity_id}'")
    print(f"   Entity Name: '{entity_name}'")
    
    # Test check_entity_exists with proper name
    print(f"\n3. Testing check_entity_exists with name='{entity_name}'...")
    try:
        exists_result = await client.check_entity_exists(entity_name)
        print(f"✅ check_entity_exists SUCCESS: {exists_result}")
    except Exception as e:
        print(f"❌ check_entity_exists FAILED: {e}")
    
    # Test update_entity with proper parameters
    print(f"\n4. Testing update_entity with proper parameters...")
    try:
        update_result = await client.update_entity(entity_id, {"test_property": "test_value"}, entity_name)
        print(f"✅ update_entity SUCCESS: {update_result}")
    except Exception as e:
        print(f"❌ update_entity FAILED: {e}")
        
        # Debug: Try raw API call to see what server expects
        print("   Debugging with raw API call...")
        try:
            raw_response = await client._make_request("POST", "/graph/entity/edit", {
                "entity_name": entity_name,
                "updated_data": {"test_property": "test_value"},
                "allow_rename": False
            })
            print(f"   Raw response: {raw_response}")
        except Exception as raw_e:
            print(f"   Raw API also failed: {raw_e}")
    
    # Test relations
    if graph_result.relations:
        first_relation = graph_result.relations[0]
        print(f"\n5. Testing relation operations...")
        print(f"   Using relation: {first_relation}")
        
        relation_id = first_relation['id']
        source_id = first_relation['source']
        target_id = first_relation['target']
        
        print(f"   Relation ID: '{relation_id}'")
        print(f"   Source: '{source_id}', Target: '{target_id}'")
        
        try:
            # Debug: Raw API call first
            raw_response = await client._make_request("POST", "/graph/relation/edit", {
                "source_id": source_id,
                "target_id": target_id,
                "updated_data": {"test_weight": 0.9}
            })
            print(f"   Raw relation response: {raw_response}")
            
        except Exception as e:
            print(f"❌ update_relation FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_entity_operations())