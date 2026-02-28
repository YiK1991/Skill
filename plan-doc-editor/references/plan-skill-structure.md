# Plan-as-Skill Structure Reference

## File Naming Rules

| Folder           | Pattern                             | Example                               |
| ---------------- | ----------------------------------- | ------------------------------------- |
| `questions/`     | `Q{NNN}_<slug>.md`                  | `Q001_check_drift_bug.md`             |
| `investigation/` | `INV-NNN_<slug>.md`                 | `INV-001_current_api_architecture.md` |
| `investigation/` | `@Snapshot_<slug>.md`               | `@Snapshot_L3_Drift.md` (覆写型)      |
| `execution/`     | `B{NNN}_<slug>.md`                  | `B001_setup_database_schema.md`       |
| `references/`    | `P{N}_<name>.md` / `A{N}_<name>.md` | `P1_design.md`, `A1_risk_register.md` |
| `history/`       | `v{NNN}_YYYYMMDD_CURRENT.md`        | `v001_20260225_CURRENT.md`            |
| `history/`       | `INV-<ID>_<slug>_<YYYYMMDD>.md`     | `INV-001_auth_failures_20260228.md`   |
| tracker files    | `_tracker.md`                       | `investigation/_tracker.md`           |
| `investigation/tool_outputs/` | `TO-<INV-ID>-<SEQ>_<tool>_<slug>.{txt\|md\|json}` | `TO-INV-001-001_api_users_dump.json` |
| `references/` | `A0_entity_registry.yaml` | Entity registry — canonical properties + pointers |

**Slug**: lowercase underscore, descriptive, ≤40 chars. No spaces/Chinese/special chars.

## Context Roles: Static vs Dynamic

| Role | Files | What to read |
|------|-------|-------------|
| **Static** (always) | `INDEX.md`, `CURRENT.md`, `*/_tracker.md` | Tables, headings, active/blocked rows |
| **Dynamic** (on-demand) | `execution/B*`, `investigation/INV-*`, `references/*`, `questions/*`, `history/*` | Full content — only when triggered by pointers or user request |

Dynamic loading entries must come from scannable pointers: B frontmatter (`prerequisites`, `related_investigations`, `impact_refs`), CURRENT §4 Context Cards, or tracker active rows.

## Discovery Entry Points

| Stop | What | How |
|------|------|-----|
| 1st (static pointers) | `INDEX.md`, `CURRENT.md`, `*/_tracker.md` | Always read — tables and active rows only |
| 2nd (structured pointers) | B frontmatter arrays + `cross_refs` | Expand prerequisites / impact_refs / related_investigations |
| 3rd (keyword/ID search) | Any file by ID (B/INV/P/Q) or keyword | grep / find — only when 1st+2nd insufficient |
| Deep read rule | Target file `#anchor` | Full-file read only for files <50 lines; otherwise anchor only |

## ID System

| Prefix          | Scope           | Example         |
| --------------- | --------------- | --------------- |
| `PLAN-YYYY-NNN` | Plan identifier | `PLAN-2026-001` |
| `INV-NNN`       | Investigation   | `INV-001`       |
| `F-NNN`         | Finding (fact)  | `F-001`         |
| `C-NNN`         | Constraint      | `C-001`         |
| `B{NNN}`        | Batch task      | `B001`          |
| `ATDD-NNN`      | Acceptance test | `ATDD-001`      |
| `D-NNN`         | Decision        | `D-001`         |
| `Q-NNN`         | Open question   | `Q-001`         |
| `R-NNN`         | Risk            | `R-001`         |
| `@Snapshot-NAME`| Snapshot (覆写型) | `@Snapshot-L3-Drift` |
| `CTX-P{N}-NAME` | Context card    | `CTX-P1-DESIGN` |
| `G-NAME`        | Gate            | `G-INV`         |

IDs are **stable** — prompts, tools, and other plans reference them.
`@Snapshot-NAME` files are overwritten in-place on each run; they do not increment.

## Status Enums

- **Plan**: `NORMING` | `INVESTIGATING` | `DESIGNING` | `READY` | `EXECUTING` | `CLOSED`
- **INV**: `TODO` | `IN_PROGRESS` | `DONE` | `REVIEWED` | `ARCHIVED` | `INVALIDATED`
- **Batch**: `TODO` | `INVESTIGATING` | `DESIGNING` | `READY` | `EXECUTING` | `DONE`

## State Transitions

| From          | To            | Gate                      |
| ------------- | ------------- | ------------------------- |
| NORMING       | INVESTIGATING | §0 baseline all confirmed |
| INVESTIGATING | DESIGNING     | All INV items REVIEWED    |
| DESIGNING     | READY         | Design contracts complete |
| READY         | EXECUTING     | ATDD task list complete   |
| EXECUTING     | CLOSED        | All DoD satisfied         |

Any state can fall back to earlier states when issues are discovered.

## Entrypoints

- `INDEX.md`: navigation only; first item → `CURRENT.md`.
- `CURRENT.md`: global entry — norms (§0), routing, status, gates. Not all deep detail.

## Phase Naming (default)

P0: Baseline | P1: Design & contracts | P2: Implementation | P3: Verification | P4: Rollout & rollback

## Cross-Reference Protocol (views-not-copies)

1. **Link, don't copy** — keep one canonical section, link to it from elsewhere.
2. **B files are hubs** — link to `investigation/INV-*` and `references/P*`; inline ≤3 lines summary.
3. **Frontmatter `cross_refs`** — every B file declares `tracker`, `current`, `changelog` paths.

### Anti-Bloat Rules

| Signal                          | Remedy                                                    |
| ------------------------------- | --------------------------------------------------------- |
| B file >120 lines               | Extract to `references/` + summary link                   |
| Same fact in ≥2 files           | Canonicalize into one, link from others                   |
| INV findings pasted into B file | Replace with ≤3-line summary + `→ [INV-NNN](...)` link   |
| Extracted Q / INV files         | Move to `history/` and mark `# ARCHIVED`                  |
| Multi-dimension investigation   | Require Jules to output separate files (F-NNN, R-NNN)     |
| CURRENT.md >150 lines           | Move deep content to `references/`; keep table + links    |
| Tool/API/terminal output in chat or INV body | Offload to `investigation/tool_outputs/` + ≤3-line summary + RefSpec in INV Tool Outputs table |

### Link Format (RefSpec)

**RefSpec format (hard rule)**: `[<label>](../<path>.md#<anchor>)`

Examples:
- `[P1_design.md#contract-B001](../references/P1_design.md#contract-B001)`
- `[INV-001#F-001](../investigation/INV-001_xxx.md#f-001)`

**Canonical placement rule**: Content referenced by ≥2 files (contracts, findings, decisions) MUST live under a stable heading in `references/P*` or the source file. Anchors must be explicit `##` headings — do not link to prose paragraphs.

## Budget Constraints (Policy v1)

| Constraint | Limit | Overflow action |
|-----------|-------|----------------|
| Dynamic deep-reads per B | ≤ 8 | Move detail to `references/`; keep RefSpec + ≤3 lines |
| INV deep-reads per B | ≤ 2 | Summarize remainder; link via RefSpec |
| P* anchor reads per B | ≤ 3 | Merge/extract into P* before referencing |
| History reads | **0 by default** | Only on explicit `regression` / `backtrace` trigger in B/INV |

`references/` is the detail sink — B files keep only executable items and pointers (RefSpec).

## Tracker Files (_tracker.md)

Trackers store ID + status + mode + file link. Actual content lives in individual files.

| ID | mode | status | file | notes |
|----|------|--------|------|-------|
| INV-001 | recon | TODO | `INV-001_xxx.md` | |
| @Snapshot-L3-Drift | snapshot | ACTIVE | `@Snapshot_L3_Drift.md` | long-lived |

### Mandatory Update Events

| Event                    | Tracker(s)                                      | Action               |
| ------------------------ | ----------------------------------------------- | -------------------- |
| Batch status change      | `execution/_tracker.md`                         | Update status        |
| INV opened/closed        | `investigation/_tracker.md`                     | Update status + date |
| Batch completed          | `execution/_tracker.md` + `CURRENT.md §1`       | Both reflect DONE    |
| Plan state transition    | `CURRENT.md` header metadata                    | Update `status`      |

Every B file's Post-Completion Updates checklist enforces these updates.

> **INVALIDATED rule**: Do not delete tracker rows. Set status to `INVALIDATED`; require `superseded_by` + updated `as_of`. Archived INVs move to `history/` with date-stamped filename; tracker `Report` link must point to the new path.

## Entity Registry (Entity Memory Layer)

`references/A0_entity_registry.yaml` is the single source for entity properties.

| Rule | Detail |
|------|--------|
| Single source | Registry owns canonical_name, key_properties, last_verified; INV/B/P do not repeat |
| Reference by ID | Use `ENT-xxx` in F/C/B files; link to registry for properties |
| New properties | Update registry + set `last_verified`; do not scatter attributes across files |
| Anti-bloat | Max 5 key_properties per entity; detailed specs → `references/P*` via RefSpec |

Details: [entity-registry.md](entity-registry.md)

## Temporal Validity Rules

| Rule | Detail |
|------|--------|
| Every F-* / C-* must include | `valid_from`, `valid_until` (null = current), `status` (active / invalidated) |
| Conflicting facts | Prefer most recent `valid_from`; low confidence → keep both + record in Conflicts & Resolutions |
| Stale information | Set `status: invalidated` + `superseded_by: F-00X`; do **not** delete |
| INV frontmatter `as_of` | Must reflect report effective date; update on each snapshot overwrite |
| Tracker `as_of` column | Enables quick staleness check without opening INV file |

> *Source*: `memory-systems` — "Ignoring temporal validity… outdated information poisons context."

Details: [investigation-temporal-validity.md](investigation-temporal-validity.md)

## Frontmatter Convention

All documents MUST include `name` and `description` in YAML frontmatter:

```yaml
---
name: <ID> <Short Title>
description: >-
  One-line purpose. Consumed by <who>. Lifecycle: <recon|snapshot>.
---
```

This enables AI to scan headers without loading full content.
