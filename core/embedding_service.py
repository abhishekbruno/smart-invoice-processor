import threading
from typing import Any, List, Optional, Union
from config.settings import settings
from utils.logger import logger


class EmbeddingService:
    """
    Local embedding service powered by Sentence Transformers.
    Runs completely on local CPU/device without paid APIs or cloud dependencies.
    Lazy-loads and caches the model to avoid re-initialization overhead.
    """

    _instance: Optional["EmbeddingService"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name: Optional[str] = None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None
        self._load_lock = threading.Lock()
        self._dimension = 384  # Default for all-MiniLM-L6-v2
        self._initialized = True

    @property
    def is_loaded(self) -> bool:
        """Returns True if the underlying model is already loaded in memory."""
        return self._model is not None

    @property
    def dimension(self) -> int:
        """Returns the embedding vector dimension."""
        return self._dimension

    def _ensure_model_loaded(self) -> None:
        """Loads the SentenceTransformer model in a thread-safe manner if not loaded."""
        if self._model is None:
            with self._load_lock:
                if self._model is None:
                    try:
                        logger.info(f"Loading local embedding model: '{self.model_name}' on CPU...")
                        from sentence_transformers import SentenceTransformer

                        # Force CPU execution for maximum compatibility
                        self._model = SentenceTransformer(self.model_name, device="cpu")
                        test_emb = self._model.encode(["test"], convert_to_numpy=True)
                        self._dimension = int(test_emb.shape[1])
                        logger.info(
                            f"Embedding model '{self.model_name}' successfully initialized (dim={self._dimension})."
                        )
                    except Exception as e:
                        logger.error(f"Failed to load embedding model '{self.model_name}': {e}", exc_info=True)
                        raise RuntimeError(
                            f"Could not load SentenceTransformer model '{self.model_name}': {str(e)}"
                        )

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generates dense vector embeddings for a list of text strings.
        Safely handles empty lists and empty strings.
        """
        if not texts:
            return []

        self._ensure_model_loaded()

        # Sanitize texts (replace empty or pure whitespace strings with a placeholder)
        sanitized = [t.strip() if t and t.strip() else "[EMPTY]" for t in texts]

        try:
            embeddings = self._model.encode(
                sanitized,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings for {len(texts)} texts: {e}", exc_info=True)
            raise

    def embed_query(self, query: str) -> List[float]:
        """Generates embedding for a single query string."""
        if not query or not query.strip():
            return [0.0] * self._dimension

        results = self.embed_texts([query])
        return results[0] if results else [0.0] * self._dimension


try:
    from chromadb import Documents, EmbeddingFunction, Embeddings
except ImportError:
    EmbeddingFunction = object  # type: ignore
    Documents = Any  # type: ignore
    Embeddings = Any  # type: ignore


class LocalChromaEmbeddingFunction(EmbeddingFunction[Documents]):
    """Adapter for ChromaDB embedding function interface."""

    def __init__(self, service: Optional[EmbeddingService] = None):
        self.service = service or EmbeddingService()

    @staticmethod
    def name() -> str:
        return "local_sentence_transformers"

    def get_config(self) -> dict:
        return {"model_name": self.service.model_name}

    @classmethod
    def build_from_config(cls, config: dict):
        return cls(EmbeddingService(model_name=config.get("model_name")))

    def __call__(self, input: Documents) -> Embeddings:
        if isinstance(input, str):
            input = [input]
        return self.service.embed_texts(input)

    def embed_query(self, input: Union[str, List[str]]) -> List[List[float]]:
        if isinstance(input, str):
            input = [input]
        return self.service.embed_texts(input)

    def embed_documents(self, input: List[str]) -> List[List[float]]:
        return self.service.embed_texts(input)


# Global embedding service singleton
embedding_service = EmbeddingService()
