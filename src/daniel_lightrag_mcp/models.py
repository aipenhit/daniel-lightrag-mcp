"""
Pydantic models for LightRAG API requests and responses.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# Enums for status types and mode parameters
class DocStatus(str, Enum):
    """Document status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DELETED = "deleted"


class QueryMode(str, Enum):
    """Query mode enumeration."""
    NAIVE = "naive"
    LOCAL = "local"
    GLOBAL = "global"
    HYBRID = "hybrid"


class PipelineStatus(str, Enum):
    """Pipeline status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Common Models
class TextDocument(BaseModel):
    """Text document model."""
    title: Optional[str] = None
    content: str = Field(..., description="Document content")
    metadata: Optional[Dict[str, Any]] = None


class PaginationInfo(BaseModel):
    """Pagination information model."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")
    total_pages: Optional[int] = None
    total_items: Optional[int] = None


class ValidationError(BaseModel):
    """Validation error model."""
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    """HTTP validation error model."""
    detail: List[ValidationError]


# Document Management Request Models
class InsertTextRequest(BaseModel):
    """Request model for inserting a single text document."""
    title: Optional[str] = None
    content: str = Field(..., description="Text content to insert")


class InsertTextsRequest(BaseModel):
    """Request model for inserting multiple text documents."""
    texts: List[TextDocument] = Field(..., description="List of text documents to insert")


class DeleteDocRequest(BaseModel):
    """Request model for deleting a document by ID."""
    document_id: str = Field(..., description="ID of the document to delete")


class DeleteEntityRequest(BaseModel):
    """Request model for deleting an entity."""
    entity_id: str = Field(..., description="ID of the entity to delete")


class DeleteRelationRequest(BaseModel):
    """Request model for deleting a relation."""
    relation_id: str = Field(..., description="ID of the relation to delete")


class DocumentsRequest(BaseModel):
    """Request model for paginated documents."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")
    status_filter: Optional[DocStatus] = None


class ClearCacheRequest(BaseModel):
    """Request model for clearing cache."""
    cache_type: Optional[str] = None


# Query Request Models
class QueryRequest(BaseModel):
    """Request model for text queries."""
    query: str = Field(..., description="Query text")
    mode: QueryMode = Field(QueryMode.HYBRID, description="Query mode")
    only_need_context: bool = Field(False, description="Whether to only return context")
    stream: bool = Field(False, description="Whether to stream results")


# Knowledge Graph Request Models
class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""
    entity_id: str = Field(..., description="ID of the entity to update")
    properties: Dict[str, Any] = Field(..., description="Properties to update")


class RelationUpdateRequest(BaseModel):
    """Request model for updating a relation."""
    relation_id: str = Field(..., description="ID of the relation to update")
    properties: Dict[str, Any] = Field(..., description="Properties to update")


class EntityExistsRequest(BaseModel):
    """Request model for checking if entity exists."""
    entity_name: str = Field(..., description="Name of the entity to check")


# Authentication Request Models
class LoginRequest(BaseModel):
    """Request model for login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


# Document Management Response Models
class InsertResponse(BaseModel):
    """Response model for document insertion."""
    id: str = Field(..., description="Document ID")
    status: str = Field(..., description="Insertion status")
    message: Optional[str] = None


class ScanResponse(BaseModel):
    """Response model for document scanning."""
    scanned: int = Field(..., description="Number of documents scanned")
    new_documents: List[str] = Field(default_factory=list, description="List of new document names")
    message: Optional[str] = None


class UploadResponse(BaseModel):
    """Response model for file upload."""
    filename: str = Field(..., description="Uploaded filename")
    status: str = Field(..., description="Upload status")
    message: Optional[str] = None


class DocumentInfo(BaseModel):
    """Document information model."""
    id: str = Field(..., description="Document ID")
    title: Optional[str] = None
    status: DocStatus = Field(..., description="Document status")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentsResponse(BaseModel):
    """Response model for retrieving documents."""
    documents: List[DocumentInfo] = Field(default_factory=list)
    total: Optional[int] = None


class PaginatedDocsResponse(BaseModel):
    """Response model for paginated documents."""
    documents: List[DocumentInfo] = Field(default_factory=list)
    pagination: PaginationInfo = Field(..., description="Pagination information")


class DeleteDocByIdResponse(BaseModel):
    """Response model for document deletion by ID."""
    deleted: bool = Field(..., description="Whether deletion was successful")
    document_id: str = Field(..., description="ID of the deleted document")
    message: Optional[str] = None


class ClearDocumentsResponse(BaseModel):
    """Response model for clearing all documents."""
    cleared: bool = Field(..., description="Whether clearing was successful")
    count: int = Field(..., description="Number of documents cleared")
    message: Optional[str] = None


class PipelineStatusResponse(BaseModel):
    """Response model for pipeline status."""
    status: PipelineStatus = Field(..., description="Pipeline status")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    current_task: Optional[str] = None
    message: Optional[str] = None


class TrackStatusResponse(BaseModel):
    """Response model for track status."""
    track_id: str = Field(..., description="Track ID")
    status: str = Field(..., description="Track status")
    progress: Optional[float] = Field(None, ge=0, le=100)
    message: Optional[str] = None


class StatusCountsResponse(BaseModel):
    """Response model for document status counts."""
    pending: int = Field(0, ge=0)
    processing: int = Field(0, ge=0)
    processed: int = Field(0, ge=0)
    failed: int = Field(0, ge=0)
    total: int = Field(0, ge=0)


class ClearCacheResponse(BaseModel):
    """Response model for cache clearing."""
    cleared: bool = Field(..., description="Whether cache was cleared")
    cache_type: Optional[str] = None
    message: Optional[str] = None


class DeletionResult(BaseModel):
    """Response model for entity/relation deletion."""
    deleted: bool = Field(..., description="Whether deletion was successful")
    id: str = Field(..., description="ID of the deleted item")
    type: str = Field(..., description="Type of deleted item (entity/relation)")
    message: Optional[str] = None


# Query Response Models
class QueryResult(BaseModel):
    """Query result model."""
    document_id: str = Field(..., description="Document ID")
    snippet: str = Field(..., description="Text snippet")
    score: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response model for text queries."""
    query: str = Field(..., description="Original query")
    results: List[QueryResult] = Field(default_factory=list)
    total_results: Optional[int] = None
    processing_time: Optional[float] = None
    context: Optional[str] = None


# Knowledge Graph Response Models
class EntityInfo(BaseModel):
    """Entity information model."""
    id: str = Field(..., description="Entity ID")
    name: str = Field(..., description="Entity name")
    type: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RelationInfo(BaseModel):
    """Relation information model."""
    id: str = Field(..., description="Relation ID")
    source_entity: str = Field(..., description="Source entity ID")
    target_entity: str = Field(..., description="Target entity ID")
    type: str = Field(..., description="Relation type")
    properties: Dict[str, Any] = Field(default_factory=dict)
    weight: Optional[float] = Field(None, ge=0, le=1)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GraphResponse(BaseModel):
    """Response model for knowledge graph."""
    entities: List[EntityInfo] = Field(default_factory=list)
    relations: List[RelationInfo] = Field(default_factory=list)
    total_entities: Optional[int] = None
    total_relations: Optional[int] = None


class LabelsResponse(BaseModel):
    """Response model for graph labels."""
    entity_labels: List[str] = Field(default_factory=list)
    relation_labels: List[str] = Field(default_factory=list)


class EntityExistsResponse(BaseModel):
    """Response model for entity existence check."""
    exists: bool = Field(..., description="Whether entity exists")
    entity_name: str = Field(..., description="Entity name")
    entity_id: Optional[str] = None


class EntityUpdateResponse(BaseModel):
    """Response model for entity update."""
    updated: bool = Field(..., description="Whether update was successful")
    entity_id: str = Field(..., description="Entity ID")
    message: Optional[str] = None


class RelationUpdateResponse(BaseModel):
    """Response model for relation update."""
    updated: bool = Field(..., description="Whether update was successful")
    relation_id: str = Field(..., description="Relation ID")
    message: Optional[str] = None


# System Management Response Models
class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status")
    version: Optional[str] = None
    uptime: Optional[float] = None
    database_status: Optional[str] = None
    cache_status: Optional[str] = None
    message: Optional[str] = None


# Authentication Response Models
class AuthStatusResponse(BaseModel):
    """Response model for authentication status."""
    authenticated: bool = Field(..., description="Whether user is authenticated")
    user: Optional[str] = None


class LoginResponse(BaseModel):
    """Response model for login."""
    success: bool = Field(..., description="Whether login was successful")
    token: Optional[str] = None
    user: Optional[str] = None
    message: Optional[str] = None


# Ollama API Models (for completeness)
class OllamaVersionResponse(BaseModel):
    """Response model for Ollama version."""
    version: str = Field(..., description="Ollama version")


class OllamaTagsResponse(BaseModel):
    """Response model for Ollama tags."""
    models: List[Dict[str, Any]] = Field(default_factory=list)


class OllamaProcessResponse(BaseModel):
    """Response model for Ollama running processes."""
    models: List[Dict[str, Any]] = Field(default_factory=list)


class OllamaGenerateRequest(BaseModel):
    """Request model for Ollama generate."""
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="Prompt text")
    stream: bool = Field(False, description="Whether to stream response")


class OllamaChatMessage(BaseModel):
    """Chat message model for Ollama."""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")


class OllamaChatRequest(BaseModel):
    """Request model for Ollama chat."""
    model: str = Field(..., description="Model name")
    messages: List[OllamaChatMessage] = Field(..., description="Chat messages")
    stream: bool = Field(False, description="Whether to stream response")


# File upload models
class Body_upload_to_input_dir_documents_upload_post(BaseModel):
    """Request body for file upload."""
    file: bytes = Field(..., description="File content")


class Body_login_login_post(BaseModel):
    """Request body for login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


# Status response models
class DocStatusResponse(BaseModel):
    """Response model for document status."""
    document_id: str = Field(..., description="Document ID")
    status: DocStatus = Field(..., description="Document status")
    message: Optional[str] = None


class DocsStatusesResponse(BaseModel):
    """Response model for multiple document statuses."""
    statuses: List[DocStatusResponse] = Field(default_factory=list)
    total: int = Field(0, ge=0)