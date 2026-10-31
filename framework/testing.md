# Testing

Rules for tests in every project, written after finding, in `vocab`, an assertion changed during a GREEN step to fit the code, and a deleted test file that took a behaviour away with it without anyone deciding it.

The principle behind every rule: **a test is the specification. The code adapts to it, never the reverse, unless the user decides the specification changes.**

## What a test targets

A test follows a **behaviour** the user (or the caller) can observe, not a function. The "unit" of a unit test is a unit of behaviour.

The question to ask of every test: **would it survive a refactoring that changes no behaviour?**

- yes → it is in the right place, whatever its level
- no → it tests the implementation: move it up to the behaviour, or delete it

In practice:

- **Most tests follow the features**, through the highest public boundary that stays fast: the rendered screen (React Native Testing Library, Testing Library), an HTTP handler through its router, a CLI command with its arguments. The brief's acceptance checklist is their list.
- **Function-level tests only for dense logic**: parsers, URL normalisation, scheduling algorithms, distance computations, validation rules — many cases, a stable interface. There, a table of cases at the function level is faster and clearer than going through a screen.
- **No tests on the intermediate layers** (internal hooks, stores, state shapes, private helpers), unless they hold dense logic themselves. Replacing them must not lose a test.

Signs that a test is coupled to the implementation:

- it asserts an internal state shape or ordering the user never sees
- it selects elements by decorative content (emoji, icon, styling) instead of their role, label or a `testID` named after what they do
- it mocks a close collaborator of the code under test instead of a boundary
- it must be deleted or rewritten when the module it targets is replaced, while the feature stays the same

In `vocab`, these three cost us: tests on a hook were deleted with the hook and a behaviour vanished; an assertion on the order of an internal array was "fixed" to fit the code; tests looking for `'📷 Galerie'` broke when an emoji was replaced by an icon.

### What to test first

A bug is expensive when it is both **irreversible** (persisted data lost or corrupted, a message or payment sent) and **silent** (no crash, no visible error). Test first whatever writes persistent data, state machines, and transformations that never throw.

## The TDD cycle, commit by commit

| Step | Commit | Touches | Never touches |
|---|---|---|---|
| RED | `test(<scope>): <behaviour> (RED)` | test files only | production code (except empty stubs so it compiles) |
| GREEN | `feat\|fix(<scope>): <behaviour> (GREEN)` | production code only | **test files** |
| REFACTOR | `refactor(<scope>): <what>` | production code; tests only to rename or move them, assertions unchanged | expected values |

RED tests are written by the `test-writer` agent from the feature brief's acceptance checklist, so they describe the behaviour without knowing the implementation. They must fail for the right reason: a failing assertion or a missing function, not a syntax error or a broken import.

## The four rules

1. **A GREEN commit touches no test file.** When the code seems to need a test change, stop and commit it separately first, saying why:
   - the test is wrong → `test:` commit, and rule 2 applies
   - a new behaviour came up while coding → its own RED commit, then the GREEN
   - a fixture or mock must follow a type change (a new field) → `test:` commit with only that change
2. **Changing an existing assertion is a change of specification**, so it is the user's decision. Claude says which assertion, the old and new expected value, and why, and waits for an answer. A changed matcher or query counts too (a regex narrowed, `includeHiddenElements` added): the commit message never says « no assertion changed » when one did, and names the weakening if there is one.
3. **Deleting a test file means listing the behaviours it covered**, each one either re-tested elsewhere (where) or dropped (a decision written in the commit message and the session log).
4. **Raising a timeout, adding `skip`, `only`, `xfail` or a retry** needs a comment saying why in the code, and a roadmap item to remove it.

## What to test, at which level

| Level | Covers | Share of the suite |
|---|---|---|
| Feature | a behaviour through the public boundary, with real internals and mocked boundaries: a rendered screen with its hooks and store, an HTTP handler through its router with an in-memory DB, a CLI command | **the bulk** — one or more per acceptance-checklist row |
| Dense logic | pure functions with many cases: parsers, normalisation, scheduling, validation rules — as tables of cases | where the logic is dense, not for every function |
| Integration | what the feature level mocks and must still be proven: migrations on a real database, a real third-party call in a sandbox | a few |
| End to end | the critical paths on the real target (Maestro, Playwright, a CLI run, an HTTP call to a deployed server), and what can only be seen there (native, visual) | slow, few |

Each state of the brief's acceptance checklist is covered at least at one level, preferably the feature level; the `test-auditor` checks it.

### When the RED tests are wrong

The GREEN step is where a RED test turns out wrong: an interaction outside `act()`, an element the brief hides from accessibility, a negative assertion that also matches legitimate copy. The code cannot fix those, and bending the code to them is worse. Stop, list each one with its cause and the proposed fix, get the user's answer, and commit the fixes as `test(<scope>): fix RED tests (user-approved)` before the GREEN. `check-tdd-commits.sh` then sees a clean GREEN.

## Mocks

- Mock what crosses the boundary of the program (network, clock, native modules, third-party SDKs), not the code under test or its close collaborators.
- A mock keeps the real types and error classes (`jest.requireActual`, interfaces in Go), so the test fails when the real API changes.
- One mock per boundary, shared (`__mocks__/`, a fake in `testutil`), rather than a different hand-written one in every file.

## Flaky tests

A test that fails now and then is a bug, either in the test or in the code. Find the cause before touching the timeout; if the timeout is the answer, rule 4 applies.

## Checks

- `framework/scripts/check-tdd-commits.sh [range]` fails on a GREEN commit that touches a test file and warns on deleted test files, `skip`/`only` and raised timeouts. Run it before a merge, or in CI on pull requests.
- The `test-auditor` agent reviews the test history of a branch before it is merged.
