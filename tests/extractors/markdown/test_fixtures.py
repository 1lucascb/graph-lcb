"""Golden fixture integration test for the Markdown extractor."""

import json
from pathlib import Path


def test_markdown_fixture_matches_expected_entities_and_relationships(markdown_extractor):
    fixture_dir = Path(__file__).parent / "fixtures"
    source_dir = fixture_dir / "source"
    records = [record.to_dict() for record in markdown_extractor.extract(source_dir)]

    actual_entities = [record for record in records if record["record_type"] == "ENTITY"]
    actual_relationships = [record for record in records if record["record_type"] == "RELATIONSHIP"]
    expected_entities = json.loads((fixture_dir / "expected_entities.json").read_text(encoding="utf-8"))
    expected_relationships = json.loads((fixture_dir / "expected_relationships.json").read_text(encoding="utf-8"))

    assert actual_entities == expected_entities
    assert actual_relationships == expected_relationships
