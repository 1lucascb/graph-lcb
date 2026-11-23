# Workspace format

A graph workspace is scoped to the process's current working directory. The
CLI does not locate a workspace relative to its installation path. Run
commands from the project whose `.graph/` directory you intend to use.

> [!NOTE]
> The same installed `graph` command can operate on different workspaces; the
> directory you launch it from determines which graph it reads and writes.

## Files

| Path | Role |
| --- | --- |
| `.graph/entities.json` | Entity type definitions and property contracts. |
| `.graph/edges.json` | Edge type definitions, endpoint constraints, and property contracts. |
| `.graph/graph.json` | Persisted `nodes` and `edges` arrays; created on the first write. |
| `.graph/schemas/entities.schema.json` | JSON Schema for editor support of entity contracts. |
| `.graph/schemas/edges.schema.json` | JSON Schema for editor support of edge contracts. |
| `.graph/view.html` | Generated visualization from `graph view`. |

`graph init` creates missing contracts and schemas without replacing existing
contracts that already define types. The contracts are JSON files intended to
be edited to fit the domain. The bundled schemas help editors validate and
complete those files; runtime validation is performed by the graph engine.

## Contract shape

An entity contract maps each type to a `properties` object. An edge contract
also defines lists of permitted source and target entity types:

```json
{
  "$schema": "./schemas/entities.schema.json",
  "API": {
    "description": "An API or application service",
    "properties": {
      "language": { "type": "string", "required": true },
      "framework": "string"
    }
  }
}
```

```json
{
  "$schema": "./schemas/edges.schema.json",
  "CALLS": {
    "description": "One service invokes another.",
    "source": ["API"],
    "target": ["API"],
    "properties": {
      "protocol": { "type": "string", "required": false }
    }
  }
}
```

A property definition can be a type name or an object with `type` and optional
`required`. Supported property types are `string`, `number`, `integer`, and
`boolean`; arrays and nested objects are not supported as contract properties.
`number` accepts integer and decimal JSON numbers, but neither `number` nor
`integer` accepts booleans. `required` defaults to false. Edge source and target
entries must refer to defined entity types. Type names must be unique without
regard to case.

The `$schema` field is metadata for tools. `graph contract` omits it from
command output.

## Record shape

The store has this top-level shape:

```json
{
  "nodes": [],
  "edges": []
}
```

A node has required string fields `id`, `type`, and `name`. It can also contain
`description`, `properties`, `metadata`, and `evidences`. An edge has required
string fields `id`, `type`, `source`, and `target`, with the same optional
record fields. Properties and metadata are objects; evidence is a list of
objects. Evidence object fields are user-defined and may contain nested values.

Node IDs must match `^[a-z0-9][a-z0-9._-]*$`. Edge IDs are generated UUIDs.
Records created by the CLI include UTC `created_at` and `updated_at` values in
metadata. An edge's target type is derived from the target node when returned
by the CLI; it is not stored on the edge.

## Validation and integrity

Graph operations use the current contracts to check record types, property
names and values, required properties, edge endpoint existence, and endpoint
type compatibility. `graph validate` reports contract and record violations
without changing files. A missing `graph.json` counts as an empty graph.

> [!IMPORTANT]
> Treat the contracts as part of the workspace's data model. Changing them can
> make existing records invalid, so run `graph validate` after contract edits.

Additional integrity behavior includes:

- Node IDs are unique. Deleting a node also removes its connected edges.
- Edge duplicates with the same type, endpoints, and properties are rejected.
- More than one edge between the same endpoints is allowed only when each
  additional edge has a non-empty description; edges of the same type must
  also differ in properties.
- Node and edge types, IDs, and edge endpoints cannot be edited in place.

For detailed contract syntax and command examples, see the
[project README](../../README.md#contract-format).
