# Recitation Protocol (Plan Persistence)

Long tasks drift: plans fall out of attention. Persist plan in files and recite briefly to re-orient.

## Recitation source (priority order)

1. If plan-doc-editor present: CURRENT Head/Tail + tracker active rows + selected B headline
2. Otherwise: Session Head Anchor + last step summary + dynamic read list (RefSpec)

## Cadence (when to recite)

- Start of session
- Before each step
- After each step (update anchors)
- After any failure / blocker resolution
- Before completion summary

## Output format (≤7 lines)

- **Goal**
- **Current step**
- **Next step**
- **Hard constraints**
- **Key pointers** (RefSpec)

## Drift fix

If recitation conflicts with current actions: **STOP** → update anchors/plan artifacts → continue.

## Truth priority (consistency rule)

1. **Session Head Anchor** is the single source of truth (≤7 lines, edge-favored position).
2. **Session Compaction Block** is the historical summary; it merges FROM anchors/steps, never contradicts the anchor.
3. **Conflict resolution**: fix Head Anchor first → then incrementally merge into Compaction Block.
4. **Recitation Log** updates must propagate to both Anchor and Compaction Block within the same step.

> *Source*: `context-degradation` — "Edge positions have highest attention"; `context-compression` — "Anchored summarization must stay consistent to avoid drift."

> *Source*: `filesystem-context` — "Plan Persistence: plans fall out of attention in long tasks… persist in files and re-read to re-orient."
