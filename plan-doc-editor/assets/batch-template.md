---
name: B001 <Batch Title>
description: >-
  <One-line purpose of this batch.>
batch_id: B001
title: <Batch Title>
status: TODO
phase: P1
created: YYYY-MM-DD
updated: YYYY-MM-DD
prerequisites: []          # Dynamic pointer: B### IDs that must be DONE before this batch
impact_refs: []            # Dynamic pointer: references/P*.md#anchor RefSpecs
related_investigations: [] # Dynamic pointer: INV-### or investigation/INV-*.md RefSpecs
cross_refs:
  tracker: execution/_tracker.md
  current: CURRENT.md
  changelog: change_log.md
  inv_tracker: investigation/_tracker.md
---

## B Headline
- **Objective**: <one sentence>
- **Inputs**: <RefSpec links to prereqs/INVs>
- **DoD**: ATDD-001 ⬜ | ATDD-002 ⬜
- **Next actions**: 1. … 2. … 3. …
- **Hard constraints**: <from §0 norms>

# B001: <Batch Title>

## Objective
One sentence goal.

## Context
2-3 sentences background. **RefSpec only** — any context >3 lines must live in `references/` and be linked here.
→ Baseline: [P0_baseline.md#section](../references/P0_baseline.md#section)

---

## ⚙️ Before You Start (READ FIRST)

> **This section tells you what to read and why. Do not skip.**

| # | Read This                    | Why                                                       |
|---|------------------------------|-----------------------------------------------------------|
| — | **Static baseline** | |
| 0 | [INDEX.md](../INDEX.md)      | Confirm correct module + CURRENT.md is the sole entry      |
| 1 | [CURRENT.md §0 Norms](../CURRENT.md#§0-norms-standards-baseline) | Understand the standards this task must comply with        |
| 2 | [execution/_tracker.md](../execution/_tracker.md) | See this batch's current status, dependencies, and blockers |
| — | **Dynamic (from frontmatter pointers)** | |
| 3 | Investigation reports below  | Absorb the facts — don't re-investigate what's already known |
| 4 | `prerequisites` (frontmatter)| Confirm all prerequisite batches are DONE before starting  |
| 5 | `/pdca` skill (可选执行)      | 这类明确了 ATDD-ID 的任务，极度推荐用 PDCA 工作流来开发    |

**Gate check**: If any prerequisite batch is not DONE, **STOP**. Do not begin.

> ⚠️ **Deep Pass only**: Do not full-text scan `references/` or `history/` beyond what this table lists. To add a new reading item, first add a row to this table (with Why) before reading it.

> 🔍 **If context is missing**: Follow the Discovery Ladder (Pointer Scan → Pointer Expansion → Header Scan → Targeted Read). Add each new deep-read to the table above (Read This = RefSpec, Why = trigger).

> 📊 **Budget check** (before starting work):
> - Dynamic deep-reads (excluding static #0/#1/#2): **≤ 8**
> - INV deep-reads: **≤ 2**
> - P* anchors: **≤ 3**
> - If exceeded: **STOP** → move detail to `references/P*` → keep only RefSpec + ≤3 lines here.

## 🔁 Recitation (Start of Batch)
> Read CURRENT Head Anchor + trackers active rows. Write ≤7 lines:
> - Goal / Status / Active IDs / Next actions / Constraints
> - If drift detected: update CURRENT anchors first, then proceed.

---

## Status
- **Gates**: G-INV ⬜ | G-DESIGN ⬜ | G-IMPL ⬜
- **ATDD**: ATDD-001 ⬜ | ATDD-002 ⬜

## Investigation Dependencies
| ID      | Topic | Method      | Status | Key Findings (≤3 lines) |
| ------- | ----- | ----------- | ------ | ----------------------- |
| INV-001 | ...   | jules/local | ⬜      | —                       |

→ Detail: [INV-001](../investigation/INV-001_xxx.md)

## Design Points
Key interface/contract content **inline here** (≤10 lines, limited to signatures & key constraints). All other design detail → `references/P1_design.md` contract section via RefSpec.
→ Full definition: [P1_design.md#contract-B001](../references/P1_design.md#contract-B001)

### Files Involved
- Create: `path/to/new.py`
- Modify: `path/to/existing.py:L42-60`
- Test: `tests/path/test_xxx.py`

## Execution Steps

### Step 1: <step name>
- **Acceptance**: `ATDD-001: <assertable description> → expected(code)`
- Write failing test → confirm fail → write impl → confirm pass → commit

### Step 2: <step name>
- **Prerequisite**: Step 1
- **Acceptance**: `ATDD-002: ...`

---

## 🔍 遇坑记录 (Discovery Protocol)

如果写代码时发现设计有大坑或依赖超出当前 scope：**别硬写**。去 Tracker 记下阻塞状态，去 `questions/` 目录下新建一个 `Q-NNN` 文件把现场和报错留下，派给 Jules 调查。当前执行终止。小 Bug 直接就地修。

---

## Definition of Done (DoD)
- [ ] All ATDD-ID tests pass
- [ ] Interface contract satisfied
- [ ] No Mixed States
- [ ] Post-Completion Updates (below) ALL executed

## ✅ Post-Completion Updates

> **MANDATORY** — execute ALL rows immediately after ATDD tests pass.
> Skipping any item causes documentation drift. This is not optional.

| # | Go To                                | Do This                                                         |
|---|--------------------------------------|-----------------------------------------------------------------|
| 1 | [execution/_tracker.md](../execution/_tracker.md) | Set this batch status → `DONE`, fill completion date            |
| 2 | [CURRENT.md §1](../CURRENT.md#§1-batch-overview) | Update status column for this batch                             |
| 3 | [change_log.md](../change_log.md)    | Append: `YYYY-MM-DD: B{NNN} — <one-line summary>`              |
| 4 | Each file in `impact_refs`           | Open → review its Reflection & Cascade → update if affected     |
| 5 | [investigation/_tracker.md](../investigation/_tracker.md) | If any INV was opened/closed during execution, update status    |
| 6 | This file's ChangeLog (below)        | Record completion date and outcome summary                      |

## Reflection & Cascade
> This batch's changes **may affect**: B002 (shared interface)
> This batch **is affected by**: —

## ChangeLog
- YYYY-MM-DD: Created

## 🔁 Recitation (End of Batch)
> Before marking DONE, verify:
> - [ ] CURRENT Head/Tail Anchors still accurate? Update if needed.
> - [ ] Tracker status updated for this batch?
> - [ ] B Headline "Next actions" cleared or updated?

## B Tail Anchor
<!-- Keep in sync with B Headline above -->
- **Objective**: <one sentence>
- **DoD**: ATDD-001 ⬜ | ATDD-002 ⬜
- **Next actions**: 1. … 2. … 3. …
- **Hard constraints**: <from §0 norms>
