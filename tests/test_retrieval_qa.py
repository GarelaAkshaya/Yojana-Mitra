from backend.retrieval.hybrid_search import rebuild_vector_index
from backend.pipeline.qa_pipeline import run_qa_pipeline
from backend.schemas.scheme import Chunk, DocumentRecord, Scheme
from backend.storage.db_manager import DatabaseManager
from backend.storage.repository import Repository


def test_qa_pipeline_returns_grounded_fallback(tmp_path):
    repo = Repository(DatabaseManager(tmp_path / "test.sqlite3"))
    document_id = repo.create_document(
        DocumentRecord(filename="scheme.txt", file_path="scheme.txt", file_type="txt", checksum="qa123")
    )
    repo.save_scheme(document_id, Scheme(scheme_name="Income Support"))
    repo.insert_chunks([Chunk(document_id=document_id, text="Eligibility: Annual income below Rs 200000.")])
    rebuild_vector_index(repo)

    result = run_qa_pipeline("Who is eligible?", document_id=document_id, repo=repo)

    assert "income" in result.answer.lower()
    assert result.confidence > 0
