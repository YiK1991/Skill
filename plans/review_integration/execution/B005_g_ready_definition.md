---
name: B005 定义 G-READY 与 PlanApproved
description: >-
  在 integration-router.md 追加 G-READY (Execution Readiness Gate) 可计算条件，并在 plan-template.md 新增 PlanApproved: NO|YES 标志位。
batch_id: B005
title: 定义 G-READY 与 PlanApproved
status: READY
phase: P5
created: 2026-03-02
updated: 2026-03-02
review: none
prerequisites: []
impact_refs:
  - plan-doc-editor/references/integration-router.md
  - plan-doc-editor/assets/plan-template.md
related_investigations: []
cross_refs:
  tracker: execution/_tracker.md
  current: CURRENT.md
  changelog: change_log.md
---

## B Headline
- **Objective**: 定义可计算的 G-READY 门禁，并在 plan 模板中引入 `PlanApproved` 硬开关
- **Inputs**: [integration-router.md](../../plan-doc-editor/references/integration-router.md) · [plan-template.md](../../plan-doc-editor/assets/plan-template.md)
- **DoD**: 路由新增 G-READY 段落；plan 模板 Header/Tail 增加 `PlanApproved` 标记
- **Next actions**: 1. 更新 integration-router.md 的 G-READY 段 2. 更改 plan-template.md
- **Hard constraints**: 门禁规则必须机械可计算

# B005: 定义 G-READY 与 PlanApproved

## Objective
把“细则计划不实施”从软约束变成硬性防错：
1. `G-READY`：定义何为“执行就绪”（无 tracker、无 B-file 或缺骨架均 fail）
2. `PlanApproved`：给 CURRENT 添加人为/系统性的放行开关选项

## Context
当前 gate 映射包含 G-READY，但无判定细则，导致规划半途容易急于写代码。
> Baseline: [integration-router.md](../../plan-doc-editor/references/integration-router.md)

---

## ⚙️ Before You Start (READ FIRST)

| # | Read This | Why |
|---|-----------|-----|
| 0 | [CURRENT.md §0](../CURRENT.md#§0-norms-standards-baseline) | 核心规范 |
| 1 | [plan-template.md](../../plan-doc-editor/assets/plan-template.md) | 需增加 PlanApproved 字段 |

---

## Execution Steps

### Step 1: integration-router.md 新增 G-READY 定义
插入位置：在 `Gate-R 定义` 结束处与 `回流协议` 之间新增 `## G-READY 定义（Execution Readiness Gate）`

```markdown
## G-READY 定义（Execution Readiness Gate）

- **触发**：计划进入 EXECUTING 阶段前
- **通过条件（必须全部满足）**：
  1. `execution/_tracker.md` 存在且包含 ≥1 条非表头任务行
  2. `execution/` 目录下存在至少一个 `B{NNN}_*.md`
  3. 各 Active B-files 具备最小执行结构：`Objective`、`Execution Steps`、`Definition of Done (DoD)`/`ATDD` 三个 block 必须存在（允许 stub 骨架，但区块不可少）。
- **失败动作**：
  - 计划模块 `Status` 回退为 `DESIGNING`
  - 创建或更新 `questions/Q-NNN_exec_ready_<slug>.md`
  - 在 tracker 中对应行标记 `BLOCKED(Q-NNN)`
```

### Step 2: plan-template.md 增加 PlanApproved
在 `## Head Anchor` 和 `## Tail Anchor` 列表里（`Links:` 行下方），补充 `PlanApproved` 标记：

```markdown
- **PlanApproved**: NO
```
默认初始为 `NO`，只允许人工 Review 或明确规则放行后改为 `YES`。

---

## Definition of Done (DoD)
- [ ] `integration-router.md` 含 `G-READY 定义`，且 fail 条件、失败动作完整
- [ ] `plan-template.md` 的 Head / Tail Anchor 皆含 `- **PlanApproved**: NO`

## ✅ Post-Completion Updates

| # | Go To | Do This |
|---|-------|---------|
| 1 | [execution/_tracker.md](../_tracker.md) | B005 → DONE |
| 2 | [CURRENT.md §1](../CURRENT.md#§1-batch-overview) | 更新状态 |
| 3 | [change_log.md](../change_log.md) | 追加变更记录 |

## B Tail Anchor
- **Objective**: 定义可计算的 G-READY 门禁，并在 plan 模板中引入 `PlanApproved` 硬开关
- **DoD**: 路由新增 G-READY 段落；plan 模板 Header/Tail 增加 `PlanApproved` 标记
- **Next actions**: 1. 更新 integration-router.md 的 G-READY 段 2. 更改 plan-template.md
- **Hard constraints**: 门禁规则必须机械可计算
