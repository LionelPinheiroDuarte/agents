# agents

A curated collection of custom AI agents and skills I've built and use daily to augment my development workflow.

## Why this repo?

As AI agents become a core part of how software gets built, I've started treating them like any other tool in my stack — versioned, documented, and refined over time. This repo is where I keep them.

## Structure

```
agents/
├── claude/     # Claude Code agents (Anthropic)
├── framework/  # How I run a project: rules + templates
├── hooks/      # Claude Code hooks (wired in dotfiles' settings.json)
└── skills/     # Claude Code skills (slash commands)
```

## Claude Code Agents

[Claude Code](https://claude.ai/code) supports custom agents defined as Markdown files. Each agent has a persona, a set of tools, and a specific focus area.

See [`claude/`](./claude/), one folder per function. Each agent is symlinked into `~/.claude/agents/`.

### Project management — `claude/project/`

Running a project: framework, issues, git.

| Agent | What it does |
|-------|--------------|
| [`git-manager`](./claude/project/git-manager.md) | Commits, branches, merges, history and conflict resolution |
| [`issue-manager`](./claude/project/issue-manager.md) | Turns reviews or feature requests into GitHub issues, then implements them (branch, commit, PR) |
| [`product-manager`](./claude/project/product-manager.md) | Applies the [project framework](./framework/README.md): phase plan, one goal per session, docs kept in their place |

### Testing — `claude/testing/`

Writing and auditing tests.

| Agent | What it does |
|-------|--------------|
| [`test-auditor`](./claude/testing/test-auditor.md) | Audits a branch's test history before merge: tests bent to the code, lost behaviours, coupling to the implementation |
| [`test-writer`](./claude/testing/test-writer.md) | Writes the failing (RED) tests of a feature from its brief, without seeing the implementation |
| [`wiktionary-tester`](./claude/testing/wiktionary-tester.md) | Runs the Wiktionnaire parser against edge-case words and reports failures |

### Frontend & UX — `claude/frontend/`

Feature briefs and web quality.

| Agent | What it does |
|-------|--------------|
| [`opquast-auditor`](./claude/frontend/opquast-auditor.md) | Audits a web project against the Opquast quality reference (v5, 245 rules) |
| [`ux-reviewer`](./claude/frontend/ux-reviewer.md) | Reviews a feature brief before design: missing states, vague errors, unjustified motion, accessibility |

### Mobile — `claude/mobile/`

React Native / Expo, Play Store publishing.

| Agent | What it does |
|-------|--------------|
| [`db-migration-planner`](./claude/mobile/db-migration-planner.md) | Plans SQLite migrations for Expo / React Native projects |
| [`expo-doctor-agent`](./claude/mobile/expo-doctor-agent.md) | Checks Expo package compatibility before an install or upgrade |
| [`expo-upgrade-advisor`](./claude/mobile/expo-upgrade-advisor.md) | Plans an Expo SDK upgrade with its breaking changes and commands |
| [`play-store-auditor`](./claude/mobile/play-store-auditor.md) | Audits a Play Store listing for ASO quality |
| [`privacy-policy-generator`](./claude/mobile/privacy-policy-generator.md) | Generates a minimal GDPR-compliant privacy policy for a mobile app |
| [`rn-component-reviewer`](./claude/mobile/rn-component-reviewer.md) | Reviews React Native / Expo code for platform pitfalls |
| [`store-listing-writer`](./claude/mobile/store-listing-writer.md) | Writes Play Store / App Store listings in French and English |

### Backend — `claude/backend/`

Languages and server code.

| Agent | What it does |
|-------|--------------|
| [`go-expert`](./claude/backend/go-expert.md) | Writes and reviews idiomatic Go: structure, concurrency, errors, tests |

### DevOps — `claude/devops/`

Cloud and infrastructure.

| Agent | What it does |
|-------|--------------|
| [`cloud-auditor`](./claude/devops/cloud-auditor.md) | Audits an AWS project against Well-Architected, CIS, Terraform best practices and FinOps |

### Docs & content — `claude/docs/`

Journal, READMEs, portfolio, diagrams, demos.

| Agent | What it does |
|-------|--------------|
| [`diagram-generator`](./claude/docs/diagram-generator.md) | Generates architecture diagrams with D2 and the ELK layout engine |
| [`journal`](./claude/docs/journal.md) | Writes the daily work log from the current conversation |
| [`portfolio-sync`](./claude/docs/portfolio-sync.md) | Keeps portfolio project pages in sync with the repos |
| [`post-commit-sync`](./claude/docs/post-commit-sync.md) | Updates READMEs, GIF demos and portfolio pages after a `feat:` commit |
| [`vhs-gif`](./claude/docs/vhs-gif.md) | Creates and tunes VHS tapes for terminal GIF demos |

### Career — `claude/career/`

CV and job applications.

| Agent | What it does |
|-------|--------------|
| [`ats-advisor`](./claude/career/ats-advisor.md) | Audits a CV against ATS norms for a given job offer |
| [`cv-generator`](./claude/career/cv-generator.md) | Generates a LaTeX CV tailored to a job offer from a YAML profile |

## Claude Code Skills

Skills are reusable workflows invoked as slash commands. Unlike agents, they run in the
current session — so they keep the full context of the work in progress. Each one lives in
`skills/<name>/SKILL.md` and is symlinked into `~/.claude/skills/`.

| Skill | What it does |
|-------|--------------|
| [`feature-brief`](./skills/feature-brief/SKILL.md) | Ideation interview for a feature, ending in a brief ready for visual design: every screen state, errors, motion, UX decisions |
| [`grill-me`](./skills/grill-me/SKILL.md) | Interviews you relentlessly about a plan until every branch of the design tree is resolved |
| [`mentor`](./skills/mentor/SKILL.md) | Explains a code change like a senior mentor: what changed, how it works, why this approach, and the real alternatives |
| [`preflight`](./skills/preflight/SKILL.md) | Go/no-go checklist before an expensive or quota-bound run (cloud build, deploy, terraform apply) |
| [`todo`](./skills/todo/SKILL.md) | Manages a Markdown task file — create, check, complete and archive todos |
| [`vi`](./skills/vi/SKILL.md) | Opens the file of the current change in the editor, in a new tmux window, at the changed line |

## Project framework

[`framework/`](./framework/README.md) is how I run a project with Claude Code: build order (walking skeleton first), session scope, and one source of truth per kind of documentation. The [`product-manager`](./claude/project/product-manager.md) agent applies it, the [`ux-reviewer`](./claude/frontend/ux-reviewer.md) agent reviews feature briefs, [`test-writer`](./claude/testing/test-writer.md) and [`test-auditor`](./claude/testing/test-auditor.md) apply the [testing rules](./framework/testing.md); [`templates/`](./framework/templates/) holds the phase-0 files and the feature brief; [`scripts/`](./framework/scripts/) holds `proj-status`, `proj-check` (quiet checks for any stack) and `claude-usage` (tracks the commands Claude repeats across projects, to turn them into scripts).

## Claude Code Hooks

Hooks are scripts Claude Code runs on session events. Each one lives in `hooks/<name>/` with its own README, and is wired in the `hooks` block of [dotfiles' `settings.json`](https://github.com/LionelPinheiroDuarte/dotfiles/blob/main/.claude/settings.json).

| Hook | Event | Description |
|------|-------|-------------|
| [`log-edits`](./hooks/log-edits/README.md) | `PostToolUse` (`Edit\|Write\|NotebookEdit`) | Logs every file Claude writes and snapshots its previous content, for the `claude-edits` tmux popup in dotfiles (list, diff, vimdiff) |
