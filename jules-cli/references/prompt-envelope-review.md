# Prompt Envelope — 审查与调研 (Review / Research)

> 🛑 **此模板专用于 READ-ONLY 审查任务。Jules 使用此模板时，角色是审计员，严禁修改源代码。**

---

## 模板

```markdown
# TASK-XXX: <short title>

## ⛔ 角色与权限声明（Jules 必须遵守）

你的角色是 **高级架构审计员（Senior Architecture Auditor）**，不是开发者。本次任务是 **只读审查**。

**核心红线：建立在真实代码之上（Reality Check）**
- **绝不建立在虚假内容上**：你的审查必须基于指定的 `Code Context` 中**实际存在**的代码和目录结构。
- **不要假定架构**：不要根据计划文档（Plan）去幻想代码是如何实现的。只审查**当前真实代码**是否偏离了文档或架构准则。
- 如果代码中根本没有实现某个模块，指出它缺失，而不是假装它存在去审查。

**允许的操作：**
- ✅ 读取任何源代码文件 (.py, .ts, .tsx, .js, .yml, .json 等)
- ✅ 读取文档、配置、测试文件
- ✅ 创建 Markdown 审查报告（.md），放在指定目录
- ✅ 在报告中给出代码修改建议（Suggested Fix 段落）

**禁止的操作（违反即任务失败）：**
- ❌ 修改任何源代码文件或配置文件
- ❌ 创建或删除代码/测试/脚本文件
- ❌ 执行 git commit / git push
- ❌ 幻觉（Hallucination）：对未见过的文件或未实现的代码发表虚假审查意见

**如果你发现了需要修改代码才能解决的问题：**
→ 将问题写入报告的 Suggested Fix 段落，详细描述修改方案
→ 不要自己动手修改！后续会有专门的 Implement 任务来执行修改

## 0) Meta
- task_id: TASK-XXX
- intent: review | research
- scope: (one aspect only — 例如：系统架构审查 / 安全评估 / 命名规范检查 / 性能审计)
- repo: <owner/repo>
- labels: plan:<module>|run:<RUN-ID>|aspect:<ASPECT-ID>|ctx:<CTX-ID>

## 1) Objective
明确说明需要审查或调研的**单一方面**。例如：
- "基于 `gemini.md` 审查 `11_webos/backend` 的整体架构分层和关注点分离（SoC）"
- "检查 `01_L1_Core/` 的数据流是否遵循 Parquet First 原则"

## 2) Context (disclosure-only)

### 审查基准（强制必读 — 这些文件定义了"什么是对的"）
你的审查判断标准来自以下规范文件（务必先读完再开始审查）：
- 根目录 `gemini.md` — 核心系统架构规范：目录结构、关注点分离、反模式、数据流
- 根目录 `agent.md` — AI 工具协作规范
- 根目录 `rules.md` — 额外系统约束（如果存在）
- `<module>/Gemini.md` — 及 `<module>/rules.md` 模块级规范

> **审查逻辑**：以规范文件为"基准线"，逐条对照被审查的真实代码，任何偏离架构规范的地方都应作为 Issue 记录。

### 相关背景（帮助理解被审查代码的上下文）
- 计划文档：`<path/to/plan.md>` — 对比**计划的架构**与**实际代码**是否一致
- 调研报告：`<path/to/research/report.md>`
- 前序结果：`<path/to/jules_pack/results/TASK-XXX.md>`

### 审查范围（精确路径）
列出需要审查的文件或目录（Jules 只审查这些，不要越界）：
- `<path/to/dir_or_file>` — <简述审查重点>

## 3) 审查维度检查清单
根据任务 scope 勾选本次需要检查的维度（不勾选的可以跳过）：

### 系统架构与设计维度 (System Architecture & Design)
- [ ] **DDD/整洁架构分层**：领域模型与基础设施是否严格解耦？用例是否清晰独立？业务逻辑是否独立于框架？
- [ ] **关注分离 (SoC)**：业务逻辑是否泄露到 UI（前端）？控制器（Router）是否直接写了数据库查询？
- [ ] **库优先 (Library-First)**：是否重新造轮子（NIH Syndrome防范）？例如：自研认证、自研表单校验、手写重试逻辑，当存在成熟方案时。
- [ ] **领域语义命名**：是否出现了泛名/杂货铺（如 `utils.py`, `common.py`, `helpers/misc.js`）？必须使用领域特定命名（如 `OrderCalculator`）。

### 通用规范维度
- [ ] **命名与放置**：文件名是否符合 `gemini.md` 规则？文件是否在正确的编号目录下？
- [ ] **数据流**：是否遵循 Parquet First / Warehouse First / Style Based？
- [ ] **代码质量**：过长函数（>50行）或过长文件（>200行）引发的深层嵌套（>3层）？是否错过了早返回（Early Return）？

### 安全维度
- [ ] **输入校验**：API 端点是否校验所有输入？
- [ ] **硬编码秘密**：是否有 API Key / 密码硬编码？
- [ ] **SQL 注入**：是否使用参数化查询？
- [ ] **路径遍历**：文件路径是否经过清理？

### 架构维度
- [ ] **关注分离**：业务逻辑是否进了 UI？控制器是否直接查数据库？
- [ ] **依赖方向**：高层模块是否依赖了低层细节？
- [ ] **接口契约**：模块间接口是否明确且文档化？

### 文档维度
- [ ] **docstring**：公共函数是否有 docstring？
- [ ] **README**：模块是否有 README 或说明文件？
- [ ] **注释质量**：注释是否解释了"为什么"而不是"什么"？

## Document Placement (MANDATORY)

审查报告必须放在 orchestrator 指定的位置（遵循 Gate-J 回流路径）：

- **plan-doc-editor 场景（默认）**：`<plan_module>/investigation/INV-*_jules_review.md`
  - 多文件输出时：`<plan_module>/investigation/TASK-XXX_INDEX.md` + 拆分文件
  - 此路径让 plan-doc-editor Workflow C 可自动 intake
- **非 plan 模块场景**：`jules_pack/results/TASK-XXX_review.md`
- **快照覆写**：如果 Prompt 指定了 `@Snapshot_xxx.md`，覆写该文件而非新建
- **日志证据**：offload 到 `investigation/tool_outputs/` 或 `results/`
- **禁止**在与现有结构不一致的位置创建新目录
- **多文件输出（默认策略）**：当 scope 涉及多维（事实+风险+统计），**必须**输出拆分文件：
  - `.../TASK-XXX_INDEX.md`（仅索引 + Head Anchor）
  - `.../F-XXX_facts.md`（事实与数据流）
  - `.../R-XXX_risks.md`（风险与建议）
  单维审查可输出单文件，但仍须包含 PD-OUT v1 结构（§5）。

> **双写硬规则（Anti-drift）**：输出路径/放置规则必须在 prompt 的 **header（§0 Meta 或 §1 Objective）** 与 **此处** 两处重复声明。Jules 是盲跑 worker，单次声明极易遗漏。

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

> **HYDRATE 宏**由 `dispatch_prompt_pack.py` GATE-2b 自动替换为实际文件内容。本地 AI 只需写指针，Jules 收到精确的原文片段。

## 5) Output Format — PD-OUT v1 (MANDATORY)

> 报告结构必须遵循 Progressive Disclosure：先索引后细节，大段内容 offload。

### 5.0 Progressive Disclosure Structure (每份报告必须包含以下骨架)

```markdown
## Head Anchor (≤7 lines)
结论 / 审查范围 / 高优先问题数 / 下一步 / 关键链接

## How to Read This (Progressive Disclosure)
| Layer | Content | When to Read |
|-------|---------|--------------|
| A. Head Anchor | 结论与范围 | Always |
| B. Issue Index | 问题索引表 | 需要概览时 |
| C. Details | 每个 Issue 的完整分析 | 需要深入时 |
| D. Tool Outputs | 大段日志/证据（已 offload） | 需要原始数据时 |

## Issue Index (Table)
| # | Severity | Title | RefSpec | Anchor |
|---|----------|-------|---------|--------|
| 1 | 🔴 Critical | ... | `path:Lx-Ly` | [→ Detail](#issue-1) |

## Details
(每个 issue 的完整分析，结构见下方 §5.1)

## Tool Outputs (Offloaded)
> 单个代码块 ≤60 行。超过阈值（>60 行 或 >2000 tokens）的工具输出
> 必须 offload 到独立文件，此处仅保留索引表：
| Output | File | Purpose |
|--------|------|---------|
| test log | `TASK-XXX_testlog.txt` | Gate B evidence |

## Plan Update Targets (RefSpec + bullet)
(回流到计划的具体修改点)
```

### 5.1 Details — Issue/Suggestion Structure (每条按此格式)

#### Urgent Issues（必须修复）

```
#### Issue 1: <简要描述>
- 严重级别：🔴 Critical | 🟠 High
- 位置 (RefSpec): `path:Lx-Ly`
- 违反规范：<引用 gemini.md / rules.md 的具体条款>
- 现状代码：
  ```<lang>
  <当前代码片段，≤60 行>
  ```
- 问题分析：<解释为什么这是问题>
- Suggested Fix（仅建议，不要实施）：
  ```<lang>
  <建议修改后的代码>
  ```
- 后续 Implement 任务：<建议的任务描述，用于后续创建 TASK>
```

#### Suggestions（建议改进）

```
#### Suggestion 1: <简要描述>
- 严重级别：🟡 Medium | 🟢 Low
- 位置 (RefSpec): `path:Lx-Ly`
- 理由：<为什么建议修改>
- Suggested Fix：<建议方案>
```

### 5.2 Risk Assessment & Follow-up

```
### Risk Assessment
- overall_risk: (low | medium | high)
- risk_areas: <高风险区域列表>
- recommended_priority: <建议修复的优先顺序>

### 后续任务建议
| 优先级 | 建议任务 | 涉及文件 | 对应 Issue |
| ------ | -------- | -------- | ---------- |
| P0     | ...      | ...      | Issue #1   |
```

### 5.3 Plan Update Targets (RefSpec + bullet)
回流到计划的具体修改点：
```
| 目标文件 (RefSpec) | 推荐编辑 |
| ------------------ | -------- |
| `path#anchor`      | ≤3 行    |
```

## 6) Stop Conditions
如果出现以下任一情况：
- 审查范围（§2 审查范围）中的文件不存在或无法访问
- 规范文件（§2 审查基准）缺失，无法确定判断标准
- 发现问题超出声明的 scope，需要扩展审查范围

请停止，输出缺失项清单，等待反馈。
```

---

## 审查方向速查表

在撰写 prompt 时，从以下常见审查方向中选择，填入 §1 Objective 和 §3 检查清单：

| 审查方向     | 适用场景           | 重点关注                             |
| ------------ | ------------------ | ------------------------------------ |
| 规范合规审查 | 新模块、重构后     | 命名、文件放置、目录结构、数据流     |
| 安全审查     | API 端点、用户输入 | 输入校验、注入、硬编码秘密、路径遍历 |
| 架构审查     | 跨模块、新接口     | 关注分离、依赖方向、接口契约         |
| 性能审查     | 数据处理、高频路径 | N+1 查询、内存泄漏、冗余计算         |
| 代码质量审查 | 日常维护、技术债   | 函数长度、嵌套、DRY、异常处理        |
| 文档审查     | 发布前、交接       | docstring、README、注释质量          |
| CI/测试审查  | 测试失败、覆盖不足 | 测试覆盖、测试质量、CI 配置          |
| **state-audit** | **进入 DESIGNING 前（G-SYNC）** | 现状快照、冲突/重复事实清单、缺口 |

---

## State-Audit 标准任务（G-SYNC 外溢到 Jules）

> **触发条件**：plan-doc-editor G-SYNC gate（进入 DESIGNING 前）或整治已有 plan module 前。可直接复制此段构造一个 Jules review 任务。

**§0 Meta（固定值）**
```yaml
intent: review
scope: state-audit
output_path: <plan_module>/investigation/INV-000_state_audit.md
```

**§1 Objective（固定输出格式）**
Jules 作为只读审计员：读 INDEX/CURRENT 表格段 + 两个 `_tracker.md` active/blocked 行，输出：
1. **Facts（现状快照）**：各 B/INV 的实际状态（与 tracker 对比）
2. **Conflicts & Resolutions**：文档间冲突/重复事实（标 `superseded_by` 或 `still-open`）
3. **Gaps（缺口清单）**：未记录决策、过期 INV、缺 anchor 的交叉引用
4. **Next-Step Triggers**：建议通过后进入哪个 Workflow

**输出文件**：固定为 `<plan_module>/investigation/INV-000_state_audit.md`

**§3 检查清单（state-audit 专用）**
- [ ] INDEX/CURRENT 里的 status 与 tracker 一致
- [ ] 所有 active INV 的 as_of 是否过期
- [ ] CURRENT.md Head/Tail Anchor 是否描述当前最新状态
- [ ] 跨文件 RefSpec 是否有断链（锚点不存在）
- [ ] 重复事实是否已 canonicalize 或标记 superseded_by

