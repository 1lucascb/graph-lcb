
import json
from datetime import datetime, timezone
from pathlib import Path

from graph_lcb.extractors.base.extractor import ExtractorBase


class Orchestrator:

    def __init__(self, extractor: ExtractorBase):
        self.extractor = extractor

    def run(self, root_path: Path) -> Path:
        root_path = root_path.resolve()
        extractor_name = type(self.extractor).__name__.removesuffix("Extractor").casefold()
        started_at = datetime.now(timezone.utc)
        run_stamp = started_at.strftime("%Y-%m-%dT%H%M%SZ")
        extractor_dir = root_path / ".graph" / "extractions" / extractor_name
        output_dir = extractor_dir / run_stamp
        suffix = 1
        while True:
            try:
                output_dir.mkdir(parents=True, exist_ok=False)
                break
            except FileExistsError:
                output_dir = extractor_dir / f"{run_stamp}-{suffix}"
                suffix += 1

        entities_file = (output_dir / "entities.jsonl").open("w", encoding="utf-8")
        relationships_file = (output_dir / "relationships.jsonl").open("w", encoding="utf-8")
        entity_count = 0
        relationship_count = 0
        try:
            for record in self.extractor.extract(root_path):
                if record.record_type.value == "ENTITY":
                    destination = entities_file
                    entity_count += 1
                else:
                    destination = relationships_file
                    relationship_count += 1
                destination.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        finally:
            entities_file.close()
            relationships_file.close()

        manifest = {
            "schema_version": "1.0",
            "extractor": extractor_name,
            "extractor_version": self.extractor.version,
            "tree_sitter_version": getattr(self.extractor, "tree_sitter_version", None),
            "timestamp": started_at.strftime("%Y-%m-%dT%H%M%SZ"),
            "source_directory": str(root_path),
            "detected_languages": list(self.extractor.detected_languages),
            "entity_count": entity_count,
            "relationship_count": relationship_count,
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        return output_dir
