# Plan-as-Skill Integration (披露式上下文)

> 目标：让调用方只把 **"当前阶段/当前节点需要的上下文"** 提供给 Jules，避免长 plan 导致的漂移和成本。

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

- `SKILL.md`：导航面（Layer 0–1）——告诉"现在读什么"。
- `references/`：深层细节（Layer 2–3）——按阶段/关注点拆分。

> **入口规则**：
> - **plan-doc-editor 模块**（含 `INDEX.md` + `CURRENT.md` + `_tracker.md`）：入口 = `INDEX.md` → `CURRENT.md`（Two-Pass 的 Pass0/Pass1）。若存在 `SKILL.md`，它仅作为导航壳指向 INDEX/CURRENT。
> - **skill-pack 模块**（无 INDEX/CURRENT）：入口 = `SKILL.md`。
> - **混合模块**：优先读 `INDEX.md`；没有则读 `SKILL.md`。

---

## 如何在 prompt 中引用计划

在 `Prompt Envelope` 的 `Context to read` 里，只引用：

- 必读：`<plan_module>/INDEX.md`（若存在；plan-doc-editor 模块优先）否则 `<plan_module>/SKILL.md`
- 若有 `CURRENT.md`：读表格段落（Pass0 静态基线）
- 选读：与本任务"单一方面"直接相关的 1–3 个 references 文件

避免：
- 把整个 plan 粘贴进 prompt
- 一次让 Jules 读所有 phase

---

## 回流

Prompt Pack 的 `results/` 中必须使用**统一输出契约字段**（与 PDCA Output Contract 对齐）：

- `Read List (RefSpec)` — 实际读取的文件/锚点
- `Write List (RefSpec)` — 创建或修改的文件
- `Evidence Pointers (RefSpec)` — Top 3-5 关键证据
- `Plan Update Targets (RefSpec + bullet)` — 应更新的计划卡片（`path#anchor` + ≤3 行编辑建议）

> 字段名固定，禁止同义词。格式：`path:Lx-Ly`（代码）或 `path#anchor`（文档）。

这样计划可以在"审查后回流"，形成闭环。
