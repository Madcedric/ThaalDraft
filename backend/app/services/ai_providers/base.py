"""Base AI Provider — abstract interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AIResponse:
    """Standardized response from any AI provider."""
    text: str = ""
    parsed_json: Optional[Dict[str, Any]] = None
    provider: str = ""
    model: str = ""
    tokens_used: int = 0
    latency_ms: float = 0
    success: bool = True
    error: Optional[str] = None

    @property
    def failed(self) -> bool:
        return not self.success or self.error is not None


class AIProvider(ABC):
    """Abstract base class for all AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'gemini', 'deepseek')."""
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and reachable."""
        ...

    @abstractmethod
    def chat(self, prompt: str, system: str = "", **kwargs) -> AIResponse:
        """Send a chat message and return a response."""
        ...

    @abstractmethod
    def chat_json(self, prompt: str, system: str = "", **kwargs) -> AIResponse:
        """Send a chat message and parse the JSON response."""
        ...
