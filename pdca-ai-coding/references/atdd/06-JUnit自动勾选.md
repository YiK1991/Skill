# JUnit 自动勾选

## 核心理念

**勾选来自测试证据，不靠 AI 自觉。**

## 工作流程

1. 验收测试运行时输出 JUnit XML
2. Gate B 读取 XML，找到通过的测试
3. 自动将对应清单条目从 `[ ]` 改为 `[x]`

## 命令

```bash
# 生成 JUnit XML
pytest tests/atdd --junitxml=test-results/junit.xml
npm test -- --reporter=jest-junit

# 自动勾选
python scripts/atdd_gate.py --plan TEST_PLAN.md --junit test-results/junit.xml --tick --strict
```

## 输出格式要求

JUnit XML 中 `testcase` 的 `name` 属性必须与清单条目一致：

```xml
<testcase name="用户输入错误的Email格式" classname="...">
  <!-- 通过则无子元素 -->
</testcase>
```

## 各框架配置

### Jest
```json
// jest.config.js
{
  "reporters": [
    "default",
    ["jest-junit", { "outputDirectory": "test-results", "outputName": "junit.xml" }]
  ]
}
```

### PyTest
```bash
pytest --junitxml=test-results/junit.xml
```

### Go
```bash
go test -v ./... 2>&1 | go-junit-report > test-results/junit.xml
```

## 严格模式

`--strict` 标志下：
- 跳过 (skipped) 也算失败
- 清单中有但 JUnit 中没有 = 未运行 = 失败
- 必须所有条目都通过才返回 `true`
