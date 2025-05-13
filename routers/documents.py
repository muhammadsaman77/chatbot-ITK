from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/")
async def get():
  return {"message": "Hello World"}


@router.post("/")
async def post(file:UploadFile):
  return {"message": "Hello World",
          "payload": file.filename
          }


@router.delete("/")
async def delete():
  return {"message": "Hello World"}