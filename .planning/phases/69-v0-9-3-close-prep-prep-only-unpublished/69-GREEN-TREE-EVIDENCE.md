# Phase 69 — Local Green-Tree Evidence (SC#3, local half)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T22:47:17Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
...
 + ruff==0.15.20
 ...
 + tox==4.56.1
 + tox-uv==1.36.0
 + tox-uv-bare==1.36.0
 ...
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b)
 + typst==0.15.0
 ...
 + uv==0.12.13
 + virtualenv==21.5.1
```

Both extras synced without error (`myst-parser`, `furo`, `sphinx-autodoc-typehints`, `sphinx-intl` all
present in the resolved set, confirming the docs extra is live).

Before any commit in this plan:

```
$ git rev-parse HEAD
becd70c31bfed573dc10cdc20dcf7a30d57edd57
```

BASE_69_03 = becd70c31bfed573dc10cdc20dcf7a30d57edd57

```
$ git log --oneline -8
becd70c3 docs(phase-69): update tracking after wave 1, mark wave 2 executing
56880eca docs(69-01): move key-line prose off five evidence keys (format only)
435cbbfe chore: merge executor worktree (worktree-agent-ab4c25ec1378d6a2a)
11e8da4d chore: merge executor worktree (worktree-agent-abe1318883a64e327)
ac13a1de docs(69-01): complete CHANGELOG-bullets-and-clean-docs-proof plan
98cbc372 docs(69-02): complete REL-12 fence, SC#1 observation 1 and COVERAGE.md plan
a30fd6f2 feat(69-01): author DEP and NIX changelog bullets, full pure-addition and fence proof
0527f857 docs(69-02): write reasoned no-external-API COVERAGE.md
```

This confirms wave 1 (69-01, 69-02) is merged into this worktree's HEAD before this plan's first
commit.

## Tree identity

```
$ uv run python -c "import typsphinx, sys; print(typsphinx.__version__); print(typsphinx.__file__)"
0.9.2
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b/typsphinx/__init__.py
```

TYPSPHINX_FILE = /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b/typsphinx/__init__.py

The printed path resolves **inside this worktree**, not the main checkout
(`/home/yuta/Documents/typsphinx/typsphinx`) — this proves the worktree's own editable install is
what every measurement below exercises, not a stale main-checkout copy.

```
$ uv run python -c "import myst_parser; print(myst_parser.__version__)"
5.1.0
```

`myst_parser` imports successfully, proving the docs extra is present in this worktree's venv.

```
$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx
```

PYVENV_HOME_69_03 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_69_03 = 3.14

```
$ cat /home/yuta/Documents/typsphinx/.venv/pyvenv.cfg   (read-only, main checkout)
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

MAIN_PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
MAIN_PYVENV_VERSION = 3.13.13

**The two interpreters differ**, exactly as CLAUDE.md's "Interpreters may differ" note anticipates:
this worktree's fresh `uv sync` built its `.venv` on uv-managed CPython 3.14, while the main
checkout's `.venv` is on nixpkgs' `python3-3.13.13`. Counts taken in this worktree (below) are
compared only against baselines recorded inside worktrees of this same phase family
(`69-CHANGELOG-EVIDENCE.md`'s own `agent-ab4c25ec1378d6a2a` worktree, also uv-managed CPython 3.14 —
confirmed identical interpreter in that file's own § "Head check and provisioning"), never against
the main checkout's counts, so no comparison in this evidence file crosses an interpreter boundary.

## Product-tree delta and D-06

`PHASE_BASE_SHA` read from `69-CLOSEOUT-GUARD.md`:

```
$ sed -n "s/^PHASE_BASE_SHA = //p" 69-CLOSEOUT-GUARD.md
2db4e803d36d5f7a5db0a92b08cac4988fa88957
```

```
$ git diff --stat 2db4e803d36d5f7a5db0a92b08cac4988fa88957 HEAD -- . ':(exclude).planning'
 CHANGELOG.md | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)

$ git diff --name-only 2db4e803d36d5f7a5db0a92b08cac4988fa88957 HEAD -- . ':(exclude).planning'
CHANGELOG.md
```

PRODUCT_DELTA = CHANGELOG.md

Exactly one product-tree file changed since the phase base, with 25 insertions and zero deletions —
this is the positive control on the anchor: a non-empty, single-file diff proves `PHASE_BASE_SHA` is
a real ancestor rather than a mistaken pointer at HEAD itself (which would also print an empty diff).
This is the same single file `69-01`'s worktree edited (its own `CHANGELOG.md` diff against the same
base is likewise exactly `CHANGELOG.md`, 25 insertions per `69-CHANGELOG-EVIDENCE.md`'s "Pure-addition
proof" section) — confirming this plan's tree and 69-01's tree carry the identical product-tree
content, so a docs render measured in one worktree applies equally to the other.

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"
exit:1
```

MAIN_ABSORBED = no

`origin/main` is NOT an ancestor of this worktree's HEAD (exit 1) — D-06's non-absorption
requirement holds: this phase's merged tree has not absorbed `main`, and the SC#3 green measured
below is proven on this phase's own tip, not on a tree that pulled in `main`'s lock or `ruff` 0.16.x.

## Full suite

```
$ uv run pytest --collect-only -q -p no:cacheprovider
...
======================== 1548 tests collected in 1.22s =========================
```

COLLECTED_69_03 = 1548

```
$ uv run pytest -q -rs -p no:cacheprovider
...
=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1547 passed, 1 skipped in 116.80s (0:01:56) ==================
```

Run in a single foreground Bash call (well inside the 600000 ms budget; total wall time 116.80s) — no
split was needed.

FULL_SUMMARY = 1547 passed, 1 skipped
FULL_FAILED = 0
FULL_SKIPPED = 1

Every skip accounted for by its printed reason: `tests/test_corpus_gate.py::test_empty_url_before_after`
is deliberately env-gated behind `TYPSPHINX_CORPUS_REPORT=1` (an opt-in before/after measurement,
RESEARCH Open Question 1) — not a failure, not a hidden pass, exactly one skip and it is this one.

`COLLECTED_69_03` (1548) equals `1547 passed + 1 skipped` (1548) from the live run — the collect
count and the executed-plus-skipped count agree.

## Full suite under LC_ALL=C

Re-ran the head check and the provisioning line at the start of this task:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Resolved 91 packages in 0.73ms
Checked 90 packages in 0.71ms
```

No drift from Task 1's sync.

```
$ LC_ALL=C uv run pytest -q -rs -p no:cacheprovider
...
=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1547 passed, 1 skipped in 114.04s (0:01:54) ==================
```

Run in a single foreground Bash call (114.04s wall time, well inside the 600000 ms budget) — no split
was needed.

LCALLC_SUMMARY = 1547 passed, 1 skipped
LCALLC_FAILED = 0

Why this run is repeated: CI runs in English, and warning-text assertions have failed only on CI
before (the `CI-only defect class` this project has hit previously is locale-dependent warning text
that renders differently under a non-English `LANG`) — re-running the full suite under `LC_ALL=C`
locally pre-empts that class rather than discovering it only after a CI dispatch.

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
ruff 0.15.20
```

RUFF_LOCAL_VERSION = 0.15.20

```
$ uv run ruff check .; echo "exit:$?"
All checks passed!
exit:0
```

RUFF_LOCAL_EXIT = 0

CI's `Lint and Format Check` job holds lint authority (ROADMAP constraint 7), and plan 69-04 reads
its verdict from a real dispatched CI run against the three-OS matrix — this local run is additive,
proving the gates pass on this worktree's own uv-managed CPython 3.14 interpreter, not a substitute
for CI's verdict.

## Version-sync family

```
$ uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- .../agent-a69047240a759c44b/.venv/bin/python
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 4 items

tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [ 25%]
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 50%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 75%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 4 passed in 0.02s ===============================

$ uv run pytest tests/test_extension.py -k version_matches_pyproject_toml -v -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- .../agent-a69047240a759c44b/.venv/bin/python
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 6 items / 5 deselected / 1 selected

tests/test_extension.py::test_version_matches_pyproject_toml PASSED      [100%]

======================= 1 passed, 5 deselected in 0.02s ========================
```

VERSION_SYNC_FAILED = 0

This runs even though no version literal moves this phase (D-06/no version bump in Phase 69): it is
the mechanism that would catch a version literal moving out of sync between `pyproject.toml`,
`README.md` and the four `@preview` package declaration sites — running it by name is the only way
to actually confirm the guard itself is intact on this tree, not an assumption that it must be
because nothing touched a version string.

## Changelog page gate

```
$ uv run pytest tests/test_changelog_page_gate.py -v -rs -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- .../agent-a69047240a759c44b/.venv/bin/python
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 6 items

tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_delegates_to_changelog_md PASSED [ 16%]
tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_carries_no_hand_maintained_release_history PASSED [ 33%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_carries_every_release PASSED [ 50%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_has_one_changelog_heading PASSED [ 66%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_build_emits_no_changelog_warnings PASSED [ 83%]
tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf PASSED [100%]

============================== 6 passed in 3.24s ===============================
```

CHANGELOG_GATE_SUMMARY = 6 passed
CHANGELOG_GATE_SKIPPED = 0

All six build classes ran — none skipped. A skip here would mean the docs extra is missing
(`myst_parser` unimportable); with the docs extra provisioned (confirmed in Task 1's Tree identity
section), the gate executed against the tree carrying this milestone's three CHANGELOG bullets,
including `TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf`, which drives
the PDF build class end to end.

## Docs builds on the merged tree

Re-ran the head check and the provisioning line at the start of this task:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Resolved 91 packages in 0.67ms
Checked 90 packages in 0.43ms
```

No drift from Tasks 1-2's sync.

```
$ rm -rf docs/_build && uv run tox -e docs-html
...
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.22=setup[0.10]+cmd[3.12] seconds)
  congratulations :) (3.25 seconds)
```

`WARNING` lines (identical set to `69-CHANGELOG-EVIDENCE.md`'s pre-edit and post-edit baselines — the
four pre-existing `visit_toctree` docstring warnings, unrelated to `CHANGELOG.md`):

```
21::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
43::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
417::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
444:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

DOCS_HTML_WARN_FINAL = 3

```
$ rm -rf docs/_build && uv run tox -e docs-pdf
...
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (3.84=setup[0.08]+cmd[3.75] seconds)
  congratulations :) (3.86 seconds)
```

`WARNING` lines (identical set to the baseline — the same four docstring warnings plus the two
pre-existing `doctest_block` unknown-node-type warnings):

```
22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
445:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a69047240a759c44b/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
456:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
462:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

DOCS_PDF_WARN_FINAL = 5

```
$ head -c 5 docs/_build/pdf/typsphinx.pdf
%PDF-
```

PDF_MAGIC = %PDF-

```
$ ls -l docs/_build/pdf/typsphinx.pdf
-rw-r--r-- 1 yuta users 2786762  9月 13 07:54 docs/_build/pdf/typsphinx.pdf
```

`DOCS_HTML_WARN_BASE` and `DOCS_PDF_WARN_BASE` read from `69-CHANGELOG-EVIDENCE.md`:

```
$ grep '^DOCS_HTML_WARN_BASE = ' 69-CHANGELOG-EVIDENCE.md
DOCS_HTML_WARN_BASE = 3

$ grep '^DOCS_PDF_WARN_BASE = ' 69-CHANGELOG-EVIDENCE.md
DOCS_PDF_WARN_BASE = 5
```

Both final counts equal their clean pre-edit baselines exactly (3 = 3, 5 = 5), and the `WARNING`
lines are the same sets in each case. No interpreter-traced drift occurred — both this worktree's
build and `69-CHANGELOG-EVIDENCE.md`'s build ran on uv-managed CPython 3.14 (this file's own § "Tree
identity" and `69-CHANGELOG-EVIDENCE.md`'s § "Head check and provisioning" both record
`version_info = 3.14`), so there is no interpreter boundary crossed by this comparison and no basis
to attribute any difference to interpreter drift — because there is no difference to attribute.

## Division of authority

Three evidence files, each authoritative for a different slice of SC#3 and the merged tree's health:

- **`69-CHANGELOG-EVIDENCE.md`** (plan 69-01) is authoritative for the pre-edit versus post-edit docs
  warning-count comparison taken inside one tree, at the moment `CHANGELOG.md` was actually edited.
- **This file (`69-GREEN-TREE-EVIDENCE.md`, plan 69-03)** is authoritative for the full pytest suite
  (twice, once under `LC_ALL=C`), format/type/lint, the version-sync family, the changelog page gate,
  and the final-tree clean docs builds compared against 69-01's baseline.
- **`69-CI-EVIDENCE.md`** (plan 69-04, running in parallel in wave 2) is authoritative for the
  three-OS CI matrix and the lint verdict, since CI holds lint authority on this project.

This file does not read 69-04's results — plan 69-06 (wave 3) sets the two side by side.

## Executed versus skipped

| Gate | Outcome |
|------|---------|
| Full pytest suite (`uv run pytest -q -rs`) | Executed — green: 1547 passed, 1 skipped, 0 failed |
| Full pytest suite under `LC_ALL=C` | Executed — green: 1547 passed, 1 skipped, 0 failed |
| `uv run black --check .` | Executed — green (355 files unchanged) |
| `uv run mypy typsphinx/` | Executed — green (no issues, 9 source files) |
| `uv run ruff check .` | Executed — green (`All checks passed!`, local ruff 0.15.20; CI's `Lint and Format Check` job holds lint authority per ROADMAP constraint 7, read by 69-04) |
| `tests/test_readme_version_sync.py` + `tests/test_preview_version_sync.py` | Executed — green (4 passed) |
| `tests/test_extension.py::test_version_matches_pyproject_toml` | Executed — green (1 passed) |
| `tests/test_changelog_page_gate.py` (docs extra present) | Executed — green (6 passed, 0 skipped) |
| `uv run tox -e docs-html` (clean build) | Executed — green (3 warnings, equals baseline) |
| `uv run tox -e docs-pdf` (clean build) | Executed — green (5 warnings, equals baseline; PDF starts `%PDF-`) |
| CI 3-OS matrix and lint verdict | Not executed here by design — authoritative source is `69-CI-EVIDENCE.md` (plan 69-04), read together in plan 69-06 |

Nothing in this table is implied: every gate this plan attempted ran to completion, and the one gate
this plan deliberately does not own (the CI matrix) is named with its actual owner rather than left
silent.

## SC#3 local verdict

Checking every condition:

- `FULL_FAILED` = 0, `LCALLC_FAILED` = 0
- `BLACK_EXIT` = 0, `MYPY_EXIT` = 0, `RUFF_LOCAL_EXIT` = 0
- `CHANGELOG_GATE_SKIPPED` = 0
- `DOCS_HTML_WARN_FINAL` (3) = `DOCS_HTML_WARN_BASE` (3); `DOCS_PDF_WARN_FINAL` (5) = `DOCS_PDF_WARN_BASE` (5)
- `PDF_MAGIC` = `%PDF-`

All conditions hold.

SC3_LOCAL_VERDICT = MET
