---
name: PLAN-20260301-001 三 Skill Suite 对齐优化
description: >-
  Plan entry for 三 Skill Suite 对齐优化.
plan_title: 三 Skill Suite 对齐优化
plan_id: PLAN-20260301-001
status: DESIGNING
revision: v002
last_updated: 2026-03-01
---

# 三 Skill Suite 对齐优化

## Head Anchor
<!-- Recitation Source of Truth. Keep ≤7 lines. -->
- **Goal**: 三 Skill（plan-doc-editor / PDCA / jules-cli）入口、契约、证据形态、回流方式完全对齐，Cold/Warm-start 体验自然
- **Status**: DESIGNING（Milestone 1 大部分已完成，进入 Milestone 2+3 设计）
- **Active IDs**: PR-2, PR-3, PR-5
- **Next actions**: 1. PR-2 init shim 落地 2. PR-3 Cold/Warm routing 3. PR-5 consistency lint
- **Hard constraints**: 只保留 5 条 Suite 不变量，其余不加硬 gate
- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md)

## §0 Norms (Standards Baseline)

### Suite 不变量（全系统必须遵守，仅 5 条）

1. **dispatch-only**：Jules submit 必须经由 `dispatch_prompt_pack.py`
2. **Core Worker Contract（4 字段固定名）**：Read / Write / Evidence / Plan Update Targets
3. **Evidence shape**：RefSpec + ≤60 行内联摘录 + 其余 offload
4. **Cold-start vs Warm-start**：首次/大变更必须 Sync；熟悉上下文走 Lite
5. **No chat-only planning**：所有决策必须落盘（对话不算交付）

> 除这 5 条之外，一律避免新增"强制 gate"。需要控制风险时优先用：单一真源文档 + 少量 lint 检查。

### Norm Sources
- `pdca-ai-coding/references/repo-contract-priority.md` — 入口优先级单一真源
- `plan-doc-editor/references/integration-router.md` — 跨 Skill 路由契约
- `pdca-ai-coding/references/output-contract.md` — 输出契约（PDCA extended）
- 各 Skill 的 `SKILL.md` — 入口第一屏

### 设计原则（避免越改越重）
- 不变量只保留上述 5 条
- 需要控制风险时：单一真源文档 + lint > 新 gate
- 三 Skill 说同一种话（引用同一份真源，不各写各的）

---

## §1 Batch Overview

| Batch | Title | Status | Gates | Impact |
|-------|-------|--------|-------|--------|
| PR-1 | Repo Contract Priority 单一真源 | ✅ DONE | — | 消除 11 处优先级漂移 |
| PR-2 | init_plan_skill 生成 SKILL.md shim | 🟡 ACTIVE | — | 入口收敛 |
| PR-3 | 三 Skill Cold/Warm-start 路由 | 📋 READY | — | 第一屏体验 |
| PR-4 | Jules refs dispatch-only 化 | ✅ DONE | — | 消除旧叙事误导 |
| PR-5 | Suite consistency lint | 📋 READY | — | 防回退 |
| PR-6 | atdd_gate --base auto | ✅ DONE | — | 消除 origin/main 死角 |
| PR-7 | 回流方式统一（Plan Update Targets） | ✅ DONE | — | tracker 治理 |

→ Detail: [execution/_tracker.md](execution/_tracker.md)

## §2 Investigation Overview
→ Detail: [investigation/_tracker.md](investigation/_tracker.md)

## §3 Batch Dependency Graph

```
PR-1 (✅) ← PR-3 depends on repo-contract-priority
PR-2 (🟡) ← standalone
PR-4 (✅) ← PR-5 validates PR-4's cleanup
PR-6 (✅) ← standalone
PR-7 (✅) ← standalone
```

## §4 Context Cards

### CTX-P0-BASELINE
→ [P0_baseline.md](references/P0_baseline.md) — 5 条不变量 + 已完成基线

## §5 Decisions / Open Questions

### Decisions (D-*)

- **D-001**: 不做 update_tracker.py；用"契约 + 10 秒校对"替代
- **D-002**: Suite 不变量只保留 5 条（dispatch-only / 4-field contract / evidence shape / cold-warm / no-chat-only）
- **D-003**: repo-contract-priority.md 放 pdca-ai-coding/references/（已落地）

### Open Questions (Q-*)

- **Q-001**: check_suite_consistency.py 扫哪些 pattern？（建议：direct submit / --parallel / echo | jules / GATE-2a 等旧术语）

## §6 Iteration Log
| Date | Trigger Event | Action | Impact |
|------|--------------|--------|--------|
| 2026-03-01 | Round 5-7 完成 | PR-1/4/6/7 已落地 | 大部分基线对齐 |
| 2026-03-01 | 用户提出完整优化方案 | 创建 plan module，进入 DESIGNING | — |

## Tail Anchor
<!-- Repeat Head Anchor. Keep in sync. -->
- **Goal**: 三 Skill 入口、契约、证据形态、回流方式完全对齐
- **Status**: DESIGNING
- **Active IDs**: PR-2, PR-3, PR-5
- **Next actions**: 1. PR-2 init shim 落地 2. PR-3 Cold/Warm routing 3. PR-5 consistency lint
- **Hard constraints**: 只保留 5 条 Suite 不变量，其余不加硬 gate
- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md)
