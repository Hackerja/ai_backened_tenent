from pwdlib import PasswordHash
from app.models import User
import jwt
from jwt.exceptions import InvalidTokenError
from .config import settings
from app.schemas.token_sch import Token
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from .database import AsyncSessionLocal
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel





oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    email: str | None = None





password_hash = PasswordHash.recommended()
dummy_password = password_hash.hash('dummypassword')

def verify_password(plain_password, hash_password):
    return password_hash.verify(plain_password, hash_password)

def get_password_hash(password):
    return password_hash.hash(password)

async def get_user(email: str):
    async with AsyncSessionLocal() as session:

        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

async def authenitcate_user(email, password):
    user = await get_user(email)
    if not user:
        verify_password(password, dummy_password)
        return False

    if not verify_password(password, user.hash_password):
        return False
    return user


#jwt tokens area

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta

    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_sec_key , algorithm= settings.ALGORITHM)
    return encoded_jwt 


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_execpetion = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail="could not verify credentials",
        headers={"WWW-Authenticate": "Bearer"},

    )

    try:
        payload = jwt.decode(token, settings.jwt_sec_key, algorithms=settings.ALGORITHM)
        email = payload.get('sub')

        if email is None:
            raise credentials_execpetion
        
        token_data = TokenData(email=email)

    except InvalidTokenError:
        raise credentials_execpetion


    user = await get_user(token_data.email)
    if not user:
        raise credentials_execpetion
    
    return user



    


