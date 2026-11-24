# Source extractors

Use source extractors for quick fact retrieval. An extractor can find entities such as files, classes, or functions (depending on the extractor) and candidate relationships between them. Use these results to guide investigation and identify source locations to verify.

## Extractor output is never a graph import

> **NEVER directly import extractor output into the user’s graph.**
>
> Extractor output is generated using an independent extraction schema. It is **not tied to the user-defined entity and edge contracts** in `.graph/entities.json` and `.graph/edges.json`, and its JSONL files are **not meant to be directly imported under any circumstances**. Do not run `graph import` on an extractor snapshot’s `entities.jsonl` or `relationships.jsonl`.
>
> Extracted facts must first be reviewed, checked against source material, and adapted into records that satisfy the current graph contracts. The adaptation step is mandatory even when the names or shapes appear to match.

## Run an extractor

Check `graph help extract` for the extractors supported by the installed CLI, then run the appropriate extractor for the source root. For example, the Markdown extractor is run as:

```sh
graph extract . markdown
```

The command writes a dated snapshot under `.graph/extractions/<extractor>/<timestamp>/`, with separate `entities.jsonl`, `relationships.jsonl`, and `manifest.json` files. The snapshot is an independent retrieval artifact; it does not change `graph.json` or use the workspace’s entity and edge contracts.

Read the manifest and inspect the extracted entities and relationships. Treat them as candidate facts, not as approved graph records. Extractors may omit context, include files outside the intended scope, return unresolved or external relationship targets, or report facts that need source verification. Follow the relevant paths, declarations, or links in the source before recording important claims.

## Adapt facts to the active contract

Before preparing graph records:

1. Read the current contract with `graph contract --compact` (or inspect `.graph/entities.json` and `.graph/edges.json`). Use the contract as it exists now; do not assume the extractor schema is the graph schema.
2. For each verified extracted fact, decide whether an existing entity type represents it and whether its extracted properties fit that type’s allowed properties and required fields. Do the same for each relationship, checking its meaning, allowed source and target types, and property requirements.
3. Map only facts with a sound semantic fit. A similar label alone is not enough: for example, a candidate link/reference may fit an existing documentation relationship only when that relationship’s meaning covers what the source establishes. Convert IDs, names, properties, and evidence into the graph’s record format. Do not carry extractor-only fields or types through automatically.
4. If the current contract has no suitable type, or cannot represent a fact without changing its meaning, stop before writing that fact. Explain the mismatch and ask the user whether they want to extend or change the contract. Reach agreement before editing the contract or importing records that depend on the change. If the user does not approve a contract change, leave those facts out of the graph and report them as unmapped.
5. Once the records are adapted, use the workflow in [batch_imports.md](batch_imports.md): prepare a reviewable JSONL batch, run `graph import FILE --dry-run`, resolve validation errors, then import the validated batch. **This batch contains newly adapted graph records, not extractor output.**

Extractor results are useful even when they are not added to the graph. Use them to answer quick questions, find declarations and links, and focus source review. Import is a separate, deliberate mapping step governed by the user’s current contract.
