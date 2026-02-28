# Output Contract (Cross-Prompt Unified Fields)

All PDCA phase outputs must use these exact field names. This enables automated compression, evaluation, and traceability.

## Required fields (every phase output)

| Field | Format | Description |
|-------|--------|-------------|
| `Read List` | RefSpec list | Files/sections read during this phase |
| `Write List` | RefSpec list | Files modified/created during this phase |
| `Evidence Pointers` | RefSpec list | Top 3–5 pointers supporting key decisions |
| `Budget Triggers & Actions` | trigger → action pairs | Which triggers hit, which optimization actions taken |
| `Offloads Index` | pointer + purpose | Offloaded files with purpose annotation |
| `Partitions Index` | pointer + purpose | Evidence/notes split into dedicated files |

## Phase-specific additions

| Phase | Additional fields |
|-------|-------------------|
| Analysis | `Candidate List`, `Deep-read RefSpecs`, `Investigation Notes (if any)` |
| Planning | `Execution Read List`, `Execution Write List`, `Worker Scopes (if any)` |
| Implementation | `Test Status`, `Commits`, `Compaction Block updates` |
| Completion | `Eval Evidence Block`, `Final Compaction Snapshot`, `Consolidation Record` |

## Rules

- **Same names everywhere**: Do not invent synonyms (e.g., "files touched" vs "write list").
- **RefSpec format only**: `path#anchor` or `path:Lx-Ly`. No free-text file references.
- **Append, don't repeat**: If a field was populated in Analysis, Planning inherits it and appends; it does not restate.

> *Source*: `tool-design` — "Reduce ambiguity via consistent output format"; `evaluation` — "Outputs must be measurable and comparable."
