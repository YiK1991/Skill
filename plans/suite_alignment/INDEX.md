# 三 Skill Suite 对齐优化 — INDEX

## CURRENT (唯一可信入口)
- [CURRENT](CURRENT.md)

### PD Read Order
- **Static baseline** (always): INDEX → CURRENT (§0/§1/§2 tables) → trackers (active rows)
- **Dynamic drill-down** (only if triggered): B* / INV-* / references/P*
- **Budget**: Prefer pointers. History default 0. Per-batch deep reads ≤ 8.
- **Recitation**: If lost, recite from CURRENT Head Anchor + trackers before reading dynamic docs.

## Investigation
- [investigation/](investigation/)

## Execution (Batch Tasks)
- [execution/](execution/)

## Deep Detail
- [references/](references/)
- [Entity Registry](references/A0_entity_registry.yaml)

## History
- history/ (frozen prior versions)
