from pydantic import BaseModel, model_validator
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

    @model_validator(mode="after")
    def reject_explicit_nulls(self):
        null_fields = [
            field
            for field in self.model_fields_set
            if getattr(self, field) is None
        ]

        if null_fields:
            fields = ", ".join(sorted(null_fields))
            raise ValueError(f"Fields cannot be null: {fields}")

        return self
