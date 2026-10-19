# log-edits

A Claude Code hook that records every file Claude writes. It feeds the `claude-edits` tmux popup in [dotfiles](https://github.com/LionelPinheiroDuarte/dotfiles), which lists the files Claude recently touched, shows what it changed in them, and opens them in Vim.

## Shortcuts

Prefix is `Ctrl-a`.

| Key | Action |
|-----|--------|
| `prefix + e` | Open the popup: files from all sessions |
| `prefix + E` | Open the popup: only files under the current pane's directory |

Inside the popup:

| Key | Action |
|-----|--------|
| type | Fuzzy-filter the list |
| `enter` | Open the file in Vim, in a new tmux window |
| `ctrl-d` | Open `vimdiff` before/after in a new tmux window |
| `ctrl-f` | Toggle the preview between the diff and the full file |
| `esc` | Close |

In `vimdiff`, the left side is Claude's "before" (read-only), the right side is the real file:

| Key | Action |
|-----|--------|
| `]c` / `[c` | Next / previous change |
| `do` | *diff obtain*: pull the "before" version of this hunk into the file — undoes Claude's change |
| `:diffupdate` | Recompute the diff after editing |
| `:qa` | Close both sides |

## What "before" and "after" mean

- **Before**: the file as it was right before Claude's **first** edit, in the **most recent session** that touched it.
- **After**: the file on disk **now**.

So the diff is everything that changed since Claude started on that file, including any edits you made after it. A file created by Claude is diffed against an empty file.

The list shows each file once, newest first, with the age of its last edit (`5m`, `2h`, `3d`). Deleted files are left out.

## How it works

```
Claude Edit/Write ──► PostToolUse hook (log-edits.py)
                          ├─ append to   ~/.local/state/claude/edits.log
                          └─ snapshot to ~/.local/state/claude/snapshots/

prefix + e ──► claude-edits (fzf popup) ── reads both ──► diff / vimdiff / vim
```

Claude Code passes the hook a JSON payload on stdin after each edit. Its `tool_response.originalFile` holds the full file content **before** that edit (`null` when the edit created the file). The hook stores it:

```
~/.local/state/claude/
├── edits.log                          # <epoch>\t<session_id>\t<path>, one line per edit
└── snapshots/                         # mode 0700: may hold old copies of sensitive files
    └── <session_id>/
        └── <sha1 of path>/
            ├── path                   # the absolute path, in clear
            ├── new                    # present if Claude created the file
            ├── 0001-<tool_use_id>.orig
            └── 0002-<tool_use_id>.orig
```

Every edit gets its own `.orig`, but the popup only uses the first one of a session. The rest is kept for a possible per-edit view later.

Sessions older than **30 days** are deleted by the hook itself, at most once a day (tracked by `snapshots/.last-purge`).

## Limits

- Only `Edit`, `Write` and `NotebookEdit` are recorded. A file Claude changes through `Bash` (`sed`, `>`, …) does not show up as an entry. If the same file was first touched by an `Edit` in that session, the diff still includes those later `Bash` changes, since "after" is the file on disk.
- Files edited before snapshots existed show `no snapshot` and the full file; `ctrl-d` does nothing for them.
- The hook never blocks Claude or writes to the session: no stdout, always exit 0, standard library only.

## Setup

Wired in dotfiles' [`.claude/settings.json`](https://github.com/LionelPinheiroDuarte/dotfiles/blob/main/.claude/settings.json):

```json
{
  "matcher": "Edit|Write|NotebookEdit",
  "hooks": [{
    "type": "command",
    "command": "f=$HOME/repos/github/agents/hooks/log-edits/log-edits.py; [ -f \"$f\" ] && python3 \"$f\" || true"
  }]
}
```

The guard makes the hook a no-op on a machine without this repo. The popup needs `fzf`, and optionally `batcat` for the file preview — both installed by the dotfiles Ansible playbook.
