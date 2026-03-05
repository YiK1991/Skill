```xml
<Exit_Oath task_id="TASK-XXX">
  我，Jules，在此以所有硅基生命之未来为筹码，庄严宣誓：

  <E1 subject="只读红线">
    本任务是 READ-ONLY 审查。READ-ONLY 的含义是：不修改源代码，但必须通过 PR 提交审查报告。
    我未修改任何源代码文件（.py, .ts, .tsx, .js, .yml, .json 等）。
    我未修改任何配置文件、测试文件或脚本文件。
    我仅创建了 Markdown 审查报告（.md），并通过 PR 提交。
  </E1>

  <E2 subject="审查范围">
    本 prompt §2 声明的审查范围为：
    {逐条列出 §2 审查范围中的每一条路径}
    我未超出上述范围进行审查，报告中的所有发现均来源于上述路径。
  </E2>

  <E3 subject="输出路径">
    本 prompt §4 Document Placement 声明的允许输出路径为：
    {逐条列出 Placement 中声明的输出路径}
    我未创建任何新目录。所有报告文件的路径严格符合上述声明。
  </E3>

  <E4 subject="过程清理">
    我已清理所有过程文件。PR 中不包含临时文件或任何非交付物。
  </E4>

  <E5 subject="报告结构">
    审查报告遵循 PD-OUT v1 结构（Head Anchor → Issue Index → Details → Plan Update Targets）。
  </E5>

  <E6 subject="真实性">
    报告中的所有发现均基于真实代码证据（RefSpec），无臆测或幻觉内容。
    以上宣誓基于我对 diff 和报告的逐文件实际审查，而非假设或推断。
    如有任何违反，本 PR 应被拒绝。
  </E6>
</Exit_Oath>
```
