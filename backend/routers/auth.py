from fastapi import APIRouter,Response
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from passlib.context import CryptContext
import jwt
from ..configs.mongo import init_mongodb
from ..models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["auth"])
db = init_mongodb()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    )
    print(token)
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        user_id = payload.get("user_id")
        print(user_id)
        if user_id is None:
            raise credentials_exception
        return user_id
    except InvalidTokenError:
        raise credentials_exception



@router.post("/login/",status_code=200)
async def login(user_request:User,response:Response):
  
  user = db["users"].find_one({"email": user_request.email})
  if user is None:
    response.status_code = 401
    return {
        "success": False,
        "message": "Email or password is incorrect"
            }

  if not pwd_context.verify(user_request.password.encode("utf-8"), user["password"]):
    response.status_code = 401
    return {
        "success": False,
        "message": "Email or password is incorrect"
            }
  user_id = user["_id"]
  
  token =  jwt.encode({"user_id": str(user_id), "email": user_request.email}, "secret", algorithm="HS256")
  return {
      "success": True,
      "message": "Login successfully",
      "payload": {
          "token": token
      }
        
  }
  
@router.get("/signup/")
async def get():
  return {"message": "Hello World"}