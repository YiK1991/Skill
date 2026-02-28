---
name: Investigation Consolidation Playbook
description: >-
  Rules for consolidating, archiving, and invalidating investigation reports.
  Prevents unbounded growth while preserving history for temporal queries.
---

# Investigation Consolidation

## When to consolidate (triggers)

| Trigger | Action |
|---------|--------|
| All F/C extracted to P1/B files | Fill Consolidation Record → archive to `history/` |
| >50% of findings invalidated | Review remaining items; archive if all stale |
| Periodic (>30 days since `as_of`) | Re-verify or archive |
| Retrieval quality dropping | Consolidate related INVs into a single updated report |

## Archive vs Invalidate (decision table)

| Condition | Action | Status |
|-----------|--------|--------|
| Findings fully consumed by downstream docs | Archive → `history/` | `ARCHIVED` |
| New evidence contradicts findings | Set items `status: invalidated` + `superseded_by` | `INVALIDATED` |
| Partial extraction (some items still active) | Keep in `investigation/`; mark extracted items individually | `DONE` |

## How to archive

1. Fill the **Consolidation Record** in the INV file (extracted_to / invalidated / archived_at)
2. Move file to `history/` with date-stamped name: `INV-<ID>_<slug>_<YYYYMMDD>.md`
3. Update `investigation/_tracker.md`: set status → `ARCHIVED`, update `Report` link to new path
4. Prefix first line of moved file with `# ARCHIVED`

## How to invalidate

1. Set F/C items: `status: invalidated`, `superseded_by: F-00X` (or new INV ID)
2. Update tracker: status → `INVALIDATED`, update `as_of`
3. Do **not** delete the file or tracker row — history supports temporal queries

## Consolidation Record example

```markdown
| Item | extracted_to (RefSpec) | invalidated | archived_at |
|------|----------------------|-------------|-------------|
| F-001 | `references/P1_design.md#contract-B001` | no | 2026-02-28 |
| F-002 | — | yes (superseded by F-005 in INV-003) | — |
| C-001 | `execution/B001_xxx.md#constraints` | no | 2026-02-28 |
```

> *Source*: `memory-systems` — "consolidation prevents unbounded growth… invalidate but don't discard."
