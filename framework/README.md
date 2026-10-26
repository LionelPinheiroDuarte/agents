# Project framework

How I build a project with Claude Code.

The [`product-manager`](../claude/project/product-manager.md) agent applies this framework; the [`feature-brief`](../skills/feature-brief/SKILL.md) skill and the [`ux-reviewer`](../claude/frontend/ux-reviewer.md) agent prepare each feature; the [`test-writer`](../claude/testing/test-writer.md) and [`test-auditor`](../claude/testing/test-auditor.md) agents keep the tests honest ([`testing.md`](./testing.md)); the [`preflight`](../skills/preflight/SKILL.md) skill guards the expensive runs.

## 1. Build order: walking skeleton first

The whole delivery chain exists before the first real feature. Each phase has an exit criterion; the next one starts only when it is met.

| Phase | Content | Exit criterion |
|---|---|---|
| 0. Repo | Repo, `CLAUDE.md`, `docs/roadmap.md`, `docs/sessions.md` | Files exist from the templates |
| 1. CI | Lint, typecheck, one test, on every push | CI green on `main` |
| 2. Skeleton | A "hello" version built, deployed or published to its first target (store test track, server, site) | Someone other than the dev machine can run it |
| 3. Release command | One command does a release (`./x release`); the tag is a marker, the build is triggered explicitly | One release done with that command only |
| 4. Features | Small increments, each merged to `main` when done | — |
| 5. Observability | Error tracking, logs, metrics | One real error visible end to end |
| 6. Ecosystem | Showcase site, beta sign-up, store listing, portfolio page | — |

Rules:

- **No long-lived `dev` branch ahead of `main`.** Feature branches merge to `main` when they are done. If an integration branch exists, it is never more than a few days ahead.
- **If the pipeline is bypassed, fix the pipeline.** A manual workaround becomes a roadmap item, not a paragraph of docs.
- **The feedback loop on the real target is part of phase 2** (phone, browsers, terminal, deployed server). If Claude can't see the result (no device, no screenshot, no logs), fix that before building features on top.

### The feature loop (phase 4)

Each feature goes through the same loop. The brief is written before any code, so error states, motion and UX choices are designed, not discovered while coding.

1. **Brief** — `/feature-brief <idea>`: interview, then `docs/features/<NN>-<slug>.md` (flows, states of every screen, motion, UX decisions, accessibility, design prompt, acceptance checklist)
2. **Review** — `ux-reviewer` agent on the brief; answer the blocking questions, update the brief
3. **Design** — paste the brief's design prompt into Claude Design with the design system; store the mock-ups (or their link) next to the brief, status `designed`
4. **Build** — one branch, TDD per [`testing.md`](./testing.md): the `test-writer` agent writes the RED tests from the acceptance checklist, the session writes the GREEN without touching them, then REFACTOR; before the merge to `main`, `scripts/check-tdd-commits.sh` and the `test-auditor` agent
5. **Verify** — the brief's acceptance checklist on the real target (phone, browsers, terminal…), status `built`

A design system shared by all features (`docs/design-system.md` or tokens) is set up once, before the first feature: briefs reuse its patterns instead of inventing new ones.

## 2. Sessions

- **One goal per session**, chosen at the start from the roadmap. Anything else that comes up goes to the roadmap's *Later* section.
- **Time box**: about 3–4 hours. Past that, close the session properly instead of starting a new topic.
- **Console work** (store consoles, hosting panels, SaaS settings) gets its own short session: Claude first writes a sheet of the fields to fill, what each choice implies and what is irreversible; after, every setting is checked from the CLI when possible (`dig`, `curl -I`, a cheap API call).
- **Expensive runs** go through `/preflight`.

## 3. Documentation: one source of truth per kind of information

| Where | Holds | Never holds |
|---|---|---|
| `CLAUDE.md` (repo) | Stable rules: conventions, architecture, commands, permanent pitfalls. Links to `docs/*` for details | TODOs, history, current state |
| `docs/roadmap.md` | Now / Next / Later, decisions waiting on someone | History |
| `docs/sessions.md` | One short section per session: done, pitfalls, left | Plans |
| Claude memory | What the repo can't say: user preferences, decisions pending outside the repo, machine-specific pitfalls. ~20 lines, rewritten, not appended | Anything the repo already says |
| git | What is merged where (`git log main..dev`), what changed | — |

Rules:

- **Replace, don't append.** "Current state" is rewritten at the end of each session; a section per date only exists in `sessions.md`.
- **`CLAUDE.md` stays short** (target: under 200 lines). It is loaded at every session; the detail lives in `docs/` and is read on demand.

## 4. Scripts: spend tokens on decisions, not on plumbing

Every command output stays in Claude's context for the rest of the session. A check that prints 50 lines when one would do is paid at every following turn.

Generic scripts, in [`scripts/`](./scripts/), linked into `~/.local/bin`:

| Script | What it does |
|---|---|
| `proj-status` | One screen to start a session: git state, branches not merged, recent CI runs, the roadmap's *Now*. A project adds its own lines with an executable `.proj-status` (build quota, deploy state…) |
| `proj-check [--related]` | Types, lint, tests for the detected stack (Node, Go, Python, Terraform, shell), **silent when they pass**: one summary line, or the tail of each failing step. `--related` runs only the tests of changed files (TDD loop). A `.proj-check` file replaces detection |
| `claude-usage report [--project .]` | Ranks the command combinations Claude keeps running, per project and across projects, from a persistent history (`collect` copies transcripts before Claude Code deletes them after 30 days) |
| `check-tdd-commits.sh` | The TDD rules on a range of commits (see [`testing.md`](./testing.md)) |

Rules:

- **Rule of three**: a command combination run in three sessions becomes a script. Seen in one project → a command in that project's script, `.proj-check` or `.proj-status`. Seen in several → a generic script here.
- **Every script is quiet on success.** The output says what needs attention, nothing else.
- `claude-usage report` runs in the `product-manager`'s `end` and `audit` modes, so candidates show up without anyone looking for them.

## Templates

[`templates/`](./templates/) holds the starting files for phase 0 (`CLAUDE.md`, `roadmap.md`, `sessions.md`) and the feature brief (`feature-brief.md`).
