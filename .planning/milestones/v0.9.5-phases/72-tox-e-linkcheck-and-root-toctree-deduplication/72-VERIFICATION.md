---
phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
verified: 2026-09-13T00:00:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-01-PLAN.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-01-SUMMARY.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-02-PLAN.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-02-SUMMARY.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-03-PLAN.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-03-SUMMARY.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-04-PLAN.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-04-SUMMARY.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-05-PLAN.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-05-SUMMARY.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-06-PLAN.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-06-SUMMARY.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-BASE-EVIDENCE.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CI-EVIDENCE.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CONTEXT.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-DOC24-EVIDENCE.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-GATES-EVIDENCE.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-LINKCHECK-EVIDENCE.md"
  - ".planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-TOCTREE-EVIDENCE.md"
  - ".planning/todos/completed/2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md"
  - ".planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md"
  - "CLAUDE.md"
  - "README.md"
  - "docs/source/contributing.rst"
  - "docs/source/index.rst"
  - "tox.ini"
covered_digest: "v1:sha256:b2bdda1f0a5be38ca1fc737d5771d4b941d27c98dea7d7e0da562697dacb0d38"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Open the phase tip's clean HTML build (`docs/_build/html/index.html` from a fresh `tox -e docs-html` or manual `sphinx-build -b html`) in a browser and look at the furo left sidebar."
    expected: "Configuration, Builders, Templates and Output Layout each appear exactly once, nested under 'User Guide'; Basic and Advanced each appear exactly once, nested under 'Examples'. No page is listed a second time beside its section heading."
    why_human: "ROADMAP Phase 72 SC#4 explicitly names this as the human check the 2026-08-16 todo asks for ('The owner looks at the rendered sidebar at UAT'). The automated DOM/markup count (already independently re-measured by this verifier: every one of the five pages counts exactly 1 in the sidebar-tree, control page counts 1) proves the structural fact but not the visual rendering the todo was filed against."
---

# Phase 72: `tox -e linkcheck` and Root Toctree Deduplication Verification Report

**Phase Goal:** Two changes to this project's own documentation: (1) `tox -e linkcheck` runs Sphinx's
own link check with one command, and every surface listing the project's tox environments names it
(QUA-13, DOC-24); (2) the root `docs/source/index.rst` toctrees list only the section indexes, so
each User Guide and Examples page appears exactly once in the HTML sidebar and exactly once in the
Typst output (DOC-18). The milestone branch reaches `origin` with a green 3-OS CI run.

**Verified:** 2026-09-13
**Status:** human_needed
**Re-verification:** No — initial verification

All five must-haves are independently re-measured below from a fresh checkout of the phase tip
(`gsd/v0.9.5-docs-link-check-and-navigation` at `0b2595df21399363f50e5e1a55935f470e0df00d`, the
pushed SHA; the working tree's later commits touch only `.planning/`). Every SUMMARY.md claim cited
here was re-derived from scratch rather than trusted.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria SC#1–SC#5)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC#1 | `tox -e linkcheck` exists, shaped like `docs-html`, passes clean at execution time | ✓ VERIFIED | Fresh `rm -rf docs/_build/linkcheck && uv run tox -e linkcheck`: exit 0. Live recount of `output.json`: 95 rows, all `working` (total == working, ≥1). `uv run tox list` shows `linkcheck` only under `additional environments:` (not `default environments:`). `tox.ini` diff from `098a8ff6` is exactly 8 lines added, 0 removed; `env_list` (line 2) and the `requires = tox-uv~=1.35` pin are byte-identical. No `linkcheck_*` key in `conf.py` (none was needed — matches D-01/D-02/D-03/D-04 disposition of zero non-working rows). |
| SC#2 | Every surface listing the tox environments names `tox -e linkcheck`, found by grep | ✓ VERIFIED | Fresh `git grep -n 'tox -e docs-pdf' -- ':!.planning'` returns the same 5 hits recorded at roadmap/discussion time: `CLAUDE.md:33`, `README.md:262`, `docs/source/contributing.rst:124` (listing surfaces, now each followed by a `tox -e linkcheck` / `uv run tox -e linkcheck` line with column-aligned comments) plus `.github/workflows/docs.yml:36` and `CHANGELOG.md:921` (correctly dispositioned as non-listing: a CI step and released history). |
| SC#3 | Root toctrees list only section indexes; clean HTML build shows zero `multiple toctrees` messages with unchanged warning count | ✓ VERIFIED | `docs/source/index.rst`'s User Guide toctree lists only `user_guide/index`, Examples lists only `examples/index` (independently confirmed by reading the file). Fresh clean `LANG=C LC_ALL=C sphinx-build -b html` of the tip: 0 `document is referenced in multiple toctrees` lines; `build succeeded, 3 warnings.` — matching `BASE_WARNING_COUNT = 3` recorded pre-edit (the 3 warnings are pre-existing `visit_toctree` docstring rST errors in `typsphinx/`, untouched — confirmed `typsphinx/` diff from base is empty). |
| SC#4 | Each page appears once in the HTML sidebar (nested under its section) and once in the Typst output (via its section index) | ✓ VERIFIED (structural evidence); human sidebar look required | HTML: independently re-ran the sidebar-tree `html.parser` count over a fresh build's `index.html` — all five pages (`user_guide/configuration.html`, `user_guide/builders.html`, `user_guide/templates.html`, `examples/basic.html`, `examples/advanced.html`) and the control `user_guide/output_layout.html` each count exactly 1. Typst: fresh clean `-b typst` build shows 0 root `index.typ` guard lines for the five pages (7 `include(` lines left, vs. base's 12) and the `typsphinx:include-edges` state has exactly one edge per page, each `<section-index>#0>›<page>`. SC#4 itself designates a human look at the rendered sidebar as the closing check (see Human Verification below). |
| SC#5 | Tree green locally and on CI; milestone branch on `origin`; nothing outside scope moved | ✓ VERIFIED | Local: `ruff check .`, `black --check .`, `mypy typsphinx/` all exit 0; full `pytest` suite: 1547 passed, 1 skipped, 0 failed (re-run fresh, matches `72-GATES-EVIDENCE.md`). Scope: `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` is empty; product diff from base is exactly `CLAUDE.md README.md docs/source/contributing.rst docs/source/index.rst tox.ini` (no `conf.py` — no D-02 key ever fired). Remote: `origin/gsd/v0.9.5-docs-link-check-and-navigation` exists at `0b2595df…` (the recorded `PUSHED_SHA`); no `gsd/v0.9.5-milestone` decoy on origin or locally; no `v0.9.3`/`v0.9.4`/`v0.9.5` tag on origin. CI run `34761445288` re-queried live: `status=completed`, `conclusion=success`, `headSha` matches `PUSHED_SHA`, 12/12 jobs success, including `Test Python 3.12/3.13 on windows-latest` and `Test Python 3.12/3.13 on macos-latest` (all four named and green). Required status checks re-read live: `strict=true`, 6 contexts (`Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check`) — identical to `REQUIRED_CONTEXTS_HEAD` recorded at phase head. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tox.ini` | `[testenv:linkcheck]` section, outside `env_list` | ✓ VERIFIED | Present, correctly shaped, `tox list` confirms placement |
| `docs/source/index.rst` | Root toctrees list only `user_guide/index` / `examples/index` | ✓ VERIFIED | Read directly; 5 lines removed, 0 added vs. base |
| `CLAUDE.md`, `README.md`, `docs/source/contributing.rst` | Each names `tox -e linkcheck` | ✓ VERIFIED | Each gains exactly one line, column-aligned with neighbours |
| `.planning/todos/completed/2026-08-16-…md` | Folded DOC-18 todo, moved (D-08) | ✓ VERIFIED | Present in `todos/completed/`, absent from `todos/pending/` |
| `.planning/todos/pending/2026-07-22-…md` | Gains D-07 status note, stays pending | ✓ VERIFIED | Present, ends with `## Status note (Phase 72, v0.9.5)` naming `[testenv:linkcheck]`, QUA-08 and the side-PR-to-`main` constraint |
| `72-BASE/LINKCHECK/DOC24/TOCTREE/GATES/CI-EVIDENCE.md` | Full evidence chain, all verdict keys MET/PASS | ✓ VERIFIED | All six evidence files present, all verdict keys re-checked against live measurements as above |
| `.planning/todos/pending/2026-09-13-…-diverge…` | Only if the examples/basic parent divergence survives | ✓ N/A (correctly absent) | `DIVERGENCE_SURVIVES = no` recorded and confirmed no such file exists — the parent-notion re-measurement found `collect_relations()`/`_get_toctree_ancestors()`/Typst edge parent agree (`examples/index`) at the tip |

### Key Link Verification

| From | To | Via | Status |
|------|-----|-----|--------|
| `docs/source/index.rst` toctrees | `user_guide/index.rst`, `examples/index.rst` | each section index is now the sole toctree listing its children | ✓ WIRED (both section-index files unchanged in the diff, confirmed absent from `git diff --name-only` against base) |
| `tox.ini [testenv:linkcheck]` | `docs/_build/linkcheck/output.json` | `changedir = docs` then `sphinx-build -b linkcheck source _build/linkcheck` | ✓ WIRED (fresh run produced the file, live-recounted) |
| `CLAUDE.md`/`README.md`/`contributing.rst` listing blocks | `tox.ini [testenv:linkcheck]` | the listed command names an environment that exists at this HEAD | ✓ WIRED |
| local canonical branch | `origin/gsd/v0.9.5-docs-link-check-and-navigation` | `git push --no-follow-tags -u` | ✓ WIRED (origin head equals `PUSHED_SHA`, tracking confirmed) |
| `gh workflow run CI --ref …` | `ci.yml` jobs on ubuntu/windows/macos | `workflow_dispatch` | ✓ WIRED (run 34761445288, headSha match, all 12 jobs success) |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| QUA-13 | 72-02, 72-05, 72-06 | `tox -e linkcheck` environment, network-only, passes clean | ✓ SATISFIED | Fresh run 95/95 working; outside `env_list`; no ignore-style key |
| DOC-24 | 72-03, 72-06 | Every listing surface names `tox -e linkcheck` | ✓ SATISFIED | Fresh grep confirms 3 edited surfaces, 2 correctly dispositioned as non-listing |
| DOC-18 | 72-01, 72-04, 72-05, 72-06 | Root toctrees list only section indexes; sidebar/Typst dedup | ✓ SATISFIED | Fresh clean builds confirm 0 duplicate messages, 1 sidebar link/page, 1 Typst edge/page |

No orphaned requirements: `.planning/REQUIREMENTS.md` maps exactly QUA-13, DOC-18, DOC-24 to Phase 72
("Mapped to phases: 4 (Phase 72: QUA-13, DOC-24, DOC-18 · Phase 73: REL-14)"), and all three appear
in the `requirements:` frontmatter of at least one of this phase's six plans. REQUIREMENTS.md's own
checkboxes remain `[ ]`/"Pending" at this writing — expected, since this project's convention is that
the orchestrator flips them centrally after verification passes, not the executing plans.

### Anti-Patterns Found

None. `grep -nE 'TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER'` over every product file this phase touched
(`tox.ini`, `CLAUDE.md`, `README.md`, `docs/source/index.rst`, `docs/source/contributing.rst`)
returns nothing. An independent `/code-review` pass already exists on disk
(`.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-REVIEW.md`, untracked,
`status: clean`, 0 critical, 0 warning, 1 info) — its one info-level note (linkcheck has no
failure-tolerance override for transient network flakiness) is an optional future refinement, not a
defect against this phase's scope, and is not repeated as a gap here.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| `tox -e linkcheck` passes clean | `rm -rf docs/_build/linkcheck && uv run tox -e linkcheck` | exit 0, 95/95 `working` | ✓ PASS |
| Clean HTML build has zero toctree duplication | `LANG=C LC_ALL=C sphinx-build -b html` | 0 `multiple toctrees`, `build succeeded, 3 warnings.` | ✓ PASS |
| Clean Typst build dedupes root includes | `LANG=C LC_ALL=C sphinx-build -b typst` | 0 root guard lines for the 5 pages; 1 edge/page in state | ✓ PASS |
| Local quality gates | `ruff check .`, `black --check .`, `mypy typsphinx/`, `pytest` | all exit 0; 1547 passed/1 skipped | ✓ PASS |
| Dispatched CI run all-green | `gh run view 34761445288 --json status,conclusion,headSha,jobs` | completed/success, 12/12 jobs success | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` files exist in this repository and none is named by any Phase 72
plan or SUMMARY. Step 7c: SKIPPED (no probes declared or discovered).

### Human Verification Required

### 1. Rendered furo sidebar shows each page once, correctly nested

**Test:** Open the phase tip's clean HTML build's `index.html` (rebuild with `tox -e docs-html` or a
manual clean `sphinx-build -b html` if needed) in a browser, and look at the left sidebar navigation.
**Expected:** Configuration, Builders, Templates and Output Layout appear once each, nested under
"User Guide"; Basic and Advanced appear once each, nested under "Examples". No page is duplicated
beside its section heading.
**Why human:** ROADMAP Phase 72 SC#4 names this explicitly as the human check the 2026-08-16 todo
asked for, and this verifier's own automated DOM count (each page = 1, confirmed above) proves the
structural fact but not the rendered visual outcome the todo was filed against.

### Gaps Summary

No gaps. Every ROADMAP Success Criterion (SC#1–SC#5) and all three requirement IDs (QUA-13, DOC-24,
DOC-18) were independently re-measured from a fresh checkout and confirmed true — not merely
asserted by the plans' own SUMMARY.md files. The only reason this report is not `passed` is that
SC#4 itself designates one item (the rendered sidebar) as an owner UAT check rather than something
grep or a build log can close; that is exactly the shape the ROADMAP anticipated, not a defect found
during verification.

---

_Verified: 2026-09-13_
_Verifier: Claude (gsd-verifier)_
