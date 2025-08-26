from pydantic import BaseModel
from beanie import Document, Link

class Role(Document):
    class Settings: name = "roles"
    name: str

class User(Document):
    class Settings: name = "users"
    first_name: str
    last_name: str
    email: str
    password: str
    role: Link[Role]

class LoginUser(BaseModel):
    email: str
    password: str

class RegisterUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str