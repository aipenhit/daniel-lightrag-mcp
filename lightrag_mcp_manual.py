#!/usr/bin/env python3
"""
Manual MCP server for LightRAG integration - bypasses MCP library issues.
"""

import asyncio
import json
import sys
import logging
import os
from typing import Dict, Any, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daniel_lightrag_mcp.client import (
    LightRAGClient, 
    LightRAGError, 
    LightRAGConnectionError, 
    LightRAGAuthError, 
    LightRAGValidationError, 
    LightRAGAPIError,
    LightRAGTimeoutError,
    LightRAGServerError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightRAGMCPServer:
    """Manual MCP server for LightRAG."""
    
    def __init__(self):
        self.tools = self._define_tools()
        self.lightrag_client = None
        
        # Get configuration from environment
        self.base_url = os.getenv("LIGHTRAG_BASE_URL", "http://localhost:9621")
        self.api_key = os.getenv("LIGHTRAG_API_KEY")
        self.timeout = float(os.getenv("LIGHTRAG_TIMEOUT", "30.0"))
        
        logger.info(f"LightRAG MCP Server configured with base_url: {self.base_url}")
    
    async def _get_client(self) -> LightRAGClient:
        """Get or create LightRAG client."""
        if self.lightrag_client is None:
            self.lightrag_client = LightRAGClient(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout
            )
            logger.info("LightRAG client initialized")
        return self.lightrag_client
        
    def _define_tools(self) -> list:
        """Define all 22 LightRAG tools."""
        return [
            # Document Management Tools (8 tools)
            {
                "name": "insert_text",
                "description": "Insert text content into LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text content to insert"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "insert_texts",
                "description": "Insert multiple text documents into LightRAG",
                "inputSchema": {
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
            },
            {
                "name": "upload_document",
                "description": "Upload a document file to LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file to upload"}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "scan_documents",
                "description": "Scan for new documents in LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_documents",
                "description": "Retrieve all documents from LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_documents_paginated",
                "description": "Retrieve documents with pagination",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "page": {"type": "integer", "description": "Page number (1-based)", "minimum": 1},
                        "page_size": {"type": "integer", "description": "Number of documents per page", "minimum": 10, "maximum": 100}
                    },
                    "required": ["page", "page_size"]
                }
            },
            {
                "name": "delete_document",
                "description": "Delete a specific document by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "ID of the document to delete"}
                    },
                    "required": ["document_id"]
                }
            },
            {
                "name": "clear_documents",
                "description": "Clear all documents from LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            
            # Query Tools (2 tools)
            {
                "name": "query_text",
                "description": "Query LightRAG with text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Query text"},
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
            },
            {
                "name": "query_text_stream",
                "description": "Stream query results from LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Query text"},
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
            },
            
            # Knowledge Graph Tools (7 tools)
            {
                "name": "get_knowledge_graph",
                "description": "Retrieve the knowledge graph from LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_graph_labels",
                "description": "Get labels from the knowledge graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "check_entity_exists",
                "description": "Check if an entity exists in the knowledge graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_name": {"type": "string", "description": "Name of the entity to check"}
                    },
                    "required": ["entity_name"]
                }
            },
            {
                "name": "update_entity",
                "description": "Update an entity in the knowledge graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_id": {"type": "string", "description": "ID of the entity to update"},
                        "properties": {"type": "object", "description": "Properties to update"}
                    },
                    "required": ["entity_id", "properties"]
                }
            },
            {
                "name": "update_relation",
                "description": "Update a relation in the knowledge graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "relation_id": {"type": "string", "description": "ID of the relation to update"},
                        "properties": {"type": "object", "description": "Properties to update"}
                    },
                    "required": ["relation_id", "properties"]
                }
            },
            {
                "name": "delete_entity",
                "description": "Delete an entity from the knowledge graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_id": {"type": "string", "description": "ID of the entity to delete"}
                    },
                    "required": ["entity_id"]
                }
            },
            {
                "name": "delete_relation",
                "description": "Delete a relation from the knowledge graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "relation_id": {"type": "string", "description": "ID of the relation to delete"}
                    },
                    "required": ["relation_id"]
                }
            },
            
            # System Management Tools (5 tools)
            {
                "name": "get_pipeline_status",
                "description": "Get the pipeline status from LightRAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_track_status",
                "description": "Get track status by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "track_id": {"type": "string", "description": "ID of the track to get status for"}
                    },
                    "required": ["track_id"]
                }
            },
            {
                "name": "get_document_status_counts",
                "description": "Get document status counts",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "clear_cache",
                "description": "Clear LightRAG cache",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_health",
                "description": "Check LightRAG server health",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def handle_request(self, request_data: str) -> str:
        """Handle MCP requests."""
        try:
            request = json.loads(request_data)
            method = request.get("method")
            request_id = request.get("id")
            
            logger.info(f"Handling request: {method}")
            
            if method == "initialize":
                return self._handle_initialize(request_id)
            elif method == "tools/list":
                return self._handle_list_tools(request_id)
            elif method == "tools/call":
                return await self._handle_call_tool(request, request_id)
            elif method == "notifications/initialized":
                # Just acknowledge - no response needed for notifications
                return ""
            else:
                return self._create_error_response(request_id, -32601, f"Method not found: {method}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._create_error_response(None, -32700, "Parse error")
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._create_error_response(request.get("id"), -32603, f"Internal error: {str(e)}")
    
    def _handle_initialize(self, request_id: int) -> str:
        """Handle initialization request."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "lightrag-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
        return json.dumps(response)
    
    def _handle_list_tools(self, request_id: int) -> str:
        """Handle tools list request."""
        logger.info(f"Returning {len(self.tools)} tools")
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
        return json.dumps(response)
    
    async def _handle_call_tool(self, request: Dict[str, Any], request_id: int) -> str:
        """Handle tool call request."""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        try:
            client = await self._get_client()
            logger.debug(f"Client initialized for {tool_name}, attempting API call...")
            
            # Document Management Tools
            if tool_name == "insert_text":
                logger.info(f"Calling client.insert_text with text length: {len(arguments['text'])}")
                result_data = await client.insert_text(arguments["text"])
                logger.info(f"insert_text completed successfully")
                
            elif tool_name == "insert_texts":
                logger.info(f"Calling client.insert_texts with {len(arguments['texts'])} texts")
                result_data = await client.insert_texts(arguments["texts"])
                logger.info(f"insert_texts completed successfully")
                
            elif tool_name == "upload_document":
                result_data = await client.upload_document(arguments["file_path"])
                
            elif tool_name == "scan_documents":
                result_data = await client.scan_documents()
                
            elif tool_name == "get_documents":
                result_data = await client.get_documents()
                
            elif tool_name == "get_documents_paginated":
                result_data = await client.get_documents_paginated(
                    arguments["page"], 
                    arguments["page_size"]
                )
                
            elif tool_name == "delete_document":
                result_data = await client.delete_document(arguments["document_id"])
                
            elif tool_name == "clear_documents":
                result_data = await client.clear_documents()
                
            # Query Tools
            elif tool_name == "query_text":
                mode = arguments.get("mode", "hybrid")
                only_need_context = arguments.get("only_need_context", False)
                result_data = await client.query_text(
                    arguments["query"], 
                    mode=mode, 
                    only_need_context=only_need_context
                )
                
            elif tool_name == "query_text_stream":
                mode = arguments.get("mode", "hybrid")
                only_need_context = arguments.get("only_need_context", False)
                
                # Collect streaming results
                chunks = []
                async for chunk in client.query_text_stream(
                    arguments["query"], 
                    mode=mode, 
                    only_need_context=only_need_context
                ):
                    chunks.append(chunk)
                
                result_data = {
                    "streaming_response": "".join(chunks),
                    "chunks_count": len(chunks)
                }
                
            # Knowledge Graph Tools
            elif tool_name == "get_knowledge_graph":
                result_data = await client.get_knowledge_graph()
                
            elif tool_name == "get_graph_labels":
                result_data = await client.get_graph_labels()
                
            elif tool_name == "check_entity_exists":
                result_data = await client.check_entity_exists(arguments["entity_name"])
                
            elif tool_name == "update_entity":
                result_data = await client.update_entity(
                    arguments["entity_id"], 
                    arguments["properties"]
                )
                
            elif tool_name == "update_relation":
                result_data = await client.update_relation(
                    arguments["relation_id"], 
                    arguments["properties"]
                )
                
            elif tool_name == "delete_entity":
                result_data = await client.delete_entity(arguments["entity_id"])
                
            elif tool_name == "delete_relation":
                result_data = await client.delete_relation(arguments["relation_id"])
                
            # System Management Tools
            elif tool_name == "get_pipeline_status":
                result_data = await client.get_pipeline_status()
                
            elif tool_name == "get_track_status":
                result_data = await client.get_track_status(arguments["track_id"])
                
            elif tool_name == "get_document_status_counts":
                result_data = await client.get_document_status_counts()
                
            elif tool_name == "clear_cache":
                result_data = await client.clear_cache()
                
            elif tool_name == "get_health":
                result_data = await client.get_health()
                
            else:
                return self._create_error_response(
                    request_id, 
                    -32601, 
                    f"Unknown tool: {tool_name}"
                )
            
            # Convert result to JSON string
            if hasattr(result_data, 'model_dump'):
                # Pydantic model
                result_json = json.dumps(result_data.model_dump(), indent=2)
            elif hasattr(result_data, '__dict__'):
                # Regular object with __dict__
                result_json = json.dumps(result_data.__dict__, indent=2)
            else:
                # Direct serialization
                result_json = json.dumps(result_data, indent=2)
            
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": result_json
                    }
                ]
            }
            
            logger.info(f"Tool {tool_name} executed successfully")
            
        except LightRAGConnectionError as e:
            logger.error(f"Connection error in {tool_name}: {e}")
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": "Connection Error",
                            "message": str(e),
                            "tool": tool_name,
                            "suggestion": "Ensure LightRAG server is running on " + self.base_url
                        }, indent=2)
                    }
                ],
                "isError": True
            }
            
        except LightRAGValidationError as e:
            logger.error(f"Validation error in {tool_name}: {e}")
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": "Validation Error",
                            "message": str(e),
                            "tool": tool_name,
                            "arguments": arguments
                        }, indent=2)
                    }
                ],
                "isError": True
            }
            
        except LightRAGAPIError as e:
            logger.error(f"API error in {tool_name}: {e}")
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": "API Error",
                            "message": str(e),
                            "tool": tool_name,
                            "status_code": getattr(e, 'status_code', None)
                        }, indent=2)
                    }
                ],
                "isError": True
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in {tool_name}: {e}")
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": "Unexpected Error",
                            "message": str(e),
                            "tool": tool_name,
                            "type": type(e).__name__
                        }, indent=2)
                    }
                ],
                "isError": True
            }
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
        return json.dumps(response)
    
    def _create_error_response(self, request_id: Optional[int], code: int, message: str) -> str:
        """Create error response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        return json.dumps(response)

async def main():
    """Main server loop."""
    logger.info("Starting LightRAG MCP Server (Manual Implementation)")
    
    server = LightRAGMCPServer()
    
    try:
        while True:
            # Read from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            # Handle the request
            response = await server.handle_request(line)
            
            # Write response to stdout (only if not empty)
            if response:
                print(response, flush=True)
                
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up client connection
        if server.lightrag_client:
            try:
                await server.lightrag_client.__aexit__(None, None, None)
                logger.info("LightRAG client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing LightRAG client: {e}")
        logger.info("LightRAG MCP Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())