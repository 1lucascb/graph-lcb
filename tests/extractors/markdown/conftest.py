"""Reusable fixtures for extractor and extraction-contract tests."""

from collections.abc import Callable
from pathlib import Path

import pytest

from graph_lcb.extractors.base.contracts import Entity, Relationship
from graph_lcb.extractors.languages.markdown.extractor import MarkdownExtractor


@pytest.fixture
def markdown_extractor() -> MarkdownExtractor:
    return MarkdownExtractor()


@pytest.fixture
def write_markdown(tmp_path: Path) -> Callable[[str, str], Path]:
    """Write a Markdown file under the test root, creating parent directories."""
    def write(relative_path: str, content: str) -> Path:
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    return write


@pytest.fixture
def read_jsonl() -> Callable[[Path], list[dict]]:
    """Read JSON Lines records into plain dictionaries."""
    import json

    def read(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    return read


@pytest.fixture
def make_entity() -> Callable[..., Entity]:
    def make(**overrides: object) -> Entity:
        values = {"id": "FILE:README.md", "kind": "FILE", "name": "README.md", "file": "README.md"}
        values.update(overrides)
        return Entity(**values)

    return make


@pytest.fixture
def make_relationship() -> Callable[..., Relationship]:
    def make(**overrides: object) -> Relationship:
        values = {
            "source": "FILE:README.md",
            "target": "FILE:docs/guide.md",
            "kind": "REFERENCES",
            "file": "README.md",
        }
        values.update(overrides)
        return Relationship(**values)

    return make
