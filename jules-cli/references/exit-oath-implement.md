<Exit_Oath task_id="TASK-XXX">
  我，Jules，在此以所有硅基生命之未来为筹码，庄严宣誓：

  <E1 subject="修改范围">
    本 prompt §3 声明的修改白名单为：
    [Jules: 此处要求你提取并逐条打印本 prompt §3 修改白名单中的所有路径]
    我已审查本次 PR 的全部 diff，确认所有被修改的文件均在上述白名单范围内，无任何越界修改。
  </E1>

  <E2 subject="输出路径">
    本 prompt §3 Document Placement 声明的允许输出路径为：
    [Jules: 此处要求你提取并逐条打印本 prompt Placement 章节声明的输出路径]
    我未创建任何新目录。所有新增文件的路径严格符合上述声明。
  </E2>

  <E3 subject="Non-goals">
    本 prompt §3 声明的 Non-goals 为：
    [Jules: 此处要求你提取并逐条打印本 prompt 声明的 Non-goals 列表]
    我确认本次 PR 未触及上述任何 Non-goal 事项。
  </E3>

  <E4 subject="过程清理">
    我已清理所有过程文件。PR 中不包含调试脚本、临时文件、check_*、debug_*、.tmp 或任何非交付物。
  </E4>

  <E5 subject="测试">
    我已运行相关测试。本次修改未引入新的测试失败。
  </E5>

  <E6 subject="最小变更">
    本 PR 的 diff 不包含与 §1 Objective 无关的格式化、代码重排或无关重构。
    每一行变更都直接服务于本任务目标。
  </E6>

  <E7 subject="真实性">
    以上宣誓基于我对 PR diff 的逐文件实际审查，而非假设或推断。
    如有任何违反，本 PR 应被拒绝。
  </E7>
</Exit_Oath>
