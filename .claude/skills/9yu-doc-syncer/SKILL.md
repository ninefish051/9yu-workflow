---
name: 9yu-doc-syncer
description: 交付前同步项目文档（README、docs/）与实际实现，并生成 docs/9yu-delivery-report.md 交付报告。用于 9yu 工作流 W8，或用户要求"同步文档/出交付报告"时。
---

# 9yu-doc-syncer：文档同步与交付报告

## 1. 同步文档

以**代码为准**，修正文档中过时或缺失的内容：
- **README**：项目简介、安装、启动、测试、构建命令（逐条实际运行验证），以及环境变量清单（只写变量名和用途，不写值）。
- **docs/**：接口文档、配置说明。只改与本次交付相关的部分，原始需求文档（PRD）**不要改**。
- **specs/**：实现过程中偏离了 design.md 的地方，在 design.md 末尾的「实现偏差」小节中写明原因。

## 2. 交付报告 `docs/9yu-delivery-report.md`

```markdown
# 9yu 交付报告 · <项目名> · <日期>

## 概览
- 分支: <work_branch>（基于 <base_branch>），提交 N 个
- Feature: 完成 a / 部分阻塞 b / 共 c；Task: 完成 x / 阻塞 y / 共 z

## Feature 明细
| Feature | 状态 | 进度 | 说明 |

## 验证结果
- 全量测试: <命令> → 通过/失败（数量）
- E2E/Playwright: 覆盖的主流程、截图路径
- 最终审查: Codex/9yu-reviewer，意见 n 条，采纳 m 条（详见 specs/INDEX.md）

## 阻塞与遗留问题
| 项 | 原因 | 建议处理 |

## 本次沉淀经验
| 层 | 新增 | 更新 | 晋升 | 归档 |
（L1 AGENTS.md 铁律 / L2 docs/lessons/ / L3 ~/.claude/9yu/lessons/，列出新增条目的 ID 和一句话摘要）

## 如何验收
<启动与验证步骤；合并命令：git checkout <base> && git merge --no-ff <work_branch>>
```

报告中的所有数字都要从 tasks.md、git log 和测试输出中实际统计，不要估算。
