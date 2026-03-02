# PDCA AI Coding — Examples

## Lite Mode (single-file / small change)

Use when Lite eligibility is true (small diff, no cross-module coupling).

1. Write the failing test (RED).
2. Implement the smallest fix (GREEN).
3. Refactor (keep tests green).
4. Run the narrowest relevant tests, then the broader suite if available.

## Full PDCA (copy/paste prompts)

Use when the change is non-trivial, risky, or the repo is unfamiliar.

```text
Load references/analysis-prompt.md and analyze: <objective>
Load references/planning-prompt.md and create the execution plan
Load references/implementation-prompt.md and execute the plan
Load references/completion-prompt.md and verify our work
```

## Strict Mode (gates fully on)

- Use the ATDD overlay and treat Gate outputs as evidence.
- Prefer small commits and keep changes reviewable.
- If a `plan-doc-editor` module exists, do not edit trackers directly; return `Plan Update Targets`.

See also:
- `assets/TEST_PLAN_TEMPLATE.md`
- `assets/ARCHITECTURE_LOCK_TEMPLATE.md`
- `references/working-agreements.md`

