from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.core.db import get_db
from tickethub.core.security import get_current_user
from tickethub.models.ticket import Ticket
from tickethub.schemas.stats import TicketStats


router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=TicketStats)
async def get_ticket_stats(
    db: AsyncSession = Depends(get_db),
) -> TicketStats:
    total_tickets = await db.scalar(
        select(func.count(Ticket.id))
    )

    status_result = await db.execute(
        select(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
    )
    by_status = {
        "open": 0,
        "closed": 0,
    }
    by_status.update({
        status: count
        for status, count in status_result.all()
    })

    priority_result = await db.execute(
        select(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
    )
    by_priority = {
        "low": 0,
        "medium": 0,
        "high": 0,
    }
    by_priority.update({
        priority: count
        for priority, count in priority_result.all()
    })

    return TicketStats(
        total_tickets=total_tickets or 0,
        by_status=by_status,
        by_priority=by_priority,
    )
