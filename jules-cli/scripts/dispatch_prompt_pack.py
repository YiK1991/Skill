#!/usr/bin/env python3
"""Dispatch a Prompt Pack (tasks/*.md) via jules_bridge.

Three hard gates block submission before any API call is made:

  GATE-1 (Status Filter): Only tasks marked `pending` in PACK.md are submitted.
         If PACK.md is missing or has no pending tasks, abort.
  GATE-2 (ASCII Path):    All file paths passed to jules_bridge must be ASCII-only.
         If the pack-dir contains non-ASCII characters, task files are transparently
         copied to a temp directory under an ASCII-safe path before dispatch.
  GATE-3 (Smoke Test):    The FIRST pending task is submitted alone. Only if it
         succeeds (returns ok=true) are the remaining tasks dispatched.
  GATE-4 (Batch Limit):   Default max 5 tasks per dispatch. Override with --max-batch N.
         Prevents accidental mass submission.
         Use --skip-smoke to bypass (e.g., re-runs after a partial batch).

Example:
  python scripts/dispatch_prompt_pack.py \\
    --pack-dir 00_Documentation/99_Inbox/<module>/jules_pack \\
    --repo YiK1991/Amazon_SaaS_ERP \\
    --starting-branch master \\
    --json

Output:
  JSON array of per-task submit payloads.
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
from typing import Any, Dict, List, Set

# --------------- Encoding: force UTF-8 on Windows (GBK default) ---------------
if sys.platform == "win32":
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name)
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")


# ========================== GATE-1: PACK.md Status Filter ==========================


def parse_pending_tasks(pack_dir: str) -> Set[str]:
    """Parse PACK.md and return set of task_ids whose status is 'pending'.

    Returns empty set if PACK.md is missing or has no task table.
    Raises SystemExit if PACK.md exists but has zero pending tasks (safety).
    """
    pack_md = os.path.join(pack_dir, "PACK.md")
    if not os.path.isfile(pack_md):
        raise SystemExit(
            f"GATE-1 BLOCKED: PACK.md not found at {pack_md}.\n"
            "Every pack MUST have a PACK.md with a task table. "
            "Cannot determine which tasks to submit without it."
        )

    with open(pack_md, encoding="utf-8") as f:
        content = f.read()

    # Parse markdown table rows: | TASK-XXX | ... | pending | ...
    pending: Set[str] = set()
    all_tasks: Set[str] = set()
    for line in content.splitlines():
        # Match table rows like: | TASK-017 | description | aspect | pending | ...
        m = re.match(r"\|\s*(TASK-[\w\-]+)\s*\|", line)
        if not m:
            continue
        task_id = m.group(1)
        all_tasks.add(task_id)
        # Check if any cell in this row contains 'pending' (case-insensitive)
        cells = [c.strip().lower() for c in line.split("|")]
        if "pending" in cells:
            pending.add(task_id)

    if not all_tasks:
        raise SystemExit(
            "GATE-1 BLOCKED: PACK.md has no task table rows (expected | TASK-XXX | ... |).\n"
            "Add tasks to the table before dispatching."
        )

    if not pending:
        raise SystemExit(
            f"GATE-1 BLOCKED: PACK.md has {len(all_tasks)} tasks but NONE are 'pending'.\n"
            f"Found statuses: {', '.join(sorted(all_tasks))} — all non-pending.\n"
            "Mark tasks as 'pending' in PACK.md before dispatching."
        )

    return pending


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
    return matched


# ========================== GATE-2: ASCII Path Enforcement ==========================


def is_ascii_safe(path: str) -> bool:
    """Check if path contains only ASCII characters."""
    try:
        path.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def ensure_ascii_paths(task_files: List[str]) -> List[str]:
    """If any task file path has non-ASCII chars, copy ALL to an ASCII-safe temp dir.

    Returns the (potentially relocated) list of file paths.
    """
    if all(is_ascii_safe(f) for f in task_files):
        eprint("GATE-2 PASSED: All paths are ASCII-safe")
        return task_files

    # Create isolated PID-scoped temp directory (prevents concurrent collision)
    temp_dir = os.path.join(tempfile.gettempdir(), f"jules_dispatch_{os.getpid()}")
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    relocated: List[str] = []
    for src in task_files:
        fname = os.path.basename(src)
        dst = os.path.join(temp_dir, fname)
        shutil.copy2(src, dst)
        relocated.append(dst)

    eprint(
        f"GATE-2 PASSED: Copied {len(relocated)} files to ASCII-safe path: {temp_dir}"
    )
    return relocated


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
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
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


def get_default_branch() -> str:
    """Auto-detect remote HEAD branch or fallback to current branch"""
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
    return "main"


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
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    tasks_dir = os.path.join(args.pack_dir, "tasks")
    if not os.path.isdir(tasks_dir):
        raise SystemExit(f"tasks/ not found: {tasks_dir}")

    # ---- GATE-1: Only submit pending tasks from PACK.md ----
    pending_ids = parse_pending_tasks(args.pack_dir)
    task_files = filter_task_files(tasks_dir, pending_ids)

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

    # ---- GATE-2: Ensure ASCII-safe paths ----
    task_files = ensure_ascii_paths(task_files)

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
            eprint(f"GATE-6 SKIPPED: git ls-remote timed out (proceeding anyway)")

    bridge_py = os.path.join(os.path.dirname(__file__), "jules_bridge.py")

    def build_cmd(tf: str) -> List[str]:
        base = os.path.basename(tf)
        title = os.path.splitext(base)[0]
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
        cmd += ["--json", "submit", "--title", title, "--prompt-file", tf]
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
        time.sleep(3)  # Rate limit: prevent API 429 (matches P9 .bat timeout)

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
