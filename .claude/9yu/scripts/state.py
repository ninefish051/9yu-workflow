#!/usr/bin/env python3
"""9yu 工作流状态与进度工具。

用法:
  state.py init <project> [--base BRANCH] [--auto]   初始化/激活工作流状态
  state.py get <project>                              输出 state.json
  state.py set <project> key=value [key=value ...]    更新状态（value 按 JSON 解析，失败则当字符串）
  state.py progress <project> [--json]                解析 specs/*/tasks.md 汇总进度
  state.py pause <project>                            暂停（Stop hook 不再拦截）
  state.py resume <project>                           恢复
  state.py finish <project>                           交付完成，注销
"""
import json
import os
import re
import sys
import time
from pathlib import Path

REGISTRY = Path.home() / ".claude" / "9yu" / "registry.json"
TASK_RE = re.compile(r"^\s*[-*]\s+\[( |x|X|!)\]\s+(T\d+[\w-]*)\s*(.*)$")
FEATURE_DIR_RE = re.compile(r"^F\d+")
AC_RE = re.compile(r"^\s+[-*]\s*(AC|验收)\s*[:：]")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def state_path(project):
    return Path(project).resolve() / ".9yu" / "state.json"


def load_state(project):
    p = state_path(project)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_state(project, st):
    p = state_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    st["updated"] = now()
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def load_registry():
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_registry(items):
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(sorted(set(items)), ensure_ascii=False, indent=2), encoding="utf-8")


def register(project, on=True):
    items = set(load_registry())
    root = str(Path(project).resolve())
    if on:
        items.add(root)
    else:
        items.discard(root)
    save_registry(items)


def ensure_gitignore(project):
    gi = Path(project) / ".gitignore"
    lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
    changed = False
    for item in (".9yu/", "CLAUDE.local.md"):
        if item not in lines:
            lines.append(item)
            changed = True
    if changed:
        gi.write_text("\n".join(lines) + "\n", encoding="utf-8")


def progress(project):
    """返回 {features:[...], total, done, blocked, todo, next}。"""
    specs = Path(project) / "specs"
    features = []
    nxt = None
    if specs.is_dir():
        for d in sorted(p for p in specs.iterdir() if p.is_dir() and FEATURE_DIR_RE.match(p.name)):
            tf = d / "tasks.md"
            counts = {"done": 0, "blocked": 0, "todo": 0}
            first_todo = None
            no_ac = []
            cur = None
            if tf.exists():
                for line in tf.read_text(encoding="utf-8").splitlines():
                    m = TASK_RE.match(line)
                    if not m:
                        if cur and AC_RE.match(line):
                            cur[1] = True
                        continue
                    if cur and not cur[1]:
                        no_ac.append(cur[0])
                    cur = [m.group(2), False]
                    mark, tid, title = m.group(1), m.group(2), m.group(3).strip()
                    if mark in "xX":
                        counts["done"] += 1
                    elif mark == "!":
                        counts["blocked"] += 1
                    else:
                        counts["todo"] += 1
                        if first_todo is None:
                            first_todo = f"{tid} {title}"
                if cur and not cur[1]:
                    no_ac.append(cur[0])
            features.append({
                "feature": d.name,
                "has_requirements": (d / "requirements.md").exists(),
                "has_design": (d / "design.md").exists(),
                "has_tasks": tf.exists(),
                "tasks_without_ac": no_ac,
                **counts,
                "next": first_todo,
            })
            if nxt is None and first_todo:
                nxt = f"{d.name}/{first_todo}"
    tot = lambda k: sum(f[k] for f in features)
    done, blocked, todo = tot("done"), tot("blocked"), tot("todo")
    return {
        "features": features,
        "total": done + blocked + todo,
        "done": done,
        "blocked": blocked,
        "todo": todo,
        "next": nxt,
        "specs_complete": bool(features) and all(
            f["has_requirements"] and f["has_design"] and f["has_tasks"]
            and (f["done"] + f["blocked"] + f["todo"]) > 0 and not f["tasks_without_ac"]
            for f in features
        ),
    }


def parse_value(v, old=None):
    if re.fullmatch(r"\+\d+", v) and isinstance(old, int):
        return old + int(v[1:])
    try:
        return json.loads(v)
    except Exception:
        return v


def main(argv):
    if len(argv) < 2 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, project = argv[0], argv[1]
    rest = argv[2:]
    project = str(Path(project).resolve())

    if cmd == "init":
        st = load_state(project) or {}
        if st.get("phase") == "paused":
            st["phase"] = st.pop("phase_before_pause", None) or "init"
            st.pop("pause_reason", None)
        if st.get("phase") == "done":
            st["phase"] = "init"
            st["w8_rounds"] = 0
        st["blocks"] = 0
        base = None
        if "--base" in rest:
            base = rest[rest.index("--base") + 1]
        st.update({
            "active": True,
            "project": project,
            "phase": st.get("phase") or "init",
            "auto": "--auto" in rest or st.get("auto", False),
            "base_branch": base or st.get("base_branch"),
            "work_branch": st.get("work_branch"),
            "current_feature": st.get("current_feature"),
            "current_batch": st.get("current_batch"),
            "batch_no": st.get("batch_no", 0),
            "w6_attempts": 0,
            "w8_rounds": st.get("w8_rounds", 0),
            "session_id": None,  # 由 Stop hook 首次触发时绑定
            "stall": 0,
            "last_sig": None,
            "created": st.get("created") or now(),
        })
        save_state(project, st)
        register(project, True)
        ensure_gitignore(project)
        print(json.dumps(st, ensure_ascii=False, indent=2))
        return 0

    st = load_state(project)
    if cmd == "progress":
        pg = progress(project)
        if "--json" in rest:
            print(json.dumps(pg, ensure_ascii=False, indent=2))
        else:
            print(f"总计 {pg['total']} · 完成 {pg['done']} · 阻塞 {pg['blocked']} · 待办 {pg['todo']}")
            for f in pg["features"]:
                miss = [n for n, k in (("requirements", "has_requirements"), ("design", "has_design"), ("tasks", "has_tasks")) if not f[k]]
                extra = f"  缺: {','.join(miss)}" if miss else ""
                if f["tasks_without_ac"]:
                    extra += f"  无AC: {','.join(f['tasks_without_ac'])}"
                print(f"  {f['feature']}: {f['done']}✓ {f['blocked']}! {f['todo']}☐  下一个: {f['next'] or '-'}{extra}")
            print(f"下一个 task: {pg['next'] or '无'}")
            print(f"specs 完整: {'是' if pg['specs_complete'] else '否'}")
            if st:
                print(f"阶段: {st.get('phase')} · 激活: {st.get('active')} · 分支: {st.get('work_branch')}")
        return 0

    if st is None:
        print(f"未找到状态文件: {state_path(project)}（先运行 init）", file=sys.stderr)
        return 1

    if cmd == "get":
        print(json.dumps(st, ensure_ascii=False, indent=2))
    elif cmd == "set":
        for kv in rest:
            k, _, v = kv.partition("=")
            st[k] = parse_value(v, st.get(k, 0))
        if any(kv.startswith(("phase=", "current_batch=", "current_feature=")) for kv in rest):
            st["stall"] = 0
        save_state(project, st)
        print(json.dumps({k.partition("=")[0]: st[k.partition("=")[0]] for k in rest}, ensure_ascii=False))
    elif cmd == "pause":
        st["active"] = False
        if st.get("phase") != "paused":
            st["phase_before_pause"] = st.get("phase")
            st["phase"] = "paused"
        save_state(project, st)
        print("已暂停：Stop hook 不再拦截。恢复请重新运行 /9yu-workflow。")
    elif cmd == "resume":
        st["active"] = True
        if st.get("phase") == "paused":
            st["phase"] = st.pop("phase_before_pause", None) or "init"
            st.pop("pause_reason", None)
        st["stall"] = 0
        st["blocks"] = 0
        st["session_id"] = None
        save_state(project, st)
        register(project, True)
        print("已恢复。")
    elif cmd == "finish":
        st["active"] = False
        st["phase"] = "done"
        save_state(project, st)
        register(project, False)
        print("工作流已完成并注销。")
    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
