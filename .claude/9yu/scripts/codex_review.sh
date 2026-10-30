#!/usr/bin/env bash
# 9yu Codex CR：通过 openai/codex-plugin-cc 的 codex-companion 运行一轮审查，输出写入文件。
# 用法:
#   codex_review.sh <project> <out_file>                                  工作区改动（W5，原生 review）
#   codex_review.sh <project> <out_file> --base BRANCH [--focus "重点"]   分支整体（W8，adversarial-review）
# 退出码: 0 成功；3 未安装 codex 插件或 codex CLI（调用方改用 9yu-reviewer 兜底）；其它为审查失败
set -uo pipefail

project="$1"; out="$2"; shift 2
base=""; focus=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) base="$2"; shift 2;;
    --focus) focus="$2"; shift 2;;
    *) shift;;
  esac
done

# 定位 codex-plugin-cc 的 companion 脚本（可用 NINEYU_CODEX_COMPANION 覆盖）
companion="${NINEYU_CODEX_COMPANION:-}"
if [[ -z "$companion" ]]; then
  companion=$(find "$HOME/.claude/plugins" -path '*codex*' -name codex-companion.mjs 2>/dev/null \
    | xargs ls -t 2>/dev/null | head -1)
fi
if [[ -z "$companion" || ! -f "$companion" ]]; then
  echo "未找到 codex-plugin-cc。安装: claude plugin marketplace add openai/codex-plugin-cc && claude plugin install codex@openai-codex" >&2
  exit 3
fi
if ! command -v codex >/dev/null 2>&1 || ! command -v node >/dev/null 2>&1; then
  echo "codex CLI 或 node 不可用，先运行 /codex:setup" >&2
  exit 3
fi

mkdir -p "$(dirname "$out")"
if [[ -n "$base" ]]; then
  node "$companion" adversarial-review --wait -C "$project" --base "$base" \
    ${focus:+"$focus"} >"$out" 2>"$out.log"
else
  node "$companion" review --wait -C "$project" --scope working-tree >"$out" 2>"$out.log"
fi
rc=$?
if [[ ! -s "$out" && -s "$out.log" ]]; then cp "$out.log" "$out"; fi
exit $rc
