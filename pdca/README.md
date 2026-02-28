# PDCA AI Coding Skill

基于 [Ken Judy 的 InfoQ 文章](https://www.infoq.com/articles/PDCA-AI-code-generation/) 的 PDCA（Plan-Do-Check-Act）AI 辅助编码框架。

## 来源

Fork 自 [MarcherGA/pdca-ai-coding-skill](https://github.com/MarcherGA/pdca-ai-coding-skill)（MIT License）。

## 与原版的主要差异

在原版基础上进行了大量扩展和定制，主要包括：

| 领域 | 原版 | 当前版本 |
|------|------|----------|
| 门禁系统 | 无 | ATDD Gate A/B/C/D + Circuit Breaker + Gate-J |
| 执行模式 | 单一全链路 | Lite Mode（≤3 文件快速通道）+ 完整链路 |
| 会话管理 | 手动记录 | 结构化 session-template + 自动初始化脚本 |
| 上下文管理 | 无 | Discovery Ladder + Edge Anchors + Context Budget |
| 集成 | 独立使用 | 与 plan-doc-editor（控制面）、jules-cli（Worker 面）协同 |
| 脚本 | `track_metrics.py` | + `atdd_gate.py` + `doc_gate.py` + `init_session.py` |

## 目录结构

```
pdca/
├── SKILL.md             ← 主入口（AI Agent 读取此文件）
├── assets/              ← 模板（session-template、TEST_PLAN_TEMPLATE 等）
├── references/          ← 详细参照文档（prompt 模板、working agreements 等）
└── scripts/             ← 门禁脚本和工具
```

## 使用

详见 [`SKILL.md`](SKILL.md)。

## License

[MIT](../LICENSE) — 原版由 Ken Judy 创建。
