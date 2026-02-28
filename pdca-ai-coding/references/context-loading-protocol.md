# Context Loading Protocol (PD + JIT)

Default protocol for all PDCA phases. Keeps context lean by loading pointers first and content only when needed.

## Core rules (must follow)

1. **Progressive Disclosure**: Read summary/index first; deep-read only when triggered.
2. **JIT identifiers**: Store pointers (RefSpec), not copied content.
3. **Excerpts only**: Inline excerpts ≤60 lines per snippet; otherwise use RefSpec.
4. **Two-pass read**: (1) list candidate files (RefSpec) → (2) open only the smallest relevant sections.
5. **Write protocol**: Show changes as patch-style snippets with file path + line range; avoid full-file dumps.

## RefSpec format

| Type | Format | Example |
|------|--------|---------|
| File anchor | `path/to/file.md#heading-anchor` | `references/P1_design.md#contract-B001` |
| Code line-range | `path/to/file.py:L120-L180` | `src/auth/service.py:L42-L55` |
| Directory scope | `path/to/dir/` | `03_L3_Core/l3/pipeline/` (discovery only) |

## RefSpec normalization rules

- **Markdown/prose**: prefer `#heading-anchor` (stable across reformats).
- **Code/logs**: use `path:Lx-Ly` (line ranges may shift; re-verify after refactors).
- **Every RefSpec must have a short label**: `[purpose] path#anchor` (e.g., `[contract] P1_design.md#B001`).
- **No bare paths**: `src/foo.py` alone is not a valid RefSpec; must include anchor or line-range.

## Excerpt limits

| Context | Max lines |
|---------|-----------|
| Inline code excerpt | ≤60 lines |
| Inline search results | ≤30 lines |
| Anything larger | Offload to file & reference via RefSpec |

## Output expectations per phase

| Phase | Default output |
|-------|---------------|
| **Analysis** | Read List (RefSpec) + ≤3 representative excerpts |
| **Planning** | Execution Read/Write List (RefSpec) + step-by-step pointers |
| **Implementation** | Patch-style snippets + RefSpec/line ranges |
| **Completion** | Artifact pointers (files changed + key anchors) |

> *Source*: Progressive disclosure, JIT identifiers — "load information only as needed… maintain lightweight identifiers."
