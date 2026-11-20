# graph-lcb documentation

`graph-lcb` is a local Python CLI for building and querying typed, evidence-backed
graphs. It stores a graph as JSON in a `.graph/` directory in the current
working directory; it does not run a server or require a database.

This site focuses on the CLI's implementation and data model:

- [Architecture](./technical/architecture.md) explains command dispatch,
  graph operations, and persistence.
- [Workspace format](./technical/workspace-format.md) documents contracts,
  records, validation, and the files under `.graph/`.
- [CLI reference](./technical/cli-reference.md) describes argument parsing,
  output conventions, command groups, and exit codes.
- [Development](./technical/development.md) maps the source tree and gives
  project-specific development commands.

For installation and the complete command-by-command user reference, see the
[project README](../README.md). The [skills section](./skills/README.md)
contains workflows for using graph-lcb with AI agents.

## At a glance

```text
Python 3.10+  ->  graph command  ->  .graph/{entities,edges,graph}.json
```

The entity and edge contracts define the types and properties allowed in a
workspace. The CLI validates writes against those contracts, and graph records
can include free-form evidence objects that point back to their sources.

Initialize a workspace from the directory you want the graph to belong to:

```console
graph init --template=codebase
graph contract --compact
graph validate
```

Templates are starting points: adapt their type definitions to your domain
before adding records.
