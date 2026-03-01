#!/usr/bin/env python3
"""Suite Consistency Lint — scan for deprecated patterns across skill docs.

Usage:
  python scripts/check_suite_consistency.py [--root <repo_root>]

Scans all .md and .py files for known anti-patterns (old narratives,
deprecated commands, etc.) and reports file + line number.

This is a manual script — not a CI gate. Run after doc changes to catch
"old narrative revival".
"""

import argparse
import os
import re
from typing import List, Tuple

# Each rule: (pattern_regex, description, allowed_context_regex_or_None)
# If allowed_context is set, matches within that context are suppressed.
RULES: List[Tuple[re.Pattern, str, re.Pattern | None]] = [
    (
        re.compile(r"jules_bridge\.py\s+.*submit", re.IGNORECASE),
        "direct bridge submit (should be dispatch-only; debug requires _JULES_DISPATCH=1)",
        re.compile(
            r"debug|legacy|emergency|_JULES_DISPATCH|禁止|不要|deprecated|blocked|NEVER|MUST|Anti.Pattern|Symptom|Root.Cause|bypassed|wasted",
            re.IGNORECASE,
        ),
    ),
    (
        re.compile(r"--parallel\s+\d"),
        "--parallel flag (known to cause API 400; should be marked as deprecated/disabled)",
        re.compile(
            r"禁用|不建议|deprecated|bug|400|不要|avoid|disabled|warning|⚠",
            re.IGNORECASE,
        ),
    ),
    (
        re.compile(r'echo\s+["\'].*["\']\s*\|\s*jules\s+remote'),
        "echo pipe to jules (encoding risk; use 'type file |' or dispatch)",
        re.compile(
            r"legacy|emergency|risk|warning|⚠|不建议|avoid|deprecated", re.IGNORECASE
        ),
    ),
    (
        re.compile(r"GATE-2a", re.IGNORECASE),
        "GATE-2a (deprecated term; now GATE-2)",
        None,
    ),
    (
        re.compile(r"--base\s+origin/main(?!\s*[→>])", re.IGNORECASE),
        "hardcoded --base origin/main (should use --base auto)",
        re.compile(
            r"auto|候选|fallback|example|显式|explicit|历史|historical|pitfall|anti.pattern|symptom",
            re.IGNORECASE,
        ),
    ),
    (
        re.compile(r"English[- ]only\s+prompt", re.IGNORECASE),
        "English-only prompt enforcement (CJK allowed in body since Round 5)",
        re.compile(
            r"旧|legacy|historical|deprecated|已改|changed|CJK allowed", re.IGNORECASE
        ),
    ),
    (
        re.compile(r"00_Documentation/99_Inbox", re.IGNORECASE),
        "00_Documentation/99_Inbox as default placement (should be conditional/standalone-only)",
        re.compile(
            r"legacy|example|仅|only|示例|project-specific|ERP|Standalone|条件",
            re.IGNORECASE,
        ),
    ),
]

SKIP_DIRS = {"__pycache__", ".git", ".runtime", "history", "node_modules"}
SKIP_FILES = {"check_suite_consistency.py"}  # exclude self
EXTENSIONS = {".md", ".py"}


def scan_file(filepath: str) -> List[Tuple[int, str, str]]:
    """Scan a single file. Returns list of (line_no, line_content, rule_desc)."""
    hits = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except OSError:
        return hits

    for i, line in enumerate(lines, 1):
        for pattern, desc, allowed_ctx in RULES:
            if pattern.search(line):
                # Check if the violation is in an allowed context
                if allowed_ctx and allowed_ctx.search(line):
                    continue
                # Also check surrounding lines (±2) for context
                context_window = "".join(lines[max(0, i - 3) : min(len(lines), i + 2)])
                if allowed_ctx and allowed_ctx.search(context_window):
                    continue
                hits.append((i, line.rstrip(), desc))
    return hits


def main():
    ap = argparse.ArgumentParser(description="Suite Consistency Lint")
    ap.add_argument(
        "--root",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Repository root (default: parent of scripts/)",
    )
    args = ap.parse_args()

    total_hits = 0
    files_with_hits = 0

    for dirpath, dirnames, filenames in os.walk(args.root):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in filenames:
            if fname in SKIP_FILES:
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, fname)
            rel = os.path.relpath(filepath, args.root)
            hits = scan_file(filepath)
            if hits:
                files_with_hits += 1
                for line_no, line_content, desc in hits:
                    total_hits += 1
                    print(f"  {rel}:{line_no}: {desc}")
                    print(f"    | {line_content}")

    print(f"\n{'=' * 60}")
    if total_hits == 0:
        print("[OK] No deprecated patterns found. Suite is consistent.")
        return 0
    else:
        print(f"[WARN] {total_hits} hit(s) in {files_with_hits} file(s).")
        print(
            "Review each hit: if it's in a 'legacy/debug/warning' context, it may be acceptable."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
