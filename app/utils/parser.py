from pathlib import Path
import fitz
import docx2txt


def extract_text(file_path: Path, mime: str) -> str:
    if mime == "application/pdf":
        with fitz.open(file_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    elif mime in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }:
        return docx2txt.process(file_path)
    else:
        return file_path.read_text(encoding="utf-8", errors="ignore")
