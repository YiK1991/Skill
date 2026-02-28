#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ATDD Gate V3+ - 验收测试门禁工具

功能：
1) Gate A (--parity-only): 清单↔测试名一致性校验 + 一对一约束 + 稳定ID强制 + 位置追溯
2) Gate B (--junit): JUnit 驱动校验 + (可选) 自动勾选 + 位置追溯
3) Gate C (--audit): Plan Change Audit（防隐式删题/偷换题）

输出：
- stdout: "true\n" 或 "false\n"（适合门禁）
- stderr: 详细失败原因（可追溯到 Plan 行号 / 测试文件与行号 / JUnit case）

支持配置（环境变量）：
- ATDD_MODE: strict(默认) / robust（规范化匹配 + 标点归一 + 空白归一）
- ATDD_USE_STABLE_ID: on(默认) / off
- ATDD_PARAM_TESTS: off(默认,一对一) / prefix（允许子例：ATDD-001 #case1）
- ATDD_STRICT_SKIPPED: fail(默认) / warn（仅非 --strict 时生效）

用法示例：
  # Gate A
  python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd --parity-only

  # Gate B (仅校验，无写入)
  python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd \
    --junit test-results/junit.xml --strict --dry-run

  # Gate B (勾选模式，带写入)
  python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd \
    --junit test-results/junit.xml --tick --strict

  # Gate C (审计：git 基准)
  python3 scripts/atdd_gate.py --plan TEST_PLAN.md --base origin/main --audit --strict

  # Gate C (审计：文件基准)
  python3 scripts/atdd_gate.py --plan TEST_PLAN.md --base-plan TEST_PLAN.md.bak --audit
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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
        # Reset breaker on success
        if _MAX_RETRIES > 0:
            state = _load_breaker_state()
            state.pop(gate_name, None)
            _save_breaker_state(state)
        sys.stdout.write("true\n")
        return 0

    # Environment errors: do not count toward retries, escalate immediately
    if env_error:
        print(
            f"[ENV_ERROR] {gate_name}: environment/infrastructure failure — do NOT self-repair",
            file=sys.stderr,
        )
        sys.stdout.write("false\n")
        return 2 if _MAX_RETRIES > 0 else 1

    # Circuit breaker logic
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


# === 配置项 ===
MODE = os.environ.get("ATDD_MODE", "strict")  # strict / robust
USE_STABLE_ID = os.environ.get("ATDD_USE_STABLE_ID", "on")  # on / off
PARAM_TESTS = os.environ.get("ATDD_PARAM_TESTS", "off")  # off / prefix
STRICT_SKIPPED = os.environ.get("ATDD_STRICT_SKIPPED", "fail")  # fail / warn

# === 正则表达式 ===
# 支持：
#   - [ ] ATDD-001 文本...
#   - [x] ATDD-001 文本...
#   - [-] ATDD-002 原文 CANCELLED(reason: ...)
#   - [>] ATDD-003 原文 REPLACED(by: ATDD-005)
PLAN_ITEM_RE = re.compile(
    r"^\s*-\s*\[(?P<status>[ xX\->])\]\s*"
    r"(?:(?P<id>ATDD-\d+)\s+)?"
    r"(?P<text>.*?)"
    r"(?:\s+(?P<cancelled>CANCELLED\([^)]+\))|\s+(?P<replaced>REPLACED\([^)]+\)))?\s*$"
)

ATDD_ID_RE = re.compile(r"(ATDD-\d+)")
REPLACED_BY_RE = re.compile(r"by:\s*(ATDD-\d+)")

# 测试名提取（尽量覆盖常见框架）
JS_TEST_RE = re.compile(r"\b(?:it|test)\(\s*([\'\"`])(?P<name>.+?)\1", re.DOTALL)
GO_TEST_RE = re.compile(r"\bt\.Run\(\s*\"(?P<name>[^\"]+)\"\s*,")
JUNIT_DISPLAYNAME_RE = re.compile(r"@DisplayName\(\s*\"(?P<name>[^\"]+)\"\s*\)")
PY_DOCSTRING_RE = re.compile(
    r"^\s*def\s+test_[a-zA-Z0-9_]+\s*\(.*?\)\s*:\s*\n\s*(?P<q>\"\"\"|\'\'\')(?P<name>.*?)(?P=q)",
    re.DOTALL | re.MULTILINE,
)

DEFAULT_GLOBS = [
    "**/*.test.ts",
    "**/*.test.js",
    "**/*.spec.ts",
    "**/*.spec.js",
    "**/test_*.py",
    "**/*_test.go",
    "**/*.java",
    "**/*.kt",
]

PUNCTUATION_MAP = {
    "，": ",",
    "。": ".",
    "：": ":",
    "；": ";",
    "！": "!",
    "？": "?",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "「": '"',
    "」": '"',
    "　": " ",
}


def normalize(text: str) -> str:
    text = (text or "").strip()
    if MODE != "robust":
        return text

    text = re.sub(r"\s+", " ", text)
    for full, half in PUNCTUATION_MAP.items():
        text = text.replace(full, half)
    return text


def extract_atdd_id(text: str) -> Optional[str]:
    m = ATDD_ID_RE.search((text or "").strip())
    return m.group(1) if m else None


def get_item_key(item_id: Optional[str], item_text: str) -> str:
    if USE_STABLE_ID == "on" and item_id:
        return item_id
    return normalize(item_text)


def get_test_key(test_name: str) -> str:
    test_name = normalize(test_name)

    if USE_STABLE_ID == "on":
        tid = extract_atdd_id(test_name)
        if tid:
            return tid  # stable id 永远按 id 聚合/对账

    if PARAM_TESTS == "prefix":
        parts = re.split(r"\s*#\s*", test_name, maxsplit=1)
        return normalize(parts[0])

    return test_name


@dataclass(frozen=True)
class TestOccurrence:
    name: str
    path: str
    line: int


class PlanItem:
    def __init__(
        self,
        status: str,
        item_id: Optional[str],
        text: str,
        line_no: int,
        raw_line: str,
        cancelled: Optional[str] = None,
        replaced: Optional[str] = None,
    ):
        self.status = status
        self.item_id = item_id
        self.text = text
        self.line_no = line_no
        self.raw_line = raw_line
        self.cancelled = cancelled
        self.replaced = replaced

        if self.is_active:
            self.key = get_item_key(item_id, text)
        else:
            self.key = None

    @property
    def is_active(self) -> bool:
        return (
            (self.status not in ["-", ">"])
            and (not self.cancelled)
            and (not self.replaced)
        )

    def label(self) -> str:
        if self.item_id:
            return f"{self.item_id} {self.text}".strip()
        return self.text.strip()


def _line_no_from_pos(text: str, pos: int) -> int:
    # 1-based
    return text.count("\n", 0, max(pos, 0)) + 1


def read_plan_items(plan_path: Path) -> List[PlanItem]:
    items: List[PlanItem] = []
    for idx, line in enumerate(
        plan_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        m = PLAN_ITEM_RE.match(line)
        if not m:
            continue
        items.append(
            PlanItem(
                status=m.group("status") or " ",
                item_id=m.group("id"),
                text=(m.group("text") or "").strip(),
                line_no=idx,
                raw_line=line,
                cancelled=m.group("cancelled"),
                replaced=m.group("replaced"),
            )
        )
    return items


def read_plan_from_git(base: str, plan_file: str) -> Optional[List[PlanItem]]:
    try:
        mb = subprocess.run(
            ["git", "merge-base", "HEAD", base],
            capture_output=True,
            text=True,
            check=True,
        )
        merge_base = mb.stdout.strip()
        show = subprocess.run(
            ["git", "show", f"{merge_base}:{plan_file}"],
            capture_output=True,
            text=True,
            check=True,
        )

        items: List[PlanItem] = []
        for idx, line in enumerate(show.stdout.splitlines(), start=1):
            m = PLAN_ITEM_RE.match(line)
            if not m:
                continue
            items.append(
                PlanItem(
                    status=m.group("status") or " ",
                    item_id=m.group("id"),
                    text=(m.group("text") or "").strip(),
                    line_no=idx,
                    raw_line=line,
                    cancelled=m.group("cancelled"),
                    replaced=m.group("replaced"),
                )
            )
        return items
    except subprocess.CalledProcessError:
        return None


def read_manifest(manifest_path: Path) -> List[str]:
    if not manifest_path.exists():
        return []
    names: List[str] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            names.append(s)
    return names


def extract_test_occurrences(
    tests_root: Path, globs_list: List[str]
) -> List[TestOccurrence]:
    occs: List[TestOccurrence] = []
    for pattern in globs_list:
        for p in tests_root.glob(pattern):
            if p.is_dir():
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            suffix = p.suffix.lower()
            if suffix in (".js", ".ts"):
                for m in JS_TEST_RE.finditer(content):
                    name = (m.group("name") or "").strip()
                    if not name:
                        continue
                    occs.append(
                        TestOccurrence(
                            name=name,
                            path=str(p),
                            line=_line_no_from_pos(content, m.start()),
                        )
                    )
            elif suffix == ".go":
                for m in GO_TEST_RE.finditer(content):
                    name = (m.group("name") or "").strip()
                    if not name:
                        continue
                    occs.append(
                        TestOccurrence(
                            name=name,
                            path=str(p),
                            line=_line_no_from_pos(content, m.start()),
                        )
                    )
            elif suffix in (".java", ".kt"):
                for m in JUNIT_DISPLAYNAME_RE.finditer(content):
                    name = (m.group("name") or "").strip()
                    if not name:
                        continue
                    occs.append(
                        TestOccurrence(
                            name=name,
                            path=str(p),
                            line=_line_no_from_pos(content, m.start()),
                        )
                    )
            elif suffix == ".py":
                for m in PY_DOCSTRING_RE.finditer(content):
                    name = (m.group("name") or "").strip()
                    if not name:
                        continue
                    occs.append(
                        TestOccurrence(
                            name=name,
                            path=str(p),
                            line=_line_no_from_pos(content, m.start()),
                        )
                    )

    return occs


def build_test_key_index(occs: List[TestOccurrence]) -> Dict[str, List[TestOccurrence]]:
    idx: Dict[str, List[TestOccurrence]] = {}
    for oc in occs:
        key = get_test_key(oc.name)
        idx.setdefault(key, []).append(oc)
    return idx


def parse_junit(junit_path: Path) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    if not junit_path.exists():
        raise FileNotFoundError(f"JUnit XML not found: {junit_path}")

    tree = ET.parse(str(junit_path))
    root = tree.getroot()

    status_by_key: Dict[str, str] = {}
    cases_by_key: Dict[str, List[str]] = {}

    for tc in root.iter("testcase"):
        name = (tc.attrib.get("name") or "").strip()
        if not name:
            continue

        atdd_id = None
        props = tc.find("properties")
        if props is not None:
            for prop in props.findall("property"):
                if prop.attrib.get("name") == "atdd_id":
                    atdd_id = prop.attrib.get("value")
                    break

        key = atdd_id if atdd_id else get_test_key(name)

        status = "pass"
        if tc.find("failure") is not None:
            status = "fail"
        elif tc.find("error") is not None:
            status = "error"
        elif tc.find("skipped") is not None:
            status = "skipped"

        cases_by_key.setdefault(key, []).append(name)

        prev = status_by_key.get(key)
        if prev is None:
            status_by_key[key] = status
        else:
            order = {"pass": 0, "skipped": 1, "fail": 2, "error": 3}
            if order.get(status, 0) > order.get(prev, 0):
                status_by_key[key] = status

    return status_by_key, cases_by_key


def update_plan(plan_path: Path, passed_keys: Set[str], reset: bool) -> None:
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    out: List[str] = []

    for line in lines:
        m = PLAN_ITEM_RE.match(line)
        if not m:
            out.append(line)
            continue

        status = m.group("status") or " "
        item_id = m.group("id")
        text = (m.group("text") or "").strip()
        cancelled = m.group("cancelled")
        replaced = m.group("replaced")

        # 非 active 条目不应被 tick/reset
        is_active = (status not in ["-", ">"]) and (not cancelled) and (not replaced)
        if not is_active:
            out.append(line)
            continue

        key = get_item_key(item_id, text)
        if key in passed_keys:
            out.append(re.sub(r"\[\s*\]", "[x]", line, count=1))
        else:
            if reset:
                out.append(re.sub(r"\[[xX]\]", "[ ]", line, count=1))
            else:
                out.append(line)

    plan_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def gate_a_parity(
    plan_items: List[PlanItem], test_index: Dict[str, List[TestOccurrence]]
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    # Plan active items + duplicates
    active = [it for it in plan_items if it.is_active and it.key]

    # Stable ID 强制
    if USE_STABLE_ID == "on":
        missing_id = [it for it in active if not it.item_id]
        if missing_id:
            errors.append(
                "[Stable ID 缺失] ATDD_USE_STABLE_ID=on 要求所有 active 条目包含 ATDD-xxx："
            )
            for it in missing_id[:10]:
                errors.append(f"  - L{it.line_no}: {it.raw_line.strip()}")
            if len(missing_id) > 10:
                errors.append(f"  ... 以及其他 {len(missing_id) - 10} 条")

    # Duplicate plan key
    from collections import Counter

    keys = [it.key for it in active if it.key]
    c = Counter(keys)
    dups = [(k, n) for k, n in c.items() if n > 1]
    if dups:
        errors.append(
            "[Plan 重复 Key] 清单内部存在重复键（同一 ATDD-xxx 或同一文本键）："
        )
        for k, n in sorted(dups):
            lines = [f"L{it.line_no}" for it in active if it.key == k]
            errors.append(f"  - {k}: {n} 次 ({', '.join(lines)})")

    plan_keys = set(keys)
    test_keys = set(test_index.keys())

    missing = plan_keys - test_keys
    extra = test_keys - plan_keys

    if missing:
        errors.append("[Missing Tests] 清单有但 tests/atdd 内未找到对应测试：")
        for k in sorted(missing):
            its = [it for it in active if it.key == k]
            for it in its:
                errors.append(f"  - {k} @ L{it.line_no}: {it.label()}")

    if extra:
        errors.append("[Extra Tests] tests/atdd 有但清单没有（范围漂移）：")
        for k in sorted(extra):
            occs = test_index.get(k, [])
            for oc in occs[:10]:
                errors.append(f"  - {k} @ {oc.path}:{oc.line}  name='{oc.name}'")
            if len(occs) > 10:
                errors.append(f"    ... 以及其他 {len(occs) - 10} 处")

    # 一对一约束
    if PARAM_TESTS == "off":
        violations = []
        for k in sorted(plan_keys):
            occs = test_index.get(k, [])
            if len(occs) > 1:
                violations.append((k, occs))
        if violations:
            errors.append(
                "[一对一违规] ATDD_PARAM_TESTS=off 要求每个条目恰好 1 个测试："
            )
            for k, occs in violations:
                errors.append(f"  - {k}: {len(occs)} 个测试")
                for oc in occs:
                    errors.append(f"      * {oc.path}:{oc.line}  name='{oc.name}'")

    return len(errors) == 0, errors


def gate_b_junit(
    plan_items: List[PlanItem],
    junit_status: Dict[str, str],
    junit_cases: Dict[str, List[str]],
    strict: bool,
) -> Tuple[bool, Set[str], List[str]]:
    errors: List[str] = []
    passed_keys: Set[str] = set()
    all_passed = True

    for it in plan_items:
        if not it.is_active or not it.key:
            continue

        st = junit_status.get(it.key)
        if st == "pass":
            passed_keys.add(it.key)
            continue

        # 非 pass 统一为未通过
        all_passed = False

        if st == "skipped":
            if strict or STRICT_SKIPPED == "fail":
                errors.append(f"[SKIPPED] {it.key} @ L{it.line_no}: {it.label()}")
            else:
                print(
                    f"[WARN] [SKIPPED] {it.key} @ L{it.line_no}: {it.label()}",
                    file=sys.stderr,
                )
        elif st in ("fail", "error"):
            errors.append(f"[{st.upper()}] {it.key} @ L{it.line_no}: {it.label()}")
        else:
            errors.append(f"[NOT_RUN] {it.key} @ L{it.line_no}: {it.label()}")

        cases = junit_cases.get(it.key, [])
        if cases:
            # 控制输出长度
            for cn in cases[:5]:
                errors.append(f"    - junit: {cn}")
            if len(cases) > 5:
                errors.append(f"    ... 以及其他 {len(cases) - 5} 个 case")

    return all_passed, passed_keys, errors


def gate_c_audit(
    current_items: List[PlanItem], base_items: List[PlanItem]
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    # 审计前提：active 必须有 ID
    for it in current_items:
        if it.is_active and not it.item_id:
            errors.append(
                f"[审计真空] current active 条目缺少 ATDD-ID @ L{it.line_no}: {it.raw_line.strip()}"
            )
    for it in base_items:
        if it.is_active and not it.item_id:
            errors.append(
                f"[审计真空] base active 条目缺少 ATDD-ID @ L{it.line_no}: {it.raw_line.strip()}"
            )

    if errors:
        errors.append(
            "[FATAL] Gate C 要求所有 active 条目必须包含 ATDD-ID，否则无法可靠审计"
        )
        return False, errors

    # 格式校验
    for it in current_items:
        if it.replaced:
            if not REPLACED_BY_RE.search(it.replaced):
                errors.append(
                    f"[格式错误] {it.item_id} @ L{it.line_no}: REPLACED 必须包含 'by: ATDD-xxx'"
                )
        if it.cancelled:
            if "reason:" not in it.cancelled.lower():
                errors.append(
                    f"[格式错误] {it.item_id} @ L{it.line_no}: CANCELLED 必须包含 'reason:'"
                )

    if errors:
        return False, errors

    base_active_ids = {it.item_id for it in base_items if it.is_active and it.item_id}

    current_active_ids = {
        it.item_id for it in current_items if it.is_active and it.item_id
    }
    current_cancelled_ids = {
        it.item_id for it in current_items if it.cancelled and it.item_id
    }
    current_replaced_old_ids = {
        it.item_id for it in current_items if it.replaced and it.item_id
    }

    # replaced targets
    replaced_targets: Dict[str, str] = {}
    for it in current_items:
        if it.replaced and it.item_id:
            m = REPLACED_BY_RE.search(it.replaced)
            if m:
                replaced_targets[it.item_id] = m.group(1)

    accounted = current_active_ids | current_cancelled_ids | current_replaced_old_ids
    missing = base_active_ids - accounted
    if missing:
        errors.append(
            "[隐式删除] 以下基准 active 条目消失但未标记 CANCELLED/REPLACED："
        )
        for mid in sorted(missing):
            errors.append(f"  - {mid}")

    invalid_targets = [
        (old, new)
        for old, new in replaced_targets.items()
        if new not in current_active_ids
    ]
    if invalid_targets:
        errors.append("[替换目标不存在或非 active]：")
        for old, new in sorted(invalid_targets):
            errors.append(f"  - {old} -> {new}")

    # CANCELLED/REPLACED 必须带旧 ID（按规则这里已满足，但保留防御）
    for it in current_items:
        if (it.cancelled or it.replaced) and not it.item_id:
            errors.append(
                "[缺少 ATDD-ID] CANCELLED/REPLACED 条目必须携带旧条目的 ATDD-ID"
            )

    return len(errors) == 0, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="ATDD Gate V3+")
    ap.add_argument("--plan", default="TEST_PLAN.md")
    ap.add_argument("--tests-root", default="tests/atdd")
    ap.add_argument("--glob", action="append", default=[])
    ap.add_argument(
        "--manifest", default="", help="测试名 manifest 文件（兜底；每行一个测试名）"
    )
    ap.add_argument("--junit", default="")
    ap.add_argument("--base-plan", default="", help="审计基准清单文件路径")
    ap.add_argument("--base", default="", help="git 基准（origin/main 等）")

    ap.add_argument("--parity-only", action="store_true")
    ap.add_argument("--tick", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--reset", action="store_true")

    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"[ERROR] Plan file not found: {plan_path}", file=sys.stderr)
        sys.stdout.write("false\n")
        return 1

    plan_items = read_plan_items(plan_path)
    tests_root = Path(args.tests_root)

    globs_list = args.glob if args.glob else DEFAULT_GLOBS

    occs: List[TestOccurrence] = []
    if tests_root.exists():
        occs = extract_test_occurrences(tests_root, globs_list)

    # manifest 兜底/补充
    if args.manifest:
        mf = Path(args.manifest)
        names = read_manifest(mf)
        if names:
            if not occs:
                # 无文件扫描结果时，manifest 作为唯一来源
                occs = [
                    TestOccurrence(name=n, path=str(mf), line=i + 1)
                    for i, n in enumerate(names)
                ]
                print(f"[INFO] 使用 manifest: {len(names)} 个测试名", file=sys.stderr)
            else:
                # 合并：避免一对一重复的假阳性，按 name 去重
                seen = {o.name for o in occs}
                add = [n for n in names if n not in seen]
                occs.extend(
                    TestOccurrence(name=n, path=str(mf), line=i + 1)
                    for i, n in enumerate(add)
                )
                print(f"[INFO] 合并 manifest: +{len(add)} 个新测试名", file=sys.stderr)

    test_index = build_test_key_index(occs)

    # Gate A
    if args.parity_only:
        passed, errors = gate_a_parity(plan_items, test_index)
        return _finalize_gate("gate_a", passed, errors)

    # Gate C
    if args.audit:
        base_items: Optional[List[PlanItem]] = None

        if args.base:
            base_items = read_plan_from_git(args.base, args.plan)
            if not base_items:
                msg = f"[ERROR] Failed to read plan from git base: {args.base}"
                print(msg, file=sys.stderr)
                if args.strict:
                    sys.stdout.write("false\n")
                    return 1

        if (not base_items) and args.base_plan:
            bp = Path(args.base_plan)
            if bp.exists():
                base_items = read_plan_items(bp)
            else:
                print(f"[ERROR] Base plan not found: {bp}", file=sys.stderr)

        if not base_items:
            print("[ERROR] Gate C requires --base or --base-plan", file=sys.stderr)
            sys.stdout.write("false\n")
            return 1

        passed, errors = gate_c_audit(plan_items, base_items)
        return _finalize_gate("gate_c", passed, errors)

    # Gate B
    junit_path = Path(args.junit) if args.junit else Path("test-results/junit.xml")
    if not junit_path.exists():
        return _finalize_gate(
            "gate_b",
            False,
            [f"[ERROR] JUnit XML not found: {junit_path}"],
            env_error=True,
        )

    try:
        junit_status, junit_cases = parse_junit(junit_path)
    except Exception as exc:
        return _finalize_gate(
            "gate_b",
            False,
            [f"[ERROR] JUnit XML parse failed: {exc}"],
            env_error=True,
        )

    passed, passed_keys, errors = gate_b_junit(
        plan_items, junit_status, junit_cases, args.strict
    )

    if args.tick and (not args.dry_run):
        update_plan(plan_path, passed_keys, reset=args.reset)

    return _finalize_gate("gate_b", passed, errors)


if __name__ == "__main__":
    raise SystemExit(main())
