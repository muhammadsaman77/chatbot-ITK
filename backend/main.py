from dotenv import load_dotenv
load_dotenv(".env.local")
from fastapi import FastAPI

from .routers import auth,documents


app = FastAPI()
app.include_router(auth.router,prefix="/api",)
app.include_router(documents.router,prefix="/api")
@app.get("/ping")
async def root():
  return {"message": "PONG"}
