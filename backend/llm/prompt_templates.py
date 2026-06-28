from __future__ import annotations

from backend.localization.translator import language_name
from backend.schemas.scheme import RetrievedChunk


def qa_prompt(question: str, chunks: list[RetrievedChunk], language: str = "en") -> str:
    context = "\n\n".join(
        f"[chunk:{chunk.id} page:{chunk.page_number} source:{chunk.document_name}]\n{chunk.text}"
        for chunk in chunks
    )
    answer_language = language_name(language)
    return f"""You are Yojana Mitra, an offline assistant for government scheme documents.
Answer only from the provided context. Keep the answer concise.
Answer in {answer_language}.
If the answer is not present, say: Not enough information in the uploaded document.

Context:
{context}

Question: {question}
Answer:"""
