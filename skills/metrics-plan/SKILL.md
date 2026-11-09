---
name: metrics-plan
description: Goal-Question-Metric workshop with the user for one project, ending in docs/metrics.md (goal, questions, metrics, exact definitions, data sources, build order, limits) and the .shipmetrics.json that the metrics-analyst agent reads. Use when the user wants to decide what to measure on a project, add or revise a goal, or types /metrics-plan.
argument-hint: "[goal in one line, or « revise G<n> »]"
---

Goal: `$ARGUMENTS`

Goal of the workshop: the user knows why each number exists and how it is computed. The method is the Goal-Question-Metric approach (Basili and Weiss; *Software Architecture Metrics*, O'Reilly 2022, ch. 10), with the four key metrics of *Accelerate* (same book, ch. 1) as the usual core of a delivery goal. GQM takes nine steps; you facilitate them with one person, the user.

## Before the first question

- Read the project's `CLAUDE.md`, `docs/roadmap.md` and, if it exists, `docs/metrics.md`. An existing file: you are adding a goal (`G<n+1>`) or revising one, never rewriting the others.
- Look at the delivery data the repo really has: `git for-each-ref refs/tags --sort=creatordate`, `git log --first-parent <main> --merges`, a branch's commit subjects, `gh run list --json`, `gh issue list`, the CI workflows, the test and e2e scripts. Definitions get written against this, not against the book.

## How to facilitate

- One step at a time. At each step, propose first (your draft, with the reason), then ask the user to cut, reword or add. Don't move on before they answer.
- Answers go in the file with « (user, <date>) ».
- Steps 3 and 4 are brainstorming: don't worry about data yet. Step 6 is where the data gets checked, with commands, before anything is written as a source.

## The nine steps

1. **Frame.** Restate the user's intent and why they want numbers now (a decision to take, a doubt, a profile to show). Say what the workshop produces.
2. **Goal.** One sentence holding the purpose, the object measured, the issue and the point of view (« Ship often without breaking what the user already does, from the solo developer's point of view »). Imperfect is fine; step 5 revises it.
3. **Questions.** Operational ones that tell whether the work gets closer to the goal or farther. Group them (for a delivery goal: throughput, stability, balance). Include at least one question whose bad answer would hurt.
4. **Metrics.** At least one per question, numbered `M<n>`, each listing the questions it answers. Prefer metrics that answer several questions. Pair positive metrics with negative ones (a rework rate beside a failure rate) so that a declared figure has a check. A question answered by a chart (two series on one time axis) can have no metric of its own.
5. **Sanity check.** Do these metrics evaluate this goal? Look for the part of the goal that nothing measures (« what the user already does » → journey coverage). Offer to rephrase the goal or add a metric.
6. **Data and definitions.** For each metric: the exact data, its source, and whether it exists today (✅) or needs instrumentation or a convention (⚠️). Check each source with a command. Write precise definitions for whatever the numbers depend on: what a change is, what a deployment is (with no production: the highest environment, e.g. a tag on `main`), where a change starts, what a failure is (one that stops a user's task; cosmetic defects are not failures), which windows (31 days for throughput and failure rate, 120 for time to restore), mean or median. Look for history traps (changes delivered by the first tag of a repo that tagged late; author vs committer dates after rebases) and write the rule that handles each. Ask where raw data lives (versioned in `metrics/data/`, local under `~/.local/state/metrics/<project>/`, or split by how often it is written).
7. **Prioritize.** Value against cost, in batches: batch 1 needs only git and `gh`; batch 2 needs one instrumentation or a convention; batch 3 waits for enough points (about 20 changes for a correlation). Say which batch each metric is in and why.
8. **Reflect.** Name the surprises and the weak spots: which metric rests on a human declaration, which one rests on commit conventions (a misnamed commit skews it), what the small sample size forbids reading. These become the Limits section.
9. **Record.** Write the files below, then rebuild the history the plan asks for (e.g. failures from past `fix` commits), with each judgement call shown to the user to validate; unknown stays « unknown », never a guess.

## Output

`docs/metrics.md` (in the language of the project's docs):

- a one-paragraph header: the method, the date of the workshop, the rule « a number comes from a script, never counted by hand or by an LLM », and the tool with its config
- per goal: the goal sentence and point of view, the questions (`Q<n>`), the metrics table (`#`, metric, definition, answers)
- **Definitions**: change, deployment, start, failure, windows, special rules; phase markers if a lead time is split by phase
- **Data**: metric → source table, where raw data lives, the conventions it needs, the rebuilt history and its margin of error
- **Order**: the batches
- **Limits**

`.shipmetrics.json` at the repo root for the `shipmetrics` CLI (`~/repos/github/shipmetrics`, README for every key): `exclude_paths` (docs, the metrics data and this config: nothing that ships), `exclude_subjects` (version-bump commits), `failures_history`, and `phases` with markers matching the commit subjects the repo actually uses (check them against two or three merged branches). Run `shipmetrics --no-snapshot`: every stderr warning is either fixed in the config or written in Limits.

Then add a roadmap line for the batches still to build, and a row for `docs/metrics.md` in the docs table of `CLAUDE.md` if the project has one. Commit on a `chore/` branch.

To read the numbers later: the `metrics-analyst` agent, on the project.
