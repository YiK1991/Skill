---
name: pdca-ai-coding
description: Structured Plan-Do-Check-Act, PDCA, framework for AI code generation. Use when implementing features, adding functionality, refactoring code, or any coding task that benefits from test-driven development, quality assurance, and continuous improvement. Prevents code quality issues, reduces debugging time, and maintains architectural consistency through structured prompts and human-AI collaboration.
---
# PDCA AI Coding Framework

Structured workflow for high-quality AI-assisted code generation using Plan-Do-Check-Act principles.

## When to Use This Skill

Use this skill for:

- Implementing new features (1-3 hour tasks)
- Refactoring existing code
- Adding integrations or cross-system functionality
- Any coding task requiring test-driven development
- Tasks where code quality and maintainability matter

**Do NOT use for:**

- Trivial changes that don't need testing
- Exploratory coding or prototyping
- Simple, well-patterned tasks → use **Lite Mode** below

## Lite Mode (Fast-track)

For small, well-understood changes that don't justify the full PDCA cycle.

**Eligibility (ALL must be true):**

1. Single-file change (or ≤2 tightly-coupled files)
2. Total diff < 50 lines
3. No cross-layer / cross-module dependencies
4. Existing test pattern can be reused (copy-adapt, not invent)
5. No architectural, public-interface, or functional behavior change
   (cosmetic/textual/logging changes are OK)

**Lite Mode flow:**

1. Write TDD steps directly (skip Analysis/Planning prompts)
2. Implement: RED → GREEN → Refactor
3. Run existing test suite to verify no regressions
4. Commit

**Escalation triggers (→ switch to Full Mode immediately):**

- Any eligibility condition becomes false mid-work
- You discover unexpected coupling or missing context
- Test failures reveal deeper issues
- Changes grow beyond 50 lines

## Quick Start

For a standard coding session:

0. **Decide Mode** — Evaluate task complexity:
   - ALL Lite eligibility met? → **Lite** (skip to step 4 TDD only)
   - Existing pattern, simple task with behavior change? → **Lightweight** (simplified analysis, skip detailed planning)
   - Production fire? → **Emergency** (skip analysis, reproduce-bug test → fix → verify)
   - Everything else → **Full** (all steps below)
1. **Review Working Agreements** - Load references/working-agreements.md (1 min read)
2. **Run Analysis**: "Load references/analysis-prompt.md and analyze [your objective]"
3. **Run Planning**: "Load references/planning-prompt.md and create the plan"
4. **Run Implementation**: "Load references/implementation-prompt.md and proceed with the plan"
5. **Run Completion Check**: "Load references/completion-prompt.md and verify our work"
6. **Run Retrospective**: "Load references/retrospective-prompt.md to learn from this session"

## Working Agreements (Summary)

**Full agreements in references/working-agreements.md - read before each session!**

**Note:** This skill works globally across all your projects. Project context is discovered automatically via Repo Contract Priority (see `references/repo-contract-priority.md`): `gemini.md`/`agent.md`/`rules.md` first, then architecture docs, then `.claude/instructions.md` as optional override.

**Core Principles:**

- ✅ **Test-Driven Development**: Failing tests first, then production code
- ✅ **Incremental Change**: Small commits (<100 lines, <5 files)
- ✅ **Respect Architecture**: Follow existing patterns
- ✅ **Human Accountability**: You own all AI-generated code

**Key Intervention Questions:**

- "Where's the failing test first?"
- "Are we fixing multiple things at once?"
- "Does this follow our patterns?"
- "Is this commit reviewable?"

See references/working-agreements.md for complete details.

## ai-driven-dev (ATDD Gate Overlay)

Enable this overlay **by default for most coding work** (features, refactors, non-trivial bugfixes). It turns acceptance criteria into a **durable regression/QA mechanism** via an evidence chain: `TEST_PLAN.md` (ATDD-xxx) → same-name tests → JUnit → boolean gates.

Skip only when explicitly declared: `ATDD_OVERLAY=off (reason: prototype/trivial/no-behavior-change)`.

**Chain:** Plan → Same-name tests → Gate A → Strict TDD → ≤3 self-repair → Gate B (JUnit) → Architecture lock → Gate D (Docs)

**Gates (stdout `true/false`, stderr diagnostics):**

- Gate A: `scripts/atdd_gate.py --parity-only` (plan ↔ tests parity)
- Gate B: `scripts/atdd_gate.py --junit ... --strict --dry-run` (JUnit evidence; no workspace writes in dry-run mode)
  - **Side-effects note**: Gate scripts are default side-effect-free, with these exceptions: `test-results/` (JUnit output dir), `.pdca/` (circuit breaker state when `PDCA_GATE_MAX_RETRIES>0`). Both are `.gitignore`d.
- Gate C: `scripts/atdd_gate.py --audit` (plan change audit: no silent delete / swap)
- Gate D: `scripts/doc_gate.py` (doc obligations for behavior / cross-layer / API changes)

### How it fits the PDCA phases

- **Plan (Analysis/Planning):** extract Repo Contract, draft `TEST_PLAN.md`, ensure every plan item is testable/observable.
- **Do (Implementation):** strict TDD per acceptance item; enforce file/architecture boundaries via Architecture Lock.
- **Check (Verification):** run Gate A → tests → Gate B → Gate D; results are evidence.
- **Act (Adjust):** if assumptions change, use Change Control (CANCELLED/REPLACED) and re-run Gate C/A.

### References

- Start here: `references/atdd/INDEX.md`
- Templates: `assets/TEST_PLAN_TEMPLATE.md`, `assets/ARCHITECTURE_LOCK_TEMPLATE.md`, `assets/ADR_LITE_TEMPLATE.md`
- Optional hook (no workspace writes): `assets/pre-push-hook-atdd.sh`

## Context Loading Protocol (PD + JIT)

PDCA uses progressive disclosure and just-in-time identifiers by default:

- Read summary/index first; deep-read only when triggered.
- Use RefSpec pointers (`path#anchor` or `path:Lx-Ly`) instead of copying content.
  - **Prefer stable anchors** (`path#heading` for markdown; `path#ClassName.method` for code) over line ranges, because line numbers drift during editing.
- Keep inline excerpts small (≤60 lines); otherwise reference via RefSpec.
- Show changes as patch-style snippets, not full-file dumps.

See: [context-loading-protocol.md](references/context-loading-protocol.md)

## Tool Output Offloading (Short-term Memory)

Large tool outputs must be offloaded to files (do not paste dumps into chat/session):

- Store full output to filesystem, return only a short summary + RefSpec pointer.
- Prefer targeted retrieval (grep + line ranges) when reusing evidence.

See: [tool-output-offloading.md](references/tool-output-offloading.md)

## Context Budget Allocation (Triggers)

PDCA follows an explicit context budget with trigger-based optimization:

- Maintain small static baseline; load dynamic context only when triggered.
- Reserve buffer; never fully spend context on pre-loading.
- If budget is exceeded, stop and optimize (mask/point/offload) before proceeding.

See: [context-budget-policy.md](references/context-budget-policy.md)

## Edge Anchors (Lost-in-the-middle)

To reduce drift and mid-context loss:

- Maintain short Head/Tail anchors (≤7 lines) in the session log.
- Critical goal/next/constraints must appear at the edges, not buried mid-session.

See: [edge-anchors.md](references/edge-anchors.md)

## Plan Persistence / Recitation

For long tasks, persist the plan in files and re-orient via short recitation:

- Use ≤7-line recitations before/after each step.
- If recitation conflicts with current work, stop and fix drift first.

See: [recitation-protocol.md](references/recitation-protocol.md)

## Investigation Compatibility (Memory Systems)

When PDCA produces investigation artifacts (INV/Q/notes), it must follow:

- Temporal validity fields (`valid_from`/`valid_until`/`status`/`superseded_by`)
- Entity identifiers (`ENT-xxx`) + registry
- Consolidation: invalidate but don't discard (keep history)

See: [investigation-compatibility.md](references/investigation-compatibility.md)

## Context Compression (Anchored + Incremental)

For long sessions, compress using anchored summaries and incremental merging:

- Optimize tokens-per-task (avoid re-fetch costs).
- Trigger at ~70–80% utilization (or proxy triggers) and merge incrementally.
- Track artifact trail (files/decisions) explicitly.

See: [context-compression.md](references/context-compression.md)

## Tool Design (Consolidation + Verbosity)

To reduce tool overhead and ambiguity:

- Prefer a small consolidated tool set; avoid overlapping tools.
- Any tool output must support format=concise|detailed (default: concise).
- Prefer filesystem primitives (ls/rg/open) before adding specialized tools.

See: [tool-catalog.md](references/tool-catalog.md) and [tool-spec.md](references/tool-spec.md)

## Multi-agent (Context Isolation)

Workers are used only for high-parallel-value scenarios (wide search / multi-hypothesis / multi-module triage).
Worker outputs must be short (≤12 lines) + RefSpecs + confidence; bulk evidence must be offloaded.

See: [multi-agent-protocol.md](references/multi-agent-protocol.md)

## Evaluation Gate

Prompt/rule changes must be validated on a small regression suite under budget constraints.
Use the multi-dimensional rubric (correctness, traceability, tool efficiency, budget compliance).

See: [eval-rubric.md](references/eval-rubric.md) and [eval-regression-suite.md](references/eval-regression-suite.md)

## Context Engineering (All Protocols Index)

All context-engineering protocols are cataloged in a single index for discoverability.

See: [context-engineering/INDEX.md](references/context-engineering/INDEX.md)

## Adaptive Execution (Env-Aware)

PDCA is an agile implementer that adapts to the project's existing infrastructure:

1. **With Infrastructure (plan-doc-editor is present)**

   - If you detect `_tracker.md` or planned `B file`s in the workspace:
     - **Static baseline (always)**: `_tracker.md` active rows + the selected B file header/Before-You-Start (no deep reads yet).
     - **Dynamic discovery**: when missing context, run Discovery Ladder ([discovery-ladder.md](references/discovery-ladder.md)) and only open targeted sections.
     - **Record**: every deep read must be captured as RefSpec in session log (read list).
     - **Discovery (Hitting a blocker)**: Do not force a fix for major architectural gaps. **STOP execution**, create a `Q-NNN` file in the `questions/` directory outlining the traceback/issue, and mark the Tracker as blocked.
     - **Post-work**: Upon successful TDD completion, update `_tracker.md` status to DONE (if no `update_tracker.py` script exists in the project, edit the tracker table directly with care).
   - **Gate-J (Jules Review)**: If B file frontmatter contains `gate_j: required`, do NOT mark as DONE until Jules review PR is merged. Trigger Jules review pack via `/jules` workflow, wait for result in `investigation/INV-*_jules_review.md` (must contain unified output fields: Read/Write/Evidence/Plan Update Targets per integration-router.md), then proceed to DONE.
     - **Recitation source**: when plan-doc-editor is present, recitation prioritizes CURRENT Head/Tail + tracker active rows; otherwise use session anchors.
2. **Without Infrastructure (Greenfield / Zero-start)**

   - Follow the standard PDCA workflow (Analysis -> Planning -> Implementation).
   - Run the **full Discovery Ladder** during Analysis to build initial context.
   - Only create `execution/`, `_tracker.md`, `questions/` if plan-doc-editor is detected **or** the user explicitly opts into plan-doc-editor layout. Otherwise, keep artifacts under `scratch/`.

## PDCA Workflow

### 1. Plan Phase - Analysis (2-10 min)

**Load the analysis prompt:**
\`\`\`
Load references/analysis-prompt.md and analyze: [your business objective]
\`\`\`

The AI will:

- Check for .claude/instructions.md (project configuration)
- Search codebase for existing similar patterns
- Document architectural context and abstractions
- Propose 2-3 alternative approaches with pros/cons
- Recommend the best approach

**Your actions:**

- Provide project context if requested (no .claude/instructions.md found)
- Review the analysis thoroughly
- Ask clarifying questions
- Provide additional context
- Approve the recommended approach
- Save analysis to project tracking (Jira, Linear, etc.)

### 2. Plan Phase - Task Breakdown (2 min)

**Load the planning prompt:**
\`\`\`
Load references/planning-prompt.md and create the execution plan
\`\`\`

The AI will:

- Break work into numbered, atomic TDD steps
- Define clear acceptance criteria for each step
- Set checkpoints every 3 steps for human review
- Flag risks and integration points

**Your actions:**

- Review the plan
- Adjust step order if needed
- Identify high-risk steps needing more attention
- Proceed to implementation

### 3. Do Phase - Implementation (variable, <3 hours)

**Load the implementation prompt:**
\`\`\`
Load references/implementation-prompt.md and execute the plan
\`\`\`

The AI will:

- Show reasoning before each step
- Write failing tests first (RED phase)
- Implement minimal production code (GREEN phase)
- Refactor while keeping tests green
- Commit after each successful batch

**Your actions:**

- Monitor AI reasoning for errors
- Intervene when context drifts
- Provide missing context when stuck
- Redirect if going off-plan
- Stop and replan if assumptions prove wrong
- Commit code after each step/batch

**Key intervention points:**

- When AI skips tests: "Stop. Write the failing test first."
- When changes too big: "This is too much. Break it into smaller steps."
- When context drifts: "Return to step X of the plan."
- When off-pattern: "This doesn't follow the [X] pattern we identified."

### 4. Check Phase - Completion Analysis (5 min)

**Load the completion check prompt:**
\`\`\`
Load references/completion-prompt.md and verify our work
\`\`\`

The AI will:

- Verify all tests pass and manual testing is complete
- Check code quality and test coverage
- Audit process adherence (TDD discipline maintained)
- Review architectural consistency
- Summarize accomplishments and deviations

**Your actions:**

- Review the completion analysis
- Spot-check code to verify claims
- Correct any inaccuracies
- Add completion analysis to project tracking
- Perform your own code review

### 5. Act Phase - Retrospective (2-10 min)

**Load the retrospective prompt:**
\`\`\`
Load references/retrospective-prompt.md and analyze our session
\`\`\`

The AI will:

- Summarize what was accomplished
- Identify critical moments that impacted success
- Flag wasted effort and wrong paths
- Highlight what worked well
- Suggest specific improvements for next time

**Your actions:**

- Read and reflect on findings
- Identify the ONE most valuable improvement
- Update prompt templates if needed
- Document patterns for future reference
- Note learnings in your personal knowledge base

## Complexity Modes

| Mode                  | When                                                                         | Skip                                          | Keep                                                          |
| --------------------- | ---------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------- |
| **Lite**        | Single-file, <50 lines, no behavior/interface change, reuse existing pattern | Analysis, Planning, Completion, Retrospective | TDD, Commit                                                   |
| **Lightweight** | Small task with behavior change, clear existing patterns                     | Detailed analysis                             | TDD, Planning (simplified), Retrospective                     |
| **Full**        | Cross-system, architectural, novel domain, >50 lines                         | —                                            | All 5 phases                                                  |
| **Emergency**   | Production down, requires immediate fix                                      | Analysis                                      | Reproduce-bug test → minimal fix → verify → root-cause doc |

**Mode selection rule:**

1. ALL Lite Mode eligibility met (see above)? → **Lite**
2. Existing pattern, simple task? → **Lightweight**
3. Production fire? → **Emergency**
4. Everything else → **Full**

## Tracking Metrics

Use the metrics tracking script to measure quality:

\`\`\`bash
python scripts/track_metrics.py --repo /path/to/repo --since "7 days ago"
\`\`\`

Monitors:

1. Large commit % (>100 lines) - target: <20%
2. Sprawling commit % (>5 files) - target: <10%
3. Test-first discipline % - target: >50%
4. Avg files per commit - target: <5
5. Avg lines per commit - target: <100

## Session Logging

Track your sessions for continuous improvement:

\`\`\`bash
python scripts/init_session.py "Feature name" --objective "Business objective"
\`\`\`

This creates a session log in \`assets/session-template.md\` format to track:

- Analysis and plan decisions
- Implementation notes and interventions
- Completion verification results
- Retrospective learnings and improvements

## Tips for Success

### Context Management

- Keep sessions focused (1-3 hours)
- If context drifts, save and start new session
- Reference earlier analysis/plan to maintain coherence

### Effective Intervention

- Interrupt early when seeing reasoning errors
- Provide missing context proactively
- Ask clarifying questions for wrong assumptions

### Common Pitfalls to Avoid

- **Skipping analysis** → leads to code duplication and pattern violations
- **Skipping tests** → leads to regressions and debugging loops
- **Large batches** → harder to review, more likely to have issues
- **No retrospective** → miss improvement opportunities

### When to Replan

Stop and create a new plan if:

- Regression tests fail unexpectedly
- You discover missing context or wrong assumptions
- The approach proves more complex than anticipated
- Context drifts (off-pattern solutions emerge)

## Reference Files

All prompts and guidelines are in the \`references/\` directory:

- \`working-agreements.md\` - Core principles and intervention questions (read first!)
- \`analysis-prompt.md\` - Detailed codebase analysis and approach selection
- \`planning-prompt.md\` - Task breakdown into TDD steps
- \`implementation-prompt.md\` - TDD execution guidelines
- \`completion-prompt.md\` - Quality verification checklist
- \`retrospective-prompt.md\` - Session learning and improvement

Load these files as needed during each phase of the PDCA cycle.
