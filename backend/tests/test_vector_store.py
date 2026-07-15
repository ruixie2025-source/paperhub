import os
import sys

from app.db.session import SessionLocal
from app.models.paper import Paper
from app.services.vector_store import (
    delete_paper_index,
    get_collection,
    reindex_paper,
)


def get_paper_with_content() -> Paper:
    db = SessionLocal()
    try:
        paper = (
            db.query(Paper)
            .filter(Paper.content.is_not(None))
            .filter(Paper.content != "")
            .order_by(Paper.id.desc())
            .first()
        )
        assert paper is not None
        assert paper.content
        db.expunge(paper)
        return paper
    finally:
        db.close()


def test_index_paper() -> None:
    paper = get_paper_with_content()
    indexed_count = reindex_paper(paper)

    try:
        collection = get_collection()
        peeked = collection.peek(limit=1)
        stored = collection.get(ids=[f"paper_{paper.id}_0"])

        print(f"total chunk count: {indexed_count}")
        print(f"collection count: {collection.count()}")
        print(f"peek ids: {peeked['ids']}")
        print(f"peek documents: {peeked['documents']}")
        print(f"peek embeddings length: {len(peeked['embeddings'][0])}")
        print(f"peek metadatas: {peeked['metadatas']}")

        assert indexed_count > 0
        assert collection.count() >= indexed_count
        assert peeked["documents"]
        assert len(peeked["embeddings"]) > 0
        assert len(peeked["embeddings"][0]) == 1024
        assert peeked["metadatas"]
        assert stored["ids"] == [f"paper_{paper.id}_0"]
        assert stored["metadatas"][0]["paper_id"] == paper.id
        assert stored["metadatas"][0]["title"] == paper.title
    finally:
        delete_paper_index(paper.id)


if __name__ == "__main__":
    test_index_paper()
    sys.stdout.flush()
    os._exit(0)
