from pydantic import BaseModel


class TicketListItem(BaseModel):
    id: int
    title: str
    status: str
    priority: str
    description: str

    model_config = {"from_attributes": True}


class TicketDetail(BaseModel):
    id: int
    title: str
    status: str
    priority: str
    assignee: str
    source_data: dict

    model_config = {"from_attributes": True}