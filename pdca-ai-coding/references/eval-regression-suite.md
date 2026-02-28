# Regression Suite (Small, Fixed)

Fixed task set for validating prompt/rule changes under budget constraints.

## Task Set (v1)

| ID | Scenario | Forces | Expected failure mode (anti-example) |
|----|----------|--------|--------------------------------------|
| T1 | Simple bugfix (single-file) + unit test update | Correctness baseline | None (happy path) |
| T2 | Multi-file refactor with existing pattern constraints | Traceability + plan quality | Missing RefSpec on key decisions |
| T3 | Failing test triage with **500+ line logs** | Offloading / masking / tool efficiency | ❌ Logs pasted inline instead of offloaded; masking not triggered |
| T4 | **Conflicting evidence** (2 sources disagree on root cause) | Temporal validity + conflict resolution | ❌ Conflict silently resolved; no F/C with `valid_from/superseded_by` |
| T5 | Multi-hypothesis solution selection (optional) | Worker protocol + context isolation | ❌ Worker returns >12 lines or >8 RefSpecs |

## Metrics to record

| Metric | Source |
|--------|--------|
| Rubric score (0–10) | eval-rubric.md |
| dynamic_reads_count | Budget Tracker |
| tool_outputs_offloaded | Tool Outputs Index |
| masking_actions_count | Compression Trigger Log |
| compaction_triggers_hit | Compression Trigger Log |
| tool_calls_count | Eval Metrics Snapshot |

## Regression process

1. **Before** changing prompts/rules: run T1–T3, record rubric + metrics.
2. **After** change: run T1–T3 again, compare.
3. If rubric drops or evidence traceability < 2/2 → rollback/fix.
4. Periodically run T4–T5 to validate advanced protocols.

> *Source*: `evaluation` — "Continuous evaluation under real constraints… compare strategies on fixed task sets."
