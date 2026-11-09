---
name: todo
description: Manage the personal task file — list, create, check, uncheck, complete and archive todos. Invoked only by the user via /todo.
argument-hint: "[check|uncheck|done|clean] [#Section] <todo> -step -step"
disable-model-invocation: true
---

Task file: `~/documents/journal/tasks.md`
Archive file: `~/documents/journal/tasks-archive.md`

Arguments: `$ARGUMENTS`

## Format

The task file starts with the heading `# Tasks`. Todos are grouped under level-2 section headings (`## Tools`, `## Organisation`, …). A todo is a top-level checkbox; its steps are checkboxes indented by four spaces under it:

```markdown
# Tasks

## Tools
- [ ] Todo name
    - [ ] Step one
    - [ ] Step two
## Organisation
- [ ] Todo without steps
```

- A finished todo or step is `- [x]`.
- When reading, `- []` counts as `- [ ]`. Every line this skill writes or edits uses `- [ ]`; other lines are left as they are.
- Steps nested deeper than one level are preserved, but new steps are always added at one level only.
- Section headings follow each other with no blank line between a list and the next heading, as in the existing file. Keep whatever spacing the file already uses.

## Parsing the arguments

1. If the first word is `check`, `uncheck`, `done` or `clean`, it is a subcommand. Otherwise the whole argument string is a todo to create. A todo whose name starts with one of these words is passed in quotes (`/todo "clean the garage"`): strip the quotes and treat it as a creation.
2. A leading `#Word` (creation only) names the section. Without it, the section is inferred (see below).
3. Split the rest on ` -` (space followed by a dash) only. The first part is the todo name, the following parts are steps. A dash inside a word (`CI-CD`, `docker-compose`, `e-mail`) never splits.
4. Keep the language the user typed. Fix spelling and grammar without changing the meaning. Technical terms, product names and code stay as typed. Start each item with a capital letter.

## Commands

### `/todo` (no argument)

Read the task file and list the open todos grouped by section, in file order, with their progress, for example `Portfolio 1/6`. A todo without steps shows `—`. Do not write anything. (For a summary with a priority, the user has `/tasks`.)

### `/todo [#Section] <name> -step -step`

- Look for an open todo whose name matches exactly, ignoring case, in any section. Checked todos are ignored.
  - **Exact match**: append the new steps as indented `- [ ]` at the end of its steps. Skip any step already present.
  - **No exact match**: add `- [ ] <name>` with its steps at the end of the section's list.
- Choosing the section for a new todo:
  - `#Section` given: use the section whose name matches it, ignoring case; if none does, create `## <Section>` at the end of the file.
  - Not given: pick the existing section that fits the todo's meaning. If none clearly fits, ask the user which section to use (or which new one to create) before writing.
  - Say which section was used.
- If an open todo has a close but not exact name, create the new one anyway and tell the user which todo looked similar.

### `/todo check <todo> -step -step`

Find the todo and each step by meaning, not exact text. Turn `- [ ]` into `- [x]` for each step. With no step given, check the todo itself (see `done`). If a todo or step is ambiguous or not found, ask the user before writing.

### `/todo uncheck <todo> -step -step`

Same as `check`, but turns `- [x]` back into `- [ ]`. With no step given, uncheck the todo itself.

### `/todo done <todo>`

Find the todo by meaning, and check it and all its steps (nested ones included). Leave it in place — it is archived by `clean`.

### `/todo clean`

Without asking for confirmation:

1. Check every open todo that has at least one step and all steps checked.
2. Move every checked top-level todo, with its steps, out of the task file into the archive file, under the same section heading there (create the heading at the end of the archive if missing). Append ` — done YYYY-MM-DD` (today) to the todo line. Create the archive file with the heading `# Archive` if it does not exist.
3. Leave a section heading in the task file even when it becomes empty.
4. Print a summary: the todos marked done, the todos archived, the number of open todos left.

## After writing

Edit the files with targeted edits, never rewrite the whole file. After each write, print the section that changed (for `clean`, the summary instead).
