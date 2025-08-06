#!/usr/bin/env python3

import asyncio
from src.daniel_lightrag_mcp.client import LightRAGClient

async def test_file_source_fix():
    """Test the file_source fix for insert operations."""
    client = LightRAGClient(api_key="lightragsecretkey")
    
    print("🧪 TESTING FILE_SOURCE FIX")
    print("=" * 50)
    print("⚠️  Watch server logs - should NOT see 'unknown_source' or 'None' filenames")
    print()
    
    # Test 1: insert_text with proper file_source
    print("1. Testing insert_text with file_source...")
    try:
        result = await client.insert_text("Test text with proper file source", title="test_document")
        print(f"✅ insert_text: {result.status}")
    except Exception as e:
        print(f"❌ insert_text: {e}")
    
    # Test 2: insert_texts with proper file_sources
    print("\n2. Testing insert_texts with file_sources...")
    try:
        result = await client.insert_texts([
            {"title": "Test 1", "content": "Content 1 with file source"},
            {"title": "Test 2", "content": "Content 2 with file source"}
        ])
        print(f"✅ insert_texts: {result.status}")
    except Exception as e:
        print(f"❌ insert_texts: {e}")
    
    # Test 3: Check if documents work now
    print("\n3. Testing get_documents after fix...")
    try:
        result = await client.get_documents()
        print(f"✅ get_documents: {len(result.statuses)} status groups")
        for status, docs in result.statuses.items():
            print(f"   - {status}: {len(docs)} documents")
            for doc in docs[:2]:  # Show first 2 docs
                print(f"     * {doc.get('id', 'no-id')}: file_path='{doc.get('file_path', 'NO FILE_PATH')}'")
    except Exception as e:
        print(f"❌ get_documents STILL BROKEN: {e}")
    
    print("\n" + "=" * 50)
    print("Check server logs for 'unknown_source' or 'None' filenames")

if __name__ == "__main__":
    asyncio.run(test_file_source_fix())