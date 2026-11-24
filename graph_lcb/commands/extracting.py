"""Run source extractors and write independent extraction snapshots."""

from pathlib import Path

from graph_lcb.cli import CLIError, Context
from graph_lcb.commands.common import cli, emit
from graph_lcb.extractors.languages.markdown.extractor import MarkdownExtractor
from graph_lcb.extractors.orchestrator import Orchestrator


@cli.handler("extract", "Extract Markdown files into a dated JSONL snapshot.")
def extract_graph(ctx: Context) -> int:
    if len(ctx.args) != 2:
        raise CLIError("use extract ROOT_PATH markdown")
    if ctx._options:
        raise CLIError("extract does not accept options")

    root_path = Path(ctx.positional(0)).resolve()
    extractor_name = ctx.positional(1).casefold()
    if extractor_name != "markdown":
        raise CLIError("supported extractor: markdown")
    if not root_path.is_dir():
        raise CLIError(f"extraction root is not a directory: {root_path}")

    try:
        output_dir = Orchestrator(MarkdownExtractor()).run(root_path)
    except (OSError, UnicodeError) as exc:
        raise CLIError(f"Markdown extraction failed: {exc}") from exc

    emit({
        "extraction": str(output_dir),
        "manifest": str(output_dir / "manifest.json"),
        "entities": str(output_dir / "entities.jsonl"),
        "relationships": str(output_dir / "relationships.jsonl"),
    })
    return 0
