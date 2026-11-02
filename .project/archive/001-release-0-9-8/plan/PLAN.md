# Plan — typsphinx

<!-- Written by the planner role. Executed wave-by-wave by /gsd-path-build. -->

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — risk burn-down and independent fixes

Goal: Prove the stripped-PATH R010 graphviz proof passes in the NixOS devShell with `dot` on host PATH (the one low-confidence SYNTHESIS decision), giving a trustworthy 0-failed full-suite baseline; in parallel remove the inert `typst_debug` config value through the removed-config path (with its sphinx-build console surface) and correct CLAUDE.md. If the stripped-PATH build fails inside the FHS sandbox, the R010 proof mechanism must be re-decided before release prep.
Review depth: full

## Wave 2 — release readiness

Goal: Fold `[Unreleased]` into `## [0.9.8]` (including the `typst_debug` removal entry that wave 1 landed), fix the remaining stale doc claims, and prove the HEAD is release-ready: `scripts/extract_changelog_section.py 0.9.8` prints Graphviz and BibTeX, version is 0.9.8, `uv build` + `twine check` pass.
Review depth: full

## Surface contract

### CHANGELOG.md release notes — T004

Criteria: SC2
Entry: `uv run python scripts/extract_changelog_section.py 0.9.8` (the exact command `.github/workflows/release.yml` uses for the GitHub Release body), plus CHANGELOG.md opened at the top
States: empty — `## [Unreleased]` shows only `### Planned for Future Releases`; loading — n/a (synchronous CLI); error — the extractor exits non-zero with a "not found"/"empty section" message on stderr when the 0.9.8 section is missing or empty; success — exit 0 and stdout holds the 0.9.8 body with the Graphviz items first, then the BibTeX bibliography items, then the `typst_debug` removal entry
Walkthrough:
1. In a fresh worktree run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`.
2. Run `uv run python scripts/extract_changelog_section.py 0.9.8; echo "rc=$?"` and confirm rc=0 and the output contains `Graphviz`, `BibTeX`, and `typst_debug`, with Graphviz Added/Changed items before the bibliography ones.
3. Open CHANGELOG.md: `## [Unreleased]` holds only `### Planned for Future Releases`; the `## [0.9.8] - <date>` heading date equals the release-prep commit's date; the link block has `[Unreleased]: .../compare/v0.9.8...HEAD` and `[0.9.8]: .../releases/tag/v0.9.8`.
4. Open README.md: the Status line names v0.9.8, matching `pyproject.toml` `version = "0.9.8"`.

### sphinx-build console output — T002

Criteria: SC4
Entry: `sphinx-build -b typst <srcdir> <outdir>` on a project whose `conf.py` sets `typst_debug`
States: empty — a `conf.py` without `typst_debug` prints no `typst_debug` warning; loading — normal Sphinx progress lines; error — none expected: the removed-config warning never fails the build (only `-W` would); success — exactly one `WARNING: 'typst_debug' was removed in v0.9.8 ...` line on stderr, exit 0, and `.typ` output byte-identical to the same project without the setting
Walkthrough:
1. In a fresh worktree run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`.
2. Copy `examples/basic` to a scratch directory, build it with `LC_ALL=C uv run sphinx-build -E -b typst <copy> <out1>`.
3. Append `typst_debug = True` to the copy's `conf.py`, rebuild with `LC_ALL=C uv run sphinx-build -E -b typst <copy> <out2> 2> err.txt; echo "rc=$?"`.
4. Confirm rc=0, `grep -c "'typst_debug' was removed" err.txt` prints 1, and `diff -r -x .doctrees -x .buildinfo <out1> <out2>` prints nothing.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC1 | T001 | AC2 |
| SC1 | T001 | AC3 |
| SC1 | T001 | AC4 |
| SC2 | T004 | AC1 |
| SC2 | T004 | AC2 |
| SC2 | T004 | AC3 |
| SC2 | T004 | AC4 |
| SC2 | T004 | AC5 |
| SC3 | T003 | AC1 |
| SC3 | T003 | AC2 |
| SC3 | T003 | AC3 |
| SC3 | T003 | AC4 |
| SC3 | T003 | AC5 |
| SC3 | T003 | AC6 |
| SC4 | T002 | AC1 |
| SC4 | T002 | AC2 |
| SC4 | T002 | AC3 |
| SC4 | T002 | AC4 |
| SC4 | T004 | AC6 |
| SC5 | T004 | AC7 |
| SC6 | T004 | AC8 |

## Held-out checks

| Edge | Task | Test |
|------|------|------|
| E1 | T001 | tests/test_graphviz_render_gate.py::test_path_without_dot_removes_every_dot_entry |
| E2 | T004 | tests/test_release_0_9_8_docs_gate.py::test_0_9_8_graphviz_items_precede_bibliography_items |
| E4 | T004 | tests/test_release_0_9_8_docs_gate.py::test_0_9_8_date_is_release_prep_commit_date |

## Dependency notes

- T004 depends on T002 (landed effect, two parts): (1) the CHANGELOG 0.9.8 removal entry T004 writes must describe the shipped code (Prohibition N3) — a reviewer sees `"typst_debug"` absent from `typsphinx/__init__.py` and present as a key of `REMOVED_CONFIG_VALUES` in `typsphinx/removed_config.py` at T004's base; (2) T004 owns SC5, whose claim re-check covers DOCS-AUDIT #11/#12 in `examples/advanced/README.md`, a file T002 owns and fixes — a reviewer sees the `_templates/` tree line and the "edit `conf.py` and uncomment" sentence gone from that file at T004's base. T004's files do not overlap T002's; T004's test only reads `examples/advanced/README.md`.
- T001, T002, T003 are mutually independent and have disjoint files. T004 does not depend on T001 or T003: no file, symbol, or landed effect crosses those edges (SC1's full-suite and SC3's CLAUDE.md checks are owned and verified by T001/T003 themselves; the project Verify re-checks the whole suite at ship).
- DOCS-AUDIT remediation queue ownership: #1, #2, #3, #9, #10, #13 → T004; #4, #5, #6, #7, #8 → T003; #11, #12 → T002 (re-checked by T004 for SC5).
- Out of milestone (INTENT Constraints, Prohibitions N1/N2): pushing tag `v0.9.8`, PyPI publication, and the PR's six required checks run at ship/post-merge, never inside a task.
