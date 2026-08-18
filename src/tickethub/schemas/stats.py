from pydantic import BaseModel

from tickethub.schemas.ticket import TicketPriority, TicketStatus


class TicketStats(BaseModel):
    total_tickets: int
    by_status: dict[TicketStatus, int]
    by_priority: dict[TicketPriority, int]
