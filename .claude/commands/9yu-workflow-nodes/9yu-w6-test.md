---
description: "【9yu 节点】W6 自动化测试 · E2E 脚本（由 /9yu-workflow 调度；也可单独运行，只执行本节点）"
disable-model-invocation: true
---

# 节点 W6 · 自动化测试 · E2E 脚本

> 本节点遵守 `/9yu-workflow` 中的「全局约定」（KIT、state、目录结构、tasks.md 格式）。单独运行时，先读取 `.claude/commands/9yu-workflow.md` 的「全局约定」部分。

**进入条件**：W5 完成；或本节点修复后重跑

**原则**：验收标准（AC）一律**写成可以重复运行的测试脚本**，由脚本来验证，不靠模型临场点页面。脚本跑起来不耗 token、结果稳定，W8 全量回归时可以直接复用。只有排查问题时，才让模型操作浏览器。

## 步骤

1. `state set phase=W6`
2. **补齐测试**：本批每条 AC 都要有对应的测试。W4 已经写了的就复用，缺的现在补上。
   - **后端 / 库 / CLI**：用项目的单元测试或集成测试框架。
   - **Web 前端**：用 `@playwright/test` 写 E2E 脚本，放在 `e2e/<Fxx>-<slug>.spec.ts`。要求如下：
     - 测试名带上 AC 编号，例如 `test('AC2 勾选后显示为已完成', …)`。
     - 定位元素时优先用 `getByRole`、`getByLabel`、`getByText`，必要时用 `getByTestId`。不要用 CSS 层级选择器或 `nth`。
     - 断言用 `expect(...)` 自带的自动等待，不要写 `waitForTimeout`。
     - 每个测试互相独立：自己准备数据，不依赖其它测试的执行顺序。
3. **首次接入 Playwright**（项目里还没有 `playwright.config.*` 时才做）：
   - 安装：`npm i -D @playwright/test && npx playwright install chromium`。
   - 新建 `playwright.config.ts`，要点如下：
     - 配置 `webServer`，让测试自动启动、关闭开发服务器（填 `command`、`url`、`reuseExistingServer: true`）；
     - 只跑 chromium；
     - 开启 `screenshot: 'only-on-failure'` 和 `trace: 'retain-on-failure'`。
   - 在 `package.json` 中加脚本 `"test:e2e": "playwright test"`。
   - 把 `test-results/`、`playwright-report/` 加入 `.gitignore`。
4. **运行测试**：
   - 先运行项目的单元测试命令。
   - Web 项目再运行 `npx playwright test e2e/<Fxx>-*.spec.ts --reporter=line`，只跑本 Feature 的脚本。
5. **失败排查**（按成本从低到高，前一种能定位问题就不用往下走）：
   1. 读测试输出里的报错和断言差异。
   2. 读 `test-results/<用例>/` 下的失败截图（用 Read 查看 png）和 `error-context.md`（失败时的页面结构）。
   3. 还是定位不了，再让模型操作浏览器复现：
      - 有 Claude in Chrome（`mcp__claude-in-chrome__*` 工具）时优先用它；
      - 否则用 Playwright MCP。它默认没有启用，需要的话提示用户运行 `/mcp` 开启 `playwright`。
      
      复现只用来定位问题，修完后仍然以测试脚本通过为准。
6. 有设计稿（Figma 链接）时，可以用 Figma MCP 读取设计做视觉对照，对照结果写进 reviews.md。

## 出口
- **全部通过** → **W7**。测试脚本跟着本批代码一起提交。
- **未通过，且 `w6_attempts` < 3** → `state set w6_attempts=+1`，就地修复后重跑本节点（不再送 Codex）。
  - 只能修改代码，或者修改确实写错了的测试。**禁止为了让测试通过而放宽断言或删掉测试**。
- **未通过，且已修复 3 次**：
  - 失败只影响本批 task：把这些 task 标为 `[!] 测试未通过：<一句话原因>`，保留代码，失败的用例标为 `test.fixme` 并写明原因 → **W7**
  - 导致原有测试回归：先执行 `git stash push -u -m "9yu-blocked-<Fxx>-batch<n>"` 撤回本批改动，把 task 标为 `[!] 已撤回（stash: 9yu-blocked-…）：<原因>` → **W7**
