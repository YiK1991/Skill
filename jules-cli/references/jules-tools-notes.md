# Jules Tools (CLI) Notes

> 用 CLI 直接对接时，建议把"稳定接口"放在 `scripts/jules_bridge.py` 上，让调用方不直接依赖 CLI 输出格式。

---

## CLI 常用命令（脚本化）

- 版本：`jules version`（注意：是子命令，不是 `--version`）
- 登录：`jules login`
- 列表：`jules remote list --repo` / `jules remote list --session`
- 创建 session：`echo "..." | jules remote new --repo owner/repo`
- 并行（同一 prompt）：`jules remote new --repo . --session "..." --parallel N`
- 拉取代码：`jules remote pull --session <session_id>`（PR-Only 流中禁止使用）

---

## TUI vs Non-Interactive 模式

| 调用方式               | 行为                         | AI Agent 可用？      |
| ---------------------- | ---------------------------- | -------------------- |
| `jules`（无参数）      | 启动 bubbletea TUI dashboard | ❌ 在非交互终端中乱码 |
| `jules remote list`    | 返回结果但含 TUI 格式字符    | ⚠ 可用但输出可能截断 |
| `jules remote new ...` | 创建 session，返回 ID        | ✅ 可靠               |
| `jules version`        | 返回版本号                   | ✅ 可靠               |
| Bridge API 模式        | 稳定 JSON 输出               | ✅ 首选               |

**结论**：AI Agent（如 Codex/Claude）必须使用 `jules remote` 子命令或 Bridge API 模式。
TUI dashboard 仅适用于人类在终端中交互操作。

---

## Bridge Script 参数顺序陷阱

Bridge 的全局选项（`--json`、`--repo`、`--mode` 等）必须放在子命令之前：

```bash
# ✅ 正确
python jules_bridge.py --json status --session-id <id>

# ❌ 错误（报 unrecognized arguments）
python jules_bridge.py status --session-id <id> --json
```

原因：argparse 将 `--json` 注册在根 parser 上，子命令有独立的 subparser。

---

## CLI 对接的常见坑

1. **stdout 非稳定**：版本更新后输出可能变化；不要把 stdout 当协议。
2. **session_id 解析不可靠**：部分输出可能不包含 id；应做二次验证。
3. **重试导致重复 session**：必须做 idempotency（Bridge 已内置）。
4. **缺少状态机信号**：CLI 无法稳定判断何时需要 plan approval / feedback（需 API 模式）。
5. **TUI 乱码**：`jules` 和 `jules remote list --session` 在非交互终端中输出包含 bubbletea 渲染序列。
6. **PowerShell 路径问题**：在 PowerShell 中反斜杠路径可能引发解析错误，用 `cmd /c` 包裹更可靠。
7. **`--parallel` flag**：已知在某些场景下导致 API 400 错误。

**因此**：CLI 模式只建议作为"本地人类操作"或"兜底路径"。程序化集成首选 Bridge API 模式。
