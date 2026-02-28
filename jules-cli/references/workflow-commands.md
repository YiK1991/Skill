# Jules 工作流命令参考

> 从 SKILL.md 搬出的完整 CLI 命令、JSON 输出示例、方法对比和批量模板。

---

## 提交任务（Submit）

> **⚠ Windows 用户**：Bridge CLI 模式的 session ID 提取不可靠。
> 优先使用 `cmd /c` 直接调用 `jules remote new`，或使用 API 模式（`JULES_API_KEY`）。
> 详见 `operational-pitfalls.md` P2。

### Method A — Direct CLI（Windows 推荐）

```powershell
cmd /c "chcp 65001 >nul && type C:\temp\task.md | jules remote new --repo owner/repo"
# Output: Session is created. ID: 158271... URL: https://jules.google.com/session/...
# ⚠ 禁止使用 --parallel flag — 导致 API 400 (see P7)
```

### Method B — Bridge + API Key（最可靠）

```bash
export JULES_API_KEY="your-key"
python scripts/jules_bridge.py submit \
  --repo <owner/repo> \
  --prompt-file <path/to/TASK-XXX.md> \
  --title "TASK-XXX: <short title>" \
  --require-plan-approval \
  --automation-mode AUTO_CREATE_PR \
  --json
```

### Method C — 批量提交（10+ 任务）

编写 `.bat` 文件并通过 `cmd /c submit.bat` 执行。详见 `operational-pitfalls.md` P9。关键规则：
- 短 ASCII 文件名（`INV-D001.md`）
- 每次提交间隔 5 秒
- 禁止 `--parallel` flag
- 禁止用 Python subprocess 驱动 `cmd /c`

### 提交成功信号

```json
{"ok":true,"mode":"api","session_id":"...","session_url":"...","idempotency_key":"...","record_path":"..."}
```

`ok=true` + 有 `session_id` 才算任务已发出。

---

## 轮询 / 等待

```bash
python scripts/jules_bridge.py status --session-id <id> --json
python scripts/jules_bridge.py wait --session-id <id> --until COMPLETED,FAILED,AWAITING_PLAN_APPROVAL --json
```

## 审批计划

当 session 进入 `AWAITING_PLAN_APPROVAL`：

```bash
python scripts/jules_bridge.py approve --session-id <id> --json
```

## 迭代修正

### 首选：同 session sendMessage

session 仍处于 `AWAITING_USER_FEEDBACK` 或未终结时：

```bash
python scripts/jules_bridge.py send \
  --session-id <id> \
  --message-file <path/to/FU-001.md> \
  --json
```

### 次选：PR 评论 `@Jules`

session 已 `COMPLETED`，需在 PR 上追加修改时，在 PR 页面使用标准"进一步修改"模板（见 `prompt-envelope.md`）。

## 获取结果（仅通过 PR）

> **⚠ 禁止 `jules remote pull`。所有异步工作通过 PR 审阅。**

1. 从 `status` 输出的 `pr_url` 获取 PR 链接
2. 在 PR 页面进行 Code Review
3. 通过 `@Jules` 评论沟通修改需求
4. 审阅通过后，由人类决定合并

## 计划审批策略

| 任务类型                       | `requirePlanApproval` | 说明                                 |
| ------------------------------ | --------------------- | ------------------------------------ |
| 改代码 / 改接口 / 引入依赖     | `true`（强制）        | 必须显式审批后才执行                 |
| 补测试 / 补文档 / 极小 cleanup | 可选 `false`          | Planning Critic 会审视，仍需人工审阅 |

## Session 策略

- 同一主题优先在**一个 session** 内迭代（sendMessage）
- 仅当方面（aspect）完全独立时才开并行 session
- session 已 `COMPLETED` 后，先尝试 PR 评论 `@Jules`
- 若需全新上下文，创建 continuation session 并携带先前 session ID + 已确认发现
