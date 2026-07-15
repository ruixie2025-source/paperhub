import os
import sys
from time import perf_counter

from app.services.embedding import embed_text, get_embedding_model, get_model_load_seconds


def test_embed_text_with_single_chunk() -> None:
    chunk = (
        "PaperHub uses local PDF parsing, metadata extraction, text chunking, "
        "and vector embeddings to prepare for future retrieval workflows."
    )

    get_embedding_model()
    model_load_seconds = get_model_load_seconds()

    start = perf_counter()
    embedding = embed_text(chunk)
    embedding_seconds = perf_counter() - start

    print(f"model load seconds: {model_load_seconds:.3f}")
    print(f"single chunk embedding seconds: {embedding_seconds:.3f}")
    print(f"embedding dimension: {len(embedding)}")
    print(f"first 5 floats: {embedding[:5]}")

    assert len(embedding) > 0
    assert len(embedding[:5]) == 5
    assert all(isinstance(value, float) for value in embedding[:5])


if __name__ == "__main__":
    test_embed_text_with_single_chunk()
    sys.stdout.flush()
    os._exit(0)
