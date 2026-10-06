import asyncio
from sqlalchemy import delete
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from app.core.database import AsyncSessionLocal
from app.models import DocumentChunk
import os

embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def fileloader(file):
    loader = TextLoader(file)
    documents = loader.load()
    return documents  # document object



# make the chunks

def chunker(documents): 
    text_spliltter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)    # chunking object
    docs = text_spliltter.split_documents(documents)

    for i, chunk in enumerate(docs[:3], start=1):

        print(f"\nChunk {i}:\n{chunk.page_content}\n")

    return docs
    






async def save_embeddings(docs, *, user_id: int, document_id: int) -> int:
    if not docs:
        raise ValueError("Cannot save embeddings because the document has no text chunks.")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    contents = [chunk.page_content for chunk in docs]
    embeddings = await asyncio.to_thread(embedding_model.embed_documents, contents)

    chunks = [
        DocumentChunk(user_id=user_id, document_id=document_id, chunk_index=index, content=chunk.page_content, embedding=embedding, chunk_metadata=chunk.metadata,)   for index, (chunk, embedding) in enumerate(zip(docs, embeddings))
    ]

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(DocumentChunk).where(
                DocumentChunk.user_id == user_id,
                DocumentChunk.document_id == document_id,
            )
        )
        session.add_all(chunks)
        await session.commit()

    return len(chunks)



# ask questions



"""
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt
)

response.text
"""