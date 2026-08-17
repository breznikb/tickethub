from contextlib import asynccontextmanager

from fastapi import FastAPI

from tickethub.api.tickets import router as tickets_router
from tickethub.core.vector_db import qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await qdrant_client.close()


app = FastAPI(title="TicketHub", lifespan=lifespan)
app.include_router(tickets_router)


@app.get("/")
async def root():
    return {"status": "ok"}
