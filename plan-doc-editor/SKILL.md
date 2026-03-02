---
name: plan-doc-editor
description: This skill should be used when the user asks to "restructure a plan", "split a long plan into phases", "create a plan skeleton", "write back review findings into a plan", "计划", "拆分长计划", "创建计划骨架", "写入审查发现", or mentions progressive disclosure for plan documents. Converts complex goals into layered, iteratable plan-as-skill packages with standards-first design, investigation tracking, and batch task management.
---
# Plan Doc Editor

Restructure **complex plans too long for one context window** into layered modules. Never simplify away details — restructure so humans and AI load only needed context.

## Compatibility (Low coupling)

- **Standalone**: Works with only this folder's `scripts/`, `references/`, and `assets/`.
- **Integrated (optional)**: Can hand off execution to `pdca-ai-coding` and async investigation/review to `jules-cli`, but degrades gracefully if they are not installed.

## Quick Start (30 seconds)

Run from the `plan-doc-editor/` directory (where this SKILL.md lives).

1. Create a plan module skeleton (or copy `examples/minimal-module/`):

```powershell
python scripts/init_plan_skill.py plans <slug> "<title>"
```

2. Run Pass 0 only: open `INDEX.md` + `CURRENT.md` + tracker active rows; write `investigation/INV-000_state_audit.md`.
3. Choose one next hop:
   - Execution → create/activate one `execution/B*.md` and hand off to `pdca-ai-coding` (or execute manually).
   - Investigation/review → create `questions/Q-*.md` (and optionally dispatch via `jules-cli`).

## Strict Mode (gates fully on)

- Always perform **G-SYNC** before any design/task breakdown (see Cold-start).
- Enforce Two-Pass loading + RefSpec links; offload logs/tool output instead of pasting.
- Any new decision/change must land in `references/P*` + `change_log.md` before execution proceeds.

## Cold-start vs Warm-start (choose before proceeding)

| Mode | Trigger | Action |
|------|---------|--------|
| **Cold-start** | First time seeing this plan module / no recent state audit / change_log shows major changes / obvious conflicts | **G-SYNC first**: Pass0 (INDEX+CURRENT+trackers) → write INV-000 state audit → update CURRENT §1 + change_log → then design |
| **Warm-start** | Recent state audit exists + small scope (≤1 B file / few refs) | **Direct execution**: INDEX+CURRENT + active rows → PDCA Lite / Jules task → Plan Update Targets |

> Project context discovery (standalone): read repo-local instructions in this order: AGENTS.md → gemini.md/agent.md/rules.md → architecture docs → plan module (INDEX/CURRENT) → optional .claude/instructions.md.

## PD Protocol (Two-Pass Loading)

Every interaction with a plan module follows **two passes**:

1. **Pass 0 — Index Pass**: Read only `INDEX.md` + `CURRENT.md` index segments (§0/§1/§2 titles & tables, §4/§5 headings). Determine: what to do, which IDs are active, which path to take.
2. **Pass 1 — Deep Pass**: Open specific `execution/B*`, `investigation/INV-*`, `references/P*` only when the task demands it. Never full-text scan.

**Hard rule**: Before deep-reading any new file or section, add it to the B file's "Before You Start" table (with a Why column entry). Read only what you registered.

> *Rationale*: Progressive disclosure keeps agents fast while preserving access to full detail on demand.

## Core Flow

```
Define Standards (§0 Norms)
  → Investigate against standards (偏移检测)
    → Design with evidence
      → Break into batch tasks
        → Execute via PDCA / subagent / Jules
```

## Plan-as-Skill Architecture (two-level flat)

```
<plan_module>/
├── INDEX.md                          # Navigation → CURRENT.md
├── CURRENT.md                        # Norms + routing + status
├── change_log.md                     # Change record
├── questions/                        # 发射井：待解决的疑问或分发给 Jules 的调查任务 (Q-NNN)
├── investigation/                    # 接收箱：Jules 或本地执行的详细调查报告 (INV-NNN)
│   └── _tracker.md
├── execution/                        # 唯一的执行工作区 (B-files)
│   ├── _tracker.md
│   └── B{NNN}_<slug>.md
├── references/                       # 提炼后的契约与设计干货 (Px/Ax)
│   ├── P0_baseline.md ... P4_release.md
│   └── A*_<name>.md                  # Appendices
└── history/                          # 扁平化归档区：存放过期版本、以及提炼完毕的 Q/INV 文件
    └── v{NNN}_YYYYMMDD_CURRENT.md
```

**Max two levels deep.** ID conventions and naming: see [plan-skill-structure.md](references/plan-skill-structure.md).

## Static vs Dynamic Protocol

**Static Context** (always read first):
`INDEX.md` → `CURRENT.md` (§0/§1/§2 tables only) → `execution/_tracker.md` & `investigation/_tracker.md` (active/blocked rows only)

**Dynamic Context** (on-demand deep-read):
`execution/B*` · `investigation/INV-*` · `references/P*` · `questions/Q*` · `history/*`

**When to load dynamic**—only on trigger:

1. User names a specific ID (B/INV/P/Q)
2. Tracker marks a row `active` / `blocked` / `depends_on`
3. B frontmatter pointers: `prerequisites` / `related_investigations` / `impact_refs`
4. CURRENT §4 Context Card links

> *Rationale*: Dynamic context is loaded on-demand; avoid full-text scans.

### Dynamic Context Discovery (Discovery Ladder)

When context is missing, follow this fixed sequence:

1. **Pointer Scan** (zero cost): Read INDEX.md, CURRENT.md index segments, tracker active rows
2. **Pointer Expansion** (structured): Read current B’s frontmatter pointers (`prerequisites` / `impact_refs` / `related_investigations` / `cross_refs`)
3. **Header Scan** (lightweight): For candidate files, read YAML frontmatter + headings only — do not deep-read
4. **Edge-first** (lost-in-middle mitigation): Read target document's Head/Tail anchors first; enter mid-section only if edges insufficient
5. **Targeted Read** (precise): Read only the specific `#anchor` needed; full-file reads only for short files
6. **Record** (audit trail): Add each new deep-read to B’s Before You Start table (Why = trigger that led here)

> Steps 1–4 are free discovery; step 5 is the only token-expensive action; step 6 ensures repeatability.

## Lifecycle State Machine

| State         | Entry Gate                | Fallback on issues |
| ------------- | ------------------------- | ------------------ |
| NORMING       | — (initial)              | norms changed      |
| INVESTIGATING | §0 baseline confirmed    | new unknowns found |
| DESIGNING     | All INV items REVIEWED    | design flaw found  |
| READY         | Design contracts complete | —                 |
| EXECUTING     | ATDD task list complete   | —                 |
| CLOSED        | All DoD satisfied         | —                 |

Any state can fall back to earlier states when issues arise.

## CURRENT.md — Global Entry

### §0 Norms (Standards Baseline)

Before any investigation or design:

1. Read norm sources: `gemini.md`, architecture docs, interfaces, tests
2. Map data flows relevant to this plan
3. Record interface contracts: Input → Output → Error
4. List gates: tests, CI, architectural constraints
5. List boundary constraints from norms

Write into CURRENT.md §0. Confirm before entering INVESTIGATING.

### Remaining Sections

- **§1 Batch Overview**: table of B files + status + gates
- **§2 Investigation Overview**: link to `investigation/_tracker.md`
- **§3 Dependency Graph**: B → B relationships
- **§4 Context Cards**: pointers to `references/`
- **§5 Decisions / Open Questions**: D-\*, Q-\*
- **§6 Iteration Log**: event-driven changes

Template: [plan-template.md](assets/plan-template.md)

## Investigation Design

Investigation = **neutral fact-finding against §0**. Only facts, constraints, and the norm-compliant path.

### Five Dimensions

| Dimension          | Content                               |
| ------------------ | ------------------------------------- |
| Facts              | Actual state of code/config/data      |
| Data Flow          | Source → processing → destination   |
| Interface/Contract | Current interface vs §0 contract     |
| Gate Coverage      | Existing tests/CI for this area       |
| Deviation          | ⚠️ Drift from §0 (or ✅ compliant) |

Template: [investigation-template.md](assets/investigation-template.md)

## Batch Task Design

Each B file in `execution/` is a **behavioral specification** with three zones:

1. **Before You Start** — required reading (norms, tracker, INV reports). Gate: prerequisites DONE.
2. **Discovery Protocol** — handling unexpected issues during execution:
   - Out-of-scope problem → create INV → register in tracker → link back → log
   - Bug in scope → fix + add ATDD criterion + log
   - Design change needed → STOP → update design → fallback status → log
3. **Post-Completion Updates** — mandatory checklist linking tracker, CURRENT.md §1, change_log.md, impacted B files.

### Demand-Based Extraction Protocol (replaces line-count rules)

**Document Roles** (determines extraction policy, not line counts):

| Role | Files | Policy |
|------|-------|--------|
| **Hub** (executable) | `execution/B*`, `CURRENT.md` | Pointers-dense; body = only "next-step must-know". Background/specs → RefSpec to Canonical. |
| **Canonical** (authoritative detail) | `references/P*`, `references/A*` | May be long and dense. Must be PD-navigable: Head Anchor + Index table + stable `##` anchors. |
| **Evidence** (raw outputs) | `investigation/tool_outputs/*`, logs, traces | Never inline. Always offloaded + indexed via Tool Outputs table in INV. |

**Semantic Triggers** (any one triggers extraction/offload — no line-count threshold):

| Signal | Action |
|--------|--------|
| Non-executable content in Hub | Move to `references/P*`; Hub keeps ≤3-line summary + RefSpec |
| Evidence pollution (tool/log/trace) | Offload to `investigation/tool_outputs/`; keep ≤3-line summary + RefSpec |
| Same fact in ≥2 files | Canonicalize to one `references/P*` location; others → RefSpec |
| Missing Index/anchors (not PD-navigable) | Add Head Anchor + Index table + `##` anchors before adding content |
| Cross-B dependency (content referenced by ≥2 B files) | Canonicalize to `references/` |

**Compression Safety Rules** (information must never be lost):

- 100% preserve: IDs, Gate commands, DoD, acceptance criteria, rollback strategy, WHY/constraints, Files touched, Evidence pointers
- Allowed to compress: background prose, long derivations, repeated paragraphs, long examples (offload)
- Compressed text must retain RefSpec (information is "folded", not deleted)

**Inline excerpt limit**: Code/output excerpts inline ≤60 lines (from PDCA); longer → offload + RefSpec.

- Investigations must track temporal validity (valid_from/valid_until/status); see [investigation-temporal-validity.md](references/investigation-temporal-validity.md).
- Entity consistency: use `references/A0_entity_registry.yaml`; see [entity-registry.md](references/entity-registry.md).
- Investigation consolidation: archive/invalidate completed INVs; see [investigation-consolidation.md](references/investigation-consolidation.md).

### Context Budget Allocation (Policy v1)

**Budget buckets** (mapped to plan structure):

| Bucket          | Scope                                                                                   | Default                                                      |
| --------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Static baseline | INDEX + CURRENT (index segments/tables) + tracker active rows                           | Always included                                              |
| Dynamic reads   | Current B + its frontmatter pointers (prerequisites/impact_refs/related_investigations) | On-demand                                                    |
| Tool / logs     | Docx outline, Jules/INV report summaries                                                | On-demand                                                    |
| History         | `history/*`                                                                           | **0** — only on explicit regression/backtrace trigger |
| Reserved buffer | Space for unexpected findings / new evidence                                            | Never pre-fill                                               |

**Proxy budget limits** (v1 — item count, not tokens):

- Per-B dynamic deep-reads: **≤ 8** (excluding static baseline)
- INV deep-reads per B: **≤ 2** (others → ≤3 lines summary + RefSpec)
- P* anchor deep-reads per B: **≤ 3** (excess → merge into P* first, then reference)

**Compression trigger**: When any limit is exceeded → STOP → move detail to `references/` → keep only RefSpec + ≤3 lines in B. Always preserve Head/Tail anchors as the last-cut boundary.

> *Source*: `context-compression` — "design explicit budgets… trigger optimization when approaching thresholds."

### JIT Identifiers Protocol

JIT identifiers = **identifiers, not content**. Cross-file sharing follows three rules:

1. **RefSpec only**: Every cross-file reference uses `[<label>](../<path>.md#<anchor>)`. No copying.
2. **≤3 lines + 1 link**: Inline summaries max 3 lines; anything longer → move to `references/` and link via RefSpec.
3. **Scan-before-read**: Read YAML frontmatter + headings first, then decide whether to deep-read the body. This makes PD's "load on demand" executable.

> *Rationale*: JIT identifiers keep hub docs light; load details only when needed.

Details: [plan-skill-structure.md § Cross-Reference](references/plan-skill-structure.md#cross-reference-protocol-views-not-copies). Template: [batch-template.md](assets/batch-template.md)

### Lost-in-the-Middle Mitigation: Edge Anchors

Long documents suffer from **lost-in-the-middle** — recall drops 10–40% for content in the middle of context. Mitigation:

1. **Head Anchor** (first 5–7 lines after title): Goal / Active IDs / Next actions / Hard constraints / Key links
2. **Tail Anchor** (last 5–7 lines): Repeat the same Head Anchor content
3. **Content restriction**: Anchors contain only navigation/decision/execution info — no prose, no background
4. **Dynamic loading**: Read Head/Tail first; deep-read mid-section only when Discovery Ladder triggers require it
5. **Compression priority**: When over budget, cut mid-section detail first; Head/Tail are the last-cut boundary

**Required on**: `CURRENT.md`, all `B*.md` files. Optional on `INV-*` and `references/P*`.

> *Source*: `context-degradation` — "middle position recall drops 10–40%… place critical information at beginning or end."

### Plan Persistence / Recitation (Protocol v1)

**Plan artifact** = CURRENT.md (Head + Tail Anchors) + tracker active rows. All other files (B/INV/P) are detail carriers, not the plan itself.

**Recitation cadence** — recite at these points:

1. Before starting each Batch (after opening B file)
2. Before any deep-read, major change, or CURRENT write-back
3. After completing a gate transition (e.g. READY → EXECUTING)

**Recitation content** (≤7 lines, from CURRENT Head Anchor + trackers):

- Goal / Status / Active IDs / Next 3 actions / Hard constraints / Links

**Drift fix**: If recitation reveals mismatch (goal/constraints/IDs differ from current work) → update CURRENT Head/Tail Anchors + tracker first, then resume execution.

> *Rationale*: Recitation makes long-running plans resilient to context drift.

## Workflows

### A — Create skeleton

1. Read norms → fill CURRENT.md §0
2. Identify INV needs → populate `investigation/_tracker.md`
3. Create `references/P0_baseline.md`
4. Run: `python scripts/init_plan_skill.py <target_dir> <slug> "<title>"`
5. Transition: NORMING → INVESTIGATING

### B — Investigation

**Decoupling principle**: If the investigation covers multiple dimensions (facts + risks + stats), require Jules to output separate files (`F-NNN`, `R-NNN`) instead of one monolith. Each file can be independently referenced, consumed, and archived.

1. For each TODO in `investigation/_tracker.md`:
   - Decide mode: **recon** (one-shot) or **snapshot** (long-lived, overwrite)
   - Jules: self-contained prompt via `/jules` (independent, parallelizable)
   - Local: execute in current session (needs context/code execution)
2. Write to `investigation/INV-NNN_<slug>.md` (recon) or `@Snapshot_<slug>.md` (snapshot) → update `_tracker.md` with mode
3. Review each report → mark REVIEWED → check G-INV gate
4. **Snapshot maintenance**: Re-run the same prompt after code changes. The snapshot file is overwritten in-place to reflect current state. It stays ACTIVE until the monitoring goal is met.

### C — Design refinement (event-driven)

1. **Intake (提炼)**: Extract Findings (F-\*) and Constraints (C-\*) from completed reports in `investigation/`
2. **Canonicalize**: Update `references/P1_design.md` + relevant B files with the core facts
3. **Archive (降噪)**: Move the processed `questions/Q-NNN` and `investigation/INV-NNN` files directly to `history/` and mark them `# ARCHIVED`.
4. Check G-DESIGN gate; new unknowns → back to Workflow B
5. Freeze CURRENT.md to `history/`

### D — Task breakdown

1. Break `references/P2_implementation.md` into B files
2. Fill: objective, prerequisites, ATDD acceptance, steps, DoD
3. Update `execution/_tracker.md` → check G-READY gate
4. When handoff targets Jules parallel implement:
   a. Modification whitelist per task MUST NOT overlap
   b. Each TASK file contains complete extracted task text (no "see CURRENT.md §3")
   c. Interface contracts must be designed and frozen before dispatch

### E — Execution handoff

| Method           | Skill                           | When                         |
| ---------------- | ------------------------------- | ---------------------------- |
| PDCA cycle       | `/pdca` workflow              | Standard development         |
| Subagent         | `subagent-driven-development` | Same-session batch execution |
| Parallel session | `executing-plans`             | Independent session          |
| Jules dispatch   | `/jules` workflow             | Independent tasks            |

### F — Plan update (event-driven)

1. Record in `change_log.md` → update affected B files
2. Assess cascade via `impact_refs`
3. Status fallback if needed: design→DESIGNING / investigation→INVESTIGATING / norms→NORMING
4. Freeze old CURRENT.md to `history/`

## Non-Negotiables

1. **Standards first** — NORMING reads norms, maps flows, records contracts
2. **Investigate against standards** — every INV checks §0 deviation
3. **Five dimensions** — facts / data flow / interface / gates / deviation
4. **B file = behavioral guide** — Before Start / Discovery Protocol / Post-Completion
5. **Two-level flat** — max `plan_module/folder/file.md`
6. **Event-driven** — no fixed rounds; new input triggers update
7. **Cascade awareness** — `impact_refs` + reflection section
8. **Stable IDs** — INV-\*, F-\*, C-\*, B\*, D-\*, Q-\*, R-\*, ATDD-\*
9. **Gate-driven** — state transitions require gate passage
10. **Views-not-copies** — one source of truth, link references
11. **Closed-loop** — batch completion requires updating tracker + CURRENT.md §1 + change_log.md
12. **Link-first** — inline ≤3 lines; full detail one link away; Hub files contain only executable/navigational content (non-executable → extract to Canonical)
13. **Discovery-then-record** — unexpected issues → INV file + tracker + change_log; no silent fixes
14. **PD two-pass** — Index Pass first (INDEX + CURRENT tables), Deep Pass only for registered items
15. **Gate-J (Jules Review)** — B file DoD 含 `gate_j: required` 时，须在 DONE 前完成 Jules review PR 合并。产物：`investigation/INV-*_jules_review.md`。失败：回退为 blocked，写 Q-NNN 阻塞 tracker。
16. **G-SYNC（强制同步门禁）** — 进入 DESIGNING 前必须通过：(1) Pass0 读 INDEX/CURRENT 表格段 + `_tracker.md` active/blocked 行；(2) 写 `investigation/INV-000_state_audit.md`（含 Facts / Conflicts & Resolutions / 缺口清单）；(3) 更新 `CURRENT.md §1` + `change_log.md`；(4) Tracker sanity check（10 秒校验：每行 `|` 数量一致、header 分隔行存在、无空行打断表格）。四步全做完方可进 DESIGNING。
17. **No-chat-only-planning** — 对话中产生的任何新架构决策/方案变更，必须落盘到 `references/P*`（含 D-xxx 锚点）+ 记入 `change_log.md`，否则不允许进入 Workflow D（Task Breakdown）。纯对话推进等于未记录，不算完成。

## Skill Integration

```
plan-doc-editor (this skill)
  ├── Investigation dispatch → /jules workflow → Jules agent
  │     └── Parallel dispatch → dispatching-parallel-agents
  ├── Plan design → ai-driven-dev (ATDD ID + Gate norms)
  │     └── Gate checks → kaizen (DoD + No Mixed States)
  └── Execution handoff
        ├── /pdca workflow
        ├── subagent-driven-development
        └── executing-plans
```

**Routing contract**: [integration-router.md](references/integration-router.md) — 任务类型→Skill 路由、统一输出契约、门禁映射、回流协议

## Bundled Resources

### Scripts

- **scripts/init_plan_skill.py** — initialize plan module skeleton
- **scripts/docx_outline.py** — extract DOCX heading outline. **Rule**: When the source plan is a long `.docx`, run this script first to get the heading structure, then decide which sections to deep-read. Never load the full DOCX into context.
- **scripts/split_plan_with_markers.py** — split Markdown by `<!-- FILE: ... -->` markers

### References

- **references/plan-skill-structure.md** — ID conventions, naming, status enums, cross-reference protocol

### Assets

- **assets/plan-template.md** — CURRENT.md template
- **assets/batch-template.md** — B file template
- **assets/investigation-template.md** — INV report template
- **assets/plan-template.docx** — DOCX template
