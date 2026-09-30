---
quick_id: 260722-t3q
description: remove .bg-shell directory
date: 2026-07-22
status: complete
commit: 58a5481
---

# Quick Task 260722-t3q: Remove `.bg-shell` directory

## Investigation

- `.bg-shell/` contained a single tracked file, `manifest.json`, whose entire
  content was `[]` (an empty background-shell registry).
- It entered the repo via commit `1dc3a77` (`chore: auto-commit after
  workflow-template`) — an accidental auto-commit, not a deliberate addition.
- `grep -rn "bg-shell"` across the working tree (excluding `.git/`) found **no**
  references from code, tests, config, docs, or tooling. Nothing reads or writes
  it.

**Conclusion: unnecessary → delete.**

## Changes

- `git rm -r .bg-shell` — removed the tracked directory.
- `.gitignore` — added `/.bg-shell/` under a comment noting it is machine-local
  Claude Code background-shell scratch state, so the runtime recreating it does
  not re-introduce it into version control.

## Verification

- `git ls-files | grep bg-shell` → empty.
- Working tree clean after commit; no source, test, or build file touched.

## Commit

`58a5481` — chore(260722-t3q): remove stray .bg-shell directory
