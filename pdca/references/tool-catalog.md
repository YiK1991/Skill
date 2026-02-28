# Tool Catalog (Consolidated)

Prefer a small set of general tools with clear boundaries. Default to filesystem primitives before introducing specialized tools.

## Tier 0: Filesystem primitives (default)

| Tool | Purpose |
|------|---------|
| `ls` / `glob` | Discover structure |
| `rg` / `grep` | Search identifiers, errors, patterns |
| `open` / `read` | Targeted reads (anchors, line ranges) |

## Tier 1: Execution primitives

| Tool | Purpose | Default format |
|------|---------|---------------|
| `run_tests` | Run minimal test set | concise |
| `run_cmd` | General command runner | concise |
| `apply_patch` | Apply a patch; returns changed files + diff stats | concise |

## Disallowed overlaps

- Do not add both `run_pytest` and `run_tests` (overlap).
- Do not add both `search_code` and `rg` (prefer `rg`).
- Do not add a "read_file" wrapper when `open` + line range suffices.

## Escalation path

Tier 0 (filesystem) → Tier 1 (execution) → Specialized tool (only if both tiers fail).

> *Source*: `tool-design` — "Consolidation principle: tool overlap causes selection ambiguity… prefer filesystem primitives."
