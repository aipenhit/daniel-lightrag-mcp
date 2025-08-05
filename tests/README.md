# Test Suite for Daniel LightRAG MCP Server

This directory contains a comprehensive test suite for the Daniel LightRAG MCP Server, covering all 22 MCP tools with unit tests, integration tests, and validation tests.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── test_server.py              # MCP server unit tests
├── test_client.py              # LightRAG client unit tests
├── test_models.py              # Pydantic model validation tests
├── test_integration.py         # Integration tests with mock server
├── test_runner.py              # Test runner script
└── README.md                   # This file
```

## Test Categories

### 1. Unit Tests (`test_server.py`)
Tests for MCP server functionality:
- **Tool Listing**: Verifies all 22 tools are properly registered
- **Argument Validation**: Tests input validation for all tools
- **Response Creation**: Tests success and error response formatting
- **Document Management Tools**: Tests for 8 document management tools
- **Query Tools**: Tests for 2 query tools (including streaming)
- **Knowledge Graph Tools**: Tests for 7 knowledge graph tools
- **System Management Tools**: Tests for 5 system management tools
- **Error Handling**: Tests for various error scenarios

### 2. Client Tests (`test_client.py`)
Tests for LightRAG client functionality:
- **Client Initialization**: Tests client setup and configuration
- **HTTP Error Mapping**: Tests error mapping to custom exceptions
- **Document Management Methods**: Tests all document management API calls
- **Query Methods**: Tests query and streaming query functionality
- **Knowledge Graph Methods**: Tests knowledge graph operations
- **System Management Methods**: Tests system management operations
- **Error Handling**: Tests client-side error handling
- **Context Manager**: Tests async context manager functionality

### 3. Model Tests (`test_models.py`)
Tests for Pydantic model validation:
- **Enums**: Tests for status and mode enumerations
- **Common Models**: Tests for shared models like TextDocument
- **Request Models**: Tests for all API request models
- **Response Models**: Tests for all API response models
- **Model Serialization**: Tests for JSON serialization/deserialization
- **Validation Edge Cases**: Tests for validation edge cases and error handling

### 4. Integration Tests (`test_integration.py`)
End-to-end integration tests:
- **Full Workflow Integration**: Tests complete document management workflows
- **Query Workflow**: Tests document insertion and querying workflows
- **System Management Workflow**: Tests system health and cache management
- **Error Scenarios**: Tests error handling in integration context
- **Streaming Integration**: Tests streaming functionality end-to-end
- **Concurrent Operations**: Tests concurrent tool operations
- **Tool Listing Integration**: Tests tool listing completeness

## Test Coverage

The test suite provides comprehensive coverage for:

### All 22 MCP Tools:
1. **Document Management (8 tools)**:
   - `insert_text` - Insert single text document
   - `insert_texts` - Insert multiple text documents
   - `upload_document` - Upload document file
   - `scan_documents` - Scan for new documents
   - `get_documents` - Retrieve all documents
   - `get_documents_paginated` - Retrieve documents with pagination
   - `delete_document` - Delete specific document
   - `clear_documents` - Clear all documents

2. **Query Tools (2 tools)**:
   - `query_text` - Query with text
   - `query_text_stream` - Stream query results

3. **Knowledge Graph Tools (7 tools)**:
   - `get_knowledge_graph` - Retrieve knowledge graph
   - `get_graph_labels` - Get graph labels
   - `check_entity_exists` - Check entity existence
   - `update_entity` - Update entity
   - `update_relation` - Update relation
   - `delete_entity` - Delete entity
   - `delete_relation` - Delete relation

4. **System Management Tools (5 tools)**:
   - `get_pipeline_status` - Get pipeline status
   - `get_track_status` - Get track status
   - `get_document_status_counts` - Get document status counts
   - `clear_cache` - Clear cache
   - `get_health` - Health check

### Test Scenarios:
- ✅ **Input Validation**: All tools tested with valid and invalid inputs
- ✅ **Error Handling**: All error types tested (connection, validation, API, timeout)
- ✅ **Streaming Functionality**: Query streaming tested with mock responses
- ✅ **Mock HTTP Responses**: All API endpoints tested with mock responses
- ✅ **Pydantic Model Validation**: All request/response models tested
- ✅ **Integration Workflows**: Complete workflows tested end-to-end
- ✅ **Concurrent Operations**: Multi-tool concurrent execution tested
- ✅ **Edge Cases**: Boundary conditions and edge cases covered

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -e ".[dev]"
```

### Run All Tests
```bash
# Using pytest directly
python3 -m pytest tests/ -v

# Using the test runner
python3 tests/test_runner.py all --verbose
```

### Run Specific Test Categories
```bash
# Unit tests only
python3 tests/test_runner.py unit

# Integration tests only
python3 tests/test_runner.py integration

# Model tests only
python3 tests/test_runner.py models

# Server tests only
python3 tests/test_runner.py server

# Client tests only
python3 tests/test_runner.py client
```

### Run with Coverage
```bash
python3 tests/test_runner.py all --coverage
```

### Run Specific Tests
```bash
# Test specific tool
python3 -m pytest tests/test_server.py::TestDocumentManagementTools::test_insert_text_success -v

# Test specific model
python3 -m pytest tests/test_models.py::TestRequestModels::test_query_request_valid -v

# Test specific integration workflow
python3 -m pytest tests/test_integration.py::TestFullWorkflowIntegration::test_document_management_workflow -v
```

## Test Fixtures and Mocks

### Key Fixtures (`conftest.py`):
- `lightrag_client`: Mock LightRAG client for testing
- `mock_response`: Factory for creating mock HTTP responses
- `mock_streaming_response`: Factory for creating mock streaming responses
- Sample data fixtures for all response types

### Mock Strategies:
- **HTTP Client Mocking**: Uses `unittest.mock.AsyncMock` to mock httpx client
- **Server Response Mocking**: Mock LightRAG server with realistic responses
- **Streaming Mocking**: Mock async generators for streaming responses
- **Error Injection**: Mock various error conditions for error handling tests

## Test Quality Metrics

### Coverage Goals:
- **Line Coverage**: >95% for all source files
- **Branch Coverage**: >90% for all conditional logic
- **Function Coverage**: 100% for all public methods

### Test Quality:
- **Isolation**: Each test is independent and can run in any order
- **Deterministic**: Tests produce consistent results across runs
- **Fast**: Unit tests complete in <1 second, integration tests in <5 seconds
- **Comprehensive**: All code paths and error conditions tested
- **Maintainable**: Clear test structure and good documentation

## Continuous Integration

The test suite is designed to run in CI/CD environments:
- **No External Dependencies**: All tests use mocks, no real LightRAG server needed
- **Parallel Execution**: Tests can run in parallel for faster CI builds
- **Clear Exit Codes**: Proper exit codes for CI/CD integration
- **Detailed Reporting**: Comprehensive test reports and coverage data

## Adding New Tests

When adding new functionality:

1. **Add Unit Tests**: Test the new functionality in isolation
2. **Add Integration Tests**: Test the new functionality in realistic scenarios
3. **Update Model Tests**: If new models are added, test their validation
4. **Update Fixtures**: Add new sample data fixtures as needed
5. **Update Documentation**: Update this README with new test information

### Test Naming Convention:
- `test_<functionality>_success` - Happy path tests
- `test_<functionality>_error` - Error condition tests
- `test_<functionality>_validation` - Input validation tests
- `test_<functionality>_edge_cases` - Edge case tests

## Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure the package is installed in development mode: `pip install -e .`
2. **Async Test Issues**: Make sure `pytest-asyncio` is installed and configured
3. **Mock Issues**: Verify mock setup in `conftest.py` and test-specific mocks
4. **Pydantic Validation**: Check model definitions match test expectations

### Debug Mode:
```bash
# Run with maximum verbosity and no capture
python3 -m pytest tests/ -vvv -s --tb=long

# Run specific failing test with debug info
python3 -m pytest tests/test_server.py::TestDocumentManagementTools::test_insert_text_success -vvv -s --tb=long
```

## Performance Benchmarks

### Test Execution Times (approximate):
- **Model Tests**: ~0.1 seconds (44 tests)
- **Server Tests**: ~0.5 seconds (50+ tests)
- **Client Tests**: ~0.3 seconds (40+ tests)
- **Integration Tests**: ~1.0 seconds (20+ tests)
- **Total Suite**: ~2.0 seconds (150+ tests)

The test suite is optimized for speed while maintaining comprehensive coverage.