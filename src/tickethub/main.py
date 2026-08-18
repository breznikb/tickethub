import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from tickethub.api.ai import router as ai_router
from tickethub.api.tickets import router as tickets_router
from tickethub.core.vector_db import qdrant_client
from tickethub.api.auth import router as auth_router
from tickethub.api.stats import router as stats_router
from tickethub.core.rate_limit import limiter
from tickethub.core.logging_config import configure_logging


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TicketHub application started")

    try:
        yield
    finally:
        await qdrant_client.close()
        logger.info("TicketHub application stopped")


app = FastAPI(title="TicketHub", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(stats_router)
app.include_router(ai_router)


@app.get("/")
async def root():
    return {"status": "ok"}
