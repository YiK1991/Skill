# Integration Router — 控制面 / 执行面 / Worker 面协作契约

> 统一 plan-doc-editor、PDCA、jules-cli 三套 Skill 的任务路由、输入/输出契约和门禁映射。

## 任务路由表

| 任务类型 | 目标 Skill | 触发条件 | 输入 | 输出 |
|----------|-----------|----------|------|------|
| 独立 Review/Research | `/jules` (review 模板) | INV tracker 标记 Jules dispatch | Prompt Envelope + Context refs | `investigation/INV-*_jules_review.md` |
| 独立 Implement | `/jules` (implement 模板) | B file 标记 Jules handoff | Prompt Envelope + Interface contracts | PR + `results/TASK-XXX.md` |
| 标准开发 | `/pdca` | B file `method: pdca` | B file + tracker active rows | PDCA Output Contract |
| 同会话子任务 | `subagent-driven-development` | ≥2 独立子任务可并行 | Worker scopes (≤3) | WORKER_REPORT (≤12 lines) |
| 独立会话 | `executing-plans` | 需隔离上下文 | Implementation plan | Session artifacts |

## 统一输出契约（所有路由共用字段）

每个执行结果（无论 PDCA / Jules / subagent）**必须**包含以下固定字段，格式为 RefSpec：

| 字段 | 格式 | 说明 |
|------|------|------|
| `Read List (RefSpec)` | `path:Lx-Ly` 或 `path#anchor` | 实际读取的文件/锚点 |
| `Write List (RefSpec)` | 同上 | 创建或修改的文件 |
| `Evidence Pointers (RefSpec)` | Top 3-5 | 支持结论的关键代码/文档锚点 |
| `Plan Update Targets (RefSpec + bullet)` | `path#anchor` + ≤3 行编辑建议 | 回流到计划的具体修改点 |

> 字段名固定，禁止同义词替代（如不许用 "Files Changed" 替代 "Write List"）。

### 证据形态标准（所有 worker 必须遵守）

| 规则 | 说明 |
|------|------|
| RefSpec 格式 | `path:Lx-Ly` 或 `path#anchor`（禁止裸路径或 "see file X"） |
| Inline excerpt | ≤60 lines；超过必须 offload 到独立文件 + RefSpec 引用 |
| Evidence offload | Tool/log/trace 输出 → 独立文件（`investigation/tool_outputs/` 或 `results/`）；正文只留 ≤3 行摘要 + RefSpec |
| 禁止全文粘贴 | 不允许在结果文件中粘贴完整源码/日志；只保留关键片段 + RefSpec 指向原文 |

## 门禁映射

| Skill | 前置门禁 | 执行中门禁 | 完成门禁 |
|-------|---------|-----------|---------|
| plan-doc-editor | G-INV → G-DESIGN → G-READY | — | G-CLOSED (DoD) |
| PDCA | Gate A (parity) | Gate B (JUnit) + Gate C (audit) | Gate D (docs) |
| jules-cli | GATE-1 (pending) + GATE-2 (ASCII) + GATE-3 (smoke) + GATE-6 (branch) | — | Gate-J (review PR merged) |

## Gate-J 定义

- **触发**：B file frontmatter 含 `gate_j: required`
- **产物路径**：`<plan_module>/investigation/INV-*_jules_review.md`（固定在计划模块内，不允许全局 docs 目录）
- **产物内容**：必须包含统一输出字段（Read/Write/Evidence/Plan Update Targets）+ RefSpec 格式
- **通过**：Review PR 已 merge 且无 🔴 Critical issues 未解决
- **失败**：B file 回退为 `blocked`，写 `questions/Q-NNN` 阻塞 tracker

## 回流协议

Jules 结果 → plan-doc-editor 的路径：

1. PR merge 后，结果摘要写入 `investigation/INV-*` 或 `results/TASK-XXX.md`
2. `Plan Update Targets (RefSpec)` 指明要更新的计划文件和锚点
3. plan-doc-editor 按 Workflow C（提炼）消费结果，更新 `references/P*` 和 B files
4. 更新 `_tracker.md`，标记 INV 为 REVIEWED

### Tracker 治理规则

> Workers（PDCA / Jules）**不直接编辑** `_tracker.md`。
> 只输出 `Plan Update Targets (RefSpec + bullet edits)`，由 plan-doc-editor 统一应用。

如必须手动改 tracker（例如标记 status = DONE）：

1. **只改单元格值**（如 status），不改表头 / 列数 / 管道对齐
2. **10 秒校对**：修改后检查 (a) 每行 `|` 数量一致，(b) header 分隔行存在 `|---|...|`，(c) 无空行打断表格
3. plan-doc-editor 在 G-SYNC 阶段会校验 tracker 表格完整性

## 并行拆分约束（Jules implement handoff）

当 plan-doc-editor 拆分任务并 handoff 到 Jules 并行 implement 时，**必须**满足：

1. **修改白名单互不相交**：每个 TASK 的 Modification Whitelist 不得重叠
2. **完整任务指令**：每个 `TASK-XXX.md` 包含完整 Extracted Task Text（禁止 "see CURRENT.md §3"）
3. **接口契约先行**：共享接口在 dispatch 前冻结，作为所有 TASK 的只读上下文
