---
name: 9yu-prd-splitter
description: 把 docs/ 下的需求文档（PRD、原型说明、会议纪要等）按 SDD 拆成 specs/F*/requirements.md、design.md、tasks.md 和 specs/INDEX.md。用于 9yu 工作流 W2，或用户要求"拆需求/拆任务/写 spec"时。
---

# 9yu-prd-splitter：需求 → SDD 规格

## 输入
- `docs/` 下的所有需求材料。需求只有一段话也照样拆。
- 已有代码：先摸清技术栈、目录结构和现有约定，设计要贴合现状，不要另起炉灶。
- `AGENTS.md` 中的项目约定和铁律，以及 W1 预读的同技术栈全局经验（L3）。设计时主动避开其中记录的坑。

## 步骤

1. **划分 Feature**：按用户可感知的完整能力来切，每个 Feature 能独立验收。编号从 `F01` 开始，目录命名为 `specs/F01-<英文slug>/`。顺序按依赖排列：基础能力在前。
   - 小需求只拆 1 个 Feature 也可以，不要为拆而拆。
   - 新项目的脚手架（初始化工程、依赖、测试框架）放进第一个 Feature，作为它的前几个 task。
2. **写 requirements.md**（这个 Feature 要做什么）：
   ```markdown
   # F01 <名称> · Requirements
   ## 背景与目标
   ## 用户故事
   - US1 作为<角色>，我希望<能力>，以便<价值>
   ## 验收标准
   - AC1 [US1] Given … When … Then …
   ## 不做（范围外）
   ## 假设与待确认
   ```
3. **写 design.md**（怎么做）：
   ```markdown
   # F01 <名称> · Design
   ## 方案概述
   ## 模块与文件
   ## 接口契约      <!-- 前后端都有时必须写：路径、方法、请求/响应字段与类型、错误码 -->
   ## 数据模型      <!-- 表/字段/索引，或前端状态结构 -->
   ## 关键决策      <!-- 方案取舍及理由 -->
   ## 测试策略      <!-- 单测、集成测试、E2E 脚本（@playwright/test，e2e/Fxx-*.spec.ts）分别覆盖哪些 AC -->
   ```
4. **写 tasks.md**（按什么顺序做）。格式必须严格遵守，状态脚本靠正则解析：
   ```markdown
   # F01 <名称> · Tasks
   <!-- [ ] 待办  [x] 完成  [!] 阻塞（行末写原因） -->

   - [ ] T01 [infra] 初始化项目脚手架与测试框架
     - 文件: package.json, vite.config.ts, src/main.ts
     - 依赖: -
     - AC: `npm test` 能运行；`npm run build` 成功
   - [ ] T02 [backend] 实现 POST /api/todos
     - 文件: server/routes/todos.ts, server/routes/todos.test.ts
     - 依赖: T01
     - AC: 对应 requirements AC1；单测覆盖成功与参数校验失败
   ```
   规则：
   - 层级标签只能用：`[frontend]`、`[backend]`、`[data]`、`[test]`、`[infra]`。
   - `文件:` 列出预计新建或修改的文件。并行批次靠这一项判断冲突，**尽量写准**。
   - `依赖:` 写同一 Feature 内的 task 编号，没有就写 `-`；跨 Feature 的依赖通过 Feature 顺序保证。
   - `AC:` 必须可以验证（能跑的命令，或可观察的页面行为），并对应 requirements 中的 AC 编号。
   - 粒度：每个 task 约 15–60 分钟，一个 Feature 通常 3–10 个 task。
   - 有意让前端和后端 task 能够并行：先定接口契约，前端 task 只依赖契约，不依赖后端实现。
   - **Web 项目**：
     - 有 UI 验收标准的 `[frontend]` task，要在 `文件:` 中列出对应的 `e2e/<Fxx>-<slug>.spec.ts`，由这个 task 同时写好 E2E 用例；
     - 同一 Feature 内，多个 task 共用一个 spec 文件时，只能写进其中一个 task 的文件列表，避免并行批次冲突；
     - 新项目在脚手架 task 中接入 `@playwright/test`：安装依赖、建 `playwright.config.ts`、配好 `webServer`。
5. **写 specs/INDEX.md**：
   ```markdown
   # Specs Index
   | # | Feature | 目录 | 状态 | 进度 |
   |---|---|---|---|---|
   | F01 | 待办清单 | specs/F01-todo-list | 待开发 | 0/5 |
   ```
   状态取值：待开发 / 进行中 / 已完成 / 部分阻塞。
6. **自检**：
   - requirements 中的每条 AC 都至少被一个 task 覆盖；
   - 依赖不成环；
   - 每个 task 都有 文件、依赖、AC 三项。

## 输出给 Queen
返回一段摘要：Feature 列表（每个 task 数）、关键设计决策，以及不超过 5 条需要人确认的假设。
