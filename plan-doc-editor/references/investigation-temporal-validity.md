---
name: Temporal Validity Playbook
description: >-
  Rules for tracking fact/constraint validity, handling stale data,
  and resolving conflicts in investigation reports.
---

# Investigation Temporal Validity

## When to set valid_from / valid_until

- `valid_from`: The date the fact/constraint was **verified** (not when it was written).
- `valid_until`: Set to a date when there is a known expiry (API deprecation, seasonal data, etc.). Leave `null` if the fact has no known expiry.

## How to invalidate

1. Set `status: invalidated` on the old item.
2. Set `superseded_by: F-00X` (or `C-00X`) pointing to the replacement.
3. **Do not delete** — invalidated items serve as audit trail and prevent re-investigation.

## Conflict playbook

| Situation | Action |
|-----------|--------|
| Two facts contradict | Prefer the one with the most recent `valid_from` |
| Confidence is low | Keep both facts; record the conflict in **Conflicts & Resolutions** table |
| External dependency changed | Re-verify the older fact; update `valid_until` if stale |
| Both facts are recent and verified | Escalate: create a new Q-* question or INV to resolve |

## Snapshot cadence

- `as_of` in frontmatter **must** advance on each overwrite.
- Stale items within a snapshot: mark `status: invalidated`, do not silently remove.
- If a snapshot has not been updated for >14 days and is still `ACTIVE` in tracker, it should be re-run or archived.

## Examples

### Example 1: Conflicting API findings

```
F-001: /api/v1/products returns paginated results (valid_from: 2026-01-15, status: invalidated, superseded_by: F-003)
F-003: /api/v2/products returns cursor-based results (valid_from: 2026-02-20, status: active)
```

**Resolution**: F-003 adopted (newer valid_from, verified against live API).

### Example 2: Stale constraint

```
C-002: Max 100 concurrent connections (valid_from: 2025-11-01, valid_until: 2026-02-01, status: invalidated)
C-005: Max 500 concurrent connections after infra upgrade (valid_from: 2026-02-01, status: active)
```

### Example 3: Snapshot overwrite

```yaml
# @Snapshot_L3_Drift.md frontmatter
as_of: 2026-02-28           # ← updated from 2026-02-14
```

Items from the previous run that no longer hold are marked `status: invalidated` within the snapshot body.
