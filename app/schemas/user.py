from app.models import  User
from pydantic import BaseModel

class IncomingCreateData(BaseModel):
    name: str
    email: str
    password: str

class OutgoingUserData(BaseModel):
    name: str
    email: str

class Loginform(BaseModel):
    email: str
    password: str