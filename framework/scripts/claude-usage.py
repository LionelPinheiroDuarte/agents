#!/usr/bin/env python3
"""Track the shell commands Claude Code runs, across sessions and projects.

Claude Code deletes transcripts after 30 days, so `collect` copies what matters
(command shape, project, session, date, output size) into a persistent history.
`report` ranks the command combinations that keep coming back: candidates for a
project script (one project) or a generic one (several projects).

Usage:
  claude-usage collect [--quiet]
  claude-usage report [--project PATH] [--since DAYS] [--min-sessions N] [--top N] [--json]

`report` runs `collect` first.
"""

import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import shlex
import sys

TRANSCRIPTS = os.path.expanduser("~/.claude/projects/*/**/*.jsonl")
DATA_DIR = os.path.expanduser(os.environ.get("CLAUDE_USAGE_DIR", "~/.local/share/claude-usage"))
HISTORY = os.path.join(DATA_DIR, "history.jsonl")
SEEN = os.path.join(DATA_DIR, "seen-ids.txt")

# CLIs whose first one or two words after the program name say what it does.
MULTI_LEVEL = {
    "git", "gh", "eas", "docker", "npm", "pnpm", "yarn", "kubectl", "terraform",
    "aws", "go", "cargo", "sentry-cli", "tmux", "expo", "systemctl", "pip", "uv",
    "poetry", "helm", "gcloud", "az", "make",
}
WRAPPERS = {"npx", "sudo", "time", "timeout", "env", "exec", "nohup", "bunx"}
NOISE = {"cd", "echo", "true", "sleep", "export", "set", "clear", ":", "printf", "test", "[",
         "for", "do", "done", "if", "then", "else", "fi", "while", "read", "case", "esac"}
# Plumbing: reading and filtering text. Not a behaviour on its own, unless it targets
# something telling (dependencies, project docs), which becomes a marker.
PLUMBING = {"cat", "head", "tail", "sed", "grep", "ls", "wc", "sort", "uniq", "awk", "tr", "cut",
            "xargs", "find", "tee", "less", "stat", "file", "diff", "basename", "dirname", "realpath",
            "mkdir", "rm", "cp", "mv", "touch", "chmod", "ln", "jq", "column", "nl", "type", "which"}
MARKERS = [
    (re.compile(r"node_modules"), "search dependencies"),
    (re.compile(r"(^|/)(CLAUDE\.md|README\.md|docs/|memory/|sessions\.md|roadmap\.md)"), "read project docs"),
    (re.compile(r"\.(log|output)\b|/tasks/"), "read logs"),
]
SECRET_ASSIGN = re.compile(r"\b([A-Z0-9_]*(TOKEN|KEY|SECRET|PASSWORD|PASS)[A-Z0-9_]*)=(\S+)", re.I)
LONG_SECRET = re.compile(r"\b(?=[A-Za-z0-9_\-]*\d)(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{32,}\b")


def redact(cmd):
    cmd = SECRET_ASSIGN.sub(lambda m: f"{m.group(1)}=***", cmd)
    return LONG_SECRET.sub("***", cmd)


def git_root(path):
    path = os.path.abspath(os.path.expanduser(path))
    while path not in ("/", ""):
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
    return None


def project_of(cmd, cwd):
    m = re.match(r"\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd)
    target = m.group(1).strip("\"'") if m else cwd
    if m and not os.path.isabs(os.path.expanduser(target)):
        target = os.path.join(cwd, target)
    root = git_root(target) if target else None
    return root or os.path.abspath(os.path.expanduser(cwd or "~"))


def strip_heredocs(cmd):
    """Drop heredoc bodies: they hold file contents, not commands."""
    kept, end = [], None
    for line in cmd.splitlines():
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        kept.append(line)
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", line)
        if m:
            end = m.group(1)
    return "\n".join(kept)


def segments(cmd):
    """Split a compound command into its simple commands."""
    text = " ".join(cmd.splitlines())
    return [s.strip() for s in re.split(r"&&|\|\||;|\|(?!\|)|\$\(|`", text) if s.strip()]


def shape_of(segment):
    try:
        words = shlex.split(segment, posix=True)
    except ValueError:
        words = segment.split()
    words = [w for w in words if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w)]  # VAR=value prefixes
    while words and (words[0] in WRAPPERS or re.match(r"^-|^\d+[smh]?$", words[0])):
        words = words[1:]
    if not words:
        return None
    prog = os.path.basename(words[0])
    if prog in ("node", "python", "python3") and len(words) > 1:
        if words[1] == "-m" and len(words) > 2:
            prog, words = words[2], words[2:]
        elif "/" in words[1]:  # node node_modules/typescript/bin/tsc
            prog, words = os.path.basename(words[1]).removesuffix(".js"), words[1:]
    if prog in NOISE or not re.match(r"^[\w.\-]+$", prog):
        return None
    if prog in PLUMBING:
        for pattern, marker in MARKERS:
            if any(pattern.search(w) for w in words[1:]):
                return marker
        return None
    args = [w for w in words[1:] if not w.startswith("-")]
    parts = [prog]
    if prog in MULTI_LEVEL:
        for a in args[:2]:
            if re.match(r"^[a-z][a-z0-9:_\-]*$", a) and len(a) < 25:
                parts.append(a)
            else:
                break
    return " ".join(parts)


def load_seen():
    if not os.path.exists(SEEN):
        return set()
    with open(SEEN) as f:
        return {line.strip() for line in f}


def collect(quiet=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    seen = load_seen()
    pending, new = {}, []
    for path in glob.glob(TRANSCRIPTS, recursive=True):
        session = os.path.basename(path).removesuffix(".jsonl")
        with open(path, errors="ignore") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = (entry.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "tool_use" and item.get("name") == "Bash":
                        if item["id"] in seen:
                            continue
                        cmd = (item.get("input") or {}).get("command", "")
                        pending[item["id"]] = (session, entry.get("timestamp", "")[:10], entry.get("cwd") or "", cmd)
                    elif item.get("type") == "tool_result" and item.get("tool_use_id") in pending:
                        tid = item["tool_use_id"]
                        session_id, date, cwd, cmd = pending.pop(tid)
                        out = item.get("content")
                        new.append({
                            "id": tid, "session": session_id, "date": date,
                            "project": project_of(cmd, cwd), "cmd": redact(strip_heredocs(cmd))[:2000],
                            "out_chars": len(json.dumps(out)) if out is not None else 0,
                        })
                        seen.add(tid)
    with open(HISTORY, "a") as h:
        for rec in new:
            h.write(json.dumps(rec, ensure_ascii=False) + "\n")
    with open(SEEN, "a") as s:
        for rec in new:
            s.write(rec["id"] + "\n")
    if not quiet:
        print(f"collect: {len(new)} new commands -> {HISTORY}")


def report(args):
    collect(quiet=True)
    since = (dt.date.today() - dt.timedelta(days=args.since)).isoformat() if args.since else ""
    only = git_root(args.project) or os.path.abspath(args.project) if args.project else None
    home = os.path.expanduser("~")

    records = []
    with open(HISTORY) as f:
        for line in f:
            rec = json.loads(line)
            if rec["date"] >= since and (only is None or rec["project"] == only):
                rec["shapes"] = [s for s in (shape_of(seg) for seg in segments(rec["cmd"])) if s]
                records.append(rec)

    def stats():
        return {"calls": 0, "sessions": set(), "projects": set(), "out": 0, "example": ""}

    singles, combos = collections.defaultdict(stats), collections.defaultdict(stats)
    for rec in records:
        uniq = sorted(set(rec["shapes"]))
        keys = [(singles, s) for s in uniq]
        if len(uniq) >= 2:
            keys.append((combos, " + ".join(uniq)))
        for table, key in keys:
            st = table[key]
            st["calls"] += 1
            st["sessions"].add(rec["session"])
            st["projects"].add(rec["project"])
            st["out"] += rec["out_chars"]
            example = " ".join(rec["cmd"].split())
            if not st["example"] or len(example) < len(st["example"]):
                st["example"] = example

    def rank(table):
        rows = [(k, v) for k, v in table.items() if len(v["sessions"]) >= args.min_sessions]
        return sorted(rows, key=lambda kv: (len(kv[1]["sessions"]), kv[1]["out"]), reverse=True)[: args.top]

    def short(p):
        return p.replace(home, "~")

    if args.json:
        out = {}
        for name, table in (("singles", singles), ("combos", combos)):
            out[name] = [{"shape": k, "calls": v["calls"], "sessions": len(v["sessions"]),
                          "projects": sorted(short(p) for p in v["projects"]), "out_chars": v["out"],
                          "example": v["example"]} for k, v in rank(table)]
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return

    total_out = sum(r["out_chars"] for r in records)
    sessions = {r["session"] for r in records}
    print(f"{len(records)} commands, {len(sessions)} sessions, ~{total_out // 4000}k tokens of output"
          f"{' since ' + since if since else ''}{' in ' + short(only) if only else ''}")

    for title, table in (("Repeated combinations (script candidates)", combos), ("Repeated commands", singles)):
        print(f"\n## {title} — seen in >= {args.min_sessions} sessions")
        print(f"{'sess':>4} {'calls':>5} {'~ktok':>5} {'proj':>4}  shape")
        for key, v in rank(table):
            generic = " [generic]" if len(v["projects"]) >= 2 else ""
            print(f"{len(v['sessions']):>4} {v['calls']:>5} {v['out'] // 4000:>5} {len(v['projects']):>4}  {key}{generic}")
            print(f"{'':>22}e.g. {v['example'][:110]}")
    print("\n[generic] = seen in several projects: candidate for a script in agents/framework/scripts.")
    print("Others: candidate for a command in the project's own script (or its .proj-check / .proj-status).")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--quiet", action="store_true")
    r = sub.add_parser("report")
    r.add_argument("--project", help="limit to one project (any path inside its repo)")
    r.add_argument("--since", type=int, help="only the last N days")
    r.add_argument("--min-sessions", type=int, default=3)
    r.add_argument("--top", type=int, default=15)
    r.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.cmd == "collect":
        collect(args.quiet)
    else:
        report(args)


if __name__ == "__main__":
    main()
