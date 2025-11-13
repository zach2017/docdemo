# 📘 Document Processing & Chroma RAG Pipeline

This project is a **multi-service document pipeline** that:

1. Accepts file uploads via a simple **web app**
2. Uses a **Python Unstructured service** to convert documents to clean text and store them in **LocalStack S3**
3. Uses a **Java worker** to watch S3 for new text documents
4. Pushes text into a dedicated **Chroma Embeddings service** which builds a **ChromaDB vector store** for RAG

It is designed as an educational, end-to-end example of:

- Microservices & Docker Compose
- Document ingestion pipelines
- Vector databases & embeddings
- Retrieval-Augmented Generation (RAG) architecture

---

## 🧱 Services

- `web` – Node.js upload UI
- `unstructured` – Python FastAPI + Unstructured.io for text extraction and S3 storage
- `localstack` – Local AWS S3 simulator
- `java-worker` – Spring Boot worker that polls S3 and sends documents to Chroma
- `chroma-service` – Python FastAPI service using ChromaDB for embeddings & queries

For detailed documentation, see the **docs/wiki**:

- [docs/overview.md](docs/overview.md)
- [docs/services.md](docs/services.md)
- [docs/data-flow.md](docs/data-flow.md)
- [docs/rag-concepts.md](docs/rag-concepts.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)

---

## ▶️ Quick Start

```bash
docker-compose up --build
```

Then:

- Web UI: http://localhost:8080
- Chroma query API: `POST http://localhost:9000/query` with `{ "query": "...", "n_results": 3 }`

For full instructions and diagrams, open `docs/overview.md`.
