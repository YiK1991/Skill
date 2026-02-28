---
name: INV-NNN <Investigation Topic>
description: >-
  <One-line purpose. What this investigates and who consumes it.>
inv_id: INV-001
mode: recon
method: jules | local
status: TODO
created: YYYY-MM-DD
reviewed: null
plan_ref: PLAN-YYYY-NNN
related_batches: []
as_of: YYYY-MM-DD  # effective date of this report; update on each snapshot overwrite
entities: []  # ENT-xxx IDs involved in this investigation
---

> **MODE SELECTION** — Before creating this file, decide:
> - **recon**: One-shot investigation. Archive to `history/` after extraction.
> - **snapshot**: Long-lived monitor. Use `@Snapshot_<slug>.md` naming. Overwrite in-place on each run.
>
> If the investigation covers multiple dimensions (stats + issues), request Jules to output separate files (F-NNN, R-NNN) instead of one monolith.
>
> Snapshot: on each overwrite, update `as_of` in frontmatter. Mark stale items `status: invalidated`; do not delete.

> ⚠️ **LIFECYCLE (recon only)**: Once core facts are extracted to P1_design or B file, move this file to `history/` and mark `# ARCHIVED`. If the entire report is superseded by new evidence, set frontmatter `status: INVALIDATED` and fill `Consolidation Record` with `superseded_by`/`as_of`.

> 🧠 **TOOL OUTPUT OFFLOADING**: If a tool/API/terminal output is large (>2000 tokens or >100 lines), write it to `investigation/tool_outputs/` and record only (a) ≤3-line summary + (b) RefSpec to the TO file here. Do not paste raw dumps into chat or this report.

> 🎯 **ENTITY CONSISTENCY**: When mentioning modules/APIs/services/persons in F/C items, use `ENT-xxx` from `references/A0_entity_registry.yaml`. Store detailed properties in the registry; keep only RefSpec pointers here.

# INV-001: <Investigation Topic>

## Investigation Purpose
One sentence why this investigation is needed.
→ Batch: [B001](../execution/B001_xxx.md)
→ Baseline: [CURRENT.md §0](../CURRENT.md#§0-norms-standards-baseline)

## Scope
- Item 1
- Item 2
- **Out of scope**: ...

## Discovery Log

| Step | Detail |
|------|--------|
| Search terms / IDs tried | |
| Files checked (header only) | |
| Deep reads performed | |

## Tool Outputs (Offloaded)

> Rule: Do **not** paste raw logs/JSON here. Offload to `investigation/tool_outputs/` and index below.

| TO-ID | Tool | File (RefSpec) | Purpose | Extracted to |
|-------|------|----------------|---------|-------------|
| TO-INV-001-001 | grep | `tool_outputs/TO-INV-001-001_grep_auth.txt` | find error signature | F-001 |

## Findings (Facts)

### F-001: <title>
- **Fact**: ...
- **Evidence**: `path/to/file.py:L42` / URL
- **valid_from**: YYYY-MM-DD
- **valid_until**: null
- **status**: active
- **superseded_by**: null
- **entities**: [ENT-...]
- **Data flow**: ... → ... → ...
- **Contract**: current interface vs §0 definition
- **Deviation**: ⚠️ drift from §0 (or ✅ compliant)

### F-002: <title>
- **Fact**: ...
- **Evidence**: ...
- **Deviation**: ...

## Constraints

### C-001: <constraint>
- **Source**: gemini.md / technical limitation / dependency
- **Evidence**: ...
- **valid_from**: YYYY-MM-DD
- **valid_until**: null
- **status**: active
- **superseded_by**: null

## Conflicts & Resolutions

> Rule: If facts/constraints conflict, prefer the item with the most recent `valid_from`. If confidence is low, surface the conflict explicitly and keep both.

| Conflict | Candidates | Decision | Rationale | resolved_at |
|----------|------------|----------|-----------|-------------|
| F-002 vs F-005 | F-002, F-005 | adopt F-005 | newer valid_from; verified by <evidence> | YYYY-MM-DD |

## Compliance Path
Based on findings and constraints, record the norm-compliant approach.

## Open Items
Remaining questions or items requiring further investigation.

## Consolidation Record

> Fill this when extracting findings to P1/B files or when archiving/invalidating this INV.

| Item | extracted_to (RefSpec) | invalidated | archived_at |
|------|----------------------|-------------|-------------|
| F-001 | `references/P1_design.md#contract-B001` | no | — |
| C-001 | `execution/B001_xxx.md#constraints` | no | — |

> See [investigation-consolidation.md](../references/investigation-consolidation.md) for full playbook.

### Artifact Trail
- **files_created**: []
- **files_modified**: []
- **files_read**: []
