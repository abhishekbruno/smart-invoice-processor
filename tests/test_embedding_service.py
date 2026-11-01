import pytest
from core.embedding_service import EmbeddingService, LocalChromaEmbeddingFunction


def test_embedding_service_dimensions():
    service = EmbeddingService()
    assert service.dimension == 384


def test_embed_texts_and_query():
    service = EmbeddingService()
    texts = ["Invoice from Amazon Web Services for cloud servers.", "Office supplies expense receipt."]
    embeddings = service.embed_texts(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
    assert isinstance(embeddings[0][0], float)

    # Test single query embedding
    q_emb = service.embed_query("AWS cloud servers")
    assert len(q_emb) == 384


def test_embed_empty_input_handled_safely():
    service = EmbeddingService()
    assert service.embed_texts([]) == []

    # Empty text string
    res = service.embed_texts(["", "   "])
    assert len(res) == 2
    assert len(res[0]) == 384


def test_chroma_adapter():
    service = EmbeddingService()
    adapter = LocalChromaEmbeddingFunction(service)
    assert adapter.name() == "local_sentence_transformers"
    embs = adapter(["Sample document snippet"])
    assert len(embs) == 1
    assert len(embs[0]) == 384

