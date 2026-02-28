# Investigation Compatibility (PDCA ↔ plan-doc-editor)

Bridge protocol ensuring PDCA investigation artifacts are compatible with plan-doc-editor's memory systems.

## When to create investigation artifacts

**Trigger**: ambiguous root cause, multiple hypotheses, >1 tool output, or decision impacts more than one file/module.

## Canonical schema (must follow)

### Findings (F-*)
- `statement` / `evidence` (RefSpec) / `valid_from` / `valid_until` / `status` / `superseded_by` / `entities` [ENT-...]

### Constraints (C-*)
- `statement` / `evidence` (RefSpec) / `valid_from` / `valid_until` / `status` / `superseded_by` / `entities` [ENT-...]

### Hypotheses (H-*) (optional)
- `claim` + `confidence` + `validation_plan` / `entities` [ENT-...]

## Temporal validity rules

1. Prefer the most recent `valid_from` when facts conflict.
2. Mark stale items `status: invalidated`; do not delete.
3. Record conflicts in Conflicts & Resolutions section.

## Entity registry rules

1. Use `ENT-xxx` identifiers in F/C/H; store properties in `A0_entity_registry.yaml`.
2. Update `last_verified` when adding/modifying properties.

## Consolidation rules (invalidate but don't discard)

1. When extracted into implementation plan/design: archive report (move to `history/`).
2. If superseded: mark report `INVALIDATED`; keep history; record `superseded_by`/`as_of`.

## Storage locations

| Scenario | investigation | references | history |
|----------|--------------|------------|---------|
| plan-doc-editor present | `investigation/` | `references/` | `history/` |
| Greenfield / standalone | `scratch/investigation/` | `scratch/references/` | `scratch/history/` |

> *Source*: `memory-systems` — Temporal validity, Entity memory, Memory consolidation layers.
