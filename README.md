# agents

A curated collection of custom AI agents and skills I've built and use daily to augment my development workflow.

## Why this repo?

As AI agents become a core part of how software gets built, I've started treating them like any other tool in my stack — versioned, documented, and refined over time. This repo is where I keep them.

## Structure

```
agents/
├── claude/     # Claude Code agents (Anthropic)
└── skills/     # Claude Code skills (slash commands)
```

## Claude Code Agents

[Claude Code](https://claude.ai/code) supports custom agents defined as Markdown files. Each agent has a persona, a set of tools, and a specific focus area.

See [`claude/`](./claude/) for the full list.

## Claude Code Skills

Skills are reusable workflows invoked as slash commands. Unlike agents, they run in the
current session — so they keep the full context of the work in progress. Each one lives in
`skills/<name>/SKILL.md` and is symlinked into `~/.claude/skills/`.

| Skill | What it does |
|-------|--------------|
| [`grill-me`](./skills/grill-me/SKILL.md) | Interviews you relentlessly about a plan until every branch of the design tree is resolved |
| [`mentor`](./skills/mentor/SKILL.md) | Explains a code change like a senior mentor: what changed, how it works, why this approach, and the real alternatives |
| [`todo`](./skills/todo/SKILL.md) | Manages a Markdown task file — create, check, complete and archive todos |
| [`vi`](./skills/vi/SKILL.md) | Opens the file of the current change in the editor, in a new tmux window, at the changed line |
