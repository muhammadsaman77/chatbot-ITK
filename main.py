from .routers import chats
from fastapi import FastAPI




app = FastAPI()
app.include_router(chats.router)

@app.get("/ping")
async def root():
  return {"message": "PONG"}
