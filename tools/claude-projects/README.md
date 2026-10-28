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
| type | Fuzzy-filter the list |
| `enter` | Jump to the project, creating its session if needed |
| `ctrl+s` | Same, landing on its `shell` window |
| `ctrl+x` | Close the project's session |
| `ctrl+n` | Create `$GITHUB/<query>` (`git init`) and open it |
| `ctrl+r` | Restore every saved project (`claude-projects restore`) |
| `ctrl+/` | Hide or show the preview |

The list has up to four groups, *sessions ouvertes*, *à restaurer*, *sans projet* and *dépôts*, and one row per project: mark, name, branch, changes and age. The cursor steps over the group headers, which disappear as soon as something is typed; next to the prompt, how many projects are active, open and saved.

| Mark | Meaning | Age |
|------|---------|-----|
| `⟳` | Claude is working | since the prompt was sent |
| `✓` | Claude has answered | since the answer |
| `●` | Open | since the session's last activity |
| `↺` | Saved, reopened with `claude --continue` | since the last commit |
| `◇` | No project: Claude in `~`, while it is not open | — |
| none | Another repo of `$GITHUB` | since the last commit |

**No project.** `home` is a Claude session in `~`: no repo, so only the global `~/.claude/CLAUDE.md` applies. Once open it is a session like the others (state, saved, restored with `claude --continue`, which resumes the last conversation started in `~`). A `home` session opened before, e.g. by the dotfiles' `home` script, is taken over rather than duplicated. From a shell: `claude-projects open ~`.

Changes are `±N` modified files and `↑N` commits not pushed, for open and saved projects only: running `git status` on every repo at each opening would slow the popup down.

The preview is a card: the project's name with Claude's state and how long it has been in it, the path, branch, ahead/behind, clean tree or not and tmux windows; the **last exchange** with Claude (the last prompt and the start of the answer, read with `jq` from the newest transcript in `~/.claude/projects/`; that format is internal to Claude Code, so the section is just left out when it cannot be read); and the last five commits.

## Claude's state

The status bar shows the current session as a pill, its windows, then the other project sessions, `✓` on a green background, since it is the one thing worth seeing from another session:

```
 ◆ dotfiles   1:claude  2:shell  │  ⟳ infra-lab   ✓ portfolio   ● brain          prefix+g projets │ mar. 27 oct. 18:07
 ◆ dotfiles   1:claude  2:shell  │  tout est calme · 4 sessions                     prefix+g projets │ mar. 27 oct. 18:07
```

The pill's colour is `@claude_accent` in `.tmux.conf` (`#f0a45d` orange or `#82aaff` blue).

Claude Code hooks call `claude-projects state` from the pane Claude runs in, which sets the `@claude_state` option on its tmux session, and `@claude_state_at` when the state changes:

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
claude-projects open [dir] [shell]  open (or jump to) the project in dir, e.g. one outside $GITHUB
claude-projects new <name>      create $GITHUB/<name> (git init) and open it
claude-projects save            remember the open project sessions
claude-projects restore         reopen every saved project
claude-projects kill <name>     close a project session
claude-projects state <state>   running|done|none, called by Claude Code hooks
```

Project sessions carry the `@claude_project` tmux option (their directory), which tells them apart from other sessions. The saved list is `~/.local/state/claude/projects.tsv`, one `name<TAB>dir` line per project. It is rewritten when a project is opened or killed from the popup, and by `save`, but not on tmux's `session-closed` hook: when the server dies every session closes, and the hook would empty the list right before `restore` needs it.

## Setup

The dotfiles Ansible playbook symlinks the script into `~/.local/bin` and installs `fzf` (the official binary, 0.66 or later is needed) and `jq`; the binding lives in dotfiles' [`.tmux.conf`](https://github.com/LionelPinheiroDuarte/dotfiles/blob/main/tmux/.tmux.conf):

```tmux
bind g display-popup -E -w 80% -h 70% "~/.local/bin/claude-projects"
set-hook -g client-session-changed 'if -F "#{==:#{@claude_state},done}" "set -u @claude_state ; set -u @claude_state_at"'
```

The status bar part is in the same file (`status-format[0]`, built from `@status_windows` and `@status_others`), and the Claude Code hooks in dotfiles' [`.claude/settings.json`](https://github.com/LionelPinheiroDuarte/dotfiles/blob/main/.claude/settings.json).

The palette, ages, fzf version check and the fzf options shared by both popups live in [`tools/lib/popup.sh`](../lib/popup.sh), which the script sources from its real location (through the symlink), so the whole `tools/` directory must stay together.
