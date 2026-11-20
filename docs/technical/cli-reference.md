# CLI behavior reference

The executable accepts one command followed by positional arguments and
long-form options:

```text
graph <command> [arguments] [options]
```

Run `graph --help` to list registered commands, or `graph help COMMAND` for
the built-in guide for one command. Those forms do not require an initialized
workspace. `graph --version` prints the installed package version.

## Argument parsing

- Options use `--name value` or `--name=value`. Short options are not supported,
  apart from the help forms `-h` and `--help`.
- Comma-separated options accept values such as `--type=API,WORKER`.
- JSON options must contain valid JSON. Quote JSON appropriately for the
  shell in use; POSIX single-quote examples may need adjustment in PowerShell
  or `cmd.exe`.
- `--` ends option parsing. Following values are positional arguments.
- An option without a value is represented as a boolean flag; each command
  checks whether its options accept a value.
- If an option value begins with a hyphen, use the `--option=value` form to
  avoid treating the value as another option.

The CLI parser does not define aliases or abbreviations for command options.
Each handler validates the options it supports.

## Command groups

The complete argument and option definitions are maintained in the
[project README](../../README.md#command-reference) and in `graph help COMMAND`.
The commands are grouped here by purpose:

| Purpose | Commands | Workspace needed? |
| --- | --- | --- |
| Workspace setup and contracts | `init`, `contract` | No |
| Validation and overview | `validate`, `status`, `summary` | `validate` can report a missing workspace; `status` and `summary` require initialization. |
| Record creation and bulk loading | `add-node`, `add-edge`, `import` | Yes |
| Record lookup and search | `nodes`, `edges`, `search` | Yes |
| Graph algorithms | `traverse`, `path` | Yes |
| Record changes | `edit`, `delete` | Yes |
| Visualization and agent support | `view`, `install-skill` | Workspace required for `view`; `install-skill` copies skill files. |
| Help | `help` | No |

`graph init --list-templates` lists bundled templates. A template is an
editable starter contract, not an assumed model of the user's domain.

## Output conventions

Most commands write compact, single-line JSON to standard output. Collection
queries generally return an envelope:

```json
{"rows": [], "total": 0, "truncated": false}
```

`total` is the count after filtering and before a limit or page is applied.
`truncated` indicates that results were omitted. Some commands have
command-specific response shapes: for example, `traverse` returns `nodes`,
`edges`, and `truncated`, while `path` returns `paths` and `truncated`.
`--fields` can reduce returned record fields where supported.

Usage and operation errors are printed to standard error. `graph validate`
returns a JSON report for validation failures and unavailable workspaces.
`graph contract --compact` returns plain text instead of JSON.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success; `validate` found no violations, or `status --strict` found no selected findings. |
| `2` | Usage or operation error, such as invalid arguments, invalid data, missing initialized workspace, or ambiguous edge deletion. |
| `3` | Requested record not found, `validate` found violations, or `status --strict` found selected findings. |
| `4` | `validate` could not run because workspace files were unavailable or unreadable. |

The default `status` mode is informational and exits successfully even when
findings are present. `--strict` changes the exit status to `3` when a selected
check has findings.

## Bulk import

`graph import FILE` reads JSON Lines: one JSON object per line. Use `-` for
standard input. A record may use `"kind":"node"` or `"kind":"edge"`; without
`kind`, records with `source` or `target` fields are treated as edges and other
records as nodes. Edge IDs may be omitted and generated. Edges can refer to
nodes appearing later in the same file.

The importer stages nodes before edges, checks the complete batch against the
current graph and contracts, then saves once. If validation fails, no batch
changes are written. `--dry-run` performs the checks and reports the planned
counts without saving. `--on-conflict` supports:

- `error` (default): report the conflict and abort the batch.
- `skip`: keep the existing record unchanged.
- `replace`: update changed records; identical content is counted as unchanged.

Node conflicts use node IDs. Edge conflicts use edge IDs or matching edge type,
endpoints, and properties. A semantic edge replacement preserves the existing
edge ID.

## Query characteristics

`nodes` and `edges` are for structured filters; `search` is for text across
record fields. Search uses case-insensitive substring matching by default and
combines positive terms with AND; `--any` changes that to OR. Regex search
uses Python's regular-expression engine without a timeout, and scans records
linearly, so use narrow fields or filters for large graphs.

`traverse` performs breadth-first traversal from one node. `path` finds simple
paths, ordered shortest-first. Both accept edge-type filters and direction
controls. Path enumeration may be expensive on dense graphs; bound it with
`--max-depth`, `--edge`, and a modest `--limit`.

For exact flags, field lists, and return shapes, consult the specific guide
with `graph help COMMAND` or the full [command reference](../../README.md#command-reference).
