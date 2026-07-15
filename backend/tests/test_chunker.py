from app.services.chunker import CHUNK_OVERLAP, CHUNK_SIZE, chunk_text


def test_chunk_text_with_paper_content() -> None:
    paragraph = (
        "PaperHub studies local paper management, PDF parsing, metadata extraction, "
        "and later retrieval workflows. "
    )
    content = paragraph * 30

    chunks = chunk_text(content)

    print(f"chunk count: {len(chunks)}")
    print(f"first chunk length: {len(chunks[0])}")
    print(f"second chunk length: {len(chunks[1])}")

    assert len(chunks) > 2
    assert len(chunks[0]) == CHUNK_SIZE
    assert len(chunks[1]) == CHUNK_SIZE
    assert chunks[0][-CHUNK_OVERLAP:] == chunks[1][:CHUNK_OVERLAP]


def test_chunk_text_empty_content() -> None:
    assert chunk_text("") == []
    assert chunk_text("   ") == []


if __name__ == "__main__":
    test_chunk_text_with_paper_content()
    test_chunk_text_empty_content()
