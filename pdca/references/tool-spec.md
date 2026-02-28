# Tool Spec Standard (PDCA)

Standard for all tool outputs used within PDCA sessions.

## Required parameters

- `format`: `concise` | `detailed` (default: `concise`)

## Output contract

### concise (default)
- `status`: ok | error
- `summary`: ≤10 lines
- `key_excerpt`: optional, ≤80 lines
- `pointers`: RefSpec list (files/logs)
- `next_suggested_action`: short

### detailed (only when explicitly needed)
- Includes full stdout/stderr/log pointers
- Includes structured artifacts (json) if applicable

## When to use detailed (hard threshold — must be justified)

Allowed ONLY when:
- Error is **nondeterministic** (cannot reproduce with concise output)
- Gate/decision **requires evidence preservation** (e.g., eval Evidence Block)
- Environment-specific issue needs **full reproduction context**

Even in detailed mode:
- Full output must be **offloaded** to a file (not inline)
- Session keeps only ≤10-line summary + RefSpec pointer
- Unjustified detailed usage fails the Tool Efficiency rubric dimension

## Anti-patterns

- ❌ Returning full logs by default
- ❌ Multiple tools with overlapping purpose
- ❌ Inline dumps without RefSpec pointers

## PR Checklist for adding a tool

- [ ] Does this overlap an existing tool? If yes, consolidate instead.
- [ ] Does it support `format=concise|detailed` with concise default?
- [ ] Is filesystem-first still sufficient? If yes, do not add tool.
- [ ] Does the output avoid inline dumps and provide RefSpec pointers?

> *Source*: `tool-design` — "Response format options: tools must support concise/detailed… default concise to conserve context."
