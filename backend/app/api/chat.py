from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.services.rag_service import ask_question


router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


class ChatRequest(BaseModel):
    question: str


class ChatSource(BaseModel):
    title: str
    paper_id: int
    chunk_index: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]


@router.post("", response_model=ChatResponse)
@limiter.limit(settings.chat_rate_limit)
def chat(request: Request, chat_request: ChatRequest) -> ChatResponse:
    if not chat_request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required",
        )

    result = ask_question(chat_request.question.strip())

    return ChatResponse(answer=result["answer"], sources=result["sources"])
