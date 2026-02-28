# AI Agent 开发者技能库：上下文工程与多节点编排

> [English](README.md) | **中文**

专为解决大型 LLM 辅助软件工程中的三大痛点而设计的专业 Agent 技能库：**长上下文退化 (Context Degradation)**、**架构漂移 (Architectural Drift)** 与 **质量保障 (Quality Assurance)**。

本仓库提供了三个深度协同的技能包，将您的 AI 编程助手（如 Claude Code 或 Cline）从“单文件编辑器”升级为“多 Agent 编排引擎”，使其具备零技术债务交付史诗级 (Epic-scale) 级特性的能力。

---

## 🏗️ 三大核心基石 (Skills)

| 技能 | 层面 | 核心机制 | 入口 |
|------|------|----------|------|
| **`plan-doc-editor`** | **控制面**<br/>*(上下文管家)* | 将宏大的目标重构为两级扁平的“模块树”。实现**渐进式披露 (Progressive Disclosure)**，仅优先加载索引，并通过 `Q-` 与 `INV-` 文件追踪未知变量生命周期。 | [`plan-doc-editor/SKILL.md`](plan-doc-editor/SKILL.md) |
| **`pdca-ai-coding`** | **执行面**<br/>*(TDD 引擎)* | 用纪律严明的 Plan-Do-Check-Act 循环取代自由散漫的编码。强制推行 **ATDD 门禁**（奇偶校验、JUnit 证据、审计与文档对照）、熔断器与上下文预算策略。 | [`pdca-ai-coding/SKILL.md`](pdca-ai-coding/SKILL.md) |
| **`jules-cli`** | **Worker 面**<br/>*(异步集群)* | 将独立的调研、代码审查或边界分明的开发任务分发给异步 Worker (Jules)。提供严格的 `Prompt Envelopes` (提示词封装条约) 和批量调度脚本。 | [`jules-cli/SKILL.md`](jules-cli/SKILL.md) |

---

## 🧠 核心架构哲学

### 1. 上下文防御 (Context Defense)
抛弃无脑填塞 Token 的低效方式，系统采用 **先扫描后阅读 (Scan-Before-Read)** 与 **JIT 按需指针** 协议。控制面仅静态映射项目的骨架（标题与表格），只有当触发器条件满足时，才顺着 `RefSpec` 指针（如 `path#anchor`）动态加载指定范围的深层上下文，有效规避“迷失在中间 (Lost-in-the-Middle)”现象。

### 2. 物理与逻辑验证门禁 (The Verification Gates)
`pdca-ai-coding` 拒绝仅凭 AI 的“自言自语”确认质量，它通过外部脚本建立物理防线：
- **Gate A (一致性)**：校验执行计划与测试计划 (`TEST_PLAN`) 的严格对应。
- **Gate B (物理证据)**：在标记任务完成前，强制要求通过 JUnit/Pytest/Vitest 的 dry-run 拦截。
- **Gate C/D**：进行计划防篡改审计与 API 文档更新校验。

### 3. 一元化的集成契约 (Unified Integration Contract)
跨越三个层面的输入与输出已被彻底标准化。任何任务（无论由本地执行还是异步节点执行），其结束标记必须是标准的 **RefSpec 契约返回**：
- `Read List` (挂载了哪些上下文)
- `Write List` (突变了哪些文件)
- `Evidence Pointers` (指向验证结论的关键日志/代码行)
- `Plan Update Targets` (对上游控制面板的设计调整建议)

---

## 🔄 弹性协作模式

该工具链可随项目规模弹性伸缩，支持三种协作拓扑：

### 模式一：单兵作战 (Greenfield / Standalone)
**适用场景**：中小型功能开发、局部缺陷修复（1-3 小时的任务段）。
**运转机制**：以 `pdca-ai-coding` 为唯一引擎。分析仓库、提出备选方案、将其拆解为严谨的 RED/GREEN/REFACTOR TDD 步骤，并通过内置回顾机制进行自我修正。

### 模式二：顶层编排 (Top-Down Orchestration)
**适用场景**：史诗级特性交付、跨层级的系统重构。
**运转机制**：由 `plan-doc-editor` 充当主脑。它绘制依赖图谱，将阻塞性问题打包发给 `jules-cli` 调研，同时将静态的基线要求（B-files 规范）喂给本地 `pdca-ai-coding` 稳步推进执行，断绝无头苍蝇式的全局游荡和雪崩式的代码破坏。

### 模式三：异步并发集群 (Asynchronous Swarm)
**适用场景**：大规模机械性代码审查、架构漏洞广度扫描。
**运转机制**：主脑将工作切割为修改集不相交的任务碎片，通过 `jules-cli` 的 `dispatch_prompt_pack.py` 并行唤起多台云端 Agent，以 PR 的形式安全合流，并在合并前引入 **Gate-J** 异步审查关卡。

*(关于更详尽的 I/O 边界与调度表，请查阅 [集成路由参考](plan-doc-editor/references/integration-router.md))*

---

## 🚀 安装与用法

1. 克隆或下载本仓库。
2. 挑选符合您当下开发流的 Skill 目录。
3. 将该目录（如 `plan-doc-editor`）直接拖入 AI 助手的专门目录中（例如 `.agent/skills/` ）。
4. 大语言模型在读取其 `SKILL.md` 的描述字段后，会在您发送对应自然语言指令（如“请帮我拆解一下这份重构计划”、“把这个 review 任务发给 Jules”）时自动无缝唤醒并接管流程。

---

## 📜 致谢与开源许可

- **PDCA TDD 引擎**：Fork 自 [MarcherGA/pdca-ai-coding-skill](https://github.com/MarcherGA/pdca-ai-coding-skill)，并做了重度二次开发（基于 [Ken Judy 关于 AI 辅助编码的深度文章](https://www.infoq.com/articles/PDCA-AI-code-generation/)）。
- **上下文工程 (Context Engineering)**：有关多 Agent 协调、降级上下文保护与动态预算等思想内核，深受 Murat Can Koylan 所著 [Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) 的启发。
- **架构编排**：控制面 (`plan-doc-editor`)、Worker 面 (`jules-cli`)、ATDD 逻辑门禁组及统一路由契约，均为本项目的原创性扩展成果。

基于 [MIT License](LICENSE) 授权。
