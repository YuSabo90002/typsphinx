---
status: testing
phase: 33-v0-6-4-release-prep
source: [33-VERIFICATION.md]
started: 2026-07-27T21:35:00Z
updated: 2026-07-27T21:35:00Z
---

## Current Test

number: 1
name: JA→EN translation meaning-preservation spot-check (D-05)
expected: |
  Every translated clause in .planning/PROJECT.md, .planning/ROADMAP.md,
  .planning/MILESTONES.md, and .planning/STATE.md carries the same claim,
  scope, and register as its Japanese source (pre-phase main-branch version).
  A claim that was wrong or a decision that was narrowly scoped in Japanese
  stays equally wrong/narrowly scoped in English — nothing was "improved"
  under cover of translation (no condensation, no silent correction, no loss
  of a hedge/reversal structure).
awaiting: user response

## Tests

### 1. JA→EN translation meaning-preservation spot-check (D-05)
expected: Spot-check a sample of the translated prose in the four top-level .planning/ documents against their pre-phase Japanese originals (e.g. `git diff b74baa5^..6a518a8 -- .planning/`) for meaning drift — condensation, silent correction of a claim believed wrong, or loss of a hedge/reversal structure. Every translated clause carries the same claim, scope, and register as its Japanese source.
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
