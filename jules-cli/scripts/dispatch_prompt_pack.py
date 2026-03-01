#!/usr/bin/env python3
"""Dispatch a Prompt Pack (tasks/*.md) via jules_bridge.

Gates block submission before any API call is made:

  GATE-1    (Status Filter):  Only tasks marked `pending` in PACK.md status column are submitted.
  GATE-FNAME (Unique Mapping): Each pending task_id maps to exactly one file; duplicate/missing files are blocked.
  GATE-UTF8 (Encoding):       All pack/task files must be strict UTF-8 (BOM auto-stripped).
  GATE-2    (Temp Copy):      ALL tasks copied to ASCII-safe temp dir; canonical TASK-XXX.md names; BOM stripped.
  GATE-2b   (Hydration):      {{ HYDRATE: path:selector }} macros replaced (Lx-Ly, #Heading, BEGIN...END).
  GATE-4    (Batch Limit):    Batch size capped (default 50).
  GATE-CLI-BATCH (CLI Mode):  Blocks multi-task dispatch without JULES_API_KEY (ghost session reuse risk).
  GATE-6    (Branch Check):   Verifies starting branch exists on remote (timeout = BLOCK).
  GATE-7    (Governance):     Each task must have Governance Capsule + Document Placement.
  GATE-FFFD (Integrity):      Reject prompts containing U+FFFD (silent corruption indicator).
  GATE-TASKID (Content):      task_id in file header must match filename prefix (case-insensitive).
  GATE-3    (Smoke Test):     First task submitted alone; failure aborts batch.

See jules-cli/references/operational-pitfalls.md for the full pitfall catalog.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Set, Tuple

# --------------- Encoding: force UTF-8 on Windows (GBK default) ---------------
if sys.platform == "win32":
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name)
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")


# ========================== GATE-1: PACK.md Status Filter ==========================


def parse_pending_tasks(pack_dir: str) -> Tuple[List[str], Set[str]]:
    """Parse PACK.md and return (ordered_list, set) of task_ids whose status is 'pending'.

    The list preserves PACK.md row order (for deterministic smoke-test ordering).
    Returns ([], set()) if PACK.md is missing or has no task table.
    Raises SystemExit if PACK.md exists but has zero pending tasks (safety).
    """
    pack_md = os.path.join(pack_dir, "PACK.md")
    if not os.path.isfile(pack_md):
        raise SystemExit(
            f"GATE-1 BLOCKED: PACK.md not found at {pack_md}.\n"
            "Every pack MUST have a PACK.md with a task table. "
            "Cannot determine which tasks to submit without it."
        )

    # Read with strict UTF-8 (binary + decode) to give clear error on bad encoding
    try:
        raw = open(pack_md, "rb").read()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]  # strip BOM
        content = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SystemExit(
            f"GATE-1 BLOCKED: PACK.md is not valid UTF-8 (byte {exc.start}).\n"
            "Fix: Re-save PACK.md as UTF-8 (no BOM)."
        )

    # Locate the "status" column index from the header row.
    # Typical format: | Task ID | Description | Aspect | Status | ... |
    # If no explicit "status" header is found, BLOCK (enforces table contract).
    status_col: int | None = None
    header_found = False
    pending_list: List[str] = []  # preserves PACK.md row order
    pending_set: Set[str] = set()
    all_tasks: Set[str] = set()

    for line in content.splitlines():
        cells = [c.strip() for c in line.split("|")]
        # Detect header row (contains "status" in one of its cells)
        if not header_found and not re.match(r"\|\s*(TASK-[\w\-]+)\s*\|", line):
            for idx, cell in enumerate(cells):
                if cell.lower() == "status":
                    status_col = idx
                    header_found = True
                    break
            continue

        # Skip separator rows (|---|---|---| etc.)
        if re.match(r"\|[\s\-:|]+\|", line):
            continue

        # Match data rows: | TASK-XXX | ... |
        m = re.match(r"\|\s*(TASK-[\w\-]+)\s*\|", line)
        if not m:
            continue
        task_id = m.group(1).upper()  # normalize to uppercase
        all_tasks.add(task_id)

        # Determine if this row is "pending" — only check the Status column
        is_pending = False
        if status_col is not None and status_col < len(cells):
            is_pending = cells[status_col].strip().lower() == "pending"

        if is_pending and task_id not in pending_set:
            pending_list.append(task_id)
            pending_set.add(task_id)

    if not header_found:
        raise SystemExit(
            "GATE-1 BLOCKED: PACK.md table has no 'Status' column header.\n"
            "Expected a header row with a cell exactly matching 'Status' "
            "(e.g. | Task ID | Description | Status | ...).\n"
            "Add the Status column header to PACK.md so pending detection is unambiguous."
        )

    if not all_tasks:
        raise SystemExit(
            "GATE-1 BLOCKED: PACK.md has no task table rows (expected | TASK-XXX | ... |).\n"
            "Add tasks to the table before dispatching."
        )

    if not pending_list:
        raise SystemExit(
            f"GATE-1 BLOCKED: PACK.md has {len(all_tasks)} tasks but NONE are 'pending'.\n"
            f"Found task IDs: {', '.join(sorted(all_tasks))} — all non-pending.\n"
            "Mark tasks as 'pending' in the Status column of PACK.md before dispatching."
        )

    return pending_list, pending_set


def filter_task_files(tasks_dir: str, pending_ids: Set[str]) -> List[str]:
    """Return only task files whose TASK-XXX id is in the pending set."""
    all_files = sorted(f for f in os.listdir(tasks_dir) if f.lower().endswith(".md"))

    matched: List[str] = []
    skipped: List[str] = []
    for fname in all_files:
        # Extract TASK-XXX from filename (e.g., TASK-017.md, TASK-017_auth.md)
        m = re.match(r"(TASK-[\w\-]+)", fname, re.IGNORECASE)
        if m and m.group(1).upper() in pending_ids:
            matched.append(os.path.join(tasks_dir, fname))
        else:
            skipped.append(fname)

    if skipped:
        eprint(
            f"GATE-1: Skipping {len(skipped)} non-pending tasks: {', '.join(skipped)}"
        )

    if not matched:
        raise SystemExit(
            f"GATE-1 BLOCKED: {len(all_files)} files in tasks/ but none match pending IDs "
            f"({', '.join(sorted(pending_ids))}).\n"
            "Ensure task filenames start with TASK-XXX matching PACK.md entries."
        )

    eprint(
        f"GATE-1 PASSED: {len(matched)} pending tasks to submit "
        f"(skipped {len(skipped)} non-pending)"
    )

    # GATE-1b: tasks/ must ONLY contain pending files (no stale leftovers)
    extra_files = [f for f in skipped if f not in (".", "..")]
    if extra_files:
        eprint(
            f"GATE-1b WARNING: {len(extra_files)} extra files in tasks/ not in PACK pending: "
            f"{', '.join(extra_files)}\n"
            "  These will NOT be submitted but should be removed to keep the pack clean."
        )

    return matched


# ========================== GATE-FNAME: Unique task_id→file mapping ================

_TASK_ID_RE = re.compile(r"(TASK-[\w-]+)", re.IGNORECASE)


def extract_task_id_from_filename(fname: str) -> str | None:
    """Extract the canonical (uppercased) TASK-XXX id from filename prefix."""
    m = _TASK_ID_RE.match(os.path.basename(fname))  # prefix match, not search
    return m.group(1).upper() if m else None


def gate_fname_unique_mapping(
    task_files: List[str], pending_list: List[str]
) -> Dict[str, str]:
    """Enforce 1:1 mapping: each pending task_id maps to exactly one file.

    Returns a dict {task_id_upper: file_path}.
    Raises SystemExit if any task_id has 0 or >1 matching files.
    """
    # Group files by task_id
    by_id: Dict[str, List[str]] = {}
    for fpath in task_files:
        tid = extract_task_id_from_filename(fpath)
        if tid:
            by_id.setdefault(tid, []).append(fpath)

    errors: List[str] = []
    mapping: Dict[str, str] = {}

    for tid in pending_list:  # preserves PACK.md row order
        tid_upper = tid.upper()
        matches = by_id.get(tid_upper, [])
        if len(matches) == 0:
            errors.append(
                f"  {tid_upper}: no matching file in tasks/ (expected TASK-XXX*.md)"
            )
        elif len(matches) > 1:
            names = ", ".join(os.path.basename(f) for f in matches)
            errors.append(
                f"  {tid_upper}: {len(matches)} files match ({names}).\n"
                f"    Fix: keep one canonical file; move others to tasks/_stale/ or rename."
            )
        else:
            mapping[tid_upper] = matches[0]

    if errors:
        raise SystemExit(
            "GATE-FNAME BLOCKED: task_id → file mapping is not 1:1\n\n"
            + "\n".join(errors)
            + "\n\nEach pending TASK-XXX in PACK.md must have exactly one file in tasks/."
        )

    eprint(f"GATE-FNAME PASSED: {len(mapping)} tasks have unique file mappings")
    return mapping


# ========================== GATE-UTF8: Strict Encoding Enforcement =================


def ensure_utf8_strict(pack_dir: str, task_files: List[str]) -> List[str]:
    """Verify all pack/task files are valid UTF-8. Strip BOM if present.

    Returns the (potentially BOM-stripped) list of file paths.
    Raises SystemExit if any file is not valid UTF-8.
    """
    files_to_check = list(task_files)
    pack_md = os.path.join(pack_dir, "PACK.md")
    if os.path.isfile(pack_md) and pack_md not in files_to_check:
        files_to_check.insert(0, pack_md)

    failures = []
    for fpath in files_to_check:
        try:
            with open(fpath, "rb") as fh:
                raw = fh.read()
        except OSError as exc:
            failures.append(f"  {fpath}: cannot read ({exc})")
            continue

        has_bom = raw.startswith(b"\xef\xbb\xbf")
        if has_bom:
            raw = raw[3:]

        try:
            raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            failures.append(
                f"  {os.path.basename(fpath)}: not valid UTF-8 at byte {exc.start}"
            )
            continue

        if has_bom:
            # Only WARN; do NOT write back to original file (avoid repo dirty surprises)
            # BOM will be stripped later when file is copied to temp dir (GATE-2)
            eprint(
                f"  BOM detected (will be stripped in temp copy): {os.path.basename(fpath)}"
            )

    if failures:
        raise SystemExit(
            "GATE-UTF8 BLOCKED: Non-UTF-8 files detected\n"
            "\n" + "\n".join(failures) + "\n\n"
            "Fix: Re-save files as UTF-8 (no BOM). On Windows: "
            "chcp 65001 then re-create the file."
        )
    eprint(f"GATE-UTF8 PASSED: {len(files_to_check)} files are valid UTF-8")
    return task_files


# ========================== GATE-2: ASCII Path Enforcement ==========================


def is_ascii_safe(path: str) -> bool:
    """Check if path contains only ASCII characters."""
    try:
        path.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def ensure_ascii_paths(task_files: List[str]) -> List[str]:
    """Copy ALL task files to an isolated ASCII-safe temp dir.

    Basenames are renamed to canonical ASCII-safe names (TASK-XXX.md)
    to avoid the 'copied but still non-ASCII filename' problem.
    Returns the relocated list of file paths.
    """

    # Create isolated PID-scoped temp directory (prevents concurrent collision)
    temp_dir = os.path.join(tempfile.gettempdir(), f"jules_dispatch_{os.getpid()}")
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    _task_id_re = re.compile(r"(TASK-[\w-]+)", re.IGNORECASE)
    relocated: List[str] = []
    for i, src in enumerate(task_files):
        orig_name = os.path.basename(src)
        tid = extract_task_id_from_filename(orig_name)
        ext = os.path.splitext(orig_name)[1] or ".md"
        # Canonical temp name: always TASK-XXX.md (strip slug; task_id is the key)
        canonical_name = f"{tid}{ext}" if tid else f"TASK-{i:03d}{ext}"
        if is_ascii_safe(orig_name):
            # Even ASCII files get canonical name in temp to ensure consistency
            safe_name = canonical_name if canonical_name != orig_name else orig_name
        else:
            safe_name = canonical_name
        dst = os.path.join(temp_dir, safe_name)
        # Copy content, stripping BOM if present
        with open(src, "rb") as f_in:
            raw = f_in.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        with open(dst, "wb") as f_out:
            f_out.write(raw)

        if safe_name != orig_name:
            eprint(f"  Renamed: {orig_name} -> {safe_name}")
        relocated.append(dst)

    eprint(
        f"GATE-2 PASSED: Copied {len(relocated)} files to ASCII-safe path: {temp_dir} "
        f"(canonical basenames: TASK-XXX.md)"
    )
    return relocated


# ========================== GATE-2b: JIT Context Hydration ==========================


_HYDRATE_RE = re.compile(
    r"\{\{\s*HYDRATE:\s*(?P<path>[^:}]+?)(?::(?P<range>[^}]+))?\s*\}\}"
)


def _read_hydrate_target(raw_path: str, range_str: str | None) -> str:
    """Read file content for a HYDRATE macro. Returns replacement text or error comment."""
    path = raw_path.strip()
    # Fallback: if relative path not found from cwd, try relative to pack-dir or repo root
    if not os.path.isfile(path) and not os.path.isabs(path):
        # Try common base directories: pack-dir, cwd, git repo root
        repo_root = ""
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if r.returncode == 0:
                repo_root = r.stdout.strip()
        except Exception:
            pass
        for base in [os.environ.get("_JULES_PACK_DIR", ""), os.getcwd(), repo_root]:
            candidate = os.path.join(base, path)
            if os.path.isfile(candidate):
                path = candidate
                break
    if not os.path.isfile(path):
        return f"<!-- HYDRATE ERROR: file not found: {path} -->"
    try:
        with open(
            path, encoding="utf-8-sig"
        ) as f:  # utf-8-sig strips BOM automatically
            lines = f.readlines()
    except (OSError, UnicodeDecodeError) as exc:
        return f"<!-- HYDRATE ERROR: {exc} -->"

    if not range_str:
        selected = lines
        label = path
    else:
        range_str = range_str.strip()
        m_lines = re.match(r"L(\d+)-L?(\d+)", range_str, re.IGNORECASE)
        if m_lines:
            start, end = int(m_lines.group(1)), int(m_lines.group(2))
            selected = lines[max(0, start - 1) : end]
            label = f"{path}:{range_str}"
        elif range_str.startswith("#"):
            # Markdown heading support (e.g., #Heading)
            def _normalize_heading(text: str) -> str:
                """Normalize heading text for comparison (strip backticks, emoji, extra punct)."""
                text = text.lower().strip()
                text = re.sub(
                    r"[`\u200b]", "", text
                )  # strip backticks, zero-width spaces
                text = re.sub(r"\s+", " ", text)  # collapse whitespace
                return text

            heading = _normalize_heading(range_str[1:])
            start_idx = -1
            end_idx = len(lines)
            heading_level = 0
            for i, line in enumerate(lines):
                m_head = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
                if m_head:
                    level = len(m_head.group(1))
                    title = _normalize_heading(m_head.group(2))
                    if start_idx == -1 and title == heading:
                        start_idx = i
                        heading_level = level
                    elif start_idx != -1 and level <= heading_level:
                        end_idx = i
                        break
            if start_idx != -1:
                selected = lines[start_idx:end_idx]
                label = f"{path}:{range_str}"
            else:
                return (
                    f"<!-- HYDRATE ERROR: heading '{range_str}' not found in {path} -->"
                )
        elif "..." in range_str:
            # BEGIN...END block marker support
            parts = range_str.split("...")
            start_marker, end_marker = parts[0].strip(), parts[1].strip()
            start_idx = -1
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if start_idx == -1 and start_marker in line:
                    start_idx = i
                elif start_idx != -1 and end_idx == len(lines) and end_marker in line:
                    end_idx = i + 1
                    break
            if start_idx != -1:
                selected = lines[start_idx:end_idx]
                label = f"{path}:{range_str}"
            else:
                return (
                    f"<!-- HYDRATE ERROR: markers '{range_str}' not found in {path} -->"
                )
        else:
            return f"<!-- HYDRATE ERROR: invalid range format '{range_str}' -->"

    content = "".join(selected).rstrip()
    return f"```\n# Source: {label}\n{content}\n```"


def hydrate_prompt_files(task_files: List[str]) -> List[str]:
    """Scan task files for {{ HYDRATE: path:Lx-Ly }} macros and replace with content.

    Files are modified in-place (they should already be temp copies from GATE-2).
    Returns the same list. If no macros found, files are untouched.
    """
    total_hydrated = 0
    for tf in task_files:
        with open(tf, encoding="utf-8") as f:
            content = f.read()

        if "HYDRATE:" not in content:
            continue

        def _replacer(m: re.Match) -> str:
            rng = m.group("range") if "range" in m.groupdict() else None
            return _read_hydrate_target(m.group("path"), rng)

        new_content = _HYDRATE_RE.sub(_replacer, content)
        if new_content != content:
            count = len(_HYDRATE_RE.findall(content))
            with open(tf, "w", encoding="utf-8") as f:
                f.write(new_content)
            total_hydrated += count

    if total_hydrated:
        eprint(f"GATE-2b PASSED: Hydrated {total_hydrated} macro(s) across task files")
    return task_files


# ========================== GATE-FFFD: Replacement Character Check ================


def check_no_replacement_chars(task_files: List[str]) -> None:
    """Scan all task files for U+FFFD (replacement character).

    If found, it means some gate silently corrupted content.
    Raises SystemExit with diagnostics.
    """
    failures = []
    for tf in task_files:
        content = open(tf, encoding="utf-8").read()
        if "\ufffd" in content:
            # Find first occurrence line number
            for i, line in enumerate(content.splitlines(), 1):
                if "\ufffd" in line:
                    failures.append(f"  {os.path.basename(tf)}:L{i}: contains U+FFFD")
                    break
    if failures:
        raise SystemExit(
            "GATE-FFFD BLOCKED: Unicode replacement character detected\n"
            "This means a file was silently corrupted somewhere in the pipeline.\n"
            "\n" + "\n".join(failures) + "\n\n"
            "Fix: Check source files for encoding issues. "
            "Re-save as UTF-8 and re-run."
        )
    eprint(f"GATE-FFFD PASSED: No replacement characters in {len(task_files)} files")


# ========================== GATE-3: Smoke Test ==========================


def smoke_test_first(task_files: List[str], build_cmd_fn) -> Dict[str, Any]:
    """Submit the first task alone. If it fails, abort the entire batch.

    Returns the result dict on success.
    Raises SystemExit if it failed.
    """
    first = task_files[0]
    eprint(f"GATE-3: Smoke test — submitting {os.path.basename(first)} alone...")

    cmd = build_cmd_fn(first)
    result = run_bridge(cmd)

    if result.get("ok"):
        eprint(
            f"GATE-3 PASSED: Smoke test succeeded (session_id={result.get('session_id', '?')})"
        )
        return result

    raise SystemExit(
        f"GATE-3 BLOCKED: Smoke test FAILED for {os.path.basename(first)}.\n"
        f"Error: {result.get('stderr', result.get('raw', 'unknown'))}\n"
        "Fix the issue before batch submission. "
        "The remaining tasks were NOT submitted (zero quota wasted on batch)."
    )


# ========================== Core Dispatch ==========================


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def run_bridge(cmd: List[str]) -> Dict[str, Any]:
    env = {
        **os.environ,
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "_JULES_DISPATCH": "1",  # Required by jules_bridge.py cmd_submit gate
    }
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        env=env,
    )
    if p.returncode != 0:
        return {
            "ok": False,
            "cmd": cmd,
            "stderr": p.stderr.strip(),
            "stdout": p.stdout.strip(),
        }
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return {
            "ok": False,
            "cmd": cmd,
            "stderr": "invalid json from jules_bridge",
            "raw": p.stdout,
        }


def get_default_repo() -> str:
    """Auto-detect GitHub repo from git remote origin URL"""
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"], capture_output=True, text=True
        )
        if r.returncode == 0:
            url = r.stdout.strip()
            if "github.com" in url:
                if url.startswith("git@"):
                    repo = url.split(":")[-1]
                elif url.startswith("https://"):
                    repo = url.split("github.com/")[-1]
                else:
                    return "."
                if repo.endswith(".git"):
                    repo = repo[:-4]
                return repo
    except Exception:
        pass
    return "."


def get_default_branch() -> str | None:
    """Auto-detect remote HEAD branch or current branch. Blocks if neither found."""
    try:
        r = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            return r.stdout.strip().split("/")[-1]

        r = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    # Do NOT guess "main" — wrong branch causes queued -> FAILED (P11)
    return None


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Dispatch a Jules prompt pack with GATE-1/2/3 safety checks."
    )
    ap.add_argument("--pack-dir", required=True, help="Path to .../jules_pack")
    ap.add_argument(
        "--repo", default=get_default_repo(), help="Auto-detected from git origin"
    )
    ap.add_argument(
        "--starting-branch", default=get_default_branch(), help="Auto-detected from git"
    )
    ap.add_argument("--require-plan-approval", action="store_true")
    ap.add_argument("--automation-mode", default="AUTO_CREATE_PR")
    ap.add_argument(
        "--skip-smoke",
        action="store_true",
        help="Skip GATE-3 smoke test (use for re-runs after partial batch)",
    )
    ap.add_argument(
        "--max-batch",
        type=int,
        default=50,
        help="GATE-4: max tasks per dispatch (default 50, prevents mass submission)",
    )
    ap.add_argument(
        "--no-cache",
        action="store_true",
        help="Clear idempotency records for pending tasks before submission",
    )
    ap.add_argument(
        "--allow-cli-batch",
        action="store_true",
        help="Allow dispatching multiple tasks without JULES_API_KEY (WARNING: session reuse risk)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    # Validate starting-branch (get_default_branch returns None if undetectable)
    if args.starting_branch is None:
        raise SystemExit(
            "Cannot auto-detect default branch.\n"
            "Specify --starting-branch explicitly (e.g. --starting-branch master).\n"
            "Guessing 'main' is disabled because wrong branch causes silent FAILED sessions."
        )

    tasks_dir = os.path.join(args.pack_dir, "tasks")
    if not os.path.isdir(tasks_dir):
        raise SystemExit(f"tasks/ not found: {tasks_dir}")

    # Set pack dir for HYDRATE relative path fallback
    os.environ["_JULES_PACK_DIR"] = os.path.abspath(args.pack_dir)

    # ---- GATE-1: Only submit pending tasks from PACK.md ----
    pending_list, pending_ids = parse_pending_tasks(args.pack_dir)
    task_files = filter_task_files(tasks_dir, pending_ids)

    # ---- GATE-FNAME: Enforce unique 1:1 task_id → file mapping ----
    id_to_file = gate_fname_unique_mapping(task_files, pending_list)
    # Reorder task_files to match PACK.md row order (deterministic)
    task_files = list(id_to_file.values())

    # ---- --no-cache: Clear idempotency records for pending tasks ----
    if args.no_cache:
        state_dir = os.path.join(".runtime", "jules", "dispatch")
        if os.path.isdir(state_dir):
            cleared = 0
            for f in os.listdir(state_dir):
                if f.endswith(".json"):
                    os.remove(os.path.join(state_dir, f))
                    cleared += 1
            if cleared:
                eprint(
                    f"--no-cache: Cleared {cleared} idempotency records from {state_dir}"
                )
        else:
            eprint("--no-cache: No idempotency records found (clean state)")

    # ---- GATE-4: Batch size limit ----
    if len(task_files) > args.max_batch:
        raise SystemExit(
            f"GATE-4 BLOCKED: {len(task_files)} pending tasks exceed batch limit of {args.max_batch}.\n"
            f"Pending tasks: {', '.join(os.path.basename(f) for f in task_files)}\n"
            f"\n"
            f"Options to proceed:\n"
            f"  1. Increase limit:  --max-batch {len(task_files)}\n"
            f"  2. Reduce scope:    Mark some tasks as 'queued' (not 'pending') in PACK.md\n"
            f"  3. Split into waves: Set only the first {args.max_batch} tasks to 'pending',\n"
            f"     dispatch, then update PACK.md for the next wave.\n"
            f"\n"
            f"This limit exists to prevent accidental mass submission (see P10)."
        )
    eprint(
        f"GATE-4 PASSED: {len(task_files)} tasks within batch limit of {args.max_batch}"
    )

    # ---- GATE-UTF8: Strict encoding check (before any file processing) ----
    task_files = ensure_utf8_strict(args.pack_dir, task_files)

    # ---- GATE-2: Ensure ASCII-safe paths (and strip BOM natively) ----
    task_files = ensure_ascii_paths(task_files)

    # ---- GATE-CLI-BATCH: Prevent ghost session reuse for multi-task runs in CLI mode ----
    api_key = os.environ.get("JULES_API_KEY", "").strip()
    if not api_key:
        if len(task_files) > 1 and not args.allow_cli_batch:
            raise SystemExit(
                f"GATE-CLI-BATCH BLOCKED: Attempting to submit {len(task_files)} tasks in CLI mode.\n"
                "Without JULES_API_KEY (or key is empty), the bridge will guess the session_id, "
                "which often causes all tasks to merge into the SAME session (Pitfall P2/P14).\n"
                "Fix:\n"
                '  1. Export JULES_API_KEY="your-key" (recommended)\n'
                "  2. Or use --allow-cli-batch to proceed anyway at your own risk"
            )
        eprint("GATE-CLI-BATCH WARNING: Running in CLI mode (no JULES_API_KEY).")
    else:
        eprint("GATE-CLI-BATCH PASSED: JULES_API_KEY found, API mode active.")

    # ---- GATE-2b: Hydrate {{ HYDRATE: ... }} macros ----
    task_files = hydrate_prompt_files(task_files)

    # ---- GATE-HYDRATE-ERR: Reject if any HYDRATE macros failed ----
    for tf in task_files:
        content = open(tf, encoding="utf-8").read()
        if "<!-- HYDRATE ERROR:" in content:
            raise SystemExit(
                f"GATE-HYDRATE-ERR BLOCKED: {os.path.basename(tf)} contains failed HYDRATE macros.\n"
                "The Governance Capsule or other injected content may be missing/corrupt.\n"
                "Fix: Check the HYDRATE source file paths and encoding, then re-run."
            )

    # ---- GATE-6: Verify remote branch exists ----
    repo = args.repo
    branch = args.starting_branch
    if repo != "." and not repo.startswith("sources/"):
        gh_url = f"https://github.com/{repo}.git"
        try:
            ls = subprocess.run(
                ["git", "ls-remote", "--heads", gh_url, branch],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if ls.returncode != 0:
                raise SystemExit(
                    f"GATE-6 BLOCKED: Cannot reach remote repository {gh_url}\n"
                    f"  git ls-remote stderr: {ls.stderr.strip()}\n"
                    f"\n"
                    f"Check that the repo exists and you have access."
                )
            if not ls.stdout.strip():
                # List available branches for guidance
                ls_all = subprocess.run(
                    ["git", "ls-remote", "--heads", gh_url],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                branches = [
                    line.split("refs/heads/")[-1]
                    for line in ls_all.stdout.strip().splitlines()
                    if "refs/heads/" in line
                ]
                raise SystemExit(
                    f"GATE-6 BLOCKED: Branch '{branch}' not found in {repo}\n"
                    "\n"
                    f"Available branches: {', '.join(branches[:10])}\n"
                    "\n"
                    "Fix: use --starting-branch <correct_branch>\n"
                    "This repo likely uses 'master' instead of 'main'."
                )
            eprint(f"GATE-6 PASSED: Branch '{branch}' exists in {repo}")
        except subprocess.TimeoutExpired:
            raise SystemExit(
                f"GATE-6 BLOCKED: git ls-remote timed out for branch '{branch}'.\n"
                "Fix: Check network/proxy, increase timeout, or verify branch manually.\n"
                "Timeout is set to 15s. On slow networks, retry after checking connectivity."
            )

    # ---- GATE-7: Governance Capsule Validation ----
    gate7_failures = []
    for tf in task_files:
        try:
            content = open(tf, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            gate7_failures.append(f"  {os.path.basename(tf)}: cannot read file")
            continue
        missing = []
        if "Governance Capsule" not in content:
            missing.append("## Governance Capsule")
        if "Document Placement" not in content:
            missing.append("## Document Placement")
        if missing:
            gate7_failures.append(
                f"  {os.path.basename(tf)}: missing {', '.join(missing)}"
            )
    if gate7_failures:
        raise SystemExit(
            "GATE-7 BLOCKED: Governance Capsule / Document Placement missing\n"
            "\n" + "\n".join(gate7_failures) + "\n\n"
            "Fix: Add §4.5 Governance Capsule (with HYDRATE macros) and §4 Document\n"
            "Placement to each task file. See prompt-envelope-review.md / implement.md."
        )
    eprint(
        f"GATE-7 PASSED: All {len(task_files)} tasks have Governance Capsule + Placement"
    )

    # ---- GATE-FFFD: Reject if any replacement chars leaked through ----
    check_no_replacement_chars(task_files)

    # ---- GATE-TASKID-CONTENT: file header task_id must match filename prefix ----
    taskid_failures = []
    for tf in task_files:
        tid_from_name = extract_task_id_from_filename(tf)
        if not tid_from_name:
            continue
        try:
            first_lines = open(tf, encoding="utf-8").read(512)
        except (OSError, UnicodeDecodeError):
            continue
        m = re.search(r"task_id:\s*(TASK-[\w-]+)", first_lines, re.IGNORECASE)
        if m:
            tid_from_content = m.group(1).upper()
            if tid_from_content != tid_from_name:
                taskid_failures.append(
                    f"  {os.path.basename(tf)}: header task_id='{tid_from_content}' "
                    f"!= filename prefix '{tid_from_name}'"
                )
    if taskid_failures:
        raise SystemExit(
            "GATE-TASKID BLOCKED: task_id in file header does not match filename prefix\n\n"
            + "\n".join(taskid_failures)
            + "\n\nFix: ensure the 'task_id:' YAML field matches the filename TASK-XXX prefix."
        )
    if task_files:
        eprint("GATE-TASKID PASSED: all task_id headers match filename prefixes")

    bridge_py = os.path.join(os.path.dirname(__file__), "jules_bridge.py")

    def build_cmd(tf: str) -> List[str]:
        # title = task_id (canonical, not filename stem) for stable cross-system tracking
        tid = (
            extract_task_id_from_filename(tf)
            or os.path.splitext(os.path.basename(tf))[0]
        )
        cmd = [
            sys.executable,
            bridge_py,
            "--repo",
            args.repo,
            "--starting-branch",
            args.starting_branch,
            "--automation-mode",
            args.automation_mode,
        ]
        if args.require_plan_approval:
            cmd.append("--require-plan-approval")
        cmd += ["--json", "submit", "--title", tid, "--prompt-file", tf]
        return cmd

    # ---- GATE-3: Smoke test first task ----
    smoke_result = None
    if not args.skip_smoke:
        smoke_result = smoke_test_first(task_files, build_cmd)
        # First task already submitted by smoke test; start from index 1
        remaining = task_files[1:]
    else:
        eprint("GATE-3: Skipped (--skip-smoke)")
        remaining = task_files

    # ---- Dispatch remaining tasks ----
    results: List[Dict[str, Any]] = []

    # Reuse smoke test result directly (no re-invocation)
    if smoke_result is not None:
        results.append(smoke_result)

    for tf in remaining:
        eprint(f"Submitting: {os.path.basename(tf)}")
        results.append(run_bridge(build_cmd(tf)))
        time.sleep(
            5
        )  # Rate limit: 5s delay prevents API 429 (matches P9 recommendation)

    # ---- GATE-5: Post-dispatch reconciliation (planned vs actual) ----
    planned = {os.path.splitext(os.path.basename(f))[0] for f in task_files}
    succeeded = set()
    failed_tasks = []
    for i, r in enumerate(results):
        task_name = os.path.splitext(os.path.basename(task_files[i]))[0]
        if r.get("ok") and r.get("state") != "FAILED":
            succeeded.add(task_name)
        else:
            failed_tasks.append((task_name, r.get("stderr", r.get("state", "unknown"))))

    missing = planned - succeeded
    extra = succeeded - planned

    if missing or extra or failed_tasks:
        eprint("\n=== GATE-5 FAILED: Planned vs Actual mismatch ===")
        if failed_tasks:
            eprint(f"  FAILED tasks ({len(failed_tasks)}):")
            for name, reason in failed_tasks:
                eprint(f"    - {name}: {reason}")
        if missing:
            eprint(
                f"  MISSING (planned but not submitted): {', '.join(sorted(missing))}"
            )
        if extra:
            eprint(f"  EXTRA (submitted but not planned): {', '.join(sorted(extra))}")
        eprint(f"\n  Planned: {', '.join(sorted(planned))}")
        eprint(f"  Succeeded: {', '.join(sorted(succeeded))}")

        if args.json:
            print(json.dumps(results, ensure_ascii=False))
        else:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    eprint(f"\n=== GATE-5 PASSED: {len(succeeded)}/{len(planned)} tasks reconciled ===")
    eprint(
        f"=== DISPATCH COMPLETE: {len(succeeded)} ok / 0 failed / {len(results)} total ==="
    )

    if args.json:
        print(json.dumps(results, ensure_ascii=False))
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
