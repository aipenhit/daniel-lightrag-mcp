# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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