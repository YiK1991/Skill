# Prompt Envelope — 实现与测试 (Implement / Test)

> 用于：编写代码、修复 Bug、添加测试、修改配置等需要 **修改源代码** 的任务。
> 一个 prompt 只覆盖一个方面。

---

## 模板

```markdown
# TASK-XXX: <short title>

## 0) Meta
- task_id: TASK-XXX
- intent: implement | test | release
- scope: (one aspect only)
- risk_level: (low | medium | high)
- repo: <owner/repo>
- branch_context: <starting branch>
- labels: plan:<module>|run:<RUN-ID>|aspect:<ASPECT-ID>|ctx:<CTX-ID>

## 1) Objective (Extracted Task Text)

> **反模式警示**：严禁只写“请参考 CURRENT.md 执行第三步”之类的懒指令。
> Jules 是一个无交互的盲跑 Subagent，不可能中途问你“第三步具体是什么”。
> 必须由主控端（人类或本地 AI）将具体任务内容**无损、完整地提取**到此处。

用一句话说明“这次只做什么”，然后给出完整的任务细节：

**具体任务内容**（从计划/调查文档中提取的原文，或人类手写的精确指令）：
```
<paste the exact, complete task description here>
```

## 2) Context (disclosure-only)

### 项目规范（强制必读 — 写代码前先通读）
- 根目录 `gemini.md` — 项目管理规范、文件组织规则、数据流原则、CI 要求
- 根目录 `agent.md` — AI 工具规范入口
- 根目录 `rules.md` — 额外规则/约束（如果存在）
- `<module>/Gemini.md`（如改动涉及 `01_L1_Core`，读 `01_L1_Core/Gemini.md`）
- `<module>/rules.md`（如果存在）

> **开发准则**：
> 先读 `gemini.md` 的目录编号规则（`00_Data_Source` ~ `Warehouse`）。
> 新文件必须放入对应编号目录，禁止在根目录散落。
> Python 脚本用小写下划线命名。数据文件遵循 `raw_*.parquet` / `*_l2_daily.parquet`。
> 临时文件（`check_*` / `debug_*` / `diagnose_*`）进 `08_System_Maintenance/Temp/`。
> 数据流：L1 输出 Parquet → L2/L3 消费 Parquet，不引入额外格式。
>
> **架构与 CI 意识（强制要求）**：
> - **系统架构**：严格遵循 DDD/分层架构。保持关注点分离（SoC，业务逻辑严禁泄露到 UI/Router）。优先使用现有生态（防 NIH 综合征）。使用领域语义命名，**严禁使用** `utils.py`, `common.py`, `helpers.js` 等泛名/杂货铺模式。
> - **CI 工作流**：你的代码将运行在自动化的 CI 环境中。必须确保修改不破坏现有的 CI 构建和测试流（如 GitHub Actions 工作流），禁止为了绕过 CI 门禁而草率注释或跳过失败的测试。

### 相关计划与调研文档（必须给出链接）
- 计划文档：`<path/to/plan/SKILL.md>` 或 `<path/to/CURRENT.md>`
- 调研报告：`<path/to/research/report.md>`
- 前序 Jules 结果：`<path/to/jules_pack/results/TASK-XXX_*.md>`
- 相关 PR：`<GitHub PR URL>`

> 目的：避免重复调研、违背已定决策。至少给出文档路径链接。

### Code Context (供广泛阅读 — 不限制读取范围)
- <path/to/file_or_dir>

### Interface Contracts (接口契约 — 如涉及跨模块交互则必须提供)
如本任务涉及新增或修改与其他模块的交互，必须提供已设计好的契约文件（类型定义、接口签名、数据结构），
**禁止让 Jules 自行设计跨模块接口**。
- <path/to/interface/contract.ts or types.py> (只读参照)
- <path/to/existing/api_schema.py> (只读参照)

## 3) Constraints (Hard Boundaries)

### 修改白名单（Modification Whitelist — 绝对红线）
> Jules 可以广泛阅读代码库以充分理解上下文，但**只允许修改**以下路径：
- `<path/to/allowed/file_or_dir>`
- `<path/to/allowed/file_or_dir>`

> 任何超出上述白名单的文件修改（即使看起来“有用”）都属于越界行为，将在 PR 审查时被拒绝。

### 架构与质量约束
- 禁止破坏关注点分离（SoC）；禁止违背已有模块的领域设计边界
- 提交的代码必须能通过当前的自动化测试套件；禁止通过 skip 等方式逃避测试
- 遵守所有规范文件中的编码规范、命名规则和文件放置规则
- 禁止：大范围重构 / 改动无关模块 / 引入新依赖（除非这里明确允许）
- 必须保持：<behavioral invariants>
- **分支规则**：在特性分支上工作，通过 PR 提交，禁止直接推送 main

### Non-goals（本次明确不做的事 — 防止盲跑 Agent 好心办坏事）
- <例：不改接口契约>
- <例：不引入新依赖>
- <例：不重构无关模块的命名>

### Document Placement (MANDATORY — 双写硬规则)
> 关键约束必须在 prompt 的 **header + placement** 两处重复，确保 Jules 不会遗漏。

1. **允许的输出路径**：仅限修改白名单中的文件
2. **禁止创建新目录**（不允许 `_governance/`, `Reviews/` 等）
3. **输出路径至少在 prompt 中出现两次**（此处 + §1 Objective 或 §0 Meta）

## 4) Acceptance Criteria (testable)
- [ ] ...

## 4b) Assumptions（显式假设 — 降低盲跑不确定性）
> Jules 无法中途提问。如果遇到不确定的决策点，它会按以下假设行事：
- 假设 <X> 采用 <Y> 方案（例：假设数据库迁移采用向后兼容策略）
- 假设 <A> 的默认值为 <B>
- 如果 <条件> 不成立，则采用保守路径 <C>

## 4c) Interaction Budget（交互预算 — 仅限 C 档任务）
> A/B 档任务期望零交互。C 档任务允许以下窗口：
- **Return Triggers**（必须停下回主流程的情况）：
  - 需要跨模块修改超出修改白名单
  - 需要变更接口契约
  - 需要引入新依赖
  - 测试无法通过且原因不在修改范围内
- **如果不确定**：输出"需要的材料清单 + 建议拆分"，而非强行编写猜测代码

## 4.5) Governance Capsule (MANDATORY)

> 每个 Jules 任务必须携带治理胶囊。不要整段粘贴规范原文，使用 HYDRATE 宏注入关键片段。

```markdown
## Governance Capsule (MANDATORY — treat as non-negotiable)

### Authority & Must-Read (in order)
1) Project root rules: `gemini.md`, `agent.md`, `rules.md` (and module-level rule files)
2) Integration contract (Core output fields + evidence standard): `.agent/skills/plan-doc-editor/references/integration-router.md`
3) Plan disclosure rule: `.agent/skills/jules-cli/references/plan-as-skill-integration.md`

### Output Contract (REQUIRED Core fields; exact names; RefSpec only)
{{ HYDRATE: .agent/skills/pdca-ai-coding/references/output-contract.md:L8-L13 }}

### Integration Router (gates + Gate-J definition)
{{ HYDRATE: .agent/skills/plan-doc-editor/references/integration-router.md:L17-L44 }}

### Stop Conditions (do NOT "guess and patch")
- If required files are missing, rules conflict, or scope is ambiguous: STOP and report with Evidence Pointers.
- If you cannot produce RefSpec evidence for a claim: mark it as UNKNOWN (do not fabricate).
```

## 5) Output Format
### Documentation Output (Progressive Disclosure REQUIRED)

> **触发条件**：当任务 intent 涉及 write docs / update README / create spec / generate report 时，文档输出必须遵循以下分层结构。纯代码变更不受此约束。

文档结构至少包含：
1. **TL;DR / Quick Start**（给 90% 用户的一句话摘要）
2. **Basic**（默认路径与核心用法）
3. **Advanced / Edge Cases**（折叠层，仅需深入时阅读）
4. **Appendix**（长解释、示例、FAQ、术语）

强制规则：
- 使用**稳定 heading anchors**，跨文件只用 RefSpec 链接（`path#anchor`），不复制粘贴大段内容
- 文档缺乏 PD 导航结构（无 Index/Head Anchor/稳定 anchors）或包含大段证据/日志 → **必须拆分**为 `INDEX/OVERVIEW.md` + `DETAILS.md`（放在修改白名单允许路径内）
- 仍遵守 §4 的 placement 双写 + 禁止新目录红线

### A) Changes
- 变更文件清单（文件路径 + 简述）

### B) Evidence
- 测试命令 + 输出（成功/失败 + 关键日志）

### C) Risk & Rollback
- recommended next step
- risk notes
- rollback plan

## 6) Stop Conditions
如果出现以下任一情况：需求不明确 / 必要上下文缺失 / 需要越界改动——
请停止执行，输出 what is missing + 建议补充什么，然后等待反馈。
```

---

## "进一步修改" 消息模板

### sendMessage（同 session）

```markdown
**[plan:<module> run:<RUN-ID> aspect:<ASPECT-ID> ctx:<CTX-ID>]**

- Scope: `<file/dir list>`
- Change request:
  1. …
- Constraints: …
- Tests/Evidence: 请运行 `…` 并给出结果。
- Done criteria: …（满足即停止）
```

### PR 评论（session 已完成后）

```markdown
@Jules

**[plan:<module> run:<RUN-ID> aspect:<ASPECT-ID>]**

请在本 PR 分支上修改：
1. …

约束：只修改 `<file list>`；遵守 `gemini.md`；附带测试输出。
```
