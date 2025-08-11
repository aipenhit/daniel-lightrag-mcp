"""
MCP server for LightRAG integration.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl

from .client import (
    LightRAGClient, 
    LightRAGError, 
    LightRAGConnectionError, 
    LightRAGAuthError, 
    LightRAGValidationError, 
    LightRAGAPIError,
    LightRAGTimeoutError,
    LightRAGServerError
)

# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Set specific log levels for different components
logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce httpx noise
logging.getLogger("mcp").setLevel(logging.INFO)

# Initialize the MCP server
server = Server("daniel-lightrag-mcp")

# Global client instance
lightrag_client: Optional[LightRAGClient] = None


def _validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> None:
    """Validate tool arguments against expected schemas."""
    # Define required arguments for each tool
    required_args = {
        "insert_text": ["text"],
        "insert_texts": ["texts"],
        "upload_document": ["file_path"],
        "get_documents_paginated": ["page", "page_size"],
        "delete_document": ["document_id"],
        "query_text": ["query"],
        "query_text_stream": ["query"],
        "check_entity_exists": ["entity_name"],
        "update_entity": ["entity_id", "properties"],
        "update_relation": ["relation_id", "properties"],
        "delete_entity": ["entity_id"],
        "delete_relation": ["relation_id"],
        "get_track_status": ["track_id"],
    }
    
    # Check if tool requires specific arguments
    if tool_name in required_args:
        missing_args = []
        for required_arg in required_args[tool_name]:
            if required_arg not in arguments:
                missing_args.append(required_arg)
        
        if missing_args:
            error_msg = f"Missing required arguments for {tool_name}: {missing_args}"
            logger.warning(f"Validation error: {error_msg}")
            raise LightRAGValidationError(error_msg)
    
    # Additional validation for specific tools
    if tool_name == "get_documents_paginated":
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)
        
        if not isinstance(page, int) or page < 1:
            raise LightRAGValidationError("Page must be a positive integer")
        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            raise LightRAGValidationError("Page size must be an integer between 1 and 100")
    
    elif tool_name == "query_text" or tool_name == "query_text_stream":
        mode = arguments.get("mode", "hybrid")
        valid_modes = ["naive", "local", "global", "hybrid"]
        if mode not in valid_modes:
            raise LightRAGValidationError(f"Invalid query mode '{mode}'. Must be one of: {valid_modes}")
    
    logger.debug(f"Tool arguments validation passed for {tool_name}")


def _serialize_result(result: Any) -> str:
    """Serialize result to JSON, handling Pydantic models."""
    if hasattr(result, 'dict'):
        # Pydantic model
        return json.dumps(result.model_dump(), indent=2)
    elif hasattr(result, '__dict__'):
        # Regular object with __dict__
        return json.dumps(result.__dict__, indent=2)
    else:
        # Fallback to direct serialization
        return json.dumps(result, indent=2)


def _create_success_response(result: Any, tool_name: str) -> dict:
    """Create standardized MCP success response."""
    logger.info("=" * 60)
    logger.info("CREATING SUCCESS RESPONSE")
    logger.info("=" * 60)
    logger.info(f"SUCCESS RESPONSE INPUT:")
    logger.info(f"  - tool_name: '{tool_name}'")
    logger.info(f"  - result type: {type(result)}")
    logger.info(f"  - result content: {repr(result)}")
    
    # Handle Pydantic models properly
    logger.info("RESPONSE SERIALIZATION:")
    if hasattr(result, 'model_dump'):
        logger.info("  - Using result.model_dump() (Pydantic v2)")
        try:
            serialized_data = result.model_dump()
            logger.info(f"  - model_dump() result: {serialized_data}")
            response_text = json.dumps(serialized_data, indent=2)
            logger.info(f"  - JSON serialization successful")
        except Exception as e:
            logger.error(f"  - model_dump() failed: {e}")
            response_text = str(result)
    elif hasattr(result, 'dict'):
        logger.info("  - Using result.dict() (Pydantic v1)")
        try:
            serialized_data = result.dict()
            logger.info(f"  - dict() result: {serialized_data}")
            response_text = json.dumps(serialized_data, indent=2)
            logger.info(f"  - JSON serialization successful")
        except Exception as e:
            logger.error(f"  - dict() failed: {e}")
            response_text = str(result)
    elif result:
        logger.info("  - Direct JSON serialization")
        try:
            response_text = json.dumps(result, indent=2)
            logger.info(f"  - Direct JSON serialization successful")
        except Exception as e:
            logger.error(f"  - Direct JSON serialization failed: {e}")
            response_text = str(result)
    else:
        logger.info("  - Result is None/empty, using 'Success'")
        response_text = "Success"
    
    logger.info(f"FINAL RESPONSE TEXT:")
    logger.info(f"  - Length: {len(response_text)} characters")
    logger.info(f"  - Content preview: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
    
    # Create response dictionary
    response_dict = {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }
    
    logger.info(f"SUCCESS RESPONSE CREATED:")
    logger.info(f"  - Response type: {type(response_dict)}")
    logger.info(f"  - Response keys: {list(response_dict.keys())}")
    logger.info(f"  - Content length: {len(response_dict['content'])}")
    logger.info(f"  - Content[0] type: {response_dict['content'][0]['type']}")
    logger.info(f"  - Content[0] text length: {len(response_dict['content'][0]['text'])}")
    logger.info("=" * 60)
    
    return response_dict

# def _create_success_response(result: Any, tool_name: str) -> CallToolResult:
#     """Create standardized MCP success response."""
#     logger.info(f"Successfully executed {tool_name}")
#     return CallToolResult(
#         content=[TextContent(type="text", text=_serialize_result(result))]
#     )
# def _create_success_response(result: Any, tool_name: str) -> CallToolResult:
#     """Create standardized MCP success response."""
#     logger.info(f"Successfully executed {tool_name}")
    
#     # Simple text response format
#     # response_text = json.dumps(result, indent=2) if result else "Success"

#     # Handle Pydantic models properly
#     if hasattr(result, 'model_dump'):
#         # Pydantic v2
#         response_text = json.dumps(result.model_dump(), indent=2)
#     elif hasattr(result, 'dict'):
#         # Pydantic v1
#         response_text = json.dumps(result.dict(), indent=2)
#     elif result:
#         response_text = json.dumps(result, indent=2)
#     else:
#         response_text = "Success"

    
#     return CallToolResult(
#         content=[TextContent(type="text", text=response_text)]
#     )
# def _create_success_response(result: Any, tool_name: str) -> CallToolResult:
#     """Create standardized MCP success response."""
#     logger.info(f"Successfully executed {tool_name}")
    
#     # Handle Pydantic models properly
#     if hasattr(result, 'model_dump'):
#         response_text = json.dumps(result.model_dump(), indent=2)
#     elif hasattr(result, 'dict'):
#         response_text = json.dumps(result.dict(), indent=2)
#     elif result:
#         response_text = json.dumps(result, indent=2)
#     else:
#         response_text = "Success"
    
#     # Create TextContent object explicitly
#     text_content = TextContent(type="text", text=response_text)
    
#     # Return CallToolResult with explicit parameters
#     return CallToolResult(content=[text_content])


def _create_error_response(error: Exception, tool_name: str) -> dict:
    """Create standardized MCP error response."""
    logger.error("=" * 60)
    logger.error("CREATING ERROR RESPONSE")
    logger.error("=" * 60)
    logger.error(f"ERROR RESPONSE INPUT:")
    logger.error(f"  - tool_name: '{tool_name}'")
    logger.error(f"  - error type: {type(error)}")
    logger.error(f"  - error message: {str(error)}")
    logger.error(f"  - error args: {error.args}")
    
    # Get full traceback
    import traceback
    logger.error(f"ERROR TRACEBACK:")
    logger.error(f"  - Full traceback: {traceback.format_exc()}")
    
    error_details = {
        "tool": tool_name,
        "error_type": type(error).__name__,
        "message": str(error),
        "timestamp": asyncio.get_event_loop().time()
    }
    
    logger.error(f"BASE ERROR DETAILS:")
    logger.error(f"  - error_details: {error_details}")
    
    # Add additional details for LightRAG errors
    if isinstance(error, LightRAGError):
        logger.error("LIGHTRAG ERROR DETECTED:")
        logger.error(f"  - LightRAG error type: {type(error)}")
        try:
            error_dict = error.to_dict()
            logger.error(f"  - error.to_dict(): {error_dict}")
            error_details.update(error_dict)
        except Exception as e:
            logger.error(f"  - error.to_dict() failed: {e}")
        
        # Log different error types at appropriate levels with structured context
        error_context = {
            "tool": tool_name,
            "error_type": type(error).__name__,
            "status_code": getattr(error, 'status_code', None),
            "response_data": getattr(error, 'response_data', {})
        }
        
        logger.error(f"ERROR CONTEXT: {error_context}")
        
        if isinstance(error, (LightRAGConnectionError, LightRAGTimeoutError)):
            logger.warning(f"Connection/timeout error in {tool_name}: {error}", extra=error_context)
        elif isinstance(error, LightRAGAuthError):
            logger.error(f"Authentication error in {tool_name}: {error}", extra=error_context)
        elif isinstance(error, LightRAGValidationError):
            logger.warning(f"Validation error in {tool_name}: {error}", extra=error_context)
        elif isinstance(error, LightRAGServerError):
            logger.error(f"Server error in {tool_name}: {error}", extra=error_context)
        else:
            logger.error(f"API error in {tool_name}: {error}", extra=error_context)
    else:
        logger.error("NON-LIGHTRAG ERROR:")
        # Handle Pydantic validation errors specifically
        if hasattr(error, 'errors') and callable(getattr(error, 'errors')):
            logger.error("  - Pydantic validation error detected")
            try:
                validation_errors = error.errors()
                logger.error(f"  - validation_errors: {validation_errors}")
                error_details["validation_errors"] = validation_errors
                logger.warning(f"Input validation error in {tool_name}: {validation_errors}")
            except Exception as e:
                logger.error(f"  - error.errors() failed: {e}")
                logger.error(f"Unexpected error in {tool_name}: {error}")
        else:
            logger.error(f"  - Generic error: {error}")
            logger.error(f"Unexpected error in {tool_name}: {error}")
    
    logger.error(f"FINAL ERROR DETAILS:")
    logger.error(f"  - error_details: {error_details}")
    
    # Create error response dictionary
    error_response = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(error_details, indent=2)
            }
        ],
        "isError": True
    }
    
    logger.error(f"ERROR RESPONSE CREATED:")
    logger.error(f"  - Response type: {type(error_response)}")
    logger.error(f"  - Response keys: {list(error_response.keys())}")
    logger.error(f"  - isError: {error_response['isError']}")
    logger.error(f"  - Content length: {len(error_response['content'])}")
    logger.error("=" * 60)
    
    return error_response


@server.list_tools()
async def handle_list_tools() -> List[Tool]:#ListToolsResult:
    """List available tools."""
    logger.info("Listing available MCP tools")
    
    # Create tools list with explicit validation
    tools = []
    
    # Document Management Tools (8 tools)
    tools.extend([
        Tool(
            name="insert_text",
            description="Insert text content into LightRAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to insert"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="insert_texts",
            description="Insert multiple text documents into LightRAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "texts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"},
                                "metadata": {"type": "object"}
                            },
                            "required": ["content"]
                        },
                        "description": "Array of text documents to insert"
                    }
                },
                "required": ["texts"]
            }
        ),
        Tool(
            name="upload_document",
            description="Upload a document file to LightRAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to upload"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="scan_documents",
            description="Scan for new documents in LightRAG",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_documents",
            description="Retrieve all documents from LightRAG",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_documents_paginated",
            description="Retrieve documents with pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-based)",
                        "minimum": 1
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of documents per page",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["page", "page_size"]
            }
        ),
        Tool(
            name="delete_document",
            description="Delete a specific document by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of the document to delete"
                    }
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="clear_documents",
            description="Clear all documents from LightRAG",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ])
    
    # Query Tools (2 tools)
    tools.extend([
        Tool(
            name="query_text",
            description="Query LightRAG with text",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query text"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Query mode",
                        "enum": ["naive", "local", "global", "hybrid"],
                        "default": "hybrid"
                    },
                    "only_need_context": {
                        "type": "boolean",
                        "description": "Whether to only return context without generation",
                        "default": False
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_text_stream",
            description="Stream query results from LightRAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query text"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Query mode",
                        "enum": ["naive", "local", "global", "hybrid"],
                        "default": "hybrid"
                    },
                    "only_need_context": {
                        "type": "boolean",
                        "description": "Whether to only return context without generation",
                        "default": False
                    }
                },
                "required": ["query"]
            }
        ),
    ])
    
    # Knowledge Graph Tools (7 tools)
    tools.extend([
        Tool(
            name="get_knowledge_graph",
            description="Retrieve the knowledge graph from LightRAG",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_graph_labels",
            description="Get labels from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="check_entity_exists",
            description="Check if an entity exists in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                        "description": "Name of the entity to check"
                    }
                },
                "required": ["entity_name"]
            }
        ),
        Tool(
            name="update_entity",
            description="Update an entity in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID of the entity to update"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Properties to update"
                    }
                },
                "required": ["entity_id", "properties"]
            }
        ),
        Tool(
            name="update_relation",
            description="Update a relation in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "relation_id": {
                        "type": "string",
                        "description": "ID of the relation to update"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Properties to update"
                    }
                },
                "required": ["relation_id", "properties"]
            }
        ),
        Tool(
            name="delete_entity",
            description="Delete an entity from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID of the entity to delete"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="delete_relation",
            description="Delete a relation from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "relation_id": {
                        "type": "string",
                        "description": "ID of the relation to delete"
                    }
                },
                "required": ["relation_id"]
            }
        ),
    ])
    
    # System Management Tools (5 tools)
    tools.extend([
        Tool(
            name="get_pipeline_status",
            description="Get the pipeline status from LightRAG",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_track_status",
            description="Get track status by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_id": {
                        "type": "string",
                        "description": "ID of the track to get status for"
                    }
                },
                "required": ["track_id"]
            }
        ),
        Tool(
            name="get_document_status_counts",
            description="Get document status counts",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="clear_cache",
            description="Clear LightRAG cache",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_health",
            description="Check LightRAG server health",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ])
    
    logger.info(f"Created {len(tools)} tools")
    
    # Simple validation like working server
    for i, tool in enumerate(tools):
        if not isinstance(tool, Tool):
            raise ValueError(f"Tool {i} is not a Tool instance: {type(tool)}")
        logger.info(f"Tool {i}: {tool.name} - OK")
    
    # Create result exactly like working server
    result = ListToolsResult(tools=tools)
    logger.info(f"ListToolsResult created successfully with {len(result.tools)} tools")
    
    return tools

@server.call_tool()
async def handle_call_tool(self, request: CallToolRequest) -> dict:
    """Handle tool calls."""
    global lightrag_client
    
    # === COMPREHENSIVE LOGGING START ===
    logger.info("=" * 80)
    logger.info("MCP TOOL CALL HANDLER STARTED")
    logger.info("=" * 80)
    
    # Log all incoming parameters with full details
    logger.info(f"HANDLER INPUT ANALYSIS:")
    logger.info(f"  - self type: {type(self)}")
    logger.info(f"  - self content: {repr(self)}")
    logger.info(f"  - self length: {len(str(self)) if isinstance(self, str) else 'N/A'}")
    logger.info(f"  - request type: {type(request)}")
    logger.info(f"  - request content: {repr(request)}")
    
    # Check all attributes of self and request
    if hasattr(self, '__dict__'):
        logger.info(f"  - self.__dict__: {self.__dict__}")
    else:
        logger.info(f"  - self has no __dict__ attribute")
        
    if hasattr(request, '__dict__'):
        logger.info(f"  - request.__dict__: {request.__dict__}")
    else:
        logger.info(f"  - request has no __dict__ attribute")
        
    # Log request attributes if it's a dict
    if isinstance(request, dict):
        logger.info(f"  - request keys: {list(request.keys())}")
        logger.info(f"  - request values: {list(request.values())}")
        for key, value in request.items():
            logger.info(f"    - request['{key}'] = {repr(value)} (type: {type(value)})")
    
    # The MCP library passes tool_name as 'self' and empty dict as 'request'
    tool_name = self  # self is the tool name string
    arguments = {}   # arguments are always empty for now
    
    logger.info(f"EXTRACTED PARAMETERS:")
    logger.info(f"  - tool_name: '{tool_name}' (type: {type(tool_name)})")
    logger.info(f"  - arguments: {arguments} (type: {type(arguments)})")
    logger.info(f"  - arguments length: {len(arguments)}")
    
    # Log global client state
    logger.info(f"GLOBAL CLIENT STATE:")
    logger.info(f"  - lightrag_client is None: {lightrag_client is None}")
    if lightrag_client is not None:
        logger.info(f"  - lightrag_client type: {type(lightrag_client)}")
        logger.info(f"  - lightrag_client base_url: {getattr(lightrag_client, 'base_url', 'N/A')}")
    
    logger.info("=" * 80)



    
    logger.info(f"TOOL EXECUTION PHASE:")
    logger.info(f"  - Processing tool: '{tool_name}'")
    logger.info(f"  - Tool arguments: {json.dumps(arguments, indent=2)}")
    
    # Client initialization with detailed logging
    if lightrag_client is None:
        logger.info("CLIENT INITIALIZATION:")
        logger.info("  - LightRAG client is None, initializing new client")
        try:
            logger.info("  - Creating LightRAGClient instance...")
            
            # Get configuration from environment variables
            base_url = os.getenv("LIGHTRAG_BASE_URL", "http://localhost:9621")
            api_key = os.getenv("LIGHTRAG_API_KEY", None)
            timeout = float(os.getenv("LIGHTRAG_TIMEOUT", "30.0"))
            
            logger.info("CLIENT CONFIGURATION:")
            logger.info(f"  - base_url: {base_url}")
            logger.info(f"  - api_key: {'***REDACTED***' if api_key else 'None'}")
            logger.info(f"  - timeout: {timeout}")
            
            lightrag_client = LightRAGClient(
                base_url=base_url,
                api_key=api_key,
                timeout=timeout
            )
            logger.info(f"  - Client initialized successfully: {type(lightrag_client)}")
            logger.info(f"  - Client base_url: {lightrag_client.base_url}")
            logger.info(f"  - Client timeout: {lightrag_client.timeout}")
            logger.info(f"  - Client has API key: {lightrag_client.api_key is not None}")
        except Exception as e:
            logger.error(f"CLIENT INITIALIZATION FAILED:")
            logger.error(f"  - Exception type: {type(e)}")
            logger.error(f"  - Exception message: {str(e)}")
            logger.error(f"  - Exception args: {e.args}")
            import traceback
            logger.error(f"  - Full traceback: {traceback.format_exc()}")
            return _create_error_response(
                LightRAGConnectionError(f"Failed to initialize LightRAG client: {str(e)}"),
                tool_name
            )
    else:
        logger.info("CLIENT STATE:")
        logger.info(f"  - Using existing LightRAG client: {type(lightrag_client)}")
        logger.info(f"  - Client base_url: {lightrag_client.base_url}")
    
    try:
        logger.info("ARGUMENT VALIDATION:")
        logger.info(f"  - Validating arguments for tool: {tool_name}")
        logger.info(f"  - Arguments to validate: {arguments}")
        
        # Validate that required arguments are present for each tool
        _validate_tool_arguments(tool_name, arguments)
        logger.info("  - Argument validation passed")
        
        logger.info("TOOL DISPATCH:")
        logger.info(f"  - Dispatching to tool handler for: {tool_name}")
        
        # Document Management Tools (8 tools)
        if tool_name == "insert_text":
            result = await lightrag_client.insert_text(arguments["text"])
            return _create_success_response(result, tool_name)
        
        elif tool_name == "insert_texts":
            result = await lightrag_client.insert_texts(arguments["texts"])
            return _create_success_response(result, tool_name)
        
        elif tool_name == "upload_document":
            result = await lightrag_client.upload_document(arguments["file_path"])
            return _create_success_response(result, tool_name)
        
        elif tool_name == "scan_documents":
            result = await lightrag_client.scan_documents()
            return _create_success_response(result, tool_name)
        
        elif tool_name == "get_documents":
            result = await lightrag_client.get_documents()
            return _create_success_response(result, tool_name)
        
        elif tool_name == "get_documents_paginated":
            result = await lightrag_client.get_documents_paginated(
                arguments["page"], arguments["page_size"]
            )
            return _create_success_response(result, tool_name)
        
        elif tool_name == "delete_document":
            result = await lightrag_client.delete_document(arguments["document_id"])
            return _create_success_response(result, tool_name)
        
        elif tool_name == "clear_documents":
            result = await lightrag_client.clear_documents()
            return _create_success_response(result, tool_name)
        
        # Query Tools (2 tools)
        elif tool_name == "query_text":
            logger.info("EXECUTING QUERY_TEXT TOOL:")
            logger.info(f"  - Tool: {tool_name}")
            logger.info(f"  - Client type: {type(lightrag_client)}")
            logger.info(f"  - Client base_url: {lightrag_client.base_url}")
            logger.info(f"  - Raw arguments: {arguments}")
            
            # Extract and validate parameters
            query = arguments.get("query", "")
            mode = arguments.get("mode", "hybrid")
            only_need_context = arguments.get("only_need_context", False)
            
            logger.info(f"QUERY_TEXT PARAMETERS:")
            logger.info(f"  - query: '{query}' (length: {len(query)})")
            logger.info(f"  - mode: '{mode}'")
            logger.info(f"  - only_need_context: {only_need_context}")
            logger.info(f"  - query type: {type(query)}")
            
            # Validate query
            if not query or not query.strip():
                logger.error("QUERY_TEXT VALIDATION ERROR:")
                logger.error("  - Query is empty or whitespace only")
                raise LightRAGValidationError("Query cannot be empty")
            
            valid_modes = ["naive", "local", "global", "hybrid"]
            if mode not in valid_modes:
                logger.error("QUERY_TEXT MODE ERROR:")
                logger.error(f"  - Invalid mode: '{mode}'")
                logger.error(f"  - Valid modes: {valid_modes}")
                raise LightRAGValidationError(f"Invalid query mode '{mode}'. Must be one of: {valid_modes}")
            
            logger.info("  - Parameter validation passed")
            logger.info("  - Calling lightrag_client.query_text()...")
            
            try:
                result = await lightrag_client.query_text(
                    query, mode=mode, only_need_context=only_need_context
                )
                logger.info("QUERY_TEXT SUCCESS:")
                logger.info(f"  - Result type: {type(result)}")
                logger.info(f"  - Result content: {repr(result)}")
                if hasattr(result, '__dict__'):
                    logger.info(f"  - Result.__dict__: {result.__dict__}")
                if hasattr(result, 'model_dump'):
                    try:
                        result_dump = result.model_dump()
                        logger.info(f"  - Result.model_dump(): {result_dump}")
                        logger.info(f"  - Response length: {len(str(result_dump.get('response', '')))}")
                        logger.info(f"  - Results count: {len(result_dump.get('results', []))}")
                    except Exception as e:
                        logger.error(f"  - model_dump() failed: {e}")
                
                logger.info("  - Calling _create_success_response()...")
                response = _create_success_response(result, tool_name)
                logger.info(f"  - Success response type: {type(response)}")
                logger.info(f"  - Success response keys: {list(response.keys())}")
                return response
            except Exception as e:
                logger.error("QUERY_TEXT FAILED:")
                logger.error(f"  - Exception type: {type(e)}")
                logger.error(f"  - Exception message: {str(e)}")
                logger.error(f"  - Exception args: {e.args}")
                logger.error(f"  - Query: '{query}'")
                logger.error(f"  - Mode: '{mode}'")
                logger.error(f"  - Only need context: {only_need_context}")
                import traceback
                logger.error(f"  - Full traceback: {traceback.format_exc()}")
                raise
        
        elif tool_name == "query_text_stream":
            mode = arguments.get("mode", "hybrid")
            only_need_context = arguments.get("only_need_context", False)
            
            # Collect streaming results
            chunks = []
            async for chunk in lightrag_client.query_text_stream(
                arguments["query"], mode=mode, only_need_context=only_need_context
            ):
                chunks.append(chunk)
            
            result = {"streaming_response": "".join(chunks)}
            logger.info(f"Successfully executed {tool_name}, collected {len(chunks)} chunks")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        # Knowledge Graph Tools (7 tools)
        elif tool_name == "get_knowledge_graph":
            result = await lightrag_client.get_knowledge_graph()
            return _create_success_response(result, tool_name)
        
        elif tool_name == "get_graph_labels":
            result = await lightrag_client.get_graph_labels()
            return _create_success_response(result, tool_name)
        
        elif tool_name == "check_entity_exists":
            result = await lightrag_client.check_entity_exists(arguments["entity_name"])
            return _create_success_response(result, tool_name)
        
        elif tool_name == "update_entity":
            result = await lightrag_client.update_entity(
                arguments["entity_id"], arguments["properties"]
            )
            return _create_success_response(result, tool_name)
        
        elif tool_name == "update_relation":
            result = await lightrag_client.update_relation(
                arguments["relation_id"], arguments["properties"]
            )
            return _create_success_response(result, tool_name)
        
        elif tool_name == "delete_entity":
            result = await lightrag_client.delete_entity(arguments["entity_id"])
            return _create_success_response(result, tool_name)
        
        elif tool_name == "delete_relation":
            result = await lightrag_client.delete_relation(arguments["relation_id"])
            return _create_success_response(result, tool_name)
        
        # System Management Tools (5 tools)
        elif tool_name == "get_pipeline_status":
            logger.info("EXECUTING GET_PIPELINE_STATUS TOOL:")
            logger.info(f"  - Tool: {tool_name}")
            logger.info(f"  - Client type: {type(lightrag_client)}")
            logger.info(f"  - Client base_url: {lightrag_client.base_url}")
            logger.info(f"  - Arguments: {arguments}")
            logger.info(f"  - Arguments length: {len(arguments)}")
            logger.info("  - This tool requires no parameters")
            logger.info("  - Calling lightrag_client.get_pipeline_status()...")
            
            try:
                result = await lightrag_client.get_pipeline_status()
                logger.info("GET_PIPELINE_STATUS SUCCESS:")
                logger.info(f"  - Result type: {type(result)}")
                logger.info(f"  - Result content: {repr(result)}")
                if hasattr(result, '__dict__'):
                    logger.info(f"  - Result.__dict__: {result.__dict__}")
                if hasattr(result, 'model_dump'):
                    try:
                        result_dump = result.model_dump()
                        logger.info(f"  - Result.model_dump(): {result_dump}")
                        logger.info(f"PIPELINE STATUS DETAILS:")
                        logger.info(f"    - autoscanned: {result_dump.get('autoscanned', 'N/A')}")
                        logger.info(f"    - busy: {result_dump.get('busy', 'N/A')}")
                        logger.info(f"    - job_name: {result_dump.get('job_name', 'N/A')}")
                        logger.info(f"    - job_start: {result_dump.get('job_start', 'N/A')}")
                        logger.info(f"    - docs: {result_dump.get('docs', 'N/A')}")
                        logger.info(f"    - batchs: {result_dump.get('batchs', 'N/A')}")
                        logger.info(f"    - cur_batch: {result_dump.get('cur_batch', 'N/A')}")
                        logger.info(f"    - request_pending: {result_dump.get('request_pending', 'N/A')}")
                        logger.info(f"    - progress: {result_dump.get('progress', 'N/A')}")
                        logger.info(f"    - current_task: {result_dump.get('current_task', 'N/A')}")
                        logger.info(f"    - latest_message: {result_dump.get('latest_message', 'N/A')}")
                        history_messages = result_dump.get('history_messages', [])
                        logger.info(f"    - history_messages count: {len(history_messages) if history_messages else 0}")
                        if history_messages:
                            logger.info(f"    - latest history message: {history_messages[-1] if history_messages else 'N/A'}")
                    except Exception as e:
                        logger.error(f"  - model_dump() failed: {e}")
                
                logger.info("  - Calling _create_success_response()...")
                response = _create_success_response(result, tool_name)
                logger.info(f"  - Success response type: {type(response)}")
                logger.info(f"  - Success response keys: {list(response.keys())}")
                return response
            except Exception as e:
                logger.error("GET_PIPELINE_STATUS FAILED:")
                logger.error(f"  - Exception type: {type(e)}")
                logger.error(f"  - Exception message: {str(e)}")
                logger.error(f"  - Exception args: {e.args}")
                import traceback
                logger.error(f"  - Full traceback: {traceback.format_exc()}")
                raise
        
        elif tool_name == "get_track_status":
            result = await lightrag_client.get_track_status(arguments["track_id"])
            return _create_success_response(result, tool_name)
        
        elif tool_name == "get_document_status_counts":
            result = await lightrag_client.get_document_status_counts()
            return _create_success_response(result, tool_name)
        
        elif tool_name == "clear_cache":
            result = await lightrag_client.clear_cache()
            return _create_success_response(result, tool_name)
        
        elif tool_name == "get_health":
            logger.info("EXECUTING GET_HEALTH TOOL:")
            logger.info(f"  - Tool: {tool_name}")
            logger.info(f"  - Client type: {type(lightrag_client)}")
            logger.info(f"  - Client base_url: {lightrag_client.base_url}")
            logger.info("  - Calling lightrag_client.get_health()...")
            
            try:
                result = await lightrag_client.get_health()
                logger.info("GET_HEALTH SUCCESS:")
                logger.info(f"  - Result type: {type(result)}")
                logger.info(f"  - Result content: {repr(result)}")
                if hasattr(result, '__dict__'):
                    logger.info(f"  - Result.__dict__: {result.__dict__}")
                if hasattr(result, 'model_dump'):
                    logger.info(f"  - Result.model_dump(): {result.model_dump()}")
                logger.info("  - Calling _create_success_response()...")
                response = _create_success_response(result, tool_name)
                logger.info(f"  - Success response type: {type(response)}")
                logger.info(f"  - Success response: {response}")
                return response
            except Exception as e:
                logger.error("GET_HEALTH FAILED:")
                logger.error(f"  - Exception type: {type(e)}")
                logger.error(f"  - Exception message: {str(e)}")
                logger.error(f"  - Exception args: {e.args}")
                import traceback
                logger.error(f"  - Full traceback: {traceback.format_exc()}")
                raise
        
        else:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )
    
    except LightRAGError as e:
        logger.error("LIGHTRAG EXCEPTION CAUGHT:")
        logger.error(f"  - Exception type: {type(e)}")
        logger.error(f"  - Exception message: {str(e)}")
        logger.error(f"  - Tool name: {tool_name}")
        logger.error(f"  - Status code: {getattr(e, 'status_code', 'N/A')}")
        logger.error(f"  - Response data: {getattr(e, 'response_data', 'N/A')}")
        import traceback
        logger.error(f"  - Traceback: {traceback.format_exc()}")
        return _create_error_response(e, tool_name)
    
    except Exception as e:
        logger.error("GENERIC EXCEPTION CAUGHT:")
        logger.error(f"  - Exception type: {type(e)}")
        logger.error(f"  - Exception message: {str(e)}")
        logger.error(f"  - Exception args: {e.args}")
        logger.error(f"  - Tool name: {tool_name}")
        import traceback
        logger.error(f"  - Traceback: {traceback.format_exc()}")
        return _create_error_response(e, tool_name)


async def main():
    """Main entry point for the MCP server."""
    logger.info("=" * 100)
    logger.info("STARTING LIGHTRAG MCP SERVER")
    logger.info("=" * 100)
    
    # Log system information
    import sys
    import platform
    logger.info("SYSTEM INFORMATION:")
    logger.info(f"  - Python version: {sys.version}")
    logger.info(f"  - Platform: {platform.platform()}")
    logger.info(f"  - Current working directory: {os.getcwd()}")
    logger.info(f"  - Script path: {__file__}")
    
    # Log environment variables
    logger.info("ENVIRONMENT VARIABLES:")
    for key, value in os.environ.items():
        if 'LIGHTRAG' in key.upper() or 'MCP' in key.upper():
            logger.info(f"  - {key}: {value}")
    
    try:
        logger.info("SERVER INITIALIZATION:")
        logger.info("  - Validating server configuration...")
        logger.info(f"  - Server name: daniel-lightrag-mcp")
        logger.info(f"  - Server object: {server}")
        logger.info(f"  - Server type: {type(server)}")
        
        logger.info("STDIO SERVER SETUP:")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("  - STDIO server context entered successfully")
            logger.info(f"  - Read stream: {read_stream}")
            logger.info(f"  - Write stream: {write_stream}")
            logger.info("  - MCP server initialized, starting communication loop")
            
            # Initialize server capabilities
            logger.info("CAPABILITIES INITIALIZATION:")
            capabilities = server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            )
            logger.info(f"  - Server capabilities: {capabilities}")
            logger.info(f"  - Capabilities type: {type(capabilities)}")
            
            # Create initialization options
            init_options = InitializationOptions(
                server_name="daniel-lightrag-mcp",
                server_version="0.1.0",
                capabilities=capabilities,
            )
            logger.info(f"INITIALIZATION OPTIONS:")
            logger.info(f"  - Init options: {init_options}")
            logger.info(f"  - Init options type: {type(init_options)}")
            
            logger.info("STARTING SERVER RUN LOOP:")
            await server.run(
                read_stream,
                write_stream,
                init_options,
            )
            
    except KeyboardInterrupt:
        logger.info("SERVER SHUTDOWN:")
        logger.info("  - Server shutdown requested by user (KeyboardInterrupt)")
    except ConnectionError as e:
        logger.error("CONNECTION ERROR:")
        logger.error(f"  - Connection error during server startup: {e}")
        logger.error(f"  - Error type: {type(e)}")
        logger.error(f"  - Error args: {e.args}")
        import traceback
        logger.error(f"  - Traceback: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error("FATAL SERVER ERROR:")
        logger.error(f"  - Fatal server error: {e}")
        logger.error(f"  - Error type: {type(e)}")
        logger.error(f"  - Error args: {e.args}")
        import traceback
        logger.error(f"  - Traceback: {traceback.format_exc()}")
        raise
    finally:
        logger.info("SERVER CLEANUP:")
        logger.info("  - LightRAG MCP server shutting down")
        global lightrag_client
        if lightrag_client:
            logger.info("  - Closing LightRAG client...")
            try:
                await lightrag_client.__aexit__(None, None, None)
                logger.info("  - LightRAG client closed successfully")
            except Exception as e:
                logger.warning(f"  - Error closing LightRAG client: {e}")
                logger.warning(f"  - Error type: {type(e)}")
        else:
            logger.info("  - No LightRAG client to close")
        logger.info("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
