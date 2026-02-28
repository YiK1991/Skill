# Context Compression (Anchored + Incremental Merge)

Optimizes tokens-per-task (including re-fetch costs), not just tokens-per-request.

## When to trigger

**Primary**: 70–80% context utilization (if measurable).

**Proxy triggers (v1)**:

| Trigger | Threshold |
|---------|-----------|
| Steps completed in session | ≥ 8 |
| Dynamic deep-reads (RefSpec items) | ≥ 30 |
| Offloaded tool outputs | ≥ 6 |
| Budget trigger hits | ≥ 2 |

## Session Compaction Block (anchored; do not rewrite from scratch)

Maintain a single persistent block with fixed sections:

```
### Intent
### Decisions
### Files touched (read/modified/created)   ← artifact trail anchor
### Next steps
### Risks
### Evidence pointers (RefSpec; tool_outputs, logs, key excerpts)
```

## Incremental merge rule (critical)

On trigger:
1. Identify the newly-truncated span (oldest steps beyond "keep last N").
2. Summarize **ONLY** that span into the fixed sections above.
3. **Merge** into existing sections (append/update bullets). **Do NOT regenerate full summary.**
4. Keep last 2–3 steps uncompressed for continuity.

## Artifact trail rule

Maintain a separate index for:
- `files_read` / `files_modified` / `files_created`
- Key identifiers (functions, errors, entities)

This is implemented as the "Files touched" section + session Tool Outputs Index.

## Code-safe compression rules
Context compression must never destroy contract information needed for correct reasoning.

**100% preserve (never compress):**

- File paths and symbol names
- Public signatures (function / method / class / interface declarations)
- Type definitions, DTOs, schemas, enums
- Critical comments: invariants, security notes, `// WHY:` annotations
- Import/export statements that define module boundaries

**Allowed to fold (replace body with summary):**

- Function/method body internals (keep signature + 1–3 line behavior summary)
- Boilerplate / scaffolding code
- Test fixtures and generated code (keep public surface)
- Repeated similar blocks (keep first instance, summarize count)

**Recommended fold format:**

```
def calculate_forecast(series: TimeSeries, horizon: int) -> TimeSeries:
    """Applies TFT model with covariates. (~45 lines folded)
    preprocessing → model.predict → post-processing
    """
    ...
```

## Anti-patterns

- ❌ Regenerating the entire summary each time (causes drift).
- ❌ Compressing too early (wastes effort; items may still be needed).
- ❌ Losing artifact trail (files/decisions silently dropped).

> *Source*: `context-compression` — "Optimize tokens-per-task… anchored iterative summarization… trigger at 70–80% utilization… artifact trail must be tracked separately."
