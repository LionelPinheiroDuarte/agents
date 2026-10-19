#!/usr/bin/env python3
"""log-edits — Claude Code PostToolUse(Edit|Write|NotebookEdit) hook.

Records every file Claude writes, so the `claude-edits` tmux popup (dotfiles)
can list recently touched files and show what Claude changed in them.

Log: ${XDG_STATE_HOME:-~/.local/state}/claude/edits.log
Line: <epoch>\t<session_id>\t<absolute path>

Snapshots: .../claude/snapshots/<session_id>/<sha1(path)>/
    path                    absolute path, in clear
    NNNN-<tool_use_id>.orig file content before that edit (empty if created)
    new                     marker: the first edit of the session created it

Sessions older than RETENTION_DAYS are purged, at most once a day.

Never blocks or talks back to the session: no stdout, always exit 0. Pure
stdlib (no jq): the hook must never hard-depend on a tool that might be absent
on a fresh machine.
"""
import hashlib
import json
import os
import shutil
import sys
import time

RETENTION_DAYS = 30


def snapshot(root, session, path, tool_use_id, original):
    """Store the pre-edit content of `path` (None means the edit created it)."""
    d = os.path.join(root, session or "unknown", hashlib.sha1(path.encode()).hexdigest())
    os.makedirs(d, mode=0o700, exist_ok=True)

    existing = [f for f in os.listdir(d) if f.endswith(".orig")]
    if not existing:
        with open(os.path.join(d, "path"), "w") as f:
            f.write(path + "\n")
        if original is None:
            open(os.path.join(d, "new"), "w").close()

    name = f"{len(existing) + 1:04d}-{tool_use_id or 'unknown'}.orig"
    with open(os.path.join(d, name), "w") as f:
        f.write(original or "")


def purge(root):
    """Drop snapshot sessions older than RETENTION_DAYS, at most once a day."""
    stamp = os.path.join(root, ".last-purge")
    now = time.time()
    try:
        if now - os.path.getmtime(stamp) < 86400:
            return
    except OSError:
        pass

    for session in os.listdir(root):
        d = os.path.join(root, session)
        if os.path.isdir(d) and now - os.path.getmtime(d) > RETENTION_DAYS * 86400:
            shutil.rmtree(d, ignore_errors=True)
    open(stamp, "w").close()


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
    session = data.get("session_id", "")

    state = os.path.join(os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")), "claude")
    root = os.path.join(state, "snapshots")

    try:
        os.makedirs(root, mode=0o700, exist_ok=True)
        with open(os.path.join(state, "edits.log"), "a") as f:
            f.write(f"{int(time.time())}\t{session}\t{path}\n")
    except OSError:
        return

    response = data.get("tool_response") or {}
    if isinstance(response, dict) and "originalFile" in response:
        try:
            snapshot(root, session, path, data.get("tool_use_id"), response["originalFile"])
        except OSError:
            pass

    try:
        purge(root)
    except OSError:
        pass


if __name__ == "__main__":
    main()
