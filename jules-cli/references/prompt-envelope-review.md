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

## 4) 报告放置规则
审查报告必须放在指定位置：
- 先查看 `00_Documentation/` 的现有目录结构
- 默认路径：`00_Documentation/99_Inbox/<模块>/<日期>_<主题>/review_report.md`
- 如果是 Prompt Pack 的一部分：`jules_pack/results/TASK-XXX_review.md`
- 日志证据：`08_System_Maintenance/Logs/`
- **多文件输出**：如果 Prompt 要求分解输出（例如 `F-NNN` 和 `R-NNN`），在声明的目录内输出多个文件
- **快照覆写**：如果 Prompt 指定了 `@Snapshot_xxx.md`，覆写该文件而非新建
- **禁止**在与现有结构不一致的位置创建新目录

## 5) Output Format（报告结构 — 严格遵守）

### 审查摘要
```
审查范围：<被审查的文件/目录列表>
审查基准：<使用的规范文件列表>
审查维度：<本次检查的维度>
结果：Found <N> urgent issues, <M> suggestions.
```

### Urgent Issues（必须修复）
<违背规范、安全漏洞、严重逻辑错误>

```
#### Issue 1: <简要描述>
- 严重级别：🔴 Critical | 🟠 High
- 位置：`<FilePath>` line <N>-<M>
- 违反规范：<引用 gemini.md / rules.md 的具体条款>
- 现状代码：
  ```<lang>
  <当前代码片段>
  ```
- 问题分析：<解释为什么这是问题>
- Suggested Fix（仅建议，不要实施）：
  ```<lang>
  <建议修改后的代码>
  ```
- 后续 Implement 任务：<建议的任务描述，用于后续创建 TASK>
```
(每个 issue 重复此结构)

### Suggestions（建议改进）
<架构优化、命名改进、代码可读性提升>

```
#### Suggestion 1: <简要描述>
- 严重级别：🟡 Medium | 🟢 Low
- 位置：`<FilePath>` line <N>
- 理由：<为什么建议修改>
- Suggested Fix：<建议方案>
```

### Risk Assessment
- overall_risk: (low | medium | high)
- risk_areas: <高风险区域列表>
- recommended_priority: <建议修复的优先顺序>

### 后续任务建议
将需要代码修改的 issue 整理为可执行的 Implement 任务列表：
```
| 优先级 | 建议任务 | 涉及文件 | 对应 Issue |
| ------ | -------- | -------- | ---------- |
| P0     | ...      | ...      | Issue #1   |
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
