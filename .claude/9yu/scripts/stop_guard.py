#!/usr/bin/env python3
"""Stop hook：9yu 工作流激活且未完成时，阻止 Claude 停下，让 Agent Loop 持续推进。

放行条件（任一满足即允许停止）：
  - 当前会话没有激活的 9yu 工作流
  - 处于需要人工的阶段（awaiting_spec_review / paused / done）
  - 连续 STALL_LIMIT 次拦截之间进度没有任何变化（防止死循环烧 token）
  - 单个工作流累计拦截超过 MAX_BLOCKS 次
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state as S  # noqa: E402

ALLOW_PHASES = {"awaiting_spec_review", "paused", "done"}
STALL_LIMIT = 3
MAX_BLOCKS = 300


def candidates(cwd):
    seen = []
    if cwd:
        seen.append(str(Path(cwd).resolve()))
    for p in S.load_registry():
        if p not in seen:
            seen.append(p)
    return seen


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    sid = data.get("session_id")
    cwd = data.get("cwd")

    for project in candidates(cwd):
        st = S.load_state(project)
        if not st or not st.get("active"):
            continue
        bound = st.get("session_id")
        if bound and bound != sid:
            continue  # 属于别的会话
        if not bound:
            st["session_id"] = sid
        if st.get("phase") in ALLOW_PHASES:
            S.save_state(project, st)
            return 0

        pg = S.progress(project)
        sig = f"{pg['done']}/{pg['blocked']}/{pg['todo']}|{st.get('phase')}|{st.get('current_batch')}|{st.get('w8_rounds')}"
        st["stall"] = st.get("stall", 0) + 1 if sig == st.get("last_sig") else 0
        st["last_sig"] = sig
        st["blocks"] = st.get("blocks", 0) + 1

        if st["stall"] >= STALL_LIMIT or st["blocks"] > MAX_BLOCKS:
            st["active"] = False
            st["phase_before_pause"] = st.get("phase")
            st["phase"] = "paused"
            st["pause_reason"] = "Stop hook 检测到连续无进展，自动暂停"
            S.save_state(project, st)
            print(json.dumps({
                "systemMessage": f"9yu：连续 {STALL_LIMIT} 次无进展，工作流已自动暂停。修复问题后运行 /9yu-workflow 续跑。"
            }, ensure_ascii=False))
            return 0

        S.save_state(project, st)
        if pg["todo"] > 0:
            todo_msg = f"还有 {pg['todo']} 个待办 task，下一个：{pg['next']}。"
        else:
            todo_msg = "所有 task 已处理，但 W8 交付尚未完成。"
        reason = (
            f"9yu 工作流尚未完成（阶段 {st.get('phase')}，项目 {project}）。{todo_msg}"
            "请按 /9yu-workflow 的 Agent Loop 继续推进，不要停下来汇报。"
            f"确实需要人工介入时，先运行 `python3 {Path(__file__).resolve().parent}/state.py pause \"{project}\"` 再说明原因。"
        )
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
