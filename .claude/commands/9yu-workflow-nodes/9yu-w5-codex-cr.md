---
description: "【9yu 节点】Codex CR · 每批一轮（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W5 · Codex CR · 每批一轮

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：W4a 或 W4b 完成

## 步骤

1. `state set phase=W5`
2. **送审前密钥检查**：`bash "$KIT/scripts/precommit_secret_scan.sh" "P"`。有命中就先处理（改为读环境变量，或加入 .gitignore），处理完再送审。
3. 送审：`bash "$KIT/scripts/codex_review.sh" "P" "P/.9yu/reviews/batch-<n>.md"`，Bash 超时设为 600000。
   - 这个脚本调用 codex-plugin-cc 的 `codex-companion.mjs review --wait --scope working-tree`，与 `/codex:review` 同源，审查的是本批未提交的改动。
   - 退出码 3（没装 codex 插件或 CLI）或执行失败 → 改为派 `9yu-reviewer` 子代理审查 `git diff` 加未跟踪文件，审查口径相同。
4. **Claude 裁决**：逐条判断。
   - 采纳 → 立即修复。
   - 不采纳 → 必须写明理由。
   - 把裁决结果追加到 `specs/Fxx/reviews.md`：
     ```
     ## Batch <n>（T01,T02）· <日期>
     | # | 级别 | 意见 | 裁决 | 理由/处理 |
     ```

## 出口
- 裁决和修复完成 → **W6**。修复后**不再送 Codex**，每批只审一轮。
