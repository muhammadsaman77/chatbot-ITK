from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login/")
async def get():
  return {"message": "Hello World"}

@router.get("/signup/")
async def get():
  return {"message": "Hello World"}