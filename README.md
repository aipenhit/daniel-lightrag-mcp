# Daniel LightRAG MCP Server

A comprehensive MCP (Model Context Protocol) server that provides full integration with LightRAG API, offering 22 tools across 4 categories for complete document management, querying, knowledge graph operations, and system management.

## Features

- **Document Management**: 8 tools for inserting, uploading, scanning, retrieving, and deleting documents
- **Query Operations**: 2 tools for text queries with regular and streaming responses
- **Knowledge Graph**: 7 tools for accessing, checking, updating, and deleting entities and relations
- **System Management**: 5 tools for health checks, status monitoring, and cache management

## Quick Start

1. **Install the server**:
   ```bash
   pip install -e .
   ```

2. **Start LightRAG server** (ensure it's running on http://localhost:9621)

3. **Configure your MCP client** (e.g., Claude Desktop):
   ```json
   {
     "mcpServers": {
       "daniel-lightrag": {
         "command": "python",
         "args": ["-m", "daniel_lightrag_mcp"]
       }
     }
   }
   ```

4. **Test the connection**:
   Use the `get_health` tool to verify everything is working.

## Installation

```bash
# Basic installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Usage

### Command Line
Start the MCP server:

```bash
daniel-lightrag-mcp
```

### Environment Variables
Configure the server with environment variables:

```bash
export LIGHTRAG_BASE_URL="http://localhost:9621"
export LIGHTRAG_API_KEY="your-api-key"  # Optional
export LIGHTRAG_TIMEOUT="30"            # Optional
export LOG_LEVEL="INFO"                 # Optional

daniel-lightrag-mcp
```

## Configuration

The server expects LightRAG to be running on `http://localhost:9621` by default. Make sure your LightRAG server is started before running this MCP server.

For detailed configuration options, see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

## Available Tools (22 Total)

### Document Management Tools (8 tools)

#### `insert_text`
Insert text content into LightRAG.

**Parameters:**
- `text` (required): Text content to insert

**Example:**
```json
{
  "text": "This is important information about machine learning algorithms and their applications in modern AI systems."
}
```

#### `insert_texts`
Insert multiple text documents into LightRAG.

**Parameters:**
- `texts` (required): Array of text documents with optional title and metadata

**Example:**
```json
{
  "texts": [
    {
      "title": "AI Overview",
      "content": "Artificial Intelligence is transforming industries...",
      "metadata": {"category": "technology", "author": "researcher"}
    },
    {
      "content": "Machine learning algorithms require large datasets..."
    }
  ]
}
```

#### `upload_document`
Upload a document file to LightRAG.

**Parameters:**
- `file_path` (required): Path to the file to upload

**Example:**
```json
{
  "file_path": "/path/to/document.pdf"
}
```

#### `scan_documents`
Scan for new documents in LightRAG.

**Parameters:** None

**Example:**
```json
{}
```

#### `get_documents`
Retrieve all documents from LightRAG.

**Parameters:** None

**Example:**
```json
{}
```

#### `get_documents_paginated`
Retrieve documents with pagination.

**Parameters:**
- `page` (required): Page number (1-based)
- `page_size` (required): Number of documents per page (1-100)

**Example:**
```json
{
  "page": 1,
  "page_size": 20
}
```

#### `delete_document`
Delete a specific document by ID.

**Parameters:**
- `document_id` (required): ID of the document to delete

**Example:**
```json
{
  "document_id": "doc_12345"
}
```

#### `clear_documents`
Clear all documents from LightRAG.

**Parameters:** None

**Example:**
```json
{}
```

### Query Tools (2 tools)

#### `query_text`
Query LightRAG with text.

**Parameters:**
- `query` (required): Query text
- `mode` (optional): Query mode - "naive", "local", "global", or "hybrid" (default: "hybrid")
- `only_need_context` (optional): Whether to only return context without generation (default: false)

**Example:**
```json
{
  "query": "What are the main concepts in machine learning?",
  "mode": "hybrid",
  "only_need_context": false
}
```

#### `query_text_stream`
Stream query results from LightRAG.

**Parameters:**
- `query` (required): Query text
- `mode` (optional): Query mode - "naive", "local", "global", or "hybrid" (default: "hybrid")
- `only_need_context` (optional): Whether to only return context without generation (default: false)

**Example:**
```json
{
  "query": "Explain the evolution of artificial intelligence",
  "mode": "global"
}
```

### Knowledge Graph Tools (7 tools)

#### `get_knowledge_graph`
Retrieve the knowledge graph from LightRAG.

**Parameters:** None

**Example:**
```json
{}
```

#### `get_graph_labels`
Get labels from the knowledge graph.

**Parameters:** None

**Example:**
```json
{}
```

#### `check_entity_exists`
Check if an entity exists in the knowledge graph.

**Parameters:**
- `entity_name` (required): Name of the entity to check

**Example:**
```json
{
  "entity_name": "Machine Learning"
}
```

#### `update_entity`
Update an entity in the knowledge graph.

**Parameters:**
- `entity_id` (required): ID of the entity to update
- `properties` (required): Properties to update

**Example:**
```json
{
  "entity_id": "entity_123",
  "properties": {
    "description": "Updated description for machine learning",
    "category": "AI Technology"
  }
}
```

#### `update_relation`
Update a relation in the knowledge graph.

**Parameters:**
- `relation_id` (required): ID of the relation to update
- `properties` (required): Properties to update

**Example:**
```json
{
  "relation_id": "rel_456",
  "properties": {
    "strength": 0.9,
    "type": "implements"
  }
}
```

#### `delete_entity`
Delete an entity from the knowledge graph.

**Parameters:**
- `entity_id` (required): ID of the entity to delete

**Example:**
```json
{
  "entity_id": "entity_789"
}
```

#### `delete_relation`
Delete a relation from the knowledge graph.

**Parameters:**
- `relation_id` (required): ID of the relation to delete

**Example:**
```json
{
  "relation_id": "rel_101"
}
```

### System Management Tools (5 tools)

#### `get_pipeline_status`
Get the pipeline status from LightRAG.

**Parameters:** None

**Example:**
```json
{}
```

#### `get_track_status`
Get track status by ID.

**Parameters:**
- `track_id` (required): ID of the track to get status for

**Example:**
```json
{
  "track_id": "track_abc123"
}
```

#### `get_document_status_counts`
Get document status counts.

**Parameters:** None

**Example:**
```json
{}
```

#### `clear_cache`
Clear LightRAG cache.

**Parameters:** None

**Example:**
```json
{}
```

#### `get_health`
Check LightRAG server health.

**Parameters:** None

**Example:**
```json
{}
```

## Example Workflows

### Complete Document Management Workflow

1. **Check server health**:
   ```json
   {"tool": "get_health", "arguments": {}}
   ```

2. **Insert documents**:
   ```json
   {
     "tool": "insert_texts",
     "arguments": {
       "texts": [
         {
           "title": "AI Research Paper",
           "content": "Recent advances in transformer architectures have shown remarkable improvements in natural language understanding tasks...",
           "metadata": {"category": "research", "year": 2024}
         }
       ]
     }
   }
   ```

3. **Query the knowledge base**:
   ```json
   {
     "tool": "query_text",
     "arguments": {
       "query": "What are the recent advances in transformer architectures?",
       "mode": "hybrid"
     }
   }
   ```

4. **Explore the knowledge graph**:
   ```json
   {"tool": "get_knowledge_graph", "arguments": {}}
   ```

5. **Check entity existence**:
   ```json
   {
     "tool": "check_entity_exists",
     "arguments": {"entity_name": "transformer architectures"}
   }
   ```

### Knowledge Graph Management Workflow

1. **Get current graph structure**:
   ```json
   {"tool": "get_knowledge_graph", "arguments": {}}
   ```

2. **Get available labels**:
   ```json
   {"tool": "get_graph_labels", "arguments": {}}
   ```

3. **Update entity properties**:
   ```json
   {
     "tool": "update_entity",
     "arguments": {
       "entity_id": "transformer_arch_001",
       "properties": {
         "description": "Advanced neural network architecture for sequence processing",
         "applications": ["NLP", "computer vision", "speech recognition"],
         "year_introduced": 2017
       }
     }
   }
   ```

4. **Update relation properties**:
   ```json
   {
     "tool": "update_relation",
     "arguments": {
       "relation_id": "rel_improves_002",
       "properties": {
         "improvement_factor": 2.5,
         "confidence": 0.92,
         "evidence": "Multiple benchmark studies"
       }
     }
   }
   ```

### System Monitoring Workflow

1. **Check overall health**:
   ```json
   {"tool": "get_health", "arguments": {}}
   ```

2. **Monitor pipeline status**:
   ```json
   {"tool": "get_pipeline_status", "arguments": {}}
   ```

3. **Check document processing status**:
   ```json
   {"tool": "get_document_status_counts", "arguments": {}}
   ```

4. **Track specific operations**:
   ```json
   {
     "tool": "get_track_status",
     "arguments": {"track_id": "upload_batch_001"}
   }
   ```

5. **Clear cache when needed**:
   ```json
   {"tool": "clear_cache", "arguments": {}}
   ```

## Error Handling

The server provides comprehensive error handling with detailed error messages:

- **Connection Errors**: When LightRAG server is unreachable
- **Authentication Errors**: When API key is invalid or missing
- **Validation Errors**: When input parameters are invalid
- **API Errors**: When LightRAG API returns errors
- **Timeout Errors**: When requests exceed timeout limits
- **Server Errors**: When LightRAG server returns 5xx status codes

All errors include:
- Error type and message
- HTTP status code (when applicable)
- Timestamp
- Tool name that caused the error
- Additional context data when available

### Error Response Format

```json
{
  "tool": "insert_text",
  "error_type": "LightRAGConnectionError",
  "message": "Failed to connect to LightRAG server at http://localhost:9621",
  "timestamp": 1703123456.789,
  "status_code": null,
  "response_data": {}
}
```

### Common Error Scenarios

#### Connection Errors
```json
{
  "error_type": "LightRAGConnectionError",
  "message": "Connection refused to http://localhost:9621",
  "status_code": null
}
```

#### Validation Errors
```json
{
  "error_type": "LightRAGValidationError", 
  "message": "Missing required arguments for query_text: ['query']",
  "validation_errors": [
    {
      "loc": ["query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### API Errors
```json
{
  "error_type": "LightRAGAPIError",
  "message": "Document not found",
  "status_code": 404,
  "response_data": {
    "detail": "Document with ID 'doc_123' does not exist"
  }
}
```

## Troubleshooting

### Quick Diagnostics

1. **Check LightRAG Server Status**:
   ```bash
   curl http://localhost:9621/health
   ```

2. **Test MCP Server**:
   ```bash
   python -m daniel_lightrag_mcp &
   sleep 2
   pkill -f daniel_lightrag_mcp
   ```

3. **Verify Installation**:
   ```bash
   python -c "import daniel_lightrag_mcp; print('OK')"
   ```

### Common Issues

#### Server Won't Start
- **Check Python version**: Requires Python 3.8+
- **Verify dependencies**: Run `pip install -e .`
- **Check port availability**: Ensure no conflicts on stdio

#### Connection Refused
- **LightRAG not running**: Start LightRAG server first
- **Wrong URL**: Verify `LIGHTRAG_BASE_URL` environment variable
- **Firewall blocking**: Check firewall settings for port 9621

#### Authentication Failed
- **Missing API key**: Set `LIGHTRAG_API_KEY` environment variable
- **Invalid key**: Verify API key with LightRAG server
- **Key format**: Ensure key format matches LightRAG expectations

#### Timeout Errors
- **Increase timeout**: Set `LIGHTRAG_TIMEOUT=60` environment variable
- **Check server load**: Verify LightRAG server performance
- **Network latency**: Test direct API calls with curl

#### Tool Not Found
- **Restart MCP client**: Reload server configuration
- **Check tool name**: Verify exact tool name spelling
- **Server registration**: Ensure all 22 tools are listed

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python -m daniel_lightrag_mcp
```

### Getting Help

1. Check server logs for detailed error messages
2. Test individual tools with minimal examples
3. Verify LightRAG server is responding correctly
4. Review the [Configuration Guide](CONFIGURATION_GUIDE.md) for setup details

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src/daniel_lightrag_mcp --cov-report=html
```

Format code:

```bash
black src/ tests/
isort src/ tests/
```

## License

MIT License
