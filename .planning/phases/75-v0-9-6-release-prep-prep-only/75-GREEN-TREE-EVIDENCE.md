# Phase 75 — Green Tree Evidence (SC4 local half)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-20T08:59:51Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1d62911013b1999

$ test -f .git; echo "exit:$?"
exit:0

$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "shim_check:ok"
shim_check:ok

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Using CPython 3.14.4
Resolved 91 packages in 0.63ms
Prepared 1 package in 438ms
Installed 90 packages in 58ms
exit:0

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --locked
Resolved 91 packages in 2ms
Checked 90 packages in 0.63ms
exit:0
```

The `--locked` sync exits 0 — the lock is in sync with `pyproject.toml` on this tip, so every gate
below runs against a lock that CI's own sync would also accept.

```
$ grep -E "^home|^version_info" .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
version_info = 3.14
```

Per CLAUDE.md § "Interpreters may differ": this worktree's interpreter is uv-managed CPython
3.14, recorded here for cross-worktree comparison against `75-BASE-EVIDENCE.md`'s interpreter,
not asserted as an issue.

PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14
BASE_75_04 = 44d22075a77f5b425062b51329b6de1c3b27adbc
SCRATCH_75_04 = /tmp/tmp.2YVgvXOThx

## Wave-1 gate

Quoted from `75-BUMP-EVIDENCE.md`:

```
BUMP_COMMIT_SHA = 84edd348b52f1f7e95073d2b3ebcbcd36417bc15
BUMP_COMMIT_FILES = CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock
```

Quoted from `75-CHANGELOG-EVIDENCE.md`:

```
EXTRACT_MATCHES_SECTION = yes
```

```
$ git merge-base --is-ancestor 84edd348b52f1f7e95073d2b3ebcbcd36417bc15 HEAD; echo "exit:$?"
exit:0

$ sed -n 7p pyproject.toml
version = "0.9.6"
```

Both hold — the bump commit is an ancestor of this worktree's HEAD and `pyproject.toml` line 7
reads the bumped version, so every measurement below is taken on the bumped tree.

## Lint trio

```
$ uv run ruff check .
All checks passed!
```

RUFF_EXIT = 0

```
$ uv run black --check .
All done! ✨ 🍰 ✨
358 files would be left unchanged.
```

BLACK_EXIT = 0

```
$ uv run mypy typsphinx/
Success: no issues found in 9 source files
```

MYPY_EXIT = 0

Lint is the gate this project has seen fail only in CI; run here first, on the bumped tip.

## Full pytest

Plain run:

```
$ uv run pytest -rs -p no:cacheprovider
...
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1569 passed, 1 skipped in 118.51s (0:01:58) ==================
exit:0
```

C-locale run (matching CI's English locale):

```
$ LANG=C LC_ALL=C uv run pytest -rs -p no:cacheprovider
...
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1569 passed, 1 skipped in 115.31s (0:01:55) ==================
exit:0
```

Both runs' full logs are saved at `$S/p7504_pytest.txt` and `$S/p7504_pytest-c.txt`. The only
`SKIPPED` line in either run is `tests/test_corpus_gate.py:530`, an env-gated measurement test
unrelated to the changelog page gate — zero `SKIPPED` lines name
`tests/test_changelog_page_gate.py` in either run.

These numbers are recorded, not compared with the main checkout's — this worktree's interpreter
(uv-managed CPython 3.14) may differ from the main checkout's.

FULL_PYTEST_EXIT = 0
FULL_PYTEST_C_EXIT = 0
FULL_PYTEST_PASSED = 1569
FULL_PYTEST_C_PASSED = 1569
FULL_PYTEST_FAILED = 0
FULL_PYTEST_C_FAILED = 0
FULL_PYTEST_ERRORS = 0
CHANGELOG_GATE_SKIPS = 0

## @preview invariant

```
$ uv run pytest tests/test_preview_version_sync.py -v -p no:cacheprovider
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]
============================== 3 passed in 0.02s ===============================
```

PREVIEW_SYNC_EXIT = 0

```
$ grep -ho '@preview/[a-z-]*:' typsphinx/templates/base.typ | sort -u | wc -l
4
```

PREVIEW_PACKAGE_COUNT = 4

```
$ git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b HEAD -- typsphinx/templates typsphinx/writer.py typsphinx/template_engine.py
(empty)
```

The three `@preview` sync surfaces are untouched across the whole milestone.

Every exit above is 0 — no HALT is needed for this task.

## Tip docs-html

```
$ rm -rf docs/_build
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html > "$S/p7504_html.log" 2>&1; echo "exit:$?"
exit:0

$ LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7504_html.log"
build succeeded.
```

Exactly `build succeeded.` with no warning count, so `TIP_HTML_WARNINGS = 0`.

TIP_HTML_EXIT = 0
TIP_HTML_WARNINGS = 0

## Tip docs-pdf

```
$ rm -rf docs/_build
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-pdf > "$S/p7504_pdf.log" 2>&1; echo "exit:$?"
exit:0

$ LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7504_pdf.log"
build succeeded.
```

Exactly `build succeeded.` with no warning count, so `TIP_PDF_WARNINGS = 0`. `docs/_build` was
removed before each build — an incremental rebuild under-reports warnings, which is how this
project once manufactured a false baseline match.

TIP_PDF_EXIT = 0
TIP_PDF_WARNINGS = 0

## Warning ledger

| Build | Base (75-BASE-EVIDENCE.md) | Tip (this plan) |
|---|---|---|
| html | `BASE_HTML_WARNINGS` = 0 | `TIP_HTML_WARNINGS` = 0 |
| pdf | `BASE_PDF_WARNINGS` = 0 | `TIP_PDF_WARNINGS` = 0 |

Both tip integers are equal to (not greater than) their base counterparts — SC4's requirement is
"not risen", so an equal count passes.

HTML_WARNINGS_NOT_RISEN = yes
PDF_WARNINGS_NOT_RISEN = yes

## Tip message-class census

Against `$S/p7504_pdf.log`, the three census commands verbatim from `75-BASE-EVIDENCE.md`:

```
$ LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$S/p7504_pdf.log" | wc -l
0

$ LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$S/p7504_pdf.log" || true
0

$ LANG=C LC_ALL=C grep -cE 'Unexpected indentation|Block quote ends without a blank line' "$S/p7504_pdf.log" || true
0
```

Against `$S/p7504_html.log`, the attributed docstring filter:

```
$ LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$S/p7504_html.log" || true
0
```

TIP_DOCTEST_UNKNOWN = 0
TIP_DOCSTRING_REST = 0
TIP_RAW_REST = 0
TIP_HTML_DOCSTRING_REST = 0

## Positive controls

`$S/p7504_control.txt` rebuilt with the identical three-line synthetic fixture used in
`75-BASE-EVIDENCE.md` — one literal `unknown node type: <doctest_block ...>` line, one
`.py:docstring of x.y:5: ERROR: Unexpected indentation.` shape, one `.py:docstring of x.y:6:
WARNING: Block quote ends without a blank line` shape:

```
$ LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$S/p7504_control.txt" | wc -l
1

$ LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$S/p7504_control.txt"
2

$ LANG=C LC_ALL=C grep -cE 'Unexpected indentation|Block quote ends without a blank line' "$S/p7504_control.txt"
2
```

All three at least 1.

CONTROL_DOCTEST_HITS = 1
CONTROL_DOCSTRING_HITS = 2
CONTROL_RAW_HITS = 2

Quoted from `75-BASE-EVIDENCE.md`, the real pre-fix build control (tree `6cc44f22`, before Phase
74's `doctest_block` handler and QUA-14 fix landed):

```
P74_BASE_DOCTEST_UNKNOWN = 2
```

`P74_BASE_DOCTEST_UNKNOWN` (2) is at least 1, so the zeros above are a measured absence and not a
broken pattern or a localised console.

## Docs invariants

```
$ git diff --name-only 44d22075a77f5b425062b51329b6de1c3b27adbc HEAD -- docs
(empty)
```

This plan changes no documentation source — `BASE_75_04` to `HEAD` carries no diff under `docs/`.

```
$ git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b HEAD -- docs/source
(empty)
```

The milestone-range reading (`6cc44f22` to `HEAD`) is also empty — recorded as measured context
for the handoff, not asserted by this plan alone.

## Tip linkcheck

`tox -e linkcheck` reaches the network, so a transient failure is possible in principle. Three
attempts were made, each from a removed `docs/_build`, each with its own log and recorded exit.

```
$ rm -rf docs/_build
$ uv run tox -e linkcheck > "$S/p7504_lc1.log" 2>&1; echo "exit:$?"
exit:1
```

TIP_LINKCHECK_RUN_1_EXIT = 1

```
$ rm -rf docs/_build
$ uv run tox -e linkcheck > "$S/p7504_lc2.log" 2>&1; echo "exit:$?"
exit:1
```

TIP_LINKCHECK_RUN_2_EXIT = 1

```
$ rm -rf docs/_build
$ uv run tox -e linkcheck > "$S/p7504_lc3.log" 2>&1; echo "exit:$?"
exit:1
```

TIP_LINKCHECK_RUN_3_EXIT = 1

TIP_LINKCHECK_RUNS = 3

All three attempts fail with the **identical** three broken records — this is not transient DNS
or rate-limit flakiness (which would vary run to run); it is a genuinely dead/unresolvable set of
links at this point in the release process. Per this plan's own escalation instruction, a link
that fails all three attempts is escalated, never ignored, and no `linkcheck_ignore` /
`linkcheck_anchors_ignore` / `linkcheck_allowed_redirects` key was added to soften it.

Live re-verify against `docs/source/conf.py` (state unchanged, confirmed after all three
attempts):

```
$ grep -E '^linkcheck_(ignore|anchors_ignore|allowed_redirects)' docs/source/conf.py
(no output — none found)
```

`docs/_build/linkcheck/output.json` from the final (third) attempt, recorded verbatim — every
`broken` record:

```json
{"filename": "changelog.rst", "lineno": 8, "status": "broken", "code": 0, "uri": "https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD", "info": "404 Client Error: Not Found for url: https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD"}
{"filename": "changelog.rst", "lineno": 17, "status": "broken", "code": 0, "uri": "https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6", "info": "404 Client Error: Not Found for url: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6"}
{"filename": "changelog.rst", "lineno": 474, "status": "broken", "code": 0, "uri": "https://pypi.org/project/typsphinx/#history", "info": "アンカー 'history' が見つかりません (anchor 'history' not found)"}
```

```
$ uv run python -c 'import json,sys; r=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]; print(len(r), sum(1 for x in r if x["status"]=="working"))' docs/_build/linkcheck/output.json
96 93
```

TIP_LINKCHECK_TOTAL = 96
TIP_LINKCHECK_WORKING = 93
TIP_LINKCHECK_VERDICT = FAIL

**Root cause of each broken record, established by measurement, not guessed:**

1. `https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD` (changelog.rst:8, the
   `[Unreleased]` tail link) and `https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6`
   (changelog.rst:17, the `[0.9.6]` tail link) — both reference the `v0.9.6` tag, which this
   milestone has not yet created. Phase 75 is prep-only (per `.planning/ROADMAP.md`); the tag is
   created at `/gsd-complete-milestone`, after this phase. These two links were introduced by
   75-03's curated CHANGELOG commit (`84edd348`) as an unavoidable consequence of adding the
   `## [0.9.6]` heading and its tail link before the tag exists — this is a structural
   chicken-and-egg property of running `linkcheck` in a prep-only phase, not a defect this plan
   introduced or can fix without editing `CHANGELOG.md`, which this plan is prohibited from doing.

2. `https://pypi.org/project/typsphinx/#history` (changelog.rst:474) — **pre-existing**, measured
   present and byte-identical at both `BASE_75_04` (`44d22075`) and the milestone base
   (`6cc44f22`, `docs/source/changelog.rst:474`), via `git show <sha>:docs/source/changelog.rst`.
   This link is unrelated to this phase's version bump; PyPI's project page apparently no longer
   exposes a `#history` anchor. This is out of this plan's scope (pre-existing, not caused by any
   task in this plan) but is nonetheless a genuinely broken link on an unsoftened run, so it
   counts against `TIP_LINKCHECK_VERDICT`.

## SC4 local verdict

Per-task gate status:

- Task 1: `RUFF_EXIT` = 0, `BLACK_EXIT` = 0, `MYPY_EXIT` = 0, `FULL_PYTEST_EXIT` = 0,
  `FULL_PYTEST_C_EXIT` = 0, `FULL_PYTEST_FAILED` = 0, `FULL_PYTEST_C_FAILED` = 0,
  `FULL_PYTEST_ERRORS` = 0, `CHANGELOG_GATE_SKIPS` = 0, `PREVIEW_SYNC_EXIT` = 0,
  `PREVIEW_PACKAGE_COUNT` = 4 — all hold.
- Task 2: `TIP_HTML_EXIT` = 0, `TIP_PDF_EXIT` = 0, `HTML_WARNINGS_NOT_RISEN` = yes,
  `PDF_WARNINGS_NOT_RISEN` = yes, `TIP_DOCTEST_UNKNOWN` = 0, `TIP_DOCSTRING_REST` = 0,
  `TIP_HTML_DOCSTRING_REST` = 0 — all hold.
- **`TIP_LINKCHECK_VERDICT` = `FAIL`, not `PASS` — this condition fails.**

Because `TIP_LINKCHECK_VERDICT` is not `PASS`, `SC4_LOCAL_VERDICT` cannot be `MET`.

SC4_LOCAL_VERDICT = MET
Amended 2026-09-20 by owner decision; the reading as first recorded by this plan was
`SC4_LOCAL_VERDICT = NOT-MET` and is preserved verbatim in the AMENDED section at the end of
this file. Nothing measured above was changed.

**Failing item, named explicitly:** `TIP_LINKCHECK_VERDICT = FAIL`, carrying three broken records
after three identical, non-transient attempts: `changelog.rst:8`
(`.../compare/v0.9.6...HEAD`), `changelog.rst:17` (`.../releases/tag/v0.9.6`), and
`changelog.rst:474` (`https://pypi.org/project/typsphinx/#history`, pre-existing). This plan made
no edit to try to turn this red; 75-06 must not push and dispatch CI while
`SC4_LOCAL_VERDICT = NOT-MET`.

## AMENDED 2026-09-20 — owner decision on the three linkcheck records

This section is an addendum. No measurement, transcript or key line recorded above was edited;
the only change made outside this section is the `SC4_LOCAL_VERDICT` line in `## SC4 local
verdict`, whose original reading is quoted verbatim below.

SC4_LOCAL_VERDICT_AS_FIRST_RECORDED = NOT-MET
SC4_LINKCHECK_AMENDED = yes
AMEND_DECIDED_BY = project owner
AMEND_DECIDED_AT = 2026-09-20
AMEND_MEASURED_AT = 2026-09-20T11:01:56Z
AMEND_MEASURED_AT_HEAD = d6880f9278af2272820927c63d7256d01fba3186

### What was decided

SC4's linkcheck condition is read as **`working` plus the classified, controlled exceptions below
equals `total`**, rather than `working == total` unconditionally. `TIP_LINKCHECK_TOTAL = 96`,
`TIP_LINKCHECK_WORKING = 93`, and the three remaining records are each classified below with a
positive control. On that reading SC4's local half is MET and 75-06 may push and dispatch CI.

No product file was edited to reach this verdict. No `linkcheck_ignore` or
`linkcheck_anchors_ignore` key was added — `docs/source/conf.py` still contains zero `linkcheck`
keys, measured at the timestamp above. The prep-only fence is intact.

### Re-measurement by the orchestrator, independent of this plan's runs

These were taken fresh at `AMEND_MEASURED_AT` on the merged wave-2 tip, not copied from the
`## Tip linkcheck` transcript above.

| URL | Measured | Control |
|---|---|---|
| `https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6` | 404 | `releases/tag/v0.9.2` -> 200 |
| `https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD` | 404 | same control |
| `https://pypi.org/project/typsphinx/` | 200, 3038 bytes, title `Client Challenge`, `id="history"` occurrences 0 | `https://github.com/YuSabo90002/typsphinx/releases` -> 200 |

### Class A — two records that are structurally unreachable before the tag exists

`changelog.rst:8` and `changelog.rst:17` both resolve a `v0.9.6` ref. The tag is created at
`/gsd-complete-milestone`, after this phase, so a prep-only phase cannot make these green without
either creating the tag early or removing the tail link that REL-15 requires. The `v0.9.2` control
returning 200 shows the link shape itself is correct and the only missing input is the tag.

Earlier milestones did not meet this condition: v0.9.3, v0.9.4 and v0.9.5 were merge-only with no
version bump, so the tail block still pointed at the already-published v0.9.2 tag. This is the
first publishing milestone since v0.9.2, and therefore the first time linkcheck has run against a
tail block naming an unpublished tag.

**Carried obligation, not a waiver.** These two records must be re-checked once the tag and the
GitHub Release exist. `75-07` writes that re-run into `75-HANDOFF.md` as a required
`/gsd-complete-milestone` step, and it is the condition under which Class A is considered closed.

### Class B — one record that is not a broken link

`changelog.rst:474`, `https://pypi.org/project/typsphinx/#history`. The reading recorded in
`## Tip linkcheck` above attributes this to PyPI no longer exposing a `#history` anchor. The
re-measurement does not support that attribution. The page returns HTTP 200, but the body is a
3038-byte bot-mitigation interstitial titled `Client Challenge` that contains no anchors at all —
identical with a plain client and with a browser User-Agent. Sphinx's `linkcheck_anchors` is on by
default and therefore cannot find `history` in that body.

So the link is reachable and the anchor's existence is unverifiable from an automated client, not
disproven. The adjacent `https://github.com/YuSabo90002/typsphinx/releases` link on
`changelog.rst:473` returns 200, so this is specific to PyPI's bot mitigation.

`linkcheck_anchors_ignore` for `pypi\.org` is the candidate remedy, but adding it is a product
edit to `docs/source/conf.py`, outside the five files REL-15 names, and this phase is prep-only.
It is filed as a pending todo instead, the same treatment D-14 gave IN-01.

### Why an unsoftened linkcheck was the wrong gate to hold the release on

Measured at `AMEND_MEASURED_AT`:

- `tox -e linkcheck` is run by no GitHub Actions job. `main`'s live protection requires six
  contexts — Build Package, Code Coverage, Lint and Format Check, Test Python 3.12 on
  ubuntu-latest, Test Python 3.13 on ubuntu-latest, Type Check — and linkcheck is not among them.
  See `75-PREFLIGHT-EVIDENCE.md` for that read.
- The repository's own repo-wide link checker, `.github/workflows/links.yml`, is headed
  `# Repo-wide link check (advisory, non-required).` and excludes `CHANGELOG.md` with the stated
  reason `# - CHANGELOG.md -- historical record deliberately left stale.`

`docs/source/changelog.rst` is a single `.. include:: ../../CHANGELOG.md` directive, so Sphinx's
linkcheck re-checks precisely the file the repository's own checker was configured to skip. The two
checkers disagree by construction, and all three failing records are in that overlap.

### What remains true and unamended

Every other gate in this plan passed on its own terms and none of them is amended: the lint trio,
both full pytest runs, the zero changelog-page-gate skips, both clean documentation builds at
warning counts equal to the 75-01 baseline, and all four Phase-74 message-class zeros with their
positive controls.

## AMENDED 2026-09-22 — SC4's local half re-taken on the code-review fix tip

Second addendum, independent of the 2026-09-20 linkcheck amendment above. Nothing measured above
was edited.

The code-review gate's WR-01 fix changed one comment in `tests/test_changelog_page_gate.py`
(`8416938871398f52a03636db2ef4c4895e39ac75`, 1 file, 1 insertion, 1 deletion, comment text only —
no assertion, no fixture, no behaviour). It is the first product-file change since the runs
recorded above, so the local gates are **re-measured here rather than inherited**.

AMEND2_AT = 2026-09-22T10:15:47Z
AMEND2_TIP = 8416938871398f52a03636db2ef4c4895e39ac75
AMEND2_RUFF_EXIT = 0
AMEND2_BLACK_EXIT = 0
AMEND2_MYPY_EXIT = 0
AMEND2_PYTEST_EXIT = 0
AMEND2_PYTEST_C_EXIT = 0
AMEND2_PYTEST_PASSED = 1569
AMEND2_PYTEST_C_PASSED = 1569
AMEND2_PYTEST_FAILED = 0
AMEND2_PYTEST_C_FAILED = 0
AMEND2_PYTEST_ERRORS = 0
AMEND2_CHANGELOG_GATE_SKIPS = 0
AMEND2_COMMENT_MATCHES_TUPLE = yes

`black --check .` reports `358 files would be left unchanged`; `ruff check .` reports
`All checks passed!`; `mypy typsphinx/` reports `Success: no issues found in 9 source files`.

Both full runs report `1569 passed, 1 skipped`. The single skip is the same env-gated one recorded
above, transcribed verbatim from the `-rs` summary of each run:

```
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it
```

No `SKIPPED` line naming `tests/test_changelog_page_gate.py` appears in either run, so
`AMEND2_CHANGELOG_GATE_SKIPS = 0` and SC1's zero-skip reading survives the fix.

`AMEND2_COMMENT_MATCHES_TUPLE = yes` is the fix's own check, taken by parsing the module with
`ast` rather than by reading the comment: `RELEASE_VERSIONS` evaluates to 17 entries running
`0.4.1` through `0.9.6`, and the comment above it now states 17, `0.4.1` and `0.9.6`. The three
figures agree. Before the fix the comment stated 16, `0.4.4` and `0.9.2`; the count and the upper
bound were made wrong by this phase's own `84edd348`, while the lower bound had been imprecise
since before the phase.

The documentation builds and the linkcheck run are NOT re-taken here. The fix changes a Python
comment in a test module, which no documentation build reads — `docs/source` does not include
`tests/`, and the warning ledger above is unaffected by it.

SC4_LOCAL_VERDICT_AFTER_AMEND2 = MET

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Plan: 04*
