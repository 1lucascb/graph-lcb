"""Markdown extraction behavior and snapshot serialization tests."""

import json
import re
from dataclasses import asdict

from graph_lcb.extractors.base.contracts import SourceLocation
from graph_lcb.extractors.orchestrator import Orchestrator


def test_extracts_deterministic_file_ids_and_local_markdown_links(
    tmp_path, markdown_extractor, write_markdown,
):
    write_markdown("README.md", "[Guide](docs/guide.md#start)")
    write_markdown("docs/guide.md", "Guide")

    records = list(markdown_extractor.extract(tmp_path))
    entities = [record for record in records if record.record_type.value == "ENTITY"]
    relationships = [record for record in records if record.record_type.value == "RELATIONSHIP"]

    assert [entity.id for entity in entities] == ["FILE:docs/guide.md", "FILE:README.md"]
    assert len(relationships) == 1
    assert relationships[0].source == "FILE:README.md"
    assert relationships[0].target == "FILE:docs/guide.md"
    assert relationships[0].metadata["target_path"] == "docs/guide.md"


def test_extracts_external_markdown_and_bare_urls_once(
    tmp_path, markdown_extractor, write_markdown,
):
    write_markdown(
        "README.md",
        "[site](https://example.com/docs) and https://example.org/page.",
    )

    relationships = [
        record for record in markdown_extractor.extract(tmp_path)
        if record.record_type.value == "RELATIONSHIP"
    ]

    assert [record.target for record in relationships] == [
        "https://example.com/docs",
        "https://example.org/page",
    ]
    assert all(record.metadata["resolution"] == "EXTERNAL" for record in relationships)
    assert relationships[0].metadata["link_text"] == "site"


def test_extraction_records_serialize_nested_common_fields(make_entity, make_relationship):
    location = SourceLocation(start_line=1, start_column=0, end_line=1, end_column=7)
    entity = make_entity(location=location, metadata={"format": "markdown"})
    relationship = make_relationship(metadata={"reference_type": "markdown_link"})

    entity_json = json.loads(json.dumps(entity.to_dict(), ensure_ascii=False))
    relationship_json = json.loads(json.dumps(relationship.to_dict(), ensure_ascii=False))

    assert entity_json["location"] == asdict(location)
    assert entity_json["record_type"] == "ENTITY"
    assert relationship_json["record_type"] == "RELATIONSHIP"
    assert relationship_json["metadata"]["reference_type"] == "markdown_link"


def test_orchestrator_writes_separate_dated_snapshot_files(
    tmp_path, markdown_extractor, write_markdown, read_jsonl,
):
    write_markdown("README.md", "[Guide](guide.md) https://example.com")
    write_markdown("guide.md", "Guide")

    first_dir = Orchestrator(markdown_extractor).run(tmp_path)
    second_dir = Orchestrator(markdown_extractor).run(tmp_path)

    assert first_dir.parent.name == "markdown"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{6}Z(?:-\d+)?", first_dir.name)
    assert first_dir != second_dir
    assert {path.name for path in first_dir.iterdir()} == {
        "manifest.json", "entities.jsonl", "relationships.jsonl",
    }

    entities = read_jsonl(first_dir / "entities.jsonl")
    relationships = read_jsonl(first_dir / "relationships.jsonl")
    manifest = json.loads((first_dir / "manifest.json").read_text(encoding="utf-8"))
    timestamp = re.match(r"\d{4}-\d{2}-\d{2}T\d{6}Z", first_dir.name).group()
    assert [record["id"] for record in entities] == ["FILE:guide.md", "FILE:README.md"]
    assert len(relationships) == 2
    assert manifest == {
        "schema_version": "1.0",
        "extractor": "markdown",
        "extractor_version": "1.0.0",
        "tree_sitter_version": None,
        "timestamp": timestamp,
        "source_directory": str(tmp_path.resolve()),
        "detected_languages": ["markdown"],
        "entity_count": 2,
        "relationship_count": 2,
    }
