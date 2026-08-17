from pydantic import BaseModel, Field

from tickethub.schemas.ticket import (
    TicketPriority,
    TicketStatus,
)


class AskTicketsRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=10)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None


class AnswerSource(BaseModel):
    id: int
    title: str
    score: float


class AskTicketsResponse(BaseModel):
    answer: str
    sources: list[AnswerSource]
