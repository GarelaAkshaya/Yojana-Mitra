from backend.ingestion.pdf_extractor import PageText, RawTextResult
from backend.structuring.chunker import chunk_text


def test_chunk_text_keeps_government_scheme_sections_separate():
    raw = RawTextResult(
        text="",
        pages=[
            PageText(
                page_number=1,
                text="""
                Benefits
                - Rs 6000 per year

                Eligibility
                - Small and marginal farmers
                - Land records are required

                FAQs
                Q. What if payment fails?
                A. Contact the bank.
                """,
            )
        ],
        extraction_method="native_pdf",
    )

    chunks = chunk_text(raw, document_id=1)
    sections = [chunk.section_title for chunk in chunks]

    assert "Benefits" in sections
    assert "Eligibility" in sections
    assert "FAQs" in sections
    eligibility_chunk = next(chunk for chunk in chunks if chunk.section_title == "Eligibility")
    assert "Small and marginal farmers" in eligibility_chunk.text
    assert "payment fails" not in eligibility_chunk.text
