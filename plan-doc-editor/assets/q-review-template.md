---
name: Q-NNN Review Request
description: >-
  Template for requesting a review (local or Jules). Fill in and place in questions/ directory.
q_id: Q-NNN
type: review
status: open
created: YYYY-MM-DD
related_batch: BNNN
blocker: true              # true = tracker writes BLOCKED(Q-NNN)
---

# Q-NNN: Review Request — <slug>

## Trigger
- **B-file**: [BNNN](../execution/BNNN_xxx.md)
- **review 声明值**: `local` | `required_jules`
- **触发原因**: <为什么需要 review — 例如：跨模块改动 / 外部依赖变更 / 安全路径>

## Scope
审查范围（精确路径）：
- `path/to/dir_or_file` — <审查重点>
- `path/to/another` — <审查重点>

## Baseline
审查判断基准：
- [CURRENT.md §0](../CURRENT.md#§0-norms-standards-baseline)
- [references/P0_baseline.md](../references/P0_baseline.md)

## Expected Output
- **路径**: `investigation/INV-<Q-NNN>_local_review.md` 或 `investigation/INV-*_jules_review.md`
- **格式**: review-report-template（Issue Index + 四字段 + Plan Update Targets）

## Blocker
- **阻塞 tracker**: yes → tracker 写 `BLOCKED(Q-NNN)`
- **解除条件**: Gate-R 通过（无 🔴 Status=open）

## deps_to_verify (可选)
需要 Context7 校验的外部依赖：
- 格式：优先 `/org/project(/vX.Y.Z)`（libraryId），其次 `name@major`（如 `next.js@15`）
- 已知 libraryId 必须写 libraryId

| 依赖 | 格式 | 校验重点 |
|------|------|---------|
| — | — | — |
