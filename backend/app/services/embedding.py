from __future__ import annotations

from time import perf_counter

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.paths import MODEL_CACHE_DIR


settings = get_settings()
DEFAULT_EMBEDDING_MODEL = settings.embedding_model

_model: SentenceTransformer | None = None
_model_load_seconds: float | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model, _model_load_seconds

    if _model is None:
        start = perf_counter()
        MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _model = SentenceTransformer(
            DEFAULT_EMBEDDING_MODEL,
            cache_folder=str(MODEL_CACHE_DIR),
        )
        _model_load_seconds = perf_counter() - start

    return _model


def get_model_load_seconds() -> float | None:
    return _model_load_seconds


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
