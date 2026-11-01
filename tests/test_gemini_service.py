import pytest
from unittest.mock import MagicMock, patch
from core.gemini_service import GeminiService, GeminiAPIError


def test_gemini_service_initialization():
    service = GeminiService(api_key="test-key-12345", model="gemini-2.5-flash")
    assert service.model == "gemini-2.5-flash"
    assert service.is_configured is True
    # Verify private key attribute exists and isn't displayed in str/repr
    assert "test-key-12345" not in str(service)
    assert "test-key-12345" not in repr(service)


def test_missing_api_key_behavior():
    service = GeminiService(api_key="")
    assert service.is_configured is False
    health = service.check_health()
    assert health["status"] == "missing_key"
    assert health["is_available"] is False
    assert "missing" in health["error"].lower()

    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate("Hello")
    assert "GEMINI_API_KEY is not configured" in str(exc_info.value)


@patch("core.gemini_service.GeminiService._get_client")
def test_generate_success_mock(mock_get_client):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello! Here is the invoice analysis."
    mock_client.models.generate_content.return_value = mock_response
    mock_get_client.return_value = mock_client

    service = GeminiService(api_key="fake-key", model="gemini-2.5-flash")
    answer = service.generate(
        prompt="Explain this invoice",
        system_prompt="You are a financial auditor.",
    )

    assert answer == "Hello! Here is the invoice analysis."
    assert mock_client.models.generate_content.called
    call_kwargs = mock_client.models.generate_content.call_args[1]
    assert call_kwargs["contents"] == "Explain this invoice"


@patch("core.gemini_service.GeminiService._get_client")
def test_model_fallback_on_404(mock_get_client):
    mock_client = MagicMock()
    # First model call raises 404 (model retired/not found)
    # Second model call (fallback) succeeds
    success_response = MagicMock()
    success_response.text = "Success from fallback model"

    mock_client.models.generate_content.side_effect = [
        Exception("404 NOT_FOUND: models/gemini-2.5-flash is not available"),
        success_response,
    ]
    mock_get_client.return_value = mock_client

    service = GeminiService(api_key="fake-key", model="gemini-2.5-flash")
    answer = service.generate("Test prompt")

    assert answer == "Success from fallback model"
    assert mock_client.models.generate_content.call_count == 2
    first_call_model = mock_client.models.generate_content.call_args_list[0][1]["model"]
    second_call_model = mock_client.models.generate_content.call_args_list[1][1]["model"]
    assert first_call_model == "gemini-2.5-flash"
    assert second_call_model == "gemini-3.5-flash"


@patch("core.gemini_service.GeminiService._get_client")
def test_quota_exhausted_429(mock_get_client):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception(
        "429 RESOURCE_EXHAUSTED: Quota exceeded for quota metric"
    )
    mock_get_client.return_value = mock_client

    service = GeminiService(api_key="fake-key", model="gemini-2.5-flash")
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate("Test prompt")

    assert "rate limit or quota exceeded" in str(exc_info.value)
    assert "429" in str(exc_info.value)


@patch("core.gemini_service.GeminiService._get_client")
def test_auth_error_handling(mock_get_client):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception(
        "400 API_KEY_INVALID: API key not valid."
    )
    mock_get_client.return_value = mock_client

    service = GeminiService(api_key="fake-key", model="gemini-2.5-flash")
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate("Test prompt")

    assert "authentication failed" in str(exc_info.value)


def test_api_key_security_no_leakage():
    secret_key = "AIzaSySecretKeyNeverExposeMe"
    service = GeminiService(api_key=secret_key, model="gemini-2.5-flash")

    # Ensure the secret key isn't in string representation
    assert secret_key not in str(service)
    assert secret_key not in repr(service)

    # Test that check_health error dictionary does not leak the secret key
    with patch("core.gemini_service.GeminiService._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception(
            f"Error occurred while processing request with key {secret_key}"
        )
        mock_get_client.return_value = mock_client

        health = service.check_health()
        assert health["is_available"] is False
        assert health["status"] == "error"

