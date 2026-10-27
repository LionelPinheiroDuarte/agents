# log-edits

A Claude Code hook that records every file Claude writes. It feeds the [`claude-edits`](../../tools/claude-edits/README.md) tmux popup, which lists the files Claude recently touched, shows what it changed in them, and opens them in Vim.

## Shortcuts

Prefix is `Ctrl-a`.

| Key | Action |
|-----|--------|
| `prefix + e` | Open the popup: files from all sessions |
| `prefix + E` | Open the popup: only files of the current pane's repo |

Inside the popup (the list, **before** pressing `enter`):

| Key | Action |
|-----|--------|
| type | Fuzzy-filter the list; the preview shows Claude's diff for the selected file |
| `enter` | Open the file in Vim, in a new tmux window |
| `ctrl+d` | Open the file directly in the `,d` diff view |
| `ctrl+f` | Toggle the preview between the diff and the full file (the active view is highlighted in the preview header) |
| `ctrl+g` | Toggle the list between the current repo and all sessions |
| `ctrl+y` | Copy the file's full path (tmux buffer and system clipboard, through OSC 52) |
| `ctrl+/` | Hide or show the preview |
| `esc` | Close |

Keys are lowercase: `ctrl+d` is Ctrl and `d`, **without** Shift. Windows Terminal grabs `ctrl+shift+d` (duplicate tab) and `ctrl+shift+f` (search) before tmux sees them. Once in Vim, `ctrl+d`/`ctrl+f` are Vim's own scroll keys.

Inside Vim (a file opened from the popup):

| Key | Action |
|-----|--------|
| `,d` | Claude's changes as a `git diff`-style view (`-` red, `+` green) in a full-screen tab; `q` or `,d` closes it |
| `,D` | Side-by-side diff: Claude's "before" read-only on the left, the real file on the right; `,D` again closes it |

The `,d` view diffs the buffer, so unsaved edits are included. In the side-by-side view:

| Key | Action |
|-----|--------|
| `]c` / `[c` | Next / previous change |
| `do` | *diff obtain*: pull the "before" version of this hunk into the file — undoes Claude's change |
| `:diffupdate` | Recompute the diff after editing |
| `q` | Close both sides (plain `:q` only closes one) |

A file Claude created has no "before": `,d` and `,D` just say so.

## What "before" and "after" mean

- **Before**: the file as it was right before Claude's **first** edit, in the **most recent session** that touched it.
- **After**: the file on disk **now**.

So the diff is everything that changed since Claude started on that file, including any edits you made after it. A file created by Claude is diffed against an empty file.

The list shows each file once, under the Claude session that touched it last (*dernière session*, *session précédente*, then older ones), newest first. Each row has a mark, the path, the lines added and removed since "before", and the age of the last edit (`5m`, `2h`, `3d`):

| Mark | Meaning |
|------|---------|
| `✚` | Created by Claude |
| `~` | Modified |
| `↶` | Reverted since: the file matches "before" again (`annulé`) |
| `?` | No snapshot, so no diff (`sans diff`) |

Deleted files are left out. Paths are shortened for display: relative to the repo when the list is filtered (its name is the badge in the prompt), else `repo/path` under `$GITHUB` or `~/…` under home; when still too wide for the list, whole leading directories are dropped (`…/scratchpad/notes.md`) so the file name stays readable. The filter matches what is displayed, session headers disappear as soon as something is typed, and the cursor steps over them.

The preview starts with a header: the path, when Claude last edited it, `+added -removed`, the number of hunks and of Claude edits. The diff below has the old and new line numbers, a full-width background on changed lines, and after each `@@` the enclosing top-level line (function, class, import). A file Claude created is shown in full.

## How it works

```
Claude Edit/Write ──► PostToolUse hook (log-edits.py)
                          ├─ append to   ~/.local/state/claude/edits.log
                          └─ snapshot to ~/.local/state/claude/snapshots/

prefix + e ──► claude-edits (fzf popup) ── reads both ──► diff preview / vim + ,d
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
- Files edited before snapshots existed show `?` / `sans diff` and the full file; `ctrl+d`, `,d` and `,D` do nothing for them.
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

The guard makes the hook a no-op on a machine without this repo. The popup and its Vim side live in [`tools/claude-edits/`](../../tools/claude-edits/). They need `fzf` 0.66 or later — Debian's package is too old, so the dotfiles Ansible playbook installs the official binary (`--tags fzf`); the popup says so and exits on an older one — and use `batcat` for the file preview when present (numbered plain text otherwise). Nothing else: the diff is drawn by the script itself.
