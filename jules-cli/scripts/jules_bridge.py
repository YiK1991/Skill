#!/usr/bin/env python3
"""Jules Bridge: stable, machine-readable orchestration for Jules.

Why this exists:
  - Jules Tools CLI is convenient but not a stable integration surface for other agents/tools.
  - Jules API provides stable JSON + explicit session state machine.

This bridge presents ONE stable interface to callers and can operate in:
  - api mode (recommended): talks to Jules REST API (v1alpha)
  - cli mode (fallback): shells out to `jules` CLI

Core guarantees (when --json is used):
  - Submit returns ok=true ONLY when we can verify the session exists.
  - Outputs include session_id, session_url (when available), idempotency_key, record_path.

Security:
  - API key should be provided via JULES_API_KEY env var.
  - Never hardcode keys in prompt files or repo.

Note: This script intentionally avoids third-party dependencies.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

# --------------- Encoding: force UTF-8 on Windows (GBK default) ---------------
if sys.platform == "win32":
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name)
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")


API_BASE = "https://jules.googleapis.com/v1alpha"


@dataclass
class BridgeConfig:
    mode: str  # auto|api|cli
    repo: str
    starting_branch: str
    source: Optional[str]
    require_plan_approval: bool
    automation_mode: str
    api_key: Optional[str]
    state_dir: str
    json_output: bool
    timeout_s: int
    poll_interval_s: int


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def json_out(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_idempotency_key(
    *,
    repo: str,
    starting_branch: str,
    title: str,
    prompt: str,
    require_plan_approval: bool,
    automation_mode: str,
) -> str:
    norm = "\n".join(
        [
            f"repo={repo}",
            f"branch={starting_branch}",
            f"title={title}",
            f"require_plan_approval={int(require_plan_approval)}",
            f"automation_mode={automation_mode}",
            "prompt=<<EOF",
            prompt.strip(),
            "EOF",
        ]
    )
    return sha256_hex(norm)[:16]


def record_path(state_dir: str, key: str) -> str:
    return os.path.join(state_dir, "dispatch", f"{key}.json")


def load_record(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_record(path: str, rec: Dict[str, Any]) -> None:
    ensure_dir(os.path.dirname(path))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


# ----------------------------- API client -----------------------------


def api_request(
    api_key: str,
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
    timeout_s: int = 30,
) -> Tuple[int, Dict[str, Any]]:
    url = f"{API_BASE}{path}"
    data = None
    headers = {
        "X-Goog-Api-Key": api_key,
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            return resp.getcode(), json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw) if raw else {"error": raw}
        except json.JSONDecodeError:
            return e.code, {"error": raw}
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}


def api_list_sources(api_key: str) -> List[Dict[str, Any]]:
    sources: List[Dict[str, Any]] = []
    page_token = ""
    while True:
        path = "/sources?pageSize=100" + (f"&pageToken={page_token}" if page_token else "")
        code, data = api_request(api_key, "GET", path)
        if code != 200:
            raise RuntimeError(f"ListSources failed: {code} {data}")
        sources.extend(data.get("sources", []))
        page_token = data.get("nextPageToken", "")
        if not page_token:
            return sources


def api_resolve_source(api_key: str, repo: str) -> str:
    """Resolve a GitHub repo (owner/repo) to a Jules API source name.

    If repo is already in 'sources/...' format, return it as-is.
    """
    if repo.startswith("sources/"):
        return repo

    m = re.match(r"^([^/]+)/([^/]+)$", repo)
    if not m:
        raise ValueError(
            "For API mode, --repo must be 'owner/repo' (or provide --source 'sources/...')."
        )
    owner, rname = m.group(1), m.group(2)

    for s in api_list_sources(api_key):
        gh = s.get("githubRepo", {})
        if gh.get("owner") == owner and gh.get("repo") == rname:
            return s["name"]

    raise RuntimeError(
        f"Cannot resolve repo '{repo}' to a Jules source. Ensure the repo is connected in Jules web app."
    )


def api_create_session(cfg: BridgeConfig, title: str, prompt: str) -> Dict[str, Any]:
    assert cfg.api_key
    source_name = cfg.source or api_resolve_source(cfg.api_key, cfg.repo)
    body: Dict[str, Any] = {
        "prompt": prompt,
        "title": title,
        "sourceContext": {
            "source": source_name,
            "githubRepoContext": {"startingBranch": cfg.starting_branch},
        },
    }
    if cfg.require_plan_approval:
        body["requirePlanApproval"] = True
    if cfg.automation_mode and cfg.automation_mode != "AUTOMATION_MODE_UNSPECIFIED":
        body["automationMode"] = cfg.automation_mode

    code, data = api_request(cfg.api_key, "POST", "/sessions", body)
    if code not in (200, 201):
        raise RuntimeError(f"CreateSession failed: {code} {data}")
    return data


def api_get_session(cfg: BridgeConfig, session_id: str) -> Dict[str, Any]:
    assert cfg.api_key
    code, data = api_request(cfg.api_key, "GET", f"/sessions/{session_id}")
    if code != 200:
        raise RuntimeError(f"GetSession failed: {code} {data}")
    return data


def api_approve_plan(cfg: BridgeConfig, session_id: str) -> None:
    assert cfg.api_key
    code, data = api_request(cfg.api_key, "POST", f"/sessions/{session_id}:approvePlan", {})
    if code not in (200, 204):
        raise RuntimeError(f"ApprovePlan failed: {code} {data}")


def api_send_message(cfg: BridgeConfig, session_id: str, message: str) -> None:
    assert cfg.api_key
    code, data = api_request(cfg.api_key, "POST", f"/sessions/{session_id}:sendMessage", {"prompt": message})
    if code not in (200, 204):
        raise RuntimeError(f"SendMessage failed: {code} {data}")


def api_list_activities(cfg: BridgeConfig, session_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
    assert cfg.api_key
    out: List[Dict[str, Any]] = []
    token = ""
    while True:
        path = f"/sessions/{session_id}/activities?pageSize={page_size}" + (f"&pageToken={token}" if token else "")
        code, data = api_request(cfg.api_key, "GET", path)
        if code != 200:
            raise RuntimeError(f"ListActivities failed: {code} {data}")
        out.extend(data.get("activities", []))
        token = data.get("nextPageToken", "")
        if not token:
            return out


# ----------------------------- CLI helpers -----------------------------


def _resolve_jules_exe() -> str:
    """Resolve 'jules' to its full path (needed on Windows where npm installs .cmd/.ps1)."""
    resolved = shutil.which("jules")
    if not resolved:
        raise FileNotFoundError("`jules` CLI not found in PATH.")
    return resolved


def cli_run(
    cmd: List[str],
    timeout_s: int = 120,
    stdin_text: Optional[str] = None,
) -> subprocess.CompletedProcess:
    # Force UTF-8 for downstream processes (avoids GBK corruption on Chinese Windows)
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    # On Windows, resolve 'jules' to full path (.cmd/.ps1) to avoid FileNotFoundError
    if cmd and cmd[0] == "jules":
        cmd = [_resolve_jules_exe()] + cmd[1:]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_s,
        input=stdin_text,
        env=env,
    )


def cli_check_available() -> None:
    try:
        r = cli_run(["jules", "version"], timeout_s=20)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip() or "unknown error")
    except FileNotFoundError as e:
        raise RuntimeError("`jules` CLI not found in PATH.") from e


def cli_remote_new(repo: str, prompt: str, parallel: int = 1) -> Tuple[str, str]:
    # We cannot rely on the stdout format. We return (stdout, stderr) for the record.
    # IMPORTANT: pipe prompt via stdin instead of --session arg to avoid
    # PowerShell/cmd.exe codepage (GBK) corrupting Chinese characters.
    cmd = ["jules", "remote", "new", "--repo", repo]
    if parallel and parallel > 1:
        cmd += ["--parallel", str(parallel)]
    r = cli_run(cmd, timeout_s=300, stdin_text=prompt)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip() or "jules remote new failed")
    return r.stdout, r.stderr


def cli_remote_list_sessions() -> str:
    r = cli_run(["jules", "remote", "list", "--session"], timeout_s=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "jules remote list --session failed")
    return r.stdout


def cli_guess_session_id(list_output: str, prompt_hint: str = "") -> Optional[str]:
    """Best-effort extraction.

    Since CLI output format is not part of a stable contract, we only do:
      - Find long digit tokens (>= 6)
      - Optionally prefer lines that contain the prompt hint
    """
    candidates: List[str] = []
    lines = list_output.splitlines()
    if prompt_hint:
        for ln in lines:
            if prompt_hint[:40] in ln:
                candidates += re.findall(r"\b\d{6,}\b", ln)
    if not candidates:
        candidates = re.findall(r"\b\d{6,}\b", list_output)
    return candidates[-1] if candidates else None


# ----------------------------- Commands -----------------------------


def choose_mode(cfg: BridgeConfig) -> str:
    if cfg.mode != "auto":
        return cfg.mode
    return "api" if cfg.api_key else "cli"


def cmd_submit(cfg: BridgeConfig, title: str, prompt_file: str) -> Dict[str, Any]:
    prompt = read_text(prompt_file)
    key = compute_idempotency_key(
        repo=cfg.repo,
        starting_branch=cfg.starting_branch,
        title=title,
        prompt=prompt,
        require_plan_approval=cfg.require_plan_approval,
        automation_mode=cfg.automation_mode,
    )
    rec_path = record_path(cfg.state_dir, key)
    existing = load_record(rec_path)

    mode = choose_mode(cfg)

    # If we have an existing record, verify the session still exists and reuse it.
    if existing and existing.get("session_id"):
        sid = str(existing["session_id"])
        try:
            if mode == "api":
                sess = api_get_session(cfg, sid)
                return {
                    "ok": True,
                    "mode": "api",
                    "session_id": sid,
                    "session_url": sess.get("url"),
                    "state": sess.get("state"),
                    "idempotency_key": key,
                    "record_path": rec_path,
                    "reused": True,
                }
            else:
                # CLI verification is weak; we do best-effort by checking list output contains sid.
                out = cli_remote_list_sessions()
                if sid in out:
                    return {
                        "ok": True,
                        "mode": "cli",
                        "session_id": sid,
                        "session_url": None,
                        "state": None,
                        "idempotency_key": key,
                        "record_path": rec_path,
                        "reused": True,
                    }
        except Exception:
            # fall through: create a new one
            pass

    if mode == "api":
        sess = api_create_session(cfg, title=title, prompt=prompt)
        sid = sess.get("id") or sess.get("name", "").split("/")[-1]
        if not sid:
            raise RuntimeError(f"API create returned no session id: {sess}")
        # ACK: verify it is readable
        sess2 = api_get_session(cfg, str(sid))
        rec = {
            "mode": "api",
            "idempotency_key": key,
            "title": title,
            "repo": cfg.repo,
            "starting_branch": cfg.starting_branch,
            "require_plan_approval": cfg.require_plan_approval,
            "automation_mode": cfg.automation_mode,
            "prompt_file": prompt_file,
            "session_id": str(sid),
            "session_url": sess2.get("url"),
            "create_time": sess2.get("createTime"),
        }
        save_record(rec_path, rec)
        return {
            "ok": True,
            "mode": "api",
            "session_id": str(sid),
            "session_url": sess2.get("url"),
            "state": sess2.get("state"),
            "idempotency_key": key,
            "record_path": rec_path,
            "reused": False,
        }

    # cli mode
    cli_check_available()
    stdout, stderr = cli_remote_new(cfg.repo, prompt)
    # ACK: best-effort session id extraction from list
    list_out = cli_remote_list_sessions()
    sid = cli_guess_session_id(list_out, prompt_hint=prompt)
    if not sid:
        # still record, but mark as not-acked
        sid = ""
    rec = {
        "mode": "cli",
        "idempotency_key": key,
        "title": title,
        "repo": cfg.repo,
        "starting_branch": cfg.starting_branch,
        "prompt_file": prompt_file,
        "cli_stdout": stdout.strip(),
        "cli_stderr": stderr.strip(),
        "session_id": sid,
        "create_time": int(time.time()),
    }
    save_record(rec_path, rec)

    if not sid:
        raise RuntimeError(
            "CLI submit executed but session_id could not be verified. "
            "Use API mode (recommended) or inspect `jules remote list --session` / TUI to locate the session."
        )

    return {
        "ok": True,
        "mode": "cli",
        "session_id": sid,
        "session_url": None,
        "state": None,
        "idempotency_key": key,
        "record_path": rec_path,
        "reused": False,
    }


def cmd_status(cfg: BridgeConfig, session_id: str) -> Dict[str, Any]:
    mode = choose_mode(cfg)
    if mode == "api":
        sess = api_get_session(cfg, session_id)
        pr_url = None
        for out in sess.get("outputs", []) or []:
            pr = (out.get("pullRequest") or {})
            if pr.get("url"):
                pr_url = pr.get("url")
                break
        return {
            "ok": True,
            "mode": "api",
            "session_id": session_id,
            "session_url": sess.get("url"),
            "state": sess.get("state"),
            "pr_url": pr_url,
            "title": sess.get("title"),
            "update_time": sess.get("updateTime"),
        }

    # cli mode (limited)
    cli_check_available()
    out = cli_remote_list_sessions()
    present = session_id in out
    return {
        "ok": present,
        "mode": "cli",
        "session_id": session_id,
        "session_url": None,
        "state": None,
        "present_in_list": present,
    }


def cmd_wait(cfg: BridgeConfig, session_id: str, until: List[str]) -> Dict[str, Any]:
    mode = choose_mode(cfg)
    deadline = time.time() + cfg.timeout_s
    last: Dict[str, Any] = {}

    if mode != "api":
        raise RuntimeError("wait is only reliable in api mode (explicit session state).")

    while True:
        last = cmd_status(cfg, session_id)
        state = last.get("state")
        if state in until:
            return {"ok": True, **last, "until": until}
        if time.time() > deadline:
            return {"ok": False, **last, "until": until, "error": "timeout"}
        time.sleep(cfg.poll_interval_s)


def cmd_approve(cfg: BridgeConfig, session_id: str) -> Dict[str, Any]:
    mode = choose_mode(cfg)
    if mode != "api":
        raise RuntimeError("approve requires api mode.")
    api_approve_plan(cfg, session_id)
    sess = api_get_session(cfg, session_id)
    return {
        "ok": True,
        "mode": "api",
        "session_id": session_id,
        "state": sess.get("state"),
        "session_url": sess.get("url"),
    }


def cmd_send(cfg: BridgeConfig, session_id: str, message_file: str) -> Dict[str, Any]:
    mode = choose_mode(cfg)
    if mode != "api":
        raise RuntimeError("send requires api mode (same-session iteration).")
    msg = read_text(message_file)
    api_send_message(cfg, session_id, msg)
    sess = api_get_session(cfg, session_id)
    return {
        "ok": True,
        "mode": "api",
        "session_id": session_id,
        "state": sess.get("state"),
        "session_url": sess.get("url"),
    }


def cmd_tail(cfg: BridgeConfig, session_id: str, limit: int) -> Dict[str, Any]:
    mode = choose_mode(cfg)
    if mode != "api":
        raise RuntimeError("tail requires api mode.")
    acts = api_list_activities(cfg, session_id)
    # Keep only message-like activities for concise tail
    msgs: List[Dict[str, Any]] = []
    for a in acts:
        if a.get("agentMessaged") or a.get("userMessaged"):
            msgs.append(
                {
                    "time": a.get("createTime"),
                    "originator": a.get("originator"),
                    "agent": (a.get("agentMessaged") or {}).get("agentMessage"),
                    "user": (a.get("userMessaged") or {}).get("userMessage"),
                }
            )
    return {
        "ok": True,
        "mode": "api",
        "session_id": session_id,
        "messages": msgs[-limit:],
    }


# ----------------------------- CLI entry -----------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Jules bridge (stable JSON interface).")
    p.add_argument(
        "--mode",
        choices=["auto", "api", "cli"],
        default=os.environ.get("JULES_MODE", "auto"),
        help="auto (default): api if JULES_API_KEY is set, else cli",
    )
    p.add_argument("--repo", default=os.environ.get("JULES_REPO", "."), help="For cli: '.' or owner/repo. For api: owner/repo (or use --source).")
    p.add_argument("--starting-branch", default=os.environ.get("JULES_BRANCH", "main"), help="API only: starting branch.")
    p.add_argument("--source", default=os.environ.get("JULES_SOURCE"), help="API only: source name like 'sources/github/owner/repo'.")
    p.add_argument("--automation-mode", default=os.environ.get("JULES_AUTOMATION_MODE", "AUTO_CREATE_PR"), help="API only: default AUTO_CREATE_PR (PR-only workflow). Override with AUTOMATION_MODE_UNSPECIFIED if needed.")
    p.add_argument("--require-plan-approval", action="store_true", help="API only: require explicit plan approval before execution")
    p.add_argument("--state-dir", default=os.environ.get("JULES_STATE_DIR", ".runtime/jules"), help="Local durable state directory (not in documentation domain).")
    p.add_argument("--timeout-s", type=int, default=int(os.environ.get("JULES_TIMEOUT_S", "1800")), help="wait timeout")
    p.add_argument("--poll-interval-s", type=int, default=int(os.environ.get("JULES_POLL_INTERVAL_S", "10")), help="wait poll interval")
    p.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    sub = p.add_subparsers(dest="cmd", required=True)

    s_submit = sub.add_parser("submit", help="Submit a prompt file as a new Jules session (idempotent).")
    s_submit.add_argument("--title", required=True)
    s_submit.add_argument("--prompt-file", required=True)

    s_status = sub.add_parser("status", help="Get session status.")
    s_status.add_argument("--session-id", required=True)

    s_wait = sub.add_parser("wait", help="Wait until session reaches one of the target states (API only).")
    s_wait.add_argument("--session-id", required=True)
    s_wait.add_argument(
        "--until",
        required=True,
        help="Comma-separated states, e.g. COMPLETED,FAILED,AWAITING_PLAN_APPROVAL,AWAITING_USER_FEEDBACK",
    )

    s_approve = sub.add_parser("approve", help="Approve latest plan (API only).")
    s_approve.add_argument("--session-id", required=True)

    s_send = sub.add_parser("send", help="Send a follow-up message to the same session (API only).")
    s_send.add_argument("--session-id", required=True)
    s_send.add_argument("--message-file", required=True)

    s_tail = sub.add_parser("tail", help="Tail last N message activities (API only).")
    s_tail.add_argument("--session-id", required=True)
    s_tail.add_argument("--limit", type=int, default=6)

    return p


def main() -> None:
    p = build_parser()
    args = p.parse_args()

    cfg = BridgeConfig(
        mode=args.mode,
        repo=args.repo,
        starting_branch=args.starting_branch,
        source=args.source,
        require_plan_approval=bool(args.require_plan_approval),
        automation_mode=args.automation_mode,
        api_key=os.environ.get("JULES_API_KEY"),
        state_dir=args.state_dir,
        json_output=bool(args.json),
        timeout_s=int(args.timeout_s),
        poll_interval_s=int(args.poll_interval_s),
    )

    ensure_dir(cfg.state_dir)

    try:
        if args.cmd == "submit":
            payload = cmd_submit(cfg, title=args.title, prompt_file=args.prompt_file)
        elif args.cmd == "status":
            payload = cmd_status(cfg, session_id=args.session_id)
        elif args.cmd == "wait":
            until = [s.strip() for s in str(args.until).split(",") if s.strip()]
            payload = cmd_wait(cfg, session_id=args.session_id, until=until)
        elif args.cmd == "approve":
            payload = cmd_approve(cfg, session_id=args.session_id)
        elif args.cmd == "send":
            payload = cmd_send(cfg, session_id=args.session_id, message_file=args.message_file)
        elif args.cmd == "tail":
            payload = cmd_tail(cfg, session_id=args.session_id, limit=int(args.limit))
        else:
            raise RuntimeError(f"Unknown cmd: {args.cmd}")
        if cfg.json_output:
            json_out(payload)
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))

    except Exception as e:
        payload = {"ok": False, "error": str(e)}
        if cfg.json_output:
            json_out(payload)
        else:
            eprint(str(e))
            sys.exit(2)


if __name__ == "__main__":
    main()
