# Jules Implement 报告模板

> **Jules 必须严格按照此模板组织 PR 报告。缺少任何必填段落视为不合格。**

---

## Head Anchor (≤5 行)

```
task_id: TASK-XXX
intent: implement
scope: <做了什么一句话>
status: DONE | PARTIAL | BLOCKED
test_result: PASS <N> / FAIL <N>
```

## Changes

| 文件路径 (RefSpec) | 变更类型 | 简述 |
|-------------------|---------|------|
| `path:Lx-Ly` | ADD / MODIFY / DELETE | 一句话描述 |

## Evidence

```
测试命令: <具体命令>
测试结果: PASS / FAIL
关键日志: <≤10 行关键输出>
```

> 完整日志 offload 到独立文件，此处只放摘要 + RefSpec。

## Risk & Rollback

```
- risk_level: (low | medium | high)
- risk_notes: <风险说明>
- rollback_plan: <回滚步骤>
- recommended_next_step: <建议下一步>
```

## Documentation Output (如涉及文档修改)

文档结构至少包含：
1. **TL;DR / Quick Start** — 一句话摘要
2. **Basic** — 核心用法
3. **Advanced / Edge Cases** — 仅需深入时阅读
4. **Appendix** — 示例、FAQ

> 使用稳定 heading anchors，跨文件只用 RefSpec 链接。

## Output Contract (MANDATORY)

| Field | Format | 内容 |
|-------|--------|------|
| Read List (RefSpec) | `path:Lx-Ly` 或 `path#anchor` | 实际读取的文件 |
| Write List (RefSpec) | 同上 | 创建或修改的文件 |
| Evidence Pointers (RefSpec) | Top 3-5 | 支持结论的关键锚点 |
| Plan Update Targets (RefSpec + bullet) | `path#anchor` + ≤3 行 | 回流到计划的修改点 |

> 字段名固定，禁止同义词。

## RefSpec 规则

- 格式：`path:Lx-Ly` 或 `path#anchor`。禁止裸路径。
- 代码块 ≤60 行。超过必须 offload。
- 禁止全文粘贴。
