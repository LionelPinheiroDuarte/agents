#!/usr/bin/env python3
"""log-edits — Claude Code PostToolUse(Edit|Write|NotebookEdit) hook.

Appends every file Claude writes to a tab-separated log, so a tmux popup
(`claude-edits` in dotfiles) can list the most recently touched files and
open one in Vim.

Log: ${XDG_STATE_HOME:-~/.local/state}/claude/edits.log
Line: <epoch>\t<session_id>\t<absolute path>

Never blocks or talks back to the session: no stdout, always exit 0. Pure
stdlib (no jq): the hook must never hard-depend on a tool that might be absent
on a fresh machine.
"""
import json
import os
import sys
import time


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return

    cwd = data.get("cwd") or os.getcwd()
    path = os.path.abspath(os.path.join(cwd, os.path.expanduser(path)))

    state = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
    log = os.path.join(state, "claude", "edits.log")

    try:
        os.makedirs(os.path.dirname(log), exist_ok=True)
        with open(log, "a") as f:
            f.write(f"{int(time.time())}\t{data.get('session_id', '')}\t{path}\n")
    except OSError:
        pass


if __name__ == "__main__":
    main()
