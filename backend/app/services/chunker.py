CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def chunk_text(content: str) -> list[str]:
    text = content.strip()
    if not text:
        return []

    chunks: list[str] = []
    step = CHUNK_SIZE - CHUNK_OVERLAP

    for start in range(0, len(text), step):
        chunk = text[start : start + CHUNK_SIZE]
        if chunk:
            chunks.append(chunk)
        if start + CHUNK_SIZE >= len(text):
            break

    return chunks
