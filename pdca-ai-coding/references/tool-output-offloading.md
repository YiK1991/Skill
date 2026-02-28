# Tool Output Offloading (Short-term Memory)

Large tool outputs pollute context. Offload to filesystem; keep chat/session clean.

## Offload rule

If output is large (>2000 tokens OR >100 lines OR >50KB):
1. Write full output to a file.
2. Return only:
   - ≤10-line summary
   - ≤80-line key excerpt (optional)
   - RefSpec pointer to the stored file (+ line range if relevant)

## Naming convention (mandatory)

Pattern: `TO-<session_id>-<step>-<seq>_<tool>_<slug>.<ext>`

Example: `TO-20260228-S03-001_pytest_auth_failures.txt`

Components: session date or ID + step number + sequence + tool name + short slug.

## Indexing

Record each offloaded file in:
- **Session**: `Tool Outputs Index` table (session-template)
- **INV report** (if using plan-doc-editor): `Tool Outputs (Offloaded)` table

Required index columns:
- `File (RefSpec)` — path to offloaded file
- `Purpose` — what this output contains
- `masked_from` — which session step/chat turn this was originally pasted in
- `extracted_to` — which decision/compaction section/INV F/C this evidence feeds

## Targeted retrieval

When you need evidence from an offloaded file:
1. Use `grep`/`rg` + line ranges to pull only the needed fragment.
2. Inline only the minimal excerpt (≤80 lines).
3. Reference the rest via RefSpec pointer.

> *Source*: `filesystem-context` — "Tool outputs can be extremely large… write the full result to a file and return only a summary with reference."

## Offloading vs Masking

- **Offloading** = store full output to file (storage action).
- **Masking** = replace any previously pasted verbose content with summary + RefSpec, and never paste it again (context cleanup action).
