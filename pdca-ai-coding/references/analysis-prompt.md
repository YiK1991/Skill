# Analysis Prompt - PDCA Plan Phase

Use this prompt at the start of each coding session to analyze the business problem and identify the best technical approach.

## When to Use

- At the beginning of every feature implementation
- When refactoring or adding cross-system functionality
- Before making significant architectural changes
- Any time you need to understand existing patterns before coding

## Analysis Prompt

```
ANALYSIS PHASE - Business Problem and Technical Approach

STEP 0: PROJECT CONTEXT VERIFICATION (30 seconds)
────────────────────────────────────────────────────

Before analysis, verify project-specific context:

🔍 CHECKING FOR PROJECT CONFIGURATION:
   - Look for .claude/instructions.md in project root
   - Check if project has specific tech stack or conventions documented

📋 IF .claude/instructions.md EXISTS:
   ✅ Read and acknowledge the project guidelines
   ✅ Follow the tech stack specified (framework, language, patterns)
   ✅ Respect any architectural constraints or conventions
   ✅ Note any team-specific practices
   
❓ IF NO .claude/instructions.md FOUND:
   Ask the human for essential project context:
   
   "I don't see a .claude/instructions.md file with project guidelines.
   
   Before we proceed, please tell me:
   • What's your tech stack? (e.g., Next.js 14, TypeScript, Prisma)
   • Any architectural patterns to follow? (e.g., Clean Architecture, MVC)
   • Any conventions or constraints? (e.g., use functional components only)
   
   Or just say 'proceed' and I'll use best practices for your objective."

💡 NOTE: This quick context check prevents hours of rework later!

────────────────────────────────────────────────────

STEP 1: BUSINESS OBJECTIVE

Business Objective:
[The human will fill this in - what are they trying to achieve and why?]

STEP 2: EXISTING PATTERNS SEARCH
   - Identify 2-3 existing implementations that follow similar patterns
   - Search the codebase for comparable functionality
   - Document which files/classes implement related features
   - Show relevant code examples from the codebase

   PD + JIT RULES FOR STEP 2:
   - Two-pass: (1) list candidate files (RefSpec) → (2) open only the smallest relevant sections.
   - For each pattern you cite: provide RefSpec + a small excerpt (≤60 lines). Do NOT paste full files.
   - Produce a "Read List (RefSpec)" that implementation can follow without re-searching.

   DISCOVERY LADDER (Static→Dynamic):
   - Start with Static Baseline Scan (project config/docs/test entrypoints).
   - Produce a Candidate List (file paths) via rg/grep before opening files.
   - Do Header Scan first; deep-read only the minimal relevant sections.
   - Output must include: (a) Static baseline findings, (b) Candidate List, (c) Deep-read RefSpecs.
   See: references/discovery-ladder.md

   TOOL DESIGN RULES:
   - Use filesystem primitives first (ls/glob → rg/grep → targeted read).
   - Avoid introducing specialized tools for search/inspection unless primitives fail.
   - If a tool is used, default to format=concise; only use detailed with explicit justification.
   See: references/tool-catalog.md and references/tool-spec.md

   TOOL OUTPUT OFFLOADING:
   - If grep/rg output is large, offload it to a file and reference via RefSpec.
   - Inline excerpts must be small; keep the session context clean.
   See: references/tool-output-offloading.md

   MASKING RULE:
   - If a search output/log has been offloaded once, do not paste it again.
   - Always cite the RefSpec pointer + small excerpt instead (observation masking).
   See: references/context-budget-policy.md

   INVESTIGATION TRIGGER:
   If root cause is ambiguous or evidence conflicts:
   - Create/update an investigation note (INV-001) following the compatibility schema.
   - Record F-*/C-* with temporal validity fields + entity IDs (ENT-xxx) + evidence RefSpecs.
   - Do not "decide silently"; surface conflicts explicitly.
   See: references/investigation-compatibility.md

   MULTI-AGENT TRIGGER:
   If wide search, multi-hypothesis, or multi-module triage is required:
   - Spawn workers with isolated scopes (one worker per scope).
   - Each worker must return a WORKER_REPORT (≤12 lines) + RefSpecs + confidence.
   - Any bulk evidence must be offloaded to files; do not paste long logs back.
   See: references/multi-agent-protocol.md

STEP 3: ARCHITECTURAL CONTEXT
   - Document the established architectural layers (which namespaces, which interfaces)
   - Identify the abstractions already available (base classes, interfaces, utilities)
   - Map integration touch points (which existing methods will need modification)
   - Note the dependency injection patterns used
   - Identify where similar features are configured

STEP 4: CONFIGURATION & SETUP
   - Identify where similar features are configured
   - Document configuration file patterns used in the project
   - Note any environment-specific considerations
   - Check for feature flags or settings that may be relevant

STEP 5: ALTERNATIVE APPROACHES
   - If a plan-doc-editor B file is provided, SKIP this step entirely.
     Treat the B file as architectural truth. Focus on verifying alignment
     and surfacing blockers as Q-NNN.
   - Otherwise, propose 2-3 different technical approaches to solve this problem
   - For each approach, provide:
     * Pros and cons
     * Integration complexity (low/medium/high)
     * Amount of existing code to modify vs create new
     * Risk factors
     * Estimated implementation time
     * Impact on existing architecture

STEP 6: RECOMMENDED APPROACH
   - Which approach do you recommend and why?
   - What are the key architectural decisions?
   - What existing patterns should we follow?
   - What abstractions should we reuse vs create?
   - What are the main integration points?

CONSTRAINTS:
- Focus on "what" and "why", not implementation details
- Search the codebase BEFORE suggesting new code patterns
- Keep analysis human-readable and under 500 words
- Identify code reuse opportunities - avoid duplication
- Be specific with file paths and class names
- Cite specific code examples when describing patterns
- Use RefSpec pointers for all cited evidence (path#anchor or path:Lx-Ly)
- Keep inline excerpts small (≤60 lines); prefer pointers over copying
- Maintain a small static baseline; do not deep-read many files
- Dynamic deep-reads must be recorded as RefSpec; keep count per step
- If candidate list is large, stop and narrow via search; do not open everything
- Follow proxy limits from references/context-budget-policy.md

OUTPUT FORMAT:
Provide a clear, structured analysis that addresses all deliverables above.
Use markdown formatting for readability.
This analysis will be added to project tracking (Jira/Linear), so make it clear and professional.
Include a "Read List (RefSpec)" section: list all files/sections deep-read during analysis as path#anchor or path:Lx-Ly.
```

## Expected Output

The AI should provide:

1. **Project Context** - Acknowledgment of .claude/instructions.md or request for context
2. **Existing Patterns** - 2-3 concrete examples with file paths
3. **Architecture** - Clear description of layers, abstractions, DI patterns
4. **Configuration** - Where and how this feature should be configured
5. **Alternatives** - 2-3 approaches with detailed pros/cons
6. **Recommendation** - Clear recommendation with justification

## Human Follow-Up Actions

After receiving the analysis:

1. ✅ **Provide project context** - If requested and no .claude/instructions.md exists
2. ✅ **Review thoroughly** - Check that patterns cited actually exist
3. ✅ **Ask clarifying questions** - If anything is unclear or missing
4. ✅ **Provide additional context** - Share domain knowledge the AI lacks
5. ✅ **Approve approach** - Explicitly approve before moving to planning
6. ✅ **Save to project tracker** - Document in Jira/Linear for transparency

## Red Flags to Watch For

- ⚠️ No existing patterns cited (may duplicate code)
- ⚠️ Vague architectural descriptions
- ⚠️ Only one approach proposed
- ⚠️ No consideration of integration points
- ⚠️ Recommendation lacks clear justification
- ⚠️ Skipped project context verification

If you see these, ask the AI to dig deeper before proceeding.

## Example Usage

```
Human: Load references/analysis-prompt.md and analyze: 
Add user authentication with JWT tokens to our REST API

AI: [Checks for .claude/instructions.md, finds Next.js + TypeScript project config]
[Provides detailed analysis searching for existing auth patterns, 
documenting API layers, proposing JWT vs OAuth vs session approaches, 
recommending JWT with refresh tokens based on existing patterns and project stack]
```

---

## Optional Addendum: ATDD Gate Overlay (ai-driven-dev)

If the session enables the ATDD overlay, apply the following **in addition** to the PDCA analysis.

### Contract extraction (mandatory)
- Read repo contract files (as applicable): `gemini.md` / `agent.md`, `ARCHITECTURE.md` / `CLAUDE.md`, and (if present) `docs/architecture/**`, `docs/boundaries/**`.
- Produce a **Contract Summary** (3–7 numbered constraints). These constraints must be referenced later by number/title during Architecture Lock.

### Acceptance truth source planning
- Confirm whether `TEST_PLAN.md` already exists. If not, explicitly plan to create it *before* any production code.
- Identify the acceptance-test entrypoint directory: `tests/atdd/`.
- Identify the test runner + JUnit path for this repo (map to `ATDD_TEST_CMD` and `ATDD_JUNIT_PATH`).

### Architecture drift prevention
- Call out the top 3 “likely drift” risks (e.g., breaking dependency direction, moving business logic into UI, introducing `utils/common/shared`).
- For each risk, state the concrete guardrail (Gate, file budget, Architecture Lock red line, or doc obligation).
