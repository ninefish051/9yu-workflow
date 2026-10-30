---
description: "【9yu 节点】交付（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W8 · 交付

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：所有 Feature 已处理完

## 步骤

1. `state set phase=W8 w8_rounds=+1`
2. **全量测试**：
   - 运行项目的完整测试、构建和 lint。
   - Web 项目再运行 `npx playwright test --reporter=line`，跑全部 E2E 脚本，覆盖所有 Feature 的回归。
   - 被标为 `test.fixme` 的用例不算失败，但要写进交付报告的「遗留问题」。
3. **分支整体审查（一轮）**：
   ```
   bash "$KIT/scripts/codex_review.sh" "P" "P/.9yu/reviews/final-<round>.md" --base <base_branch> --focus "<全部 Feature 的目标与关键 AC 摘要；重点：需求符合度、安全、数据丢失、并发>"
   ```
   - 这个脚本走 codex-plugin-cc 的 `adversarial-review`，会质疑整体设计与实现取舍。
   - 没有 Codex 时由 `9yu-reviewer` 兜底。
   - 按 W5 的方式裁决，结果记入 `specs/INDEX.md` 末尾的「最终审查」小节。
4. **失败回流判断**（见出口）。
5. **文档同步**：使用 **`9yu-doc-syncer`** skill，让 README、docs/ 与实际实现保持一致，并生成 `docs/9yu-delivery-report.md`。
6. 最终提交：`git add -A && git commit -m "docs: 9yu 交付报告"`。
7. 执行 `state finish "P"`。
8. 向用户输出交付总结：
   - 分支名与提交数；
   - Feature 和 task 的完成、阻塞情况；
   - 阻塞项及原因；
   - 新增的经验条数；
   - 报告路径；
   - 合并方式（例如 `git checkout <base> && git merge --no-ff <work_branch>`）。

## 出口
- 全量测试失败，或审查发现必须修复的严重问题，且 `w8_rounds` < 2：把问题转成新 task（编号接在后面，层级照常标注，子项加 `来源: W8-<round>`），追加到对应 Feature 的 tasks.md → **W3**
- 通过，或已满 2 轮（剩余问题写进交付报告的「遗留问题」）→ 执行第 5–8 步 → **结束**
