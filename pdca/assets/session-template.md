---
schema_version: 1
---

# PDCA Session Template

Use this template to track your coding sessions. Copy this for each new session.

## Head Anchor (≤7 lines)
- Goal:
- Current step:
- Next step:
- Hard constraints:
- Key pointers (RefSpec):
- Stable pointers cache (≤5): [entrypoints, core modules, key configs]

---

**Session Date:** YYYY-MM-DD
**Feature:** [Feature name]
**Estimated Time:** [X] hours

## Business Objective

[What are you trying to achieve and why?]

---

## Session Compaction Block (anchored; incremental merge only)

### Intent
- 

### Decisions
- 

### Files touched (read/modified/created)
- read:
- modified:
- created:

### Next steps
- 

### Risks
- 

### Evidence pointers (RefSpec)
- 

---

## ANALYSIS PHASE

### Approach Selected
[After analysis, document the chosen approach]

### Key Patterns Identified
- [Pattern 1]
- [Pattern 2]
- [Pattern 3]

### Discovery Log (Static→Dynamic)
- Static baseline checked: [refs]
- Candidate list (paths): [list]
- Deep reads (RefSpec): [path#anchor / path:Lx-Ly]
- Notes: [why these were loaded]

### Files (RefSpec)
- `src/foo.py:L120-L180`
- `docs/spec.md#contract`
- [etc.]

---

### Context Budget Tracker (Proxy)

| Step | dynamic_reads | inline_excerpts | tool_outputs_offloaded | history_reads | trigger_hit? | action_taken |
|------|---------------|-----------------|------------------------|---------------|--------------|--------------|
| 1    | -             | -               | -                      | -             | -            | -            |

### Compression Trigger Log

| Trigger | Threshold | Hit? | Action | Span summarized | Notes |
|---------|-----------|------|--------|-----------------|-------|
| Steps ≥ 8 | 8 | | | oldest steps | |
| Deep-reads ≥ 30 | 30 | | | oldest steps | |
| Offloads ≥ 6 | 6 | | | tool-heavy span | |
| Budget hits ≥ 2 | 2 | | | budget-related | |

### Partitions Index (Evidence/Notes kept out of session body)

| Partition | File (RefSpec) | Purpose | Updated in step |
|-----------|----------------|---------|-----------------|
| Test runs | scratch/test_runs/TO-*_pytest.txt | full pytest output | - |
| Investigation | scratch/investigation/INV-*.md | hypotheses + F/C | - |
| Design notes | scratch/references/P1_design.md#anchor | interface contract | - |

### Worker Reports Index (Context-Isolated)

Worker detailed notes/logs must be stored as files; session keeps only index + takeaways.

| Worker | Scope | Report file (RefSpec) | Confidence | Key takeaways (≤2 bullets) |
|--------|-------|----------------------|------------|---------------------------|
| W1 | - | scratch/worker_reports/W1_*.md | - | - |

## Recitation Log (≤7 lines each)

### Recite: Session Start
- Goal:
- Current step:
- Next step:
- Constraints:
- Key pointers (RefSpec):

---

### Eval Metrics Snapshot

- dynamic_reads_total:
- tool_calls_total:
- offloads_total:
- masking_actions_total:
- partition_files_created:
- compaction_triggers_hit:
- budget_triggers_hit:
- rubric_score_estimate (0–10):

## PLANNING PHASE

### Number of Steps
[X steps total]

### Checkpoints Planned
[After steps: 3, 6, 9, etc.]

### Risk Flags
- [Risk 1]
- [Risk 2]

---

## IMPLEMENTATION NOTES

### Tool Outputs Index (Offloaded)

| TO-ID | tool | file (RefSpec) | purpose | extracted_to |
|-------|------|----------------|---------|--------------|
| TO-YYYYMMDD-001 | pytest | scratch/tool_outputs/TO-..._pytest_fail.txt | test failure log | Step N |

### Start Time
[HH:MM]

### Progress Log
[Track as you go]

**Step 1:**
- Time: [HH:MM]
- Notes: [What happened]

**Step 2:**
- Time: [HH:MM]
- Notes: [What happened]

[Continue...]

### Deviations from Plan
- [When/Why deviated]

### Interventions Made
- [When you redirected the AI]
- [What was the issue]
- [How you fixed it]

### End Time
[HH:MM]

### Actual Duration
[X] hours [X] minutes

---

## COMPLETION CHECK

### Status
[Complete / Needs Work]

### Tests Passing
[Yes / No - include test count]

### Ready to Close
[Yes / No with reasoning]

### Outstanding Items
- [Item 1]
- [Item 2]

---

## RETROSPECTIVE

### What Worked Well
1. [Success 1]
2. [Success 2]
3. [Success 3]

### What Could Be Better
1. [Improvement 1]
2. [Improvement 2]
3. [Improvement 3]

### Top Learning
[Single most valuable insight from this session]

### Change for Next Time
[One specific, actionable change]

**Type:** [PROMPT / PROCESS / BEHAVIOR]
**Action:** [Exactly what to do differently]

### Quality Metrics
- Total commits: [#]
- Largest commit: [# lines]
- Files touched: [# files]
- Avg lines per commit: [#]
- Test-first discipline: [X% of commits with tests]

---

## KNOWLEDGE CAPTURE

### Patterns Discovered
[Document patterns learned about the codebase]

### Architecture Insights
[Architectural learnings to share with team]

### Refactoring Opportunities
[Technical debt or improvement opportunities noted]

---

## PROMPT UPDATES

### Changes Made to Prompts
1. [Which prompt]
   - Change: [What changed]
   - Why: [Rationale]

---

**Session Complete:** [Date/Time]

---

## Tail Anchor (repeat Head Anchor, ≤7 lines)
- Goal:
- Current step:
- Next step:
- Constraints:
- Key pointers (RefSpec):
