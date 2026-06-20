"""Standalone Ollama service for AI-powered features.

Provides a reusable interface for calling Ollama models.
Used by: reviewer (LLM review), structure (NLP classification), etc.
"""
import os
import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))


def is_available() -> bool:
    """Check if Ollama server is reachable and has models."""
    try:
        import ollama
        client = ollama.Client(host=OLLAMA_BASE_URL, timeout=10)
        client.list()
        return True
    except Exception:
        return False


def chat(prompt: str, system: str = "", model: Optional[str] = None) -> Optional[str]:
    """Send a chat message to Ollama and return the response text."""
    try:
        import ollama
        client = ollama.Client(host=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat(model=model or OLLAMA_MODEL, messages=messages)
        return response["message"]["content"]
    except Exception as e:
        logger.warning(f"Ollama chat failed: {e}")
        return None


def chat_json(prompt: str, system: str = "", model: Optional[str] = None) -> Optional[Dict]:
    """Send a chat message and parse the JSON response."""
    text = chat(prompt, system=system, model=model)
    if not text:
        return None
    return extract_json(text)


def extract_json(text: str) -> Optional[Dict]:
    """Extract JSON from text that may contain markdown code fences."""
    try:
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        pass
    return None
