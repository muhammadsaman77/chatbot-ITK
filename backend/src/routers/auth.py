from fastapi import APIRouter,Response
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from typing import Annotated,Dict,Any
from passlib.context import CryptContext
import jwt
from ..models.user import RegisterUser,LoginUser,User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)])-> Dict[str,Any]:
    
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired",headers={"WWW-Authenticate": "Bearer"})
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    return {"user_id":user_id,"role":role}
    

@router.post("/login/",status_code=200)
async def login(user_request:LoginUser,response:Response):
  user = await User.find_one(User.email == user_request.email)
  await user.fetch_link(User.role)
  if user is None:
    response.status_code = 401
    return {
        "success": False,
        "message": "Email or password is incorrect"
            }

  if not pwd_context.verify(user_request.password.encode("utf-8"), user.password):
    response.status_code = 401
    return {
        
        "message": "Email or password is incorrect"
            }
  user_id = user.id
  
  token =  jwt.encode({"role": str(user.role.name), "user_id": str(user_id), "email": user_request.email}, "secret", algorithm="HS256")
  return {
      
      "message": "Login successfully",
      "payload": {
          "token": token,
          "user": {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role.name
          }
      }
        
  }
  
@router.post("/register/", status_code=201)
async def register(request: RegisterUser,response: Response):
  user = await User.find_one({"email": request.email})
  if user:
    response.status_code = 400
    return {
        "success": False,
        "message": "User already exists"
    }
  hashed_password = pwd_context.hash(request.password)
  result = await User.insert_one({"first_name": request.first_name, "last_name": request.last_name, "email": request.email, "password": hashed_password},)

  token = jwt.encode({"user_id": str(result.inserted_id), "email": request.email}, "secret", algorithm="HS256")

  return {
      
      "message": "Register successfully",
      "payload": {
          "token": token,
          "user": {
            "id": str(result.inserted_id),
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "role": "user"
          }
      }
  }

@router.get("/get-me")
async def get_me(current_user: Annotated[str, Depends(get_current_user)]):
  print(current_user["user_id"])
  user = await User.get(current_user["user_id"])
  await user.fetch_link(User.role)
  payload = {
    "id": str(user.id),
    "first_name": user.first_name,
    "last_name": user.last_name,
    "email": user.email,
    "role": user.role.name
  }
  return {
    "message": "Get me successfully",
    "payload": payload
  }