---
description: 查看 9yu 工作流进度（各 Feature 完成/阻塞/待办、当前阶段与下一个 task）
argument-hint: "[项目目录]"
---

项目目录为 `$ARGUMENTS`，未提供则用当前工作目录。工作流脚本目录 `KIT`：优先用 `<项目根>/.claude/9yu`；不存在时用 `~/.claude/9yu`（迁移到全局之后）。

执行：
1. `python3 "<KIT>/scripts/state.py" progress "<项目目录>"`
2. `python3 "<KIT>/scripts/state.py" get "<项目目录>"`（不存在可忽略）
3. 如有 `specs/INDEX.md`，读取它。

用一张简表汇报：阶段、分支、各 Feature 进度、阻塞项及原因（从 tasks.md 的 `[!]` 行摘取）、下一个 task。只汇报，不做任何修改。
