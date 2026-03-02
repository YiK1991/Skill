---
name: Jules CLI Orchestration
description: >-
  This skill should be used when the user asks to "send a task to Jules",
  "dispatch Jules task", "submit prompt to Jules", "create Jules session",
  "check Jules status", "manage Jules workflow", "review Jules results",
  "send followup to Jules", or needs to orchestrate asynchronous code
  review/research/implementation tasks via Jules API/CLI.
  当用户提到"发任务给Jules"、"Jules调度"、"提交Jules任务"、
  "Jules会话管理"、"审查Jules结果"时使用此技能。
---

# Jules CLI Orchestration

Submit asynchronous tasks to Jules, track status, review results via PR, and iterate.

## Compatibility (Standalone-first)

- **Standalone**: Run the scripts in this folder (`scripts/dispatch_prompt_pack.py`, `scripts/jules_bridge.py`); no other skills required.
- **Integrated**: If using `plan-doc-editor`, point Document Placement to your plan module (e.g. `<plan_module>/investigation/`) and return `Plan Update Targets` for write-back.

## Quick Start (30 seconds)

Run from the `jules-cli/` directory (where this SKILL.md lives).

1. Copy `examples/minimal-pack/` to a temp folder (or create `PACK.md` + `tasks/TASK-*.md`).
2. Submit (always pass `--starting-branch` explicitly):

```powershell
python scripts/dispatch_prompt_pack.py `
  --pack-dir C:\temp\jules_pack `
  --repo <owner/repo> `
  --starting-branch <branch>
```

3. Monitor status:

```powershell
python scripts/jules_bridge.py --json status --session-id <id>
```

## Strict Mode (gates fully on)

- Before dispatch: complete **H1–H7** checklist below (copy the XML block and fill it explicitly).
- After Jules completes (review/research): run `python scripts/gate_pd_output.py <report.md>` before merge.

## Cold-start vs Warm-start (choose before proceeding)

| Mode | Trigger | Action |
|------|---------|--------|
| **Cold-start** | First time dispatching to this repo / no recent pack / major plan changes | **Prep first**: verify repo contract (gemini/agent/rules), confirm pack structure (PACK.md + tasks/), run pre-flight checklist below |
| **Warm-start** | Familiar repo + existing pack + incremental tasks | **Direct dispatch**: update PACK.md pending tasks → `dispatch_prompt_pack.py` → gates handle the rest |

> All submit operations go through `dispatch_prompt_pack.py` (dispatch-only invariant). Bridge is for status/wait/approve only.

## Roles

- **Jules** — Lightweight executor / patch generator (review, research, test, small fixes)
- **Local AI (Codex/Claude etc.)** — Task decomposition / review / prompt revision
- **Human** — Final gate / merge decision

---

## ⛔ HARD STOP — Pre-Flight Checklist (MANDATORY before ANY submit)

> **CRITICAL: Complete ALL checks below BEFORE calling any submit command.
> Skipping ANY item causes FAILED sessions and wastes quota.**

| #  | Check | Rule | Pitfall |
|----|-------|------|---------|
| H1 | **Encoding & language** | Prompt file MUST be **UTF-8**. CJK allowed in body. Control-plane ids (task_id, paths, section anchors like `## Governance Capsule`) MUST be ASCII. | P1: dispatch script auto-handles UTF-8 transport; GATE-UTF8 validates |
| H2 | **`--starting-branch`** | MUST specify `--starting-branch` explicitly (e.g. `master`). Do NOT assume `main`; GATE-6 will verify the branch exists on remote. | P11: Undetectable default → `fatal: branch not found` → FAILED |
| H3 | **Prompt Envelope** | MUST use the correct template from `references/prompt-envelope-review.md` (for review) or `references/prompt-envelope-implement.md` (for implement). Copy the template structure verbatim. | No envelope → Jules cannot parse intent → FAILED |
| H4 | **Dispatch method** | MUST use `dispatch_prompt_pack.py` for submission. NEVER call `jules_bridge.py submit` directly. | P11: Manual calls bypass GATE-6 branch validation → silent FAILED |
| H5 | **ASCII-safe path** | Source paths with CJK are allowed — dispatch auto-copies to ASCII-safe temp (GATE-2). For reliability, prefer ASCII pack-dir/filenames. | P3: Non-ASCII paths handled by GATE-2; manual copy no longer required |
| H6 | **Output path declaration** | Prompt MUST include Document Placement block specifying allowed output paths. Multiple files are allowed within declared paths. | P6: Jules creates files outside declared paths → PR rejection |
| H7 | **Governance Capsule** | Prompt MUST include `## Governance Capsule (MANDATORY)` section with Authority chain, Output Contract fields, and Stop Conditions (§4.5 in templates). | P13: Monolithic output without PD structure → unprocessable |

### Consequence of skipping
Every FAILED session wastes Jules quota. Three consecutive failures suggest a systemic issue — STOP, re-read `references/operational-pitfalls.md`, then retry.

### MANDATORY RITUAL: Pre-Flight Verification

Before running any dispatch command, output this XML block to force token-by-token verification:

```xml
<PreFlight_Check>
  <H1>Confirmed: Prompt is UTF-8; control-plane ids are ASCII</H1>
  <H2>Confirmed: --starting-branch specified explicitly (GATE-6 will verify)</H2>
  <H3>Confirmed: Using correct envelope template (review/implement)</H3>
  <H4>Confirmed: Using dispatch_prompt_pack.py, NOT jules_bridge.py</H4>
  <H5>Confirmed: Source paths acceptable (GATE-2 handles ASCII conversion)</H5>
  <H6>Confirmed: Document Placement block included in prompt</H6>
  <H7>Confirmed: Governance Capsule included</H7>
</PreFlight_Check>
```

> Rationale: LLMs tend to skip checklist items via "lazy evaluation". Forcing explicit generation of each line reduces omission rate from ~15% to ~0.1%.

---

## Standard Single-Task Workflow (Step-by-Step)

For submitting ONE task (the most common case):

### Step 1: Write the prompt file (UTF-8; CJK allowed)

Read the appropriate template FIRST:
- Review/research task → `view_file` on `references/prompt-envelope-review.md`
- Implement/test task → `view_file` on `references/prompt-envelope-implement.md`

Write the prompt following the template structure exactly. Save as e.g. `TASK-B007-REV.md`.

### Step 2: Create a minimal prompt pack directory

```
C:\temp\jules_pack\
├── PACK.md          ← task table (see references/prompt-pack.md)
└── tasks\
    └── TASK-B007-REV.md
```

PACK.md minimal content:
```markdown
# Pack: B007 Review
| task_id | file | status |
|---------|------|--------|
| TASK-B007-REV | TASK-B007-REV.md | pending |
```

### Step 3: Verify the pre-flight checklist (H1–H7)

Confirm all 7 items. If ANY fails, fix before proceeding.

### Step 4: Submit via dispatch script

```powershell
python scripts/dispatch_prompt_pack.py `
  --pack-dir C:\temp\jules_pack `
  --repo YiK1991/Amazon_SaaS_ERP `
  --starting-branch master
```

Check exit code: 0 = success, 1 = failure (report to user immediately).

### Step 5: Monitor status

```powershell
python scripts/jules_bridge.py --json status --session-id <id>
```

> **Asynchronous Yielding (CRITICAL):**
> Jules tasks take 5-20 minutes. **NEVER** write a polling loop or `while True` to check status.
> After dispatch, record session_id(s) and **IMMEDIATELY suspend execution**.
> Tell the user: *"Tasks dispatched to Jules. Pausing to save tokens. Please ping me when Jules finishes."*
> Continuous polling burns local model context tokens with zero value.

---

## Core Principles

1. **Small & clear tasks** — One prompt covers one aspect; declare allowed file scope; provide verifiable acceptance criteria.
2. **Verifiable ACK** — Submission succeeds ONLY when output contains `session_id` + `session_url` + `idempotency_key`.
3. **PR-Only** — All output via PR. **NEVER use `jules remote pull`**.
4. **Session-internal loop** — Prefer `sendMessage` for same-session iteration; use PR comment `@Jules` after session completes.
5. **Architecture red lines** — Clean Architecture + SoC; no domain boundary violations; no NIH syndrome; domain-semantic naming (NO `utils.py`, `common.py`).
6. **CI quality red line** — Code changes must not break tests; no skip/comment workarounds.
7. **Three feedback channels** — Plan loop → In-flight loop (sendMessage) → PR loop (`@Jules`).
8. **Unified labels** — Every task carries `RUN-ID`, `ASPECT-ID`, `CTX-ID`.
9. **UTF-8 + control-plane ASCII** — Prompt files MUST be UTF-8. CJK allowed in body. Control-plane identifiers (task_id, paths, section anchors) MUST be ASCII. PowerShell pipe is forbidden. See P1.
10. **Focused > Generic** — Derive tasks from concrete plan decisions, not broad review dimensions. See P5.
11. **State machine re-entry** — Only return to main flow on: `AWAITING_PLAN_APPROVAL` (C-tier only), `AWAITING_USER_FEEDBACK`, `FAILED`, `COMPLETED`.

## Task Tiers

| Tier | Scenario | `requirePlanApproval` | Interaction | Notes |
|------|----------|----------------------|-------------|-------|
| **A** | Pure review/research (no code changes) | `false` | Zero | Planning Critic auto-guards |
| **B** | Low-risk coding (add tests, small fixes) | `false` | Minimal | Strong Envelope + `AUTO_CREATE_PR` |
| **C** | High-risk (change contracts/permissions) | `true` | Approval once | Session pauses at `AWAITING_PLAN_APPROVAL` |

> Default: Auto-approve plans + Planning Critic, zero interaction, parallel by default (group by conflict surface), re-enter main flow only on state triggers.

## Batch Submission Rules

1. **Isolate new from old**: New batch task files MUST NOT coexist with completed tasks in the same `tasks/` directory.
2. **PACK.md first**: Update PACK.md task table before submission. New tasks = `pending`, completed = `submitted/completed`.
3. **Always use dispatch script**: NEVER loop `jules_bridge.py submit` manually. Use `dispatch_prompt_pack.py` (built-in path safety + smoke test + GATE-6 branch validation).
4. **ASCII paths**: Script auto-copies from CJK paths to temp. No manual handling needed.
5. **Check exit code**: exit 0 = all success, exit 1 = failures or plan/actual mismatch. MUST report to user.

## Prompt Envelope (select by intent)

Each prompt MUST use the corresponding template. **NEVER mix templates.**

| Intent | Template | Jules Role |
|--------|----------|------------|
| `implement` / `test` / `release` | **`references/prompt-envelope-implement.md`** | Developer — may modify code |
| `review` / `research` | **`references/prompt-envelope-review.md`** | Auditor — **code modification FORBIDDEN**, output .md report only |

Routing guide and "further modification" message template: **`references/prompt-envelope.md`**

## Task Design: Focused Investigation

Derive review tasks from **specific plan decisions** (not broad dimensions):
1. Lock on one specific decision (e.g. "D-001: Dialog Reset Strategy")
2. List 4-6 questions requiring code evidence
3. Specify output format (comparison table, dependency graph, data flow trace)
4. Include mandatory Document Placement CAUTION block (see P6)

## Additional Resources

### Reference Files

- **`references/operational-pitfalls.md`** — **Critical: 11 field-proven pitfalls** (encoding, ghost sessions, path corruption, idempotency, task design, placement rules, --parallel, subprocess, batch template, dispatch scope, branch default)
- **`references/workflow-commands.md`** — Complete CLI commands, JSON output, batch templates, plan approval strategy, session strategy
- **`references/prompt-envelope.md`** — Prompt Envelope routing guide & "further modification" message templates
- **`references/prompt-envelope-implement.md`** — Implement/test task prompt template (with architecture & CI constraints)
- **`references/prompt-envelope-review.md`** — Review/research task prompt template (READ-ONLY, with architecture checklist + structured report template + anti-hallucination guardrails)
- **`references/prompt-pack.md`** — Prompt Pack directory structure & PACK.md template
- **`references/jules-api-notes.md`** — Jules API minimal facts (5 core calls + state machine)
- **`references/jules-tools-notes.md`** — Jules CLI common commands & common pitfalls
- **`references/cli-reference.md`** — Jules CLI installation & command quick reference
- **`references/plan-as-skill-integration.md`** — Disclosure-style context: provide only current-phase minimal context to Jules

### Scripts

- **`scripts/jules_bridge.py`** — Stable local entry point (API mode, JSON output, default `AUTO_CREATE_PR`)
- **`scripts/dispatch_prompt_pack.py`** — Prompt Pack batch dispatcher (GATE-1/1b/UTF8/2/2b/4/6/7/FFFD/3 + --no-cache + Governance Capsule)
- **`scripts/gate_pd_output.py`** — Post-execution quality gate: validates PD-OUT v1 structure (run before PR merge)
- **`scripts/jules_dispatch.py`** — Lightweight dispatch helper
