# Intent — typsphinx

Lane: quick   <!-- release prep (version, CHANGELOG, README, release gate) plus the charged-ieee example/README fixes fit two deliverable-sized tasks in one wave; no RESEARCH or NEEDS-USER items; no cross-wave risk -->

Review panel: off

Finding skeptics: off

Surfaces: CHANGELOG.md release notes (`scripts/extract_changelog_section.py 0.10.0` output), README.md status line, examples/charged-ieee PDFs and README

## Summary

Release preparation for typsphinx 0.10.0 on top of 81af8d6b. Four milestones of unreleased work (M002 shared `_typsphinx/deps.typ` contract and `typst_dependencies`; M004 codly 2.0.0 upgrade with code-mode `codly.new(raw(...))` emission — a breaking change for custom templates; M005 Python 3.14 support and housekeeping) move from `## [Unreleased]` into a dated `## [0.10.0]` section with a lead paragraph that states the breaking changes and the template migration. The version, README status line, CHANGELOG link block and the release gate test move to 0.10.0, and the package builds and passes `twine check`. Three docs-audit items are fixed: the charged-ieee approach1 abstract is made to render like approach2 (fix-code), the stale "sphinx-typst" name is replaced, and the misplaced `## [0.1.0b1]` CHANGELOG section is moved below `## [0.2.0]`. The `v0.10.0` tag push that publishes to PyPI happens after the PR merge, on the owner's instruction.

## Problem

- `pyproject.toml:7` is `version = "0.9.8"` and `README.md:345` says "Stable (v0.9.8)", while `CHANGELOG.md` `## [Unreleased]` (lines 8–88) holds M002–M005 entries including the "Breaking: codly is upgraded from 1.3.0 to 2.0.0" entry (evidence-codebase.md).
- `tests/test_release_0_9_8_docs_gate.py` asserts the CHANGELOG link block targets `v0.9.8` (`test_link_block_targets_v0_9_8`), so it must move with the version.
- DOCS-AUDIT #1: examples/charged-ieee/README.md claims both approaches produce identical output, but the shipped PDFs differ in the abstract's line breaks (approach1 `conf.py:26` passes a multi-line triple-quoted `ieee_abstract`). #2: the README says "sphinx-typst" at lines 3, 7 and 150. #3: CHANGELOG.md's `## [0.1.0b1]` section (line ~1389) sits above `## [0.2.0]` (line ~1562), breaking newest-first order.

## Users

typsphinx users upgrading from 0.9.8 (especially those with custom templates that imported `codly`/`codly-init` from deps.typ); readers of the charged-ieee example; the maintainer cutting the release.

## Success criteria

1. Version and build: `pyproject.toml` version is `0.10.0`; README.md's status line names v0.10.0 (no remaining "v0.9.8" status claim); on the final HEAD, `uv build` followed by `uv run twine check dist/*` passes and the built wheel and sdist are named `typsphinx-0.10.0`.
2. CHANGELOG release section (surface: CHANGELOG.md release notes): `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.10.0] - <date of the release-prep commit>` sits directly above `## [0.9.8]`, opens with a lead paragraph that names the codly 2.0.0 breaking change, the shared `/_typsphinx/deps.typ` contract and the custom-template migration, and holds every entry that was under `## [Unreleased]` at 81af8d6b except the Planned list; the link block has `[Unreleased]` comparing `v0.10.0...HEAD` and `[0.10.0]` pointing at `releases/tag/v0.10.0`, with `[0.9.8]` kept. `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and prints a section containing `codly`, `2.0.0` and `deps.typ`.
3. CHANGELOG order: every `## [x.y.z…]` release heading in CHANGELOG.md appears in strictly descending version order (so `## [0.1.0b1]` is below `## [0.2.0]`), and the moved 0.1.0b1 section's text is unchanged.
4. charged-ieee identical output (surface: examples/charged-ieee PDFs): building approach1 and approach2 with `typstpdf` produces PDFs whose extracted abstract text, including its line breaks, is identical; the README's identical-output claim is kept.
5. charged-ieee README name (surface: examples/charged-ieee/README.md): the README contains no "sphinx-typst"; the three occurrences read "typsphinx".
6. Release gate follows the version: the release-gate test asserts the 0.10.0 link block (`[Unreleased]` → `v0.10.0...HEAD`, `[0.10.0]` → `releases/tag/v0.10.0`) and no test asserts the `[Unreleased]` link still compares from `v0.9.8`.
7. On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | none | dismissed | fixed version string and one build/check command |
| E2 | SC2 | boundary | criterion SC2 | the heading date is the commit date of the release-prep commit that writes it (same rule as 0.9.8's `test_0_9_8_date_is_release_prep_commit_date`) |
| E3 | SC3 | ordering | criterion SC3 | version order uses PEP 440 comparison, so the pre-release `0.1.0b1` sorts below `0.2.0` |
| E4 | SC4 | none | dismissed | one fixed abstract in two fixed example projects |
| E5 | SC5 | none | dismissed | static documentation text |
| E6 | SC6 | none | dismissed | fixed link-block strings |
| E7 | SC7 | none | dismissed | whole-repository command results on one HEAD |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | SC2 | omit or bury the breaking codly 2.0 / template migration change from the release notes users read before upgrading | criterion SC2 | SC2 requires the lead paragraph to name it and the extracted section to contain `codly`, `2.0.0`, `deps.typ` |
| N2 | SC1 | none | dismissed | release metadata, documentation or example output; no values, safety, privacy or fairness item applies |
| N3 | SC3 | none | dismissed | release metadata, documentation or example output; no values, safety, privacy or fairness item applies |
| N4 | SC4 | none | dismissed | release metadata, documentation or example output; no values, safety, privacy or fairness item applies |
| N5 | SC5 | none | dismissed | release metadata, documentation or example output; no values, safety, privacy or fairness item applies |
| N6 | SC6 | none | dismissed | release metadata, documentation or example output; no values, safety, privacy or fairness item applies |
| N7 | SC7 | none | dismissed | release metadata, documentation or example output; no values, safety, privacy or fairness item applies |

## Scope: in

- Version bump to 0.10.0 (`pyproject.toml`, README status line).
- CHANGELOG: move Unreleased entries into `## [0.10.0] - <date>` with a lead paragraph (Q1 a); link block; move `## [0.1.0b1]` below `## [0.2.0]` (Q3 a).
- Update the release gate test for 0.10.0.
- charged-ieee: make approach1's abstract render like approach2 (Q2 a, fix-code); replace "sphinx-typst" (Q3 a).

## Scope: out (vetoes)

- Pushing the `v0.10.0` tag or publishing to PyPI inside the milestone — done after the PR merge on the owner's instruction (Q4 a).
- Product code changes under `typsphinx/`.
- Test/CI speed work (corpus gate filter, xdist, shared docs builds).
- Rewriting released CHANGELOG sections other than moving `## [0.1.0b1]` unchanged.

## Constraints

- Python >= 3.12; black/ruff line 88; mypy clean (CLAUDE.md).
- Tests must stay OS-neutral (CI ubuntu/windows/macos × py312–py314).
- The tag-triggered `release.yml` publishes on `v*`; tag `v0.10.0` is pushed only after the PR is merged and only on the owner's instruction (Q4 a). PR checks and publication are observed after integration, not success criteria (LESSONS 001).
- Integration by pull request (STATE `integration: pull-request`).

## Current state (brownfield only)

- **What exists**: typsphinx 0.9.8 + Unreleased M002–M005 changes at 81af8d6b; full suite 1881 passed, 1 skipped; CI py312–py314 × ubuntu/windows/macos.
- **Must not break**: `scripts/extract_changelog_section.py` release-notes extraction; the tests that require `### Planned for Future Releases` under Unreleased; the `@preview` single-source and toolchain-pin gates.
- **Doc-vs-code rulings**: #1 charged-ieee identical output → fix-code; #2 "sphinx-typst" → fix-doc; #3 CHANGELOG 0.1.0b1 order → fix-doc.
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- Making approach1's abstract identical may require matching how approach2's template receives the abstract; other page-1 differences (author details) are out of SC4's scope.
- Other tests may pin `v0.9.8` strings tied to the current release (static grep found only historical "removed in v0.9.8" mentions, which stay).

## Open questions

- none

## Corrections

- C1 2026-11-03: "2"
- C2 2026-11-03: "Q1 a  Q2 a  Q3 a  Q4 a"
