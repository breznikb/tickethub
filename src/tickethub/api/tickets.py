import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.core.db import get_db
from tickethub.models.ticket import Ticket
from tickethub.services.vector_sync import index_ticket_safely
from tickethub.schemas.ticket import (
    TicketCreate,
    TicketDetail,
    TicketListItem,
    TicketPriority,
    TicketSemanticSearchResult,
    TicketStatus,
    TicketUpdate,
)
from tickethub.services.vector_store import search_ticket_vectors
from tickethub.core.security import get_current_user
from tickethub.core.cache import get_cached_ticket, invalidate_cached_ticket, set_cached_ticket


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Depends(get_current_user)],
)


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


@router.get(
    "/semantic-search",
    response_model=list[TicketSemanticSearchResult],
)
async def semantic_search_tickets(
    q: str = Query(min_length=1),
    limit: int = Query(10, ge=1, le=50),
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    db: AsyncSession = Depends(get_db),
):
    matches = await search_ticket_vectors(
        query=q,
        limit=limit,
        status=status,
        priority=priority,
    )

    if not matches:
        return []

    ticket_ids = [match.ticket_id for match in matches]

    result = await db.execute(
        select(Ticket).where(Ticket.id.in_(ticket_ids))
    )
    tickets_by_id = {
        ticket.id: ticket
        for ticket in result.scalars().all()
    }

    return [
        TicketSemanticSearchResult(
            **_to_list_item(tickets_by_id[match.ticket_id]).model_dump(),
            score=match.score,
        )
        for match in matches
        if match.ticket_id in tickets_by_id
    ]


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
    cached = await get_cached_ticket(ticket_id)
    if cached is not None:
        return cached

    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    result = TicketDetail.model_validate(ticket).model_dump(mode="json")
    await set_cached_ticket(ticket_id, result)
    return result


@router.post("", response_model=TicketDetail, status_code=201)
async def create_ticket(
    payload: TicketCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    ticket = Ticket(
        title=payload.title,
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        source_data=payload.model_dump(),
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    logger.info(
        "Ticket created: ticket_id=%s",
        ticket.id,
    )

    background_tasks.add_task(
        index_ticket_safely,
        ticket,
    )

    return ticket


@router.patch("/{ticket_id}", response_model=TicketDetail)
async def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(ticket, key, value)

    await db.commit()
    await db.refresh(ticket)
    await invalidate_cached_ticket(ticket_id)

    logger.info(
        "Ticket updated: ticket_id=%s fields=%s",
        ticket.id,
        ",".join(sorted(updates)),
    )

    background_tasks.add_task(
        index_ticket_safely,
        ticket,
    )

    return ticket
