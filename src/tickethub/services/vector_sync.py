import logging

from tickethub.models.ticket import Ticket
from tickethub.services.index_tickets import index_ticket


logger = logging.getLogger(__name__)


async def index_ticket_safely(ticket: Ticket) -> None:
    try:
        await index_ticket(ticket)
    except Exception:
        logger.exception(
            "Failed to index ticket %s",
            ticket.id,
        )
