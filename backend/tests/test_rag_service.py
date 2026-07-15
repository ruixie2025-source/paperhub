import os
import sys

import fitz
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.paper import Paper
from app.services.rag_service import ask_question
from app.services.retriever import search_chunks
from app.services.vector_store import delete_paper_index, reindex_paper


QUESTION = "What is reinforcement learning?"


def build_rag_pdf() -> bytes:
    document = fitz.open()
    text = (
        "Reinforcement learning is a machine learning framework where an agent "
        "learns to make decisions by interacting with an environment. The agent "
        "observes states, chooses actions, receives rewards, and updates its "
        "policy to maximize cumulative reward over time. Important ideas include "
        "exploration, exploitation, value functions, and Markov decision processes. "
    )

    for page_index in range(5):
        page = document.new_page()
        page.insert_textbox(
            fitz.Rect(72, 72, 520, 760),
            f"RAG QA Test Page {page_index + 1}\n\n" + text * 4,
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


def test_ask_question() -> None:
    with TestClient(app) as client:
        create_response = client.post(
            "/papers",
            json={
                "title": "RAG Reinforcement Learning Test",
                "authors": "",
                "journal": "",
                "keywords": "",
            },
        )
        create_response.raise_for_status()
        paper_id = create_response.json()["id"]

        upload_response = client.post(
            f"/papers/{paper_id}/upload",
            files={"file": ("rag-test.pdf", build_rag_pdf(), "application/pdf")},
        )
        upload_response.raise_for_status()

    paper = get_uploaded_paper(paper_id)
    reindex_paper(paper)

    try:
        retrieved_chunks = search_chunks(QUESTION, top_k=5)

        print(f"Question: {QUESTION}")
        print("Retrieved Chunks:")
        for index, chunk in enumerate(retrieved_chunks, start=1):
            print(
                f"{index}. distance={chunk['distance']} "
                f"title={chunk['title']} "
                f"chunk_index={chunk['chunk_index']} "
                f"text={chunk['text'][:150]}"
        )

        if not os.getenv("DEEPSEEK_API_KEY"):
            print("DeepSeek Answer: skipped because DEEPSEEK_API_KEY is not set")
            print("Sources: skipped because DeepSeek answer generation was not called")
            return

        result = ask_question(QUESTION)
        print(f"DeepSeek Answer: {result['answer']}")
        print(f"Sources: {result['sources']}")

        assert result["answer"]
        assert result["sources"]
        assert all(source["paper_id"] == paper_id for source in result["sources"])
    finally:
        delete_paper_index(paper_id)


if __name__ == "__main__":
    test_ask_question()
    sys.stdout.flush()
    os._exit(0)
