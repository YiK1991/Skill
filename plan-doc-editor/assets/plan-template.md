---
name: <plan_id> <Plan Title>
description: >-
  <One-line purpose of this plan.>
plan_title: <Plan Title>
plan_id: PLAN-YYYY-NNN
status: NORMING
revision: v001
last_updated: YYYY-MM-DD
owners:
  - <name>
---

# <Plan Title>

## Head Anchor
<!-- Recitation Source of Truth. Keep ≤7 lines. Update whenever plan drifts. -->
- **Goal**: <one sentence>
- **Status**: <NORMING|INVESTIGATING|DESIGNING|READY|EXECUTING|CLOSED>
- **Active IDs**: <B001, INV-001, …>
- **Next actions**: 1. … 2. … 3. …
- **Hard constraints**: <key constraints from §0>
- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md)

## How to Read This (Progressive Disclosure)

| Step | Action | Scope |
|------|--------|-------|
| A    | Read §0 + §1/§2 **tables only** (titles, status rows) | Orientation |
| B    | Follow §4 Context Card links to `references/P*` **only when needed** | Design detail |
| C    | Deep-read the specific `B*` file + its referenced `INV-*` **only during execution** | Execution |

> Do NOT full-text scan `references/` or `history/`. Load on demand.

### Static vs Dynamic

- **Static** (this file): §0 norms, §1/§2 status tables, gates, tracker links
- **Dynamic** (load only when triggered): `references/P*`, `investigation/INV-*`, `execution/B*`
- **Rule**: To deep-read a new document, first register it in the corresponding B file's Before-You-Start table with a Why entry.

### Context Budget (Policy v1)

- **Static baseline**: This file (CURRENT) + trackers — index segments only
- **Dynamic reads per batch**: ≤ 8 items
- **History**: Default 0 — load only on explicit regression/backtrace
- **Reserved buffer**: Keep space for new findings; do not pre-fill

## §0 Norms (Standards Baseline)

> Read norm files and establish the baseline before any investigation.

### Norm Sources
- `gemini.md` — project root norms
- `ARCHITECTURE.md` / architecture docs
- Relevant module interfaces (`__init__.py`, type definitions)
- Existing tests — current acceptance baseline

### Data Flow
```
(Draw the data path relevant to this plan)
Input → ... → ... → Output
```

### Interface Contracts (involved in this plan)
| Interface | Input | Output | Norm Source  |
| --------- | ----- | ------ | ------------ |
| ...       | ...   | ...    | gemini.md §N |

### Gates (this plan must satisfy)
| Gate   | Condition                    | Source        |
| ------ | ---------------------------- | ------------- |
| G-ARCH | Dependency direction correct | gemini.md     |
| G-NAME | Naming conventions           | gemini.md §2  |
| G-TEST | ATDD tests pass              | ai-driven-dev |

### Boundary Constraints
- Constraint 1 — source: ...
- Constraint 2 — source: ...

### Baseline Confirmation
- [ ] Norm files read
- [ ] Data flow mapped
- [ ] Interface contracts recorded
- [ ] Gates listed
- [ ] Boundary constraints confirmed

> **NORMING gate**: All above ✅ before entering INVESTIGATING.

---

## §1 Batch Overview
| Batch | Title | Status | Gates | Impact |
| ----- | ----- | ------ | ----- | ------ |
| B001  | ...   | TODO   | —     | → ...  |

→ Detail: [execution/_tracker.md](execution/_tracker.md)

## §2 Investigation Overview
→ Detail: [investigation/_tracker.md](investigation/_tracker.md)

## §3 Batch Dependency Graph
B001 → B002 → ...

## §4 Context Cards

### CTX-P0-BASELINE
→ [P0_baseline.md](references/P0_baseline.md)

### CTX-P1-DESIGN
→ [P1_design.md](references/P1_design.md)

### CTX-P2-IMPLEMENTATION
→ [P2_implementation.md](references/P2_implementation.md)

### CTX-P3-VERIFICATION
→ [P3_verification.md](references/P3_verification.md)

### CTX-P4-RELEASE
→ [P4_release.md](references/P4_release.md)

## §5 Decisions / Open Questions

### Decisions (D-*)
- D-001: ...

### Open Questions (Q-*)
- Q-001: ...

## §6 Iteration Log
| Date       | Trigger Event    | Action           | Impact |
| ---------- | ---------------- | ---------------- | ------ |
| YYYY-MM-DD | Initial creation | Created skeleton | —      |

## Tail Anchor
<!-- Repeat Head Anchor to keep critical plan at the attention edge. Keep in sync. -->
- **Goal**: <one sentence>
- **Status**: <NORMING|INVESTIGATING|DESIGNING|READY|EXECUTING|CLOSED>
- **Active IDs**: <B001, INV-001, …>
- **Next actions**: 1. … 2. … 3. …
- **Hard constraints**: <key constraints from §0>
- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md)
