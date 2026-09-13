---
status: testing
phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
source: [72-VERIFICATION.md]
started: 2026-09-13T14:40:00Z
updated: 2026-09-13T14:40:00Z
---

## Current Test

number: 1
name: Rendered furo sidebar shows each User Guide and Examples page once, correctly nested
expected: |
  Open the phase tip's clean HTML build (`docs/_build/html/index.html`, rebuilt with
  `LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html` after `rm -rf docs/_build/html`) in a
  browser and look at the furo left sidebar. Configuration, Builders, Templates and Output Layout
  each appear exactly once, nested under "User Guide"; Basic and Advanced each appear exactly once,
  nested under "Examples". No page is listed a second time beside its section heading.
awaiting: user response

## Tests

### 1. Rendered furo sidebar shows each User Guide and Examples page once, correctly nested
expected: Configuration, Builders, Templates and Output Layout once each under "User Guide"; Basic and Advanced once each under "Examples"; no page duplicated beside its section heading (ROADMAP Phase 72 SC#4, the human check the 2026-08-16 todo names)
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
