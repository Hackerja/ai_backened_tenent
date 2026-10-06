from pathlib import Path
from app.vector import fileloader
from langchain_community.document_loaders import PyPDFLoader


def phraser(file):
    if file.suffix.lower() == ".txt":
        return fileloader(file)

    elif file.suffix.lower() == ".pdf":
        return PyPDFLoader(str(file)).load()

    else:
        raise ValueError("Format is not correct")






        




