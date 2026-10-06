from .document_phraser import phraser
from pathlib import Path
from app.vector import chunker





def make_chunks(documents):
    print("chunk running")
    docs = chunker(documents)
    return docs






