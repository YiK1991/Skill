#!/usr/bin/env python3
"""Gate-PD: Post-execution quality gate for Jules output documents.

Validates that Jules review/implement reports follow PD-OUT v1 structure:
  - Required headings present (Head Anchor, How to Read, Index, Plan Update Targets)
  - Code blocks within excerpt limit (<=60 lines)
  - RefSpec usage (path#anchor or path:Lx-Ly) vs bare paths

Usage:
    python gate_pd_output.py <report.md> [<report2.md> ...]

Exit codes:
    0 = all checks passed (stdout: true)
    1 = violations found (stdout: false, stderr: diagnostics)
"""

import re
import sys
from pathlib import Path

# --------------- Configuration ---------------

MAX_CODE_BLOCK_LINES = 60

# Required headings — at least one variant must appear
REQUIRED_HEADINGS = [
    ["Head Anchor"],
    ["How to Read This", "How to Read"],
    ["Issue Index", "Changes", "Key Findings"],
    ["Plan Update Targets"],
]

# RefSpec pattern: path#anchor or path:Lx-Ly
_REFSPEC_RE = re.compile(r"`[^\s`]+(?:#[^\s`]+|:L\d+-L?\d+)`")
# Bare path pattern: standalone file paths without RefSpec
_BARE_PATH_RE = re.compile(
    r"(?<![`#])\b[\w./\\]+\.(?:py|ts|tsx|js|md|yaml|yml|json)\b(?![\w#:`])"
)


# --------------- Checks ---------------


def check_headings(content: str, filepath: str) -> list:
    """Check that all required PD-OUT v1 headings are present."""
    violations = []
    for variants in REQUIRED_HEADINGS:
        found = False
        for v in variants:
            if re.search(
                rf"^#+\s+.*{re.escape(v)}", content, re.MULTILINE | re.IGNORECASE
            ):
                found = True
                break
        if not found:
            violations.append(
                f"  MISSING heading: '{variants[0]}' (or variants: {variants})"
            )
    return violations


def check_code_blocks(content: str, filepath: str) -> list:
    """Check that no single code block exceeds MAX_CODE_BLOCK_LINES."""
    violations = []
    in_block = False
    block_start = 0
    block_lines = 0

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_block:
                in_block = True
                block_start = i
                block_lines = 0
            else:
                if block_lines > MAX_CODE_BLOCK_LINES:
                    violations.append(
                        f"  Code block L{block_start}-L{i}: {block_lines} lines "
                        f"(limit: {MAX_CODE_BLOCK_LINES}). Offload to a separate file."
                    )
                in_block = False
                block_lines = 0
        elif in_block:
            block_lines += 1

    return violations


def check_refspec_usage(content: str, filepath: str) -> list:
    """Check RefSpec usage ratio vs bare paths."""
    refspec_count = len(_REFSPEC_RE.findall(content))
    bare_count = len(_BARE_PATH_RE.findall(content))

    violations = []
    if bare_count > 0 and refspec_count == 0:
        violations.append(
            f"  No RefSpec found but {bare_count} bare file paths detected. "
            f"Use `path#anchor` or `path:Lx-Ly` format."
        )
    elif bare_count > refspec_count and bare_count > 3:
        violations.append(
            f"  Low RefSpec ratio: {refspec_count} RefSpecs vs {bare_count} bare paths. "
            f"Prefer RefSpec for traceability."
        )
    return violations


# --------------- Main ---------------


def gate_check(filepath: str) -> list:
    """Run all PD-OUT v1 checks on a single file."""
    path = Path(filepath)
    if not path.exists():
        return [f"  File not found: {filepath}"]

    content = path.read_text(encoding="utf-8", errors="replace")
    all_violations = []

    heading_v = check_headings(content, filepath)
    if heading_v:
        all_violations.append(f"[Heading Check] {filepath}")
        all_violations.extend(heading_v)

    code_v = check_code_blocks(content, filepath)
    if code_v:
        all_violations.append(f"[Code Block Check] {filepath}")
        all_violations.extend(code_v)

    ref_v = check_refspec_usage(content, filepath)
    if ref_v:
        all_violations.append(f"[RefSpec Check] {filepath}")
        all_violations.extend(ref_v)

    return all_violations


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: gate_pd_output.py <report.md> [<report2.md> ...]", file=sys.stderr
        )
        sys.exit(2)

    all_violations = []
    for fpath in sys.argv[1:]:
        all_violations.extend(gate_check(fpath))

    if all_violations:
        print("false")
        print("Gate-PD FAILED: PD-OUT v1 violations found:\n", file=sys.stderr)
        for v in all_violations:
            print(v, file=sys.stderr)
        print(
            "\nFix: Restructure report to follow PD-OUT v1 "
            "(Head Anchor → How to Read → Index → Details → Offload → Plan Update Targets). "
            "See P13 in operational-pitfalls.md.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print("true")
        print("Gate-PD PASSED: PD-OUT v1 structure verified.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
