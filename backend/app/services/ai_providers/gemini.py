"""Gemini AI Provider — V2 Priority 1.

Uses Google's Gemini API for AI-powered features.
Requires GEMINI_API_KEY environment variable.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional

from app.services.ai_providers.base import AIProvider, AIResponse

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_TIMEOUT = int(os.environ.get("GEMINI_TIMEOUT", "60"))


class GeminiProvider(AIProvider):
    """Google Gemini AI provider."""

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_available(self) -> bool:
        if not GEMINI_API_KEY:
            return False
        try:
            import google.generativeai as genai
            return True
        except ImportError:
            logger.warning("google-generativeai not installed")
            return False

    def chat(self, prompt: str, system: str = "", **kwargs) -> AIResponse:
        """Send a chat message to Gemini."""
        if not self.is_available:
            return AIResponse(
                provider=self.name,
                success=False,
                error="Gemini not configured (missing GEMINI_API_KEY or library)",
            )

        start = time.time()
        try:
            import google.generativeai as genai

            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name=kwargs.get("model", GEMINI_MODEL),
                system_instruction=system if system else None,
            )

            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 4096),
                ),
            )

            text = response.text or ""
            latency = (time.time() - start) * 1000

            return AIResponse(
                text=text,
                provider=self.name,
                model=kwargs.get("model", GEMINI_MODEL),
                latency_ms=latency,
                success=True,
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Gemini chat failed: {e}")
            return AIResponse(
                provider=self.name,
                model=kwargs.get("model", GEMINI_MODEL),
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
            response.error = "Failed to parse JSON from Gemini response"
            return response

        response.parsed_json = parsed
        return response

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that may contain markdown code fences."""
        try:
            # Try code fence
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Try raw JSON
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
        return None
