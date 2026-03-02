# Operational Pitfalls & Fixes

Field-proven lessons from real Jules dispatching sessions. Each entry includes the symptom, root cause, and fix.

---

## P1: Windows Encoding — CJK Characters Become `?` Marks

### Symptom
Chinese (or other CJK) characters in prompts appear as `?` or `???` in the Jules session.
Jules receives garbled task descriptions and cannot follow instructions correctly.

### Root Cause
PowerShell on Windows uses the system code page (GBK/CP936) when piping stdin to child processes.
Even with `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`, the pipe between
PowerShell and `jules.cmd` uses the system locale encoding, silently converting non-ASCII to `?`.

### Fix: Ensure UTF-8 Transport (CJK Allowed)

**CJK content is allowed in prompts.** The dispatch script handles encoding automatically:

1. **GATE-UTF8** validates all task files are strict UTF-8 (BOM auto-stripped)
2. **GATE-2** copies ALL task files to ASCII-safe temp dir with canonical TASK-XXX.md basenames (BOM stripped)
3. **GATE-FFFD** scans for replacement characters before submission
4. **run_bridge** uses Python `encoding="utf-8", errors="strict"` — no silent corruption

**Mandatory**: Always submit via `dispatch_prompt_pack.py` (H4). Never pipe through PowerShell directly.

**Control-plane identifiers MUST remain ASCII**: task_id, file paths, section anchors
(`## Governance Capsule`, `## Document Placement`).

### Legacy: Manual `cmd/chcp65001` Workaround

> This is automated by the dispatch script. Listed for reference only.

1. Write the prompt to a temp file (UTF-8, no BOM)
2. Use `cmd /c` with `chcp 65001` to pipe:
   ```powershell
   cmd /c "chcp 65001 >nul && type C:\temp\task_prompt.md | jules remote new --repo owner/repo"
   ```

### Anti-Pattern
```powershell
# ❌ WRONG: PowerShell pipe corrupts CJK
Get-Content prompt.md | jules remote new --repo owner/repo

# ❌ WRONG: Python subprocess without shell=True can't find jules.cmd
subprocess.run(["jules", "remote", "new", ...], input=prompt)

# ❌ WRONG: open() with errors="replace" — silently corrupts content
open(path, encoding="utf-8", errors="replace").read()
```

---

## P2: Bridge CLI Mode — Ghost Session Reuse

### Symptom
`jules_bridge.py submit` returns `"ok": true, "reused": false` but all tasks share the same
`session_id`. No new sessions appear on the Jules dashboard.

### Root Cause
In CLI mode, the bridge calls `cli_remote_new()` which invokes `jules remote new`.
Then it calls `cli_guess_session_id()` which runs `jules remote list --session` and picks
the **first large numeric token** from the output. If an existing session is already in the
list, all subsequent tasks get mapped to that same session ID.

The `cli_remote_new` step may succeed (creating a real session), but the extracted session ID
is wrong — it points to a pre-existing session.

### Fix: Use `dispatch_prompt_pack.py` (Recommended)

The dispatch script uses API mode automatically when `JULES_API_KEY` is set,
and handles session creation correctly. For single-task verification:

```bash
export JULES_API_KEY="your-key"
# Create a minimal pack with one pending task, then dispatch:
python scripts/dispatch_prompt_pack.py \
  --pack-dir my_pack \
  --repo owner/repo \
  --starting-branch master
# GATE-3 smoke test runs the first task alone → equivalent to single-task verification
```

### Fix: Direct Jules CLI (Emergency Fallback)

When API mode is unavailable and dispatch is not an option:

```powershell
# Direct submission — returns correct session ID
cmd /c "chcp 65001 >nul && type C:\temp\task.md | jules remote new --repo owner/repo"
# Output: Session is created. ID: 158271660456... URL: https://jules.google.com/session/...
# ⚠ Do NOT use --parallel flag — see P7
```

Then manually record the session ID for tracking.

> **Debugging only**: If you must call `jules_bridge.py submit` directly (e.g., for
> driver-level debugging), you need `export _JULES_DISPATCH=1`. This bypasses the
> dispatch-only gate. **Do not use this in production workflows.**

### Anti-Pattern
```bash
# ❌ WRONG: Direct bridge call without dispatch gate — will be BLOCKED
python scripts/jules_bridge.py submit --mode cli --prompt-file task.md
# Error: _JULES_DISPATCH not set. Use dispatch_prompt_pack.py instead.

# ❌ WRONG: CLI mode bridge — session ID extraction is unreliable
# Even with _JULES_DISPATCH=1, CLI mode guesses session_id (see above)
```

---

## P3: Chinese File Paths — External Process Failure

### Symptom
Running `powershell -File script.ps1` from an external process fails with:
```
Get-ChildItem : 找不到路径"J:\宸ヤ綔鍚屾\..."
```
The Chinese path characters are garbled when passed between processes.

### Root Cause
External PowerShell processes inherit the parent's code page. Chinese directory names
get double-encoded or truncated during process boundary crossing.

### Fix: Copy Files to ASCII-Safe Path First

```powershell
# Copy from Chinese-path source to ASCII-safe temp
$src = "j:\工作同步\...\tasks"
$dst = "C:\temp\jules_tasks"
Get-ChildItem -LiteralPath $src -Filter "*.md" | ForEach-Object {
    $content = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText(
        (Join-Path $dst $_.Name),
        $content,
        [System.Text.UTF8Encoding]::new($false)
    )
}
```

Then run all subsequent operations from `C:\temp\jules_tasks\`.

### Anti-Pattern
```powershell
# ❌ Spawning new PowerShell process with Chinese paths
powershell -File submit.ps1  # Paths in submit.ps1 will be garbled
```

---

## P4: Dispatch Records — Stale Idempotency Cache

### Symptom
Re-submitting a modified prompt file returns `"reused": true` and no new session is created,
even though the prompt content has changed.

### Root Cause
The bridge computes an idempotency key from `hash(repo + branch + title + prompt)`.
If a dispatch record with the same key already exists in `.runtime/jules/dispatch/`,
the bridge skips submission and returns the cached result.

### Fix: Use `--no-cache` (Recommended)

```bash
# Selectively clears idempotency records for pending tasks only
python scripts/dispatch_prompt_pack.py --pack-dir <pack> --no-cache
```

### Fix: Manual Delete (Legacy / Last Resort)

> ⚠ This deletes **ALL** dispatch records, including those from other packs or parallel
> batches. Only use when `--no-cache` doesn't resolve the issue.

```python
import os, glob
dispatch_dir = ".runtime/jules/dispatch"
for f in glob.glob(os.path.join(dispatch_dir, "*.json")):
    os.remove(f)
```

---

## P5: Task Design — Generic vs Focused Prompts

### Symptom
Jules produces vague, high-level reports that don't answer specific questions. The code
review output is too broad to be actionable.

### Root Cause
Generic review prompts (e.g., "Review architecture boundaries") give Jules unlimited scope
and no specific acceptance criteria. Jules spends tokens on surface-level observations
rather than deep investigation of concrete questions.

### Fix: Design Targeted Investigation Tasks

Each task should:

1. **Target one specific decision or question** (e.g., D-001: Export Dialog Reset Strategy)
2. **List 4-6 concrete questions** that require specific code evidence
3. **Specify exact file paths and function names** to investigate
4. **Define the output format** (comparison table, dependency graph, data flow trace, etc.)
5. **Declare what evidence qualifies as "answered"** (grep results, line numbers, function signatures)

### Good Example
```markdown
# INV-D001: ExportDialog Reset Strategy — key unmount vs useEffect

## Questions (answer each with file/line evidence)
1. How many useState hooks does ExportDialog have? List each with initial value.
2. Does key={styleId} break Dialog open/close animations (Radix UI)?
3. Does L3FeatureSelector refetch data on every mount? Check caching behavior.
4. Does BatchConfigDialog have the same stale-state problem?

## Output Format
1. State inventory table (name | type | initial value | key-impact | useEffect-reset-difficulty)
2. Comparison table (dimension | key approach | useEffect approach)
3. Recommendation (pick one, ≤5 lines, with reasoning)
```

### Bad Example
```markdown
# Architecture Review

Please review the architecture of the frontend codebase focusing on boundaries,
module responsibilities, and dependency directions.

(Too vague — Jules will produce generic commentary without actionable insights)
```

### Anti-Pattern
```markdown
# ❌ Sending 26 generic review dimensions as separate tasks
# Result: Jules produces 26 surface-level reports, none deep enough to act on

# ✅ Instead: Derive 10-12 tasks from concrete plan decisions and open questions
# Result: Jules produces investigation reports with specific code evidence
```

---

## P6: Document Placement — Jules Creates Unauthorized Directories

### Symptom
Jules creates new directories like `_governance/`, `Reviews/`, `04_Reports/` that don't
exist in the project structure, violating the project's file organization rules.

### Root Cause
Unless explicitly constrained, Jules infers directory names from the task description
and creates what it thinks is logical.

### Fix: Inject Hard Placement Rules Into Every Prompt

Include a CAUTION block at the end of every task prompt:

```markdown
## Document Placement (MANDATORY — violations will cause PR rejection)

1. **Only output path**: `<ORCHESTRATOR_PROVIDED_PATH>` (from PACK.md or task header)
   - With plan module: `<plan_module>/investigation/INV-*_jules_review.md`
   - Standalone: `jules_pack/results/TASK-XXX_review.md`
2. **DO NOT create any new directories** (no `_governance/`, `Reviews/`, or anything not listed above)
3. **DO NOT modify any source code files** (`.ts`, `.tsx`, `.py`) — this task is research only
4. **All output goes into designated path(s)** above
```

### Key Constraint
Repeat the output path **at least twice** in the prompt (once in the header, once in the
placement section) to ensure Jules doesn't miss it.

---

## P7: `--parallel N` Flag — Silent API 400 Errors

### Symptom
All `jules remote new --parallel 1` calls return:
```
api error: status 400, content: { "error": { "code": 400, "message": "Request contains an invalid argument.", "status": "INVALID_ARGUMENT" } }
```
Identical prompts succeed without the `--parallel` flag.

### Root Cause
The `--parallel N` flag (which controls parallelism in multi-session creation) triggers a
different API code path that may reject certain request parameters. This flag is intended
for `jules remote new` when piping multiple prompts separated by `---`, not for single prompts.

### Fix: Never Use `--parallel` for Single-Prompt Submissions

```powershell
# ✅ CORRECT: no --parallel flag
cmd /c "chcp 65001 >nul && type C:\temp\task.md | jules remote new --repo owner/repo"

# ❌ WRONG: --parallel causes 400
cmd /c "chcp 65001 >nul && type C:\temp\task.md | jules remote new --repo owner/repo --parallel 1"
```

---

## P8: Python `subprocess` — Double-Escaping `cmd /c` Paths

### Symptom
Python `subprocess.run(["cmd", "/c", cmd_string])` fails with:
```
The filename, directory name, or volume label syntax is incorrect.
```
Even though the same `cmd /c` command works when typed directly in PowerShell.

### Root Cause
Python's `subprocess` with `["cmd", "/c", ...]` applies its own argument escaping, which
conflicts with `cmd.exe`'s own parsing rules. Quotes in the `cmd_string` get double-escaped,
corrupting paths passed to `type`. The empty stdin then causes Jules to return `INVALID_ARGUMENT`.

### Fix: Use `dispatch_prompt_pack.py` (Recommended)

The dispatch script handles all encoding, path, and submission concerns internally
without going through PowerShell pipe or `cmd /c`:

```bash
python scripts/dispatch_prompt_pack.py --pack-dir <pack> --repo owner/repo
# GATE-2 auto-copies to ASCII-safe temp; bridge is called with UTF-8 strict
```

### Fix: Native `.bat` File (Legacy / Emergency Only)

> ⚠ This bypasses all dispatch gates. Only use when `dispatch_prompt_pack.py` is unavailable.

Instead of Python subprocess, write a `.bat` file and execute it:

```python
# Generate .bat file
with open("C:\\temp\\submit.bat", "w") as f:
    f.write('@echo off\n')
    f.write('chcp 65001 >nul 2>&1\n')
    for task_file in task_files:
        f.write(f'type "{task_file}" | jules remote new --repo owner/repo\n')
        f.write('timeout /t 5 /nobreak >nul\n')

# Execute via cmd /c
subprocess.run(["cmd", "/c", "C:\\temp\\submit.bat"])
```

Alternatively, run `cmd /c` commands directly from the PowerShell session (not via Python).

### Anti-Pattern
```python
# ❌ WRONG: Python subprocess double-escapes the cmd_string
cmd = f'chcp 65001 >nul && type "{filepath}" | jules remote new --repo {repo}'
subprocess.run(["cmd", "/c", cmd], ...)  # Path gets corrupted
```

---

## P9: Batch Submission — `.bat` Template (Legacy / Emergency Only)

> ⚠ **LEGACY**: The `.bat` template bypasses all dispatch gates (GATE-1/FNAME/UTF8/CLI-BATCH/etc.).
> **Always prefer `dispatch_prompt_pack.py`** which enforces all safety checks.
> Use `.bat` only when: (1) API is completely unavailable, (2) dispatch script cannot run,
> and (3) you explicitly accept the risk of no automated safety checks.

### Symptom
Need to submit 10+ tasks to Jules efficiently without manual copy-paste.

### Legacy Solution: `.bat` File with Rate Limiting

The following template has been verified to submit 12 tasks successfully:

```batch
@echo off
chcp 65001 >nul 2>&1
set REPO=owner/repo
set DIR=C:\temp\jules_tasks

echo Submitting tasks to Jules...

echo [1/N] TASK-001
type "%DIR%\TASK-001.md" | jules remote new --repo %REPO%
echo.
timeout /t 5 /nobreak >nul

echo [2/N] TASK-002
type "%DIR%\TASK-002.md" | jules remote new --repo %REPO%
echo.
timeout /t 5 /nobreak >nul

REM ... repeat for each task ...

echo === ALL DONE ===
```

### Critical Rules for `.bat` Batch Submission

1. **Use short ASCII-only filenames** (e.g., `INV-D001.md`, not `INV-D001__ExportDialog_Reset_Strategy.md`)
2. **5-second delay between submissions** (`timeout /t 5 /nobreak >nul`) — prevents rate limiting
3. **Use `chcp 65001` at the top** — ensures UTF-8 encoding for the entire batch
4. **No `--parallel` flag** — use sequential submissions (one `type | jules` per task)
5. **Copy task files to ASCII-safe path first** (e.g., `C:\temp\jules_tasks\`) if source path contains non-ASCII characters
6. **Run via `cmd /c submit.bat`** from PowerShell — not via Python subprocess

### Pre-Submission Checklist (manual — dispatch automates all of these)

- [ ] All prompts are UTF-8 (CJK allowed in body; control-plane identifiers ASCII)
- [ ] Filenames are short ASCII-only
- [ ] Task files are in an ASCII-safe directory
- [ ] Each prompt includes the Document Placement CAUTION block
- [ ] No `--parallel` flag in any command
- [ ] 5-second delay between each submission
- [ ] `.bat` file uses `chcp 65001` at the top

---

## P10: `dispatch_prompt_pack.py` — Submits ALL Tasks, Not Just New Ones

### Symptom
Running `dispatch_prompt_pack.py --pack-dir jules_pack` submits **ALL** task files
(including already-completed TASK-001~016), wasting quota on 27 sessions when only 11
new tasks were intended.

### Root Cause (Historical)
`dispatch_prompt_pack.py` used to scan `tasks/*.md` without any status filtering:

```python
# dispatch_prompt_pack.py:73-75 — THE BUG (now fixed)
task_files = sorted(
    [os.path.join(tasks_dir, f) for f in os.listdir(tasks_dir) if f.lower().endswith(".md")]
)
```

> **RESOLVED**: This bug is fixed. GATE-1 now reads PACK.md and only submits
> tasks marked `pending`. GATE-1b warns about extra files in `tasks/`.

(Now) GATE-1 filters by PACK.md pending status; non-pending files are skipped and warned (GATE-1b).

### Compounding Factor: P3 (Chinese Paths) — Historical

> **Historical context**: When `--pack-dir` contained Chinese characters and tasks were
> submitted via raw `.bat`, PowerShell pipe, or bypassing dispatch, the cross-process
> encoding boundary caused P3 corruption (all sessions fail).
>
> **Current status**: `dispatch_prompt_pack.py` handles this via GATE-2 (all files copied
> to ASCII-safe temp dir). CJK pack-dir paths are **no longer a failure condition** when
> using dispatch. The real risk is external process pipe boundaries (P1/P3).

### Fix (Strongly Recommended): Isolate New Tasks in a Separate Directory

**Strongly recommended:** Do not mix new task files with old completed ones in the same `tasks/` directory.
*(The script's GATE-1b only issues a WARNING for extra files — it does NOT block. But keeping `tasks/` clean avoids clutter, accidental re-submissions, and human confusion about which tasks are active.)*

Option A: Use a versioned pack directory:
```
jules_pack_v2/          ← new pack for TASK-017~027 only
├── PACK.md
├── tasks/
│   ├── TASK-017.md
│   ├── ...
│   └── TASK-027.md
└── results/
```

Option B: Move completed task files out of `tasks/`:
```
jules_pack/
├── PACK.md
├── tasks/              ← ONLY pending tasks here
│   ├── TASK-017.md
│   └── ...
├── tasks_completed/    ← move completed tasks here
│   ├── TASK-001.md
│   └── ...
└── results/
```

### Fix: Pre-Dispatch Checklist (MANDATORY)

> **LARGELY AUTOMATED**: The dispatch script now handles most of these via gates.
> Items marked (auto) are enforced by the script.

Before running `dispatch_prompt_pack.py`:

1. **Count** (auto): GATE-1 filters by PACK.md pending status
2. **Verify isolation** (auto): GATE-1b warns about extra files
3. **Single-task test FIRST** (auto): GATE-3 smoke test
4. **ASCII path** (auto): GATE-2 auto-copy to temp dir and canonical rename
5. **Use dispatch script**: The dispatch script is now the mandatory submission method

### Anti-Patterns
```bash
# ❌ WRONG: tasks/ contains old TASK-001~016 + new TASK-017~027
python dispatch_prompt_pack.py --pack-dir jules_pack
# Submits ALL 27 tasks, wastes 16 quota slots on already-completed work

# ❌ WRONG: No single-task verification before batch
python dispatch_prompt_pack.py --pack-dir jules_pack_v2
# If format is wrong, ALL 11 tasks fail

# ⚠ CAUTION (historical): Pack dir path containing Chinese characters
# Previously caused P3 encoding corruption with direct bridge/pipe submission.
# When using dispatch_prompt_pack.py, CJK pack-dir paths are handled by GATE-2
# (auto-copy to ASCII-safe temp). This is no longer a hard failure.
# The real risk is PowerShell pipe / external process boundary encoding (P1/P3).
python dispatch_prompt_pack.py --pack-dir "00_Documentation/99_Inbox/Architecture_survey/jules_pack"
# ✅ Works with dispatch (GATE-2 handles path); ❌ Fails with raw .bat/pipe
```

### Proven Safe Pattern
```powershell
# ✅ ALWAYS use dispatch script — it handles everything
python dispatch_prompt_pack.py `
  --pack-dir C:\temp\jules_pack `
  --repo YiK1991/Amazon_SaaS_ERP `
  --starting-branch master
# GATE-1 filters pending only, GATE-3 does smoke test automatically
```

---

## P11

### Symptom
Jules session 永久卡在 `QUEUED`，或报 `fatal: Remote branch main not found in upstream origin`。

### Root Cause
`--starting-branch` 默认值为 `main`，但仓库实际默认分支是 `master`。
手动调用 `jules_bridge.py submit` 时极易漏掉此参数。

### Why Manual Calls Are Dangerous
```bash
# ❌ 手动调用漏参数 → clone 失败 → 额度浪费
python jules_bridge.py submit --repo owner/repo --prompt-file TASK.md --title TASK-019
# 默认 --starting-branch main，仓库是 master → FAILED

# ✅ 永远用 dispatch 脚本 → GATE-6 自动验证分支存在
python dispatch_prompt_pack.py --pack-dir ... --repo owner/repo --starting-branch master
# GATE-6 在提交前 git ls-remote 验证，不存在则拒绝并列出可用分支
```

### Fix (Automated)
`dispatch_prompt_pack.py` GATE-6 在提交前自动执行 `git ls-remote --heads` 校验分支：
- 分支不存在 → 列出所有可用分支 → 拒绝提交 (BLOCK)
- 仓库不可达 → 打印 stderr → 拒绝提交 (BLOCK)
- 网络超时 → 拒绝提交 (BLOCK)，防止跑错分支浪费额度

> Fix: 检查网络连接（或代理配置），重试，或显式指定 `--starting-branch`（不要依赖猜测）。

### Rule
**禁止手动调用 `jules_bridge.py submit`**。统一走 `dispatch_prompt_pack.py`，
所有参数错误（分支/路径/任务范围/批次大小）都有对应 GATE 自动拦截。

---

## P12: AI Self-Submit — Triple-Failure Cascade (CJK + No Branch + No Envelope)

### Symptom
AI agent (Codex/Claude) submits a Jules task that immediately enters `FAILED`. Retry with
"corrected" prompt also fails. Two quota slots wasted in under 5 minutes, zero useful output.

### Root Cause (Compound)
AI agent **bypassed all safety gates** by calling `jules_bridge.py submit` directly instead
of using `dispatch_prompt_pack.py`. This caused three simultaneous violations:

1. **CJK prompt through PowerShell pipe** (P1 violation): AI piped a Chinese prompt through
   PowerShell. Windows GBK pipe converted all CJK to `?`. (Note: CJK content is now allowed;
   the violation is using PowerShell pipe, not the language itself.)
2. **Missing `--starting-branch master`** (P11 violation): AI omitted the branch parameter.
   Jules defaulted to `main` which doesn't exist in the repo. Even if the prompt were readable,
   the session would fail at clone time.
3. **No Envelope template** (format violation): AI wrote a freeform markdown file instead of
   following the structured `prompt-envelope-review.md` template. Even if encoding and branch
   were correct, Jules couldn't parse the task intent.

The V2 retry fixed the Envelope but NOT the CJK or branch issues — so it failed again.

### Why This Happens
- AI reads SKILL.md which says "use dispatch script" as a principle, but
  these rules are buried among 11 other principles.
- Without a **hard-stop checklist** at the top of the execution path, AI proceeds to submit
  without verifying each rule.
- The `jules_bridge.py submit` command **succeeds** (returns `ok: true, state: QUEUED`)
  even when the prompt is garbage — failure surfaces asynchronously minutes later as `FAILED`.

### Fix: Pre-Flight Checklist in SKILL.md

The SKILL.md now contains a **HARD STOP Pre-Flight Checklist (H1–H7)** table at the top
of the file. AI MUST complete all 7 checks before calling any submit command.

### Rule
1. **NEVER call `jules_bridge.py submit` directly.** Always use `dispatch_prompt_pack.py`.
2. **ALWAYS verify H1–H7** before ANY submission attempt.
3. **After ANY `FAILED` session**, re-read `references/operational-pitfalls.md` entirely
   before retrying. Do NOT assume "just fixing one thing" will work — failures compound.
4. **If two consecutive sessions fail**, STOP all submission attempts and report to user
   with full diagnostics (session IDs, failure reasons, pitfall IDs).

### Anti-Pattern
```bash
# ❌ TRIPLE FAILURE: AI bypasses all gates
python jules_bridge.py --repo owner/repo --json submit \
  --title "B007 Review" --prompt-file TASK.md
# Prompt is in Chinese → P1
# No --starting-branch → P11
# No Envelope template → format error
# Result: QUEUED → FAILED (async, 2 min later)

# ❌ RETRY WITHOUT FULL DIAGNOSIS
# AI fixes Envelope but keeps CJK + no branch
python jules_bridge.py --repo owner/repo --json submit \
  --title "B007 Review V2" --prompt-file TASK_V2.md
# Result: QUEUED → FAILED again (same root causes)
```

### Proven Safe Pattern
```powershell
# ✅ ALWAYS use dispatch script with explicit branch
# 1. Write UTF-8 prompt using Envelope template (CJK allowed in body)
# 2. Place in ASCII-safe pack directory
# 3. Submit via dispatch with all gates
python dispatch_prompt_pack.py `
  --pack-dir C:\temp\jules_pack `
  --repo YiK1991/Amazon_SaaS_ERP `
  --starting-branch master
```

---

## P13: Monolithic Report / No Progressive Disclosure

### Symptom
Jules produces a single report file >300 lines. No index, no Head Anchor, no layered
navigation. Report is difficult to review, impossible to auto-process for plan backflow,
and causes context bloat when loaded by follow-up agents.

### Root Cause
The prompt template lacked explicit output structure requirements. Jules defaults to
"stream of consciousness" reporting — starting with analysis and ending with conclusions
— which is readable but not machine-consumable or PD-compatible.

### Fix: Enforce PD-OUT v1 in All Output Templates

Every Jules report must follow the PD-OUT v1 skeleton (defined in `prompt-envelope-review.md` §5):

1. **Head Anchor (≤7 lines)**: Conclusion / scope / counts / next step / key links
2. **How to Read This**: A/B/C/D layer table
3. **Issue Index (Table)**: Severity + RefSpec + anchor links
4. **Details**: Each issue/finding with full analysis
5. **Tool Outputs (Offloaded)**: >60 lines / >2000 tokens → separate file, index table only
6. **Plan Update Targets**: RefSpec + ≤3-line edit suggestions

Multi-dimensional investigations (facts + risks + statistics) must split into separate files:
- `TASK-XXX_INDEX.md` (index + Head Anchor only)
- `F-XXX_facts.md` / `R-XXX_risks.md`

### Rule
1. **Gate-PD** (`scripts/gate_pd_output.py`) validates PD-OUT v1 compliance before PR merge.
2. If Gate-PD fails, use `sendMessage` or PR comment `@Jules` to request **format-only fixes**
   (no content changes, no re-review).
3. Single code blocks must be ≤60 lines (PDCA excerpt limit). Longer outputs → offload file.

### Anti-Pattern
```markdown
# TASK-B007 Review Report            ← No Head Anchor
## Overview                          ← No Issue Index
### Finding 1                        ← Inline 200-line stack trace
(... 400 lines of dense analysis ...) ← No offloading, no layering
## Conclusion                        ← Plan Update Targets missing
```

### Proven Safe Pattern
```markdown
## Head Anchor (≤7 lines)
Found 5 issues (2🔴, 3🟡). Scope: 11_webos/backend/. Next: fix Issue 1-2 first.

## How to Read This (Progressive Disclosure)
| Layer | Content | When |
|-------|---------|------|
| A | Head Anchor | Always |
| B | Issue Index | Overview |
| C | Details per issue | Deep dive |
| D | Tool Outputs (offloaded) | Raw data |

## Issue Index
| # | Sev | Title | RefSpec | Link |
|---|-----|-------|---------|------|
| 1 | 🔴 | SoC violation | `svc.py:L45-L89` | [→](#issue-1) |

## Details
#### Issue 1: ...
(structured per PD-OUT v1 template)

## Tool Outputs (Offloaded)
| Output | File | Purpose |
|--------|------|---------|
| full trace | `TASK-B007_trace.txt` | Gate B evidence |

## Plan Update Targets (RefSpec + bullet)
| Target | Edit |
|--------|------|
| `CURRENT.md#b007` | Mark as needs-fix |
```

---

## P14: Ghost Session Reuse — CLI Mode Session ID Guessing

### Symptom
`submit` returns `ok: true` but multiple tasks map to the same `session_id`.
New sessions don't appear on the Jules dashboard.

### Root Cause
CLI mode creates a session via `jules remote new`, then calls `jules remote list --session`
to **guess** the session_id from stdout. This can match a stale/previous session.

### Fix
**Use API mode** (set `JULES_API_KEY`). API mode returns an explicit session ID — no guessing.

The bridge now warns when falling back to CLI mode and `choose_mode()` prints:
"CLI mode has known reliability issues (ghost session reuse)."

### Related
- P2: Bridge CLI Mode — Ghost Session Reuse (original report)

---

## P15: `--parallel` Triggers API 400 INVALID_ARGUMENT

### Symptom
Adding `--parallel 1` (or any value) to `jules remote new` returns HTTP 400.
The entire batch fails with zero sessions created.

### Root Cause
The Jules API does not support the `--parallel` flag.

### Fix
`--parallel` has been permanently removed from `cli_remote_new()` in `jules_bridge.py`.

### Anti-Pattern
```bash
# ❌ WRONG: --parallel causes 400
jules remote new --repo owner/repo --parallel 1
```

---

## P16: UTF-8 Multi-byte Truncation — Sync Tools / Editors Corrupt CJK Characters

### Symptom
Markdown files (especially `_tracker.md`, `CURRENT.md`) suddenly contain `�` (U+FFFD replacement
characters) or produce `UnicodeDecodeError: invalid start byte` when processed by Python scripts.
The corruption appears **after** a file sync or editor save, not during initial creation.

### Root Cause
Cloud sync tools (BaiduSyncdisk, OneDrive, Dropbox) or editors may truncate a file write
mid-stream, splitting a multi-byte UTF-8 character (Chinese characters are 3 bytes in UTF-8).
This leaves orphaned continuation bytes (`0x80-0xBF`) without their leading byte, producing
invalid UTF-8 sequences.

Common scenarios:
1. **Sync tool writes partial file** (network interrupt during upload/download)
2. **Editor auto-save + sync race** (editor writes, sync picks up partial write)
3. **Git checkout on sync-monitored directory** (sync tool re-writes the checkout)
4. **PowerShell `Set-Content`** writes UTF-16 (see P1), then sync tool reads it as UTF-8

### Detection
- `GATE-FFFD` catches U+FFFD **after** conversion, but the file may already be committed
- `git diff` shows garbled Chinese characters
- Python: `open(path).read()` succeeds but content contains `\ufffd` replacement chars

### Fix: `.gitattributes` Encoding Enforcement (Recommended)

Add to the repository root:

```gitattributes
# Force UTF-8 for all text files — prevents encoding drift
*.md    text eol=lf encoding=utf-8
*.py    text eol=lf encoding=utf-8
*.yaml  text eol=lf encoding=utf-8
*.yml   text eol=lf encoding=utf-8
*.json  text eol=lf encoding=utf-8
*.toml  text eol=lf encoding=utf-8
```

> `.gitattributes` tells Git to normalize line endings and flag encoding violations, but
> does NOT prevent sync tools from corrupting files on disk. It only catches issues at
> `git add` time.

### Fix: Pre-commit Hook (Defense in Depth)

```bash
#!/bin/sh
# .git/hooks/pre-commit — reject files with U+FFFD or invalid UTF-8
for f in $(git diff --cached --name-only --diff-filter=ACM -- '*.md' '*.py'); do
  if python3 -c "
import sys
try:
    data = open('$f', 'rb').read()
    text = data.decode('utf-8', errors='strict')
    if '\ufffd' in text:
        sys.exit(1)
except UnicodeDecodeError:
    sys.exit(1)
  "; then
    :
  else
    echo "BLOCKED: $f contains invalid UTF-8 or U+FFFD"
    exit 1
  fi
done
```

### Fix: Recovery When Corruption Already Happened

1. **Check git history**: `git show HEAD~1:path/to/file.md > recovered.md`
2. **Check sync tool trash/versions**: BaiduSyncdisk keeps version history
3. **Rebuild from template**: For `_tracker.md`, re-generate from the tracker template

### Rule
1. **Never edit plan-doc files in sync-monitored directories via PowerShell `Set-Content`**
2. **Always use Python `open(f, 'w', encoding='utf-8')` or AI code editors** for writing
3. **Add `.gitattributes`** to every repo that contains CJK content
4. **If U+FFFD detected in a committed file**: treat as critical — recover from git history immediately

### Related
- P1: Windows Encoding — CJK Characters Become `?` Marks
- GATE-FFFD: Scans for U+FFFD before Jules dispatch
- GATE-UTF8: Auto-converts UTF-16/GBK (added in B011)

