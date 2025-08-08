from typing import Iterable, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ollama import Client
from app.core.config import get_settings

settings = get_settings()
client = Client(host=settings.ollama_url)

EMBED_MODEL = "nomic-embed-text"


def split_for_indexing(
    text: str, chunk_size: int = 1200, overlap: int = 200
) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def embed(text: str) -> List[float]:
    res = client.embeddings(model=EMBED_MODEL, prompt=text)
    return res["embedding"]


def embed_batch(texts: Iterable[str]) -> list[list[float]]:
    return [embed(t) for t in texts]
