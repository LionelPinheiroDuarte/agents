---
name: preflight
description: Go/no-go checklist before any expensive, slow, quota-bound or hard-to-reverse run — cloud builds (EAS, Docker push), store submits, terraform apply, deploys, release workflows, paid API batches. Use it automatically right before launching such a run, or when the user types /preflight.
argument-hint: "[the run to check, e.g. eas build --profile preview]"
---

Run to check: `$ARGUMENTS` (if empty, the run about to be launched in this session).

The point of this checklist: an expensive run must only answer a question nothing cheaper can answer. Every check below costs seconds; the run costs minutes, money or quota.

Go through the checks in order. Use what the session already knows (what changed since the last successful run) before running commands. Mark each check ✅ (passed), ❌ (failed) or ➖ (not applicable).

## 0. The run

State in one line: the command, what it costs (quota left, money, duration) and whether it can be undone. If the repo has a `docs/preflight.md`, read it now: its project-specific checks are added to this list.

## 1. Is the result predictable?

What question does this run answer? If the answer can be predicted, or obtained with a cheaper command, stop here: NO-GO, and give the cheaper command.

## 2. Credentials and external services, checked locally

List every token, secret and external service the run depends on. For each one created, rotated or re-scoped since the last successful run, run a cheap check of the **permission**, not just the presence:

| Service | Cheap check |
|---|---|
| Sentry | `sentry-cli info`, then `sentry-cli releases list` (needs `org:*` / `project:releases`) |
| AWS | `aws sts get-caller-identity`, IAM policy simulator for the actions used |
| Expo / EAS | `eas whoami`, `eas env:list --environment <env>` |
| GitHub Actions | `gh secret list` (names only), `gh workflow view <file>` |
| Terraform | `terraform validate`, `terraform plan` |
| Any HTTP API | one `curl` on a read-only endpoint with the same token |

Also check *where* each secret lives: local env, CI secrets and the build service's own env are three different places, and they drift.

## 3. The right code

- Branch or ref the run will use, and the commit it points to
- That commit is pushed, and CI is green on it
- `git status` is clean (nothing local that the run won't see)
- Version / build number bumped if the target rejects duplicates

## 4. A cheaper rehearsal

Was the cheapest local equivalent run? For example `eas build --local`, `npx expo export`, `npx expo-doctor`, `terraform plan`, `act` for a GitHub workflow, `docker build` before a push, a dry-run flag. If one exists and was not run, run it first.

## 5. Will a failure be loud?

Read the pipeline files the run executes (workflow, build hooks, scripts) and look for steps that can fail without failing the run:

- `continue-on-error: true`, `|| true`, `set +e`, `2>/dev/null`, `--silent`
- uploads or integrations labelled best-effort or non-blocking

For each one: it is either justified by a comment, or it is flagged. A step allowed to fail must at least print a visible warning (`echo "::warning::..."` in GitHub Actions) so a silent failure cannot hide behind a green run.

## 6. Success criterion

Write down what will be checked after the run to call it a success (artifact produced, release created, version visible in the store, endpoint answers), and the command to check it.

## Verdict

Print a short table of the checks, then one verdict:

- **GO** — every check is ✅ or ➖
- **GO WITH RISK** — list each risk in one line; launch only if the user accepts them
- **NO-GO** — list the cheap fix for each ❌

Do not launch the run before a GO, or before the user explicitly accepts the risks.
