from pydantic import BaseModel
from typing import Literal

TicketStatus = Literal["open", "closed"]
TicketPriority = Literal["low", "medium", "high"]


class TicketListItem(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    description: str

    model_config = {"from_attributes": True}


class TicketDetail(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    assignee: str
    source_data: dict

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    title: str
    status: TicketStatus = "open"
    priority: TicketPriority = "medium"
    assignee: str


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assignee: str | None = None
