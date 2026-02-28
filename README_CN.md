# Skill Development

[English](README.md) | **中文**

AI Agent 技能集合 — 覆盖计划管理、代码质量、远程任务编排三个核心环节。专注于解决长上下文漂移、代码质量下降和复杂任务分解问题。

## 技能一览

| 技能 | 用途 | 入口 |
|------|------|------|
| **plan-doc-editor** | 计划管理（控制面）：将复杂计划拆解为两级扁平模块，支持渐进式上下文加载、调查跟踪、批量任务管理 | [`plan-doc-editor/SKILL.md`](plan-doc-editor/SKILL.md) |
| **pdca-ai-coding** | 代码开发（执行面）：基于 PDCA 循环的 AI 辅助编码框架，内置 TDD 纪律、ATDD 门禁、质量度量 | [`pdca-ai-coding/SKILL.md`](pdca-ai-coding/SKILL.md) |
| **jules-cli** | 远程编排（Worker 面）：向 Jules 分发异步任务，支持 Review/Implement 模板、批量调度、结果回流 | [`jules-cli/SKILL.md`](jules-cli/SKILL.md) |

## 协同架构模式

本组件库并非只能以单一的自上而下模式运行，而是根据任务复杂度支持三种灵活的架构模式：

### 模式一：单兵作战 (Greenfield / Zero-Infrastructure)
**适用场景**：中小型功能开发、局部重构（1-3 小时任务）
**核心机制**：无需任何前置基础设施，直接使用 `pdca-ai-coding` 完成闭环。
```
pdca-ai-coding (单体运行)
  ├── Analysis (现状分析与方案比较)
  ├── Planning (测试驱动的任务拆解)
  ├── Implementation (执行 TDD 循环)
  └── Retrospective (复盘与协议沉淀)
```

### 模式二：顶层编排 (Top-Down Orchestration)
**适用场景**：大型史诗级任务、跨模块重构、需要防范长上下文漂移的超大工程。
**核心机制**：由 `plan-doc-editor` 充当大脑建立两级扁平计划，按需加载上下文，将具体开发任务交给本地 `pdca` 执行，将耗时的代码审计或外围修正交给 `jules-cli`。
```
plan-doc-editor (控制面 - 上下文管家)
  ├── 1. 调查分发 (INV-*) → 交给 jules-cli 或 本地 subagent
  ├── 2. 计划设计 (Px/Ax) → 冻结 ATDD 规范与架构契约
  └── 3. 执行下发 (B-*)
        ├── 核心业务开发 → pdca-ai-coding (基于静态基线)
        └── 独立/并行任务 → jules-cli (异步 PR)
```

### 模式三：异步集群 (Asynchronous Swarm)
**适用场景**：大规模代码审查、批量机械化重构、针对多个独立服务的同时修改。
**核心机制**：主 Agent 将任务切分为互不干扰（无重叠修改集）的碎片指令，通过 `jules-cli` 的批量分发脚本 (`dispatch_prompt_pack.py`) 唤醒多个云端 Agent 并行工作。
```
主 Agent (或 plan-doc-editor)
  └── 生成 Prompt Pack (Review/Implement 模板)
        └── dispatch_prompt_pack.py (本地限流与防呆拦截)
              ├── Worker 1 (Jules) → PR #101
              ├── Worker 2 (Jules) → PR #102
              └── Worker 3 (Jules) → PR #103
```

> **路由契约参考**：有关各组件间完整的输入/输出/门禁映射表，请参阅 [`plan-doc-editor/references/integration-router.md`](plan-doc-editor/references/integration-router.md)。

## 来源与致谢

- **PDCA 框架**：Fork 自 [MarcherGA/pdca-ai-coding-skill](https://github.com/MarcherGA/pdca-ai-coding-skill)（基于 [Ken Judy 的 InfoQ 文章](https://www.infoq.com/articles/PDCA-AI-code-generation/)）。在原版基础上大幅扩展了 ATDD 门禁、Lite Mode、Circuit Breaker、会话模板、Discovery Ladder 等机制。
- **Context Engineering 参照**：部分机制（渐进式加载、上下文退化防护、多 Agent 协调模式）参考了 [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)。
- **plan-doc-editor** 和 **jules-cli** 为本项目原创。

## 安装

每个技能的安装方式以其 `SKILL.md` 的 frontmatter `description` 字段为触发条件。将整个技能目录放入 AI Agent 的 skills 目录即可。

## 许可

[MIT](LICENSE) — 原版 PDCA 框架由 MarcherGA 创建，扩展部分由 YiK1991 维护。
