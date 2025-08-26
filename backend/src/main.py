from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv(".env.local")
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .configs.mongo import init_mongodb

from .routers import auth,documents,chats

origins = [
    "http://localhost:5173",  # Vite dev
    "http://127.0.0.1:5173",  # alternatif
]

@asynccontextmanager
async def lifespan(app: FastAPI):
  await init_mongodb()
  yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # atau ["*"] kalau mau bebas
    allow_credentials=True,
    allow_methods=["*"],  # ["GET", "POST", ...] kalau mau dibatasi
    allow_headers=["*"],
)
app.include_router(auth.router,prefix="/api",)
app.include_router(documents.router,prefix="/api")
app.include_router(chats.router,prefix="/api")
@app.get("/ping")
async def root():
  return {"message": "PONG"}
