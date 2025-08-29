from typing import AsyncGenerator, Annotated
from fastapi import APIRouter, Depends,Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.services.rag_service import create_prompt_llm
from ..configs.global_instances import (
    get_llama_instance,
    get_vector_db_instance,
)
from ..routers.auth import get_current_user

import asyncio


router = APIRouter(prefix="/chats", tags=["chat"])
@router.get("/")
async def get():
  return {"message": "Hello World"}


async def stream_llm_response(prompt:str)-> AsyncGenerator[str, None]:
  llama = get_llama_instance()
  vector_db = get_vector_db_instance()
  formatted_prompt = create_prompt_llm(vector_db, prompt)
  print(formatted_prompt)
  for token in llama.stream(formatted_prompt):
    yield str(token)
    await asyncio.sleep(0.01)
@router.post("/")
async def generate_response_stream(current_user: Annotated[str,Depends(get_current_user)],question: str = Form(...)):
  if (current_user["role"]!= "user"):
    raise HTTPException(status_code=403, detail="User only")
    
  prompt_text = f"""Kamu adalah asisten akademik cerdas dari Institut Teknologi Kalimantan (ITK). 
    Jawablah pertanyaan pengguna berdas arkan dokumen yang tersedia. 
    Jika tidak ditemukan jawabannya dalam dokumen, katakan bahwa informasi tersebut tidak tersedia.

    {question}
    """

  return StreamingResponse(
        stream_llm_response(prompt_text),
        media_type="text/plain"
    )

