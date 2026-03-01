#!/usr/bin/env python3
"""Initialize a new *plan topic module* skeleton on disk (two-level flat).

Usage:
  python init_plan_skill.py <target_dir> <module_slug> "<plan_title>"

Recommended target_dir:
  - plans/                          (generic project root)
  - docs/plans/                     (docs-oriented projects)
  - <any>/plan_modules/             (nested within feature area)
  Legacy examples (project-specific, not for general use):
  - 00_Documentation/99_Inbox/      (ERP project intake)
  - 00_Documentation/98_WIP/        (ERP active drafting)

It creates:
  <target_dir>/<module_slug>/
    INDEX.md
    CURRENT.md
    change_log.md
    investigation/
      _tracker.md
      tool_outputs/          # short-term memory: tool logs / api dumps / test output
    execution/
      _tracker.md
    references/
      P0_baseline.md
      P1_design.md
      P2_implementation.md
      P3_verification.md
      P4_release.md
      A1_risk_register.md
      A0_entity_registry.yaml
    questions/
    history/
"""

import os
import sys
import datetime

REFERENCE_FILES = {
    "references/P0_baseline.md": (
        "---\nname: P0 Baseline\ndescription: Current state facts, constraints, and evidence hooks.\n---\n\n"
        "# P0 Baseline / Overview\n\n"
        "## Current State (facts)\n\n"
        "## Constraints / Invariants\n\n"
        "## Evidence Hooks\n"
        "- code: ...\n- config: ...\n- contracts: ...\n- tests: ...\n\n"
    ),
    "references/P1_design.md": (
        "---\nname: P1 Design\ndescription: Proposed design, interface contracts, and tradeoffs.\n---\n\n"
        "# P1 Design & Contracts\n\n"
        "## Proposed Design\n\n"
        "## Interface Contracts\n\n"
        "### contract-B001\n\n"
        "### contract-B002\n\n"
        "## Invariants\n\n"
        "## Tradeoffs\n\n"
    ),
    "references/P2_implementation.md": (
        "---\nname: P2 Implementation\ndescription: Step-by-step plan, touchpoints, and pre-merge gates.\n---\n\n"
        "# P2 Implementation\n\n"
        "## Step-by-Step Plan\n\n"
        "### step-1\n\n"
        "### step-2\n\n"
        "## Touchpoints\n\n"
        "## Gates (pre-merge)\n\n"
    ),
    "references/P3_verification.md": (
        "---\nname: P3 Verification\ndescription: Testing matrix and verification gates.\n---\n\n"
        "# P3 Verification (Testing/Validation)\n\n"
        "## Test Matrix\n\n"
        "## Gates\n\n"
    ),
    "references/P4_release.md": (
        "---\nname: P4 Release\ndescription: Rollout stages, monitoring, and rollback playbook.\n---\n\n"
        "# P4 Rollout & Rollback\n\n"
        "## Rollout Stages\n\n"
        "## Monitoring\n\n"
        "## Rollback Playbook\n\n"
    ),
    "references/A1_risk_register.md": (
        "---\nname: A1 Risk Register\ndescription: Risk register with probability, impact, and mitigation.\n---\n\n"
        "# A1 Risk Register\n\n"
        "- R-001: <risk> | prob: <L/M/H> | impact: <L/M/H> | mitigation: ...\n"
    ),
    "references/A0_entity_registry.yaml": (
        "# A0_entity_registry.yaml\n"
        "# Purpose: maintain entity consistency across investigations.\n"
        "# See references/entity-registry.md for usage rules.\n\n"
        "entities: []\n"
    ),
}


def main(target_dir: str, module_slug: str, title: str):
    topic_dir = os.path.join(target_dir, module_slug)

    # Create directories
    for d in [
        "questions",
        "investigation",
        "investigation/tool_outputs",
        "execution",
        "references",
        "history",
    ]:
        os.makedirs(os.path.join(topic_dir, d), exist_ok=True)

    today = datetime.date.today().isoformat()
    plan_id = f"PLAN-{today.replace('-', '')}-001"

    # INDEX.md
    index_md = (
        f"# {title} — INDEX\n\n"
        f"## CURRENT (唯一可信入口)\n"
        f"- [CURRENT](CURRENT.md)\n\n"
        f"### PD Read Order\n"
        f"- **Static baseline** (always): INDEX → CURRENT (§0/§1/§2 tables) → trackers (active rows)\n"
        f"- **Dynamic drill-down** (only if triggered): B* / INV-* / references/P*\n"
        f"- **Budget**: Prefer pointers. History default 0. Per-batch deep reads ≤ 8.\n"
        f"- **Recitation**: If lost, recite from CURRENT Head Anchor + trackers before reading dynamic docs.\n\n"
        f"## Investigation\n"
        f"- [investigation/](investigation/)\n\n"
        f"## Execution (Batch Tasks)\n"
        f"- [execution/](execution/)\n\n"
        f"## Deep Detail\n"
        f"- [references/](references/)\n"
        f"- [Entity Registry](references/A0_entity_registry.yaml)\n\n"
        f"## History\n"
        f"- history/ (frozen prior versions)\n"
    )
    _write(topic_dir, "INDEX.md", index_md)

    # CURRENT.md
    current_md = (
        f"---\n"
        f"name: {plan_id} {title}\n"
        f"description: >-\n"
        f"  Plan entry for {title}.\n"
        f"plan_title: {title}\n"
        f"plan_id: {plan_id}\n"
        f"status: NORMING\n"
        f"revision: v001\n"
        f"last_updated: {today}\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"## Head Anchor\n"
        f"<!-- Recitation Source of Truth. Keep ≤7 lines. -->\n"
        f"- **Goal**: <one sentence>\n"
        f"- **Status**: NORMING\n"
        f"- **Active IDs**: —\n"
        f"- **Next actions**: 1. Read norms 2. Identify INV needs 3. Create baseline\n"
        f"- **Hard constraints**: <from §0>\n"
        f"- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md)\n\n"
        f"## §0 Norms (Standards Baseline)\n\n"
        f"> Read norm files and establish the baseline before any investigation.\n\n"
        f"### Norm Sources\n"
        f"- `gemini.md` — project root norms\n"
        f"- Architecture docs\n"
        f"- Relevant module interfaces\n"
        f"- Existing tests\n\n"
        f"### Data Flow\n"
        f"```\n(Draw relevant data path here)\n```\n\n"
        f"### Interface Contracts\n"
        f"| Interface | Input | Output | Norm Source |\n"
        f"|-----------|-------|--------|------------|\n"
        f"| ... | ... | ... | ... |\n\n"
        f"### Gates\n"
        f"| Gate | Condition | Source |\n"
        f"|------|-----------|--------|\n"
        f"| ... | ... | ... |\n\n"
        f"### Boundary Constraints\n"
        f"- ...\n\n"
        f"### Baseline Confirmation\n"
        f"- [ ] Norm files read\n"
        f"- [ ] Data flow mapped\n"
        f"- [ ] Interface contracts recorded\n"
        f"- [ ] Gates listed\n"
        f"- [ ] Boundary constraints confirmed\n\n"
        f"---\n\n"
        f"## §1 Batch Overview\n"
        f"| Batch | Title | Status | Gates | Impact |\n"
        f"|-------|-------|--------|-------|--------|\n\n"
        f"→ Detail: [execution/_tracker.md](execution/_tracker.md)\n\n"
        f"## §2 Investigation Overview\n"
        f"→ Detail: [investigation/_tracker.md](investigation/_tracker.md)\n\n"
        f"## §3 Batch Dependency Graph\n\n\n"
        f"## §4 Context Cards\n\n"
        f"### CTX-P0-BASELINE\n"
        f"→ [P0_baseline.md](references/P0_baseline.md)\n\n"
        f"### CTX-P1-DESIGN\n"
        f"→ [P1_design.md](references/P1_design.md)\n\n"
        f"### CTX-P2-IMPLEMENTATION\n"
        f"→ [P2_implementation.md](references/P2_implementation.md)\n\n"
        f"### CTX-P3-VERIFICATION\n"
        f"→ [P3_verification.md](references/P3_verification.md)\n\n"
        f"### CTX-P4-RELEASE\n"
        f"→ [P4_release.md](references/P4_release.md)\n\n"
        f"## §5 Decisions / Open Questions\n\n"
        f"### Decisions (D-*)\n\n"
        f"### Open Questions (Q-*)\n\n"
        f"## §6 Iteration Log\n"
        f"| Date | Trigger Event | Action | Impact |\n"
        f"|------|--------------|--------|--------|\n"
        f"| {today} | Initial creation | Created skeleton | — |\n\n"
        f"## Tail Anchor\n"
        f"<!-- Repeat Head Anchor. Keep in sync. -->\n"
        f"- **Goal**: <one sentence>\n"
        f"- **Status**: NORMING\n"
        f"- **Active IDs**: —\n"
        f"- **Next actions**: 1. Read norms 2. Identify INV needs 3. Create baseline\n"
        f"- **Hard constraints**: <from §0>\n"
        f"- **Links**: [tracker](execution/_tracker.md) · [change_log](change_log.md)\n"
    )
    _write(topic_dir, "CURRENT.md", current_md)

    # change_log.md
    _write(
        topic_dir,
        "change_log.md",
        f"# Change Log\n\n"
        f"| Date | Scope | Change | Trigger |\n"
        f"|------|-------|--------|--------|\n"
        f"| {today} | Global | Initialized plan module | — |\n",
    )

    # investigation/_tracker.md
    _write(
        topic_dir,
        "investigation/_tracker.md",
        "# Investigation Tracker\n\n"
        "> Tool outputs/logs are stored in `investigation/tool_outputs/` and indexed inside each INV report. Do not paste raw dumps into tracker.\n"
        "> Do NOT delete tracker rows. Completed INVs → ARCHIVED/INVALIDATED; update Report link to `history/` path.\n\n"
        "| ID | Topic | Method | Status | as_of | Report | Key Findings |\n"
        "|------|-------|--------|--------|-------|--------|-------------|\n",
    )

    # execution/_tracker.md
    _write(
        topic_dir,
        "execution/_tracker.md",
        "# Execution Tracker\n\n"
        "| Batch | Title | Status | Prerequisites | ATDD IDs |\n"
        "|-------|-------|--------|--------------|----------|\n",
    )

    # Reference files
    for rel, content in REFERENCE_FILES.items():
        path = os.path.join(topic_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    # SKILL.md shim (navigation-only entry point)
    skill_shim = (
        "---\n"
        f"name: {title} — Plan Module Entry\n"
        "description: Navigation shim. Do not write decisions here.\n"
        "---\n\n"
        f"# {title} — Plan Module Entry (Shim)\n\n"
        "## Read Order (Cold-start)\n"
        "1. [INDEX.md](INDEX.md) — Pass0 only: headings + tables\n"
        "2. [CURRENT.md](CURRENT.md) — Pass0 only: status + links\n"
        "3. [execution/_tracker.md](execution/_tracker.md) — active/blocked rows only\n"
        "4. [investigation/_tracker.md](investigation/_tracker.md) — active/blocked rows only\n\n"
        "## Do NOT write decisions here\n"
        "This file is navigation only. Put decisions in `references/P*.md` "
        "and log changes in `change_log.md`.\n"
    )
    _write(topic_dir, "SKILL.md", skill_shim)

    print(topic_dir)


def _write(base: str, rel: str, content: str):
    path = os.path.join(base, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            'Usage: init_plan_skill.py <target_dir> <module_slug> "<plan_title>"',
            file=sys.stderr,
        )
        sys.exit(2)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
