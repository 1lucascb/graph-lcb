# Development

graph-lcb targets Python 3.10 or newer and has no third-party runtime
dependencies. `pytest` is an optional development dependency. From a checkout,
the project workflow is:

```console
python -m pip install -e ".[test]"
python -m pytest
```

To try the source-tree executable, run `python graph help COMMAND`. Run
`graph init` only in the intended project or a disposable directory because it
creates `.graph/` in the current working directory.

## Source map

| Location | Responsibility |
| --- | --- |
| `graph_lcb/graph_cli.py` | Installed entry point; handles version output, dispatch, and top-level graph errors. |
| `graph_lcb/cli/__init__.py` | Dependency-free option parser, command registry, context, and help dispatch. |
| `graph_lcb/cli/help_texts.py` | Detailed command guides shown by `graph help COMMAND`. |
| `graph_lcb/commands/common.py` | Shared CLI instance, JSON output, and reusable argument helpers. |
| `graph_lcb/commands/admin.py` | Initialization, contracts, validation, status, and summary. |
| `graph_lcb/commands/records.py` | Node and edge creation and lookup. |
| `graph_lcb/commands/mutations.py` | Editing and deleting records. |
| `graph_lcb/commands/importing.py` | JSONL batch import and conflict handling. |
| `graph_lcb/commands/queries.py` | Text search, traversal, and path queries. |
| `graph_lcb/commands/visualization.py` | HTML graph visualization. |
| `graph_lcb/commands/skills.py` | Installation of the bundled agent skill. |
| `graph_lcb/graphs/engine.py` | Contract and graph loading, validation, persistence, mutations, and graph algorithms. |
| `graph_lcb/graphs/types/` | Typed node, edge, and response records. |
| `graph_lcb/contracts/` | Bundled editor schemas and starter templates. |
| `tests/` | CLI, command, engine, and package tests. |

The installed console script is declared in `pyproject.toml` as
`graph_lcb.graph_cli:main`. Package data includes the visualization template,
contract schemas and templates, and bundled skill files.

## Adding or changing a command

1. Put the handler in the existing command module for its responsibility.
2. Register it with the shared `cli` from `graph_lcb.commands.common`, using
   the existing `@cli.handler` pattern.
3. Use shared parsing and output helpers where appropriate. Keep persistence
   and graph validation in the graph engine rather than writing
   `.graph/graph.json` from a handler.
4. Add or update the command's detailed text in `cli/help_texts.py`.
5. Add focused tests in the existing test organization and update the
   [user-facing command reference](../../README.md) when command behavior or
   output changes.

The entry point imports all command modules before dispatch so their decorators
register handlers. Command help is served without running a graph handler.

## Testing guidance

CLI tests should use a temporary working directory so operations cannot modify
a developer's `.graph/` data. Prefer targeted command or engine tests while
developing, then run `python -m pytest` for the full suite. The source-tree
`graph init` command writes to the current directory, so never use it for an
unintended repository workspace.
