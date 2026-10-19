---
name: todo
description: Manage the personal task file — list, create, check, uncheck, complete and archive todos. Invoked only by the user via /todo.
argument-hint: "[check|uncheck|done|clean] <todo> -step -step"
disable-model-invocation: true
---

Task file: `~/documents/journal/tasks.md`
Archive file: `~/documents/journal/tasks-archive.md`

Arguments: `$ARGUMENTS`

## Format

The task file starts with the heading `# One thing at the time`. Each todo is a level-2 block:

```markdown
## TODO <Name in English>
Start: YYYY-MM-DD
- [ ] Step one
- [ ] Step two
```

A finished todo uses `## DONE` instead of `## TODO`. Blocks are separated by one blank line. Existing nested steps (indented `- [ ]`) are preserved as they are, but new steps are always added at one level only.

## Parsing the arguments

1. If the first word is `check`, `uncheck`, `done` or `clean`, it is a subcommand. Otherwise the whole argument string is a todo to create. A todo whose name starts with one of these words is passed in quotes (`/todo "clean the garage"`): strip the quotes and treat it as a creation.
2. Split the rest on ` -` (space followed by a dash) only. The first part is the todo name, the following parts are steps. A dash inside a word (`CI-CD`, `docker-compose`, `e-mail`) never splits.
3. Translate the name and the steps into English and fix spelling and grammar, without changing their meaning. Technical terms, product names and code stay as typed. Start each item with a capital letter.

## Commands

### `/todo` (no argument)

Read the task file and list the open `## TODO` blocks in file order with their progress, for example `Portfolio 1/6`. A todo without steps shows `—`. Do not write anything.

### `/todo <name> -step -step`

- Look for an existing `## TODO` whose name matches exactly, ignoring case. `## DONE` blocks are ignored.
  - **Exact match**: append the new steps as `- [ ]` at the end of its list. Skip any step already present.
  - **No exact match**: create a new block right below `# One thing at the time` (with one blank line before and after), with `Start:` set to today's date and one `- [ ]` line per step. If an existing TODO has a close but not exact name, create the new block anyway and tell the user which todo looked similar.

### `/todo check <todo> -step -step`

Find the todo and each step by meaning, not exact text. Turn `- [ ]` into `- [x]` for each step. If a todo or step is ambiguous or not found, ask the user before writing.

### `/todo uncheck <todo> -step -step`

Same as `check`, but turns `- [x]` back into `- [ ]`.

### `/todo done <todo>`

Find the todo by meaning, check all its steps (nested ones included) and change `## TODO` into `## DONE`. Leave it in place — it is archived by `clean`.

### `/todo clean`

Without asking for confirmation:

1. Change into `## DONE` every `## TODO` that has at least one step and all steps checked.
2. Move every `## DONE` block out of the task file and append it to the archive file, adding a `Done: YYYY-MM-DD` line (today) right under the heading, after `Start:` if present. Create the archive file with the heading `# Archive` if it does not exist.
3. Print a summary: the todos marked done, the todos archived, the number of open todos left.

## After writing

Edit the files with targeted edits, never rewrite the whole file. After each write, print the block that changed (for `clean`, the summary instead).
