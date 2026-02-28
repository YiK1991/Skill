# Optimization Playbook (Quick Reference)

Scenario → Action lookup for context optimization.

| Scenario | Action | Details |
|----------|--------|---------|
| pytest output > 100 lines | **Offload + Mask** | Write to `scratch/tool_outputs/TO-*_pytest.txt`; replace in session with ≤10-line summary + RefSpec |
| 3+ hypotheses in parallel | **Partition** | Create `scratch/investigation/INV-*.md` per hypothesis; session keeps only index pointers |
| Same log block cited repeatedly | **Mask** | Keep one RefSpec pointer; remove all duplicate pastes |
| Session too long (steps ≥ 8) | **Compaction** | Anchored incremental merge into Session Compaction Block (see context-compression.md) |
| Search output > 50 matches | **Offload + Mask** | Write to file; inline only top 5–10 relevant matches + RefSpec |
| Design discussion growing | **Partition** | Move to `scratch/references/P1_design.md`; session keeps only decisions |
| Budget trigger hit ≥ 2 | **Mask → Partition → Compact** | Execute in order until under budget |

> *Source*: `context-optimization` — Decision Framework: choose the minimally invasive technique first.
