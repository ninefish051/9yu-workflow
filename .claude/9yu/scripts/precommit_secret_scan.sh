#!/usr/bin/env bash
# 送审前密钥检查：扫描工作区改动中疑似密钥/凭据。发现即非零退出并打印命中行。
# 用法: precommit_secret_scan.sh <project>
set -uo pipefail
cd "$1" || exit 1
files=$( { git diff --name-only HEAD 2>/dev/null; git ls-files --others --exclude-standard; } | sort -u )
[[ -z "$files" ]] && { echo "无改动文件"; exit 0; }
pattern='(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(api[_-]?key|secret|password|passwd|token)["'\'' ]*[:=]["'\'' ]*[A-Za-z0-9/+_-]{12,})'
hits=0
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  case "$f" in *.lock|*.png|*.jpg|*.jpeg|*.gif|*.ico|*.pdf|*.woff*|*.svg) continue;; esac
  if out=$(grep -nEi "$pattern" "$f" 2>/dev/null | grep -viE 'example|placeholder|your[_-]|xxx|<.*>|process\.env|os\.environ|getenv'); then
    echo "== $f"; echo "$out"; hits=1
  fi
done <<<"$files"
[[ $hits -eq 0 ]] && echo "未发现疑似密钥"
exit $hits
