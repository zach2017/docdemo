# 🔧 Services Deep Dive

This document describes each service, why it's here, and what a new learner should notice.

---

## 🌐 `web` – Upload UI (Node.js)

**Purpose**

- Provide a minimal web interface to upload documents.

**Key Files**

- `web/Dockerfile`
- `web/server.js`
- `web/package.json`

**How It Works**

- Renders a basic HTML form at `/`.
- When you submit, it:
  - Uses `multer` to parse the file
  - Sends the raw bytes to `unstructured` service via HTTP:
    - `POST http://unstructured:8000/upload`
    - Adds headers: `Content-Type`, `X-Filename`

**Key Concepts for New Learners**

- HTTP file upload form
- Backend-for-frontend pattern
- Environment variables (`API_URL`) in Docker

---

## 🐍 `unstructured` – Document Text Extraction (Python)

**Purpose**

- Convert user-uploaded documents into **structured text** using the `unstructured` library.
- Store both the original and text versions into S3 (LocalStack).

**Key Files**

- `unstructured/Dockerfile`
- `unstructured/app.py`
- `unstructured/requirements.txt`

**How It Works**

1. Receives raw bytes and `X-Filename` header.
2. Writes bytes to a temporary file.
3. Calls `unstructured.partition.auto.partition(filename=tmp_path)` to parse the document.
4. Joins all `element.text` into one big text string.
5. Creates an S3 key prefix: `uploads/<timestamp>_<uuid>/`.
6. Writes:
   - `original.ext` – the original file
   - `original.ext.txt` – the extracted text

**Key Concepts**

- FastAPI endpoints
- Using `unstructured` to normalize many file types (PDF, DOCX, etc.)
- S3 buckets, keys, and object storage patterns

---

## 🗄️ `localstack` – Local AWS S3 Emulator

**Purpose**

- Provide a local-only AWS-like environment so you can test S3-based pipelines without a real AWS account.

**How It Works**

- Docker image `localstack/localstack`.
- Exposes the **edge endpoint** at `http://localhost:4566`.
- `unstructured` and `java-worker` talk to S3 via `http://localstack:4566` on the Docker network.

**Key Concepts**

- What S3 is: object storage for blobs (files, text, etc.)
- Why we emulate AWS locally for learning and development
- Using environment variables to configure endpoints & regions

---

## ☕ `java-worker` – S3 Listener & Ingestion Orchestrator

**Purpose**

- Poll S3 `documents` bucket for new `.txt` documents.
- Download the text and push it into the Chroma embeddings service.

**Key Files**

- `java-worker/pom.xml`
- `java-worker/src/main/java/com/example/javaworker/JavaWorkerApplication.java`
- `java-worker/src/main/java/com/example/javaworker/S3Listener.java`

**How It Works**

- Uses Spring Boot's `@EnableScheduling` and `@Scheduled` to run a job every 10 seconds:
  1. Call `listObjectsV2` on S3 with prefix `uploads/`.
  2. For each `.txt` object not yet processed:
     - Download with `getObjectAsBytes`.
     - Convert bytes into a UTF-8 string.
     - Build a JSON payload `{ id, text, metadata }`.
     - POST to `http://chroma-service:9000/embed`.

**Why Java Here?**

- Demonstrates using **Java + AWS SDK v2** to work with S3.
- Shows scheduling and background processing with **Spring Boot**.
- Illustrates polyglot microservices (Java talks to Python services).

**Key Concepts**

- Spring Boot application & scheduling
- AWS SDK S3 client (endpoint override for LocalStack)
- `HttpClient` (Java 11+) for calling other services
- Idempotent processing (track processed keys with `Set<String>`)

---

## 🧠 `chroma-service` – ChromaDB Embeddings & Query (Python)

**Purpose**

- Provide a simple HTTP layer over ChromaDB:
  - `/embed` – insert documents and let Chroma create embeddings
  - `/query` – run semantic search over the stored documents

**Key Files**

- `chroma-service/Dockerfile`
- `chroma-service/app.py`
- `chroma-service/requirements.txt`

**How It Works**

- Configures ChromaDB with:
  - `chroma_db_impl="duckdb+parquet"`
  - `persist_directory="/data/chroma"`
- Creates or loads a collection named `documents`.
- `/embed`:
  - Accepts `{ id, text, metadata }`.
  - Calls `collection.add(ids=[...], documents=[...], metadatas=[...])`.
- `/query`:
  - Accepts `{ query, n_results }`.
  - Calls `collection.query(query_texts=[query], n_results=n_results)`.

**Key Concepts**

- What a **vector store** is.
- How ChromaDB stores text + embeddings.
- Why we use a separate service just for embeddings/queries.
- Persisted DB on disk (`/data/chroma` volume) so your data isn't lost when containers restart.

---

Next: see [data-flow.md](data-flow.md) for request/response flows and RAG path.
