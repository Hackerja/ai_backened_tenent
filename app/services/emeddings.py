from .chunky import make_chunks
from . document_phraser import phraser
from pathlib import Path

from app.vector import save_embeddings


async def control(file, *, user_id: int, document_id: int) -> int:
    file = Path(file)
    documents = phraser(file)
    docs = make_chunks(documents)
    return await save_embeddings(
        docs,
        user_id=user_id,
        document_id=document_id,
    )


