---
name: PLAN-20260301-002 Review 默认化与 Context7 集成
description: >-
  让 Review 不再是例外，而是任务设计阶段的默认机制。覆盖实施完整度 + 偏移检测两类风险，并引入 Context7 校验外部依赖正确性。
plan_title: Review 默认化与 Context7 集成
plan_id: PLAN-20260301-002
status: DESIGNING
revision: v001
last_updated: 2026-03-01
---

# Review 默认化与 Context7 集成

## Head Anchor
- **Goal**: Review 成为默认机制，补齐“执行就绪”（G-READY）硬门禁与 PlanApproved 开关，并增强 Context7 防泄漏机制。
- **Status**: DESIGNING
- **Active IDs**: B005, B006, B007, B008
- **Next actions**: 1) B005 定义可计算的 G-READY 2) B007 PDCA pre-flight gate 3) B006 收敛更新面 4) B008 Context7 安全兜底
- **Hard constraints**: 不新增目录；文档层级≤3；输出含四字段
- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md) · `plan-doc-editor/references/integration-router.md`
- **PlanApproved**: NO

## §0 Norms (Standards Baseline)

### 核心约定

1. **Review 请求入口**：`questions/Q-NNN_review_<slug>.md`（发射井）
2. **Review 结果收件箱**：`investigation/INV-*_*.md`
   - 异步审计：`INV-*_jules_review.md`（沿用 Gate-J）
   - 本地审查：`INV-*_local_review.md`（新增命名约定，不新增目录）
3. **输出协议不变**：所有 review/report 都必须包含统一四字段：Read / Write / Evidence / Plan Update Targets
4. **文档层级 ≤ 3**：靠模板固定（Q-review 模板 + review report 模板）
5. **review 声明**：B-file frontmatter 增加 `review: none | local | required_jules`
6. **执行门禁执行纪律**：未经 PlanApproved=YES 和 G-READY=pass，PDCA Implement 必须拒绝生成生产代码，只允许补齐 B-file 骨架。
7. **更新收敛原则**：Plan Update Targets 默认触达 ≤3 个目标文件，多余事实经 Canonicalization 处理。

### Norm Sources
- `plan-doc-editor/references/integration-router.md` — 门禁映射真源 (Gate-J, Gate-R, G-READY)
- `pdca-ai-coding/references/output-contract.md` — 输出契约
- `jules-cli/references/prompt-envelope-review.md` — Jules review 模板

### 设计原则
- Review 覆盖两类风险：**实施完整度**（completeness）+ **不偏移**（drift）
- 外部依赖正确性用 Context7 加强，**不替代**内部架构审查
- 任何没有细则的执行都要被系统性“阻断”在外围

### Context7 安全规范（8 层防泄漏护栏）
1. **存储层**：Key 只来自环境变量或 repo 外 `.env`；仓库最多 `.env.example`；禁止写入 questions/CURRENT/investigation/review report/prompt pack/日志
2. **执行层**：无 key → 不发 `Authorization` 头；错误输出只打印状态码
3. **产物层**：Evidence 允许 libraryId/版本/摘录；禁止请求头/curl/含 token 的变量
4. **Prompt 层**：模板硬规则 — 疑似密钥一律 `***REDACTED***`
5. **流程层**：建议 PR 加 secret scanner；怀疑泄露立即 rotate
6. **兜底层**：不配 key 也能跑（rate limit 更低但功能完整）
7. **最小暴露面**：禁止 `node ... --key ...`，强制 `export CONTEXT7_API_KEY`
8. **门禁判定**：发现疑似 secret，Issue Index 记 🔴 且 Status=open → Gate-R 直接 fail

---

## §1 Batch Overview

| Batch | Title | Phase | Status | Gates |
|-------|-------|-------|--------|-------|
| B001 | 模板与约定 | P1 | ✅ DONE | — |
| B002 | PDCA 产出本地 review report | P2 | ✅ DONE | B001 |
| B003 | Jules 对齐 Q + Context7 | P3 | ✅ DONE | B001 |
| B004 | 门禁化（Gate-R 定义 + 阻塞规则） | P4 | ✅ DONE | B001,B002 |
| B005 | 定义 G-READY + 引入 PlanApproved | P5 | 📋 READY | — |
| B006 | 收敛 Plan Update Targets | P6 | 📋 READY | — |
| B007 | PDCA Implement 增加 pre-flight gate | P7 | 📋 READY | B005 |
| B008 | Context7 防泄露护栏加强 (A+B) | P8 | 📋 READY | — |

→ Detail: [execution/_tracker.md](execution/_tracker.md)

## §2 Investigation Overview
→ Detail: [investigation/_tracker.md](investigation/_tracker.md)

## §3 Batch Dependency Graph

```
Phase 1-4: B001 → B002, B003, B004 (Review & Context7 pipeline) -> DONE
Phase 5-8: PLAN-2026-Review-Gates-vNext
  ├── B005 (定义 G-READY)
  │    └── B007 (PDCA pre-flight gate)
  ├── B006 (收敛更新靶点)
  └── B008 (Context7安全强化)
```

## §4 Context Cards

### CTX-EXISTING-GATES
→ [integration-router.md](../../plan-doc-editor/references/integration-router.md#门禁映射) — Gate 映射真源
→ [plan-template.md](../../plan-doc-editor/assets/plan-template.md) — 顶层架构计划模板

## §5 Decisions / Open Questions

### Decisions (D-*)
- **D-004**: 增设 `PlanApproved: NO|YES` 标志位至 `plan-template.md` 和所有 plan CURRENT
- **D-005**: Gate-R 判断疑似密钥泄漏等同于 Critical(🔴) open
- **D-006**: Plan Update Targets 限制 ≤3 个受影响文件目标（强迫 canonicalization）

### Open Questions (Q-*)
- 空

## §6 Iteration Log
| Date | Trigger Event | Action | Impact |
|------|--------------|--------|--------|
| 2026-03-01 | 用户提出 Review 默认化需求 | 创建 plan module (B001-B004) | — |
| 2026-03-02 | 缺口审计: 需硬化执行门禁与安全 | 纳入 PLAN-2026-Review-Gates-vNext (B005-B008) | plan-doc-editor, pdca-ai-coding |

## Tail Anchor
- **Goal**: Review 成为默认机制，补齐“执行就绪”（G-READY）硬门禁与 PlanApproved 开关，并增强 Context7 防泄漏机制。
- **Status**: DESIGNING
- **Active IDs**: B005, B006, B007, B008
- **Next actions**: 1) B005 定义可计算的 G-READY 2) B007 PDCA pre-flight gate 3) B006 收敛更新面 4) B008 Context7 安全兜底
- **Hard constraints**: 不新增目录；文档层级≤3；输出含四字段
- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md)
- **PlanApproved**: NO
