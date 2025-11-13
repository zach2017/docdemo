# 📘 Project Overview

This project shows a complete **document-to-embeddings** pipeline for **Retrieval-Augmented Generation (RAG)**:

- Upload documents via a web page
- Extract clean text from documents
- Store original and text versions in S3 (LocalStack)
- Build a **ChromaDB** vector store for semantic search

---

## 🔭 High-Level Architecture

```mermaid
flowchart LR
    U[User] -->|Upload file| W[Web App (Node.js)]
    W -->|POST file bytes| P[Unstructured Service (Python)]
    P -->|Store original + text| S[(LocalStack S3)]
    S -->|Poll for new .txt| J[Java Worker (Spring Boot)]
    J -->|POST id + text| C[Chroma Service (Python + ChromaDB)]
    C -->|Embeddings + vectors| V[(ChromaDB Vector Store)]
```

---

## 🧩 Service Roles

- **Web (Node.js)**  
  Simple upload UI that forwards files to the Unstructured API.

- **Unstructured (Python FastAPI + Unstructured.io)**  
  Converts raw documents into text and stores:
  - Original document
  - Extracted text
  in a LocalStack S3 bucket.

- **LocalStack (S3)**  
  Local, no-cost AWS S3 emulator used as the storage and event source.

- **Java Worker (Spring Boot)**  
  Polls S3 for new `.txt` files, downloads their text, and calls the Chroma service to store embeddings.

- **Chroma Service (Python + ChromaDB)**  
  Provides `/embed` and `/query` APIs:
  - `/embed` – add a document to the Chroma collection (with embeddings)
  - `/query` – query for similar documents (vector search)

---

## 🧠 Core Learning Themes

- **Microservices**: each component has one job and is independently replaceable.
- **Object Storage as Event Source**: S3 acts as the communication & persistence layer.
- **Vector Databases**: ChromaDB stores embeddings and enables semantic search.
- **RAG Pattern**: documents are embedded and later used for context-aware AI responses.

Next: see [services.md](services.md) for a deep dive into each service.
