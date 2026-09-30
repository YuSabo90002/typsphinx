---
phase: quick-260922-tkt
plan: 01
subsystem: docs
tags: [linkcheck, sphinx, conf.py, todo-close]
status: complete
dependency-graph:
  requires: []
  provides:
    - "docs/source/conf.py's first linkcheck_* key"
  affects:
    - "tox -e linkcheck's PyPI anchor record"
tech-stack:
  added: []
  patterns:
    - "linkcheck_anchors_ignore_for_url with an end-anchored, project-scoped regex"
key-files:
  created: []
  modified:
    - docs/source/conf.py
  renamed:
    - from: .planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md
      to: .planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md
decisions:
  - "D-A/D-B (plan-authored, confirmed unchanged at execution): linkcheck_anchors_ignore_for_url,
     not linkcheck_anchors_ignore; pattern end-anchored at the bare project URL
     (r\"https://pypi\\.org/project/typsphinx/$\"), not the broader `pypi\\.org` the todo suggested."
metrics:
  duration: "~15 minutes"
  completed: 2026-09-22
actuals:
  tokens: 2441
  tasks: 3
  commits: 2
  plan_head_before: d526b88ddd477019573886c0529fa3f932060d6b
---

# Phase quick-260922-tkt Plan 01: Skip the PyPI anchor check in linkcheck Summary

One-liner: Added `docs/source/conf.py`'s first `linkcheck_anchors_ignore_for_url` entry
(`r"https://pypi\.org/project/typsphinx/$"`) to stop `tox -e linkcheck` reporting the PyPI
`#history` anchor as broken under PyPI's bot-mitigation interstitial, then filed the tracking
todo as completed.

## What Happened

**Runner route and timing.** Both linkcheck runs used the primary route, `${RUN}tox -e linkcheck`
(no fallback to direct `sphinx-build` was needed). Pre-change (Task 1) run: 11.87s wall clock,
`sphinx-build` itself 11.38s, exit 1 as expected. Post-change (Task 3) run: 9.91s wall clock,
`sphinx-build` itself 9.74s, exit 1 as expected (the two Class A records are still broken while
the `v0.9.6` tag does not exist).

**Task 1 — pre-change baseline.** `docs/_build/linkcheck-tkt/before.json`: 96 total records,
status histogram `{'working': 93, 'broken': 3}`. The PyPI `#history` anchor
(`changelog.rst:474`) was confirmed `broken`, ruling out the todo's "obsolete" branch from the
oracle itself, not only from the planning-time curl measurement. Both Class A records
(`changelog.rst:8` and `:17`, the `v0.9.6` compare/release links) were confirmed `broken`. No
tracked file changed while taking this baseline (working tree clean throughout).

**Task 2 — the conf.py change.** Appended a new `# -- Link checking (tox -e linkcheck) --...`
section (78-char header, matching the file's existing convention) after the Autodoc section,
binding exactly one name:

```
CONFIGURED PATTERN: https://pypi\.org/project/typsphinx/$
LINKCHECK KEYS BOUND: ['linkcheck_anchors_ignore_for_url']
ANCHOR LOOKUPS SUPPRESSED: ['https://pypi.org/project/typsphinx/#history']
PROBE SENSITIVITY: anchored URLs in the set = 41 | suppressed by the configured pattern = 1
SCOPE-PROBE OK
```

The comment above the setting names the bot-mitigation mechanism (HTTP 200, 3038-byte body
titled "Client Challenge", zero anchors), the `2026-09-22` re-measurement date (unchanged from
the 2026-09-20 first measurement), the deletion condition, and the reason the fragment is absent
from the pattern (citing `sphinx/builders/linkcheck.py`'s `_check_uri`, which splits the URI on
`#` before matching `linkcheck_anchors_ignore_for_url` against the fragment-stripped URL).

The file still has exactly one over-88 line (line 56, the pre-existing `READTHEDOCS_LANGUAGE`
comment) — one added line initially landed at 89 chars and was rewrapped during execution to stay
inside budget. `black --check .` → `358 files would be left unchanged.`; `ruff check .` →
`All checks passed!`. Commit `2c85ebca` touches exactly one file, `docs/source/conf.py`.

**Task 3 — post-change run, the bounded differential, and the todo close.**
`docs/_build/linkcheck-tkt/after.json`: 96 total records (same count and same discovered link set
as before — `RECORDS ONLY IN BEFORE` / `RECORDS ONLY IN AFTER` both empty), status histogram
`{'working': 94, 'broken': 2}`.

```
FIXED broken->working: ('changelog.rst', 474, 'https://pypi.org/project/typsphinx/#history')
AFTER pypi-anchor record: {'filename': 'changelog.rst', 'lineno': 474, 'status': 'working',
  'code': 0, 'uri': 'https://pypi.org/project/typsphinx/#history', 'info': ''}
AFTER class-A: compare/v0.9.6...HEAD changelog.rst 8 broken
AFTER class-A: releases/tag/v0.9.6 changelog.rst 17 broken
OTHER-STATUS-DIFF count: 0
DIFFERENTIAL-OK
```

Exactly one record moved `broken` → `working` across the whole 96-record set, and it is the PyPI
anchor — status `working` (not `ignored`), confirming the URL is still fetched and its HTTP status
still checked. Both Class A records are unchanged, still `broken`, as expected until the `v0.9.6`
tag exists. No other status difference appeared (zero re-run was needed).

The todo was moved with `git mv` (`git log --diff-filter=R` confirms `R100`) from
`.planning/todos/pending/` to `.planning/todos/completed/`, body and frontmatter untouched. The
sibling CI-job todo (`.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md`) was left
untouched; its "Related" section names the PyPI anchor as a prerequisite for promoting linkcheck
to CI, and that prerequisite is now discharged by this change (the todo itself is not resolved —
promoting linkcheck to CI is a separate, still-open action). Commit `0ef243f8` touches exactly the
two todo paths (one rename).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - blocking verification-script assumption] Task 3's exact-file-list check
(`git diff --name-only 9289798c..HEAD`) did not literally match, for two environment reasons
independent of the plan's actual invariant:**
- **Found during:** Task 3's final verify step 5.
- **Issue:** The plan's hardcoded base SHA `9289798cfa31efbd1296cd8572269234f471ef03` predates a
  commit (`d526b88d`, "docs(quick-260922-tkt): plan the PyPI linkcheck anchor skip") that the
  orchestrator had already made — adding this plan's own `260922-tkt-PLAN.md` — before spawning
  this executor. That commit is not part of this plan's task work but sits between the plan's
  reference SHA and this executor's actual starting HEAD, so it appears in any diff taken against
  `9289798c`. Separately, this environment's git (2.54.0) has rename detection on by default for
  `git diff --name-only`, which collapses the todo's `pending → completed` rename into a single
  line (the destination path) rather than the two separate add/delete lines the plan's literal
  expected list enumerates.
- **Fix:** Re-ran the same substantive check against this executor's actual spawn base
  (`d526b88ddd477019573886c0529fa3f932060d6b`, confirmed via the required worktree branch-check
  block) with `--no-renames`: `git diff --no-renames --name-only d526b88d..HEAD | sort` returned
  exactly the plan's three literal expected paths — the pending todo, the completed todo, and
  `docs/source/conf.py` — byte-for-byte. This confirms the intended invariant (this plan touched
  exactly those three paths and nothing else) holds; only the literal script's base-SHA and
  rename-detection assumptions did not match this execution's git version and commit history.
- **Files modified:** none (verification-methodology adjustment only, no code or plan text
  changed).
- **Commit:** n/a (no file change; documented here per Rule 3).

No other deviations. Plan executed as written otherwise.

## Known Stubs

None.

## Threat Flags

None — this plan's threat model register (T-260922-TKT-01..05) is fully mitigated by measurement
taken during Tasks 2 and 3, reproduced above (`SCOPE-PROBE OK`, `DIFFERENTIAL-OK`). No new
security-relevant surface was introduced beyond what the plan's own threat model already covers.

## Scope Fence Confirmation

- `git diff --quiet 9289798c -- .planning/REQUIREMENTS.md .planning/ROADMAP.md CHANGELOG.md
  pyproject.toml uv.lock README.md tox.ini .github/ typsphinx/ tests/
  docs/source/changelog.rst` → clean (no output, exit 0).
- `.planning/REQUIREMENTS.md` digest: `79b93b81b5cf6ffdb20f9ddc0c97ff41969ada3547af1b16c4a20cc577d82d67`
  — unchanged from the fence value REL-15 requires.
- `git branch --list 'gsd/v0.9.6*'` → exactly one branch,
  `gsd/v0.9.6-doctest-block-rendering-and-release` (no decoy pair).
- No `phase.complete`-family tooling ran.
- `typsphinx/` untouched (the `260922-tbe` sibling task's docstring change is not part of this
  plan's diff).

## Self-Check: PASSED

- `docs/source/conf.py` exists and contains the new section — FOUND.
- `.planning/todos/completed/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md`
  exists — FOUND.
- `.planning/todos/pending/2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck.md`
  no longer exists — CONFIRMED ABSENT.
- Commit `2c85ebca` (docs(linkcheck)) — FOUND in `git log --oneline`.
- Commit `0ef243f8` (chore(todos)) — FOUND in `git log --oneline`.
