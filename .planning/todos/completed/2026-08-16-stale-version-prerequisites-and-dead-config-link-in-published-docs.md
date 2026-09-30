---
created: 2026-08-16T12:45:09.347Z
title: "Published prerequisites still say Python 3.9 / Sphinx 5.0 across four files, and `advanced/README.md` links to a `docs/configuration.rst` that does not exist"
area: docs, examples
severity: major
files:
  - docs/source/installation.rst:7-8
  - docs/source/contributing.rst:14
  - examples/basic/README.md:7-8
  - examples/advanced/README.md:31-32
  - examples/advanced/README.md:270
  - pyproject.toml:10
  - pyproject.toml:28
---

## Problem

Two independent staleness defects surfaced by Phase 56's code review (`56-REVIEW.md`,
2 WARNING findings). Both are **pre-existing** — neither was introduced by Phase 56's diff —
and both were confirmed by measurement, not by reading.

### 1. Version prerequisites contradict the shipped constraints (4 files)

Four published surfaces state prerequisites that `pyproject.toml` flatly contradicts:

| File | Line(s) | Published claim |
|------|---------|-----------------|
| `docs/source/installation.rst` | 7-8 | `Python 3.9 or later` / `Sphinx 5.0 or later` |
| `docs/source/contributing.rst` | 14 | `Python 3.9 or later` |
| `examples/basic/README.md` | 7-8 | `Python 3.9 or higher` / `Sphinx 5.0 or higher` |
| `examples/advanced/README.md` | 31-32 | `Python 3.9 or higher` / `Sphinx 5.0 or higher` |

Actual, measured from `pyproject.toml`:

- line 10: `requires-python = ">=3.12"`
- line 28: `"sphinx>=9.1,<10"`

`CLAUDE.md` independently states "Python 3.12+ is required."

A reader on Python 3.9–3.11, or on Sphinx 5–8, who follows this guidance hits an immediate
`pip install typsphinx` resolution failure. The correct floor is published nowhere on these
pages, so there is no workaround from the docs alone — hence `major`.

`installation.rst` is the highest-impact of the four: it is the published installation page,
and it is the one a new user reads first.

### 2. Dead relative link to the configuration reference

`examples/advanced/README.md:270`:

```markdown
See [Configuration Reference](../../docs/configuration.rst) for complete documentation of all options.
```

`docs/configuration.rst` does not exist. Measured actual location:
`docs/source/user_guide/configuration.rst`. From `examples/advanced/`, the correct relative
path is `../../docs/source/user_guide/configuration.rst`.

## Solution

Small and mechanical — roughly six line-edits across four files:

1. Replace the four `Python 3.9` / `Sphinx 5.0` prerequisite pairs with the real floors
   (`Python 3.12`, `Sphinx 9.1`). Prefer deriving them rather than transcribing: a gate that
   reads `requires-python` and the `sphinx>=` pin out of `pyproject.toml` and asserts the
   published prose agrees would stop this drifting a third time. Phase 56 established exactly
   this pattern — see `tests/test_registry_documentation_gate.py` and
   `tests/test_bundle_layout_sweep_gate.py` for the import-bound / repo-wide-grep gate shapes
   already in the tree.
2. Fix `examples/advanced/README.md:270` to point at
   `../../docs/source/user_guide/configuration.rst`.

Before fixing, **re-run the search repo-wide** rather than trusting the file list above — the
table was built from a `grep -rn "Python 3\.9\|Sphinx 5\.0"` over `*.md` / `*.rst` excluding
`.planning/` and `.claude/`, and a different phrasing ("3.9+", "at least 3.9", a version in a
badge or in `README.md`'s own prerequisites) would not have matched. This is the same
scoping discipline Phase 56's SC#4 sweep enforced.

## Context

- Origin: Phase 56 code review, `56-REVIEW.md` (0 BLOCKER / 2 WARNING). Both findings sat
  inside the reviewed file scope but **outside** Phase 56's success criteria — SC#4 sweeps for
  "claims the new layout invalidates", and version prerequisites are a different class of
  staleness — so the phase verifier's 8/8 pass is correct and this is genuinely deferred work,
  not a missed requirement.
- Owner decision (2026-08-16): split out as a todo rather than folded into Phase 56.
- Related: [[2026-07-22-add-sphinx-linkcheck-ci-job]] — a `sphinx-build -b linkcheck` CI job
  would have caught defect #2 automatically. Consider doing these two together; the linkcheck
  job is the durable fix for the dead-link class, while a `pyproject.toml`-derived gate is the
  durable fix for the version-drift class.
