from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.core.db import get_db
from tickethub.models.ticket import Ticket
from tickethub.schemas.ticket import TicketDetail, TicketListItem

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _to_list_item(ticket: Ticket) -> TicketListItem:
    return TicketListItem(
        id=ticket.id,
        title=ticket.title,
        status=ticket.status,
        priority=ticket.priority,
        description=ticket.title[:100],
    )


@router.get("/search", response_model=list[TicketListItem])
async def search_tickets(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ticket).where(Ticket.title.ilike(f"%{q}%")))
    tickets = result.scalars().all()
    return [_to_list_item(t) for t in tickets]


@router.get("", response_model=list[TicketListItem])
async def list_tickets(
    skip: int = 0,
    limit: int = Query(20, le=100),
    status: str | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    tickets = result.scalars().all()
    return [_to_list_item(t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket