# Edge Anchors (Lost-in-the-middle Mitigation)

Models exhibit U-shaped attention: middle content is more likely to be missed. Place critical information at the beginning and end.

## Anchor schema (≤7 lines each)

- **Goal** (1 line)
- **Current step / next step** (1–2 lines)
- **Hard constraints** (1–2 lines)
- **Key pointers** (RefSpec links) (1–2 lines)

## Where to apply

| Location | What |
|----------|------|
| Session log | Head Anchor (top) + Tail Anchor (bottom) |
| Per-step notes | Headline + Tail anchor (optional, for long steps) |

## Rules

1. Anchors must stay short (≤7 lines). No long prose.
2. Update anchors on drift or after each checkpoint.
3. If budget is tight, keep anchors; drop middle detail (use pointers/offload).
4. Head and Tail anchors must mirror each other (same content).

> *Source*: `context-degradation` — "Lost-in-the-middle / U-shaped attention… place critical info at beginning or end."
