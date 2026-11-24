from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path

from graph_lcb.extractors.base.contracts import ExtractionRecord

class ExtractorBase(ABC):
    version = "1.0.0"
    detected_languages: tuple[str, ...] = ()

    @abstractmethod
    def extract(self, root_path: Path) -> Iterator[ExtractionRecord]:
        ...

