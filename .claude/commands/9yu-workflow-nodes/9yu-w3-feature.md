---
description: "【9yu 节点】进入 Feature（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W3 · 进入 Feature

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：specs 已确认；或上一个 Feature 完成；或 W8 把问题回流成新 task

## 步骤

1. `state set phase=W3`
2. 读取 `specs/INDEX.md`，按顺序找到第一个还有 `[ ]` task 的 Feature `Fxx`，执行 `state set current_feature=Fxx`，并把 INDEX 中它的状态改为「进行中」。
3. 读取这个 Feature 的 requirements.md、design.md、tasks.md。
4. **检索经验**（L1 铁律已经随 AGENTS.md 自动加载，这里只检索 L2 和 L3）：
   ```
   python3 "$KIT/scripts/lessons.py" search "P" --stack <state 中的 stack> --kw <本 Feature 的 3–6 个关键词> --limit 15
   ```
   - 关键词从 Feature 名、模块名、design.md 中的关键技术点里取，例如 `localstorage,表单,路由`。
   - 把命中条目的 ID 记下来：`state set lessons_hit="P001,G003"`。之后派子代理时，要附上这些条目的原文；W7 会对实际用上的条目计数。
5. 分析 `[ ]` task 的依赖关系，找出当前可以开工的 task（依赖已全部 `[x]`）。依赖的 task 处于 `[!]` 阻塞时，下游 task 也标为 `[!]`，原因写「依赖 Tyy 阻塞」。

## 出口
- 有可开工的 task → **BATCH 批次规划**
- 这个 Feature 的 task 全部是 `[x]` 或 `[!]` → 回到 **W7** 第 4 步做「Feature 完成」判断
