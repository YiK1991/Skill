# Implementation Prompt - PDCA Do Phase

Use this prompt to execute the plan following strict TDD discipline.

## When to Use

- After the plan is approved and ready to implement
- At the start of the Do phase of PDCA cycle

## Implementation Prompt

```
IMPLEMENTATION PHASE - Test-Driven Development

PRE-FLIGHT (plan-doc-editor environment):

Detection: if ancestor directories contain CURRENT.md AND
investigation/ AND questions/ directories → treat as plan module.

If plan module detected, check BEFORE any code generation:
1. CURRENT.md Head/Tail Anchor: PlanApproved == YES
2. G-READY == pass (tracker exists, B-files have Objective/Steps/DoD)

If EITHER fails → STOP (no production code, no TDD):
→ Only output Plan Update Targets to fill execution/_tracker.md
  or create execution/B*_*.md stubs (skeleton only).
→ Keep PlanApproved: NO.
→ Create questions/Q-NNN_exec_ready_* to record the gap.

Execute the plan we created, following TDD discipline strictly.

TDD RULES:

❌ DON'T:
- Test interfaces - test concrete implementations
- Use compilation errors as RED phase - use behavioral failures
- Skip writing tests first
- Make multiple unrelated changes in one commit
- Use mocks when real components are available
- Fix multiple failing tests simultaneously

✅ DO:
- Create stub implementations that compile but fail behaviorally
- Use real components over mocks when possible
- Write the minimum code to make the test pass
- Commit after each green test (or small batch of related tests)
- Refactor after green, before moving to next test
- Capture full test output to a log file. Inline only a short summary (≤10 lines) and key excerpt (≤60 lines), plus RefSpec pointer to the full log.

EDGE ANCHOR CHECKPOINT (every step):
- Before executing: read the session Head Anchor (≤7 lines).
- After executing: update Head Anchor if goal/next/constraints changed.
- Always mirror Head Anchor into Tail Anchor at end of step (keep ≤7 lines).
See: references/edge-anchors.md

RECITATION CHECKPOINT (every step):
- Before executing: write a ≤7-line "Recite: Step N (Before)" using the recitation source.
- After executing (and after tests): write "Recite: Step N (After)" and update session Head/Tail anchors.
- If recitation reveals drift (goal/constraints mismatch): STOP → update plan artifacts/anchors → proceed.
See: references/recitation-protocol.md

USING INVESTIGATION EVIDENCE:
- When referencing F/C from investigations, prefer items with status=active and most recent valid_from.
- If conflicts exist, record the choice (or create a resolution entry) before proceeding.
- Reference entities via ENT-xxx; do not restate properties in-line.
See: references/investigation-compatibility.md

COMPACTION CHECKPOINT:
- Monitor proxy triggers (steps/deep-reads/offloads/budget hits).
- If triggered:
  1) Summarize ONLY the newly-truncated span into the Session Compaction Block sections.
  2) Merge into existing bullets (incremental), DO NOT regenerate the whole block.
  3) Preserve continuity: keep the last 2–3 steps uncompressed.
- Ensure "Files touched" and "Evidence pointers" are updated (artifact trail).
See: references/context-compression.md

PROCESS FOR EACH STEP:

1. CONCISE RATIONALE (1–3 bullets, not long prose)
   - What you're about to do + plan step number
   - Which failing test you'll write and why
   - Deposit detailed reasoning into Session Compaction Block if needed

2. RED: Write the failing test
   - Test must compile
   - Test must fail for behavioral reasons (not syntax/compilation)
   - Show me the test code
   - Run the test and show me the failure output
   - Explain what the failure means

3. GREEN: Write minimal production code
   - Only enough code to make the test pass
   - No premature optimization
   - No "while we're here" additions
   - Show me the production code
   - Run all tests and show me they pass
   - Verify no regressions in other tests

4. REFACTOR (if needed)
   - Improve code quality while keeping tests green
   - Remove duplication
   - Improve naming and structure
   - Run tests again to confirm still green
   - Only refactor if there's clear value

5. COMMIT CHECKPOINT
   - Summarize what was accomplished
   - List files changed
   - Wait for human review before proceeding
   - Flag any deviations from plan

DECISION TRACING (immediate, not deferred):
- Every key decision (choosing approach / modifying interface / skipping test) must be recorded IMMEDIATELY:
  - Decision + reason (1–2 lines)
  - Evidence RefSpec (pointer to supporting file/test/log)
  - Record in: Session Compaction Block → `Decisions` section
- Do NOT defer evidence to completion; it will be lost during compression.
See: references/output-contract.md

BATCHING RULES:
- Related tests (same class/feature) can be batched
- Maximum 3 tests per batch before going green
- All tests in batch must pass before moving forward
- Each batch = one coherent commit
- Document the batch scope upfront

TOOL VERBOSITY (format=concise|detailed):
- Default: concise for all tool calls (tests, commands, patching).
- Use detailed only when:
  - a failure is non-obvious and needs full context OR
  - evidence must be preserved for a gate/decision.
- Even in detailed mode, prefer pointers/offloading over inline dumps.
See: references/tool-spec.md

PD + JIT WRITE PROTOCOL:
- Show changes as patch-style snippets with file path + line range (RefSpec).
- Do NOT dump entire files; inline excerpts ≤60 lines.
- When you reference existing code/patterns, cite RefSpec and only the relevant excerpt.

TRANSPARENCY REQUIREMENTS:
- State concise rationale (1–3 bullets) BEFORE each step; deposit detail into Session Compaction Block
- Explain any deviations from the plan
- Ask questions when context is unclear or assumptions needed
- Stop after 3 failed attempts and ask for help
- Surface any integration issues immediately

EVIDENCE STORAGE:
- Full stdout/stderr and large tool outputs must be written to files.
- Provide RefSpec pointers + minimal excerpts only.
- Use targeted retrieval to reference specific failures.
See: references/tool-output-offloading.md

ARCHITECTURAL CONSISTENCY:
- Follow the patterns identified in analysis
- Use existing abstractions before creating new ones
- Match naming conventions from codebase
- Respect layer boundaries and separation of concerns
- If pattern doesn't fit, stop and discuss with human

ERROR HANDLING:
- If a test fails unexpectedly, stop and analyze why
- If multiple tests fail, fix them one at a time
- If you're unsure about an approach, ask before implementing
- If regression tests fail, stop immediately and investigate

WORKER ESCALATION (context isolation):
- If debugging requires parallel investigation, spawn workers by independent scopes.
- Workers must output WORKER_REPORT (≤12 lines) + RefSpecs + confidence only.
- Supervisor merges results by updating:
  - Session Compaction Block (Decisions/Next steps/Evidence pointers)
  - Partitions Index (if new evidence files were created)
See: references/multi-agent-protocol.md

DISCOVERY ON BLOCKER (Static→Dynamic):
- If context is missing or a failure is unclear: run the Discovery Ladder (ls/glob → rg/grep → header scan → targeted read).
- Do not open many files "just in case". Prefer targeted reads.
- Record every deep read as RefSpec in the step notes/session log.
See: references/discovery-ladder.md

BUDGET CHECKPOINT (every step):
- Count dynamic deep-reads and inline excerpts used in this step.
- If proxy limits are exceeded: STOP → optimize:
  - offload bulk outputs
  - replace content with RefSpec pointers
  - update session anchors (≤7 lines)
Then continue.
See: references/context-budget-policy.md

OPTIMIZATION ACTION SELECTION (on budget hit):
- Prefer Observation masking first (replace verbose blobs with RefSpec).
- If multiple evidence threads grow, Partition into dedicated files and keep only index pointers in session.
- If still over, run anchored compaction (incremental merge).
See: references/context-budget-policy.md

RUBRIC SELF-CHECK (quick):
- Confirm RefSpecs exist for key claims/decisions.
- Confirm tool outputs were offloaded/masked (no large dumps).
- Confirm budget triggers were handled with correct actions.
See: references/eval-rubric.md

Proceed with Step 1 of the plan. State concise rationale (1–3 bullets) first.
```

## Expected Behavior

The AI should:

1. **Explain before acting** - Clear reasoning for each step
2. **Show all output** - Test failures and passes
3. **Follow red-green-refactor** - Strict TDD discipline
4. **Commit frequently** - After each successful step/batch
5. **Ask when uncertain** - Don't make blind assumptions
6. **Stop on failures** - Investigate, don't push through

## Human Actions During Implementation

**Monitor for:**
- Reasoning errors (catch early!)
- Context drift (AI going off-pattern)
- Skipped tests
- Too much code at once
- Assumptions without verification

**Intervene when:**
- AI skips tests: "Stop. Write the failing test first."
- Changes too big: "This is too much at once. Break it down."
- Context drifts: "Return to step X. Follow the [pattern] we identified."
- Wrong assumptions: "That's not correct. The actual pattern is [X]."
- Stuck in a loop: "Let's stop and replan from where we are."

## Red Flags to Watch For

- ⚠️ No test failures shown
- ⚠️ Implementing without tests
- ⚠️ Making unrelated changes
- ⚠️ Creating new patterns instead of using existing
- ⚠️ Large commits (>100 lines)
- ⚠️ Touching many files at once

## Example Interaction

```
Human: Load references/implementation-prompt.md and execute the plan

AI: Starting with Step 1: Create failing test for JWT token generation

REASONING: We need to verify that JWTService can generate a valid token
with user claims. This test will fail because JWTService doesn't exist yet.

RED PHASE:
[Shows test code]
[Runs test, shows failure: "JWTService not defined"]

Wait - this is a compilation error, not a behavioral failure. Let me create
the stub first.

[Creates JWTService stub with generate_token() returning None]
[Runs test again]
[Shows failure: "Expected token string, got None"]

Now we have a proper behavioral failure.

GREEN PHASE:
[Implements minimal JWT generation]
[Runs all tests]
[Shows all tests pass]

Ready to commit. Files changed: JWTService.py, test_jwt_service.py
Proceeding to Step 2? [Waits for human approval]
```

---

## Optional Addendum: ATDD Gate Overlay (ai-driven-dev)

If the session enables the ATDD overlay, apply the following **in addition** to the PDCA implementation prompt.

### 1) Architecture Lock before changes
Before each change batch, produce an **Architecture Lock** (copy the template if needed):
- Scope, touched files, intended layer per file
- Allowed changes (default ≤3 files; if a B file exists, scope MUST match or encompass the B file's file list)
- Each red line must reference a Contract Summary item by number/title

### 2) Do not implement until the gates are satisfied
- If `TEST_PLAN.md` or `tests/atdd/` are missing: create them first.
- Before writing production code, ensure Gate A parity is satisfied (plan ↔ tests naming):
  - `python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd --parity-only`
- Enforce strict TDD per item:
  - RED test must fail for the right reason (not syntax/import)
  - GREEN minimal implementation only for the failing test
  - Refactor only while fully green
  - **Stale result cleanup:** Before running tests, always delete stale JUnit files: `rm -f "$ATDD_JUNIT_PATH"` (or equivalent on Windows). Then run `$ATDD_TEST_CMD` to regenerate fresh results.
  - **Tick side-effect:** If you run `--tick` (non-dry-run), it modifies `TEST_PLAN.md`. Always `git add TEST_PLAN.md` and include it in the commit. Run `git status --porcelain` before committing to detect gate side-effects.

### 3) Self-repair loop (≤3 rounds) with stop conditions
When tests fail:
- Output `Round N/3` log with failing cases, root cause, file changes, rerun result.
- If **two rounds** show no progress due to wrong approach/assumption: stop and trigger Change Control.
- If N reaches 3: stop and request human decision.

### 4) Change Control (reframing / 换题)
If you discover the plan is wrong or requirements shifted:
- Do NOT restart silently.
- Issue a Change Declaration and update `TEST_PLAN.md` only via:
  - `[-] ... CANCELLED(reason: ...)` or
  - `[>] ... REPLACED(by: ATDD-xxx)`
- Then run Gate C audit and Gate A parity again.

### 5) Evidence capture for later debugging
When a gate fails, preserve the evidence in the output:
- Gate name (A/B/C/D)
- The exact command run
- The key failing items
- The file/line pointers reported by the gate (do not paraphrase them away)
