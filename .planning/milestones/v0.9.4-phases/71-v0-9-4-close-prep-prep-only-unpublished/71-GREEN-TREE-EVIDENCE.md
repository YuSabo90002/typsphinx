# Phase 71 — Local Green-Tree Evidence (SC#3, local half)

## Head check and provisioning

- `date -u +%FT%TZ`: `2026-09-13T08:44:21Z`
- `pwd -P`: `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9`
- `test -f .git; echo "exit:$?"`: `exit:0`
- `grep -c typsphinx-fhs-run "$(command -v uv)"`: `2`
- Provisioning line run:
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`
  Tail of output:
  ```
  Installed 90 packages in 57ms
   ...
   + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9)
   + typst==0.15.0
   + urllib3==2.7.0
   + uv==0.12.13
   + virtualenv==21.5.1
  ```

BASE_71_03 = 7a42bf996b1aaca24a8b17346be78459e6d41e2b

SCRATCH_71_03 = /tmp/claude-1000/-home-yuta-Documents-typsphinx/2ab7ea40-2eb1-4a24-8331-4523dc2e4c54/scratchpad/p7103_6qoXbt

`git log --oneline -8`:
```
7a42bf99 docs(phase-71): update tracking after wave 1, mark wave 2 executing
e66d7b6e chore: merge executor worktree (worktree-agent-a571bab6fc41395dc)
c20ebaae chore: merge executor worktree (worktree-agent-a1002cdd91840430e)
fdc4ed14 docs(71-02): complete REL-13 closeout guard, SC#1 obs1, COVERAGE.md plan
5460c11a docs(71-01): complete v0.9.4 CHANGELOG bullet plan
1c6876a8 test(71-01): prove the CHANGELOG bullet is pure addition against the clean docs baseline
7610872f docs(71-02): write reasoned no-external-API COVERAGE.md, gate passes
9b0dd645 fix(71-02): put CODE_FREEZE_ANCHOR on its own bare key line
```

## Tree identity

- `uv run python -c "import typsphinx, sys; print(typsphinx.__version__); print(typsphinx.__file__)"`:
  ```
  0.9.2
  /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/typsphinx/__init__.py
  ```
  The path lies inside this worktree, proving the worktree's own editable copy is measured, not
  the main checkout's.

TYPSPHINX_FILE = /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/typsphinx/__init__.py

- `uv run python -c "import myst_parser; print(myst_parser.__version__)"`: `5.1.0` — proves the
  docs extra is present.

- `.venv/pyvenv.cfg` (this worktree):
  ```
  home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
  implementation = CPython
  uv = 0.11.25
  version_info = 3.13.13
  include-system-site-packages = false
  prompt = typsphinx
  ```

PYVENV_HOME_71_03 = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin

PYVENV_VERSION_71_03 = 3.13.13

- `/home/yuta/Documents/typsphinx/.venv/pyvenv.cfg` (main checkout, read-only):
  ```
  home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
  implementation = CPython
  uv = 0.11.25
  version_info = 3.13.13
  include-system-site-packages = false
  prompt = typsphinx
  ```

MAIN_PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin

MAIN_PYVENV_VERSION = 3.13.13

Both trees' `pyvenv.cfg` `home` and `version_info` are identical — CPython 3.13.13, same nix store
path. No interpreter difference exists between this worktree and the main checkout, so counts
compared below are compared across identical interpreters.

## Product-tree delta and D-05

PHASE_BASE_SHA (from `71-CLOSEOUT-GUARD.md`) = f1f7d54a61d74c3972f1df0508ac994c001dda7e

- `git diff --stat f1f7d54a61d74c3972f1df0508ac994c001dda7e HEAD -- . ':(exclude).planning'`:
  ```
   CHANGELOG.md | 10 ++++++++++
   1 file changed, 10 insertions(+)
  ```
  Exactly one file, `CHANGELOG.md`, 10 insertions, zero deletions.

PRODUCT_DELTA = CHANGELOG.md

- `git fetch origin main` ran cleanly (FETCH_HEAD updated).
- `git rev-parse origin/main`:

ORIGIN_MAIN_SHA_71_03 = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d

- `git merge-base HEAD origin/main`: `d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d` — equal to
  `MILESTONE_BASE` from `71-SC1-INVARIANTS.md` (`d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d`).

MAIN_ABSORBED = no

- `git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"`: `exit:0`.
  `exit:0` means `origin/main` has not moved past the milestone base, so there is nothing to
  absorb (D-05 today). The merge-base equals `MILESTONE_BASE` exactly, which is what D-05
  requires; a merge-base different from `MILESTONE_BASE` would have been the breach, and none
  occurred.

The non-empty `CHANGELOG.md`-only delta is the positive control on the anchor: it proves the diff
command actually detects change (it is not silently comparing a tree to itself), and the single
file is why 71-01's docs comparison and this plan's final-tree docs comparison (Task 3) apply to
the same product tree — nothing else moved between 71-01's post-edit measurement and this plan's
run.

## Full suite

- `uv run pytest --collect-only -q -p no:cacheprovider` tail:
  ```
  ======================== 1548 tests collected in 1.62s =========================
  ```

COLLECTED_71_03 = 1548

- `uv run pytest -q -rs -p no:cacheprovider` ran in the foreground, exit 0, one pass (no split
  needed — completed in 127.97s). Short summary and final line, verbatim:
  ```
  SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
  1547 passed, 1 skipped in 127.97s (0:02:07)
  ```

FULL_SUMMARY = 1547 passed, 1 skipped

FULL_FAILED = 0

FULL_SKIPPED = 1

The one skip is `tests/test_corpus_gate.py:530`, an env-gated SC#3 before/after measurement
(`TYPSPHINX_CORPUS_REPORT=1` required) — the same skip reason Phase 70's after-side run recorded,
by design (RESEARCH Open Question 1).

Phase 70's `PYTEST_RESULT_AFTER` (from `70-AFTER-RUNTIME-EVIDENCE.md:73`) is `1547 passed 1
skipped`, on CPython 3.13.13. `FULL_SUMMARY` here is `1547 passed, 1 skipped`, also on CPython
3.13.13 — the two agree exactly, on the same interpreter version. Since Phase 70's after-side
measurement, only the `CHANGELOG.md` bullet changed (per the Product-tree delta above), and that
change carries no test-visible effect, consistent with the identical counts.

No failure occurred; no `## HALT` heading is written in this section.

## Full suite under LC_ALL=C

- Head check re-run: `date -u +%FT%TZ` = `2026-09-13T08:48:53Z`; `pwd -P` still inside this
  worktree; `test -f .git; echo "exit:$?"` = `exit:0`; `grep -c typsphinx-fhs-run "$(command -v
  uv)"` = `2`.
- `LC_ALL=C uv run pytest -q -rs -p no:cacheprovider` ran in the foreground, exit 0, one pass (no
  split needed — completed in 125.80s). Final summary line and the skip, verbatim:
  ```
  SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
  1547 passed, 1 skipped in 125.80s (0:02:05)
  ```

LCALLC_SUMMARY = 1547 passed, 1 skipped

LCALLC_FAILED = 0

The run is repeated under `LC_ALL=C` because CI runs in English and warning-text assertions have
failed only on CI before, never locally under the host's `ja_JP.UTF-8` locale (ROADMAP SC#3).

## Format, type and lint

- `uv run black --check .; echo "exit:$?"`:
  ```
  All done! ✨ 🍰 ✨
  355 files would be left unchanged.
  exit:0
  ```

BLACK_EXIT = 0

- `uv run mypy typsphinx/; echo "exit:$?"`:
  ```
  Success: no issues found in 9 source files
  exit:0
  ```

MYPY_EXIT = 0

- `uv run ruff --version`: `ruff 0.16.6`

RUFF_LOCAL_VERSION = 0.16.6

This equals `uv.lock`'s pinned ruff (`name = "ruff"` / `version = "0.16.6"`).

- `uv run ruff check .; echo "exit:$?"`:
  ```
  All checks passed!
  exit:0
  ```

RUFF_LOCAL_EXIT = 0

CI's `Lint and Format Check` job holds lint authority (ROADMAP constraint 8); plan 71-04 reads its
verdict. This local run is additive, not a substitute for that authority.

## Version-sync family

- `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v -p
  no:cacheprovider`:
  ```
  tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED [ 25%]
  tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 50%]
  tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 75%]
  tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]
  4 passed in 0.03s
  ```
- `uv run pytest tests/test_extension.py -k version_matches_pyproject_toml -v -p no:cacheprovider`:
  ```
  tests/test_extension.py::test_version_matches_pyproject_toml PASSED      [100%]
  1 passed, 5 deselected in 0.02s
  ```

VERSION_SYNC_FAILED = 0

This runs even though no version literal moves in this plan: it is the mechanism that would catch
one moving, and constraint 12 keeps the `@preview` count at four.

## Changelog page gate

- `LC_ALL=C uv run pytest tests/test_changelog_page_gate.py -v -rs -p no:cacheprovider`:
  ```
  tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_delegates_to_changelog_md PASSED [ 16%]
  tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_carries_no_hand_maintained_release_history PASSED [ 33%]
  tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_carries_every_release PASSED [ 50%]
  tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_has_one_changelog_heading PASSED [ 66%]
  tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_build_emits_no_changelog_warnings PASSED [ 83%]
  tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf PASSED [100%]
  6 passed in 3.90s
  ```

CHANGELOG_GATE_SUMMARY = 6 passed

CHANGELOG_GATE_SKIPPED = 0

Both `myst_parser` and `typst` are importable in this worktree (confirmed in `## Tree identity`
and by this run's own zero-skip result), so every build class in the module — the HTML content
coverage class and the PDF include-compile class, not only the always-on delegation class —
actually executed. No skip is recorded as a pass; there was no skip to record.

## Docs builds on the merged tree

Head check re-run before this section: `date -u +%FT%TZ` and `pwd -P` confirmed the worktree
unchanged from the prior sections; `test -f .git; echo "exit:$?"` = `exit:0`; the provisioning
line is unchanged from Task 1 (no re-sync needed — the venv was already provisioned).

Each build is preceded immediately by `rm -rf docs/_build`, and run under `LC_ALL=C`.

- `LC_ALL=C uv run tox -e docs-html`, tail:
  ```
  追加のページを出力中... search 完了
  English (code: en) の検索インデックスを出力... 完了
  オブジェクト インベントリを出力... 完了
  build succeeded, 3 warnings.

  HTMLページは_build/htmlにあります。
    docs-html: OK (3.83=setup[0.10]+cmd[3.73] seconds)
    congratulations :) (3.85 seconds)
  ```
  Every `WARNING` line:
  ```
  22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
  44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
  418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
  /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
  ```

DOCS_HTML_WARN_FINAL = 3

- `LC_ALL=C uv run tox -e docs-pdf`, tail:
  ```
  typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
  Compiling 1 master document(s) to PDF...
  Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/docs/_build/pdf/typsphinx.pdf
  build succeeded, 5 warnings.
    docs-pdf: OK (4.27=setup[0.10]+cmd[4.18] seconds)
    congratulations :) (4.29 seconds)
  ```
  Every `WARNING` line:
  ```
  22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
  44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
  418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
  /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
  WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
  WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
  ```

DOCS_PDF_WARN_FINAL = 5

- `head -c 5 docs/_build/pdf/typsphinx.pdf`: `%PDF-`

PDF_MAGIC = %PDF-

- `ls -l docs/_build/pdf/typsphinx.pdf`:
  ```
  -rw-r--r-- 1 yuta users 2789972 9月 13 17:53 /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a43d13d9aa59679b9/docs/_build/pdf/typsphinx.pdf
  ```

`71-CHANGELOG-EVIDENCE.md`'s `DOCS_HTML_WARN_BASE` = 3 and `DOCS_PDF_WARN_BASE` = 5 (its clean
pre-edit baseline, taken in worktree `agent-a1002cdd91840430e`). Both pairs are equal:
`DOCS_HTML_WARN_FINAL` (3) = `DOCS_HTML_WARN_BASE` (3); `DOCS_PDF_WARN_FINAL` (5) =
`DOCS_PDF_WARN_BASE` (5). The `WARNING` line text is identical between that baseline and this run
except for the worktree-path prefix on the docstring warning line, which differs only because the
two runs execute in different worktree directories — the same source line
(`typsphinx/translator.py` docstring of `visit_toctree`) is cited in both.

Both this worktree's and 71-01's worktree's `.venv/pyvenv.cfg` report `version_info = 3.13.13` on
CPython built from the same nix store path (`/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`)
— confirmed in `## Tree identity` above for this worktree, and by `71-CHANGELOG-EVIDENCE.md`'s own
record for the 71-01 worktree. No interpreter difference exists between the two measurements, so
the equal counts trace to an unchanged docs tree (the one-file `CHANGELOG.md` delta carries no
docs-visible content, since `changelog.rst` delegates to `CHANGELOG.md` at build time and both
runs build the same post-edit `CHANGELOG.md`), not to a coincidence across different toolchains.

## Division of authority

- `71-CHANGELOG-EVIDENCE.md` (plan 71-01) decides the pre-edit-versus-post-edit docs comparison,
  taken inside one tree/worktree, around the single `CHANGELOG.md` edit.
- This file (`71-GREEN-TREE-EVIDENCE.md`, plan 71-03) decides the full pytest suite (twice), the
  format/type/local-lint trio, the version-sync family, the changelog page gate, and the
  final-merged-tree docs builds compared against 71-01's baseline.
- `71-CI-EVIDENCE.md` (plan 71-04, running in parallel in a different worktree) decides the
  three-OS CI matrix and holds the authoritative lint verdict (ROADMAP constraint 8).
- `71-PREFLIGHT-EVIDENCE.md` (plan 71-05, running in parallel in a different worktree) decides the
  non-committing trial merge against `origin/main`.

This file does not read 71-04's or 71-05's results, and they do not read this file's — each
plan's evidence stands on its own runs. Plan 71-07 sets all four side by side in the closing
handoff.

## Executed versus skipped

| Gate | Outcome | Note |
|------|---------|------|
| Tree identity (worktree editable install, docs extra) | executed-green | `typsphinx.__file__` inside worktree; `myst_parser` importable |
| Product-tree delta from `PHASE_BASE_SHA` | executed-green | `CHANGELOG.md` only, 0 deletions |
| D-05 non-absorption (`origin/main` merge-base) | executed-green | equals `MILESTONE_BASE`, `main` not absorbed |
| Full pytest suite (default locale) | executed-green | 1547 passed, 1 skipped (env-gated corpus measurement) |
| Full pytest suite under `LC_ALL=C` | executed-green | 1547 passed, 1 skipped, same env-gated skip |
| `black --check .` | executed-green | 355 files unchanged |
| `mypy typsphinx/` | executed-green | no issues, 9 source files |
| `ruff check .` | executed-green | all checks passed, version 0.16.6 matches `uv.lock` |
| Version-sync family (readme, preview, extension) | executed-green | 5/5 relevant tests passed |
| Changelog page gate | executed-green | 6 passed, 0 skipped (docs extra + typst both present) |
| `docs-html` clean build | executed-green | 3 warnings, matches 71-01's pre-edit baseline |
| `docs-pdf` clean build | executed-green | 5 warnings, matches 71-01's pre-edit baseline; PDF starts `%PDF-` |
| CI three-OS matrix / lint authority | not executed here | owned by plan 71-04 (`71-CI-EVIDENCE.md`), running in parallel |
| Trial merge against `origin/main` | not executed here | owned by plan 71-05 (`71-PREFLIGHT-EVIDENCE.md`), running in parallel |

Nothing this plan attempted is left implied: every row above ran to a real, quoted outcome.

## SC#3 local verdict

All of the following hold: `FULL_FAILED` = 0, `LCALLC_FAILED` = 0, `BLACK_EXIT` = 0, `MYPY_EXIT` =
0, `RUFF_LOCAL_EXIT` = 0, `VERSION_SYNC_FAILED` = 0; `CHANGELOG_GATE_SKIPPED` = 0; both docs pairs
are equal (`DOCS_HTML_WARN_FINAL` = `DOCS_HTML_WARN_BASE`, `DOCS_PDF_WARN_FINAL` =
`DOCS_PDF_WARN_BASE`); `PDF_MAGIC` is `%PDF-`.

SC3_LOCAL_VERDICT = MET
