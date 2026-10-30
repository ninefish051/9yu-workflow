---
description: "【9yu 节点】拆分需求 · SDD（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W2 · 拆分需求 · SDD

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：W1 判断 specs 不完整；或在人工检查点被要求修改 specs

## 步骤

1. `state set phase=W2`
2. 使用 **`9yu-prd-splitter`** skill，把 `docs/` 中的需求拆成 `specs/F*/requirements.md | design.md | tasks.md`，并生成 `specs/INDEX.md`。
3. 自检：
   - 每个 task 都有 `文件:`、`依赖:`、`AC:`；
   - task 粒度控制在 15–60 分钟的工作量；
   - 依赖之间不能成环。
   
   最后用 `state progress "P"` 确认 `specs 完整: 是`。
4. 执行 `git add specs docs AGENTS.md CLAUDE.md .gitignore && git commit -m "spec: 9yu 拆分需求"`。
5. **人工检查点**（没有 `--auto` 时）：
   - 执行 `state set phase=awaiting_spec_review`。
   - 输出一段简短摘要：有几个 Feature、几个 task、关键设计决策、你拿不准的假设（最多 5 条）。
   - 告诉用户：「请检查 specs/，确认后回复"确认"，或重新运行 /9yu-workflow」，然后**停止本轮**。
   - 有 `--auto` 时：在摘要里列出假设，然后直接进入 W3。

## 出口
- 用户确认，或带 `--auto` → `state set phase=W3` → **W3**
- 用户要求修改 → 按意见修改 specs，再回到本节点第 3 步自检
