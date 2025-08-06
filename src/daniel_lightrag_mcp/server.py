"""
MCP server for LightRAG integration.
"""

import asyncio
import json
import logging
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


def _create_success_response(result: Any, tool_name: str) -> CallToolResult:
    """Create standardized MCP success response."""
    logger.info(f"Successfully executed {tool_name}")
    return CallToolResult(
        content=[TextContent(type="text", text=_serialize_result(result))]
    )


def _create_error_response(error: Exception, tool_name: str) -> CallToolResult:
    """Create standardized MCP error response."""
    error_details = {
        "tool": tool_name,
        "error_type": type(error).__name__,
        "message": str(error),
        "timestamp": asyncio.get_event_loop().time()
    }
    
    # Add additional details for LightRAG errors
    if isinstance(error, LightRAGError):
        error_details.update(error.to_dict())
        
        # Log different error types at appropriate levels with structured context
        error_context = {
            "tool": tool_name,
            "error_type": type(error).__name__,
            "status_code": getattr(error, 'status_code', None),
            "response_data": getattr(error, 'response_data', {})
        }
        
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
        # Handle Pydantic validation errors specifically
        if hasattr(error, 'errors') and callable(getattr(error, 'errors')):
            try:
                validation_errors = error.errors()
                error_details["validation_errors"] = validation_errors
                logger.warning(f"Input validation error in {tool_name}: {validation_errors}")
            except:
                logger.error(f"Unexpected error in {tool_name}: {error}")
        else:
            logger.error(f"Unexpected error in {tool_name}: {error}")
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(error_details, indent=2))],
        isError=True
    )


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
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
    
    return result


@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    global lightrag_client
    
    # Extract tool name and arguments from params
    tool_name = request.params.name
    arguments = request.params.arguments or {}
    
    logger.info(f"Handling tool call: {tool_name}")
    logger.debug(f"Tool arguments: {json.dumps(arguments, indent=2)}")
    
    if lightrag_client is None:
        logger.info("Initializing LightRAG client")
        try:
            lightrag_client = LightRAGClient()
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG client: {e}")
            return _create_error_response(
                LightRAGConnectionError(f"Failed to initialize LightRAG client: {str(e)}"),
                tool_name
            )
    
    try:
        # Validate that required arguments are present for each tool
        _validate_tool_arguments(tool_name, arguments)
        
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
            mode = arguments.get("mode", "hybrid")
            only_need_context = arguments.get("only_need_context", False)
            result = await lightrag_client.query_text(
                arguments["query"], mode=mode, only_need_context=only_need_context
            )
            return _create_success_response(result, tool_name)
        
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
            result = await lightrag_client.get_pipeline_status()
            return _create_success_response(result, tool_name)
        
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
            result = await lightrag_client.get_health()
            return _create_success_response(result, tool_name)
        
        else:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )
    
    except LightRAGError as e:
        return _create_error_response(e, tool_name)
    
    except Exception as e:
        return _create_error_response(e, tool_name)


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting LightRAG MCP server")
    
    try:
        # Test basic server configuration
        logger.info("Validating server configuration...")
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP server initialized, starting communication loop")
            
            # Initialize server capabilities
            capabilities = server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            )
            logger.debug(f"Server capabilities: {capabilities}")
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="daniel-lightrag-mcp",
                    server_version="0.1.0",
                    capabilities=capabilities,
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except ConnectionError as e:
        logger.error(f"Connection error during server startup: {e}")
        raise
    except Exception as e:
        logger.error(f"Fatal server error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        logger.info("LightRAG MCP server shutting down")
        global lightrag_client
        if lightrag_client:
            try:
                await lightrag_client.__aexit__(None, None, None)
                logger.info("LightRAG client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing LightRAG client: {e}")


if __name__ == "__main__":
    asyncio.run(main())
