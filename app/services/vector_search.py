from app.vector import embedding_model
from app.models import DocumentChunk
from sqlalchemy import select
from ..core.database import AsyncSessionLocal

async def search(query, user_id):
    embedding_query = embedding_model.embed_query(query)
    distance = DocumentChunk.embedding.cosine_distance(embedding_query)

    stmt = (
        select(DocumentChunk, distance.label("distance"))
        .where(DocumentChunk.user_id == user_id)
        .order_by(distance)
        .limit(2)
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(stmt)
        rows =  result.all()  # roes has chunk object and distacne

            
    data = [{"content": chunk.content} for chunk, distance in rows]
    return data
    