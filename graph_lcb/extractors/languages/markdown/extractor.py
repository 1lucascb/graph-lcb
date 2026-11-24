
import re
from pathlib import Path
from collections.abc import Iterator

from graph_lcb.extractors.base.contracts import (
    Entity,
    Relationship,
    ExtractionRecord,
)
from graph_lcb.extractors.base.extractor import ExtractorBase


LINK_PATTERN = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
URL_PATTERN = re.compile(r"\bhttps?://[^\s<>()\]]+", re.IGNORECASE)
URL_TRAILING_PUNCTUATION = ".,;:!?\"'"


class MarkdownExtractor(ExtractorBase):
    detected_languages = ("markdown",)

    def extract(self, root_path: Path) -> Iterator[ExtractionRecord]:
        root_path = root_path.resolve()

        markdown_files = sorted(
            path for path in root_path.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".markdown"}
            and ".graph" not in path.relative_to(root_path).parts
        )
        for file_path in markdown_files:
            relative_path = file_path.relative_to(root_path).as_posix()

            source_id = f"FILE:{relative_path}"

            yield Entity(
                id=source_id,
                kind="FILE",
                name=file_path.name,
                file=relative_path,
                metadata={
                    "format": "markdown",
                },
            )

            content = file_path.read_text(encoding="utf-8")
            markdown_link_spans: list[tuple[int, int]] = []

            for match in LINK_PATTERN.finditer(content):
                markdown_link_spans.append(match.span())
                link_text, target = match.groups()

                target = target.strip()

                if target.lower().startswith(("http://", "https://")):
                    yield Relationship(
                        source=source_id,
                        target=target,
                        kind="REFERENCES",
                        file=relative_path,
                        metadata={
                            "reference_type": "markdown_url",
                            "resolution": "EXTERNAL",
                            "link_text": link_text,
                            "url": target,
                        },
                    )
                    continue

                target = target.split("#", 1)[0]

                if not target:
                    continue

                target_path = (file_path.parent / target).resolve()

                if not target_path.is_relative_to(root_path):
                    continue

                if target_path.suffix.lower() not in {".md", ".markdown"}:
                    continue

                target_relative = target_path.relative_to(root_path).as_posix()

                yield Relationship(
                    source=source_id,
                    target=f"FILE:{target_relative}",
                    kind="REFERENCES",
                    file=relative_path,
                    metadata={
                        "reference_type": "markdown_link",
                        "link_text": link_text,
                        "target_path": target,
                    },
                )

            for match in URL_PATTERN.finditer(content):
                if any(start <= match.start() < end for start, end in markdown_link_spans):
                    continue
                url = match.group().rstrip(URL_TRAILING_PUNCTUATION)
                if not url:
                    continue
                yield Relationship(
                    source=source_id,
                    target=url,
                    kind="REFERENCES",
                    file=relative_path,
                    metadata={
                        "reference_type": "markdown_url",
                        "resolution": "EXTERNAL",
                        "url": url,
                    },
                )
