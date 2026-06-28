from __future__ import annotations

from backend.schemas.scheme import RetrievedChunk


def qa_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(
        f"[chunk:{chunk.id} page:{chunk.page_number} source:{chunk.document_name}]\n{chunk.text}"
        for chunk in chunks
    )
    return f"""You are Yojana Mitra, an offline assistant for government scheme documents.
Answer only from the provided context. Keep the answer concise.
If the answer is not present, say: Not enough information in the uploaded document.

Context:
{context}

Question: {question}
Answer:"""
