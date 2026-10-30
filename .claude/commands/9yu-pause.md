---
description: 暂停 9yu 工作流（Stop hook 不再拦截，可随时 /9yu-workflow 续跑）
argument-hint: "[项目目录]"
---

项目目录为 `$ARGUMENTS`，未提供则用当前工作目录。工作流脚本目录 `KIT`：优先用 `<项目根>/.claude/9yu`；不存在时用 `~/.claude/9yu`（迁移到全局之后）。

执行 `python3 "<KIT>/scripts/state.py" pause "<项目目录>"`，然后告诉用户：已暂停在哪个阶段/批次、工作区是否有未提交改动（`git status --short`），以及用 `/9yu-workflow <项目目录>` 续跑。
