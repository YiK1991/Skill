# Convergence Mapping (Greenfield → plan-doc-editor)

When migrating from standalone PDCA (scratch/) to plan-doc-editor managed workspace:

## Directory mapping

| Greenfield (scratch/) | plan-doc-editor target | Merge rule |
|------------------------|----------------------|------------|
| `scratch/investigation/INV-*.md` | `investigation/INV-*.md` | Move; preserve F/C IDs and temporal validity |
| `scratch/references/P*.md` | `references/P*.md` | Move; reconcile anchors with existing design docs |
| `scratch/history/*` | `history/*` | Move; append to existing history |
| `scratch/tool_outputs/TO-*.txt` | `investigation/tool_outputs/TO-*.txt` | Move; update RefSpec pointers in INV reports |
| `scratch/worker_reports/W*.md` | `investigation/worker_reports/W*.md` | Move; update Worker Reports Index |
| `scratch/entity_registry.yaml` | `references/A0_entity_registry.yaml` | **Merge**: match by `entity_id`; prefer latest `last_verified`; append new entities |

## Entity registry merge rules

1. Match by `entity_id`. If both have the same entity: keep the one with latest `last_verified`.
2. New entities from scratch: append to target registry.
3. Conflicting `canonical_name` or `aliases`: flag for manual review.

## Post-migration checklist

- [ ] All RefSpec pointers in session/INV reports updated to new paths
- [ ] Entity registry merged without duplicates
- [ ] History files appended (not overwritten)
- [ ] Tool Outputs Index updated with new paths

> *Source*: `memory-systems` — "File-system memory layering and consolidation; without mapping, consolidation fails."
