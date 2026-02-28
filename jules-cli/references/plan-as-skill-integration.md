# Plan-as-Skill Integration (披露式上下文)

> 目标：让调用方只把 **“当前阶段/当前节点需要的上下文”** 提供给 Jules，避免长 plan 导致的漂移和成本。

---

## 约定：计划文档以 Skill-like Pack 组织

```
<plan_module>/
├── SKILL.md
└── references/
    ├── P0_overview.md
    ├── P1_design.md
    ├── P2_implementation.md
    ├── ...
    └── A*_appendix_*.md
```

- `SKILL.md`：导航面（Layer 0–1）——告诉“现在读什么”。
- `references/`：深层细节（Layer 2–3）——按阶段/关注点拆分。

---

## 如何在 prompt 中引用计划

在 `Prompt Envelope` 的 `Context to read` 里，只引用：

- 必读：`<plan_module>/SKILL.md`
- 选读：与本任务“单一方面”直接相关的 1–3 个 references 文件

避免：
- 把整个 plan 粘贴进 prompt
- 一次让 Jules 读所有 phase

---

## 回流

Prompt Pack 的 `results/` 中必须指出：

- 应该更新 plan pack 的哪一层/哪一个卡片（文件 + 锚点）
- 推荐的最小编辑点（bullet）

这样计划可以在“审查后回流”，形成闭环。
