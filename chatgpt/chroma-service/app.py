import os
from typing import Optional, Dict, Any, List

import chromadb
from chromadb.config import Settings
from fastapi import FastAPI
from pydantic import BaseModel

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "/data/chroma")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "documents")

client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=CHROMA_DB_DIR,
    )
)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

app = FastAPI(title="Chroma Embeddings Service")


class EmbedRequest(BaseModel):
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    query: str
    n_results: int = 3


@app.post("/embed")
def embed(req: EmbedRequest):
    ids = [req.id]
    documents = [req.text]
    metadatas = [req.metadata or {}]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return {"status": "ok", "id": req.id}


@app.post("/query")
def query(req: QueryRequest):
    result = collection.query(
        query_texts=[req.query],
        n_results=req.n_results,
    )
    return {"results": result}
