from .routers import chats,auth
from fastapi import FastAPI




app = FastAPI()
app.include_router(chats.router)
app.include_router(auth.router)
@app.get("/ping")
async def root():
  return {"message": "PONG"}
