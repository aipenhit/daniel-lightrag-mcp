# LightRAG MCP API Alignment Plan

## Overview
This document tracks the systematic alignment of MCP tools with the actual LightRAG API based on comprehensive testing and API documentation analysis.

## Current Status: 2/22 tools fully working (9% success rate)

---

## API Mapping Analysis

### Document Management Tools (8 tools)

| Tool | Current Status | API Endpoint | Issues | Priority |
|------|---------------|--------------|---------|----------|
| `insert_text` | ❌ BROKEN | `POST /documents/text` | Request expects `{title, content}` not `{text}` | HIGH |
| `insert_texts` | ❌ BROKEN | `POST /documents/texts` | Expects array of objects, not `{texts: [...]}` | HIGH |
| `upload_document` | ❌ BROKEN | `POST /documents/upload` | Multipart form-data, not JSON | HIGH |
| `scan_documents` | ✅ WORKING | `POST /documents/scan` | Response model mismatch (minor) | LOW |
| `get_documents` | ❌ SERVER ERROR | `GET /documents` | LightRAG server validation error | BLOCKED |
| `get_documents_paginated` | ❌ SERVER ERROR | `POST /documents/paginated` | LightRAG server validation error | BLOCKED |
| `delete_document` | ❌ HTTP ERROR | `DELETE /documents/delete_document` | HTTP client DELETE with JSON issue | MEDIUM |
| `clear_documents` | ❌ BROKEN | `DELETE /documents` | Response model mismatch | MEDIUM |

### Query Tools (2 tools)

| Tool | Current Status | API Endpoint | Issues | Priority |
|------|---------------|--------------|---------|----------|
| `query_text` | ❌ BROKEN | `POST /query` | Response model expects `query` field, API returns `results` | HIGH |
| `query_text_stream` | ✅ WORKING | `POST /query/stream` | Working correctly | LOW |

### Knowledge Graph Tools (7 tools)

| Tool | Current Status | API Endpoint | Issues | Priority |
|------|---------------|--------------|---------|----------|
| `get_knowledge_graph` | ❌ BROKEN | `GET /graphs` | Missing required `label` parameter | HIGH |
| `get_graph_labels` | ❌ BROKEN | `GET /graph/label/list` | Returns array, model expects object | MEDIUM |
| `check_entity_exists` | ❌ BROKEN | `GET /graph/entity/exists` | Parameter name mismatch | MEDIUM |
| `update_entity` | ❌ BROKEN | `POST /graph/entity/edit` | Parameter structure mismatch | MEDIUM |
| `update_relation` | ❌ BROKEN | `POST /graph/relation/edit` | Parameter structure mismatch | MEDIUM |
| `delete_entity` | ❌ HTTP ERROR | `DELETE /documents/delete_entity` | HTTP client DELETE with JSON issue | MEDIUM |
| `delete_relation` | ❌ HTTP ERROR | `DELETE /documents/delete_relation` | HTTP client DELETE with JSON issue | MEDIUM |

### System Management Tools (5 tools)

| Tool | Current Status | API Endpoint | Issues | Priority |
|------|---------------|--------------|---------|----------|
| `get_pipeline_status` | ❌ BROKEN | `GET /documents/pipeline_status` | Response model mismatch | MEDIUM |
| `get_track_status` | ❌ BROKEN | `GET /documents/track_status/{track_id}` | Response model mismatch | MEDIUM |
| `get_document_status_counts` | ✅ WORKING | `GET /documents/status_counts` | Working correctly | LOW |
| `clear_cache` | ❌ BROKEN | `POST /documents/clear_cache` | Response model mismatch | MEDIUM |
| `get_health` | ✅ WORKING | `GET /health` | Working correctly | LOW |

---

## Issue Categories & Fixes Required

### 🔴 Category 1: HTTP Client Issues (5 tools) - PRIORITY: HIGH
**Problem**: DELETE requests with JSON body fail
**Affected Tools**: delete_document, delete_entity, delete_relation
**Root Cause**: httpx DELETE method parameter issue
**Fix**: Update HTTP client implementation

### 🔴 Category 2: Request Parameter Mismatches (6 tools) - PRIORITY: HIGH
**Problem**: MCP tool parameters don't match API expectations
**Affected Tools**: insert_text, insert_texts, upload_document, get_knowledge_graph, check_entity_exists, update_entity, update_relation
**Root Cause**: Incorrect parameter mapping
**Fix**: Update request models and parameter passing

### 🔴 Category 3: Response Model Mismatches (8 tools) - PRIORITY: MEDIUM
**Problem**: Pydantic models expect different fields than API returns
**Affected Tools**: query_text, get_graph_labels, get_pipeline_status, get_track_status, clear_cache, clear_documents
**Root Cause**: Models don't match actual API responses
**Fix**: Update response models based on actual API responses

### 🔴 Category 4: Server-Side Issues (2 tools) - PRIORITY: BLOCKED
**Problem**: LightRAG server validation errors
**Affected Tools**: get_documents, get_documents_paginated
**Root Cause**: Server-side validation issue with file_path field
**Fix**: Cannot fix from client side - requires server fix or workaround

---

## Implementation Strategy

### Phase 1: HTTP Client Fixes (Immediate - 1 hour)
1. Fix DELETE request implementation in `_make_request` method
2. Test all DELETE endpoints
3. Expected result: 5 additional working tools

### Phase 2: Request Parameter Alignment (High Priority - 2-3 hours)
1. Fix `insert_text` request format: `{text}` → `{title, content}`
2. Fix `insert_texts` request format: `{texts: [...]}` → `[...]`
3. Fix `upload_document` to use multipart form-data
4. Fix knowledge graph parameter mappings
5. Expected result: 6 additional working tools

### Phase 3: Response Model Alignment (Medium Priority - 2-3 hours)
1. Update all response models to match actual API responses
2. Test each model with real API responses
3. Expected result: 8 additional working tools

### Phase 4: Integration Testing & Validation (1 hour)
1. Comprehensive testing of all 22 tools
2. Documentation updates
3. Expected result: 19-20/22 tools working (90%+ success rate)

---

## Success Metrics

- **Current**: 2/22 tools working (9%)
- **After Phase 1**: 7/22 tools working (32%)
- **After Phase 2**: 13/22 tools working (59%)
- **After Phase 3**: 21/22 tools working (95%)
- **Final Target**: 20/22 tools working (91% - excluding server-side issues)

---

## Next Steps

1. ✅ Create this alignment plan
2. ⏳ Implement Phase 1: HTTP Client Fixes
3. ⏳ Implement Phase 2: Request Parameter Alignment
4. ⏳ Implement Phase 3: Response Model Alignment
5. ⏳ Final integration testing and validation

---

## Testing Framework

For each phase, we will:
1. Implement fixes
2. Run comprehensive test suite
3. Validate against API documentation
4. Update this tracking document
5. Measure success rate improvement

This systematic approach ensures we address root causes rather than individual symptoms.