from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from tickethub.core.db import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    assignee: Mapped[str] = mapped_column(String, nullable=False)
    source_data: Mapped[dict] = mapped_column(JSON, nullable=False)