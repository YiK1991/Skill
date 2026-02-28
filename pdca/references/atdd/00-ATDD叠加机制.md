# PDCA + ai-driven-dev（ATDD 门禁）叠加机制

本说明把 ai-driven-dev 作为一种"可执行门禁"机制叠加到 PDCA（Plan/Do/Check/Act）之上。

## 适用情形

- 需求/缺陷存在边界条件与权限/异常处理
- Debug 场景容易出现跨层乱改、扩散修改
- 需要 CI/合并门禁来保证可信交付

## 最小落地路径（推荐）

### Plan

1) **Repo Contract 摘要**（3-7条约束）
- 读取：`gemini.md` / `agent.md` / `ARCHITECTURE.md` / `CLAUDE.md` / `docs/architecture/*` / `docs/boundaries/*`
- 输出 Contract Summary，并在后续 Architecture Lock 中引用条款编号

2) **生成验收清单 `TEST_PLAN.md`**（真源）
- 使用稳定主键：`ATDD-xxx`
- 覆盖：正常 / 异常 / 权限

3) **Gate A（对账）必须先通过**
```bash
python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd --parity-only
```

### Do

1) **同名测试（暗号）**
- 测试显示名必须为：`ATDD-xxx <条目文字>`

2) **严格 TDD 红-绿循环**
- 没见红灯，不得写生产实现

3) **限次自修（≤5轮）**
- 每轮：读取失败 -> 根因 -> 最小改动 -> 重跑
- 连续两轮无收敛，且根因是方案问题：触发变更控制（见下）

### Check

1) 运行 ATDD 测试，产出 JUnit
2) Gate B（JUnit 布尔校验，无副作用）
```bash
python3 scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd \
  --junit test-results/junit.xml --strict --dry-run
```
3) Gate D（文档门禁）
```bash
python3 scripts/doc_gate.py --base origin/main --strict
```

### Act

- 若出现"换题/重来"（目标或假设改变），必须走 **变更控制**：
  - 不允许悄悄删除旧条目
  - 旧条目只能标记：`CANCELLED(reason: ...)` 或 `REPLACED(by: ATDD-xxx)`
  - 变更后先过 Gate C（审计），再过 Gate A（对账）

## 变更控制（换题/重来）

触发条件（满足任一项即可）：
- 新信息导致原目标/假设不成立
- 某条目不可断言、不可测试
- 连续2轮自修无进展且根因是方案问题
- 需要跨围栏/跨层修改

必需输出（用于审计记录）：

```
Change Declaration
- What: <变更内容>
- Why: <变更原因>
- Impact: <影响范围>
- Affected items: <受影响的ATDD条目>
```

审计门禁：
```bash
python3 scripts/atdd_gate.py --plan TEST_PLAN.md --base origin/main --audit --strict
```

## 工具的可追溯性

- Gate A 会把问题定位到：清单行号 / 测试文件与行号
- Gate B 会把失败定位到：清单行号 /（可选）JUnit case 名称
- Gate D 会列出触发门禁的变更文件清单
