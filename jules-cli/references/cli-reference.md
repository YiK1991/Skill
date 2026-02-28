# Jules Tools CLI — Quick Reference

> 本页聚焦"能跑起来"的命令。做可靠集成请优先用 `scripts/jules_bridge.py`（对调用方输出稳定 JSON）。

## Installation

```bash
npm install -g @google/jules
# or
pnpm install -g @google/jules
```

## Authentication

```bash
jules login
jules logout
```

## Version

```bash
jules version
# 注意：是子命令，不是 --version flag
```

## Commands

### TUI Dashboard（交互模式）

```bash
jules
```

> ⚠ **非交互终端（如 AI Agent 调用）中无法正常显示**。
> Jules 的 TUI 基于 bubbletea，在非交互 stdout 中输出会乱码。
> AI Agent 应使用 `jules remote` 子命令或 Bridge API 模式。

### List repos / sessions

```bash
jules remote list --repo
jules remote list --session
```

> ⚠ `--session` 输出包含 TUI 格式化字符，在非交互终端中可能截断。
> 需要精确 session 状态时，使用 Bridge API 模式的 `status` 命令。

### Create a session

```bash
# 从 stdin 读取 prompt（Windows 推荐方式）
cmd /c "chcp 65001 >nul && type C:\temp\task.md | jules remote new --repo owner/repo"

# 直接指定 session 描述
jules remote new --repo owner/repo --session "write unit tests"

# 从 cwd 自动检测 repo
jules remote new --repo . --session "fix the login bug"

# Parallel sessions for the SAME prompt（同一 prompt 多方案，非多 prompt 并行）
jules remote new --repo . --session "optimize queries" --parallel 3
```

> ⚠ `--parallel` 用于"同一 prompt 多方案"，并不等价于"多 prompt 并行"。
> 官方示例中 `--parallel` 上限为 5。`--parallel` 已知导致 API 400 错误（见 P7）。

### Pull results

```bash
jules remote pull --session <session_id>
```

> ⚠ **PR-Only 工作流中禁止使用此命令**。所有结果通过 PR 审阅。

## Bridge Script（推荐集成方式）

Bridge 提供稳定的 JSON 输出，不依赖 CLI stdout 格式：

```bash
# 提交任务（幂等）
python jules_bridge.py --json --repo owner/repo submit --title "TASK-XXX" --prompt-file task.md

# 查询状态
python jules_bridge.py --json status --session-id <id>

# 等待状态变化
python jules_bridge.py --json wait --session-id <id> --until COMPLETED,FAILED

# 审批计划
python jules_bridge.py --json approve --session-id <id>

# 发送追加消息
python jules_bridge.py --json send --session-id <id> --message-file followup.md

# 尾部活动
python jules_bridge.py --json tail --session-id <id> --limit 5
```

> ⚠ **参数顺序陷阱**：`--json`、`--repo` 等全局选项必须放在子命令**之前**。
> ✅ 正确：`jules_bridge.py --json status --session-id <id>`
> ❌ 错误：`jules_bridge.py status --session-id <id> --json`（会报 unrecognized arguments）

## Windows 特别注意

1. `cmd /c` 管道方式是 Windows 上最可靠的 CLI 调用方式
2. 必须先 `chcp 65001` 设为 UTF-8，否则中文 prompt 会乱码
3. PowerShell 中调用 bridge 时，路径反斜杠可能引发解析问题，建议用 `cmd /c` 包裹
4. `jules version` 是子命令（不是 `--version` flag）
