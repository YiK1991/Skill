# Prompt Envelope — 路由指南

> 根据任务 intent 选择对应的专用模板。**禁止混用**。

| Intent                           | 模板文件                           | 角色                                       |
| -------------------------------- | ---------------------------------- | ------------------------------------------ |
| `implement` / `test` / `release` | **`prompt-envelope-implement.md`** | 开发者 — 可修改代码                        |
| `review` / `research`            | **`prompt-envelope-review.md`**    | 审计员 — **严禁修改代码**，只输出 .md 报告 |

## 通用规则（两种模板共享）

1. **一个 prompt 只覆盖一个方面**
2. **必须先读规范文件**（gemini.md / agent.md / rules.md / 模块级规范）
3. **必须提供相关计划/调研文档链接**
4. **分支规则**：在特性分支工作，通过 PR 提交，禁止直接推 main
5. **远程可见性**：prompt 引用的文件必须已推送到远程仓库

## "进一步修改" 消息模板

### sendMessage（同 session 迭代）

```markdown
**[plan:<module> run:<RUN-ID> aspect:<ASPECT-ID> ctx:<CTX-ID>]**

- Scope: `<file/dir list>`
- Change request:
  1. …
- Constraints: …
- Done criteria: …
```

### PR 评论（session 已完成后）

```markdown
@Jules

**[plan:<module> run:<RUN-ID> aspect:<ASPECT-ID>]**

请在本 PR 分支上修改：
1. …

约束：只修改 `<file list>`；遵守 `gemini.md`；附带测试输出。
```

---

## JIT Context Hydration（Phase 2 — 宏替换预告）

> 当前阶段：仅文档化语法。`dispatch_prompt_pack.py` 尚未实现解析。

在 prompt 的 Code Context 段中，可使用以下宏语法替代手动粘贴代码：

```markdown
### Code Context
{{ HYDRATE: src/auth/api.py:L10-L50 }}
{{ HYDRATE: 11_webos/backend/services/diagnosis_service_v4.py:L1-L30 }}
```

实现后，`dispatch_prompt_pack.py` 会在发送前自动读取本地文件并将宏替换为实际代码。本地 AI 只需写一行指针，Jules 收到 100% 精准的源码，避免截断和 token 浪费。
