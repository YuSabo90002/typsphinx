# Final Review — reused full wave

Reviewed HEAD: 4f94455d07883a9e2af6065795c48449fb3326b0
Overall verdict: pass
Source review: .project/review/wave-1.cycle1.md
Source commit: a045accf0738b1e2da089943fc4716a0fc0f3614

## Success criteria

### SC1 — Version and build: `pyproject.toml` version is `0.10.0`; README.md's status line names v0.10.0 (no remaining "v0.9.8" status claim); on the final HEAD, `uv build` followed by `uv run twine check dist/*` passes and the built wheel and sdist are named `typsphinx-0.10.0`.

- **Verdict**: met
- **Check**: `grep -n 'Status\*\*' README.md; grep -n 'v0\.9\.8' README.md`
- **Observed**: `345:**Status**: Stable (v0.10.0) - Production ready`; no v0.9.8 match (success state; the v0.9.8 error state is absent)
- **Reference**: .project/review/wave-1.cycle1.md — SC1; evidence: `pyproject.toml:7` 0.10.0. README status names v0.10.0, and no `v0.9.8` remains in README.md. At review HEAD a045accf, the reviewer's `uv build -o <mktemp>` built `typsphinx-0.10.0-py3-none-any.whl` and `typsphinx-0.10.0.tar.gz`, and `uv run twine check` gave `PASSED` for both. E1 and N2 are dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: README.md status line

### SC2 — CHANGELOG release section (surface: CHANGELOG.md release notes): `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.10.0] - <date of the release-prep commit>` sits directly above `## [0.9.8]`, opens with a lead paragraph that names the codly 2.0.0 breaking change, the shared `/_typsphinx/deps.typ` contract and the custom-template migration, and holds every entry that was under `## [Unreleased]` at 81af8d6b except the Planned list; the link block has `[Unreleased]` comparing `v0.10.0...HEAD` and `[0.10.0]` pointing at `releases/tag/v0.10.0`, with `[0.9.8]` kept. `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and prints a section containing `codly`, `2.0.0` and `deps.typ`.

- **Verdict**: met
- **Check**: `uv run python scripts/extract_changelog_section.py 0.10.0`, then open CHANGELOG.md at `## [Unreleased]` and the link block
- **Observed**: exit 0, 79 non-empty lines. The first paragraph is "0.10.0 contains breaking changes for custom templates. codly is upgraded from 1.3.0 to 2.0.0 (`@preview/codly:2.0.0`, …) … `<outdir>/_typsphinx/deps.typ` … must be migrated: see the "Migrating from codly 1.3" note …". `### Added` follows at output line 11 and `### Changed` at line 37. `## [Unreleased]` holds only `### Planned for Future Releases` with its three bullets. The link block has `[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.10.0...HEAD`, `[0.10.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.10.0` and `[0.9.8]: …/releases/tag/v0.9.8`.
- **Reference**: .project/review/wave-1.cycle1.md — SC2; evidence: The extracted section starts with the breaking-change lead and is followed by `### Added` and `### Changed`. Everything that was under the 81af8d6b `[Unreleased]`, except the Planned list, appears verbatim in the 0.10.0 section. The link block lines are present. E2 (held-out boundary): the heading date 2026-11-03 equals the commit date of b85cc016, the commit that introduced the heading (`git log -S`). N1 (judgment): the lead paragraph is the first text users read under 0.10.0. It names "codly is upgraded from 1.3.0 to 2.0.0", the `<outdir>/_typsphinx/deps.typ` public contract and the "Migrating from codly 1.3" note, so the breaking change is neither omitted nor buried. Non-blocking: the notes have no Python 3.14 entry, because none existed under Unreleased at 81af8d6b (see the T001 warning).
- **Finding**: none
- **Fix direction**: none
- **Surface**: CHANGELOG.md release notes (`scripts/extract_changelog_section.py 0.10.0` output)

### SC3 — CHANGELOG order: every `## [x.y.z…]` release heading in CHANGELOG.md appears in strictly descending version order (so `## [0.1.0b1]` is below `## [0.2.0]`), and the moved 0.1.0b1 section's text is unchanged.

- **Verdict**: met
- **Check**: none
- **Observed**: E3 (PEP 440 ordering): the reviewer compared consecutive headings with `packaging.version.Version`, and all 26 are strictly descending. The last four are `0.2.2`, `0.2.1`, `0.2.0`, `0.1.0b1`. The 0.1.0b1 block is byte-identical to its 81af8d6b text (6898 characters). N3 is dismissed.
- **Reference**: .project/review/wave-1.cycle1.md — SC3
- **Finding**: none
- **Fix direction**: none

### SC4 — charged-ieee identical output (surface: examples/charged-ieee PDFs): building approach1 and approach2 with `typstpdf` produces PDFs whose extracted abstract text, including its line breaks, is identical; the README's identical-output claim is kept.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run sphinx-build -E -q -b typstpdf -c examples/charged-ieee/<approach> examples/charged-ieee/<approach>/source <mktemp>/<approach>` for approach1 and approach2, then pypdf page-1 text from "Abstract" to "Index Terms" with CRLF folded
- **Observed**: both builds exit 0 and write paper.pdf. Both abstracts are `'Abstract—This paper presents novel approaches to machine \nlearning applications in computer vision. We demonstrate state-\nof-the-art results on benchmark datasets and provide compre -\nhensive analysis of our methodology.\n'`, and the comparison gives `identical: True` (success state). With the pre-fix conf.py, approach1 gave `…machine \nlearning\napplications…` and `identical: False` (the error state is reachable and was fixed).
- **Reference**: .project/review/wave-1.cycle1.md — SC4; evidence: The reviewer's fresh typstpdf builds of both approaches gave byte-equal abstract text, line breaks included. README.md:154 keeps the identical-output claim. The pre-fix conf.py reproduced the difference. E4 and N4 are dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: examples/charged-ieee PDFs and README

### SC5 — charged-ieee README name (surface: examples/charged-ieee/README.md): the README contains no "sphinx-typst"; the three occurrences read "typsphinx".

- **Verdict**: met
- **Check**: `grep -c 'sphinx-typst' examples/charged-ieee/README.md; grep -c typsphinx examples/charged-ieee/README.md`
- **Observed**: `0` and `3`. Lines 3, 7 and 150 read "with typsphinx.", "with typsphinx in two different ways." and "[typsphinx Documentation](…)".
- **Reference**: .project/review/wave-1.cycle1.md — SC5; evidence: README has 0 "sphinx-typst" matches. The diff changes exactly lines 3, 7 and 150 to "typsphinx". E5 and N5 are dismissed.
- **Finding**: none
- **Fix direction**: none
- **Surface**: examples/charged-ieee PDFs and README

### SC6 — Release gate follows the version: the release-gate test asserts the 0.10.0 link block (`[Unreleased]` → `v0.10.0...HEAD`, `[0.10.0]` → `releases/tag/v0.10.0`) and no test asserts the `[Unreleased]` link still compares from `v0.9.8`.

- **Verdict**: met
- **Check**: none
- **Observed**: The 0.10.0 link assertions are at tests/test_release_0_10_0_docs_gate.py:170-171. No `v0.9.8...HEAD` appears under tests/. The release gates pass at review HEAD in the reviewer's targeted run (below). E6 and N6 are dismissed.
- **Reference**: .project/review/wave-1.cycle1.md — SC6
- **Finding**: none
- **Fix direction**: none

### SC7 — On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

- **Verdict**: met
- **Check**: none
- **Observed**: T001's recorded isolated Verify ran on base+T001 and gave `1892 passed, 1 skipped`, with black, ruff and mypy clean and exit 0. T002 landed from the same base and changed only examples/charged-ieee/approach1/conf.py, examples/charged-ieee/README.md and its own gate test. Its recorded Verify gave `8 passed`, exit 0. The two tasks' file sets are disjoint. The cross-task risk is a test that reads the examples tree or the changelog. To cover it, the reviewer synced `--extra dev --extra docs` at the review HEAD in the sidecar and ran 16 test files under `LC_ALL=C`: both tasks' gates, the changelog extraction tests, every test file that references `examples/`, and test_template_engine, test_docs_contract_claims_gate and test_preview_version_sync. Result: `246 passed`. `black --check .` reported `399 files would be left unchanged.`, `ruff check .` reported `All checks passed!` and `mypy typsphinx/` reported `Success: no issues found in 10 source files`. The combined tree shows no breakage path. The whole-suite run on this HEAD is the project Verify at ship. E7 and N7 are dismissed.
- **Reference**: .project/review/wave-1.cycle1.md — SC7
- **Finding**: none
- **Fix direction**: none
