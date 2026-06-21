"""AI Provider Abstraction Layer — V2.

Provides a unified interface for AI providers (Gemini, DeepSeek).
Fallback chain: Gemini → DeepSeek → Error Report
"""

from app.services.ai_providers.base import AIProvider, AIResponse
from app.services.ai_providers.registry import get_provider, get_fallback_provider, chat_with_fallback

__all__ = [
    "AIProvider",
    "AIResponse",
    "get_provider",
    "get_fallback_provider",
    "chat_with_fallback",
]
