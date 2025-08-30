import json
import os
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

async def stream_llm_response_sse(prompt:str)-> AsyncGenerator[str, None]:
  print("stream_llm_response_sse")
  llama = get_llama_instance()
  minio_url = os.getenv("MINIO_URL")
  print(minio_url)
  vector_db = get_vector_db_instance()
  prompt_data = create_prompt_llm(vector_db, prompt)
  
  print(prompt_data["formatted_prompt"])
  print(prompt_data["sources_pages"])
  
  for token in llama.stream(prompt_data["formatted_prompt"]):
    response_chunk = {
      "type": "token",
      "data": str(token)
    }
    yield f"data: {json.dumps(response_chunk)}\n\n"
    await asyncio.sleep(0.01)

  for source in prompt_data["sources_pages"]:
    source_chunk = {
      "type": "tags",
      "data": source
    }
    yield f"data: {json.dumps(source_chunk)}\n\n"
    await asyncio.sleep(0.01)
  end_stream_chunk = {
    "type": "end",
    "data": "end of stream"}
  yield f"data: {json.dumps(end_stream_chunk)}\n\n"
  
  
@router.post("/")
async def genersate_response_stream(current_user: Annotated[str,Depends(get_current_user)],question: str = Form(...)):
  if (current_user["role"]!= "user"):
    raise HTTPException(status_code=403, detail="User only")
  return StreamingResponse(
        stream_llm_response_sse(question),
        media_type="text/event-stream"
    )

