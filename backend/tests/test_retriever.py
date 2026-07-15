import os
import sys

import fitz
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.paper import Paper
from app.services.retriever import search_chunks
from app.services.vector_store import delete_paper_index, reindex_paper


def build_retrieval_pdf() -> bytes:
    document = fitz.open()
    reinforcement_learning_text = (
        "Reinforcement learning is a machine learning framework where an agent "
        "learns by taking actions in an environment and receiving rewards. "
        "The agent improves a policy to maximize long term cumulative reward. "
        "Core concepts include states, actions, rewards, value functions, "
        "policy optimization, exploration, exploitation, temporal difference "
        "learning, and Markov decision processes. "
    )
    unrelated_text = (
        "PaperHub also manages PDF parsing, metadata extraction, vector storage, "
        "and local semantic retrieval for research notes. "
    )

    for page_index in range(6):
        page = document.new_page()
        page.insert_textbox(
            fitz.Rect(72, 72, 520, 760),
            f"Semantic Retrieval Test Page {page_index + 1}\n\n"
            + reinforcement_learning_text * 3
            + unrelated_text * 2,
            fontsize=11,
        )

    pdf_bytes = document.write()
    document.close()
    return pdf_bytes


def get_uploaded_paper(paper_id: int) -> Paper:
    db = SessionLocal()
    try:
        paper = db.get(Paper, paper_id)
        assert paper is not None
        assert paper.content
        db.expunge(paper)
        return paper
    finally:
        db.close()


def test_search_chunks() -> None:
    with TestClient(app) as client:
        create_response = client.post(
            "/papers",
            json={
                "title": "Reinforcement Learning Retrieval Test",
                "authors": "",
                "journal": "",
                "keywords": "",
            },
        )
        create_response.raise_for_status()
        paper_id = create_response.json()["id"]

        upload_response = client.post(
            f"/papers/{paper_id}/upload",
            files={"file": ("retrieval-test.pdf", build_retrieval_pdf(), "application/pdf")},
        )
        upload_response.raise_for_status()

    paper = get_uploaded_paper(paper_id)
    indexed_count = reindex_paper(paper)

    try:
        results = search_chunks("What is reinforcement learning?", top_k=5)

        print(f"indexed chunks: {indexed_count}")
        print("Top5:")
        for index, result in enumerate(results, start=1):
            print(
                f"{index}. distance={result['distance']} "
                f"title={result['title']} "
                f"chunk_index={result['chunk_index']} "
                f"text={result['text'][:150]}"
            )

        assert indexed_count >= 5
        assert len(results) == 5
        assert all(result["text"] for result in results)
        assert all(result["paper_id"] == paper_id for result in results)
        assert all(result["title"] == paper.title for result in results)
        assert all("distance" in result for result in results)
    finally:
        delete_paper_index(paper_id)


if __name__ == "__main__":
    test_search_chunks()
    sys.stdout.flush()
    os._exit(0)
