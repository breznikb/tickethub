from fastapi import FastAPI

from tickethub.api.tickets import router as tickets_router

app = FastAPI(title="TicketHub")
app.include_router(tickets_router)


@app.get("/")
async def root():
    return {"status": "ok"}
