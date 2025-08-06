#!/usr/bin/env python3

import asyncio
import json
import tempfile
import os
from src.daniel_lightrag_mcp.client import LightRAGClient

async def investigate_failing_tools():
    """Investigate each failing tool to understand the root cause."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🔍 INVESTIGATING FAILING TOOLS")
    print("=" * 50)
    
    # 1. UPLOAD_DOCUMENT - Test setup issue?
    print("\n1. INVESTIGATING upload_document")
    print("-" * 30)
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("This is a test document for upload.")
        temp_file = f.name
    
    try:
        print(f"Created temp file: {temp_file}")
        result = await client.upload_document(temp_file)
        print(f"✅ upload_document SUCCESS: {result}")
    except Exception as e:
        print(f"❌ upload_document FAILED: {e}")
    finally:
        os.unlink(temp_file)
    
    # 2. GET_DOCUMENTS - Server-side validation error
    print("\n2. INVESTIGATING get_documents")
    print("-" * 30)
    try:
        # Try raw request to see server response
        response_data = await client._make_request("GET", "/documents")
        print(f"Raw server response: {json.dumps(response_data, indent=2)}")
        
        # Try parsing with our model
        from src.daniel_lightrag_mcp.models import DocumentsResponse
        parsed = DocumentsResponse(**response_data)
        print("✅ get_documents model parsing successful")
        
    except Exception as e:
        print(f"❌ get_documents FAILED: {e}")
    
    # 3. GET_DOCUMENTS_PAGINATED - Server-side validation error  
    print("\n3. INVESTIGATING get_documents_paginated")
    print("-" * 30)
    try:
        response_data = await client._make_request("POST", "/documents/paginated", {"page": 1, "page_size": 10})
        print(f"Raw server response: {json.dumps(response_data, indent=2)}")
        
        from src.daniel_lightrag_mcp.models import PaginatedDocsResponse
        parsed = PaginatedDocsResponse(**response_data)
        print("✅ get_documents_paginated model parsing successful")
        
    except Exception as e:
        print(f"❌ get_documents_paginated FAILED: {e}")
    
    # 4. ENTITY/RELATION OPERATIONS - Need to create entities first?
    print("\n4. INVESTIGATING entity/relation operations")
    print("-" * 30)
    
    # First, let's see what entities exist
    try:
        graph = await client.get_knowledge_graph()
        print(f"Current graph entities: {len(graph.entities)} entities")
        if graph.entities:
            print(f"Sample entity: {graph.entities[0]}")
            
            # Try updating an existing entity
            existing_entity = graph.entities[0]
            entity_id = existing_entity.id if hasattr(existing_entity, 'id') else str(existing_entity)
            entity_name = existing_entity.name if hasattr(existing_entity, 'name') else str(existing_entity)
            
            print(f"Trying to update existing entity: {entity_id}")
            result = await client.update_entity(entity_id, {"test": "value"}, entity_name)
            print(f"✅ update_entity SUCCESS: {result}")
        else:
            print("No entities exist - need to create some first")
            
            # Try to create entities by inserting documents first
            print("Inserting documents to create entities...")
            await client.insert_text("John works at Microsoft. He is a software engineer.")
            await client.insert_text("Microsoft is a technology company founded by Bill Gates.")
            
            # Wait a bit for processing
            import time
            time.sleep(2)
            
            # Check graph again
            graph = await client.get_knowledge_graph()
            print(f"After inserting documents: {len(graph.entities)} entities")
            
            if graph.entities:
                existing_entity = graph.entities[0]
                entity_id = existing_entity.id if hasattr(existing_entity, 'id') else str(existing_entity)
                entity_name = existing_entity.name if hasattr(existing_entity, 'name') else str(existing_entity)
                
                print(f"Trying to update newly created entity: {entity_id}")
                result = await client.update_entity(entity_id, {"test": "value"}, entity_name)
                print(f"✅ update_entity SUCCESS: {result}")
            
    except Exception as e:
        print(f"❌ Entity operations investigation FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(investigate_failing_tools())