# Jules Review 报告模板 (PD-OUT v1)

> **Jules 必须严格按照此模板组织报告。缺少任何必填段落视为不合格。**

---

## Head Anchor (≤7 行)

```
task_id: TASK-XXX
intent: review
scope: <审查范围一句话>
conclusion: <结论一句话>
critical_count: <🔴 数量>
high_count: <🟠 数量>
next_step: <建议下一步>
```

## How to Read This (Progressive Disclosure)

| Layer | Content | When to Read |
|-------|---------|-------------|
| A. Head Anchor | 结论与范围 | Always |
| B. Issue Index | 问题索引表 | 需要概览时 |
| C. Details | 每个 Issue 完整分析 | 需要深入时 |
| D. Plan Update Targets | 回流到计划的修改点 | 需要更新计划时 |

## Issue Index

| # | Severity | Title | RefSpec | Anchor |
|---|----------|-------|---------|--------|
| 1 | 🔴 Critical | ... | `path:Lx-Ly` | [→ Detail](#issue-1) |

## Details

每条 Issue 格式：

```
#### Issue N: <简要描述>
- 严重级别：🔴 Critical | 🟠 High
- 位置 (RefSpec): `path:Lx-Ly`
- 违反规范：<引用具体条款>
- 现状代码：
  ```<lang>
  <当前代码片段，≤60 行>
  ```
- 问题分析：<解释>
- Suggested Fix（仅建议，不实施）：
  ```<lang>
  <建议修改>
  ```
```

每条 Suggestion 格式：

```
#### Suggestion N: <简要描述>
- 严重级别：🟡 Medium | 🟢 Low
- 位置 (RefSpec): `path:Lx-Ly`
- 理由：<为什么建议修改>
- Suggested Fix：<建议方案>
```

## Risk Assessment

```
- overall_risk: (low | medium | high)
- risk_areas: <高风险区域>
- recommended_priority: <修复优先顺序>
```

## Output Contract (MANDATORY — 必须包含以下 4 字段)

| Field | Format | 内容 |
|-------|--------|------|
| Read List (RefSpec) | `path:Lx-Ly` 或 `path#anchor` | 实际读取的文件 |
| Write List (RefSpec) | 同上 | 创建或修改的文件 |
| Evidence Pointers (RefSpec) | Top 3-5 | 支持结论的关键锚点 |
| Plan Update Targets (RefSpec + bullet) | `path#anchor` + ≤3 行 | 回流到计划的修改点 |

> 字段名固定，禁止同义词（如不许用 "Files Changed" 替代 "Write List"）。

## RefSpec 规则

- 格式：`path:Lx-Ly` 或 `path#anchor`。禁止裸路径或 "see file X"。
- 代码块 ≤60 行。超过必须 offload 到独立文件 + RefSpec 引用。
- 禁止全文粘贴。只保留关键片段 + RefSpec 指向原文。
