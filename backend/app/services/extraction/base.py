"""Base extractor interface."""

from abc import ABC, abstractmethod
from app.services.extraction.report import ExtractionResult


class BaseExtractor(ABC):
    """Abstract base class for all document extractors."""

    @abstractmethod
    def extract(self, file_path: str) -> ExtractionResult:
        """Extract structured data from a document file."""
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return list of supported file extensions."""
        ...
