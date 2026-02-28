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
6. **Governance Capsule**：每个任务必须包含 `## Governance Capsule (MANDATORY)` 段，声明权威规则来源（项目规范 + Output Contract + Integration Router）与输出契约字段。详见各模板的 §4.5。
7. **PD-OUT v1（输出必须分层）**：Report/文档输出必须遵循 Progressive Disclosure 结构：Head Anchor (≤7 lines) → How to Read This → Index/Summary → Details → Tool Outputs (Offloaded) → Plan Update Targets。单个代码块 ≤60 行，超出部分 offload 到独立文件并用 RefSpec 指针引用。

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

## JIT Context Hydration（已实现 — GATE-2b）

`dispatch_prompt_pack.py` 在 GATE-2b 阶段自动解析 `{{ HYDRATE: ... }}` 宏并替换为实际文件内容。

在 prompt 的任意位置，可使用以下宏语法替代手动粘贴代码：

```markdown
### Code Context
{{ HYDRATE: src/auth/api.py:L10-L50 }}
{{ HYDRATE: 11_webos/backend/services/diagnosis_service_v4.py:L1-L30 }}
```

**Governance Capsule 推荐用法**：在 Capsule 中用 HYDRATE 注入关键规范片段（如 Output Contract、Integration Router 的门禁映射），做到"全量规范可达，prompt 仍保持精炼"。
