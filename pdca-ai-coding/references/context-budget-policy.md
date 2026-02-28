# Context Budget Policy (PDCA)

Explicit context budget allocation with trigger-based optimization. Prevents unbounded context growth.

## Buckets (allocate explicitly)

| Bucket | Strategy |
|--------|----------|
| **Static baseline** | Small, always loaded (project entrypoints, plan anchors) |
| **Dynamic reads** | Only when triggered (targeted file sections via Discovery Ladder) |
| **Tool/logs** | Offloaded files + small excerpts (see tool-output-offloading.md) |
| **History** | Default 0; load only with explicit trigger (regression/debug) |
| **Buffer** | Reserve for surprises; never fully spend budget |

## Proxy budgets (v1)

| Metric | Limit per step | Limit per session |
|--------|---------------|-------------------|
| Dynamic deep-reads (RefSpec items) | ≤12 | ≤30 |
| Inline excerpts | ≤3, each ≤60 lines | - |
| Tool outputs (inline) | ≤10-line summary + ≤80-line excerpt | full logs offloaded |
| History reads | - | ≤1 unless regression trigger |

## Trigger rules (when to optimize)

If any proxy budget is exceeded:
1. **Stop** adding new reads.
2. **Offload/point**: move detail to a file; keep pointers only.
3. **Collapse into anchors**: update session Head/Tail anchors with 3–7 key items.
4. **Defer**: postpone non-critical reads.

## Optimization actions (LOCKED priority chain — execute in order, never skip ahead)

> **⚠️ Priority chain is locked**: masking → partition → caching → compaction. Do NOT run compaction before masking/partition.

### 1) Observation masking (replace verbose content with reconstructable refs)
Use when: logs/search outputs/long snippets are taking space OR budget triggers hit.

Rules:
- If a verbose blob was previously pasted in chat/session:
  1. Move/keep full blob in an offloaded file (tool_outputs / scratch).
  2. In session, REPLACE it with: ≤10-line summary + ≤80-line excerpt + RefSpec pointer + `masked_from: step N`.
- After masking, DO NOT paste the same blob again; always cite RefSpec.

### 2) Partition (split evidence/notes into dedicated files; session keeps only index)
Use when: evidence/notes are growing OR multiple threads exist.

Partitions:
- Test evidence → `scratch/test_runs/` or `investigation/tool_outputs/`
- Investigation notes → `scratch/investigation/INV-*.md`
- Design notes/contracts → `scratch/references/`
- Decision log → keep in Session Compaction Block "Decisions"

Rule: session log must NOT contain raw evidence dumps; only index pointers + summaries + decisions.

Lifecycle & cleanup:
- **Retention**: keep last 3 versions per category per session; older → `scratch/history/` (or plan-doc-editor `history/`).
- **Index must point to latest canonical**: stale files marked `archived: true` in Partitions Index.
- **Consolidation**: at session end or migration, merge fragmented partitions into consolidated files.
- **Never delete**: archive always; discard never.

### 3) Caching (reuse stable pointers)
- Cache stable RefSpecs (entrypoints, core files) in session anchors; reuse instead of re-searching.

### 4) Compaction (anchored incremental merge)
- If still over budget, run anchored incremental compaction (see context-compression.md).

For quick scenario→action lookup, see: [optimization-playbook.md](optimization-playbook.md)

> *Source*: `context-optimization` — "Context Budget Allocation… allocate budget by category, reserve buffer, trigger optimization when approaching limits."
