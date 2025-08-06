# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-06

### 🎉 Major Achievement: 100% Functional Implementation

**All 22 tools are now working perfectly** after comprehensive testing and optimization.

### Fixed - Phase 1: HTTP Client Fixes
- **HTTP DELETE with JSON support**: Fixed `AsyncClient.delete()` limitation by using `client.request("DELETE", url, json=data)`
- **Tools Fixed**: `delete_document`, `delete_entity`, `delete_relation`

### Fixed - Phase 2: Request Parameter Validation
- **InsertTextsRequest**: Changed from `List[TextDocument]` to `List[str]` with `file_sources` parameter
- **DeleteDocRequest**: Changed from `document_id: str` to `doc_ids: List[str]`
- **EntityUpdateRequest**: Added required `entity_name` and `updated_data` fields
- **RelationUpdateRequest**: Added required `source_id`, `target_id`, and `updated_data` fields
- **DeleteEntityRequest**: Added required `entity_name` field
- **DeleteRelationRequest**: Added required `source_entity` and `target_entity` fields

### Fixed - Phase 3: Response Model Alignment
- **GraphResponse**: Changed to match server response `{nodes: [], edges: [], is_truncated: bool}`
- **EntityUpdateResponse**: Changed to match server response `{status: str, message: str, data: dict}`
- **RelationUpdateResponse**: Changed to match server response `{status: str, message: str, data: dict}`
- **UploadResponse**: Fixed to match server response structure
- **PaginationInfo**: Added required fields `total_count`, `has_next`, `has_prev`

### Fixed - Critical File Source Implementation
- **Root Cause**: `insert_text` and `insert_texts` were creating documents with `file_path = null`
- **Solution**: Added proper `file_source` parameters to prevent database corruption
- **Impact**: Fixed `get_documents` and `get_documents_paginated` tools

### Fixed - Knowledge Graph Access
- **get_knowledge_graph**: Changed default label from `"all"` to `"*"` (wildcard)
- **Result**: Now successfully retrieves 180+ entities and 133+ relations

### Added
- Comprehensive [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- Detailed [MCP_CONFIGURATION_GUIDE.md](MCP_CONFIGURATION_GUIDE.md)
- Complete error handling with custom exception hierarchy
- Performance optimizations and monitoring capabilities

### Testing Results
- **Total Tools**: 22
- **Working Tools**: 22 (100%)
- **Success Rate**: 100%

## [0.1.0] - 2024-12-XX

### Added
- Initial release of Daniel LightRAG MCP Server
- 22 comprehensive MCP tools across 4 categories:
  - Document Management Tools (8 tools)
  - Query Tools (2 tools)
  - Knowledge Graph Tools (7 tools)
  - System Management Tools (5 tools)
- Complete test suite with 150+ tests
- Comprehensive documentation and configuration guide
- Error handling with detailed error messages
- Support for streaming queries
- Async operations throughout
- Environment variable configuration
- CLI interface
- Pydantic model validation
- HTTP client with proper error mapping
- Logging with structured output

### Features
- **Document Management**: Insert, upload, scan, retrieve, and delete documents
- **Query Operations**: Text queries with multiple modes and streaming support
- **Knowledge Graph**: Full CRUD operations on entities and relations
- **System Management**: Health checks, status monitoring, and cache management
- **Error Handling**: Comprehensive error types with detailed context
- **Configuration**: Flexible configuration via environment variables
- **Testing**: Extensive test coverage with mocks and integration tests
- **Documentation**: Detailed README and configuration guide with examples

### Technical Details
- Python 3.8+ support
- MCP (Model Context Protocol) integration
- httpx for async HTTP operations
- Pydantic for data validation
- pytest for testing framework
- Black and isort for code formatting
- mypy for type checking