## MCP Server Plan for LightRAG

Based on the LightRAG documentation and API endpoints, create an MCP server that provides tools to interact with your local LightRAG server running on localhost:9621.

### **Core MCP Tools to Implement:**

#### **Document Management Tools:**
1. **`insert_text`** - Insert single text document (`POST /documents/text`)
2. **`insert_texts`** - Insert multiple text documents (`POST /documents/texts`)
3. **`upload_document`** - Upload file to input directory (`POST /documents/upload`)
4. **`scan_documents`** - Scan for new documents (`POST /documents/scan`)
5. **`get_documents`** - List all documents (`GET /documents`)
6. **`get_documents_paginated`** - Get documents with pagination (`POST /documents/paginated`)
7. **`delete_document`** - Delete document by ID (`DELETE /documents/delete_document`)
8. **`clear_documents`** - Clear all documents (`DELETE /documents`)

#### **Query Tools:**
9. **`query_text`** - Query the knowledge base (`POST /query`)
10. **`query_text_stream`** - Query with streaming response (`POST /query/stream`)

#### **Knowledge Graph Tools:**
11. **`get_knowledge_graph`** - Get the knowledge graph (`GET /graphs`)
12. **`get_graph_labels`** - Get available graph labels (`GET /graph/label/list`)
13. **`check_entity_exists`** - Check if entity exists (`GET /graph/entity/exists`)
14. **`update_entity`** - Update entity information (`POST /graph/entity/edit`)
15. **`update_relation`** - Update relation information (`POST /graph/relation/edit`)
16. **`delete_entity`** - Delete entity (`DELETE /documents/delete_entity`)
17. **`delete_relation`** - Delete relation (`DELETE /documents/delete_relation`)

#### **System Management Tools:**
18. **`get_pipeline_status`** - Get processing pipeline status (`GET /documents/pipeline_status`)
19. **`get_track_status`** - Get track status by ID (`GET /documents/track_status/{track_id}`)
20. **`get_document_status_counts`** - Get document status counts (`GET /documents/status_counts`)
21. **`clear_cache`** - Clear system cache (`POST /documents/clear_cache`)
22. **`get_health`** - Check server health (`GET /health`)

### **MCP Server Structure:**
- **Language**: Python (following MCP Python SDK patterns)
- **Base URL**: `http://localhost:9621`
- **Error Handling**: Comprehensive HTTP error handling with meaningful messages
- **Request/Response**: JSON-based communication matching LightRAG API schemas
- **Authentication**: Support for auth if needed (based on `/login` endpoint)

### **Key Features:**
- **Type Safety**: Proper input validation using Pydantic models
- **Async Support**: All tools will be async for better performance
- **Error Recovery**: Graceful handling of network errors and API failures
- **Logging**: Comprehensive logging for debugging
- **Documentation**: Clear docstrings for each tool explaining parameters and usage

### **File Structure:**
```
/Users/danielsimpkins/Documents/Cline/VSCode_Projects/daniel-lightrag-mcp/
├── src/
│   └── lightrag_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       ├── client.py          # LightRAG API client
│       └── models.py          # Pydantic models for requests/responses
├── pyproject.toml             # Project configuration
├── README.md                  # Usage documentation
└── .env.example              # Environment variables template
```

This MCP server will allow you to interact with your LightRAG instance through any MCP-compatible client, providing full access to document management, querying, and knowledge graph operations.

Here are the Rules for implementation, that you MUST adhere to at ALL times:
You must use this directory ONLY: /Users/danielsimpkins/Documents/Cline/VSCode_Projects/daniel-lightrag-mcp
The implementation plan is included in here at /Users/danielsimpkins/Documents/Cline/VSCode_Projects/daniel-lightrag-mcp/implementation_plan.md
I require you to update a log of exactly what you have done, including files created, code modified, items tested, where you might have gathered data from, and so on. You need to continuously write to this plan each time you complete minor and mojor steps. The file you are to populate is here: /Users/danielsimpkins/Documents/Cline/VSCode_Projects/daniel-lightrag-mcp/implementation_log.md
If you require any information, you must explicitly ask me for it, browse the internet for it, but you may not go outside of the folder locations below without my express approval.
Allowed locations to READ ONLY: /Users/danielsimpkins/Documents/Cline/VSCode_Projects/LightRAG
Allowed locations to read and write: /Users/danielsimpkins/Documents/Cline/VSCode_Projects/daniel-lightrag-mcp
If you need to deviate from any of these rules, you MUST ask for approval first.