# ATDD 门禁参考索引

本目录提供 "ai-driven-dev" 的 ATDD 门禁机制资料，用于叠加到 PDCA 工作流（Plan/Do/Check/Act）上。

## 快速入口

- `00-ATDD叠加机制.md`：PDCA + ATDD 的最小落地路径（推荐先读）
- `01-验收清单规范.md`：TEST_PLAN.md 写法（真源）
- `02-同名测试规则.md`：测试显示名逐字一致（暗号）
- `03-Gate机器对账.md`：Gate A 规则（对账）
- `04-严格TDD流程.md`：红-绿-重构铁律
- `05-自修循环规则.md`：限次自修（≤5轮）
- `06-JUnit自动勾选.md`：Gate B（JUnit 驱动结果）
- `07-架构锁与契约.md`：Architecture Lock（防 Debug 乱改）
- `08-门禁落地指南.md`：pre-push/CI 配置
- `09-救火模式.md`：大面积失败时的分组修复

## 脚本位置

- `scripts/atdd_gate.py`：Gate A/B/C（对账、JUnit 校验、Plan 变更审计）
- `scripts/doc_gate.py`：Gate D（文档门禁）

