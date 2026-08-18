import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.core.db import get_db
from tickethub.core.security import get_current_user
from tickethub.schemas.ai import (
    AnswerSource,
    AskTicketsRequest,
    AskTicketsResponse,
)
from tickethub.services.rag import answer_ticket_question


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/ask",
    response_model=AskTicketsResponse,
)
async def ask_about_tickets(
    payload: AskTicketsRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await answer_ticket_question(
            question=payload.question,
            db=db,
            limit=payload.limit,
            status=payload.status,
            priority=payload.priority,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="The local AI model is unavailable",
        ) from exc

    return AskTicketsResponse(
        answer=result.answer,
        sources=[
            AnswerSource(
                id=source.id,
                title=source.title,
                score=source.score,
            )
            for source in result.sources
        ],
    )
