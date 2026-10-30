---
description: "【9yu 节点】批次规划（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 BATCH · 批次规划

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：W3 找出了可开工的 task；或 W7 判断本 Feature 还有 task

## 步骤

1. 从可开工的 task 中挑出一个批次，执行 `state set current_batch="Fxx:T01,T02" batch_no=+1 w6_attempts=0 phase=BATCH`。
2. 判断走哪条路：

**同时满足以下全部条件 → 并行批次**
- 至少 2 个 task，层级只有 `[frontend]` 或 `[backend]`，即纯代码；
- 批次内的 task 互不依赖；
- 各 task 的 `文件:` 列表两两不重叠；
- 不涉及数据库迁移、测试基础设施、外部写入（第三方 API 写操作、发信、支付等）。

**否则 → 串行批次**：取 1–3 个 task（可以是一条依赖链）。

## 出口
- 并行批次 → **W4b**
- 串行批次 → **W4a**
