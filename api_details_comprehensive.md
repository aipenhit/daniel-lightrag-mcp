LightRAG Server API 0.1.96
OAS 3.1
/openapi.json

Providing API for LightRAG core, Web UI and Ollama Model Emulation (With authentication).

Documents
POST /documents/scan
Scan For New Documents

Triggers the scanning process for new documents. This endpoint initiates a background task that scans the input directory for new documents and processes them. If a scanning process is already running, it returns a status indicating that fact.

Returns: ScanResponse - A response object containing the scanning status and track_id.

Parameters: None

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "message": "Scanning process has been initiated in the background",
  "status": "scanning_started",
  "track_id": "scan_20250729_170612_abc123"
}

POST /documents/upload
Upload To Input Dir

Uploads a file to the input directory and indexes it. This API accepts a file, checks if it's a supported type, saves it, indexes it, and returns a success status.

Args:

background_tasks: FastAPI BackgroundTasks for async processing.

file (UploadFile): The file to be uploaded.

Returns: InsertResponse - A response object containing the upload status.

Raises: HTTPException - If the file type is not supported (400) or other errors occur (500).

Request Body: multipart/form-data

file: string($binary)

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "message": "File 'document.pdf' uploaded successfully. Processing will continue in background.",
  "status": "success",
  "track_id": "upload_20250729_170612_abc123"
}

422 - Validation Error

Media Type: application/json

POST /documents/text
Insert Text

Inserts text data into the RAG system.

Args:

request (InsertTextRequest): The request body containing the text.

background_tasks: FastAPI BackgroundTasks for async processing.

Returns: InsertResponse - A response object with the operation status.

Raises: HTTPException - If an error occurs (500).

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "message": "File 'document.pdf' uploaded successfully. Processing will continue in background.",
  "status": "success",
  "track_id": "upload_20250729_170612_abc123"
}

422 - Validation Error

Media Type: application/json

POST /documents/texts
Insert Texts

Inserts multiple text entries into the RAG system in a single request.

Args:

request (InsertTextsRequest): Request body with a list of texts.

background_tasks: FastAPI BackgroundTasks for async processing.

Returns: InsertResponse - A response object with the operation status.

Raises: HTTPException - If an error occurs (500).

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "message": "File 'document.pdf' uploaded successfully. Processing will continue in background.",
  "status": "success",
  "track_id": "upload_20250729_170612_abc123"
}

422 - Validation Error

Media Type: application/json

GET /documents
Documents

Retrieves the status of all documents, grouped by processing status (PENDING, PROCESSING, PROCESSED, FAILED).

Returns: DocsStatusesResponse - A response object with document statuses.

Raises: HTTPException - If an error occurs (500).

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "statuses": {
    "PENDING": [
      {
        "content_length": 5000,
        "content_summary": "Pending document",
        "created_at": "2025-03-31T10:00:00",
        "file_path": "pending_doc.pdf",
        "id": "doc_123",
        "status": "PENDING",
        "track_id": "upload_20250331_100000_abc123",
        "updated_at": "2025-03-31T10:00:00"
      }
    ],
    "PROCESSED": [
      {
        "chunks_count": 8,
        "content_length": 8000,
        "content_summary": "Processed document",
        "created_at": "2025-03-31T09:00:00",
        "file_path": "processed_doc.pdf",
        "id": "doc_456",
        "metadata": { "author": "John Doe" },
        "status": "PROCESSED",
        "track_id": "insert_20250331_090000_def456",
        "updated_at": "2025-03-31T09:05:00"
      }
    ]
  }
}

DELETE /documents
Clear Documents

Deletes all documents, entities, relationships, and files from the system.

Returns: ClearDocumentsResponse - A response object with status and message.

Raises: HTTPException - On serious errors (500).

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "message": "All documents cleared successfully. Deleted 15 files.",
  "status": "success"
}

GET /documents/pipeline_status
Get Pipeline Status

Retrieves the current state of the document processing pipeline.

Returns: PipelineStatusResponse - A response object with pipeline details.

Raises: HTTPException - If an error occurs (500).

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "autoscanned": false,
  "busy": false,
  "job_name": "Default Job",
  "job_start": "string",
  "docs": 0,
  "batchs": 0,
  "cur_batch": 0,
  "request_pending": false,
  "latest_message": "",
  "history_messages": ["string"],
  "update_status": { "additionalProp1": {} },
  "additionalProp1": {}
}

DELETE /documents/delete_document
Delete a document and all its associated data by its ID.

Deletes specific documents and their data in the background.

Args:

delete_request (DeleteDocRequest): Request with document IDs.

background_tasks: FastAPI BackgroundTasks for async processing.

Returns: DeleteDocByIdResponse - The result of the deletion operation.

Raises: HTTPException - On unexpected errors (500).

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "status": "deletion_started",
  "message": "string",
  "doc_id": "string"
}

422 - Validation Error

Media Type: application/json

POST /documents/clear_cache
Clear Cache

Clears cache data from the LLM response cache storage.

Args: request (ClearCacheRequest): Request body with optional modes to clear.

Returns: ClearCacheResponse - A response object with status and message.

Raises: HTTPException - For invalid modes (400) or other errors (500).

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "message": "Successfully cleared cache for modes: ['default', 'naive']",
  "status": "success"
}

422 - Validation Error

Media Type: application/json

DELETE /documents/delete_entity
Delete Entity

Deletes an entity and its relationships from the knowledge graph.

Args: request (DeleteEntityRequest): Request body with the entity name.

Returns: DeletionResult - An object with the deletion outcome.

Raises: HTTPException - If entity not found (404) or on error (500).

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "status": "success",
  "doc_id": "string",
  "message": "string",
  "status_code": 200,
  "file_path": "string"
}

422 - Validation Error

Media Type: application/json

DELETE /documents/delete_relation
Delete Relation

Deletes a relationship between two entities.

Args: request (DeleteRelationRequest): Request body with source and target entities.

Returns: DeletionResult - An object with the deletion outcome.

Raises: HTTPException - If relation not found (404) or on error (500).

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "status": "success",
  "doc_id": "string",
  "message": "string",
  "status_code": 200,
  "file_path": "string"
}

422 - Validation Error

Media Type: application/json

GET /documents/track_status/{track_id}
Get Track Status

Retrieves document processing status by a tracking ID.

Args: track_id (str): The tracking ID.

Returns: TrackStatusResponse - A response object with tracking details.

Raises: HTTPException - If track_id is invalid (400) or on error (500).

Parameters

track_id (path, string, required): The tracking ID.

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "documents": [
    {
      "chunks_count": 12,
      "content_length": 15240,
      "content_summary": "Research paper on machine learning",
      "created_at": "2025-03-31T12:34:56",
      "file_path": "research_paper.pdf",
      "id": "doc_123456",
      "metadata": { "author": "John Doe", "year": 2025 },
      "status": "PROCESSED",
      "track_id": "upload_20250729_170612_abc123",
      "updated_at": "2025-03-31T12:35:30"
    }
  ],
  "status_summary": { "PROCESSED": 1 },
  "total_count": 1,
  "track_id": "upload_20250729_170612_abc123"
}

422 - Validation Error

Media Type: application/json

POST /documents/paginated
Get Documents Paginated

Retrieves documents with pagination, filtering, and sorting.

Args: request (DocumentsRequest): Request body with pagination parameters.

Returns: PaginatedDocsResponse - A response object with paginated documents.

Raises: HTTPException - If an error occurs (500).

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "documents": [
    {
      "chunks_count": 12,
      "content_length": 15240,
      "content_summary": "Research paper on machine learning",
      "created_at": "2025-03-31T12:34:56",
      "file_path": "research_paper.pdf",
      "id": "doc_123456",
      "metadata": { "author": "John Doe", "year": 2025 },
      "status": "PROCESSED",
      "track_id": "upload_20250729_170612_abc123",
      "updated_at": "2025-03-31T12:35:30"
    }
  ],
  "pagination": {
    "has_next": true,
    "has_prev": false,
    "page": 1,
    "page_size": 50,
    "total_count": 150,
    "total_pages": 3
  },
  "status_counts": {
    "FAILED": 5,
    "PENDING": 10,
    "PROCESSED": 130,
    "PROCESSING": 5
  }
}

422 - Validation Error

Media Type: application/json

GET /documents/status_counts
Get Document Status Counts

Retrieves the count of documents for each processing status.

Returns: StatusCountsResponse - A response object with status counts.

Raises: HTTPException - If an error occurs (500).

Responses

200 - Successful Response

Media Type: application/json

Example Value:

{
  "status_counts": {
    "FAILED": 5,
    "PENDING": 10,
    "PROCESSED": 130,
    "PROCESSING": 5
  }
}

Query
POST /query
Query Text

Handles a POST request to process user queries using RAG capabilities.

Parameters: request (QueryRequest)

Returns: QueryResponse

Raises: HTTPException (500)

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value: {"response": "string"}

422 - Validation Error

Media Type: application/json

POST /query/stream
Query Text Stream

Performs a RAG query and streams the response.

Args: request (QueryRequest)

Returns: StreamingResponse

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

422 - Validation Error

Media Type: application/json

Graph
GET /graph/label/list
Get Graph Labels

Gets all graph labels.

Returns: List[str]

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

GET /graphs
Get Knowledge Graph

Retrieves a connected subgraph of nodes.

Args:

label (str)

max_depth (int, optional)

max_nodes (int, optional)

Returns: Dict[str, List[str]]

Parameters

label (query, string, required)

max_depth (query, integer)

max_nodes (query, integer)

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

422 - Validation Error

Media Type: application/json

GET /graph/entity/exists
Check Entity Exists

Checks if an entity exists in the knowledge graph.

Args: name (str)

Returns: Dict[str, bool]

Parameters

name (query, string, required)

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

422 - Validation Error

Media Type: application/json

POST /graph/entity/edit
Update Entity

Updates an entity's properties.

Args: request (EntityUpdateRequest)

Returns: Dict

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

422 - Validation Error

Media Type: application/json

POST /graph/relation/edit
Update Relation

Updates a relation's properties.

Args: request (RelationUpdateRequest)

Returns: Dict

Request Body: application/json

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

422 - Validation Error

Media Type: application/json

Ollama
GET /api/version
Get Version

Gets Ollama version information.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

GET /api/tags
Get Tags

Returns available models.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

GET /api/ps
Get Running Models

Lists currently running models.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

POST /api/generate
Generate

Handles generate completion requests.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

POST /api/chat
Chat

Processes chat completion requests.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

Default
GET /
Redirect To Webui

Redirects the root path to /webui.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

GET /auth-status
Get Auth Status

Gets authentication status.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

POST /login
Login

Request Body: application/x-www-form-urlencoded

grant_type: string (pattern: ^password$)

username: string (required)

password: string($password) (required)

scope: string

client_id: string

client_secret: string($password)

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

422 - Validation Error

Media Type: application/json

GET /health
Get Status

Gets current system status.

Responses

200 - Successful Response

Media Type: application/json

Example Value: "string"

Schemas
Body_login_login_post
grant_type: string | null (pattern: ^password$)

username: string

password: string (password)

scope: string (Default: "")

client_id: string | null

client_secret: string | null (password)

Body_upload_to_input_dir_documents_upload_post
file: string (binary)

ClearCacheRequest
modes: array[string] | null (Enum: "default", "naive", "local", "global", "hybrid", "mix")

ClearCacheResponse
status: string (Enum: "success", "fail")

message: string

ClearDocumentsResponse
status: string (Enum: "success", "partial_success", "busy", "fail")

message: string

DeleteDocByIdResponse
status: string (Enum: "deletion_started", "busy", "not_allowed")

message: string

doc_id: string

DeleteDocRequest
doc_ids: array[string]

delete_file: boolean (Default: false)

DeleteEntityRequest
entity_name: string

DeleteRelationRequest
source_entity: string

target_entity: string

DeletionResult
status: string (Enum: "success", "not_found", "fail")

doc_id: string

message: string

status_code: integer (Default: 200)

file_path: string | null

DocStatus
string (Enum: "pending", "processing", "processed", "failed")

DocStatusResponse
id: string

content_summary: string

content_length: integer

status: string (Enum: "pending", "processing", "processed", "failed")

created_at: string (ISO format)

updated_at: string (ISO format)

track_id: string | null

chunks_count: integer | null

error_msg: string | null

metadata: object | null

file_path: string

DocsStatusesResponse
statuses: object (mapping DocStatus to lists of DocStatusResponse)

DocumentsRequest
status_filter: DocStatus | null

page: integer (>= 1, Default: 1)

page_size: integer ([10, 200], Default: 50)

sort_field: string (Enum: "created_at", "updated_at", "id", "file_path", Default: "updated_at")

sort_direction: string (Enum: "asc", "desc", Default: "desc")

EntityUpdateRequest
entity_name: string

updated_data: object

allow_rename: boolean (Default: false)

HTTPValidationError
detail: array[object]

loc: array[string | integer]

msg: string

type: string

InsertResponse
status: string (Enum: "success", "duplicated", "partial_success", "failure")

message: string

track_id: string

InsertTextRequest
text: string (>= 1 char)

file_source: string (>= 0 chars)

InsertTextsRequest
texts: array[string] (>= 1 item)

file_sources: array[string] (>= 0 items)

PaginatedDocsResponse
documents: array[DocStatusResponse]

pagination: PaginationInfo

status_counts: object (mapping status to integer)

PaginationInfo
page: integer

page_size: integer

total_count: integer

total_pages: integer

has_next: boolean

has_prev: boolean

PipelineStatusResponse
autoscanned: boolean (Default: false)

busy: boolean (Default: false)

job_name: string (Default: "Default Job")

job_start: string | null

docs: integer (Default: 0)

batchs: integer (Default: 0)

cur_batch: integer (Default: 0)

request_pending: boolean (Default: false)

latest_message: string (Default: "")

history_messages: array[string] | null

update_status: object | null

QueryRequest
query: string (>= 1 char)

mode: string (Enum: "local", "global", "hybrid", "naive", "mix", "bypass", Default: "mix")

only_need_context: boolean | null

only_need_prompt: boolean | null

response_type: string | null (>= 1 char)

top_k: integer | null (>= 1)

chunk_top_k: integer | null (>= 1)

max_entity_tokens: integer | null (>= 1)

max_relation_tokens: integer | null (>= 1)

max_total_tokens: integer | null (>= 1)

conversation_history: array[object] | null

history_turns: integer | null (>= 0)

ids: array[string] | null

user_prompt: string | null

enable_rerank: boolean | null

QueryResponse
response: string

RelationUpdateRequest
source_id: string

target_id: string

updated_data: object

ScanResponse
status: string (Const: "scanning_started")

message: string | null

track_id: string

StatusCountsResponse
status_counts: object (mapping status to integer)

TrackStatusResponse
track_id: string

documents: array[DocStatusResponse]

total_count: integer

status_summary: object (mapping status to integer)

ValidationError
loc: array[string | integer]

msg: string

type: string