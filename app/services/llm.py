# app/services/llm.py
from ollama import AsyncClient
from langchain.text_splitter import RecursiveCharacterTextSplitter

client = AsyncClient(host="http://localhost:11434")

SYSTEM_PROMPT = """
You are LegalLens AI, an assistant who explains legal documents.
Respond in plain English. No special formatting is required.
"""


def split_text(text: str, chunk_size=2_000, overlap=300) -> list[str]:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    ).split_text(text)


async def analyze_text(text: str) -> str:
    context = "\n---\n".join(split_text(text)[:3])
    prompt = f"{SYSTEM_PROMPT}\n\n[Document]\n{context}\n"
    resp = await client.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2, "num_predict": 600},
    )
    return resp["message"]["content"]
