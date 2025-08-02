import json
from typing import TypedDict
from ollama import AsyncClient
from langchain.text_splitter import RecursiveCharacterTextSplitter

client = AsyncClient(host="http://localhost:11434")

# 💡 Подробный system prompt для юридического ассистента
SYSTEM_PROMPT = """
You are a legal assistant and an expert in analyzing legal and contractual documents.

Your task is to review the following text (which may be a contract, offer, agreement, NDA, power of attorney, or other legal form) and extract the most important legal insights.

Please:
1. Identify the general purpose of the document — what it is and what it's about.
2. Extract key terms: parties, subject matter, duration, obligations, penalties, etc.
3. Highlight any legal risks or potentially unfavorable clauses:
   — automatic renewal,
   — penalties or fines,
   — unilateral termination,
   — vague or one-sided provisions.
4. If the document is incomplete or unreadable, state that clearly.

Respond in strict JSON format with the following fields:
- summary: brief description of the document (string)
- risks: list of legal risks (list of strings)
- notes: other relevant comments or issues (list of strings)
    """


class InsightJSON(TypedDict):
    summary: str
    risks: list[str]
    notes: list[str]


def split_text(text: str, chunk_size=2000, overlap=300) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_text(text)


async def analyze_text(text: str) -> InsightJSON:
    chunks = split_text(text)
    context = "\n\n---\n\n".join(chunks[:3])  # максимум 3 чанка

    prompt = f"{SYSTEM_PROMPT}\n\n[Contract Begins]\n{context}\n\n[Contract Ends]"

    response = await client.chat(
        model="llama3", messages=[{"role": "user", "content": prompt}]
    )

    try:
        content = response["message"]["content"]
        data = json.loads(content)

        # 🛡️ Безопасная обработка случая, если список пришёл как строка
        if isinstance(data.get("risks"), str):
            data["risks"] = json.loads(data["risks"])
        if isinstance(data.get("notes"), str):
            data["notes"] = json.loads(data["notes"])

        return data
    except Exception as e:
        print("❌ Error parsing response:", e)
        print("📄 Raw:", response["message"]["content"])
        raise
