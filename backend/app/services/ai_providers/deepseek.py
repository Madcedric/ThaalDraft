"""DeepSeek AI Provider — V2 Priority 2.

Uses DeepSeek API for AI-powered features.
Requires DEEPSEEK_API_KEY environment variable.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional

from app.services.ai_providers.base import AIProvider, AIResponse

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_TIMEOUT = int(os.environ.get("DEEPSEEK_TIMEOUT", "60"))


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider (OpenAI-compatible API)."""

    @property
    def name(self) -> str:
        return "deepseek"

    @property
    def is_available(self) -> bool:
        if not DEEPSEEK_API_KEY:
            return False
        try:
            import openai
            return True
        except ImportError:
            logger.warning("openai library not installed")
            return False

    def chat(self, prompt: str, system: str = "", **kwargs) -> AIResponse:
        """Send a chat message to DeepSeek."""
        if not self.is_available:
            return AIResponse(
                provider=self.name,
                success=False,
                error="DeepSeek not configured (missing DEEPSEEK_API_KEY or library)",
            )

        start = time.time()
        try:
            import openai

            client = openai.OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL,
                timeout=DEEPSEEK_TIMEOUT,
            )

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=kwargs.get("model", DEEPSEEK_MODEL),
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096),
            )

            text = response.choices[0].message.content or ""
            latency = (time.time() - start) * 1000
            tokens = response.usage.total_tokens if response.usage else 0

            return AIResponse(
                text=text,
                provider=self.name,
                model=kwargs.get("model", DEEPSEEK_MODEL),
                tokens_used=tokens,
                latency_ms=latency,
                success=True,
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"DeepSeek chat failed: {e}")
            return AIResponse(
                provider=self.name,
                model=kwargs.get("model", DEEPSEEK_MODEL),
                latency_ms=latency,
                success=False,
                error=str(e),
            )

    def chat_json(self, prompt: str, system: str = "", **kwargs) -> AIResponse:
        """Send a chat message and parse JSON response."""
        response = self.chat(prompt, system=system, **kwargs)
        if response.failed:
            return response

        parsed = self._extract_json(response.text)
        if parsed is None:
            response.success = False
            response.error = "Failed to parse JSON from DeepSeek response"
            return response

        response.parsed_json = parsed
        return response

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that may contain markdown code fences."""
        try:
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
        return None
