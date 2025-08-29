
from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile,Form,File,Depends
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from datetime import datetime,timezone
import os

from langchain_community.vectorstores.utils import filter_complex_metadata

from src.configs.global_instances import get_minio_instance, get_vector_db_instance
from src.services.document_service import chunking_document, extract_text_from_pdf
from src.services.rag_service import storing_to_vector_db, delete_documents_by_source, list_sources_in_vector_db
from src.routers.auth import get_current_user
from src.models.document import MDocument
from langchain.schema import Document
from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path
import os, shutil, tempfile
from bson import ObjectId

bucket_name = os.getenv("MINIO_BUCKET_NAME")
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
    client = get_minio_instance()
    
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
    suffix = Path(file.filename or "").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        shutil.copyfileobj(file.file, tmp)

    try:
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        object_name = f"documents/{now_str}_{Path(file.filename).name}"
        text_pdf = extract_text_from_pdf(file_path=tmp_path,source=object_name)
        chunks = chunking_document(text_pdf, chunk_size=200, chunk_overlap=100)
        filtered_chunks = filter_complex_metadata(chunks)
        vector_db = get_vector_db_instance()
        storing_to_vector_db(vector_db, filtered_chunks)
        file_size = os.path.getsize(tmp_path)

        # Get MinIO client
        client = get_minio_instance()
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)

        
        with open(tmp_path, "rb") as f:
            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=f,
                length=file_size,
                content_type=file.content_type or "application/octet-stream",
            )

        
        document = MDocument(description=description, file=object_name)
        await MDocument.insert(document)

        return {
            "message": "Upload document successfully",
            "payload": object_name,
        }
    finally:
        
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    

@router.delete("/{id}")
async def delete(current_user: Annotated[str,Depends(get_current_user)], id:str):
  client = get_minio_instance()
  vector_db = get_vector_db_instance()
  found = client.bucket_exists(bucket_name)
  if not found:
     return {"message": "Bucket not found"}
  document = await MDocument.find_one({"_id": ObjectId(id)})
  if document is None:
     return {"message": "Document not found"}
  
  # Get filename for vector database deletion
  object_name = document.file
  filename = object_name.split("/")[-1]  
  deleted_chunks = delete_documents_by_source(vector_db, object_name)
  
  # Delete from MinIO
  client.remove_object(bucket_name=bucket_name, object_name=object_name)
  
  # Delete from MongoDB
  await document.delete()
  
  return {
    "message": "Document deleted successfully", 
    "payload": {
      "object_name": object_name,
      "filename": filename,
    }
  }

@router.get("/sources")
async def get_vector_sources(current_user: Annotated[str,Depends(get_current_user)]):
  """Debug endpoint to list all source files in vector database"""
  if current_user["role"] != "admin":
     raise HTTPException(status_code=403, detail="Admin only")
  
  vector_db = get_vector_db_instance()
  sources = list_sources_in_vector_db(vector_db)
  
  return {
    "message": "Sources in vector database",
    "payload": {
      "sources": sources,
      "total_sources": len(sources)
    }
  }
  