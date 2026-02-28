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
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple


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

    return False, f"跨层变更 ({sorted(touched_layers)}) 必须新增 docs/decisions/ADR-*.md"


def check_api_changes(changed_paths: Set[str]) -> Tuple[bool, str]:
    api_dirs = {"api", "routes", "endpoints", "handlers"}

    def is_api_path(p: str) -> bool:
        parts = [x.lower() for x in Path(p).parts]
        return any(seg in api_dirs for seg in parts)

    api_changed = any(is_api_path(p) for p in changed_paths)
    if not api_changed:
        return True, ""

    docs_updated = any(
        p.startswith("docs/api/") or p.startswith("docs/changes/") for p in changed_paths
    )
    if docs_updated:
        return True, ""

    return False, "API 变更必须更新 docs/api/** 或 docs/changes/**"


def main() -> int:
    ap = argparse.ArgumentParser(description="Doc Gate V3+ - 文档门禁工具")
    ap.add_argument("--base", default="origin/main", help="比较基准分支/SHA")
    ap.add_argument("--strict", action="store_true", help="严格模式 (git/diff 失败即失败)")
    args = ap.parse_args()

    changes, warn_or_err, diff_base = get_changes(args.base, strict=args.strict)

    if changes is None:
        print(f"[ERROR] {warn_or_err}", file=sys.stderr)
        sys.stdout.write("false\n")
        return 1

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
        print(f"[FAIL] Doc Gate failed (base={args.base}, diff_base={diff_base})", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("[FAIL] Changed files:", file=sys.stderr)
        for c in sorted(changes, key=lambda x: x.path):
            print(f"  - {c.status}\t{c.path}", file=sys.stderr)
    else:
        print(f"[PASS] Doc Gate 通过 (base={args.base}, diff_base={diff_base})", file=sys.stderr)

    sys.stdout.write("true\n" if all_passed else "false\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
