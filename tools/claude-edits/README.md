# claude-edits

A tmux popup listing the files Claude Code recently wrote, with a diff of what Claude changed in the preview. `enter` opens the file in Vim, where `,d` shows a `git diff`-style view of Claude's changes and `,D` a side-by-side diff.

- `claude-edits` — the fzf popup
- `claude-edits.vim` — the Vim side (`,d`, `,D`), sourced when the popup opens a file

Its data comes from the [`log-edits`](../../hooks/log-edits/README.md) hook; the shortcuts, how the "before" file is chosen and the limits are documented there.

## Setup

The dotfiles Ansible playbook symlinks the script into `~/.local/bin` and installs `fzf` and `batcat`; the bindings live in dotfiles' [`.tmux.conf`](https://github.com/LionelPinheiroDuarte/dotfiles/blob/main/tmux/.tmux.conf):

```tmux
bind e display-popup -E -w 90% -h 80% -y '#{popup_pane_top}' "~/.local/bin/claude-edits"
bind E display-popup -E -w 90% -h 80% -y '#{popup_pane_top}' "~/.local/bin/claude-edits '#{pane_current_path}'"
```
