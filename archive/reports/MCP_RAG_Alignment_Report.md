# MCP Server to RAG Server Alignment Report

## Executive Summary

After reviewing the comprehensive API documentation and OpenAPI specification against the MCP server implementation, I've identified **critical mismatches** between what the RAG server actually returns and what the MCP server expects. The validation errors in the logs are caused by **response schema mismatches** where field names and structures don't align.

## Critical Issues Identified

### 1. **query_text** - MAJOR MISMATCH
**RAG Server Returns:**
```json
{
  "response": "string"
}
```

**MCP Server Expects (QueryResponse model):**
```json
{
  "response": "string",
  "query": "string|null",        // ❌ MISSING - REQUIRED FIELD
  "results": [...],
  "total_results": int,
  "processing_time": float,
  "context": "string"
}
```

**Issue:** The `query` field is marked as required in the MCP model but not returned by RAG server.

### 2. **get_pipeline_status** - MAJOR MISMATCH
**RAG Server Returns (PipelineStatusResponse schema):**
```json
{
  "autoscanned": false,
  "busy": false,
  "job_name": "Default Job",
  "job_start": "string",
  "docs": 0,
  "batchs": 0,
  "cur_batch": 0,
  "request_pending": false,
  "latest_message": "",
  "history_messages": ["string"],
  "update_status": {}
}
```

**MCP Server Expects:**
```json
{
  "autoscanned": bool,
  "busy": bool,
  "status": "string",           // ❌ MISSING - REQUIRED FIELD
  // ... other fields
}
```

**Issue:** MCP model incorrectly expects a `status` field that doesn't exist in RAG response.

### 3. **get_track_status** - MAJOR MISMATCH
**RAG Server Returns (TrackStatusResponse schema):**
```json
{
  "track_id": "string",
  "documents": [...],
  "total_count": 1,
  "status_summary": {}
}
```

**MCP Server Expects:**
```json
{
  "track_id": "string",
  "documents": [...],
  "total_count": int,
  "status_summary": {},
  "status": "string"           // ❌ MISSING - REQUIRED FIELD
}
```

**Issue:** MCP model incorrectly expects a `status` field.

### 4. **clear_documents** - MAJOR MISMATCH
**RAG Server Returns (ClearDocumentsResponse schema):**
```json
{
  "status": "success",
  "message": "All documents cleared successfully. Deleted 15 files."
}
```

**MCP Server Expects:**
```json
{
  "status": "string",
  "message": "string|null",
  "cleared": bool,             // ❌ MISSING - REQUIRED FIELD
  "count": int                 // ❌ MISSING - REQUIRED FIELD
}
```

**Issue:** MCP model expects `cleared` and `count` fields that don't exist.

### 5. **clear_cache** - MAJOR MISMATCH
**RAG Server Returns (ClearCacheResponse schema):**
```json
{
  "status": "success",
  "message": "Successfully cleared cache for modes: ['default', 'naive']"
}
```

**MCP Server Expects:**
```json
{
  "status": "string",
  "message": "string",
  "cache_type": "string|null",
  "cleared": bool              // ❌ MISSING - REQUIRED FIELD
}
```

**Issue:** MCP model expects `cleared` field that doesn't exist.

### 6. **get_graph_labels** - POTENTIAL MISMATCH
**RAG Server Returns:** `List[str]` (array of strings)

**MCP Server Expects (LabelsResponse model):**
```json
{
  "entity_labels": ["string"],
  "relation_labels": ["string"]
}
```

**Issue:** Server returns simple array, MCP expects structured object. Code has workaround but may be fragile.

## Correctly Aligned Endpoints

The following endpoints appear to be correctly aligned:

1. **insert_text** - ✅ Aligned with InsertResponse
2. **insert_texts** - ✅ Aligned with InsertResponse  
3. **upload_document** - ✅ Aligned with InsertResponse
4. **scan_documents** - ✅ Aligned with ScanResponse
5. **get_documents** - ✅ Aligned with DocsStatusesResponse
6. **get_documents_paginated** - ✅ Aligned with PaginatedDocsResponse
7. **delete_document** - ✅ Aligned with DeleteDocByIdResponse
8. **get_knowledge_graph** - ✅ Aligned (uses nodes/edges structure)
9. **check_entity_exists** - ✅ Aligned with EntityExistsResponse
10. **update_entity** - ✅ Aligned with EntityUpdateResponse
11. **update_relation** - ✅ Aligned with RelationUpdateResponse
12. **delete_entity** - ✅ Aligned with DeletionResult
13. **delete_relation** - ✅ Aligned with DeletionResult
14. **get_document_status_counts** - ✅ Aligned with StatusCountsResponse
15. **get_health** - ✅ Aligned with HealthResponse
16. **query_text_stream** - ✅ Aligned (streaming handled correctly)

## Implementation Plan

### Phase 1: Fix Critical Response Model Mismatches

#### 1.1 Fix QueryResponse Model
**File:** `src/daniel_lightrag_mcp/models.py`
**Change:** Make `query` field optional in QueryResponse
```python
class QueryResponse(BaseModel):
    response: str = Field(..., description="Query response text")
    query: Optional[str] = None  # ❌ Change from required to optional
    # ... rest unchanged
```

#### 1.2 Fix PipelineStatusResponse Model
**File:** `src/daniel_lightrag_mcp/models.py`
**Change:** Remove non-existent `status` field, ensure all fields match RAG schema
```python
class PipelineStatusResponse(BaseModel):
    autoscanned: bool = Field(..., description="Whether auto-scanning is enabled")
    busy: bool = Field(..., description="Whether pipeline is busy")
    # ❌ REMOVE: status field doesn't exist in RAG response
    job_name: Optional[str] = None
    job_start: Optional[str] = None
    docs: Optional[int] = None
    batchs: Optional[int] = None
    cur_batch: Optional[int] = None
    request_pending: Optional[bool] = None
    latest_message: Optional[str] = None
    history_messages: Optional[List[str]] = None
    update_status: Optional[Dict[str, Any]] = None
    # Remove fields not in RAG response:
    # progress, current_task, message
```

#### 1.3 Fix TrackStatusResponse Model
**File:** `src/daniel_lightrag_mcp/models.py`
**Change:** Remove non-existent `status` field
```python
class TrackStatusResponse(BaseModel):
    track_id: str = Field(..., description="Track ID")
    documents: List[Dict[str, Any]] = Field(default_factory=list, description="Documents in track")
    total_count: int = Field(0, description="Total document count")
    status_summary: Dict[str, Any] = Field(default_factory=dict, description="Status summary")
    # ❌ REMOVE: status field doesn't exist in RAG response
```

#### 1.4 Fix ClearDocumentsResponse Model
**File:** `src/daniel_lightrag_mcp/models.py`
**Change:** Remove non-existent fields
```python
class ClearDocumentsResponse(BaseModel):
    status: str = Field(..., description="Clearing status")
    message: Optional[str] = None
    # ❌ REMOVE: cleared and count fields don't exist in RAG response
```

#### 1.5 Fix ClearCacheResponse Model
**File:** `src/daniel_lightrag_mcp/models.py`
**Change:** Remove non-existent `cleared` field
```python
class ClearCacheResponse(BaseModel):
    status: str = Field(..., description="Cache clearing status")
    message: str = Field(..., description="Status message")
    cache_type: Optional[str] = None
    # ❌ REMOVE: cleared field doesn't exist in RAG response
    # Note: duplicate message field in original - keep one
```

### Phase 2: Verify Graph Labels Handling

#### 2.1 Review get_graph_labels Implementation
**File:** `src/daniel_lightrag_mcp/client.py`
**Current workaround:**
```python
# Server returns a list, but our model expects a dict with labels field
if isinstance(response_data, list):
    response_data = {"labels": response_data}
```

**Action:** Verify this works correctly or update LabelsResponse model to match actual RAG response.

### Phase 3: Testing and Validation

#### 3.1 Update Test Expectations
- Update comprehensive test to expect correct response formats
- Remove assumptions about non-existent fields

#### 3.2 Integration Testing
- Test each fixed endpoint individually
- Verify no regression in working endpoints
- Test with actual RAG server responses

## Risk Assessment

**High Risk:**
- Query functionality is critical - `query_text` fix is highest priority
- Pipeline status monitoring may be used by monitoring systems

**Medium Risk:**
- Cache and document clearing operations
- Track status monitoring

**Low Risk:**
- Graph operations (mostly working)
- Document management (mostly working)

## Success Criteria

1. All 22 MCP tools pass validation without Pydantic errors
2. Real-world query operations work correctly
3. No regression in currently working endpoints
4. Comprehensive test passes 100%

## Next Steps

1. **Immediate:** Fix the 5 critical response model mismatches
2. **Verify:** Test fixes against actual RAG server
3. **Validate:** Run comprehensive test suite
4. **Monitor:** Check logs for any remaining validation errors

This plan addresses the root cause of the validation errors seen in the logs and ensures proper alignment between MCP server expectations and RAG server responses.