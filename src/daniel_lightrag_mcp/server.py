"""
MCP server for LightRAG integration.
SSE-version for Docker / remote usage.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, CallToolResult
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from uvicorn import Config, Server as UvicornServer

from .client import (
    LightRAGClient,
    LightRAGError,
    LightRAGConnectionError,
    LightRAGAuthError,
    LightRAGValidationError,
    LightRAGAPIError,
    LightRAGTimeoutError,
    LightRAGServerError,
)

# ----------------------- logging -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.INFO)

# ----------------------- globals -----------------------
server = Server("daniel-lightrag-mcp")
lightrag_client: Optional[LightRAGClient] = None


# =================== ваши функции ===================
def _validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> None:
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
        "update_relation": ["source_id", "target_id", "updated_data"],
        "delete_entity": ["entity_id"],
        "delete_relation": ["relation_id"],
        "get_track_status": ["track_id"],
    }

    if tool_name in required_args:
        missing = [a for a in required_args[tool_name] if a not in arguments]
        if missing:
            raise LightRAGValidationError(f"Missing required arguments for {tool_name}: {missing}")

    if tool_name == "get_documents_paginated":
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 10)
        if not isinstance(page, int) or page < 1:
            raise LightRAGValidationError("Page must be a positive integer")
        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            raise LightRAGValidationError("Page size must be an integer between 1 and 100")

    if tool_name in ("query_text", "query_text_stream"):
        mode = arguments.get("mode", "hybrid")
        if mode not in ("naive", "local", "global", "hybrid"):
            raise LightRAGValidationError(f"Invalid query mode '{mode}'")


def _serialize_result(result: Any) -> str:
    if hasattr(result, "model_dump"):
        return json.dumps(result.model_dump(), indent=2)
    if hasattr(result, "__dict__"):
        return json.dumps(result.__dict__, indent=2)
    return json.dumps(result, indent=2)


def _create_success_response(result: Any, tool_name: str) -> dict:
    return {
        "content": [{"type": "text", "text": _serialize_result(result)}]
    }


def _create_error_response(error: Exception, tool_name: str) -> dict:
    details = {
        "tool": tool_name,
        "error_type": type(error).__name__,
        "message": str(error),
    }
    if isinstance(error, LightRAGError) and hasattr(error, "to_dict"):
        details.update(error.to_dict())
    return {
        "content": [{"type": "text", "text": json.dumps(details, indent=2)}],
        "isError": True,
    }


# =================== MCP tools ===================
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    tools = [
        Tool(
            name="insert_text",
            description="Insert text content into LightRAG",
            inputSchema={
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Text content to insert"}},
                "required": ["text"],
            },
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
                                "metadata": {"type": "object"},
                            },
                            "required": ["content"],
                        },
                        "description": "Array of text documents to insert",
                    }
                },
                "required": ["texts"],
            },
        ),
        Tool(
            name="upload_document",
            description="Upload a document file to LightRAG",
            inputSchema={
                "type": "object",
                "properties": {"file_path": {"type": "string", "description": "Path to the file to upload"}},
                "required": ["file_path"],
            },
        ),
        Tool(
            name="scan_documents",
            description="Scan for new documents in LightRAG",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_documents",
            description="Retrieve all documents from LightRAG",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_documents_paginated",
            description="Retrieve documents with pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "minimum": 1, "description": "Page number (1-based)"},
                    "page_size": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Docs per page"},
                },
                "required": ["page", "page_size"],
            },
        ),
        Tool(
            name="delete_document",
            description="Delete a specific document by ID",
            inputSchema={
                "type": "object",
                "properties": {"document_id": {"type": "string", "description": "ID of the document to delete"}},
                "required": ["document_id"],
            },
        ),
        Tool(
            name="query_text",
            description="Query LightRAG with text",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query text"},
                    "mode": {"type": "string", "enum": ["naive", "local", "global", "hybrid"], "default": "hybrid"},
                    "only_need_context": {"type": "boolean", "default": False},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="query_text_stream",
            description="Stream query results from LightRAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query text"},
                    "mode": {"type": "string", "enum": ["naive", "local", "global", "hybrid"], "default": "hybrid"},
                    "only_need_context": {"type": "boolean", "default": False},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_knowledge_graph",
            description="Retrieve the knowledge graph from LightRAG",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_graph_labels",
            description="Get labels from the knowledge graph",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="check_entity_exists",
            description="Check if an entity exists in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {"entity_name": {"type": "string", "description": "Name of the entity to check"}},
                "required": ["entity_name"],
            },
        ),
        Tool(
            name="update_entity",
            description="Update an entity in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "ID of the entity to update"},
                    "properties": {"type": "object", "description": "Properties to update"},
                },
                "required": ["entity_id", "properties"],
            },
        ),
        Tool(
            name="update_relation",
            description="Update a relation in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {"type": "string", "description": "ID of the source entity"},
                    "target_id": {"type": "string", "description": "ID of the target entity"},
                    "updated_data": {"type": "object", "description": "Properties to update on the relation"},
                },
                "required": ["source_id", "target_id", "updated_data"],
            },
        ),
        Tool(
            name="delete_entity",
            description="Delete an entity from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {"entity_id": {"type": "string", "description": "ID of the entity to delete"}},
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="delete_relation",
            description="Delete a relation from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {"relation_id": {"type": "string", "description": "ID of the relation to delete"}},
                "required": ["relation_id"],
            },
        ),
        Tool(
            name="get_pipeline_status",
            description="Get the pipeline status from LightRAG",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_track_status",
            description="Get track status by ID",
            inputSchema={
                "type": "object",
                "properties": {"track_id": {"type": "string", "description": "ID of the track to get status for"}},
                "required": ["track_id"],
            },
        ),
        Tool(
            name="get_document_status_counts",
            description="Get document status counts",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_health",
            description="Check LightRAG server health",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]
    return tools


@server.call_tool()
async def handle_call_tool(tool_name: str, arguments: Dict[str, Any]) -> dict:
    global lightrag_client

    if lightrag_client is None:
        lightrag_client = LightRAGClient(
            base_url=os.getenv("LIGHTRAG_BASE_URL", "http://localhost:9621"),
            api_key=os.getenv("LIGHTRAG_API_KEY") or None,
            timeout=float(os.getenv("LIGHTRAG_TIMEOUT", "30.0")),
        )

    try:
        _validate_tool_arguments(tool_name, arguments)

        # ---------- Document Management ----------
        if tool_name == "insert_text":
            text = arguments["text"]
            result = await lightrag_client.insert_text(text)
            return _create_success_response(result, tool_name)

        if tool_name == "insert_texts":
            result = await lightrag_client.insert_texts(arguments["texts"])
            return _create_success_response(result, tool_name)

        if tool_name == "upload_document":
            file_path = arguments["file_path"]
            if not os.path.exists(file_path):
                raise LightRAGValidationError(f"File does not exist: {file_path}")
            result = await lightrag_client.upload_document(file_path)
            return _create_success_response(result, tool_name)

        if tool_name == "scan_documents":
            result = await lightrag_client.scan_documents()
            return _create_success_response(result, tool_name)

        if tool_name == "get_documents":
            result = await lightrag_client.get_documents()
            return _create_success_response(result, tool_name)

        if tool_name == "get_documents_paginated":
            result = await lightrag_client.get_documents_paginated(
                arguments["page"], arguments["page_size"]
            )
            return _create_success_response(result, tool_name)

        if tool_name == "delete_document":
            result = await lightrag_client.delete_document(arguments["document_id"])
            return _create_success_response(result, tool_name)

        # ---------- Query ----------
        if tool_name == "query_text":
            result = await lightrag_client.query_text(
                arguments["query"],
                mode=arguments.get("mode", "hybrid"),
                only_need_context=arguments.get("only_need_context", False),
            )
            return _create_success_response(result, tool_name)

        if tool_name == "query_text_stream":
            chunks = []
            async for chunk in lightrag_client.query_text_stream(
                arguments["query"],
                mode=arguments.get("mode", "hybrid"),
                only_need_context=arguments.get("only_need_context", False),
            ):
                chunks.append(chunk)
            result = {"streaming_response": "".join(chunks)}
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }

        # ---------- Knowledge Graph ----------
        if tool_name == "get_knowledge_graph":
            result = await lightrag_client.get_knowledge_graph()
            return _create_success_response(result, tool_name)

        if tool_name == "get_graph_labels":
            result = await lightrag_client.get_graph_labels()
            return _create_success_response(result, tool_name)

        if tool_name == "check_entity_exists":
            result = await lightrag_client.check_entity_exists(arguments["entity_name"])
            return _create_success_response(result, tool_name)

        if tool_name == "update_entity":
            result = await lightrag_client.update_entity(
                arguments["entity_id"], arguments["properties"]
            )
            return _create_success_response(result, tool_name)

        if tool_name == "update_relation":
            result = await lightrag_client.update_relation(
                arguments["source_id"], arguments["target_id"], arguments["updated_data"]
            )
            return _create_success_response(result, tool_name)

        if tool_name == "delete_entity":
            result = await lightrag_client.delete_entity(arguments["entity_id"])
            return _create_success_response(result, tool_name)

        if tool_name == "delete_relation":
            result = await lightrag_client.delete_relation(arguments["relation_id"])
            return _create_success_response(result, tool_name)

        # ---------- System ----------
        if tool_name == "get_pipeline_status":
            result = await lightrag_client.get_pipeline_status()
            return _create_success_response(result, tool_name)

        if tool_name == "get_track_status":
            result = await lightrag_client.get_track_status(arguments["track_id"])
            return _create_success_response(result, tool_name)

        if tool_name == "get_document_status_counts":
            result = await lightrag_client.get_document_status_counts()
            return _create_success_response(result, tool_name)

        if tool_name == "get_health":
            result = await lightrag_client.get_health()
            return _create_success_response(result, tool_name)

        # ---------- Unknown ----------
        raise ValueError(f"Unknown tool: {tool_name}")

    except LightRAGError as e:
        return _create_error_response(e, tool_name)
    except Exception as e:
        logger.exception("Unhandled exception in tool call")
        return _create_error_response(e, tool_name)


# =================== SSE + Uvicorn entrypoint ===================
sse_transport = SseServerTransport("/message")


async def sse_endpoint(request):
    async with sse_transport.connect_sse(request) as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


def create_starlette_app() -> Starlette:
    return Starlette(
        routes=[
            Route("/sse", endpoint=sse_endpoint),
            Mount("/message", app=sse_transport.handle_post_message),
        ]
    )


async def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Starting LightRAG MCP SSE server on %s:%s", host, port)

    app = create_starlette_app()
    config = Config(app, host=host, port=port, log_level=log_level)
    await UvicornServer(config).serve()


if __name__ == "__main__":
    asyncio.run(main())
