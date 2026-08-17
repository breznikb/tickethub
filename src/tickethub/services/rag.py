from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.models.ticket import Ticket
from tickethub.services.ollama_client import generate_answer
from tickethub.services.vector_store import search_ticket_vectors
from tickethub.core.config import RAG_MIN_RELEVANCE_SCORE


@dataclass(frozen=True)
class RagSource:
    id: int
    title: str
    score: float


@dataclass(frozen=True)
class RagResult:
    answer: str
    sources: list[RagSource]


def ticket_to_context(ticket: Ticket) -> str:
    return "\n".join(
        [
            f"[Ticket #{ticket.id}]",
            f"Title: {ticket.title}",
            f"Status: {ticket.status}",
            f"Priority: {ticket.priority}",
            f"Assignee: {ticket.assignee}",
        ]
    )


async def answer_ticket_question(
    question: str,
    db: AsyncSession,
    limit: int = 5,
    status: str | None = None,
    priority: str | None = None,
) -> RagResult:
    matches = await search_ticket_vectors(
        query=question,
        limit=limit,
        status=status,
        priority=priority,
    )

    matches = [
        match
        for match in matches
        if match.score >= RAG_MIN_RELEVANCE_SCORE
    ]

    if not matches:
        return RagResult(
            answer="I could not find relevant tickets.",
            sources=[],
        )

    ticket_ids = [match.ticket_id for match in matches]

    result = await db.execute(
        select(Ticket).where(Ticket.id.in_(ticket_ids))
    )
    tickets_by_id = {
        ticket.id: ticket
        for ticket in result.scalars().all()
    }

    ordered_matches = [
        (tickets_by_id[match.ticket_id], match.score)
        for match in matches
        if match.ticket_id in tickets_by_id
    ]

    if not ordered_matches:
        return RagResult(
            answer="I could not find relevant tickets.",
            sources=[],
        )

    context = "\n\n".join(
        ticket_to_context(ticket)
        for ticket, _score in ordered_matches
    )

    answer = await generate_answer(
        question=question,
        context=context,
    )

    sources = [
        RagSource(
            id=ticket.id,
            title=ticket.title,
            score=score,
        )
        for ticket, score in ordered_matches
    ]

    return RagResult(
        answer=answer,
        sources=sources,
    )
