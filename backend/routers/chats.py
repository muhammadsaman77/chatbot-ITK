from fastapi import APIRouter
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse
from ..config import llm
from pydantic import BaseModel

import asyncio

class Prompt(BaseModel):
  question: str

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/")
async def get():
  return {"message": "Hello World"}


async def stream_llm_response(prompt:str)-> AsyncGenerator[str, None]:
  llama = llm.init_llm()
  for token in llama.stream(prompt):
    yield str(token)
    await asyncio.sleep(0.01)
    
@router.post("/")
async def generate_response_stream(prompt: Prompt):
  return StreamingResponse(stream_llm_response(prompt.question),media_type="text/plain")

