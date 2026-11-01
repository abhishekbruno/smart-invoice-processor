import pytest
from unittest.mock import MagicMock
from core.gemini_service import GeminiAPIError
from core.rag_pipeline import RAGPipeline
from utils.helpers import get_relative_date_range


class MockGeminiOnline:
    @property
    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        return "Based on the invoice excerpts, AWS billed for EC2 instances and S3 storage amounting to $793.80."


class MockGeminiOffline:
    @property
    def is_available(self) -> bool:
        return False

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        raise GeminiAPIError("Gemini API is unavailable or quota exceeded.")


def test_rag_pipeline_sql_routing():
    pipeline = RAGPipeline()
    response = pipeline.answer_query("What did we spend on AWS?")
    assert response.query_type == "sql"
    assert not response.is_llm_generated
    assert "Amazon Web Services" in response.answer or "AWS" in response.answer
    assert len(response.sources) >= 1


def test_rag_pipeline_online_llm():
    mock_llm = MockGeminiOnline()
    pipeline = RAGPipeline(llm=mock_llm)

    response = pipeline.answer_query("What services did AWS charge us for?")
    assert response.query_type == "rag"
    assert response.is_llm_generated
    assert "EC2" in response.answer or "S3" in response.answer
    assert len(response.sources) >= 1

    # Verify citation fields
    top_citation = response.sources[0]
    assert top_citation.filename != ""
    assert top_citation.page_number >= 1
    assert top_citation.snippet != ""


def test_rag_pipeline_offline_llm_fallback():
    mock_llm = MockGeminiOffline()
    pipeline = RAGPipeline(llm=mock_llm)

    response = pipeline.answer_query("Explain what services Google Cloud billed for.")
    assert response.query_type == "rag"
    assert not response.is_llm_generated
    # Fallback message includes structured excerpts
    assert "Relevant Invoice Information Found" in response.answer or "Google Cloud" in response.answer
    assert len(response.sources) >= 1


def test_rag_pipeline_missing_information():
    # Search for non-existent company
    mock_llm = MockGeminiOnline()
    mock_vstore = MagicMock()
    mock_vstore.search.return_value = []

    pipeline = RAGPipeline(llm=mock_llm, vstore=mock_vstore)
    response = pipeline.answer_query("What did NonExistentFictionalCo bill us for?")
    assert "could not find any relevant invoice" in response.answer.lower()
    assert len(response.sources) == 0


def test_relative_date_ranges():
    # Test timezone-aware relative date parsing
    start, end, desc = get_relative_date_range("What did we spend last month?")
    assert start is not None
    assert end is not None
    assert "Last Month" in desc

    start_q, end_q, desc_q = get_relative_date_range("spending in last quarter")
    assert start_q is not None
    assert end_q is not None
    assert "Quarter" in desc_q

    start_2024, end_2024, desc_2024 = get_relative_date_range("invoices in 2024")
    assert start_2024 == "2024-01-01"
    assert end_2024 == "2024-12-31"

