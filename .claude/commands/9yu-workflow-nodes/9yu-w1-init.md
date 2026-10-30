---
description: "【9yu 节点】初始化（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W1 · 初始化

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：工作流启动，或断点续跑

## 步骤

1. 解析参数 `$ARGUMENTS`，确定项目目录 `P`（转成绝对路径）。如果目录不存在就创建。
2. 先读 `state get`：
   - 如果 `phase=awaiting_spec_review`：说明上次停在人工检查点。用 AskUserQuestion 询问「specs 已确认，开始开发 / 我改过 specs，重新校验 / 取消」，按回答处理后再继续。
   - 如果是其它进行中的阶段：属于**断点续跑**，向用户说一句「从 <阶段/下一个 task> 继续」后直接跳到对应节点。
3. 执行 `state init "P" [--auto]`，然后 `state set phase=W1`。
4. 读取 `AGENTS.md`、`CLAUDE.md`（都可能不存在），扫描 `docs/` 和 `specs/`，弄清项目形态：技术栈、包管理器、测试/构建/lint 命令、是否有 Web 前端。
5. **分层经验库衔接**（分层规则见 `9yu-lesson-keeper` skill）：
   - **L1**：确保根目录有 `AGENTS.md`（没有就按下方模板创建），并确保 `CLAUDE.md` 中有一行 `@AGENTS.md`（没有就追加，CLAUDE.md 不存在就新建）。
     - 已有的 AGENTS.md 超过 30 行，或者里面有旧格式的经验条目时，按分层规则把它们迁移到 L2 或 L3，只留下约定和铁律。
   - **L2 / L3**：执行 `python3 "$KIT/scripts/lessons.py" init "P"`，建好 `docs/lessons/` 和 `~/.claude/9yu/lessons/`，同时会列出全局已有哪些技术栈文件。
   - **本机信息**：`CLAUDE.local.md` 不存在时，新建一个空文件（`state init` 已把它加进 `.gitignore`）。
   - **技术栈**：把识别出的技术栈记成小写标签，例如 `state set stack="react,vite,vitest,playwright"`。
     - 新项目要等 W2 拆完需求、确定技术栈后再记。
     - 标签名尽量与 L3 已有的文件名对齐，比如 `vitest` 对应 `vitest.md`。
   - **预读全局经验**：执行 `python3 "$KIT/scripts/lessons.py" search "P" --stack <stack> --limit 20`，把同技术栈的全局经验读一遍，用来指导 W2 的设计和拆分。
6. 需求输入：`docs/` 下没有需求文档、但参数里有需求描述时，把描述写进 `docs/prd.md`。两者都没有时，用 AskUserQuestion 向用户要需求。
7. Git：
   - 不是 git 仓库就执行 `git init`，再做一次初始提交。
   - 记下当前分支作为 `base_branch`。
   - 工作区有未提交改动时，先用 AskUserQuestion 问用户怎么处理（提交 / stash / 中止），不要擅自丢弃。
   - 新建工作分支 `9yu/<yyyyMMdd>-<slug>` 并切过去（续跑时已有分支则直接切换）。执行 `state set base_branch=… work_branch=…`。
8. 检查 Codex：审查通过 **openai/codex-plugin-cc**（`codex@openai-codex` 插件）进行。
   - 执行 `find ~/.claude/plugins -name codex-companion.mjs | head -1` 定位它，再用 `node <该文件> setup --json -C "P"` 确认 codex CLI 已安装且已登录。
   - 结果记入 `state set codex=true|false`。
   - 不可用时：提示用户先 `/plugin install codex@openai-codex` 并运行 `/codex:setup`。本次 W5/W8 改用 `9yu-reviewer` 子代理兜底，不中断流程。
9. 判断 specs 是否完整：执行 `state progress "P"`。`specs 完整: 是` 的条件是每个 Feature 都有 requirements、design、tasks 三个文件，并且每个 task 都带 `AC:`。

AGENTS.md 模板：
```markdown
# AGENTS.md

## 项目约定
<!-- 技术栈、目录约定、测试/构建命令 -->

## 铁律
<!-- 每次开工都必须遵守的规则，≤10 条；由 9yu 工作流从经验库晋升。全文 ≤30 行 -->

## 经验库
- 本项目经验：`docs/lessons/`（按需检索，不必全读；条目带 [类别][标签]，可 grep 标签）
- 跨项目经验：`~/.claude/9yu/lessons/<技术栈>.md`
```

## 出口
- specs 完整 → **W3**（断点续跑）
- specs 不完整 → **W2**
