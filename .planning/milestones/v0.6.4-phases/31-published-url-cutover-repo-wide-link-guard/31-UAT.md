---
status: complete
phase: 31-published-url-cutover-repo-wide-link-guard
source: [31-VERIFICATION.md]
started: 2026-07-27T12:35:00Z
updated: 2026-07-27T12:55:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cancelled/superseded Link Check run leaves no repository state behind

expected: Cancel or let a Link Check run get superseded mid-flight (e.g. push twice in quick succession, or `gh run cancel <id>` while in progress) and confirm no commit, tag, issue, or tree file is left behind — the job only reads the tree and writes a GitHub job summary. This is the `verification: backstop` must-have from 31-01-PLAN.md and 31-05-PLAN.md; static inspection of links.yml (checkout + lychee-action only, `permissions: contents: read`) is suggestive but the honest-verifier protocol requires direct observation for a backstop truth.
result: pass
evidence: |
  Live test executed 2026-07-27 (owner-delegated, session-observed): pushed 22ac4af
  to gsd/v0.6.4-read-the-docs-migration, cancelled Link Check run 30267597698 four
  seconds after it appeared (status queued) via `gh run cancel`; run finished
  completed/cancelled. Full `git ls-remote origin` diff against a pre-push baseline
  (130 refs) showed only the branch tip moved by our own pushes — zero new tags,
  branches, issues (issue set unchanged incl. #119), commits, or tree changes.
  A second, uncancelled run (30267554171, completed/success) also left zero
  repository state in the same observation window.

## Summary

total: 1
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
