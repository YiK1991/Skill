---
name: P0 Baseline
description: Current state facts, constraints, and evidence hooks.
---

# P0 Baseline / Overview

## Suite 不变量（5 条，写死）

1. **dispatch-only**：Jules submit → `dispatch_prompt_pack.py`
2. **Core Worker Contract**：Read / Write / Evidence / Plan Update Targets（字段名固定）
3. **Evidence shape**：RefSpec + ≤60 行 + offload
4. **Cold-start vs Warm-start**：首次/大变更 = Sync；熟悉 = Lite
5. **No chat-only planning**：决策必须落盘

## 已完成基线（Round 5–7）

| 项 | 状态 | 证据 |
|---|------|------|
| Repo Contract Priority 单一真源 | ✅ | `pdca-ai-coding/references/repo-contract-priority.md` |
| PDCA Step0/Discovery/SKILL.md 改为引用真源 | ✅ | analysis-prompt.md, discovery-ladder.md, SKILL.md |
| cli-reference / tools-notes dispatch-only | ✅ | Round 5-6 commit |
| atdd_gate --base auto | ✅ | Round 7 commit |
| Tracker 治理规则 + G-SYNC sanity check | ✅ | integration-router.md, plan-doc-editor/SKILL.md |
| init_plan_skill.py 目录中性化 | ✅ | Round 7 commit |
| task_id regex 收紧 | ✅ | Round 5 commit |
| --no-cache 精确清理 | ✅ | Round 5 commit |

## 剩余缺口

| 项 | 状态 | 说明 |
|---|------|------|
| init_plan_skill.py 生成 SKILL.md shim | 🟡 | 脚本还没自动生成 |
| Cold/Warm-start 路由写入三 SKILL 第一屏 | 📋 | 需要设计段落内容 |
| check_suite_consistency.py | 📋 | 防回退 lint |

## Evidence Hooks
- code: `jules-cli/scripts/dispatch_prompt_pack.py` — gates 实现
- config: `pdca-ai-coding/references/repo-contract-priority.md` — 入口优先级
- contracts: `plan-doc-editor/references/integration-router.md` — 跨 Skill 路由
- tests: 无自动化测试（用 lint 替代）
