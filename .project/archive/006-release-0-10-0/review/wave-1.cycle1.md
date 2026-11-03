# Review — wave 1, cycle 1

Reviewed HEAD: a045accf0738b1e2da089943fc4716a0fc0f3614
Review scope: final

Wave verdict: pass
Cycle: 1
Depth: full
Tasks reviewed: 2

Inspection mode: immutable patch, judged in the verify sidecar checked out at review HEAD a045accf0738b1e2da089943fc4716a0fc0f3614. Identity proof: T002 landing 3c23c646953f4dc64113587d465aafa129b18907 has parent d3e33bccfb008560106232d050e7324140df9e13 (= recorded base). T001 landing b85cc016d53f3ff9b868ad10d53e8762a22e0e79 has parent 3c23c646 (T002 landed first), but every T001-declared file has the same blob at d3e33bcc and at 3c23c646 (pyproject.toml deb22b8a, uv.lock 88287cb3, README.md f67a199a, CHANGELOG.md 416b58f9, tests/test_release_0_9_8_docs_gate.py a3b37e08, tests/test_deps_contract_docs_gate.py 4277bc75), so the T001 patch produces the same blobs on the recorded base. Every product file of both tasks has the same blob at its landing commit and at the review HEAD. Commit range d3e33bcc..a045accf contains only the two landings plus the `.project/build/verify-ledger.jsonl` ledger commit.

## T001 — Prepare release 0.10.0 — version, README status, dated CHANGELOG section with breaking-change lead, newest-first order, and gate tests that follow the version: pass

- ✅ T001/AC1 — `pyproject.toml:7` `version = "0.10.0"`; the uv.lock diff in b85cc016 is one line, the typsphinx project entry `0.9.8` to `0.10.0` (uv.lock:1602); `revision = 5` is still in the uv.lock header; `uv lock --check` run by the reviewer at review HEAD: `Resolved 95 packages`, exit 0. `README.md:345` `**Status**: Stable (v0.10.0) - Production ready`; no `v0.9.8` remains in README.md. Recorded orchestrator Verify (T001 Log, `verify.json` exit_code 0): built `typsphinx-0.10.0.tar.gz` and `typsphinx-0.10.0-py3-none-any.whl`, twine check `PASSED` for both. The reviewer also ran `uv build` and `twine check` at review HEAD: both 0.10.0 artifacts were built and both `PASSED`.
- ✅ T001/AC2 — CHANGELOG.md:8-13 `## [Unreleased]` holds only `### Planned for Future Releases` and its three bullets. CHANGELOG.md:15 `## [0.10.0] - 2026-11-03` is the release heading directly above `## [0.9.8]`. Its lead paragraph (lines 17-25) names codly 1.3.0 to 2.0.0, `<outdir>/_typsphinx/deps.typ` and the custom-template migration. The heading date equals the landing commit date: `git log -S'## [0.10.0] - 2026-11-03'` returns b85cc016 with commit date 2026-11-03 (E2). The 81af8d6b `[Unreleased]` body, without the Planned list, is a verbatim substring of the new 0.10.0 section. The link block has `[Unreleased]: …/compare/v0.10.0...HEAD`, `[0.10.0]: …/releases/tag/v0.10.0` and `[0.9.8]` kept. `scripts/extract_changelog_section.py 0.10.0` exits 0, and its output contains `codly`, `2.0.0` and `deps.typ`.
- ✅ T001/AC3 — reviewer check with `packaging.version`: there are 26 release headings, `0.10.0` through `0.1.0b1`, and they are in strictly descending order (E3). `## [0.1.0b1]` is now last, below `## [0.2.0]`. Its 6898-character block at 81af8d6b is byte-identical to the moved block, which the link block follows.
- ✅ T001/AC4 — tests/test_release_0_10_0_docs_gate.py:170-171 asserts the `[Unreleased]` `v0.10.0...HEAD` line and the `[0.10.0]` `releases/tag/v0.10.0` line. `grep -rnE 'v0[.]9[.]8[.]{3}HEAD' tests/` finds nothing. `test_link_block_targets_v0_9_8` became `test_link_block_keeps_v0_9_8_tag_link`, which asserts only the `[0.9.8]` tag link.
- ✅ T001/AC5 — recorded orchestrator Verify on the base+T001 isolate: `1892 passed, 1 skipped in 213.20s`, `All checks passed!` (ruff), `399 files would be left unchanged.` (black), `Success: no issues found in 10 source files` (mypy), exit 0.

Warnings (non-blocking):
- The 0.10.0 notes have no Python 3.14 support entry. The INTENT Summary assumed M005 entries existed, but the `[Unreleased]` section at 81af8d6b holds no `3.14` text, and no `3.14` appears anywhere in CHANGELOG.md. M005 (5aee2fb9) declared Python 3.14 in classifiers and CI, yet the release notes users read do not mention it. SC2 is still met as written ("every entry that was under Unreleased at 81af8d6b"). The owner may want a Python 3.14 line added before tagging.
- In the T001 isolate a fallback uv rewrote uv.lock `revision = 5` to 3, and the coder restored it by hand. The landed lock diff is the version line only, and `uv lock --check` passes at review HEAD, so nothing is affected.

Contract violations (blocking):
- none. Changed paths are exactly the task `files` plus its task file. The task-file diff changes only `status`, `agent` and `base` and appends Log entries.

## T002 — Make charged-ieee approach1 render the same abstract as approach2 and replace the stale sphinx-typst name in its README: pass

- ✅ T002/AC1 — examples/charged-ieee/approach1/conf.py:30-35 makes `ieee_abstract` one logical line through implicit concatenation, with the same words. Reviewer typstpdf builds of both approaches (walkthrough under SC4) give identical page-1 abstracts, line breaks included. The test `TestChargedIeeeExamplesGate::test_both_approaches_render_identical_abstract` was added at tests/test_examples_charged_ieee_gate.py:343. Recorded orchestrator Verify: `8 passed in 3.93s`, exit 0. The reviewer reproduced the pre-fix failure: the 3c23c646^ conf.py rendered `machine \nlearning\napplications…`, which is not identical to approach2. README.md:154 keeps "Both approaches produce identical output".
- ✅ T002/AC2 — `grep -c sphinx-typst examples/charged-ieee/README.md` = 0. The diff replaces the three occurrences at lines 3, 7 and 150 with "typsphinx". `test_readme_names_typsphinx_not_sphinx_typst` is covered by the recorded `8 passed`.

Warnings (non-blocking):
- docs/source/examples/advanced.rst:25 still shows the triple-quoted `ieee_abstract` pattern. The coder noted it, and it is outside this task's files and outside SC4.

Contract violations (blocking):
- none. Changed paths are exactly the task `files` plus its task file, and the task file changed only orchestrator-owned fields and appended Log entries.

## Intent coverage

### SC1 — Version and build: `pyproject.toml` version is `0.10.0`; README.md's status line names v0.10.0 (no remaining "v0.9.8" status claim); on the final HEAD, `uv build` followed by `uv run twine check dist/*` passes and the built wheel and sdist are named `typsphinx-0.10.0`.: pass
- ✅ `pyproject.toml:7` 0.10.0. README status names v0.10.0, and no `v0.9.8` remains in README.md. At review HEAD a045accf, the reviewer's `uv build -o <mktemp>` built `typsphinx-0.10.0-py3-none-any.whl` and `typsphinx-0.10.0.tar.gz`, and `uv run twine check` gave `PASSED` for both. E1 and N2 are dismissed.
- **Surface**: README.md status line
- **Check**: `grep -n 'Status\*\*' README.md; grep -n 'v0\.9\.8' README.md`
- **Observed**: `345:**Status**: Stable (v0.10.0) - Production ready`; no v0.9.8 match (success state; the v0.9.8 error state is absent)

### SC2 — CHANGELOG release section (surface: CHANGELOG.md release notes): `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.10.0] - <date of the release-prep commit>` sits directly above `## [0.9.8]`, opens with a lead paragraph that names the codly 2.0.0 breaking change, the shared `/_typsphinx/deps.typ` contract and the custom-template migration, and holds every entry that was under `## [Unreleased]` at 81af8d6b except the Planned list; the link block has `[Unreleased]` comparing `v0.10.0...HEAD` and `[0.10.0]` pointing at `releases/tag/v0.10.0`, with `[0.9.8]` kept. `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and prints a section containing `codly`, `2.0.0` and `deps.typ`.: pass
- ✅ The extracted section starts with the breaking-change lead and is followed by `### Added` and `### Changed`. Everything that was under the 81af8d6b `[Unreleased]`, except the Planned list, appears verbatim in the 0.10.0 section. The link block lines are present. E2 (held-out boundary): the heading date 2026-11-03 equals the commit date of b85cc016, the commit that introduced the heading (`git log -S`). N1 (judgment): the lead paragraph is the first text users read under 0.10.0. It names "codly is upgraded from 1.3.0 to 2.0.0", the `<outdir>/_typsphinx/deps.typ` public contract and the "Migrating from codly 1.3" note, so the breaking change is neither omitted nor buried. Non-blocking: the notes have no Python 3.14 entry, because none existed under Unreleased at 81af8d6b (see the T001 warning).
- **Surface**: CHANGELOG.md release notes (`scripts/extract_changelog_section.py 0.10.0` output)
- **Check**: `uv run python scripts/extract_changelog_section.py 0.10.0`, then open CHANGELOG.md at `## [Unreleased]` and the link block
- **Observed**: exit 0, 79 non-empty lines. The first paragraph is "0.10.0 contains breaking changes for custom templates. codly is upgraded from 1.3.0 to 2.0.0 (`@preview/codly:2.0.0`, …) … `<outdir>/_typsphinx/deps.typ` … must be migrated: see the "Migrating from codly 1.3" note …". `### Added` follows at output line 11 and `### Changed` at line 37. `## [Unreleased]` holds only `### Planned for Future Releases` with its three bullets. The link block has `[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.10.0...HEAD`, `[0.10.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.10.0` and `[0.9.8]: …/releases/tag/v0.9.8`.

### SC3 — CHANGELOG order: every `## [x.y.z…]` release heading in CHANGELOG.md appears in strictly descending version order (so `## [0.1.0b1]` is below `## [0.2.0]`), and the moved 0.1.0b1 section's text is unchanged.: pass
- ✅ E3 (PEP 440 ordering): the reviewer compared consecutive headings with `packaging.version.Version`, and all 26 are strictly descending. The last four are `0.2.2`, `0.2.1`, `0.2.0`, `0.1.0b1`. The 0.1.0b1 block is byte-identical to its 81af8d6b text (6898 characters). N3 is dismissed.

### SC4 — charged-ieee identical output (surface: examples/charged-ieee PDFs): building approach1 and approach2 with `typstpdf` produces PDFs whose extracted abstract text, including its line breaks, is identical; the README's identical-output claim is kept.: pass
- ✅ The reviewer's fresh typstpdf builds of both approaches gave byte-equal abstract text, line breaks included. README.md:154 keeps the identical-output claim. The pre-fix conf.py reproduced the difference. E4 and N4 are dismissed.
- **Surface**: examples/charged-ieee PDFs and README
- **Check**: `LC_ALL=C uv run sphinx-build -E -q -b typstpdf -c examples/charged-ieee/<approach> examples/charged-ieee/<approach>/source <mktemp>/<approach>` for approach1 and approach2, then pypdf page-1 text from "Abstract" to "Index Terms" with CRLF folded
- **Observed**: both builds exit 0 and write paper.pdf. Both abstracts are `'Abstract—This paper presents novel approaches to machine \nlearning applications in computer vision. We demonstrate state-\nof-the-art results on benchmark datasets and provide compre -\nhensive analysis of our methodology.\n'`, and the comparison gives `identical: True` (success state). With the pre-fix conf.py, approach1 gave `…machine \nlearning\napplications…` and `identical: False` (the error state is reachable and was fixed).

### SC5 — charged-ieee README name (surface: examples/charged-ieee/README.md): the README contains no "sphinx-typst"; the three occurrences read "typsphinx".: pass
- ✅ README has 0 "sphinx-typst" matches. The diff changes exactly lines 3, 7 and 150 to "typsphinx". E5 and N5 are dismissed.
- **Surface**: examples/charged-ieee PDFs and README
- **Check**: `grep -c 'sphinx-typst' examples/charged-ieee/README.md; grep -c typsphinx examples/charged-ieee/README.md`
- **Observed**: `0` and `3`. Lines 3, 7 and 150 read "with typsphinx.", "with typsphinx in two different ways." and "[typsphinx Documentation](…)".

### SC6 — Release gate follows the version: the release-gate test asserts the 0.10.0 link block (`[Unreleased]` → `v0.10.0...HEAD`, `[0.10.0]` → `releases/tag/v0.10.0`) and no test asserts the `[Unreleased]` link still compares from `v0.9.8`.: pass
- ✅ The 0.10.0 link assertions are at tests/test_release_0_10_0_docs_gate.py:170-171. No `v0.9.8...HEAD` appears under tests/. The release gates pass at review HEAD in the reviewer's targeted run (below). E6 and N6 are dismissed.

### SC7 — On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.: pass
- ✅ T001's recorded isolated Verify ran on base+T001 and gave `1892 passed, 1 skipped`, with black, ruff and mypy clean and exit 0. T002 landed from the same base and changed only examples/charged-ieee/approach1/conf.py, examples/charged-ieee/README.md and its own gate test. Its recorded Verify gave `8 passed`, exit 0. The two tasks' file sets are disjoint. The cross-task risk is a test that reads the examples tree or the changelog. To cover it, the reviewer synced `--extra dev --extra docs` at the review HEAD in the sidecar and ran 16 test files under `LC_ALL=C`: both tasks' gates, the changelog extraction tests, every test file that references `examples/`, and test_template_engine, test_docs_contract_claims_gate and test_preview_version_sync. Result: `246 passed`. `black --check .` reported `399 files would be left unchanged.`, `ruff check .` reported `All checks passed!` and `mypy typsphinx/` reported `Success: no issues found in 10 source files`. The combined tree shows no breakage path. The whole-suite run on this HEAD is the project Verify at ship. E7 and N7 are dismissed.

## Summary for orchestrator

- blocked findings: none
- repeat offenders: none
- warnings worth a human eye: (1) the 0.10.0 release notes have no Python 3.14 support entry. M005 shipped it, but no CHANGELOG entry ever recorded it, so SC2 is still met as written. The owner may want a line added before tagging v0.10.0. (2) docs/source/examples/advanced.rst:25 still shows the triple-quoted `ieee_abstract` pattern, which is outside scope.
