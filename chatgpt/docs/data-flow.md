# 🔄 Data Flow & RAG Pipeline

This doc walks through **how data moves** through the system.

---

## 1️⃣ Upload & Extraction

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web (Node.js)
    participant P as Unstructured (FastAPI)
    participant S as LocalStack S3

    U->>W: Upload file via HTML form
    W->>P: POST /upload (bytes + X-Filename)
    P->>P: Save temp file + run unstructured.partition
    P->>S: PutObject original file
    P->>S: PutObject text file (.txt)
    P-->>W: { status: "ok", key, text_key }
    W-->>U: Show success message
```

**Important Ideas**

- The web app never touches S3 directly.
- The Unstructured service is the **single source of truth** for document ingestion.

---

## 2️⃣ S3 Polling & Embedding

```mermaid
sequenceDiagram
    participant S as LocalStack S3
    participant J as Java Worker
    participant C as Chroma Service
    participant V as ChromaDB

    loop Every 10 seconds
        J->>S: listObjectsV2 (prefix=uploads/)
        S-->>J: list of objects
        J->>S: getObject (.txt file)
        S-->>J: text content
        J->>C: POST /embed {id, text, metadata}
        C->>V: collection.add(...)
        V-->>C: store embeddings + vectors
        C-->>J: { status: "ok" }
    end
```

**Important Ideas**

- The worker is **pull-based**, not push-based.
- Chroma is used as a **vector store**; it handles embeddings and similarity search.

---

## 3️⃣ Query Path (RAG Read Side)

```mermaid
sequenceDiagram
    participant Client as RAG Client (future)
    participant C as Chroma Service
    participant V as ChromaDB

    Client->>C: POST /query { query, n_results }
    C->>V: collection.query(query_texts=[query])
    V-->>C: nearest documents + metadata
    C-->>Client: results
```

In a full RAG application, the **Client** is often:

- A backend service that also calls an LLM (e.g., GPT, Claude, Llama)
- A chatbot that:
  1. Queries Chroma for relevant docs
  2. Feeds them into the LLM prompt as context
  3. Returns a grounded answer to the user

---

## 🧠 RAG Conceptual Diagram

```mermaid
flowchart TD
    subgraph Ingestion
        A[Raw Documents] --> B[Unstructured Service]
        B --> C[Text in S3]
        C --> D[Java Worker]
        D --> E[ChromaDB Collection]
    end

    subgraph Retrieval
        Q[User Question] --> R[Chroma Query]
        R -->|Top-k documents| K[LLM Prompt with Context]
        K --> A1[Final Answer]
    end
```

Key teaching points for a new learner:

- **Ingestion path** (write side) prepares data.
- **Retrieval path** (read side) pulls relevant context at query time.
- RAG is all about **combining your data + an LLM**.
