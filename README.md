# AI Agent Developer Skills: Context Engineering & Orchestration

> **English** | [中文](README_CN.md)

A professional suite of AI Agent Skills architected to solve the triad of challenges in LLM-assisted software engineering: **Long-Context Degradation**, **Architectural Drift**, and **Quality Assurance**.

This repository provides three synergistic skill packages that transform an AI Coding Assistant (like Claude Code or Cline) from a single-file editor into a multi-agent orchestration engine capable of delivering epic-scale features with zero technical debt.

---

## 🏗️ The Three Pillars (Skills)

| Skill | Plane | Core Mechanism | Entry Point |
|-------|-------|----------------|-------------|
| **`plan-doc-editor`** | **Control Plane**<br/>*(Context Manager)* | Restructures monolithic goals into a 2-tier flat hierarchy. Implements **Progressive Disclosure** (loading only active indexes first) and tracks unknowns via `Q-` and `INV-` lifecycle files. | [`plan-doc-editor/SKILL.md`](plan-doc-editor/SKILL.md) |
| **`pdca-ai-coding`** | **Execution Plane**<br/>*(TDD Engine)* | Replaces free-form coding with disciplined Plan-Do-Check-Act cycles. Enforces **ATDD Gates** (Parity, JUnit, Audit, Docs), Circuit Breakers, and contextual budgeting for robust implementation. | [`pdca-ai-coding/SKILL.md`](pdca-ai-coding/SKILL.md) |
| **`jules-cli`** | **Worker Plane**<br/>*(Async Swarm)* | Dispatches independent research, code reviews, or bounded implementations to asynchronous worker agents (Jules) via batch processing and strictly enforced `Prompt Envelopes`. | [`jules-cli/SKILL.md`](jules-cli/SKILL.md) |

---

## 🧠 Core Philosophies & Mechanisms

### 1. Context Defense (Progressive Disclosure)
Instead of dumping infinite tokens into the context window, the system uses a **Scan-Before-Read** and **JIT (Just-In-Time) Identifier** protocol. The Control Plane maps the project statically (reading only headings and tables), expanding context dynamically only via `RefSpec` links (`path#anchor` or `path:Lx-Ly`) when triggered.

### 2. The Verification Gates (Zero-Debt Mandate)
`pdca-ai-coding` protects the mainline through explicit bash/python evaluation scripts:
- **Gate A (Parity)**: Verifies the Execution Plan matches the `TEST_PLAN`.
- **Gate B (Evidence)**: Forces dry-run JUnit/Pytest validation before claiming completion.
- **Gate C/D**: Audits plan tampering and enforces API documentation parity.

### 3. Unified Integration Contract
Inputs and outputs across the three planes are standardized. Every task completion (whether local or asynchronous) must yield a uniform **RefSpec Contract**:
- `Read List` (Context loaded)
- `Write List` (Files mutated)
- `Evidence Pointers` (Verification telemetry)
- `Plan Update Targets` (Upstream design adjustments)

---

## 🔄 Collaborative Architectures

The suite adapts to your project's scope, supporting three distinct topologies:

### Pattern 1: Greenfield / Standalone
**Use Case**: Small to medium feature development (1–3 hours).
**Mechanism**: Uses `pdca-ai-coding` in isolation. The system analyzes the codebase, proposes an approach, breaks it into strict RED/GREEN/REFACTOR TDD steps, and self-corrects using its built-in retrospective loop.

### Pattern 2: Top-Down Orchestration
**Use Case**: Epic-level delivery, cross-module refactoring.
**Mechanism**: `plan-doc-editor` acts as the Brain. It maps out the dependencies, dispatches blocking unknowns to `jules-cli` for investigation, and feeds static baseline requirements (B-files) sequentially to the local `pdca-ai-coding` agent to prevent context poisoning.

### Pattern 3: Asynchronous Swarm
**Use Case**: Massive code reviews, generalized mechanical refactoring, large-scale security audits.
**Mechanism**: The orchestrator splits work into non-overlapping tasks and uses `jules-cli`'s `dispatch_prompt_pack.py` to command multiple asynchronous cloud agents simultaneously, merging results securely via PRs gated by **Gate-J**.

*(See the [Integration Router Reference](plan-doc-editor/references/integration-router.md) for detailed I/O boundaries.)*

---

## 🚀 Installation & Usage

1. Clone or download this repository.
2. Select the skill(s) appropriate for your current workflow.
3. Move the respective folder (e.g., `pdca-ai-coding`) into your Agent's designated `.agent/skills/` or equivalent directory.
4. The AI will seamlessly read the `SKILL.md` frontmatter and self-activate when relevant verbs (e.g., "dispatch to Jules", "restructure plan") are detected.

---

## 📜 Attribution & License

- **PDCA TDD Core**: Forked and massively expanded from [MarcherGA/pdca-ai-coding-skill](https://github.com/MarcherGA/pdca-ai-coding-skill), which is based on [Ken Judy's InfoQ article on AI Code Generation](https://www.infoq.com/articles/PDCA-AI-code-generation/).
- **Context Engineering Concepts**: Multi-agent coordination and contextual degradation defenses were heavily inspired by [Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) by Murat Can Koylan.
- **Orchestration & Control Planes**: `plan-doc-editor`, `jules-cli`, ATDD Gating, and the unified routing contracts are original contributions to this repository.

Licensed under the [MIT License](LICENSE).
