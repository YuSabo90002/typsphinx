# Phase 73 — Local Green-Tree Evidence (SC#3, local half)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-16T10:11:45Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning line:
```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
...
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba)
 + typst==0.15.0
 + uv==0.12.13
 + virtualenv==21.5.1
```
(tail: same package set 73-01 recorded — tox-uv, tox-uv-bare, sphinx 9.1.0, myst_parser bundled via
the docs extra chain)

Before any commit:

```
BASE_73_03 = a54a2d8a3b06b388c7ee004e5cfbe3405431421d
SCRATCH_73_03 = /tmp/tmp.9hhDlqX1X4
```

```
$ git log --oneline -8
a54a2d8a docs(phase-73): update tracking after wave 1
7894302a chore: merge executor worktree (worktree-agent-af4a9f698bf799c4a)
2b387010 chore: merge executor worktree (worktree-agent-a347b03dff012a923)
7e56a23b docs(73-01): finalize measured commit count in summary
7edf13c8 docs(73-01): record self-check and measured commit ledger in summary
67b426f4 docs(73-01): add plan summary
60d085a5 docs(73-02): complete phase-head REL-14 fence, SC#1 observation 1, and API coverage plan
a108cba2 docs(73-01): complete CHANGELOG evidence with pure-addition proof and gates
```

**Precondition check.** `73-CHANGELOG-EVIDENCE.md`, `73-CLOSEOUT-GUARD.md` and
`73-SC1-INVARIANTS.md` all exist; none carries a `## HALT` heading (`grep -l '^## HALT'` over all
three: exit 1, no match). The `CHANGELOG.md` region between `## [Unreleased]` and `## [0.9.2]`
holds `### Added`, `### Changed`, `### Fixed` (in that order) and 6 bold-lead bullets — precondition
met.

## Tree identity

```
$ uv run python -c "import typsphinx, sys; print(typsphinx.__version__); print(typsphinx.__file__)"
0.9.2
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba/typsphinx/__init__.py
```

TYPSPHINX_FILE = /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba/typsphinx/__init__.py

The path lies inside this worktree — this worktree's own editable copy is measured, not the main
checkout's.

```
$ uv run python -c "import myst_parser; print(myst_parser.__version__)"
5.1.0
```

The docs extra is present; `myst_parser` imports cleanly.

`.venv/pyvenv.cfg` (this worktree):
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

```
PYVENV_HOME_73_03 = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_73_03 = 3.13.13
```

`/home/yuta/Documents/typsphinx/.venv/pyvenv.cfg` (main checkout, read-only):
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

```
MAIN_PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
MAIN_PYVENV_VERSION = 3.13.13
```

Both trees report the identical `home` and `version_info` (`3.13.13`, the same nixpkgs interpreter
store path) — no interpreter difference between this worktree and the main checkout. Counts below
are therefore compared directly, with no interpreter-drift caveat needed.

## Product-tree delta and non-absorption

`PHASE_BASE_SHA` read from `73-CLOSEOUT-GUARD.md`:
```
$ sed -n 's/^PHASE_BASE_SHA = //p' .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CLOSEOUT-GUARD.md
c6bc641aa1745e6413b4f33c4d0c572a962da430
```

```
$ git diff --stat c6bc641aa1745e6413b4f33c4d0c572a962da430 HEAD -- . ':(exclude).planning'
 CHANGELOG.md | 15 +++++++++++++++
 1 file changed, 15 insertions(+)
```

PRODUCT_DELTA = CHANGELOG.md

Exactly one file, `CHANGELOG.md`, 15 insertions, 0 deletions.

```
$ git diff --name-only c6bc641aa1745e6413b4f33c4d0c572a962da430 HEAD -- docs/source/conf.py
(no output)
```

`docs/source/conf.py` is unchanged since the phase base.

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git rev-parse origin/main
6e2b789922207eb72e7aef3216fdfd924dd4bcd9

$ git merge-base HEAD origin/main
098a8ff64cf008822eef9dc69f75102ded3f7bc1
```

```
ORIGIN_MAIN_SHA_73_03 = 6e2b789922207eb72e7aef3216fdfd924dd4bcd9
MAIN_ABSORBED = no
```

The merge-base of HEAD and `origin/main` equals `MILESTONE_BASE` from `73-SC1-INVARIANTS.md`
(`098a8ff64cf008822eef9dc69f75102ded3f7bc1`) — no commit from `origin/main` has been absorbed into
this branch.

```
$ git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"
exit:1
```

`exit:1` means `origin/main` has moved past the milestone base and this branch has not absorbed
those later commits — this is D-07's expected case (plan 73-05's trial merge measures against the
live `origin/main` tip separately). The merge-base staying at `MILESTONE_BASE` is what matters here,
and it does.

The non-empty `CHANGELOG.md`-only delta is the positive control on the anchor: `PHASE_BASE_SHA` is
real, reachable, and genuinely earlier than HEAD (an anchor mistake would either show no diff or a
much wider diff). The single-file delta is why 73-01's docs comparison and this plan's docs
comparison (Task 3) apply to the same product tree.

## Full suite

```
$ uv run pytest --collect-only -q -p no:cacheprovider
...
1548 tests collected
```

COLLECTED_73_03 = 1548

```
$ uv run pytest -q -rs -p no:cacheprovider > "$SCRATCH_73_03/p7303_full.log" 2>&1; echo "exit:$?"
exit:0
```

Final summary line and skip lines, verbatim from `$SCRATCH_73_03/p7303_full.log`:
```
=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1547 passed, 1 skipped in 127.68s (0:02:07) ==================
```

```
FULL_SUMMARY = 1547 passed, 1 skipped
FULL_PASSED = 1547
FULL_FAILED = 0
FULL_SKIPPED = 1
```

Every skip accounted for: the single skip is `tests/test_corpus_gate.py:530`, an env-gated
before/after corpus measurement that requires `TYPSPHINX_CORPUS_REPORT=1` to run (RESEARCH Open
Question 1) — not a defect, a deliberately opt-in test.

Phase 72's counts, quoted from `72-GATES-EVIDENCE.md` § "Local gate quartet":
```
PYTEST_PASSED (Phase 72) = 1547
PYTEST_SKIPPED (Phase 72) = 1
```

`FULL_SUMMARY` (1547 passed, 1 skipped) agrees exactly with Phase 72's counts, on the same
interpreter (3.13.13, both `PYVENV_VERSION_73_03` and Phase 72's recorded interpreter). Only
`CHANGELOG.md` changed since Phase 72, and it is a documentation file with no test-visible effect,
so an unchanged suite count is the expected outcome, not coincidence.

No failure occurred, so no `## HALT` heading is written and no test id needs to be quoted.

## Head check and provisioning (Task 2 re-run)

```
$ date -u +%FT%TZ
2026-09-16T10:20:00Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning already completed in Task 1 (same worktree, same `.venv`); no re-provisioning needed
or performed for Task 2.

## Full suite under LC_ALL=C

The full pytest suite is run a second time under `LC_ALL=C` because CI runs in English, and
warning-text assertions in this project have failed only on CI before, never locally under the
host's own locale (ROADMAP SC#3) — this run closes that gap by reproducing the CI locale here.

```
$ LC_ALL=C uv run pytest -q -rs -p no:cacheprovider > "$SCRATCH_73_03/p7303_lcallc.log" 2>&1; echo "exit:$?"
exit:0
```

Summary, verbatim from `$SCRATCH_73_03/p7303_lcallc.log`:
```
=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1547 passed, 1 skipped in 125.44s (0:02:05) ==================
```

```
LCALLC_SUMMARY = 1547 passed, 1 skipped
LCALLC_PASSED = 1547
LCALLC_FAILED = 0
```

No failure occurred, so no `## HALT` heading is written.

## Format, type and lint

```
$ uv run black --check .; echo "exit:$?"
All done! ✨ 🍰 ✨
355 files would be left unchanged.
exit:0
```
BLACK_EXIT = 0

```
$ uv run mypy typsphinx/; echo "exit:$?"
Success: no issues found in 9 source files
exit:0
```
MYPY_EXIT = 0

```
$ uv run ruff --version
ruff 0.16.6
```
RUFF_LOCAL_VERSION = 0.16.6

```
$ grep -A1 -xF 'name = "ruff"' uv.lock
name = "ruff"
version = "0.16.6"
```
`RUFF_LOCAL_VERSION` (0.16.6) equals the ruff version pinned in `uv.lock` (0.16.6).

```
$ uv run ruff check .; echo "exit:$?"
All checks passed!
exit:0
```
RUFF_LOCAL_EXIT = 0

CI's `Lint and Format Check` job holds lint authority; plan 73-04 (running in parallel) reads its
verdict from the CI run. This local run is additive evidence, not a substitute.

## Version-sync family

```
$ uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v -p no:cacheprovider
tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [ 25%]
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 50%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 75%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 4 passed in 0.03s ===============================
```

```
$ uv run pytest tests/test_extension.py -k version_matches_pyproject_toml -v -p no:cacheprovider
tests/test_extension.py::test_version_matches_pyproject_toml PASSED      [100%]

======================= 1 passed, 5 deselected in 0.03s ========================
```

VERSION_SYNC_FAILED = 0

This runs even though no version literal moves in this phase: it is the mechanism that would catch
one moving, and constraint 2 keeps the `@preview` count at four with no version change in this
phase.

## Changelog page gate

```
$ LC_ALL=C uv run pytest tests/test_changelog_page_gate.py -v -rs -p no:cacheprovider
tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_delegates_to_changelog_md PASSED [ 16%]
tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_carries_no_hand_maintained_release_history PASSED [ 33%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_carries_every_release PASSED [ 50%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_has_one_changelog_heading PASSED [ 66%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_build_emits_no_changelog_warnings PASSED [ 83%]
tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf PASSED [100%]

============================== 6 passed in 3.89s ===============================
```

```
CHANGELOG_GATE_SUMMARY = 6 passed
CHANGELOG_GATE_SKIPPED = 0
```

No skip occurred — the docs extra (`myst_parser`, confirmed importable in Task 1's Tree Identity
section) is present in this worktree's `.venv`, so both build-dependent test classes
(`TestChangelogPageContentCoverage`, `TestChangelogIncludeCompilesToPdf`) ran rather than skipping.
A skip here would mean the docs extra is missing; provisioning was already confirmed correct in
Task 1, so no re-provisioning or re-run was needed.

## Head check and provisioning (Task 3 re-run)

```
$ date -u +%FT%TZ
2026-09-16T10:22:00Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning already completed in Task 1 (same worktree, same `.venv`); no re-provisioning
performed for Task 3.

## Docs builds on the merged tree

`73-CHANGELOG-EVIDENCE.md`'s clean phase-base baselines, read with the key reader:
```
DOCS_HTML_WARN_BASE = 3
DOCS_PDF_WARN_BASE = 5
```

`rm -rf docs/_build`, then `LANG=C LC_ALL=C uv run tox -e docs-html`, logged to
`$SCRATCH_73_03/p7303_html.log`:

```
$ rm -rf docs/_build && LANG=C LC_ALL=C uv run tox -e docs-html; echo "exit:$?"
exit:0
```

~~~text docs-html-final-warnings
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
~~~

```
build succeeded, 3 warnings.
```

```
DOCS_HTML_WARN_FINAL = 3
MULTI_TOCTREE_HTML_FINAL = 0
```

`DOCS_HTML_WARN_FINAL` (3) equals `DOCS_HTML_WARN_BASE` (3), and the WARNING lines are identical
apart from the worktree path prefix (`agent-ae72cfbb6dc9782ba` here vs. `agent-af4a9f698bf799c4a`
in 73-01's worktree) — no new warning, no drift.

`rm -rf docs/_build`, then `LANG=C LC_ALL=C uv run tox -e docs-pdf`, logged to
`$SCRATCH_73_03/p7303_pdf.log`:

```
$ rm -rf docs/_build && LANG=C LC_ALL=C uv run tox -e docs-pdf; echo "exit:$?"
exit:0
```

~~~text docs-pdf-final-warnings
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae72cfbb6dc9782ba/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
~~~

```
build succeeded, 5 warnings.
```

```
DOCS_PDF_WARN_FINAL = 5
MULTI_TOCTREE_PDF_FINAL = 0
```

`DOCS_PDF_WARN_FINAL` (5) equals `DOCS_PDF_WARN_BASE` (5), and the WARNING lines are identical
apart from the worktree path prefix — no new warning, no drift.

```
$ head -c 5 "$SCRATCH_73_03/p7303_final.pdf"
%PDF-

$ ls -l "$SCRATCH_73_03/p7303_final.pdf"
-rw-r--r-- 1 yuta users 2794665 ... p7303_final.pdf
```

PDF_MAGIC = %PDF-

Both interpreters are the same nixpkgs `python3-3.13.13` (recorded in Task 1's Tree Identity
section for both this worktree and the main checkout, and 73-01's `PYVENV_VERSION_73_01 = 3.13.13`
in `73-CHANGELOG-EVIDENCE.md`), so the equal counts trace to an unchanged docs tree, not to a
masked interpreter difference. Neither multiple-toctrees final count is non-zero, so no
`## HALT: docs warning drift` or `## HALT: multiple toctrees on the merged tree` is written.

## Linkcheck

Run 1, from a clean output directory:

```
$ rm -rf docs/_build/linkcheck
$ uv run tox -e linkcheck > "$SCRATCH_73_03/p7303_linkcheck_run1.log" 2>&1; echo "exit:$?"
exit:0
```

```
LINKCHECK_RUN_1_EXIT = 0
```

`output.json` copied to `$SCRATCH_73_03/p7303_linkcheck_run1_output.json` (95 lines) and read with
`uv run python -c`:

```
TOTAL 95
WORKING 95
CENSUS {'working': 95}
```

```
LINKCHECK_RUN_1_TOTAL = 95
LINKCHECK_RUN_1_WORKING = 95
LINKCHECK_RUN_1_STATUS_CENSUS = working:95
```

Every row is `working` and exit is 0 — this run passes; no non-`working` row to quote; no second
run needed.

```
LINKCHECK_RUNS = 1
LINKCHECK_PASS_RUN = 1
LINKCHECK_TOTAL = 95
LINKCHECK_WORKING = 95
LINKCHECK_VERDICT = PASS
```

Phase 72's `TIP_LINKCHECK_TOTAL` (context only, never a threshold — constraint 8):
```
$ grep -n 'TIP_LINKCHECK_TOTAL' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-GATES-EVIDENCE.md
86:TIP_LINKCHECK_TOTAL = 95
```
The count (95) is identical to Phase 72's, which is expected since the only product-tree change
since the phase base is `CHANGELOG.md`, containing no links.

```
$ grep -c '^linkcheck_' docs/source/conf.py || true
0

$ git diff --name-only c6bc641aa1745e6413b4f33c4d0c572a962da430 -- docs/source/conf.py
(no output)
```

No `linkcheck_` key was added to `docs/source/conf.py`, and the file is unchanged since the phase
base (D-05: `CHANGELOG.md` is the only product-tree file this phase authors).

## Division of authority

- `73-CHANGELOG-EVIDENCE.md` — the pre-edit versus post-edit CHANGELOG.md comparison in one tree
  (73-01's own worktree).
- This file (`73-GREEN-TREE-EVIDENCE.md`) — the full pytest suite (twice), format/type/local lint,
  the version-sync family, the changelog page gate, the final-tree docs builds against 73-01's
  clean baseline, and the linkcheck verdict.
- `73-CI-EVIDENCE.md` (plan 73-04, running in parallel with this plan) — the three-OS CI matrix and
  the lint verdict authority.
- `73-PREFLIGHT-EVIDENCE.md` (plan 73-05, running in parallel with this plan) — the trial merge
  against `origin/main`.

This file does not read 73-04's or 73-05's results; they run in parallel and share no file with
this plan. Plan 73-07 sets all evidence side by side in the phase handoff.

## Executed versus skipped

| Gate | Outcome | Reason |
|------|---------|--------|
| Tree identity (`typsphinx.__file__`, `myst_parser`, interpreter pair) | executed-green | Both trees on the same interpreter (3.13.13); worktree copy confirmed |
| Product-tree delta from `PHASE_BASE_SHA` | executed-green | Exactly `CHANGELOG.md`, 15 insertions, 0 deletions; `docs/source/conf.py` unchanged |
| Non-absorption (`origin/main` merge-base) | executed-green | Merge-base equals `MILESTONE_BASE`; `main` not absorbed |
| Full pytest suite | executed-green | 1547 passed, 1 skipped (env-gated), 0 failed |
| Full pytest suite under `LC_ALL=C` | executed-green | 1547 passed, 1 skipped (env-gated), 0 failed |
| `black --check .` | executed-green | exit 0 |
| `mypy typsphinx/` | executed-green | exit 0 |
| `ruff check .` | executed-green | exit 0; local version 0.16.6 matches `uv.lock` |
| Version-sync family (readme, preview, extension) | executed-green | 5 tests, 0 failed |
| Changelog page gate | executed-green | 6 passed, 0 skipped |
| `docs-html` clean build | executed-green | 3 warnings, matches phase-base baseline, 0 multiple-toctrees |
| `docs-pdf` clean build | executed-green | 5 warnings, matches phase-base baseline, 0 multiple-toctrees, PDF begins `%PDF-` |
| `tox -e linkcheck` | executed-green | Run 1 of 1: 95/95 rows `working`, exit 0 |

Nothing in this plan's scope was not-executable; every gate attempted ran and is reported above.

## SC#3 local verdict

Checking all conditions:
- `FULL_FAILED = 0`, `LCALLC_FAILED = 0` — met
- `BLACK_EXIT = 0`, `MYPY_EXIT = 0`, `RUFF_LOCAL_EXIT = 0`, `VERSION_SYNC_FAILED = 0` — met
- `CHANGELOG_GATE_SKIPPED = 0` — met
- `DOCS_HTML_WARN_FINAL = DOCS_HTML_WARN_BASE` (3 = 3), `DOCS_PDF_WARN_FINAL = DOCS_PDF_WARN_BASE`
  (5 = 5), both `MULTI_TOCTREE_*_FINAL = 0`, `PDF_MAGIC = %PDF-` — met
- `LINKCHECK_VERDICT = PASS` — met

```
SC3_LOCAL_VERDICT = MET
```

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 03 (Tasks 1-3)*
