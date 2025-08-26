
from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile,Form,File,Depends
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from datetime import datetime,timezone
import os
from ..routers.auth import get_current_user
from ..models.document import MDocument
from langchain.schema import Document
from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path
import os, shutil, tempfile
from bson import ObjectId

from ..configs.minio import init_minio

bucket_name = os.getenv("MINIO_BUCKET_NAME")
client = init_minio()
router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
async def get(current_user: Annotated[str,Depends(get_current_user)]):
  if current_user["role"]!= "admin":
     raise HTTPException(status_code=403, detail="Admin only")
  documents = await MDocument.find({}).to_list()
  results = []
  for doc in documents:
    data = {}
    filename = doc.file
    data["id"] = str(doc.id)
    data["description"] = doc.description
    data["file_name"] = doc.file.split("/")[-1]
    results.append(data)
  return {"message": "Success get documents", "payload": results}

@router.get("/download/{filename}")
async def download(current_user: Annotated[str, Depends(get_current_user)], filename: str):

    if not client.bucket_exists(bucket_name):
        
        client.make_bucket(bucket_name)
    
    try:

        file_obj = client.get_object(bucket_name=bucket_name, object_name="documents/"+filename)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in bucket.")
  
    return StreamingResponse(
        file_obj,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.post("/")
async def post(
    current_user: Annotated[str, Depends(get_current_user)],
    description: str = Form(...),
    file: UploadFile = File(...)
):
    # 1) Simpan ke file sementara
    suffix = Path(file.filename or "").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        shutil.copyfileobj(file.file, tmp)

    try:
        # 2) Pastikan ukuran & buat nama unik untuk object di MinIO
        file_size = os.path.getsize(tmp_path)
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        object_name = f"documents/{now_str}_{Path(file.filename).name}"

        # 3) Buat bucket jika perlu
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)

        # 4) Upload ke MinIO dari file temp
        with open(tmp_path, "rb") as f:
            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=f,
                length=file_size,
                content_type=file.content_type or "application/octet-stream",
            )

        # 5) Simpan metadata dokumen ke DB
        document = MDocument(description=description, file=object_name)
        await MDocument.insert(document)

        return {
            "message": "Upload document successfully",
            "payload": object_name,
        }
    finally:
        # Hapus file temp
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    

@router.delete("/{id}")
async def delete(current_user: Annotated[str,Depends(get_current_user)], id:str):
  found = client.bucket_exists(bucket_name)
  if not found:
     return {"message": "Bucket not found"}
  document = await MDocument.find_one({"_id": ObjectId(id)})
  if document is None:
     return {"message": "Document not found"}
  object_name = document.file
  client.remove_object(bucket_name=bucket_name, object_name=object_name)
  await document.delete()
  
  return {"message": "Document deleted", "payload": object_name}