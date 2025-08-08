#!/usr/bin/env python3

"""
Test script to verify that the model fixes are working correctly.
"""

import json
from src.daniel_lightrag_mcp.models import (
    QueryResponse, PipelineStatusResponse, TrackStatusResponse, 
    ClearDocumentsResponse, ClearCacheResponse, LabelsResponse
)

def test_query_response():
    """Test QueryResponse with missing query field."""
    print("Testing QueryResponse...")
    
    # This should work now (query field is optional)
    response_data = {"response": "This is a test response"}
    try:
        result = QueryResponse(**response_data)
        print(f"✅ QueryResponse: {result.response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ QueryResponse failed: {e}")
        return False

def test_pipeline_status_response():
    """Test PipelineStatusResponse without status field."""
    print("Testing PipelineStatusResponse...")
    
    # This should work now (no status field required)
    response_data = {
        "autoscanned": False,
        "busy": False,
        "job_name": "Default Job",
        "docs": 0,
        "batchs": 0,
        "cur_batch": 0,
        "request_pending": False,
        "latest_message": "",
        "history_messages": [],
        "update_status": {}
    }
    try:
        result = PipelineStatusResponse(**response_data)
        print(f"✅ PipelineStatusResponse: busy={result.busy}, autoscanned={result.autoscanned}")
        return True
    except Exception as e:
        print(f"❌ PipelineStatusResponse failed: {e}")
        return False

def test_track_status_response():
    """Test TrackStatusResponse without status field."""
    print("Testing TrackStatusResponse...")
    
    # This should work now (no status field required)
    response_data = {
        "track_id": "test_track_123",
        "documents": [],
        "total_count": 0,
        "status_summary": {}
    }
    try:
        result = TrackStatusResponse(**response_data)
        print(f"✅ TrackStatusResponse: track_id={result.track_id}, total_count={result.total_count}")
        return True
    except Exception as e:
        print(f"❌ TrackStatusResponse failed: {e}")
        return False

def test_clear_documents_response():
    """Test ClearDocumentsResponse without cleared/count fields."""
    print("Testing ClearDocumentsResponse...")
    
    # This should work now (no cleared/count fields required)
    response_data = {
        "status": "success",
        "message": "All documents cleared successfully. Deleted 15 files."
    }
    try:
        result = ClearDocumentsResponse(**response_data)
        print(f"✅ ClearDocumentsResponse: status={result.status}")
        return True
    except Exception as e:
        print(f"❌ ClearDocumentsResponse failed: {e}")
        return False

def test_clear_cache_response():
    """Test ClearCacheResponse without cleared field."""
    print("Testing ClearCacheResponse...")
    
    # This should work now (no cleared field required)
    response_data = {
        "status": "success",
        "message": "Successfully cleared cache for modes: ['default', 'naive']"
    }
    try:
        result = ClearCacheResponse(**response_data)
        print(f"✅ ClearCacheResponse: status={result.status}")
        return True
    except Exception as e:
        print(f"❌ ClearCacheResponse failed: {e}")
        return False

def test_labels_response():
    """Test LabelsResponse with our workaround."""
    print("Testing LabelsResponse...")
    
    # Test the format our client creates
    response_data = {
        "entity_labels": ["AWS", "Machine Learning", "Cloud Computing"],
        "relation_labels": []
    }
    try:
        result = LabelsResponse(**response_data)
        print(f"✅ LabelsResponse: {len(result.entity_labels)} entity labels, {len(result.relation_labels)} relation labels")
        return True
    except Exception as e:
        print(f"❌ LabelsResponse failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Model Fixes")
    print("=" * 50)
    
    tests = [
        test_query_response,
        test_pipeline_status_response,
        test_track_status_response,
        test_clear_documents_response,
        test_clear_cache_response,
        test_labels_response
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All model fixes are working correctly!")
        return True
    else:
        print("❌ Some model fixes need attention")
        return False

if __name__ == "__main__":
    main()