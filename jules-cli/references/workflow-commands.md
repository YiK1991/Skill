# Jules 工作流命令参考

> 从 SKILL.md 搬出的完整 CLI 命令、JSON 输出示例、方法对比和批量模板。

---

## 提交任务（Submit）

> **标准入口**：所有提交必须经过 `dispatch_prompt_pack.py`（H4）。
> 脚本自动处理：UTF-8 / ASCII 路径 / BOM 剥离 / PACK.md 过滤 / smoke test / CLI-batch 保护。

### Method A — Dispatch（推荐，唯一生产入口）

```bash
export JULES_API_KEY="your-key"  # API 模式，session ID 精确
python scripts/dispatch_prompt_pack.py \
  --pack-dir <path/to/jules_pack> \
  --repo <owner/repo> \
  --starting-branch master
# GATE-1: 只投递 PACK.md pending 状态的任务
# GATE-3: 第一个任务单独 smoke test，失败则中止批量
# GATE-CLI-BATCH: 无 API key 时多任务默认阻断
```

### Method B — 直接 Jules CLI（应急 fallback）

仅当 dispatch 无法运行时使用：

```powershell
cmd /c "chcp 65001 >nul && type C:\\temp\\task.md | jules remote new --repo owner/repo"
# Output: Session is created. ID: 158271... URL: https://jules.google.com/session/...
# ⚠ 禁止使用 --parallel flag — 导致 API 400 (see P7)
# ⚠ 此方法绕过所有 GATE 门禁，仅限应急
```

### Method C — Bridge（仅调试用）

> ⚠ `jules_bridge.py submit` 默认被硬拦截。必须 `export _JULES_DISPATCH=1` 才能使用。
> **禁止用于生产提交。**

```bash
export _JULES_DISPATCH=1  # 仅调试
export JULES_API_KEY="your-key"
python scripts/jules_bridge.py --json submit \
  --repo <owner/repo> \
  --prompt-file <path/to/TASK-XXX.md> \
  --title "TASK-XXX"
```

> ⚠ **参数顺序陷阱**：`--json` 是全局选项，必须放在子命令 `submit` **之前**（见 P17）。

### 提交成功信号

```json
{"ok":true,"mode":"api","session_id":"...","session_url":"...","idempotency_key":"...","record_path":"..."}
```

`ok=true` + 有 `session_id` 才算任务已发出。

---

## 轮询 / 等待

```bash
python scripts/jules_bridge.py --json status --session-id <id>
python scripts/jules_bridge.py --json wait --session-id <id> --until COMPLETED,FAILED,AWAITING_PLAN_APPROVAL
```

## 审批计划

当 session 进入 `AWAITING_PLAN_APPROVAL`：

```bash
python scripts/jules_bridge.py --json approve --session-id <id>
```

## 迭代修正

### 首选：同 session sendMessage

session 仍处于 `AWAITING_USER_FEEDBACK` 或未终结时：

```bash
python scripts/jules_bridge.py --json send \
  --session-id <id> \
  --message-file <path/to/FU-001.md>
```

> ⚠ 子命令是 `send`，**不是** `send-message`（见 P17）。

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
