---
name: INV-NNN Review Report
description: >-
  Template for review report output (local or Jules). Follows PD-OUT v1 structure.
inv_id: INV-NNN
mode: recon
method: local | jules
status: TODO
created: YYYY-MM-DD
reviewed: null
q_id: Q-NNN               # optional: 回链发射井 ID
related_batches: []
as_of: YYYY-MM-DD
---

> ⛔ **REDACT RULE**: 任何疑似密钥/Token 一律用 `***REDACTED***` 输出。永不复述环境变量内容。永不输出完整请求头。Evidence 允许 libraryId/版本/来源路径/摘录片段；禁止请求头/curl 命令/含 token 的环境变量。

# INV-NNN: Review Report — <slug>

## Head Anchor
- **结论**: <一句话结论>
- **范围**: <审查范围>
- **🔴 Critical**: N 个
- **下一步**: <建议行动>
- **q_id**: Q-NNN (optional)

## Issue Index

| # | Severity | Status | Title | RefSpec | Anchor |
|---|----------|--------|-------|---------|--------|
| 1 | 🔴 Critical | open | ... | `path:Lx-Ly` | [→ Detail](#issue-1) |
| 2 | 🟡 Medium | open | ... | `path:Lx-Ly` | [→ Detail](#issue-2) |
| 3 | 🟢 Low | open | ... | `path:Lx-Ly` | [→ Detail](#issue-3) |

> **Status 值**: `open` / `fixed` / `accepted` / `follow-up`
> **Gate-R 判定**: 🔴 + open/follow-up(无落点) → fail；🔴 + fixed/accepted → pass

## Details

### Issue 1: <title>
- **严重级别**: 🔴 Critical
- **位置 (RefSpec)**: `path:Lx-Ly`
- **违反规范**: <引用 §0 / gemini.md / rules.md 条款>
- **问题分析**: <解释>
- **Suggested Fix**: <建议（仅建议，不实施）>

## Read List (RefSpec)
实际读取的文件/锚点：
- `path:Lx-Ly` 或 `path#anchor`

## Write List (RefSpec)
创建或修改的文件：
- `path/to/file`

## Evidence Pointers (RefSpec)
支持结论的关键代码/文档锚点（Top 3-5）：
- `path:Lx-Ly`

## Plan Update Targets (RefSpec + bullet)

| 目标文件 (RefSpec) | 推荐编辑 |
|--------------------|---------|
| `path#anchor` | ≤3 行建议 |
