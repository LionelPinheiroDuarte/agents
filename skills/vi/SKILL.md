---
name: vi
description: >
  Open a file in the user's editor, in a new tmux window, at the relevant line —
  the file just proposed for a change, or an explicit path. Use when the user
  types `/vi`, or asks to open the current change in their editor.
---

# vi

Opens the target file in a new tmux window, at the line that matters.

**Never launch the editor with a plain Bash call.** The Bash tool has no TTY, so
`vi <file>` would hang on a terminal nobody can see. tmux is a client/server: a window
created from a non-TTY process runs a genuinely interactive editor. That is the only
path that works here.

## Target resolution

| Invocation | Target |
|---|---|
| `/vi` | The file of the most recent `Edit`/`Write` of this session, at its first changed line |
| `/vi <path>` | That file, at line 1 |
| `/vi <path>:<line>` | That file, at that line |

If the last turn changed **several** files, list them numbered with their changed line
and stop. Let the user pick — do not guess which one they meant.

If this session has changed no file and no path was given, say so in one line and stop.

Resolve `~` and relative paths before building the command. If the path does not exist,
say so instead of opening an empty buffer on a typo.

## How to open

```bash
tmux new-window -n edit "${EDITOR:-vi} +<line> '<path>'"
```

- `$TMUX` is inherited from the pane Claude runs in, so **no `-t` target is needed** —
  the window lands in the user's current session.
- Name the window `edit`: it is identifiable in the status bar, and quitting the editor
  closes it, leaving no state to clean up.
- Always single-quote the path.
- Omit `+<line>` when the line is 1 or unknown.
- The command returns immediately. **Never wait for the editor to exit, never poll** —
  the user is editing, and a background wait would block the session for nothing.

Then report one line: file, line, and how to come back (`C-a 1` for the Claude window,
`C-a l` to toggle between the last two).

## Outside tmux

If `$TMUX` is unset, do not try to launch anything — there is no window server to hand
the editor to. Print the command for the user to run themselves:

```
! vi +42 /path/to/file
```

## After the user edits

A file opened this way will very likely be modified outside your view. **Treat your
cached version of it as stale from the moment the window opens** — re-read it before
your next `Edit` on that file, or you will overwrite their work with a diff computed
against an older version.

This skill opens a file. It never writes one.
