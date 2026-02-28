# Jules API Notes (用于可靠集成)

> 本页只写“对接需要的最小事实”。更完整信息以官方文档为准。

---

## 为什么 API 是“推荐对接面”

- 机器可读：创建 session 的响应直接返回 `id / url / state`。
- 有明确状态机：可以稳定地做 gating（plan approval / user feedback）。
- 支持在同一 session 内继续对话：`sendMessage`。

这三点用 CLI 纯 stdout 解析很难做到稳。

---

## 你会用到的 5 个调用

1) **List sources**：找到 repo 对应的 `source` 名称。

2) **Create session**：提交 prompt 并启动。
- 可选 `requirePlanApproval=true`：先出 plan 再等待放行。
- 可选 `automationMode=AUTO_CREATE_PR`：完成后自动开 PR。

3) **Get session**：轮询 `state` + 获取 `outputs.pullRequest.url`。

4) **Approve plan**：当 `state=AWAITING_PLAN_APPROVAL`。

5) **Send message**：在 `AWAITING_USER_FEEDBACK` 或你需要追加约束时。

---

## 状态机（用于调用方编排）

- `AWAITING_PLAN_APPROVAL`：需要人/调用方审阅并 approve
- `AWAITING_USER_FEEDBACK`：需要补充信息/修正范围
- `COMPLETED` / `FAILED`：终态

---

## 产物获取

- 推荐：通过 session outputs 获取 PR URL（如果启用了 AUTO_CREATE_PR，或任务本身生成 PR）。
- 需要文本结果：通过 activities 读取 `agentMessaged` / `planGenerated`。
