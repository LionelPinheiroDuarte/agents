# claude-projects

Work with Claude Code on several projects at once: one tmux session per repo, each with a `claude` window and a `shell` window. A popup lists the projects; pick one to jump to its session, created on the fly. Open projects are remembered, and after a reboot `claude-projects restore` reopens them with `claude --continue`, so each one resumes its last conversation.

## Shortcuts

Prefix is `Ctrl-a`.

| Key | Action |
|-----|--------|
| `prefix + g` | Open the popup |

Inside the popup:

| Key | Action |
|-----|--------|
| type | Fuzzy-filter the list; the preview shows the branch, pending changes and last commits |
| `enter` | Jump to the project, creating its session if needed |
| `ctrl+x` | Close the project's session |

Marks in the list: `⟳` Claude is working · `✓` Claude has answered · `●` open · `↺` saved, reopened with `claude --continue` · no mark: another repo of `$GITHUB`.

## Claude's state

`⟳` and `✓` also show in the status bar, after the current session's name, for every other session where Claude is working or has answered:

```
dotfiles  ⟳ infra-lab  ✓ portfolio
```

Claude Code hooks call `claude-projects state` from the pane Claude runs in, which sets the `@claude_state` option on its tmux session:

| Hook | State | Mark |
|------|-------|------|
| `UserPromptSubmit` | `running` | `⟳` |
| `Stop` | `done` | `✓` |
| `SessionEnd` | `none` | — |

`✓` is not set when you are already looking at the answer (session attached, Claude's window in front), and a tmux `client-session-changed` hook clears it once you switch to the session.

Limits: `Stop` does not fire when you interrupt Claude with `Esc`, so `⟳` stays until the next prompt; and a permission prompt still shows `⟳`, although Claude is waiting for you.

## Commands

```
claude-projects                 pick a project (fzf)
claude-projects open [dir]      open (or jump to) the project in dir, e.g. one outside $GITHUB
claude-projects save            remember the open project sessions
claude-projects restore         reopen every saved project
claude-projects kill <name>     close a project session
claude-projects state <state>   running|done|none, called by Claude Code hooks
```

Project sessions carry the `@claude_project` tmux option (their directory), which tells them apart from other sessions. The saved list is `~/.local/state/claude/projects.tsv`, one `name<TAB>dir` line per project. It is rewritten when a project is opened or killed from the popup, and by `save`, but not on tmux's `session-closed` hook: when the server dies every session closes, and the hook would empty the list right before `restore` needs it.

## Setup

The dotfiles Ansible playbook symlinks the script into `~/.local/bin` and installs `fzf`; the binding lives in dotfiles' [`.tmux.conf`](https://github.com/LionelPinheiroDuarte/dotfiles/blob/main/tmux/.tmux.conf):

```tmux
bind g display-popup -E -w 80% -h 70% "~/.local/bin/claude-projects"
set-hook -g client-session-changed 'if -F "#{==:#{@claude_state},done}" "set -u @claude_state"'
```

The status bar part is in the same file (`status-left`), and the Claude Code hooks in dotfiles' [`.claude/settings.json`](https://github.com/LionelPinheiroDuarte/dotfiles/blob/main/.claude/settings.json).
