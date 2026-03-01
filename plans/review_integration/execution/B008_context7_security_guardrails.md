---
name: B008 Context7 防泄露护栏加强 (A+B)
description: >-
  落实两条“几乎不增加工程复杂度”的 Context7 防泄露兜底：1) 最小暴露面原则，2) 将疑似泄露在 Gate-R 记为红色 Critical。
batch_id: B008
title: Context7 防泄露护栏加强 (A+B)
status: READY
phase: P8
created: 2026-03-02
updated: 2026-03-02
review: none
prerequisites: []
impact_refs:
  - jules-cli/references/prompt-envelope-review.md
  - plan-doc-editor/assets/review-report-template.md
related_investigations: []
cross_refs:
  tracker: execution/_tracker.md
  current: CURRENT.md
  changelog: change_log.md
---

## B Headline
- **Objective**: 加强 Context7 的兜底安全防护，降低执行层的微小漏洞造成的 API Key 泄漏风险。
- **Inputs**: [prompt-envelope-review.md](../../jules-cli/references/prompt-envelope-review.md) · [review-report-template.md](../../plan-doc-editor/assets/review-report-template.md)
- **DoD**: prompt envelope 附加护栏 A 原则，Review 模板包含护栏 B 定义
- **Next actions**: 1. 修复 envelope 2. 修复 report 模板
- **Hard constraints**: 保持无 key 可用的兜底策略，不改动已有 context7 认证执行逻辑。

# B008: Context7 防泄露护栏加强 (A+B)

## Objective
在之前 6 层防泄漏护栏之上再补两层护栏：
- **护栏 A：最小暴露面原则**。绝不在任何可留存 history 的地方把 key 作为参数使用。
- **护栏 B：疑似泄露 = Gate-R Critical**。利用已有 REDACT RULE，一旦检查工具或人工发现在报告里产生涉敏格式，直接触发 fail。

## Context
即使有 .env.example 或不加 HTTP header 的设定，依然存在有人手动用 `node ... --key=xxx` 调用然后被 history 捕获的风险，或者 review report 里无意间带出某些形如密钥的随机字符串串流过门禁的问题。
> Baseline: [CURRENT.md](../CURRENT.md#context7-安全规范8-层防泄漏护栏)

---

## ⚙️ Before You Start (READ FIRST)

| # | Read This | Why |
|---|-----------|-----|
| 0 | [CURRENT.md §0](../CURRENT.md#§0-norms-standards-baseline) | 已经有 8 层的规则总揽 |

---

## Execution Steps

### Step 1: Jules prompt envelope 追加护栏 A 声明
在 [prompt-envelope-review.md](../../jules-cli/references/prompt-envelope-review.md) 的 `## 7) Context7 外部依赖校验（可选）` 中 `REDACT RULE` 说明部分追加内容：
```markdown
> 🛡️ **护栏 A：最小暴露面原则**：禁止使用 `node ... --key ...` 等命令行传参格式，只允许前置 `export CONTEXT7_API_KEY=...` 或通过 CI secret 注入以防留存在外部 logs/history 当中。
```

### Step 2: review-report-template.md 追加护栏 B 声明
在 [review-report-template.md](../../plan-doc-editor/assets/review-report-template.md) 的 Issue Index 上方的 `REDACT RULE` 中追加：
```markdown
> 🛡️ **护栏 B (门禁裁决)**：如果任何地方发现疑似 secret (如 Bearer 长 string, base64 格式的随机串)，必须立刻在 Issue Index 内记一条 `🔴 Critical` 且 `Status=open` 的问题，确保 Gate-R 直接 Fail 不放行任何流出物。
```
同样修改 `pdca-ai-coding/references/completion-prompt.md` 里面现有的 REDACT RULE，追加护栏 B 说明。

---

## Definition of Done (DoD)
- [ ] `prompt-envelope-review.md` 包含最小暴露面的命令行规范要求
- [ ] `review-report-template.md` 与 PDCA `completion-prompt.md` 追加了疑似泄露当做 Critical fail 的裁断指示

## ✅ Post-Completion Updates

| # | Go To | Do This |
|---|-------|---------|
| 1 | [execution/_tracker.md](../_tracker.md) | B008 → DONE |
| 2 | [CURRENT.md §1](../CURRENT.md#§1-batch-overview) | 更新状态 |
| 3 | [change_log.md](../change_log.md) | 追加记录 |

## B Tail Anchor
- **Objective**: 加强 Context7 的兜底安全防护，降低执行层的微小漏洞造成的 API Key 泄漏风险。
- **DoD**: prompt envelope 附加护栏 A 原则，Review 模板包含护栏 B 定义
- **Next actions**: 修订三个涉及安全的约定文件
- **Hard constraints**: 门禁触发 🔴
