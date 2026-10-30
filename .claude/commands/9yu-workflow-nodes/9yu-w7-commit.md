---
description: "【9yu 节点】标记 + 沉淀 + 提交（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W7 · 标记 + 沉淀 + 提交

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：W6 结束（通过或已标阻塞）

## 步骤

1. `state set phase=W7`
2. **标记**：在 tasks.md 中把本批通过的 task 从 `[ ]` 改为 `[x]`，并更新 `specs/INDEX.md` 中这个 Feature 的进度（如 `3/7`）。
3. **沉淀**：使用 **`9yu-lesson-keeper`** skill，依次完成：
   - 给实际用上的经验计数（`lessons hit`）；
   - 提炼本批经验，每批最多 3 条；
   - 判断每条写进 L1、L2、L3 还是 CLAUDE.local.md；
   - 去重；
   - 晋升和归档（`lessons stats`）。
   
   注意：L2 的改动会跟本批一起提交；L3 在全局目录，不进项目仓库。
4. **提交**：`git add -A && git commit -m "feat(<Fxx>): <T01,T02> <简述>"`。只要有 `[!]` task，提交信息末尾加 `[blocked: T03]`。**不 push。**
5. **Feature 完成判断**：这个 Feature 已经没有 `[ ]` task 时，把 INDEX 中的状态改为「已完成」；有 `[!]` 时改为「部分阻塞」，然后提交 `git commit -am "chore(<Fxx>): feature 完成"`。

## 出口
- 本 Feature 还有 `[ ]` task → **BATCH**（取下一批）
- 本 Feature 已完成，且还有别的 Feature 有 `[ ]` task → **W3**
- 全部 Feature 都处理完 → **W8**
