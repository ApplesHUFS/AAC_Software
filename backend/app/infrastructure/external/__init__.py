"""External service integrations"""

from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.external.embedding_client import EmbeddingClient

__all__ = ["OpenAIClient", "EmbeddingClient"]
