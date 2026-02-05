"""External service integrations"""

from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.external.clip_client import CLIPEmbeddingClient

__all__ = ["OpenAIClient", "CLIPEmbeddingClient"]
