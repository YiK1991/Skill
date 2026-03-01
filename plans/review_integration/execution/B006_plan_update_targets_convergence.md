---
name: B006 收敛 Plan Update Targets
description: >-
  在 integration-router.md 中明确：Plan Update Targets 默认触达最多 3 个目标文件，迫使数据 canonicalize 收敛到源头。
batch_id: B006
title: 收敛 Plan Update Targets
status: READY
phase: P6
created: 2026-03-02
updated: 2026-03-02
review: none
prerequisites: []
impact_refs:
  - plan-doc-editor/references/integration-router.md
related_investigations: []
cross_refs:
  tracker: execution/_tracker.md
  current: CURRENT.md
  changelog: change_log.md
---

## B Headline
- **Objective**: 限制 Plan Update Targets 输出面，强制采用 Canonicalization，降低文档同步导致的“漂移”故障。
- **Inputs**: [integration-router.md](../../plan-doc-editor/references/integration-router.md)
- **DoD**: 路由器契约部分明确记录 ≤3 Target 制约以及对应的收敛规范
- **Next actions**: 1. 更新 integration-router.md 的输出规范段落
- **Hard constraints**: 不改变四字段契约名称，仅限定行为

# B006: 收敛 Plan Update Targets

## Objective
降低“更新多处散落事实导致的漂移概率”，让回流修改默认集中在少数真实源文件（Single Source of Truth）。

## Context
Worker 完成工作时，四字段包含了 Plan Update Targets。当前没有数量限制，它容易在几十个引用上“撒胡椒面”，产生巨大的扩散性修改成本与审查摩擦。
> Baseline: [integration-router.md](../../plan-doc-editor/references/integration-router.md)

---

## ⚙️ Before You Start (READ FIRST)

| # | Read This | Why |
|---|-----------|-----|
| 0 | [CURRENT.md §0](../CURRENT.md#§0-norms-standards-baseline) | 更新收敛原则 |

---

## Execution Steps

### Step 1: integration-router.md 附加收敛约束
在 `## 统一输出契约` 节（或其子描述中），补充 `Plan Update Targets` 的目标文件收敛规范约束：

```markdown
> **更新面收敛原则**：`Plan Update Targets` 默认最多触达 **3 个目标文件**（每个保留 RefSpec + ≤3行编辑建议）。
> - **建议目标**：`CURRENT.md#...` (状态修改)、`references/Px_*.md#...` (主源设计)、`change_log.md` (变更)。
> - **处理超额记录**：如确需更新超过 3 个文件目标，务必先在实施端进行 Canonicalization（把重复事实合并回单一 Px 文档），在 Targets 中只反馈该一处单一更新。
```

---

## Definition of Done (DoD)
- [ ] `integration-router.md` 的 `统一输出契约` 段包含“默认最多触达 3 个目标文件”的 `更新面收敛原则`
- [ ] 规则说明了对超过 3 文件的响应行为是进行 Canonicalization

## ✅ Post-Completion Updates

| # | Go To | Do This |
|---|-------|---------|
| 1 | [execution/_tracker.md](../_tracker.md) | B006 → DONE |
| 2 | [CURRENT.md §1](../CURRENT.md#§1-batch-overview) | 更新状态 |
| 3 | [change_log.md](../change_log.md) | 追加变更记录 |

## B Tail Anchor
- **Objective**: 限制 Plan Update Targets 输出面，强制目标控制
- **DoD**: 路由契约添加 ≤3 文件约束限制及 Canonicalization
- **Next actions**: 更新 integration-router.md
- **Hard constraints**: 四字段格式稳定
