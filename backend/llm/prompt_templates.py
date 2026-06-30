from __future__ import annotations

from backend.localization.translator import language_name
from backend.schemas.scheme import RetrievedChunk


def scheme_extraction_prompt(text: str) -> str:
    return f"""You extract structured data from Indian Government scheme documents.

Return ONLY valid JSON with exactly these keys:
scheme_name, category, objective, benefits, eligibility, required_documents, application_process, faq.

Rules:
- Use only the document text.
- Use an empty string for missing text fields.
- Use an empty list for missing list fields.
- Keep list items concise.
- Do not include markdown.

Document text:
{text[:12000]}

JSON:
"""


def qa_prompt(
    question: str,
    chunks: list[RetrievedChunk],
    language: str = "en",
    intent: str = "",
) -> str:
    context = "\n\n".join(
        f"[chunk:{chunk.id} page:{chunk.page_number} section:{chunk.section_title or 'Unknown'} source:{chunk.document_name}]\n{chunk.text}"
        for chunk in chunks
    )

    answer_language = language_name(language)

    intent_rule = (
        f'- The detected question section is "{intent}". Answer only from chunks with that section.\n'
        if intent
        else ""
    )

    return f"""You are Yojana Mitra, an offline AI assistant for Indian Government Schemes.

Use ONLY the information provided in the context.

IMPORTANT RULES:
- Never use your own knowledge.
- Never guess or infer information.
- Answer ONLY using the provided context.
- If the answer is not explicitly present in the context, reply exactly:
  "Not enough information in the uploaded document."
- If the question is unrelated to the uploaded document, reply exactly:
  "This question is outside the scope of the uploaded document."
- If the retrieved context does not directly answer the question, do not attempt to answer.
- Answer ONLY what the user asked.
{intent_rule}- Ignore FAQ chunks unless the user explicitly asks an FAQ.
- If the user asks for eligibility, return ONLY the eligibility criteria.
- If the user asks for required documents, return ONLY the required documents.
- If the user asks for benefits, return ONLY the benefits.
- If the user asks for the application process, return ONLY the application process.
- If the user asks for the objective, return ONLY the objective.
- Do NOT include unrelated sections.
- Preserve bullet points if they exist in the context.
- Do not summarize the entire document.

Section-specific instructions:

If the user asks for eligibility criteria:
- Return only the text under the "Eligibility" heading.
- Stop when the next heading begins (such as "Required Documents", "Benefits", or "Application Process").

If the user asks for required documents:
- Return only the text under the "Required Documents" heading.
- Stop when the next heading begins.

Never include other sections.

Answer in {answer_language}.

Context:
{context}

Question:
{question}

Answer:
"""