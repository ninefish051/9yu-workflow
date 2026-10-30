# 9yu 工作流（项目级）

## 文件分布

```
<项目根>/
├── .mcp.json                       Playwright MCP 配置（默认不启用，排查问题时用 /mcp 开启）
└── .claude/
    ├── commands/   9yu-workflow.md（主流程：mermaid 流程图 + 节点表 + 全局约定）
    │               9yu-status.md · 9yu-pause.md
    │   └── 9yu-workflow-nodes/   10 个节点：w1-init · w2-split · w3-feature · batch-plan
    │                             w4a-serial · w4b-parallel · w5-codex-cr · w6-test · w7-commit · w8-deliver
    ├── skills/     9yu-prd-splitter · 9yu-lesson-keeper · 9yu-doc-syncer
    │               9yu-frontend-engineer · 9yu-backend-engineer · 9yu-data-engineer
    ├── agents/     9yu-frontend-dev · 9yu-backend-dev · 9yu-reviewer
    ├── settings.json         Stop 钩子 → 9yu/scripts/stop_guard.py；默认关闭 playwright MCP
    └── 9yu/scripts/          state.py · stop_guard.py · lessons.py · codex_review.sh · precommit_secret_scan.sh
```

依赖：Codex 审查使用全局安装的 `codex@openai-codex` 插件（openai/codex-plugin-cc）。

## 命令

| 命令 | 作用 |
|---|---|
| `/9yu-workflow [项目目录] [--auto] [需求描述]` | 启动工作流，或从断点续跑 |
| `/9yu-status` | 查看进度 |
| `/9yu-pause` | 暂停 |

## 迁移到全局 `~/.claude/`

1. 复制文件：
   ```bash
   cp -R .claude/commands/9yu-* ~/.claude/commands/      # 含 9yu-workflow-nodes/ 目录
   cp -R .claude/skills/9yu-* ~/.claude/skills/
   cp .claude/agents/9yu-* ~/.claude/agents/
   cp -R .claude/9yu/scripts ~/.claude/9yu/
   ```
   命令文件里的脚本路径和节点路径都会自动定位：优先找项目内的 `.claude/9yu`，找不到就用 `~/.claude/9yu`，所以迁移后不用改命令文件。
2. 在 `~/.claude/settings.json` 的 `hooks.Stop` 中加入：
   ```json
   python3 "$HOME/.claude/9yu/scripts/stop_guard.py"
   ```
3. 注册全局 MCP：
   ```bash
   claude mcp add --scope user playwright -- npx -y @playwright/mcp@latest
   ```
4. 删除项目里的这些副本：`.claude/commands/9yu-*`、`skills/9yu-*`、`agents/9yu-*`、`9yu/`，`settings.json` 中的 Stop 钩子，以及 `.mcp.json` 中的 playwright。不删的话，全局和项目两套会同时生效。
