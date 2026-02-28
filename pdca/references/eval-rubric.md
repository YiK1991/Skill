# PDCA Evaluation Rubric (Quality under Budget)

## Scoring (0–2 each; total 0–10)

### 1) Correctness
- 0: wrong / doesn't run
- 1: partially correct
- 2: correct + passes intended tests

### 2) Evidence Traceability (RefSpec)
- 0: claims without pointers
- 1: some RefSpecs but incomplete
- 2: every key claim/decision has RefSpec (path#anchor or path:Lx-Ly)

### 3) Tool Efficiency (calls + verbosity discipline)
- 0: excessive tool calls / verbose outputs pasted
- 1: some waste but controlled
- 2: minimal necessary tool calls; outputs offloaded/masked; concise default used

### 4) Budget Compliance (triggers handled correctly)
- 0: ignores budget triggers; context bloat
- 1: triggers noticed but actions inconsistent
- 2: triggers hit → masking/partition/compaction applied correctly; buffer preserved

### 5) Deliverable Quality (actionable plan & artifacts)
- 0: unclear steps / missing artifacts
- 1: mostly actionable
- 2: clear plan + artifacts pointers + next steps; no drift

## Pass/Fail Gate (fail-fast)

**Hard requirements (non-negotiable):**
- Correctness must be **2/2** (tests pass or explicitly documented skip reason)
- Evidence Traceability must be **2/2** (every key decision has RefSpec)
- If either is < 2 → **FAIL** regardless of total score

**Soft requirement:**
- Total score must be **≥8/10** for "release"
- If total < 8 but hard requirements met → flag for improvement, do not block

> *Source*: `evaluation` — "Multi-dimensional rubric… evaluate under constraints to avoid quality degradation."
