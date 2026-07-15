from __future__ import annotations

from typing import Any

from app.services.embedding import embed_text
from app.services.vector_store import get_collection


def search_chunks(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    if not query.strip():
        return []

    collection = get_collection()
    if collection.count() == 0:
        return []

    embedding = embed_text(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks: list[dict[str, Any]] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        chunks.append(
            {
                "text": document,
                "paper_id": metadata["paper_id"],
                "title": metadata["title"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance,
            }
        )

    return chunks
