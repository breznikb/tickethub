from fastapi import FastAPI

app = FastAPI(title="TicketHub")


@app.get("/")
async def root():
    return {"status": "ok"}