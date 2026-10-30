---
description: "【9yu 节点】Claude 串行开发 · Skills（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W4a · Claude 串行开发 · Skills

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：批次规划判定为串行批次

## 步骤

1. `state set phase=W4a`
2. 按 task 的层级加载对应的工程师 skill，由你自己逐个实现：

| 层 | skill |
|---|---|
| `[frontend]` | `9yu-frontend-engineer` |
| `[backend]` | `9yu-backend-engineer` |
| `[data]` | `9yu-data-engineer` |
| `[test]` / `[infra]` / 其它 | 不加载专门 skill，按项目现有约定实现 |

3. 实现时遵守 design.md 中的接口和数据约定。每个 task 写完后先跑一遍相关的局部检查（类型检查、lint、单测），再做下一个。

## 出口
- 本批全部实现完毕 → **W5**
