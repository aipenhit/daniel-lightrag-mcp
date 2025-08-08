# MCP Server to RAG Server API Analysis

This document provides a comprehensive analysis of the 22 MCP tools, their corresponding RAG server endpoints, HTTP request formats, and expected response formats.

## Tool Analysis Table

| MCP Tool Name | RAG Server Endpoint | HTTP Request Format | MCP Expected Response Format | RAG Server Actual Response | Notes |
|---------------|-------------------|-------------------|----------------------------|---------------------------|-------|
| **insert_text** | `POST /documents/text` | `{"text": "string", "file_source": "string"}` | `InsertResponse: {"status": "string", "message": "string", "track_id": "string", "id": "string\|null"}` |  | Uses InsertTextRequest model |
| **insert_texts** | `POST /documents/texts` | `{"texts": ["string"], "file_sources": ["string"]}` | `InsertResponse: {"status": "string", "message": "string", "track_id": "string", "id": "string\|null"}` |  | Uses InsertTextsRequest model |
| **upload_document** | `POST /documents/upload` | Multipart form data with file | `UploadResponse: {"status": "string", "message": "string\|null", "track_id": "string\|null"}` |  | File upload via multipart form |
| **scan_documents** | `POST /documents/scan` | `{}` (empty body) | `ScanResponse: {"status": "string", "message": "string", "track_id": "string", "new_documents": ["string"], "message": "string\|null"}` |  | No request parameters |
| **get_documents** | `GET /documents` | No body (GET request) | `DocumentsResponse: {"statuses": {}}` |  | Simple GET request |
| **get_documents_paginated** | `POST /documents/paginated` | `{"page": int, "page_size": int, "status_filter": "string\|null"}` | `PaginatedDocsResponse: {"documents": [DocumentInfo], "pagination": PaginationInfo, "status_counts": {}}` |  | Uses DocumentsRequest model |
| **delete_document** | `DELETE /documents/delete_document` | `{"doc_ids": ["string"]}` | `DeleteDocByIdResponse: {"status": "string", "message": "string\|null", "doc_id": "string\|null"}` |  | Uses DeleteDocRequest model |
| **clear_documents** | `DELETE /documents` | No body | `ClearDocumentsResponse: {"status": "string", "message": "string\|null"}` |  | Simple DELETE request |
| **query_text** | `POST /query` | `{"query": "string", "mode": "hybrid\|naive\|local\|global", "only_need_context": bool, "stream": false}` | `QueryResponse: {"response": "string", "query": "string\|null", "results": [QueryResult]\|null, "total_results": int\|null, "processing_time": float\|null, "context": "string\|null"}` |  | **VALIDATION ERROR SEEN IN LOGS** |
| **query_text_stream** | `POST /query/stream` | `{"query": "string", "mode": "hybrid\|naive\|local\|global", "only_need_context": bool, "stream": true}` | Streaming text chunks collected into `{"streaming_response": "string"}` |  | Streaming endpoint |
| **get_knowledge_graph** | `GET /graphs` | Query param: `?label=*` | `GraphResponse: {"nodes": [{}], "edges": [{}], "is_truncated": bool}` |  | Uses label query parameter |
| **get_graph_labels** | `GET /graph/label/list` | No body (GET request) | `LabelsResponse: {"entity_labels": ["string"], "relation_labels": ["string"]}` |  | **POTENTIAL MISMATCH**: Server may return list, client expects dict |
| **check_entity_exists** | `GET /graph/entity/exists` | Query param: `?name=entity_name` | `EntityExistsResponse: {"exists": bool, "entity_name": "string\|null", "entity_id": "string\|null"}` |  | Uses name query parameter |
| **update_entity** | `POST /graph/entity/edit` | `{"entity_id": "string", "entity_name": "string", "updated_data": {}}` | `EntityUpdateResponse: {"status": "string", "message": "string", "data": {}}` |  | Uses EntityUpdateRequest model |
| **update_relation** | `POST /graph/relation/edit` | `{"relation_id": "string", "source_id": "string", "target_id": "string", "updated_data": {}}` | `RelationUpdateResponse: {"status": "string", "message": "string", "data": {}}` |  | Uses RelationUpdateRequest model |
| **delete_entity** | `DELETE /documents/delete_entity` | `{"entity_id": "string", "entity_name": "string"}` | `DeletionResult: {"deleted": bool, "id": "string", "type": "string", "message": "string\|null"}` |  | Uses DeleteEntityRequest model |
| **delete_relation** | `DELETE /documents/delete_relation` | `{"relation_id": "string", "source_entity": "string", "target_entity": "string"}` | `DeletionResult: {"deleted": bool, "id": "string", "type": "string", "message": "string\|null"}` |  | Uses DeleteRelationRequest model |
| **get_pipeline_status** | `GET /documents/pipeline_status` | No body (GET request) | `PipelineStatusResponse: {"autoscanned": bool, "busy": bool, "job_name": "string\|null", "job_start": "string\|null", "docs": int\|null, "batchs": int\|null, "cur_batch": int\|null, "request_pending": bool\|null, "latest_message": "string\|null", "history_messages": ["string"]\|null, "update_status": {}\|null, "progress": float\|null, "current_task": "string\|null", "message": "string\|null"}` |  | **VALIDATION ERROR SEEN IN LOGS** |
| **get_track_status** | `GET /documents/track_status/{track_id}` | Path parameter: track_id | `TrackStatusResponse: {"track_id": "string", "documents": [{}], "total_count": int, "status_summary": {}}` |  | **VALIDATION ERROR SEEN IN LOGS** |
| **get_document_status_counts** | `GET /documents/status_counts` | No body (GET request) | `StatusCountsResponse: {"status_counts": {}}` |  | Simple GET request |
| **clear_cache** | `POST /documents/clear_cache` | `{"cache_type": "string\|null"}` or `{}` | `ClearCacheResponse: {"status": "string", "message": "string", "cache_type": "string\|null", "message": "string\|null"}` |  | **VALIDATION ERROR SEEN IN LOGS** |
| **get_health** | `GET /health` | No body (GET request) | `HealthResponse: {"status": "string", "version": "string\|null", "uptime": float\|null, "database_status": "string\|null", "cache_status": "string\|null", "message": "string\|null"}` |  | Simple GET request |

## Key Observations from Log Analysis

### Confirmed Validation Errors (from logs):

1. **query_text**: Server returned `{'response': '### AWS와 ... 말씀해 주세요.'}` but MCP expected `query` field
2. **get_track_status**: Server returned data but missing required `status` field  
3. **get_pipeline_status**: Server returned data but missing required `status` field
4. **clear_documents**: Server returned `{'status': 'success', 'message': '...'}` but MCP expected `cleared` and `count` fields
5. **clear_cache**: Server returned `{'status': 'success', 'message': '...'}` but MCP expected `cleared` field

### Areas of Uncertainty:

1. **get_graph_labels**: Code comment suggests server may return list but client expects dict structure
2. **Response field naming**: Multiple endpoints show pattern where server uses different field names than MCP client expects

### Successful Operations (from test logs):
- All 18 tested tools showed success in comprehensive test, suggesting the validation errors are recent or environment-specific

## Root Cause Analysis

The core issue appears to be **response schema validation mismatches** where:
- RAG server is returning valid HTTP responses with correct data
- MCP server's Pydantic models expect different field names than what RAG server provides
- This suggests either:
  - API version drift between RAG server and MCP client
  - Different response formats in different environments
  - Recent changes to RAG server response format not reflected in MCP models

## Next Steps Required

1. **Capture actual RAG server responses** for the failing endpoints
2. **Compare actual vs expected field names** systematically  
3. **Update Pydantic models** to match actual RAG server response format
4. **Test in controlled environment** to verify fixes