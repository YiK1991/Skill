#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Doc Gate V3+ - 文档门禁工具

功能：检查代码变更是否伴随必要的文档变更；输出布尔值。

触发规则（默认策略）：
1) TEST_PLAN.md 变更 -> 必须伴随 docs/changes/** 变更
2) 跨层变更 (domain/ + infra.../ 等) -> 必须新增 docs/decisions/ADR-*.md
3) 对外接口变更（api/routes/...） -> 必须更新 docs/api/** 或 docs/changes/**

输出：
- stdout: "true\n" / "false\n"
- stderr: 失败原因 + 相关文件列表

用法：
  python3 scripts/doc_gate.py --base origin/main --strict
  python3 scripts/doc_gate.py --base HEAD~1 --strict
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple

# === Circuit Breaker (optional, disabled by default) ===
# Enable: PDCA_GATE_MAX_RETRIES=3
# State:  PDCA_GATE_STATE_PATH=.pdca/gate_state.json (default)
# TTL:    PDCA_GATE_TTL_SEC=1800 (default 30 min; 0 = no expiry)
_MAX_RETRIES = int(os.environ.get("PDCA_GATE_MAX_RETRIES", "0"))
_STATE_PATH = Path(os.environ.get("PDCA_GATE_STATE_PATH", ".pdca/gate_state.json"))
_TTL_SEC = int(os.environ.get("PDCA_GATE_TTL_SEC", "1800"))


def _error_signature(errors: List[str]) -> str:
    """Deterministic hash of error messages to detect same-root-cause."""
    content = "\n".join(sorted(errors))
    content = re.sub(r"\s@\sL\d+:", " @ L_XX:", content)
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _load_breaker_state() -> dict:
    if _STATE_PATH.exists():
        try:
            return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_breaker_state(state: dict) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(_STATE_PATH)


def _finalize_gate(
    gate_name: str,
    passed: bool,
    errors: List[str],
    env_error: bool = False,
) -> int:
    """Unified exit point with optional circuit breaker."""
    for e in errors:
        print(e, file=sys.stderr)

    if passed:
        if _MAX_RETRIES > 0:
            state = _load_breaker_state()
            if gate_name in state:
                del state[gate_name]
                if state:
                    _save_breaker_state(state)
                elif _STATE_PATH.exists():
                    _STATE_PATH.unlink()
        sys.stdout.write("true\n")
        return 0

    if env_error:
        print(
            f"[ENV_ERROR] {gate_name}: environment/infrastructure failure — do NOT self-repair",
            file=sys.stderr,
        )
        sys.stdout.write("false\n")
        return 2 if _MAX_RETRIES > 0 else 1

    if _MAX_RETRIES > 0:
        import time

        now = time.time()
        sig = _error_signature(errors)
        state = _load_breaker_state()
        entry = state.get(gate_name, {})

        # TTL check: if entry is stale, reset
        if _TTL_SEC > 0 and entry.get("ts", 0) + _TTL_SEC < now:
            entry = {"sig": sig, "count": 1, "ts": now}
        elif entry.get("sig") == sig:
            entry["count"] = entry.get("count", 0) + 1
            entry["ts"] = now
        else:
            entry = {"sig": sig, "count": 1, "ts": now}

        state[gate_name] = entry
        _save_breaker_state(state)

        if entry["count"] >= _MAX_RETRIES:
            print(
                f"[CIRCUIT_BREAKER] {gate_name}: same-root-cause failure {entry['count']}/{_MAX_RETRIES} — human-in-the-loop required",
                file=sys.stderr,
            )
            sys.stdout.write("false\n")
            return 2

    sys.stdout.write("false\n")
    return 1


@dataclass(frozen=True)
class Change:
    status: str  # e.g. A, M, D, R100
    path: str

    @property
    def is_added(self) -> bool:
        return self.status.startswith("A")


def run_git(args: Sequence[str], strict: bool) -> Tuple[Optional[str], str]:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
        return r.stdout, ""
    except subprocess.CalledProcessError as e:
        msg = (e.stderr or "").strip() or f"git {' '.join(args)} failed"
        if strict:
            return None, msg
        return "", msg
    except (FileNotFoundError, PermissionError, OSError) as e:
        return None, f"[ENV] {e}"


def get_merge_base(base: str, strict: bool) -> Tuple[Optional[str], str]:
    out, err = run_git(["merge-base", "HEAD", base], strict=strict)
    if out is None:
        return None, err
    sha = out.strip()
    return sha or None, err


def parse_name_status(raw: str) -> List[Change]:
    changes: List[Change] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # name-status: "M\tpath" or "R100\told\tnew"
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0]
            path = parts[-1]  # for rename, take new path
            changes.append(Change(status=status, path=path))
    return changes


def get_changes(base: str, strict: bool) -> Tuple[Optional[List[Change]], str, str]:
    merge_base, mb_err = get_merge_base(base, strict=strict)
    diff_base = merge_base or base

    raw, diff_err = run_git(["diff", "--name-status", diff_base], strict=strict)
    if raw is None:
        return None, (mb_err or diff_err), diff_base

    changes = parse_name_status(raw)
    msg = mb_err or diff_err
    return changes, msg, diff_base


def check_test_plan_changes(changed_paths: Set[str]) -> Tuple[bool, str]:
    test_plan_pattern = re.compile(r"(^|/)TEST_PLAN\.md$")
    if not any(test_plan_pattern.search(p) for p in changed_paths):
        return True, ""

    if any(p.startswith("docs/changes/") for p in changed_paths):
        return True, ""

    return False, "TEST_PLAN.md 变更必须伴随 docs/changes/** 变更"


def detect_layers(path: str) -> Set[str]:
    # 仅按路径段识别，减少误判（避免 substring 命中）
    layers = {
        "domain",
        "infra",
        "infrastructure",
        "application",
        "interface",
        "ui",
    }
    touched = set()
    parts = Path(path).parts
    for part in parts:
        p = part.lower()
        if p in layers:
            touched.add(p)
    return touched


def check_cross_layer(changes: List[Change]) -> Tuple[bool, str]:
    touched_layers: Set[str] = set()
    for c in changes:
        touched_layers |= detect_layers(c.path)

    if len(touched_layers) < 2:
        return True, ""

    adr_added = any(
        c.is_added
        and c.path.startswith("docs/decisions/")
        and re.search(r"ADR-.*\.md$", c.path, flags=re.IGNORECASE)
        for c in changes
    )

    if adr_added:
        return True, ""

    return (
        False,
        f"跨层变更 ({sorted(touched_layers)}) 必须新增 docs/decisions/ADR-*.md",
    )


def check_api_changes(changed_paths: Set[str]) -> Tuple[bool, str]:
    api_dirs = {"api", "routes", "endpoints", "handlers"}

    def is_api_path(p: str) -> bool:
        parts = [x.lower() for x in Path(p).parts]
        return any(seg in api_dirs for seg in parts)

    api_changed = any(is_api_path(p) for p in changed_paths)
    if not api_changed:
        return True, ""

    docs_updated = any(
        p.startswith("docs/api/") or p.startswith("docs/changes/")
        for p in changed_paths
    )
    if docs_updated:
        return True, ""

    return False, "API 变更必须更新 docs/api/** 或 docs/changes/**"


def _resolve_base(requested: str) -> str:
    """Auto-detect base branch if requested=='auto'."""
    if requested != "auto":
        return requested
    candidates = ["origin/main", "origin/master", "main", "master"]
    for ref in candidates:
        try:
            subprocess.run(
                ["git", "rev-parse", "--verify", ref],
                capture_output=True,
                check=True,
            )
            return ref
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            continue
    return "HEAD~1"


def main() -> int:
    ap = argparse.ArgumentParser(description="Doc Gate V3+ - 文档门禁工具")
    ap.add_argument(
        "--base", default="auto", help="比较基准分支/SHA (default: auto-detect)"
    )
    ap.add_argument(
        "--strict", action="store_true", help="严格模式 (git/diff 失败即失败)"
    )
    args = ap.parse_args()
    args.base = _resolve_base(args.base)

    changes, warn_or_err, diff_base = get_changes(args.base, strict=args.strict)

    if changes is None:
        return _finalize_gate(
            "gate_d", False, [f"[ERROR] {warn_or_err}"], env_error=True
        )

    if warn_or_err:
        print(f"[WARN] {warn_or_err}", file=sys.stderr)

    if not changes:
        print("[INFO] No changes detected", file=sys.stderr)
        sys.stdout.write("true\n")
        return 0

    changed_paths = {c.path for c in changes}

    all_passed = True
    errors: List[str] = []

    checks = [
        check_test_plan_changes(changed_paths),
        check_cross_layer(changes),
        check_api_changes(changed_paths),
    ]

    for passed, msg in checks:
        if not passed:
            all_passed = False
            errors.append(msg)

    if not all_passed:
        errors.insert(
            0, f"[FAIL] Doc Gate failed (base={args.base}, diff_base={diff_base})"
        )
        errors.append("[FAIL] Changed files:")
        for c in sorted(changes, key=lambda x: x.path):
            errors.append(f"  - {c.status}\t{c.path}")
    else:
        print(
            f"[PASS] Doc Gate 通过 (base={args.base}, diff_base={diff_base})",
            file=sys.stderr,
        )

    return _finalize_gate("gate_d", all_passed, errors)


if __name__ == "__main__":
    raise SystemExit(main())
