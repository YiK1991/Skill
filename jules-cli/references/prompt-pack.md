# Prompt Pack: 并行调研/审查的文档组织

> 目标：把一个大计划拆成 **可并行的小任务**，并且让结果能回流到 plan-as-skill，而不污染文档治理。

## 任务切分原则

> Jules 一旦启动就无法中途交流。并行分发多个 Jules 任务时，**前期的切分设计决定了一切**。

1. **互不重叠的文件修改区**：每个并行 implement 任务的修改白名单（Modification Whitelist）必须互不相交。任何两个任务不得同时修改同一个文件。
   - **按功能切片（Vertical Slice）**：每个任务负责一个完整的功能切面（如 Login = UI + API + Tests）→ 适合模块间解耦较好的场景
   - **按层切片（Horizontal Layer）**：每个任务负责一个架构层（如 UI 层 / Service 层 / Data 层）→ 适合传统分层架构
   - **混合策略（Hybrid）**：功能切片为主，共享基础设施单独拆出 → 大多数真实场景的最佳选择
2. **提取后的完整任务指令**：每个 `tasks/TASK-XXX.md` 必须包含该任务的**完整指令全文**（Extracted Task Text），严禁只写"请参考 CURRENT.md 第三段"让 Jules 自己去找。
3. **接口契约先行**：如果多个并行任务之间存在接口依赖，必须在分发前统一设计好接口契约文件（Interface Contracts），作为所有任务的只读上下文共享。

---

## 目录结构

> 资产放置规则（条件式）：
> - **有 plan module**：PACK 放在 `<plan_module>/jules_pack/`，results 回流到 `<plan_module>/investigation/`
> - **Standalone**（无 plan module）：允许放在 `00_Documentation/99_Inbox/` 或自定义目录

```
jules_pack/                           # ← 路径由 orchestrator 指定
├── PACK.md
├── tasks/
│   ├── TASK-001_<slug>.md
│   ├── TASK-002_<slug>.md
│   └── ...
├── results/
│   ├── TASK-001_<slug>.md
│   └── ...
└── followups/
    └── FU-*.md
```

- `PACK.md`：唯一入口（列出任务清单、session 链接、回流点）。
- `tasks/`：输入（prompt envelope）。
- `results/`：结果摘要（用于回流计划/设计）。
- `followups/`：对某个 session 的追加消息（同一 session 内迭代）。

> 注意：滚动日志不允许内联。如需留证，offload 到 `investigation/tool_outputs/` 或 `results/`，并在 results 中用 RefSpec 链接。

---

## PACK.md 模板

```markdown
# Prompt Pack: <topic>

## Scope
- module: <module>
- goal: <one paragraph>
- related plan module: <path/to/plan_module/>
- conventions:
  - Project rules: `gemini.md`, `agent.md`, `rules.md`（Jules 执行每个 task 前必须先读取根目录及涉及模块下的规范文件）
  - Core Worker Contract + 路由门禁: `.agent/skills/plan-doc-editor/references/integration-router.md`（统一输出字段、证据标准、Gate-J）
  - 披露式上下文规则: `.agent/skills/jules-cli/references/plan-as-skill-integration.md`（最小必读 + 回流字段）
- run_id: <RUN-ID>
- result_flow: PR-only（所有结果通过 PR 推送，禁止 local pull）

## Task list
| task_id  | aspect          | aspect_id       | status | session | pr_url | result                |
| -------- | --------------- | --------------- | ------ | ------- | ------ | --------------------- |
| TASK-001 | security review | review-security | queued | (link)  | (link) | results/TASK-001_*.md |

## Where results should flow back
- PR review → merge → plan module layer/card: <references/P#_...md#anchor>

## Notes
- 所有 session 默认启用 `AUTO_CREATE_PR`
- 审阅通过的 PR 由人类决定合并
- 需要修改时，在 PR 上评论 `@Jules`
```

---

## results/ 文档模板（与 Core Worker Contract 对齐）

```markdown
# TASK-XXX result

## Session
- session_id: ...
- session_url: ...
- pr_url: ... (必须有 — PR-only workflow)
- pr_status: open | merged | closed
- labels: plan:<module>|run:<RUN-ID>|aspect:<ASPECT-ID>|ctx:<CTX-ID>

## Read List (RefSpec)
- `path:Lx-Ly` — 实际读取的文件/锚点

## Write List (RefSpec)
- `path:Lx-Ly` — 创建或修改的文件（review 通常为空）

## Evidence Pointers (RefSpec)
Top 3-5 支持结论的关键代码/文档锚点：
- `path:Lx-Ly` — 简述发现

## Key Findings
- ...

## Plan Update Targets (RefSpec + bullet)
回流到计划的具体修改点：
- `path#anchor` — 推荐编辑（≤3 行）
```
