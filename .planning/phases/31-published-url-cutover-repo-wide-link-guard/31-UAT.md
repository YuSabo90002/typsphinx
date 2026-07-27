---
status: testing
phase: 31-published-url-cutover-repo-wide-link-guard
source: [31-VERIFICATION.md]
started: 2026-07-27T12:35:00Z
updated: 2026-07-27T12:35:00Z
---

## Current Test

number: 1
name: Cancelled/superseded Link Check run leaves no repository state behind
expected: |
  The cancelled/superseded run leaves the repository state (commits, tags, issues,
  tracked files) completely unchanged; only the GitHub-hosted job summary reflects
  the run.
awaiting: user response

## Tests

### 1. Cancelled/superseded Link Check run leaves no repository state behind

expected: Cancel or let a Link Check run get superseded mid-flight (e.g. push twice in quick succession, or `gh run cancel <id>` while in progress) and confirm no commit, tag, issue, or tree file is left behind — the job only reads the tree and writes a GitHub job summary. This is the `verification: backstop` must-have from 31-01-PLAN.md and 31-05-PLAN.md; static inspection of links.yml (checkout + lychee-action only, `permissions: contents: read`) is suggestive but the honest-verifier protocol requires direct observation for a backstop truth.
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
