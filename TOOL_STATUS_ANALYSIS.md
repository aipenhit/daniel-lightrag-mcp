# LightRAG MCP Tools Status Analysis

## ✅ WORKING TOOLS (15/22 - 68.2%)

### Document Management (4/6)
1. **insert_text** ✅ - Successfully inserts single text documents
2. **insert_texts** ✅ - Successfully inserts multiple text documents  
3. **scan_documents** ✅ - Successfully scans for new documents
4. **delete_document** ✅ - Successfully deletes documents by ID
5. **clear_documents** ✅ - Successfully clears all documents

### Query Operations (2/2)
6. **query_text** ✅ - Successfully queries text with all modes
7. **query_text_stream** ✅ - Successfully streams query results

### Knowledge Graph (2/6)
8. **get_knowledge_graph** ✅ - Successfully retrieves knowledge graph
9. **get_graph_labels** ✅ - Successfully gets graph labels
10. **check_entity_exists** ✅ - Successfully checks entity existence

### System Management (4/4)
11. **get_pipeline_status** ✅ - Successfully gets pipeline status
12. **get_track_status** ✅ - Successfully gets track status
13. **get_document_status_counts** ✅ - Successfully gets status counts
14. **clear_cache** ✅ - Successfully clears cache

### Health Check (1/1)
15. **get_health** ✅ - Successfully checks server health

---

## ❌ NON-WORKING TOOLS (7/22 - 31.8%)

### Document Management (2/6)
1. **upload_document** ❌ - File not found: /tmp/test.txt
2. **get_documents** 🚫 - Server validation error (blocked)
3. **get_documents_paginated** 🚫 - Server validation error (blocked)

### Knowledge Graph (4/6)
4. **update_entity** ❌ - HTTP 400: Entity 'test_entity_id' does not exist
5. **update_relation** ❌ - HTTP 400: Relation from 'unknown' to 'unknown' does not exist
6. **delete_entity** ❌ - HTTP 404: Entity 'test_entity_id' not found
7. **delete_relation** ❌ - HTTP 404: Relation from 'unknown' to 'unknown' does not exist

---

## 🔍 DETAILED ANALYSIS OF NON-WORKING TOOLS

### INVESTIGATION NEEDED

I need to investigate each failing tool properly rather than making assumptions. Let me analyze each one:
