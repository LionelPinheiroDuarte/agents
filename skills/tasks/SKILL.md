---
name: tasks
description: Summarise the open tasks of the personal task file and pick the one to tackle first, with the reason and a first concrete step. Read-only. Invoked only by the user via /tasks.
argument-hint: "[optional focus, e.g. 30min, devops, quick win]"
disable-model-invocation: true
---

Task file: `~/documents/journal/tasks.md`

Focus given by the user: `$ARGUMENTS` (if empty, no constraint).

This skill never writes to the task file: the user edits it directly.

## 1. Read

Read the task file. Do not assume a fixed format: it may use `## TODO` / `## DONE` blocks, plain section headings (`## Tools`, `## Organisation`) or both, and checkboxes written `- [ ]`, `- []` or `- [x]`. Treat as open any item with an unchecked box that is not inside a `## DONE` block. Nested items are steps of their parent.

If the file is missing or has no open task, say so in one line and stop.

## 2. Summarise

One line per open task, grouped by section heading, in file order:

```
**<Section>**
- <Task> — <progress, e.g. 1/3 steps, or —> · <rough effort: <30min, ~1h, half-day, multi-session>
```

Write the summary in the language of the task file. Keep the task wording close to the original; shorten it only if it runs past one line.

The effort is an estimate. Base it on what the task involves, and when it is cheap (a few seconds), check the real state: does the repo or script it names exist, has a step already been done. Never run anything that changes state.

## 3. Pick one priority

Choose a single task (or a single step of a task) and rank by these criteria, in order:

1. **Unblocks something** — another task, a live project that is down, or a commitment with a date (see the memory index for projects in progress).
2. **Serves the current goals** — landing a DevOps / infrastructure job and building a visible profile (see the global CLAUDE.md). Work that ends up on the public GitHub profile or the portfolio counts here.
3. **Fits the focus** given in the arguments, when there is one (time available, domain, "quick win").
4. **Ratio effort / relief** — between two tasks of equal weight, the smaller one first. A task that has been open for a long time (`Start:` date) counts as more weight, not less.

Output:

```
**Priority: <task>**
Why: <one or two sentences, naming the criterion that decided it>
First step: <a concrete action doable in the next 15 minutes — a command, a file to open, a question to answer>
```

If two tasks are genuinely tied, name the runner-up in one line after the priority, with what would make it win instead.

## 4. Stop

End with one question: should we start on the priority now? Do not start the work before the user answers.
