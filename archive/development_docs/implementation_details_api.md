## **LightRAG Server API**

**OAS 3.1** – `/openapi.json`
Provides API for:

* **LightRAG Core**
* **Web UI**
* **Ollama Model Emulation** (with authentication)

---

## **Authentication**

| Method | Endpoint       | Description               |
| ------ | -------------- | ------------------------- |
| `GET`  | `/auth-status` | Get authentication status |
| `POST` | `/login`       | Login                     |

---

## **Documents**

| Method   | Endpoint                             | Description                                     |
| -------- | ------------------------------------ | ----------------------------------------------- |
| `POST`   | `/documents/scan`                    | Scan for new documents                          |
| `POST`   | `/documents/upload`                  | Upload to input directory                       |
| `POST`   | `/documents/text`                    | Insert a single text                            |
| `POST`   | `/documents/texts`                   | Insert multiple texts                           |
| `GET`    | `/documents`                         | Retrieve documents                              |
| `DELETE` | `/documents`                         | Clear all documents                             |
| `GET`    | `/documents/pipeline_status`         | Get pipeline status                             |
| `DELETE` | `/documents/delete_document`         | Delete a document and all associated data by ID |
| `POST`   | `/documents/clear_cache`             | Clear cache                                     |
| `DELETE` | `/documents/delete_entity`           | Delete an entity                                |
| `DELETE` | `/documents/delete_relation`         | Delete a relation                               |
| `GET`    | `/documents/track_status/{track_id}` | Get track status                                |
| `POST`   | `/documents/paginated`               | Get documents (paginated)                       |
| `GET`    | `/documents/status_counts`           | Get document status counts                      |

---

## **Query**

| Method | Endpoint        | Description       |
| ------ | --------------- | ----------------- |
| `POST` | `/query`        | Query text        |
| `POST` | `/query/stream` | Query text stream |

---

## **Graph**

| Method | Endpoint               | Description              |
| ------ | ---------------------- | ------------------------ |
| `GET`  | `/graph/label/list`    | Get graph labels         |
| `GET`  | `/graphs`              | Retrieve knowledge graph |
| `GET`  | `/graph/entity/exists` | Check if entity exists   |
| `POST` | `/graph/entity/edit`   | Update entity            |
| `POST` | `/graph/relation/edit` | Update relation          |

---

## **Ollama API**

| Method | Endpoint        | Description         |
| ------ | --------------- | ------------------- |
| `GET`  | `/api/version`  | Get Ollama version  |
| `GET`  | `/api/tags`     | Get tags            |
| `GET`  | `/api/ps`       | List running models |
| `POST` | `/api/generate` | Generate output     |
| `POST` | `/api/chat`     | Chat with model     |

---

## **Default / Utility**

| Method | Endpoint  | Description        |
| ------ | --------- | ------------------ |
| `GET`  | `/`       | Redirect to Web UI |
| `GET`  | `/health` | Get health/status  |

---

## **Schemas**

**Request/Response Objects**

* `Body_login_login_post` – object
* `Body_upload_to_input_dir_documents_upload_post` – object
* `ClearCacheRequest` – object
* `ClearCacheResponse` – object
* `ClearDocumentsResponse` – object
* `DeleteDocByIdResponse` – object
* `DeleteDocRequest` – object
* `DeleteEntityRequest` – object
* `DeleteRelationRequest` – object
* `DeletionResult` – object
* `DocStatus` – string
* `DocStatusResponse` – object
* `DocsStatusesResponse` – object
* `DocumentsRequest` – object
* `EntityUpdateRequest` – object
* `HTTPValidationError` – object
* `InsertResponse` – object
* `InsertTextRequest` – object
* `InsertTextsRequest` – object
* `PaginatedDocsResponse` – object
* `PaginationInfo` – object
* `PipelineStatusResponse` – object
* `QueryRequest` – object
* `QueryResponse` – object
* `RelationUpdateRequest` – object
* `ScanResponse` – object
* `StatusCountsResponse` – object
* `TrackStatusResponse` – object
* `ValidationError` – object

---

# **LightRAG Server API Reference**

**OpenAPI 3.1** – `/openapi.json`
Provides API for:

* **LightRAG Core**
* **Web UI**
* **Ollama Model Emulation** (with authentication)

---

## **1. Authentication**

### **GET** `/auth-status`

Check authentication status.

**Response Example:**

```json
{
  "authenticated": true,
  "user": "admin"
}
```

---

### **POST** `/login`

Login to obtain a session/token.

**Request Example:**

```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response Example:**

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## **2. Documents**

### **POST** `/documents/scan`

Scan for new documents in the input directory.

**Response Example:**

```json
{
  "scanned": 12,
  "new_documents": ["doc1.pdf", "doc2.txt"]
}
```

---

### **POST** `/documents/upload`

Upload a file to the input directory.

**Request:** Multipart/form-data

```http
POST /documents/upload
Content-Type: multipart/form-data
file=@example.pdf
```

---

### **POST** `/documents/text`

Insert a single text document.

**Request Example:**

```json
{
  "title": "Example",
  "content": "This is a test document."
}
```

**Response Example:**

```json
{
  "id": "doc_123",
  "status": "inserted"
}
```

---

### **POST** `/documents/texts`

Insert multiple text documents.

**Request Example:**

```json
[
  { "title": "Doc 1", "content": "Text for doc 1" },
  { "title": "Doc 2", "content": "Text for doc 2" }
]
```

---

### **GET** `/documents`

Retrieve all documents.

**Response Example:**

```json
[
  { "id": "doc_123", "title": "Example", "status": "processed" }
]
```

---

### **DELETE** `/documents`

Clear all documents from the system.

---

### **GET** `/documents/pipeline_status`

Get the current pipeline processing status.

**Response Example:**

```json
{
  "status": "running",
  "progress": 65
}
```

---

### **DELETE** `/documents/delete_document`

Delete a document and all associated data by its ID.

**Request Example:**

```json
{ "document_id": "doc_123" }
```

---

### **POST** `/documents/clear_cache`

Clear cached document data.

---

### **DELETE** `/documents/delete_entity`

Delete an entity from the knowledge base.

**Request Example:**

```json
{ "entity_id": "entity_456" }
```

---

### **DELETE** `/documents/delete_relation`

Delete a relation between entities.

**Request Example:**

```json
{ "relation_id": "rel_789" }
```

---

### **GET** `/documents/track_status/{track_id}`

Get status of a document tracking process.

---

### **POST** `/documents/paginated`

Retrieve paginated document lists.

**Request Example:**

```json
{ "page": 1, "page_size": 10 }
```

---

### **GET** `/documents/status_counts`

Get counts of documents by status.

**Response Example:**

```json
{
  "processed": 25,
  "pending": 5
}
```

---

## **3. Query**

### **POST** `/query`

Perform a text query.

**Request Example:**

```json
{ "query": "What is LightRAG?" }
```

**Response Example:**

```json
{
  "results": [
    { "document_id": "doc_1", "snippet": "LightRAG is..." }
  ]
}
```

---

### **POST** `/query/stream`

Stream query results as they are found.

---

## **4. Graph**

### **GET** `/graph/label/list`

List available graph labels.

---

### **GET** `/graphs`

Retrieve the full knowledge graph.

---

### **GET** `/graph/entity/exists`

Check if a specific entity exists.

---

### **POST** `/graph/entity/edit`

Update an entity's data.

**Request Example:**

```json
{
  "entity_id": "entity_456",
  "properties": { "name": "Updated Name" }
}
```

---

### **POST** `/graph/relation/edit`

Update a relation between entities.

**Request Example:**

```json
{
  "relation_id": "rel_789",
  "properties": { "weight": 0.9 }
}
```

---

## **5. Ollama API**

### **GET** `/api/version`

Get Ollama version.

### **GET** `/api/tags`

Get available tags.

### **GET** `/api/ps`

List running models.

### **POST** `/api/generate`

Generate text output.

**Request Example:**

```json
{
  "model": "llama2",
  "prompt": "Write a short story about AI."
}
```

---

### **POST** `/api/chat`

Chat with the model.

**Request Example:**

```json
{
  "model": "llama2",
  "messages": [
    { "role": "user", "content": "Hello!" }
  ]
}
```

---

## **6. Default / Utility**

### **GET** `/`

Redirect to Web UI.

### **GET** `/health`

Get API health status.

---

## **7. Schemas**

> The API defines multiple request/response objects including:

* `LoginRequest`, `ClearCacheRequest`, `InsertTextRequest`, `InsertTextsRequest`, `PaginatedDocsResponse`, `QueryRequest`, `EntityUpdateRequest`, `RelationUpdateRequest`, etc.
* All follow standard JSON structures as shown in the examples above.
