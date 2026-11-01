import pytest
from pathlib import Path
from core.vector_store import VectorStore


@pytest.fixture
def temp_vector_store(tmp_path):
    chroma_path = tmp_path / "chroma_test"
    # Create isolated vector store instance
    vstore = VectorStore.__new__(VectorStore)
    vstore.chroma_dir = chroma_path
    vstore.collection_name = "test_collection"
    vstore._client = None
    vstore._collection = None
    import threading
    vstore._init_lock = threading.Lock()
    return vstore


def test_vector_store_indexing_and_search(temp_vector_store):
    sample_inv = {
        "id": 999,
        "invoice_number": "TEST-VEC-101",
        "vendor_name": "CyberShield Defense",
        "total_amount": 1200.0,
        "currency": "EUR",
        "file_hash": "hash999abcdef0123456789",
        "source_file_path": "cyber_test.pdf",
        "line_items": [
            {"description": "Penetration testing services", "quantity": 1.0, "unit_price": 1200.0, "amount": 1200.0}
        ],
        "raw_text": "CyberShield Defense security audit and penetration testing report.",
    }

    count = temp_vector_store.index_invoice(sample_inv)
    assert count >= 1

    stats = temp_vector_store.get_stats()
    assert stats["total_chunks"] == count
    assert 999 in stats["indexed_invoice_ids"]

    # Search
    hits = temp_vector_store.search("penetration testing audit", n_results=3)
    assert len(hits) >= 1
    assert "CyberShield" in hits[0]["content"] or "Penetration" in hits[0]["content"]
    assert hits[0]["metadata"]["invoice_id"] == 999


def test_vector_store_idempotent_reindex(temp_vector_store):
    sample_inv = {
        "id": 888,
        "invoice_number": "TEST-IDEMPOTENT",
        "vendor_name": "Idempotent Corp",
        "total_amount": 50.0,
        "currency": "USD",
        "file_hash": "hash888_test_unique",
        "source_file_path": "idem.pdf",
        "line_items": [],
        "raw_text": "Testing idempotency of vector store indexing.",
    }

    # Index once
    cnt1 = temp_vector_store.index_invoice(sample_inv)
    stats1 = temp_vector_store.get_stats()

    # Index again with modified amount
    sample_inv["total_amount"] = 75.0
    cnt2 = temp_vector_store.index_invoice(sample_inv)
    stats2 = temp_vector_store.get_stats()

    # Chunks count should stay the same (not duplicate)
    assert stats2["total_chunks"] == stats1["total_chunks"]


def test_vector_store_deletion(temp_vector_store):
    sample_inv = {
        "id": 777,
        "invoice_number": "TEST-DEL",
        "vendor_name": "Deletable Corp",
        "total_amount": 30.0,
        "currency": "USD",
        "file_hash": "hash777_to_delete",
        "source_file_path": "del.pdf",
        "line_items": [],
        "raw_text": "To be deleted soon.",
    }

    temp_vector_store.index_invoice(sample_inv)
    assert temp_vector_store.get_stats()["total_chunks"] > 0

    deleted_cnt = temp_vector_store.delete_by_invoice_id(777)
    assert deleted_cnt > 0
    assert temp_vector_store.get_stats()["total_chunks"] == 0

