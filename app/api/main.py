from fastapi import FastAPI, HTTPException, status, Depends
from datetime import datetime, timezone

from ..core.config import settings
from app.schemas.user import IncomingCreateData, OutgoingUserData, Loginform
from ..models import User
from ..core.database import AsyncSessionLocal
from app.core.security import get_password_hash, authenitcate_user, create_access_token, get_current_user
from app.core.supabase import supabase
from app.services.emeddings import control
from pathlib import Path
from sqlalchemy import select




app = FastAPI()


@app.get("/")
async def home():
    return {
        "app": settings.app_name,
        "debug": settings.debug
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/register")
async def register(data: IncomingCreateData):
    name = data.name
    email = data.email
    password = data.password

    async with AsyncSessionLocal() as session:
        user = User(name=name, email=email, hash_password=get_password_hash(password))
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


@app.post("/login")
async def login(login_data: Loginform):
    # user = session.query(User).filter(User.email == login_data.email).first()
    # hash_password = user.hash_password

    if not await authenitcate_user(login_data.email, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": login_data.email})
    return {"access_token": token, "token_type": "bearer"}



from fastapi.security import OAuth2PasswordRequestForm
@app.post("/token")
async def token(login_data: OAuth2PasswordRequestForm = Depends()):
    if not await authenitcate_user(login_data.username, login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
    
    token = create_access_token({"sub": login_data.username})
    return {"access_token": token, "token_type": "bearer"}







from fastapi import UploadFile, File
from app.models import Document

@app.post("/documents")
async def upload_document(current_user: User = Depends(get_current_user), file: UploadFile = File()):

    file_path = f"documents/{file.filename}"
    print("FILENAME:", file.filename)
    print("FILE PATH:", file_path)

    content = await file.read()

    response = supabase.storage.from_("Documents").upload(
            path=file_path,
            file=content,
            file_options={
                "content-type": file.content_type
            }
        )


    async with AsyncSessionLocal() as session:
        document = Document(
            filename=file.filename,
            file_url=file_path,
            created_at=datetime.now(timezone.utc),
            user_id= current_user.id
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)


        
    return {
        "document_id": document.id,
        "filename": file.filename,
        "path": file_path
    }




@app.post("/emedding")
async def main(document_id: int, current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        query = select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
        document = await session.scalar(query)
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        file_key = document.file_url
        filename = document.filename

    file_bytes = supabase.storage.from_("Documents").download(file_key)

    tmp_path = Path("tmp") / str(document_id) / filename
    tmp_path.parent.mkdir(exist_ok=True, parents=True)
    tmp_path.write_bytes(file_bytes)

    chunk_count = await control(
        tmp_path,
        user_id=current_user.id,
        document_id=document_id,
    )
    return {
        "document_id": document_id,
        "chunks_saved": chunk_count,
    }

from app.services.vector_search import search
from app.services.llm import ask
@app.get("/search")
async def search_handel(query: str , current_user: User = Depends(get_current_user)):
    userid = current_user.id 
    data = await search(query, userid)
    return ask(data, query)

  






    









    



    
    




