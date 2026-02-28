---
name: Entity Registry Playbook
description: >-
  Rules for maintaining the entity registry (A0_entity_registry.yaml).
  Covers ID conventions, CRUD lifecycle, merge/alias, and temporal alignment.
---

# Entity Registry Playbook

## ID Convention

Format: `ENT-<DOMAIN>-<NNN>` (e.g. `ENT-AUTH-001`, `ENT-L3-002`)

- `<DOMAIN>`: short domain tag (AUTH, L3, WEBOS, INFRA, etc.)
- `<NNN>`: zero-padded sequence within domain
- Do not mix naming schemes within a single plan module

## Lifecycle

### Creating a new entity

1. Add entry to `references/A0_entity_registry.yaml` with all required fields
2. Set `last_verified` to today
3. Reference as `ENT-xxx` in INV/B/P files — do not repeat properties inline

### Updating properties

1. Edit `key_properties` in registry
2. Update `last_verified`
3. If the change invalidates prior findings, update related F/C items (`superseded_by`)

### Merging duplicates

1. Pick the canonical entry; keep its `entity_id`
2. Add the duplicate's name to `aliases`
3. In `refs`, note: `"merged from ENT-xxx on YYYY-MM-DD"`
4. In any files referencing the old ID, update to canonical ID

## Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `entity_id` | ✅ | `ENT-<DOMAIN>-<NNN>` |
| `type` | ✅ | `module` / `api` / `person` / `service` / `dataset` / `repo` |
| `canonical_name` | ✅ | Primary display name |
| `aliases` | optional | Alternative names for search/discovery |
| `key_properties` | ✅ | Only critical attributes (owner, path, endpoint, etc.) |
| `last_verified` | ✅ | Date properties were last confirmed accurate |
| `refs` | optional | RefSpec pointers to evidence (INV/B/P files) |

## Anti-Bloat Rules

- `key_properties`: max 5 fields per entity. Detailed specs → `references/P*` via RefSpec.
- `refs`: pointers only. No inline summaries.
- Registry total: if >50 entities, consider splitting by domain into separate YAML files.

## Temporal Alignment

- `last_verified` aligns with INV `as_of` and F/C `valid_from`
- If `last_verified` is >30 days old, flag for re-verification during next INV cycle

## Examples

### Module entity

```yaml
- entity_id: ENT-L3-001
  type: module
  canonical_name: l3-pipeline
  aliases: [l3_core, feature_engine]
  key_properties:
    owner: "@data-team"
    repo_path: "03_L3_Core/l3/pipeline"
  last_verified: "2026-02-28"
  refs:
    - "investigation/INV-002_l3_drift.md#F-001"
```

### API entity

```yaml
- entity_id: ENT-WEBOS-001
  type: api
  canonical_name: diagnosis-endpoint
  key_properties:
    endpoint: "/api/v2/diagnosis/{style_id}"
    method: GET
    schema_version: "4.0"
  last_verified: "2026-02-28"
  refs:
    - "references/P1_design.md#contract-B017"
```
