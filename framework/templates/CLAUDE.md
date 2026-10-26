<!--
Template from ~/repos/github/agents/framework. Fill the <placeholders>, delete
sections that don't apply, then delete every HTML comment: this file is loaded
at every session, each line costs tokens. Target: under 200 lines.
Only stable rules go here. History → docs/sessions.md, plans → docs/roadmap.md.
-->

# <Project name>

<One line: what it is, for whom.>

- **Target**: <mobile app / website / CLI / API…, on what: phone sizes, browsers, terminals>
- **Phase**: see `docs/roadmap.md` (framework phases 0–6)
- **Languages**: code, commits and docs in English; UI in <language> (<formal / informal address>)

## Stack

- <language, framework, main libraries — with versions only when they matter>

## Commands

| Command | What it does |
|---|---|
| `proj-status` | repo, CI and roadmap state — first command of every session |
| `proj-check [--related]` | types, lint, tests, quiet when they pass; `--related` in the TDD loop |
| `<cmd>` | run locally |
| `<cmd>` | release (one command, see Releases) |

<!-- Project specifics for proj-check / proj-status go in .proj-check / .proj-status, not here. -->

## How we work

The framework: `~/repos/github/agents/framework/README.md`.

**A session**
- Starts with `proj-status`, or the `product-manager` agent in `start` mode for a non-trivial session.
- Has **one goal**, taken from *Now* in `docs/roadmap.md`. Anything else that comes up goes to *Later*.
- Ends with `product-manager` in `end` mode: `docs/sessions.md`, `docs/roadmap.md`, scripts to create.
- Console work (store consoles, hosting panels, SaaS settings) gets its own session: Claude writes the sheet of fields first (what each choice implies, what is irreversible), then checks each setting from the CLI.

**A feature**
1. `/feature-brief` → `docs/features/<NN>-<slug>.md` (every state of every view, errors, motion, decisions)
2. `ux-reviewer` agent on the brief; blocking questions answered
3. Design: the brief's design prompt in Claude Design, mock-ups stored next to the brief
4. `test-writer` agent → RED commit; GREEN in session; REFACTOR
5. `test-auditor` agent + `check-tdd-commits.sh main..HEAD` before the merge
6. The brief's acceptance checklist on the real target

**What Claude does alone, what it asks**

| Alone | Asks first |
|---|---|
| Branches, commits, pushes of feature branches | Merging to `main`, tags, releases |
| Running checks and tests | Changing an existing test assertion (it is a spec change) |
| Docs updates (`sessions.md`, `roadmap.md`, README) | Deleting a test, dropping a behaviour |
| Proposing scripts for repeated commands | Expensive or quota-bound runs — after `/preflight` |
| Reading logs and outputs itself | Filling a console form whose impact is unclear |

## Conventions

- **Branches**: `feat/*`, `fix/*`, `chore/*`, `refactor/*`, short-lived, merged to `main` when done. No long-lived integration branch.
- **Commits**: Conventional Commits, one logical change each. TDD steps tagged `(RED)` / `(GREEN)`.
- **Code**:
  - One responsibility per module: views don't call the network or the database, services hold no UI logic.
  - UI depends on abstractions (hooks, stores, interfaces), not on concrete clients.
  - Shared logic lives in one place; a block repeated a third time gets extracted.
  - No hacks: no mutable globals, no suppressed type errors or lint rules without a comment saying why.
  - <language conventions: strict types, error handling style, naming>
- **Data**: migrations are additive, idempotent and tested (a column added with a default, never a silent rewrite). A destructive change is a MAJOR version and a decision.
- **Failures are loud**: no step in CI, scripts or code may fail without a visible error or warning. A best-effort step says so in a comment and prints a warning.

## Testing

Full rules: `~/repos/github/agents/framework/testing.md`.

- Tests follow **behaviours** through the public boundary (<rendered screen / HTTP handler / CLI command>); function-level tests only for dense logic (parsers, algorithms, validation).
- **Priority**: what is both **irreversible** (persisted data, sent messages, payments) and **silent** (no crash, no visible error).
- RED (tests only) → GREEN (**no test file**) → REFACTOR (assertions unchanged).
- Changing an assertion = asking the user. Deleting a test = listing the behaviours it covered.
- `skip` / `only` / raised timeout: a comment with the reason + a roadmap item.
- Test command: `<cmd>` · on the real target: `<Maestro / Playwright / manual checklist>`

## Feedback loop

<!-- How Claude sees the result without asking the user to copy-paste. Fill it in phase 2. -->

- **Logs**: <where they are and how Claude reads them, e.g. dev server in a tmux pane: `tmux capture-pane -p -J -t <pane> -S -3000`>
- **Screenshots / UI**: <command, or "not available: the user checks the acceptance checklist">
- **Ad hoc checks**: <e.g. a dev-only button or a script, when the debugger console is not usable>
- **Errors in production**: <Sentry / logs / none yet>

## Releases

- SemVer, a tag on `main` for **every** release, created by the release command:
  - **MAJOR**: changes the data model or a main flow
  - **MINOR**: an additive feature, existing flows unchanged
  - **PATCH**: a fix, polish, docs
- The tag is a marker; building and publishing are explicit steps, never a side effect of pushing a tag.
- Every expensive run (cloud build, submit, deploy, `terraform apply`) goes through `/preflight`; project checks in `docs/preflight.md`.
- If a release needs a manual workaround, the pipeline gets a roadmap item to fix it.

## Secrets and environments

| Secret | Local | CI | Build / hosting service |
|---|---|---|---|
| `<NAME>` | <`.env`, never committed> | <GitHub secret> | <service env> |

<!-- The three places drift: when a secret changes, update all of them and check its permissions with a cheap command. -->

## Architecture

<Five to ten lines or a diagram link: main modules and how data flows. Only what is stable.>

```
<folder>/   — <role>
<folder>/   — <role>
```

## Design system

<!-- Delete for a project without UI. -->
<Path to tokens / design-system doc. Briefs reuse its patterns: banners, toasts, undo, dialogs, empty states.>

## Pitfalls

<!-- Permanent traps only, one line each with the fix. A trap of this machine rather than this project goes in Claude's memory. -->

- <trap> → <fix>

## Docs

| File | Holds |
|---|---|
| `docs/roadmap.md` | Now / Next / Later, decisions waiting on someone |
| `docs/sessions.md` | one short section per session: done, pitfalls, left |
| `docs/features/` | feature briefs and their mock-ups |
| `docs/preflight.md` | project checks before expensive runs |
| <`docs/…`> | <…> |

Rules: this file holds no TODO, history or current state. Docs are rewritten, not appended. What git knows (merged where, changed when) is never written down.
