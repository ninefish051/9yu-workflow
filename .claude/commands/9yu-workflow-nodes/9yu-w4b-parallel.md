---
description: "【9yu 节点】并行开发 · SubAgent（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W4b · 并行开发 · SubAgent

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：批次规划判定为并行批次

## 步骤

1. `state set phase=W4b`
2. **在同一条消息里**并行派发子代理：`[frontend]` task 交给 `9yu-frontend-dev`，`[backend]` task 交给 `9yu-backend-dev`。每个子代理的 prompt 必须包含：
   - 项目目录、task 全文（含 AC）、相关的 design.md 片段，以及 W3 检索命中的经验条目原文（`lessons_hit`）；
   - **文件所有权**：「你只能修改以下文件：…；需要改其它文件时停下来，在报告里说明，不要自己改」；
   - 要求：不执行 git commit，不安装新依赖（确实需要时在报告里说明）；完成后报告改了哪些文件、自测结果、对接口做的假设。
3. **本地检查**：全部子代理返回后，执行 `git status --porcelain`，确认改动的文件 ⊆ 声明的文件，越界改动要逐一核查。然后跑整体的类型检查、lint 和构建。
4. **交叉校验**：对照 design.md，核对前端调用和后端实现的契约是否一致，包括路径、方法、字段名、类型、错误码。不一致的地方由你直接修正。
5. **Queen 收口**：整合以上结果；子代理报告中「需要 Queen 处理」的事项逐一处理掉，确认这个批次处于可以送审的状态。

## 出口
- 收口完成 → **W5**
