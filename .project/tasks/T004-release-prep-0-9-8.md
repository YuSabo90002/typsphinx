---
id: T004
title: Fold Unreleased into 0.9.8, fix the remaining stale doc claims, and prove release readiness
wave: 2
deps: [T002]
status: done
agent: build_T004
base: c76c3e238a828e75daf1fe922d064afa4979bfb6
worktree: null
task_branch: null
files:
  - CHANGELOG.md
  - README.md
  - docs/S03-ARTIFACT-GATE-EVIDENCE.md
  - docs/S04-PUBLISHED-SITE-EVIDENCE.md
  - examples/charged-ieee/README.md
  - tests/test_release_0_9_8_docs_gate.py
---

# T004 — Fold Unreleased into 0.9.8, fix the remaining stale doc claims, and prove release readiness

## Context

README/CHANGELOG present 0.9.8 as released, but no `v0.9.8` tag exists and PyPI serves 0.9.7. The owner ruled (DOCS-AUDIT #1, #2): fold `[Unreleased]` into `## [0.9.8]`, keep `pyproject.toml` at 0.9.8, no 0.9.9; the tag push and PyPI confirmation happen after the milestone PR merges, outside this task. CHANGELOG.md today: `## [Unreleased]` (line 8) holds bibliography `### Added` (two BibTeX/bibliography items) and `### Changed` (README no longer lists bibliography as a limitation), then `### Planned for Future Releases`; `## [0.9.8] - 2026-09-30` (line 53) holds Graphviz `### Added`, `### Changed`, `### Known Limitations`, `### Fixed`. The link block already has `[Unreleased]: .../compare/v0.9.8...HEAD` (last line) and a `[0.9.8]:` link to the GitHub release page for tag v0.9.8 (line 1554) — verify, do not re-add. A second, unrelated `## [Unreleased]` heading deep in the tail stays as-is (`scripts/extract_changelog_section.py` is positional and relies on that). T002 landed the `typst_debug` removal (`REMOVED_CONFIG_VALUES["typst_debug"]`, message `'typst_debug' was removed in v0.9.8 ...`), which this task records in 0.9.8. This task also fixes DOCS-AUDIT #3, #9, #10, #13 and owns the SC5 re-check, which includes #11/#12 that T002 fixed in `examples/advanced/README.md`.

## Approach

- CHANGELOG fold: move the Unreleased Added items after the existing Graphviz Added items in 0.9.8's `### Added`, and the Unreleased Changed item after the Graphviz Changed items in 0.9.8's `### Changed` (Edge E2). Leave `## [Unreleased]` with only `### Planned for Future Releases`. Add the `typst_debug` removal under a `### Removed` subsection of 0.9.8 (Keep a Changelog convention used elsewhere in the file), saying it was registered but never read, now warns once by name and is ignored, and changes no build output. The lead paragraph may be extended to mention bibliography support.
- 0.9.8 date (Edge E4): set the heading to `## [0.9.8] - <YYYY-MM-DD of the release-prep commit>` (today's date when you write it). Never change it to a later tag date.
- DOCS-AUDIT #3: the 0.9.8 `### Fixed` item must point at the 0.6.0 entry (the "Graceful degradation" line lives in `## [0.6.0]`, around CHANGELOG.md:986), not "the 0.9.4 entry" (no 0.9.4 heading exists). Do not rewrite the 0.6.0 entry itself.
- README.md: Status line must name v0.9.8 matching `pyproject.toml` `version = "0.9.8"` (`tests/test_readme_version_sync.py` guards it). It already does; change it only if needed. Do not edit `pyproject.toml`.
- DOCS-AUDIT #9 (`docs/S03-ARTIFACT-GATE-EVIDENCE.md`): append a section headed `## Correction` stating that CI run 41152681591 shows `test_no_graphviz_binary_is_installed` PASSED on ubuntu-latest (py3.12, py3.13), so `dot` was not on PATH in those test jobs, contradicting the "`ubuntu-latest` image preinstalls `dot`" sentence. Evidence docs are append-only: do not delete the original sentence.
- DOCS-AUDIT #10 (`docs/S04-PUBLISHED-SITE-EVIDENCE.md`): append a section headed `## Post-merge results` recording that the fix merged (`6c55e5b1`, PR #165) and that https://typsphinx.readthedocs.io/en/latest/user_guide/diagrams.html, checked on 2026-11-03, shows `class="graphviz"` (A1) and a referenced `graphviz-*.png` (A2), plus the A3 result if you can measure it (re-measure with `curl`; record `unverifiable` with the reason if the network is unavailable — do not invent results).
- DOCS-AUDIT #13 (`examples/charged-ieee/README.md`): limit the rich-author-details statement to Approach 1; say Approach 2 hardcodes department/organization in `examples/charged-ieee/approach2/source/_typst/_template.typ`. The text "on both approaches" must not remain there. `tests/test_examples_charged_ieee_gate.py` must still pass.
- New `tests/test_release_0_9_8_docs_gate.py` (reads files only; no Sphinx build):
  - `test_0_9_8_graphviz_items_precede_bibliography_items` (E2): within 0.9.8's `### Added` and `### Changed`, every Graphviz item precedes every former-Unreleased bibliography item (e.g. locate items by stable markers such as `GVZ-`/`DEG-01` vs `R001-R010`/`R013`/`bibliography`).
  - `test_0_9_8_date_is_release_prep_commit_date` (E4): the heading date equals the committer date (`%cs`) of the oldest commit whose diff adds that exact heading line (`git log --reverse -S'<heading line>' --format=%cs -- CHANGELOG.md`); when no commit has it yet (uncommitted patch), it equals today's date. `pytest.skip` (not fail) when git is unavailable or `git rev-parse --is-shallow-repository` is `true` (CI's `actions/checkout` is depth 1). The test never reads any tag date.
  - SC2 structure checks: `## [Unreleased]` (the first one) contains only `### Planned for Future Releases`; link block has `[Unreleased]` comparing `v0.9.8...HEAD` and `[0.9.8]` linking the GitHub release page for tag v0.9.8; 0.9.8 section mentions `typst_debug`.
  - SC5 claim re-checks, one per DOCS-AUDIT item: #3 (no "0.9.4 entry" text; Fixed item names 0.6.0), #9 (S03 has `## Correction` citing `41152681591`), #10 (S04 has `## Post-merge results` mentioning `class="graphviz"`), #11 (`examples/advanced/README.md` has no `_templates/` line), #12 (no "edit `conf.py` and uncomment"), #13 (charged-ieee README lacks "on both approaches").
  - Must pass on the CI matrix (ubuntu, windows, macos): read files with `encoding="utf-8"`, resolve paths from `Path(__file__)`.
- Prohibition N3 (judgment): every 0.9.8 CHANGELOG/README claim must match the code at the shipped HEAD — do not claim `typst_debug` ever did anything, do not claim features the package lacks.
- Prohibitions N1/N2 (judgment): do not create, move, delete, or push any git tag (including `v0.9.8`), do not publish anything from `gsd-path/M001`, and do not alter existing tags up to v0.9.7 or any PyPI release. The post-merge `v0.9.8` tag goes only on the CI-green `main` merge commit, outside this task.
- Do not touch `.planning/` references, `@preview` versions, or `flake.nix`.

## Interface contract

- `typsphinx.removed_config.REMOVED_CONFIG_VALUES` (type `dict[str, str]`) contains the key `"typst_debug"`; its message string starts with `'typst_debug' was removed in v0.9.8`.
- `examples/advanced/README.md` contains no line with `_templates/` and no text `edit \`conf.py\` and uncomment`.

## Intent coverage

- SC2
- SC4
- SC5
- SC6

## Acceptance criteria

1. In CHANGELOG.md, the first `## [Unreleased]` contains only `### Planned for Future Releases`, and `## [0.9.8] - <date>` holds the existing Graphviz entries followed by the former Unreleased bibliography Added/Changed entries.
2. E2 (held-out, ruling): within 0.9.8's Added and Changed lists, the existing Graphviz items come first and the former Unreleased bibliography items follow — `tests/test_release_0_9_8_docs_gate.py::test_0_9_8_graphviz_items_precede_bibliography_items` passes.
3. E4 (held-out, ruling): the 0.9.8 date is the release-prep commit's date and is not corrected to the later tag date — `tests/test_release_0_9_8_docs_gate.py::test_0_9_8_date_is_release_prep_commit_date` passes.
4. The link block has `[Unreleased]` comparing `v0.9.8...HEAD` and `[0.9.8]` pointing at `releases/tag/v0.9.8`; README.md's status line names v0.9.8, matching `pyproject.toml` version 0.9.8.
5. At the CHANGELOG.md release notes surface, `uv run python scripts/extract_changelog_section.py 0.9.8` exits 0 and prints a section containing both `Graphviz` and `BibTeX`.
6. The CHANGELOG 0.9.8 section records the `typst_debug` removal (SC4), consistent with T002's landed code.
7. DOCS-AUDIT items #3 and #9–#13 are fixed: each item's claim re-check in `tests/test_release_0_9_8_docs_gate.py` passes, and no stale claim remains (SC5).
8. Release-ready (SC6, task-local part): `pyproject.toml` version is `0.9.8`, `uv run python scripts/extract_changelog_section.py 0.9.8` exits 0, and `uv build` followed by `uv run twine check dist/*` passes. (The PR's six required checks are proven at ship.)

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/test_release_0_9_8_docs_gate.py tests/test_changelog_extraction.py tests/test_readme_version_sync.py tests/test_examples_charged_ieee_gate.py tests/test_no_stale_github_io_links.py tests/test_bundle_layout_sweep_gate.py -o addopts="" -q -rs && LC_ALL=C uv run pytest "tests/test_release_0_9_8_docs_gate.py::test_0_9_8_graphviz_items_precede_bibliography_items" "tests/test_release_0_9_8_docs_gate.py::test_0_9_8_date_is_release_prep_commit_date" -o addopts="" -q -rs && grep -q '^version = "0.9.8"' pyproject.toml && n=$(mktemp) && uv run python scripts/extract_changelog_section.py 0.9.8 > "$n" && grep -q Graphviz "$n" && grep -q BibTeX "$n" && grep -q typst_debug "$n" && grep -q 'Stable (v0.9.8)' README.md && uv run black --check tests/test_release_0_9_8_docs_gate.py && uv run ruff check tests/test_release_0_9_8_docs_gate.py && rm -rf dist && uv build && uv run twine check dist/*
```

Heavy: no

## Log

- 2026-11-03 — created by planner
- 2026-11-03 — build_T004: CHANGELOG.md: first `## [Unreleased]` now holds only `### Planned for Future Releases`; bibliography Added (R001-R010, R013) appended after Graphviz Added and README Changed item after DEG-01 Changed in `## [0.9.8] - 2026-11-03`; lead paragraph extended (bibliography + `typst_debug` removal); new `### Removed` item for `typst_debug` worded from `typsphinx/removed_config.py` (registered but never read, one warning by name, ignored, no output change); Fixed item now names the 0.6.0 entry (#3). Link block already correct (verified, not re-added); README status already `Stable (v0.9.8)` (unchanged). S03: appended `## Correction` citing CI run 41152681591 (#9). S04: appended `## Post-merge results` — measured live with curl 2026-11-03 JST: HTTP 200; A1 PASS (`class="graphviz"` x1); A2 PASS (`_images/graphviz-9d601b68….png` HTTP 200, image/png, `\x89PNG`, 11362 bytes); A3 PASS (`digraph dogfood {` 0 in visible text and raw HTML); merge `6c55e5b1` PR #165 (#10). charged-ieee README: rich author details limited to Approach 1; "on both approaches" removed (#13). Deviation: Approach asked to name `approach2/source/_typst/_template.typ`, but `tests/test_bundle_layout_sweep_gate.py` (in Verify) forbids the `/_template.typ` basename in that README, so the text points at "its custom Typst template in `approach2/source/_typst/`". New `tests/test_release_0_9_8_docs_gate.py` (file reads + git log for E4; skips on no git / shallow). Note for landing: E4 test expects the heading date 2026-11-03 to equal the `%cs` committer date of the commit that adds it — the landing commit must be dated 2026-11-03 (committer TZ), else the heading must be updated to that date. Verify (full command, exact) exit 0: 34 passed; 3 passed; black/ruff clean; uv build + twine check PASSED for wheel and sdist. Log: /tmp/claude-1000/-home-yuta-Documents-typsphinx/e3f192a2-e39e-4324-9fe0-108e1e879fe0/scratchpad/t004-verify.log. Re-synced main `.venv` with `--extra dev --extra docs` afterwards. No tags created or pushed.
- 2026-11-02 — orchestrator Verify (sidecar gsd-path-verify/task-t004-verify): pass, exit 0; output tail:
  ```
  adding 'typsphinx/__init__.py'
  adding 'typsphinx/builder.py'
  adding 'typsphinx/pathfmt.py'
  adding 'typsphinx/pdf.py'
  adding 'typsphinx/removed_config.py'
  adding 'typsphinx/template_engine.py'
  adding 'typsphinx/template_registry.py'
  adding 'typsphinx/translator.py'
  adding 'typsphinx/writer.py'
  adding 'typsphinx/templates/README.md'
  adding 'typsphinx/templates/base.typ'
  adding 'typsphinx-0.9.8.dist-info/licenses/LICENSE'
  adding 'typsphinx-0.9.8.dist-info/METADATA'
  adding 'typsphinx-0.9.8.dist-info/WHEEL'
  adding 'typsphinx-0.9.8.dist-info/entry_points.txt'
  adding 'typsphinx-0.9.8.dist-info/top_level.txt'
  adding 'typsphinx-0.9.8.dist-info/RECORD'
  removing build/bdist.linux-x86_64/wheel
  Successfully built dist/typsphinx-0.9.8.tar.gz
  Successfully built dist/typsphinx-0.9.8-py3-none-any.whl
  ```
