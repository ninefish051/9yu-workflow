#!/usr/bin/env python3
"""9yu 分层经验库工具。

  L2 项目经验库  <项目>/docs/lessons/*.md            编号 Pxxx，提交进仓库
  L3 全局经验库  ~/.claude/9yu/lessons/<技术栈>.md   编号 Gxxx，跨项目共享

条目格式（一行一条）:
  - (P012) [踩坑][vitest,env] 内容 → 做法（来源: <项目>/F01/T03, 2026-10-30, 命中 0）

用法:
  lessons.py init <project>                                   建 L2/L3 目录与说明文件
  lessons.py search <project> [--stack a,b] [--tags a,b] [--kw x,y] [--limit 15]
  lessons.py hit <project> <ID> [<ID> ...]                    命中次数 +1
  lessons.py next-id <project> P|G                            下一个可用编号
  lessons.py stats <project>                                  规模、晋升候选、超限文件
"""
import re
import sys
from pathlib import Path

import os
GLOBAL_DIR = Path(os.environ.get("NINEYU_LESSONS_GLOBAL", Path.home() / ".claude" / "9yu" / "lessons"))
ENTRY_RE = re.compile(r"^- \(([PG])(\d+)\)\s*\[([^\]]+)\](?:\[([^\]]*)\])?\s*(.*)$")
HITS_RE = re.compile(r"命中\s*(\d+)")
FILE_LIMIT = 50
AGENTS_LIMIT = 30
SKIP = {"README.md", "INDEX.md"}

L2_README = """# 项目经验库（L2）

由 9yu 工作流 W7 的 `9yu-lesson-keeper` 维护，**按需检索，不全量加载**。

| 文件 | 内容 |
|---|---|
| pitfalls.md | 踩坑：现象 + 根因 + 正确做法 |
| decisions.md | 决策：选了什么、为什么 |
| patterns.md | 可复用：可照抄的模式、工具函数位置 |
| env.md | 环境：项目级命令、端口、依赖版本（本机专属信息写 CLAUDE.local.md） |
| archive.md | 归档：过时或低频条目 |

条目格式：`- (P012) [类别][标签1,标签2] 内容（来源: 项目/Fxx/Tyy, 日期, 命中 N）`
"""

L3_README = """# 全局经验库（L3）

跨项目共享，按技术栈分文件（如 vitest.md、playwright.md、react.md、prisma.md），通用经验写 general.md。
由 9yu 工作流 W7 写入，W1/W3 按项目技术栈检索。

条目格式：`- (G012) [类别][标签1,标签2] 内容（来源: 项目/Fxx/Tyy, 日期, 命中 N）`
"""


def l2_dir(project):
    return Path(project).resolve() / "docs" / "lessons"


def lesson_files(project, stack=None):
    files = []
    d2 = l2_dir(project)
    if d2.is_dir():
        files += [p for p in sorted(d2.glob("*.md")) if p.name not in SKIP and p.name != "archive.md"]
    if GLOBAL_DIR.is_dir():
        for p in sorted(GLOBAL_DIR.glob("*.md")):
            if p.name in SKIP or p.name == "archive.md":
                continue
            if stack and p.stem not in stack and p.stem != "general":
                continue
            files.append(p)
    return files


def parse(path):
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = ENTRY_RE.match(line)
        if not m:
            continue
        hm = HITS_RE.search(line)
        out.append({
            "id": f"{m.group(1)}{m.group(2)}",
            "layer": m.group(1),
            "num": int(m.group(2)),
            "category": m.group(3).strip(),
            "tags": [t.strip().lower() for t in (m.group(4) or "").split(",") if t.strip()],
            "text": m.group(5),
            "hits": int(hm.group(1)) if hm else 0,
            "file": path,
            "line": i,
            "raw": line,
        })
    return out


def csv(argv, flag):
    if flag in argv:
        return [x.strip().lower() for x in argv[argv.index(flag) + 1].split(",") if x.strip()]
    return []


def short(path):
    home = str(Path.home())
    s = str(path)
    return "~" + s[len(home):] if s.startswith(home) else s


def cmd_init(project):
    d2 = l2_dir(project)
    d2.mkdir(parents=True, exist_ok=True)
    if not (d2 / "README.md").exists():
        (d2 / "README.md").write_text(L2_README, encoding="utf-8")
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    if not (GLOBAL_DIR / "README.md").exists():
        (GLOBAL_DIR / "README.md").write_text(L3_README, encoding="utf-8")
    stacks = sorted(p.stem for p in GLOBAL_DIR.glob("*.md") if p.name not in SKIP and p.name != "archive.md")
    print(f"L2: {d2}")
    print(f"L3: {short(GLOBAL_DIR)}  已有技术栈文件: {', '.join(stacks) or '无'}")


def cmd_search(project, argv):
    stack, tags, kws = csv(argv, "--stack"), csv(argv, "--tags"), csv(argv, "--kw")
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 15
    want_tags = set(tags) | set(stack)
    results = []
    for f in lesson_files(project, stack or None):
        for e in parse(f):
            score = 2 * len(want_tags & set(e["tags"]))
            low = e["raw"].lower()
            score += sum(1 for k in kws if k in low)
            # 技术栈文件本身就与项目相关：给基础分，保证同栈经验能被召回
            if e["layer"] == "G" and f.stem in stack:
                score += 1
            if score > 0 or not (want_tags or kws):
                results.append((score, e["hits"], e))
    results.sort(key=lambda r: (-r[0], -r[1], r[2]["id"]))
    if not results:
        print("未命中经验")
        return
    for score, _, e in results[:limit]:
        print(f"{e['raw'][2:]}  ⟨{short(e['file'])}:{e['line']}⟩")
    if len(results) > limit:
        print(f"…另有 {len(results) - limit} 条低相关条目未列出")


def find_all(project):
    entries = []
    for f in lesson_files(project):
        entries += parse(f)
    return entries


def cmd_hit(project, ids):
    want = {i.upper() for i in ids}
    done = set()
    for e in find_all(project):
        if e["id"] not in want:
            continue
        lines = e["file"].read_text(encoding="utf-8").splitlines()
        line = lines[e["line"] - 1]
        if HITS_RE.search(line):
            line = HITS_RE.sub(lambda m: f"命中 {int(m.group(1)) + 1}", line, count=1)
        else:
            line = line.rstrip("）)") + ", 命中 1）"
        lines[e["line"] - 1] = line
        e["file"].write_text("\n".join(lines) + "\n", encoding="utf-8")
        done.add(e["id"])
    print(f"已 +1: {', '.join(sorted(done)) or '无'}")
    missing = want - done
    if missing:
        print(f"未找到: {', '.join(sorted(missing))}")


def cmd_next_id(project, layer):
    layer = layer.upper()
    files = []
    if layer == "P":
        d = l2_dir(project)
        files = list(d.glob("*.md")) if d.is_dir() else []
    else:
        files = list(GLOBAL_DIR.glob("*.md")) if GLOBAL_DIR.is_dir() else []
    nums = [e["num"] for f in files for e in parse(f) if e["layer"] == layer]
    print(f"{layer}{(max(nums) + 1 if nums else 1):03d}")


def cmd_stats(project):
    print("== 文件规模（每个文件上限 %d 条）" % FILE_LIMIT)
    for f in lesson_files(project):
        n = len(parse(f))
        flag = "  ⚠ 超限，需合并或归档" if n > FILE_LIMIT else ""
        print(f"  {short(f)}: {n}{flag}")
    agents = Path(project) / "AGENTS.md"
    if agents.exists():
        n = len(agents.read_text(encoding="utf-8").splitlines())
        flag = "  ⚠ 超过 %d 行，精简或下放到 L2" % AGENTS_LIMIT if n > AGENTS_LIMIT else ""
        print(f"  AGENTS.md: {n} 行{flag}")
    print("== 晋升候选")
    any_c = False
    for e in find_all(project):
        if e["layer"] == "P" and e["hits"] >= 3:
            print(f"  {e['id']} 命中 {e['hits']} → 候选 AGENTS.md 铁律（若为技术栈通用，则晋升 L3）")
            any_c = True
        elif e["layer"] == "P" and e["hits"] >= 2:
            print(f"  {e['id']} 命中 {e['hits']} → 若为技术栈通用，候选晋升 L3")
            any_c = True
    if not any_c:
        print("  无")


def main(argv):
    if len(argv) < 2 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, project, rest = argv[0], argv[1], argv[2:]
    if cmd == "init":
        cmd_init(project)
    elif cmd == "search":
        cmd_search(project, rest)
    elif cmd == "hit":
        cmd_hit(project, rest)
    elif cmd == "next-id":
        cmd_next_id(project, rest[0] if rest else "P")
    elif cmd == "stats":
        cmd_stats(project)
    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
