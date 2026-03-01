# Discovery Ladder (Static vs Dynamic)

Default discovery protocol for all PDCA phases. Prevents blind file exploration by imposing a structured search sequence.

## Definitions

- **Static context (baseline)**: Always include; small, stable pointers (project config, READMEs, test entrypoints, tracker active rows).
- **Dynamic context**: Load on-demand only when triggered by a specific need.

## Ladder (execute in order, stop when satisfied)

| Step | Action | Tools | Output |
|------|--------|-------|--------|
| 0 | **Static Baseline Scan** (≤2 min) | read file | `gemini.md`/`agent.md`/`rules.md`, `ARCHITECTURE.md`, README/docs index, test entrypoints, `.claude/instructions.md` (optional override) |
| 1 | **Structure Discovery** | `ls` / `glob` | Map folders; identify likely files |
| 2 | **Keyword/ID Search** | `rg` / `grep` | Exact tokens (class/function/route/error string) |
| 3 | **Header Scan** (cheap validation) | read file (first ≤30 lines) | Headings, signatures, imports of candidate files |
| 4 | **Targeted Read** (deep) | read file (line range) | Only the needed section; avoid full-file loading |
| 5 | **Record Pointers** | write | Add RefSpec to session log / plan read list |

## Rules

1. **Never skip steps.** Run steps 0–2 before any deep read.
2. **Produce a Candidate List** (RefSpec) at step 2 before opening files at step 4.
3. **Limit deep reads**: ≤3 files per search round; inline excerpt ≤60 lines.
4. **Record every deep read** as RefSpec in session log or plan (step 5 is mandatory).
5. **On blocker**: restart the ladder from step 1 with a new search term; do not "guess and open many files".

## When to use

- **Analysis**: Full ladder (steps 0–5). Output = Static baseline + Candidate List + Deep-read RefSpecs.
- **Planning**: Reference the ladder output; add Discovery/Reading deliverables to plan.
- **Implementation blocker**: Re-enter at step 1 with the error token/class name.
- **Completion**: Verify all deep reads are captured in artifact pointers.

> *Source*: `filesystem-context` — "Static context… always include… Dynamic context discovery… load files only when needed using filesystem operations."
