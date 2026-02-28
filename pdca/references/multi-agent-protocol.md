# Multi-agent Protocol (Context Isolation)

Workers enable parallel investigation while keeping the supervisor context clean.

## When to spawn workers (triggers)

Use workers ONLY when:
1. Wide search needed (many modules / large codebase)
2. Multiple hypotheses/solutions to evaluate in parallel
3. Multi-module incident triage (independent threads)

## Worker scope definition (mandatory per worker)

Each worker must have:
- `scope`: what area/module/hypothesis to investigate
- `stop_condition`: specific exit criteria (e.g., "find 2 candidate files + 1 root cause")
- `max_refspecs`: ≤8 evidence pointers per worker
- `max_steps`: ≤5 tool calls per worker (prevents unbounded exploration)

## Worker constraints (hard)

- Output must be ≤12 lines total (excluding RefSpecs list).
- Must include:
  - 3–7 line summary
  - `confidence`: low | med | high
  - `evidence`: RefSpec list (pointers to files/logs)
  - `next_action`: 1-line recommendation
- No long prose. Bulk evidence must be offloaded to a file and referenced.

## Worker output schema

```
WORKER_REPORT:
- scope:
- findings (≤3 bullets):
- evidence (RefSpec list):
- confidence:
- recommended next step:
```

## Supervisor rules

1. Supervisor never ingests raw worker logs.
2. Supervisor only reads WORKER_REPORT + RefSpecs as needed (targeted).
3. Merge by updating: Session Compaction Block (Decisions / Next steps / Evidence pointers).
4. Record each worker in the Worker Reports Index (session-template).

## Anti-patterns

- ❌ Spawning workers for trivial single-file tasks
- ❌ Workers returning full logs/dumps (must offload)
- ❌ Supervisor pasting worker output verbatim into session

> *Source*: `multi-agent-patterns` — "Context isolation… supervisor bottleneck… constrain worker output and externalize details."
