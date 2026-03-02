---
task_id: TASK-EXAMPLE-REV
intent: review
scope: <one aspect only>
review_scope:
  # Add only real paths, or keep this list empty.
  # - path/to/dir_or_file
---

# TASK-EXAMPLE-REV: <short title>

## ⛔ Role & Permissions (READ-ONLY)

- Role: Senior architecture auditor (not a developer).
- Allowed: read code/docs/tests/config; write Markdown report only.
- Forbidden: modify any code/config; create/delete code files; commit/push.

## 0) Meta (repeat placement here)

- task_id: TASK-EXAMPLE-REV
- intent: review
- repo: <owner/repo>
- starting_branch: <branch>
- output_path:
  - plan module: `<plan_module>/investigation/INV-*_jules_review.md`
  - no plan module: `jules_pack/results/TASK-EXAMPLE-REV_review.md`

## 1) Objective

Write a single-scope review objective. Include 4–6 concrete questions that require code evidence.

Example questions:
- Is the dependency direction consistent with the repo's architecture rules?
- Is there any boundary leakage (domain → infra/UI coupling)?
- Are naming/placement rules violated (e.g. `utils.py`, `common.py`)?

## 2) Context (disclosure-only)

### Standards (read first)

- Root norms: `gemini.md` / `agent.md` / `rules.md` (if present)
- Architecture docs (if present)

### Review scope (paths)

List only the paths you want reviewed:
- `<path/to/dir_or_file>` — <what to check>

## Document Placement (MANDATORY)

The review report must be written to one of the following:

- plan module (preferred): `<plan_module>/investigation/INV-001_jules_review_example.md`
- no plan module: `jules_pack/results/TASK-EXAMPLE-REV_review.md`

## 4.5) Governance Capsule (MANDATORY)

### Authority

- Base every finding on **real code** from the provided context.
- If required files/paths are missing or the scope is ambiguous: **STOP** and ask for clarification.
- Do not invent modules, behavior, or tests.

### Output Contract (PD-OUT v1)

The report must include these exact fields:

- Read List (RefSpec):
- Write List (RefSpec):
- Evidence Pointers (RefSpec):
- Plan Update Targets (RefSpec + bullet edits):

### Stop Conditions

- Stop if you cannot locate the referenced files/paths in the repo.
- Stop if the task would require writing code (convert to Suggested Fix instead).

