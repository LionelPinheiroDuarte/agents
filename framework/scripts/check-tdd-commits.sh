#!/usr/bin/env bash
# Checks the TDD rules of framework/testing.md on a range of commits.
# Usage: check-tdd-commits.sh [range]   (default: origin/main..HEAD)
# Exit code 1 if a GREEN commit touches a test file; warnings don't fail.

set -euo pipefail

range="${1:-origin/main..HEAD}"
test_re='(\.(test|spec)\.[jt]sx?$|_test\.go$|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)(__tests__|tests?)/)'
risky_re='\.(skip|only)\(|\bxit\(|\bxdescribe\(|setTimeout\(|t\.Skip\(|pytest\.mark\.(skip|xfail)|@skip'

errors=0
warnings=0

while read -r sha subject; do
  files=$(git diff-tree --no-commit-id --name-status -r "$sha")
  tests=$(awk '{print $NF}' <<<"$files" | grep -E "$test_re" || true)
  [ -z "$tests" ] && continue

  if [[ "$subject" == *"(GREEN)"* ]]; then
    echo "ERROR   $sha GREEN commit touches test files: $subject"
    sed 's/^/          /' <<<"$tests"
    errors=$((errors + 1))
  fi

  deleted=$(awk '$1 == "D" {print $2}' <<<"$files" | grep -E "$test_re" || true)
  if [ -n "$deleted" ]; then
    echo "WARNING $sha deletes test files (list the behaviours they covered): $subject"
    sed 's/^/          /' <<<"$deleted"
    warnings=$((warnings + 1))
  fi

  # Only the test files the commit still has (deleted ones have no diff to scan).
  existing=$(awk '$1 != "D" {print $NF}' <<<"$files" | grep -E "$test_re" || true)
  [ -z "$existing" ] && continue
  # shellcheck disable=SC2086
  risky=$(git show --format= --unified=0 "$sha" -- $existing | grep -E "^\+.*($risky_re)" || true)
  if [ -n "$risky" ]; then
    echo "WARNING $sha adds skip/only/timeout in tests (needs a comment and a roadmap item): $subject"
    sed 's/^/          /' <<<"$risky"
    warnings=$((warnings + 1))
  fi
done < <(git log --no-merges --format='%h %s' "$range")

echo "---"
echo "$errors error(s), $warnings warning(s) on $range"
[ "$errors" -eq 0 ]
