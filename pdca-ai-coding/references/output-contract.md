# Output Contract (Cross-System Unified Fields)

All worker outputs (PDCA phases, Jules results, subagent reports) must use these exact field names.
This enables automated compression, evaluation, traceability, and plan-doc-editor backflow.

## Core Worker Contract (all workers MUST include)

| Field | Format | Description |
|-------|--------|-------------|
| `Read List (RefSpec)` | `path#anchor` or `path:Lx-Ly` | Files/sections actually read |
| `Write List (RefSpec)` | same | Files created or modified |
| `Evidence Pointers (RefSpec)` | Top 3–5 | Key code/doc anchors supporting decisions |
| `Plan Update Targets (RefSpec + bullet)` | `path#anchor` + ≤3-line edit | Specific plan edits for backflow |

> Field names are **fixed across all three skills** (plan-doc-editor, PDCA, jules-cli).
> Do NOT invent synonyms (e.g., "Files Changed" instead of "Write List").

## PDCA Extended Contract (PDCA phases only)

| Field | Format | Description |
|-------|--------|-------------|
| `Budget Triggers & Actions` | trigger → action pairs | Which budget triggers hit, which optimization actions taken |
| `Offloads Index` | pointer + purpose | Offloaded files with purpose annotation |
| `Partitions Index` | pointer + purpose | Evidence/notes split into dedicated files |

## Phase-specific additions (PDCA only)

| Phase | Additional fields |
|-------|-------------------|
| Analysis | `Candidate List`, `Deep-read RefSpecs`, `Investigation Notes (if any)` |
| Planning | `Execution Read List`, `Execution Write List`, `Worker Scopes (if any)` |
| Implementation | `Test Status`, `Commits`, `Compaction Block updates` |
| Completion | `Eval Evidence Block`, `Final Compaction Snapshot`, `Consolidation Record` |

## Rules

- **Same names everywhere**: Do not invent synonyms. Core fields use `(RefSpec)` suffix.
- **RefSpec format only**: `path#anchor` or `path:Lx-Ly`. No free-text file references.
- **Append, don't repeat**: If a field was populated in Analysis, Planning inherits it and appends.

> *Source*: `tool-design` — "Reduce ambiguity via consistent output format"; `evaluation` — "Outputs must be measurable and comparable."
