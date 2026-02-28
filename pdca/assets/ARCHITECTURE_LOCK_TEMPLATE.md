# Architecture Lock

## Affected Scope
<本次问题/需求一句话描述>

## Files & Layers
| 文件      | 层级                                      |
| --------- | ----------------------------------------- |
| `<file1>` | UI / Interface / UseCase / Domain / Infra |
| `<file2>` | ...                                       |

## Allowed Changes (≤3 files)
1. `<file1>` - <改动说明>
2. `<file2>` - <改动说明>
3. `<file3>` - <改动说明>

## Red Lines (Must Hold)
- [ ] Library-first：先找现成方案
- [ ] 禁止垃圾桶模块 (utils/helpers/common/shared)
- [ ] 业务逻辑不进 UI
- [ ] Controller 不直接查 DB
- [ ] 依赖方向正确

## Boundary Check
- [ ] 本次改动在围栏内
- [ ] 无需 ADR-lite

---

> 如果无法在上述边界内完成修复，**STOP** 并填写 ADR-lite。
