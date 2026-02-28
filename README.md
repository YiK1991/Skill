# Skill Development

AI Agent Skills 集合 — 覆盖计划管理、代码质量、远程任务编排三个核心环节。

## Skills

| Skill | 用途 | 入口 |
|-------|------|------|
| **plan-doc-editor** | 计划管理（控制面）：将复杂计划拆解为两级扁平模块，支持渐进式上下文加载、调查跟踪、批量任务管理 | [`plan-doc-editor/SKILL.md`](plan-doc-editor/SKILL.md) |
| **pdca** | 代码开发（执行面）：基于 PDCA 循环的 AI 辅助编码框架，内置 TDD 纪律、ATDD 门禁、质量度量 | [`pdca/SKILL.md`](pdca/SKILL.md) |
| **jules-cli** | 远程编排（Worker 面）：向 Jules 分发异步任务，支持 Review/Implement 模板、批量调度、结果回流 | [`jules-cli/SKILL.md`](jules-cli/SKILL.md) |

## 协同架构

```
plan-doc-editor (控制面)
  ├── 调查分发 → jules-cli → Jules Agent
  ├── 计划设计 → ATDD 规范
  └── 执行下发
        ├── pdca (标准开发)
        ├── subagent (同会话并行)
        └── jules-cli (远程独立任务)
```

统一路由契约：[`plan-doc-editor/references/integration-router.md`](plan-doc-editor/references/integration-router.md)

## 来源与致谢

- **PDCA 框架**：Fork 自 [kenjudy/pdca-code-generation-process](https://github.com/kenjudy/pdca-code-generation-process)，基于 [Ken Judy 的 InfoQ 文章](https://www.infoq.com/articles/PDCA-AI-code-generation/)。在原版基础上大幅扩展了 ATDD 门禁、Lite Mode、Circuit Breaker、会话模板、Discovery Ladder 等机制。
- **Context Engineering 参照**：部分机制（渐进式加载、上下文退化防护、多 Agent 协调模式）参考了 [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)。
- **plan-doc-editor** 和 **jules-cli** 为本项目原创。

## 安装

每个 Skill 的安装方式以其 `SKILL.md` 的 frontmatter `description` 字段为触发条件。将整个 Skill 目录放入 AI Agent 的 skills 目录即可。

## License

[MIT](LICENSE) — 原版 PDCA 框架由 Ken Judy 创建，扩展部分由 YiK1991 维护。
