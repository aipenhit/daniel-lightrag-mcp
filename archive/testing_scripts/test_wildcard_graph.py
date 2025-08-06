#!/usr/bin/env python3

import asyncio
import json
from src.daniel_lightrag_mcp.client import LightRAGClient

async def test_wildcard_graph():
    """Test knowledge graph with wildcard label."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🔍 TESTING KNOWLEDGE GRAPH WITH WILDCARD")
    print("=" * 50)
    
    # Test with wildcard
    print("Testing knowledge graph with label='*'...")
    try:
        result = await client.get_knowledge_graph("*")
        print(f"✅ Wildcard SUCCESS: Found {len(result.entities)} entities, {len(result.relations)} relations")
        
        if result.entities:
            print(f"\n📊 ENTITIES FOUND:")
            for i, entity in enumerate(result.entities[:10]):  # Show first 10
                print(f"   {i+1}. {entity}")
            if len(result.entities) > 10:
                print(f"   ... and {len(result.entities) - 10} more entities")
        
        if result.relations:
            print(f"\n🔗 RELATIONS FOUND:")
            for i, relation in enumerate(result.relations[:5]):  # Show first 5
                print(f"   {i+1}. {relation}")
            if len(result.relations) > 5:
                print(f"   ... and {len(result.relations) - 5} more relations")
                
        return result
        
    except Exception as e:
        print(f"❌ Wildcard error: {e}")
        return None

async def test_entity_operations_with_real_entities():
    """Test entity operations if we find real entities."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    # First get entities with wildcard
    graph_result = await test_wildcard_graph()
    
    if not graph_result or not graph_result.entities:
        print("\n❌ No entities found - cannot test entity operations")
        return
    
    print(f"\n🧪 TESTING ENTITY OPERATIONS WITH REAL ENTITIES")
    print("=" * 50)
    
    # Get first entity for testing
    first_entity = graph_result.entities[0]
    print(f"Using first entity for testing: {first_entity}")
    
    # Extract entity details
    if isinstance(first_entity, dict):
        entity_id = first_entity.get('id', str(first_entity))
        entity_name = first_entity.get('name', first_entity.get('label', str(first_entity)))
    else:
        entity_id = str(first_entity)
        entity_name = str(first_entity)
    
    print(f"Entity ID: '{entity_id}'")
    print(f"Entity Name: '{entity_name}'")
    
    # Test check_entity_exists
    print(f"\n1. Testing check_entity_exists...")
    try:
        exists_result = await client.check_entity_exists(entity_name)
        print(f"✅ check_entity_exists SUCCESS: {exists_result}")
    except Exception as e:
        print(f"❌ check_entity_exists FAILED: {e}")
    
    # Test update_entity (NO DELETE - just update)
    print(f"\n2. Testing update_entity...")
    try:
        update_result = await client.update_entity(entity_id, {"test_property": "test_value"}, entity_name)
        print(f"✅ update_entity SUCCESS: {update_result}")
    except Exception as e:
        print(f"❌ update_entity FAILED: {e}")
    
    # Test relations if available
    if graph_result.relations:
        first_relation = graph_result.relations[0]
        print(f"\n3. Testing relation operations with: {first_relation}")
        
        # Extract relation details
        if isinstance(first_relation, dict):
            relation_id = first_relation.get('id', str(first_relation))
            source_id = first_relation.get('source', first_relation.get('from', 'unknown'))
            target_id = first_relation.get('target', first_relation.get('to', 'unknown'))
        else:
            relation_id = str(first_relation)
            source_id = "unknown"
            target_id = "unknown"
        
        try:
            relation_result = await client.update_relation(relation_id, {"test_weight": 0.9}, source_id, target_id)
            print(f"✅ update_relation SUCCESS: {relation_result}")
        except Exception as e:
            print(f"❌ update_relation FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_entity_operations_with_real_entities())