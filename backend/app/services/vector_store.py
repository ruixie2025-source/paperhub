from __future__ import annotations

import chromadb

from app.core.paths import CHROMA_DIR
from app.models.paper import Paper
from app.services.chunker import chunk_text
from app.services.embedding import embed_text


COLLECTION_NAME = "papers"

_client: chromadb.PersistentClient | None = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client

    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    return _client


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_paper(paper: Paper) -> int:
    if not paper.content:
        return 0

    chunks = chunk_text(paper.content)
    if not chunks:
        return 0

    ids = [f"paper_{paper.id}_{chunk_index}" for chunk_index in range(len(chunks))]
    embeddings = [embed_text(chunk) for chunk in chunks]
    metadatas = [
        {
            "paper_id": paper.id,
            "chunk_index": chunk_index,
            "title": paper.title,
        }
        for chunk_index in range(len(chunks))
    ]

    collection = get_collection()
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)


def delete_paper_index(paper_id: int) -> None:
    collection = get_collection()
    existing = collection.get(where={"paper_id": paper_id})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])


def reindex_paper(paper: Paper) -> int:
    delete_paper_index(paper.id)
    return index_paper(paper)
