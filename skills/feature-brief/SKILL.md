---
name: feature-brief
description: Ideation interview for one feature, ending in a brief ready for visual design (Claude Design) and implementation — flows, every screen state (empty, loading, each kind of error, edge cases), motion, UX decisions, copy, accessibility. Use when the user wants to think a feature through before building it, or types /feature-brief.
argument-hint: "<feature name or one-line idea>"
---

Feature: `$ARGUMENTS`

Goal: a document that lets someone design every screen of this feature without guessing, then build and test it. The interview finds the cases the user would not have thought of; the document keeps them.

## How to interview

- One question at a time, each with your recommended answer and why (as in `grill-me`). Offer 2–4 options when the choice is open.
- Before asking, look for the answer in the repo: existing screens, components, error handling, design tokens, `CLAUDE.md`, `docs/design-system.md`, earlier briefs in `docs/features/`. Reuse an existing pattern rather than inventing a new one, and say which.
- Accept "skip" or "you decide": record your choice as a decision with its reason.
- Group trivial questions; spend the questions on the cases that change the design.

## The interview, in order

### 1. Intent
Who uses it, in what situation, what problem it solves, how we will know it works. The **target**: where it runs (mobile app, website, desktop app, CLI, API…) and on what (phone sizes, browsers, terminals, clients). The target decides which rows of the states matrix, which interactions and which accessibility checks apply. What it explicitly does **not** do (cut scope here, not later).

### 2. Flows
The happy path step by step, as views (screens, pages, commands, responses — whatever the target shows). Entry points (where the user comes from), exits (where they go after, back navigation, cancel). Number the screens `[N.M]` (feature number, screen) so the brief, the mock-ups and the tests share references.

### 3. States, screen by screen
Walk this matrix for each screen. Ask only the rows that apply.

| Family | Cases to check |
|---|---|
| Data | empty (first use vs filtered to nothing), one item, many, very long text, missing optional fields |
| Loading | instant, short (skeleton or nothing?), long (after how many seconds does it say something?) |
| Network | offline (detected before the action vs during), service down while online, slow, timeout |
| Input | invalid (validated when: typing, leaving the field, submitting?), duplicate, too long, empty |
| Not found | no result, close matches ("did you mean"), external content gone (deleted media, dead link) |
| Destructive | undo (how long?) vs confirmation dialog (what does it say will be lost?) |
| Interruption | flow abandoned mid-way (app killed or backgrounded, tab closed or page reloaded, Ctrl-C, client disconnect), back navigation mid-flow, resume later (does it expire?) |
| Storage / system | corrupt or unreadable data, permission denied, storage full |
| Success | silent, toast, screen change? What happens to the input after? |
| First use | onboarding hint, sample data, or nothing? |

For each error, decide: **what the user sees** (banner, inline, full screen), **the words**, **the way out** (retry, alternative, contact), and whether the rest of the app stays usable. Distinguish errors the user can fix from errors they can't.

### 4. Motion
For each animation: what moves, **why** (feedback, continuity between screens, drawing attention), duration and easing (or the existing token). What replaces it when the system's "reduce motion" setting is on. No animation without a reason.

### 5. UX decisions
Every choice where a reasonable designer could go the other way: the options, the choice, the reason. Also the tone and voice of the copy (formal / informal address, wording of errors), and the language of the UI.

### 6. Accessibility
Pick the checks that fit the target. Visual interfaces: contrast in every theme, screen reader labels for icon-only controls, text scaling, nothing conveyed by colour alone; plus touch targets on mobile, keyboard navigation and focus on the web. CLI: readable without colour (`NO_COLOR`), errors on stderr with a non-zero exit code, scriptable output. API: error bodies that say what went wrong and how to fix it.

## Output

Write `docs/features/<NN>-<slug>.md` in the project (create the folder if needed; `NN` is the next free number), from `~/repos/github/agents/framework/templates/feature-brief.md`. Write it in the language of the project's docs; UI copy in the app's language.

The **Design prompt** section must be self-contained: someone pasting it into Claude Design, with the design system files attached, gets every screen and every state of the matrix — not only the happy path.

The **Acceptance checklist** is derived from the states table: one checkable line per state, with its screen reference. It becomes the test list of the feature on its real target (phone, browsers, terminal…).

Then suggest running the `ux-reviewer` agent on the brief before designing.
