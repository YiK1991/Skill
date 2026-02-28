# Planning Prompt - PDCA Plan Phase

Use this prompt after completing the analysis to create a detailed execution plan with TDD steps.

## When to Use

- After analysis is complete and approach is approved
- When you need to break down the work into testable increments
- Before starting any code implementation

## Planning Prompt

```
PLANNING PHASE - Execution Plan

Based on our analysis, provide a coherent plan incorporating our refinements that is optimized for YOUR use as context for the implementation.

This plan is FOR YOU (the AI agent) to follow during implementation. Make it detailed enough that you can execute it step-by-step while maintaining context and coherence.

EXECUTION CONTEXT:
- This plan will be implemented step-by-step following TDD discipline
- Each step must have clear stop/go criteria
- Implementation will occur in the same context thread
- Human will supervise and intervene as needed

PLAN REQUIREMENTS:

1. Break work into numbered, atomic steps
2. Each step must:
   - Be completable in <15 minutes
   - Have a specific failing test as the starting point
   - Include explicit acceptance criteria
   - Specify which files will be modified/created
   - Note estimated complexity (low/medium/high)

6. PD + JIT DELIVERABLES (add to the plan):
   - Execution Read List (RefSpec): the exact files/anchors to read during implementation (≤12 items)
   - Execution Write List (RefSpec): files that will be modified/created
   - Excludes: what NOT to read by default (large docs, history, etc.) unless triggered
   - Each step must reference at least one RefSpec (pattern, contract, or target file section)

7. DISCOVERY/READING DELIVERABLES (Static vs Dynamic):
   - Static Baseline (always keep small): list the 2-5 static pointers you will re-check (e.g., project config, test entrypoints)
   - Dynamic Read Targets (RefSpec): list the exact code/doc sections to open during implementation (≤12)
   - Trigger rules: specify what evidence forces loading additional dynamic context
   See: references/discovery-ladder.md

8. LOGGING / OFFLOADING PLAN:
   - Define where large outputs will be stored (plan-doc-editor `tool_outputs` vs `scratch/tool_outputs`)
   - Define naming convention (`TO-<id>-<seq>_<tool>_<slug>`)
   - Define what will be inlined vs referenced (summary/excerpt thresholds)
   See: references/tool-output-offloading.md

9. CONTEXT BUDGET DELIVERABLES:
   - Budget statement: static baseline vs dynamic reads vs tool/logs vs history vs buffer
   - Proxy limits: max dynamic deep-reads and max inline excerpts per step
   - Trigger rules: what signals require optimization before continuing
   - Optimization actions: masking/offloading/partitioning choices
   See: references/context-budget-policy.md

10. ANCHOR INITIALIZATION:
   - Provide initial Head Anchor (≤7 lines): goal/next/constraints/pointers
   - This will seed the session log anchors for stable execution
   See: references/edge-anchors.md

11. INITIAL RECITATION:
   - Provide the first ≤7-line recitation (Goal/Next/Constraints/Pointers) to seed the session Recitation Log
   See: references/recitation-protocol.md

12. INVESTIGATION OUTPUTS (if any):
   - Any INV/Q referenced by the plan must follow temporal validity + entity registry + consolidation rules
   - Plan steps must reference F/C by RefSpec (not copied prose)
   See: references/investigation-compatibility.md

13. PARALLEL WORK PLAN (only if triggered):
   - Define worker scopes (1–3 scopes max)
   - For each scope: goal, search terms, expected RefSpecs, and stop condition
   - Worker output must follow WORKER_REPORT schema (≤12 lines)
   See: references/multi-agent-protocol.md

3. TDD DISCIPLINE:
   - Each step MUST start with a failing test
   - Limit to 3 attempts before stopping to ask for help
   - Production code only after test is red (behaviorally failing)
   - No compilation errors as "red" - tests must compile but fail behaviorally

4. MODEL SELECTION (optional):
   - Tag each step with complexity: [SIMPLE/MODERATE/COMPLEX]
   - Simple steps may use lighter models
   - Complex steps requiring reasoning use more capable models
   - Human can adjust model selection during execution

5. PROCESS CHECKPOINTS:
   - After every 3 steps, pause for human review
   - Flag any deviations from established patterns
   - Highlight when manual testing or end-to-end verification is needed

FORMAT:

Step 1: [Test Description]
- Failing test: [specific test case and expected failure]
- Files to modify: [list specific files]
- Acceptance: [specific criteria - what makes this step complete]
- Estimated complexity: [low/medium/high]

Step 2: [Production Code]
- Make Step 1 test pass
- Implementation approach: [brief description]
- Files to modify: [list]
- Acceptance: All tests pass, no regressions
- Estimated complexity: [low/medium/high]

[Continue alternating test/code for all steps...]

CHECKPOINT SCHEDULE:
- Human review after steps: 3, 6, 9, etc.
- Final verification after all steps complete

BATCHING GUIDELINES:
- Related tests (same class/feature) can be batched
- Maximum 3 tests per batch before going green
- Each batch = one commit

RISK FLAGS:
- [List any potential issues, unknowns, or integration challenges]
- [Note any steps that might need extra attention]
- [Identify dependencies on external systems or APIs]
```

## Expected Output

The AI should provide:

1. **Numbered Steps** - Clear sequence of test → code pairs
2. **Specific Tests** - Exact test cases, not vague descriptions
3. **File Paths** - Which files will be touched in each step
4. **Acceptance Criteria** - Observable success conditions
5. **Checkpoints** - Clear review points every 3 steps
6. **Risk Flags** - Known challenges or unknowns

## Human Follow-Up Actions

After receiving the plan:

1. ✅ **Review step granularity** - Are steps small enough?
2. ✅ **Check test-first discipline** - Every odd step a test?
3. ✅ **Verify file organization** - Are we touching the right files?
4. ✅ **Assess risk flags** - Do we need to address any before starting?
5. ✅ **Approve plan** - Explicitly approve before implementation

## Red Flags to Watch For

- ⚠️ Steps that don't start with failing tests
- ⚠️ Steps that seem too large (>15 min)
- ⚠️ Vague acceptance criteria ("make it work")
- ⚠️ No checkpoints defined
- ⚠️ Missing risk assessment

If you see these, ask the AI to refine the plan.

## Example Usage

```
Human: Load references/planning-prompt.md and create the execution plan

AI: [Provides 12 numbered steps alternating between writing tests 
and implementing code, with checkpoints at steps 3, 6, 9, and 12]
```

---

## Optional Addendum: ATDD Gate Overlay (ai-driven-dev)

If the session enables the ATDD overlay, extend the plan with the following deliverables and checkpoints.

### A. Produce the acceptance plan (single source of truth)
- Create or update `TEST_PLAN.md` using **stable IDs**: `ATDD-001`, `ATDD-002`, ...
- Each item must be assertable: **Input → Expected output/state → Error code/status (if applicable)**.
- Items must be categorized (normal / error / authz) as applicable.

### B. Map PDCA steps to ATDD items
- Every implementation step MUST reference one or more `ATDD-xxx` items.
- The plan MUST include the exact test display-name convention: `ATDD-xxx <plan text>`.

### C. Gate checkpoints (explicit commands)
Insert checkpoints as plan steps (not optional):
1. Gate A parity: `python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd --parity-only`
2. Run acceptance tests producing JUnit: `$ATDD_TEST_CMD`
3. Gate B boolean verify (no writes): `python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd --junit "$ATDD_JUNIT_PATH" --strict --dry-run`
4. Gate D doc gate (when applicable): `python3 scripts/doc_gate.py --base origin/main --strict`

### D. Change Control plan
- Specify the conditions that trigger a **Change Declaration** and Gate C audit.
- For any “reframing / 换题”, require `CANCELLED(reason: ...)` or `REPLACED(by: ATDD-xxx)`; no silent deletion.

---

