
from typing import Annotated
from fastapi import APIRouter, UploadFile,Form,File,Depends
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from datetime import datetime,timezone
import os
from ..routers.auth import get_current_user
from ..configs.minio import init_minio
from ..configs.mongo import init_mongodb

bucket_name = os.getenv("MINIO_BUCKET_NAME")
client = init_minio()
db = init_mongodb()
router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
async def get(current_user: Annotated[str,Depends(get_current_user)]):
  documents = db["documents"].find()
  results = []
  for doc in documents:
    doc["_id"] = str(doc["_id"])    
    filename = doc["file"]
    doc["file_url"] = f"/api/documents/download/{quote(filename)}"
    del doc["file"]
    results.append(doc)
  return {"message": "Hello World", "payload": results}

@router.get("/download/{filename}")
async def download(current_user: Annotated[str,Depends(get_current_user)], filename:str):
  found = client.bucket_exists(bucket_name)
  if not found:
    client.make_bucket(bucket_name)
  file = client.get_object(bucket_name=bucket_name, object_name=filename)
  return StreamingResponse(file, media_type="applicat ion/octet-stream", headers={"Content-Disposition": f'attachment; filename="{filename}"'})

@router.post("/")
async def post(current_user: Annotated[str,Depends(get_current_user)], title:str = Form(...), file:UploadFile=File(...)):
  found = client.bucket_exists(bucket_name)
  destination_file = "documents/"+  datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")+"_" +file.filename
  if not found:
      client.make_bucket(bucket_name)
  client.put_object(bucket_name=bucket_name, object_name=destination_file,data=file.file, length=file.size) 
  db["documents"].insert_one({"title": title, "file": destination_file, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)})
  return {"message": "Upload document successfully","payload": destination_file}
