---
name: B007 PDCA Implement 增加 pre-flight gate
description: >-
  在 implementation-prompt.md 插入 pre-flight gate：未通过 G-READY 或 PlanApproved=NO 时，禁止写生产代码。
batch_id: B007
title: PDCA Implement 增加 pre-flight gate
status: READY
phase: P7
created: 2026-03-02
updated: 2026-03-02
review: local
prerequisites: [B005]
impact_refs:
  - pdca-ai-coding/references/implementation-prompt.md
  - pdca-ai-coding/SKILL.md
related_investigations: []
cross_refs:
  tracker: execution/_tracker.md
  current: CURRENT.md
  changelog: change_log.md
---

## B Headline
- **Objective**: 将“执行就绪硬门槛”落实到执行面，阻止未完成的计划直接编写生产代码。
- **Inputs**: [implementation-prompt.md](../../pdca-ai-coding/references/implementation-prompt.md) · [SKILL.md](../../pdca-ai-coding/SKILL.md)
- **DoD**: prompt 头增加 PRE-FLIGHT 检测；SKILL 补充说明。
- **Next actions**: 1. 更新 implementation-prompt.md 2. 更新 SKILL.md
- **Hard constraints**: 检测条件复用 completion-prompt 的相同 plan-doc 结构探测

# B007: PDCA Implement 增加 pre-flight gate

## Objective
把“执行就绪硬门槛”防在写生产代码之前。如果强行调用 Implementation，检测到当前尚未经受评审或 `PlanApproved=NO` 实效状态，直接熔断并指导用户先回填计划与骨架。

## Context
当前 PDCA implementation-prompt 里只有 TDD 执行纪律，无 pre-flight 检测。为了确保所有实现都在稳定架构下进行，必须要求 plan module 的 G-READY == pass 且 PlanApproved == YES。
> Baseline: [implementation-prompt.md](../../pdca-ai-coding/references/implementation-prompt.md)

---

## ⚙️ Before You Start (READ FIRST)

| # | Read This | Why |
|---|-----------|-----|
| 0 | [CURRENT.md §0](../CURRENT.md#§0-norms-standards-baseline) | 核心规范 |

---

## Execution Steps

### Step 1: implementation-prompt.md 增加 pre-flight
在 `IMPLEMENTATION PHASE` 的顶部（最开始的指令前，例如 L12 之后）插入：

```markdown
### PRE-FLIGHT (plan-doc-editor 环境)

检测条件：当前工作目录向上能找到 `CURRENT.md` 且存在 `investigation/` 与 `questions/`。
若处于 plan-doc 环境，必须进行执行前置检查：
1. `CURRENT.md` Head Anchor/Tail Anchor 中必须 `PlanApproved: YES`
2. 必须满足 G-READY (存在 B file、具有 tracker 等执行条件)

**拦截动作**：若任一不满足：
→ **STOP** (禁止写任何功能代码业务层、不进入 TDD)。
→ 输出 `Plan Update Targets` 建议只补齐 `execution/_tracker.md` 或创建对应的 `execution/B*_*.md` stub (骨架)，且要求 `PlanApproved` 继续保持 NO。
→ 创建 `questions/Q-NNN_exec_ready_*.md` 记录骨架缺口并反馈给计划协调者。
```

### Step 2: pdca-ai-coding/SKILL.md 的修改
打开 [SKILL.md](../../pdca-ai-coding/SKILL.md)，在 `With Infrastructure (plan-doc-editor is present)` 段落处，追加一句说明：
“实施前必须通过 `G-READY` 且 plan 标记 `PlanApproved: YES` （否则走 STOP 流，只允许补充执行骨架文档）。”

---

## Definition of Done (DoD)
- [ ] `implementation-prompt.md` 的 `IMPLEMENTATION PHASE` 顶部含 `PRE-FLIGHT` 区块，阻断动作清晰
- [ ] `pdca-ai-coding/SKILL.md` 的 `With Infrastructure` 段落注明了 G-READY 前置限制

## ✅ Post-Completion Updates

| # | Go To | Do This |
|---|-------|---------|
| 1 | [execution/_tracker.md](../_tracker.md) | B007 → DONE |
| 2 | [CURRENT.md §1](../CURRENT.md#§1-batch-overview) | 更新状态 |
| 3 | [change_log.md](../change_log.md) | 追加变更记录 |

## B Tail Anchor
- **Objective**: 阻止未完成的计划进入 implementation 并直接编写生产代码。
- **DoD**: prompt 顶部增加 PRE-FLIGHT / SKILL.md 声明 
- **Next actions**: 1. 更新 implement-prompt 2. 改 SKILL
- **Hard constraints**: 检测条件复用 completion-prompt 的相同结构
