from backend.schemas.scheme import Chunk, DocumentRecord, Scheme
from backend.storage.db_manager import DatabaseManager
from backend.storage.repository import Repository


def test_repository_round_trip(tmp_path):
    repo = Repository(DatabaseManager(tmp_path / "test.sqlite3"))
    document_id = repo.create_document(
        DocumentRecord(
            filename="sample.pdf",
            file_path=str(tmp_path / "sample.pdf"),
            file_type="pdf",
            checksum="abc123",
        )
    )
    scheme_id = repo.save_scheme(document_id, Scheme(scheme_name="Sample Scheme"))
    chunk_ids = repo.insert_chunks(
        [Chunk(document_id=document_id, text="Eligibility income below Rs 200000")]
    )

    assert document_id > 0
    assert scheme_id > 0
    assert chunk_ids[0] > 0
    assert repo.get_chunks(document_id)[0].text.startswith("Eligibility")
