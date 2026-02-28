# Gate 机器对账

## 核心理念

**不是 AI 自己"检查一下觉得OK"，而是程序做"外卖单对外卖盒"。**

## Gate A：一致性检查

检查 TEST_PLAN.md 条目集合 = 测试文件中测试名集合

```bash
python scripts/atdd_gate.py --plan TEST_PLAN.md --tests-root tests/atdd --parity-only
```

输出：`true` 或 `false` + exit code (0/1)

### 能防止的问题

| 问题         | 说明               |
| ------------ | ------------------ |
| 漏写测试     | 清单有但测试没有   |
| 测试名不匹配 | 暗号失效           |
| 范围漂移     | 多写了清单外的测试 |

## Gate B：JUnit 自动勾选

基于 JUnit XML 结果自动更新清单：

```bash
python scripts/atdd_gate.py --plan TEST_PLAN.md --junit test-results/junit.xml --tick --strict
```

效果：
- 通过的条目 `[ ]` → `[x]`
- 输出 `true/false`（全通过才 true）
- `--strict` 模式下跳过也算失败

## 工作原理

1. 从 TEST_PLAN.md 解析所有 `- [ ] xxx` 条目
2. 从测试文件提取测试显示名（支持 JS/TS/Go/Java/Python）
3. 比较两个集合是否完全一致
4. 多一个或少一个都返回 `false`

## 目录约定

- 验收测试：`tests/atdd/`
- Gate 工具：`scripts/atdd_gate.py`
- JUnit 输出：`test-results/junit.xml`
