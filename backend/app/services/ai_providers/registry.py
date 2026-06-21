"""AI Provider Registry — fallback chain.

Fallback order: Gemini → DeepSeek → Error
"""

import logging
from typing import Optional

from app.services.ai_providers.base import AIProvider, AIResponse
from app.services.ai_providers.gemini import GeminiProvider
from app.services.ai_providers.deepseek import DeepSeekProvider

logger = logging.getLogger(__name__)

# Singleton instances
_gemini: Optional[GeminiProvider] = None
_deepseek: Optional[DeepSeekProvider] = None


def _get_gemini() -> GeminiProvider:
    global _gemini
    if _gemini is None:
        _gemini = GeminiProvider()
    return _gemini


def _get_deepseek() -> DeepSeekProvider:
    global _deepseek
    if _deepseek is None:
        _deepseek = DeepSeekProvider()
    return _deepseek


def get_provider(name: str) -> Optional[AIProvider]:
    """Get a specific AI provider by name."""
    providers = {
        "gemini": _get_gemini(),
        "deepseek": _get_deepseek(),
    }
    return providers.get(name.lower())


def get_fallback_provider() -> Optional[AIProvider]:
    """Get the first available provider in fallback order."""
    for provider in [_get_gemini(), _get_deepseek()]:
        if provider.is_available:
            return provider
    return None


def chat_with_fallback(
    prompt: str,
    system: str = "",
    preferred_provider: Optional[str] = None,
    **kwargs,
) -> AIResponse:
    """Chat with automatic fallback: Gemini → DeepSeek → Error.

    Args:
        prompt: The user prompt.
        system: System instruction.
        preferred_provider: Try this provider first if specified.
        **kwargs: Additional parameters (temperature, max_tokens, model).

    Returns:
        AIResponse from the first successful provider.
    """
    providers = []

    if preferred_provider:
        p = get_provider(preferred_provider)
        if p and p.is_available:
            providers.append(p)

    # Add remaining providers in fallback order
    for p in [_get_gemini(), _get_deepseek()]:
        if p not in providers and p.is_available:
            providers.append(p)

    if not providers:
        return AIResponse(
            text="",
            provider="none",
            success=False,
            error="No AI providers available. Set GEMINI_API_KEY or DEEPSEEK_API_KEY.",
        )

    last_error = None
    for provider in providers:
        logger.info(f"Trying AI provider: {provider.name}")
        response = provider.chat(prompt, system=system, **kwargs)
        if response.success:
            logger.info(f"AI provider {provider.name} succeeded in {response.latency_ms:.0f}ms")
            return response
        last_error = response.error
        logger.warning(f"AI provider {provider.name} failed: {response.error}")

    return AIResponse(
        text="",
        provider="none",
        success=False,
        error=f"All AI providers failed. Last error: {last_error}",
    )


def chat_json_with_fallback(
    prompt: str,
    system: str = "",
    preferred_provider: Optional[str] = None,
    **kwargs,
) -> AIResponse:
    """Chat with JSON parsing and automatic fallback."""
    providers = []

    if preferred_provider:
        p = get_provider(preferred_provider)
        if p and p.is_available:
            providers.append(p)

    for p in [_get_gemini(), _get_deepseek()]:
        if p not in providers and p.is_available:
            providers.append(p)

    if not providers:
        return AIResponse(
            text="",
            provider="none",
            success=False,
            error="No AI providers available.",
        )

    last_error = None
    for provider in providers:
        logger.info(f"Trying AI provider (JSON): {provider.name}")
        response = provider.chat_json(prompt, system=system, **kwargs)
        if response.success:
            logger.info(f"AI provider {provider.name} JSON succeeded")
            return response
        last_error = response.error
        logger.warning(f"AI provider {provider.name} failed: {response.error}")

    return AIResponse(
        text="",
        provider="none",
        success=False,
        error=f"All AI providers failed. Last error: {last_error}",
    )
