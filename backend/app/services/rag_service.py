from __future__ import annotations

from typing import Any

from app.services.llm_service import generate_answer
from app.services.retriever import search_chunks


NO_RELEVANT_CONTENT_ANSWER = "论文中没有找到相关内容。"


def build_prompt(question: str, chunks: list[dict[str, Any]]) -> str:
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"Paper:\n{chunk['title']}\n\n"
            f"Chunk:\n{chunk['text']}"
        )

    context = "\n\n------------------\n\n".join(context_parts)
    return f"""
你是一位论文阅读与研究分析助手。

请先理解 Context 中的论文内容，再结合学术研究常识做分析、解释和合理推测。

要求：

1. 回答需要优先基于 Context 中的论文内容。

2. 可以给出合理推测、机制解释、延伸理解和可能含义，但必须明确标注为“合理推测”或“可能解释”，不要把推测说成论文原文结论。

3. 如果 Context 只提供了部分依据，请先说明“根据已有论文内容”，再补充合理解释。

4. 如果 Context 完全没有相关信息，请回答：

"论文中没有找到相关内容。"

5. 不要编造具体数据、模型结果、作者观点或论文结论。

6. 回答结构建议：
   - 原文依据
   - 分析解释
   - 合理推测
   - 引用论文标题

7. 最后列出引用论文标题。

Context:
{context}

Question:
{question}

Answer:
""".strip()


def ask_question(question: str) -> dict[str, Any]:
    chunks = search_chunks(question, top_k=5)
    if not chunks:
        return {
            "answer": NO_RELEVANT_CONTENT_ANSWER,
            "sources": [],
            "chunks": [],
        }

    prompt = build_prompt(question, chunks)
    answer = generate_answer(prompt)
    sources = [
        {
            "title": chunk["title"],
            "paper_id": chunk["paper_id"],
            "chunk_index": chunk["chunk_index"],
        }
        for chunk in chunks
    ]

    return {
        "answer": answer or NO_RELEVANT_CONTENT_ANSWER,
        "sources": sources,
        "chunks": chunks,
    }
