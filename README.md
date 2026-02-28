# Skill Development

**English** | [中文](README_CN.md)

A collection of AI Agent Skills covering plan management, code quality, and remote task orchestration. Designed to mitigate long-context drift, maintain code quality, and decompose complex goals.

## Skills

| Skill | Purpose | Entry Point |
|-------|---------|-------------|
| **plan-doc-editor** | Plan Management (Control Plane): Restructures complex plans into two-level flat modules with progressive context loading, investigation tracking, and batch task management | [`plan-doc-editor/SKILL.md`](plan-doc-editor/SKILL.md) |
| **pdca-ai-coding** | Code Development (Execution Plane): PDCA-cycle AI-assisted coding framework with built-in TDD discipline, ATDD gates, and quality metrics | [`pdca-ai-coding/SKILL.md`](pdca-ai-coding/SKILL.md) |
| **jules-cli** | Remote Orchestration (Worker Plane): Dispatches async tasks to Jules with Review/Implement templates, batch scheduling, and result backflow | [`jules-cli/SKILL.md`](jules-cli/SKILL.md) |

## Collaborative Architectures

This toolkit is not restricted to a single top-down workflow. Depending on task complexity, it supports three flexible architecture patterns:

### Pattern 1: Greenfield / Zero-Infrastructure
**Use Case**: Small to medium feature development, localized refactors (1-3 hour tasks).
**Mechanism**: No infrastructure required. Uses `pdca-ai-coding` as a standalone workflow to complete the loop.
```
pdca-ai-coding (Standalone)
  ├── Analysis (Context discovery & alternative approaches)
  ├── Planning (Testing-driven task breakdown)
  ├── Implementation (Strict TDD loops)
  └── Retrospective (Knowledge capture)
```

### Pattern 2: Top-Down Orchestration
**Use Case**: Massive epics, cross-module refactoring, or extremely large codebases where combating context drift is critical.
**Mechanism**: `plan-doc-editor` acts as the Brain, mapping out a 2-tier flat plan. It progressively loads context, hands off feature development B-files to the local `pdca-ai-coding` agent, and dispatches time-consuming audits to `jules-cli`.
```
plan-doc-editor (Control Plane - Context Manager)
  ├── 1. Investigation (INV-*) → Dispatched to jules-cli or local subagent
  ├── 2. Design (Px/Ax) → Freezes ATDD specs & architectural contracts
  └── 3. Execution (B-*)
        ├── Core business logic → pdca-ai-coding (Operating on static baselines)
        └── Independent tasks → jules-cli (Async PRs)
```

### Pattern 3: Asynchronous Swarm
**Use Case**: Broad codebase audits, repetitive mechanical refactoring, or simultaneous changes across decoupled microservices.
**Mechanism**: The main agent splits work into non-overlapping tasks and uses `jules-cli`'s batch dispatcher (`dispatch_prompt_pack.py`) to wake up multiple cloud agents in parallel.
```
Main Agent (or plan-doc-editor)
  └── Generates Prompt Pack (Review/Implement templates)
        └── dispatch_prompt_pack.py (Handles rate limits + safety gates)
              ├── Worker 1 (Jules) → PR #101
              ├── Worker 2 (Jules) → PR #102
              └── Worker 3 (Jules) → PR #103
```

> **Routing Contract**: For the complete truth table on I/O boundaries and gate mappings between these components, see [`plan-doc-editor/references/integration-router.md`](plan-doc-editor/references/integration-router.md).

## Attribution

- **PDCA Framework**: Forked from [MarcherGA/pdca-ai-coding-skill](https://github.com/MarcherGA/pdca-ai-coding-skill) (based on [Ken Judy's InfoQ article](https://www.infoq.com/articles/PDCA-AI-code-generation/)). Extensively extended with ATDD gates, Lite Mode, Circuit Breaker, session templates, Discovery Ladder, and more.
- **Context Engineering Reference**: Several mechanisms (progressive loading, context degradation prevention, multi-agent coordination patterns) were informed by [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering).
- **plan-doc-editor** and **jules-cli** are original to this project.

## Installation

Each Skill is triggered by the `description` field in its `SKILL.md` frontmatter. Place the entire Skill directory into your AI Agent's skills folder.

## License

[MIT](LICENSE) — Original PDCA framework by MarcherGA, extensions by YiK1991.
