import os
from typing import Any, Dict, List, Optional
from config.settings import settings
from utils.logger import logger


class GeminiAPIError(Exception):
    """Raised when communication with Google Gemini API fails."""
    pass


class GeminiService:
    """
    Client for Google Gemini API using the official `google-genai` SDK.
    Secures API credentials, handles rate limits, model fallback, and request timeouts.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_ms: int = 25000,
    ):
        self._api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout_ms = timeout_ms
        self._client = None

    def _get_client(self):
        """Initializes and returns the Google GenAI client."""
        if not self._api_key:
            raise GeminiAPIError(
                "GEMINI_API_KEY is not configured in .env. "
                "Please add `GEMINI_API_KEY=your_key_here` to your .env file."
            )

        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(
                    api_key=self._api_key,
                    http_options={"timeout": self.timeout_ms},
                )
            except ImportError:
                raise GeminiAPIError(
                    "The `google-genai` package is not installed. Run `pip install google-genai`."
                )
            except Exception as e:
                logger.error("Failed to initialize Google GenAI Client", exc_info=True)
                raise GeminiAPIError(f"Google GenAI Client initialization failed: {type(e).__name__}")

        return self._client

    @property
    def is_configured(self) -> bool:
        """Returns True if GEMINI_API_KEY is present."""
        return bool(self._api_key and self._api_key.strip())

    def check_health(self) -> Dict[str, Any]:
        """
        Validates authentication and model connectivity with Google Gemini API.
        Never logs or exposes the API key.
        """
        if not self.is_configured:
            return {
                "status": "missing_key",
                "configured_model": self.model,
                "is_available": False,
                "error": "GEMINI_API_KEY is missing from environment / .env",
            }

        try:
            client = self._get_client()
            # Fast test call with short prompt
            test_models = [self.model, "gemini-3.5-flash", "gemini-3.5-flash-lite"]
            last_err = None

            for m in test_models:
                try:
                    res = client.models.generate_content(
                        model=m,
                        contents="Ping",
                    )
                    if res and res.text:
                        return {
                            "status": "online",
                            "configured_model": self.model,
                            "active_model": m,
                            "is_available": True,
                            "error": None,
                        }
                except Exception as call_err:
                    last_err = call_err
                    # If 404 (model deprecated for new users), try next model
                    err_str = str(call_err)
                    if "404" in err_str or "NOT_FOUND" in err_str:
                        continue
                    else:
                        break

            return {
                "status": "error",
                "configured_model": self.model,
                "is_available": False,
                "error": f"API Error: {type(last_err).__name__} - {str(last_err)[:180]}",
            }

        except GeminiAPIError as ge:
            return {
                "status": "error",
                "configured_model": self.model,
                "is_available": False,
                "error": str(ge),
            }
        except Exception as e:
            return {
                "status": "error",
                "configured_model": self.model,
                "is_available": False,
                "error": f"{type(e).__name__}: {str(e)[:180]}",
            }

    @property
    def is_available(self) -> bool:
        """Quick check for API readiness."""
        health = self.check_health()
        return health.get("is_available", False)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> str:
        """
        Calls Gemini `generate_content` using the official `google-genai` SDK.
        Applies system instructions, parameters, and automatic fallback if the configured
        model name has been superseded by Google.
        """
        client = self._get_client()

        # Candidate models to try if the default returns a deprecation 404
        candidates = [self.model]
        if self.model != "gemini-3.5-flash":
            candidates.append("gemini-3.5-flash")
        if self.model != "gemini-3.5-flash-lite":
            candidates.append("gemini-3.5-flash-lite")

        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_prompt if system_prompt else None,
        )

        last_error = None
        for model_candidate in candidates:
            try:
                response = client.models.generate_content(
                    model=model_candidate,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text.strip()
                return "No text response received from Gemini API."
            except Exception as e:
                last_error = e
                err_msg = str(e)

                # Check for 404 model retirement: fallback to next candidate
                if "404" in err_msg or "NOT_FOUND" in err_msg:
                    logger.warning(
                        f"Gemini model '{model_candidate}' returned 404. Attempting fallback..."
                    )
                    continue

                # Check for Quota exhaustion (429)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    raise GeminiAPIError(
                        "Gemini API rate limit or quota exceeded (HTTP 429). "
                        "Please wait a moment before trying again."
                    )

                # Check for Auth errors (400, 403)
                if "API_KEY_INVALID" in err_msg or "PERMISSION_DENIED" in err_msg or "403" in err_msg:
                    raise GeminiAPIError(
                        "Gemini API authentication failed. Please verify that `GEMINI_API_KEY` in `.env` is valid."
                    )

                raise GeminiAPIError(f"Gemini API generation error: {type(e).__name__} - {err_msg[:200]}")

        raise GeminiAPIError(f"All Gemini model candidates failed: {last_error}")


# Global Gemini service singleton
gemini_service = GeminiService()
