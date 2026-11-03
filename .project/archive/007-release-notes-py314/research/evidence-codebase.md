# Evidence — codebase

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-03 (Audited HEAD 6defa41d1bf9815083d5567c0dd9a4c7f7df4ca1, verify sidecar)
Checks run: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` → ok (uv-managed CPython 3.14.4); `uv run pytest -q tests/test_release_0_10_0_docs_gate.py tests/test_docs_contract_claims_gate.py tests/test_user_template_relative_asset_gate.py tests/test_changelog_extraction.py tests/test_changelog_page_gate.py` → 42 passed; scratch script (outside repo) formatting the advanced.rst `ieee_abstract` value through `TemplateEngine._format_typst_value` and compiling with typst-py → literal `"\nThis paper ... learning\napplications in computer vision.\n"`, PDF text `'A \nThis paper ... machine \nlearning\napplications in computer vision.\n Z'`. Full suite not run (scan kept proportionate to a two-item docs follow-up).

## Map

- **Stack**: Python >=3.12 (classifiers 3.12/3.13/3.14), Sphinx >=9.1,<10, docutils >=0.21,<0.23, typst (typst-py) >=0.15.0,<0.16; setuptools build; uv + uv.lock; tox (env_list py312, py313, py314, lint, type, cov, docs); black/ruff/mypy; pytest with sphinx.testing fixtures; pypdf + pillow dev-only (pyproject.toml:1-60, tox.ini:2).
- **Entry points**: `typsphinx.setup(app)`; `sphinx.builders` entry points `typst` and `typstpdf` → `typsphinx` (pyproject.toml "[project.entry-points]").
- **Architecture**: Sphinx builder → writer → translator layering in `typsphinx/` (builder.py, writer.py, translator.py, template_engine.py, typst_deps.py, pdf.py, plus template_registry.py, pathfmt.py, removed_config.py; 13,579 py lines). Translator emits Typst body; writer writes content files with the `/_typsphinx/deps.typ` preamble and wrapper files through TemplateEngine; typstpdf compiles masters via typst-py.
- **Conventions**: Python config values formatted to Typst literals by `TemplateEngine._format_typst_value` — `str` becomes a quoted Typst string with only `\` and `"` escaped, newlines kept verbatim (typsphinx/template_engine.py:784-787). Docs/CHANGELOG content is bound by text-asserting gate tests (`tests/test_*_gate.py`, 194 test modules). Commits: GSD Path subjects (`T00N: ...`, `build: ...`, `ship: M00N — <slug>`, PR merges).
- **Maturity**: Version 0.10.0 already set (pyproject.toml:7); CHANGELOG `## [0.10.0] - 2026-11-03` written by M006. Release-docs gates pass (42/42 in the selected set).
- **Recent activity**: 121 commits since 2026-10-01; last milestones M004 (codly 2 upgrade), M005 (housekeeping + Python 3.14, 5aee2fb9), M006 (release prep 0.10.0, b85cc016 / 3c23c646), merged as PR #192 (6defa41d).

## Finding: CHANGELOG 0.10.0 has no Python 3.14 entry although 3.14 support shipped

- **Claim**: No line in CHANGELOG.md mentions Python 3.14; 3.14 is declared in pyproject classifiers (pyproject.toml:23), black target-version (pyproject.toml:112), CI matrix (.github/workflows/ci.yml:18,24-25) and tox env_list (tox.ini:2), introduced by 5aee2fb9 (M005).
- **Source**: `grep -n "3\.14" CHANGELOG.md` → no hits (only older "Python 3.13"/"3.12" lines at 533, 1097, 1122); M006 wave review .project/archive/006-release-0-10-0/review/wave-1.cycle1.md:22,78 records the same gap as non-blocking.
- **Confidence**: high
- **Why it matters here**: This is follow-up item 1. The entry belongs inside `## [0.10.0]` (likely `### Added` or `### Changed`). Gates that constrain the edit: tests/test_release_0_10_0_docs_gate.py checks Unreleased holds only "Planned for Future Releases" (line 100), the lead paragraph fragments (143-147), eight former-Unreleased bullet fragments (150-163), link block (168), heading order (181) and the extract script (197). Adding a bullet does not break these as written, but the M006 SC "every entry that was under Unreleased at 81af8d6b" framing means a new SC should name the 3.14 line explicitly. The 0.10.0 heading date gate (tests/test_release_0_10_0_docs_gate.py:124-140) compares the heading date to the earliest commit whose diff adds/removes the heading string (`git log --reverse -S<heading>`), so a later bullet-only edit that leaves the heading line untouched keeps it passing; changing the heading date would break it.

## Finding: docs/source/examples/advanced.rst:25 multi-line ieee_abstract renders with hard line breaks and leading/trailing newlines

- **Claim**: The documented `ieee_abstract = """\nThis paper presents ... learning\napplications in computer vision.\n"""` is passed through `typst_template_function["params"]["abstract"]` (advanced.rst:51) as a Typst string that keeps its newlines; Typst renders each as a hard line break, so the abstract starts with a blank break, breaks mid-sentence after "learning", and ends with a break.
- **Source**: docs/source/examples/advanced.rst:25-28,51; typsphinx/template_engine.py:784-787; scratch compile in Checks run (PDF text `'A \nThis paper ... machine \nlearning\napplications in computer vision.\n Z'`).
- **Confidence**: high
- **Why it matters here**: Follow-up item 2. M006 T002 fixed the identical pattern in examples/charged-ieee/approach1/conf.py:26-35 by implicit string concatenation with an explanatory comment (commit 3c23c646); that is the in-repo precedent to copy. The same advanced.rst page also shows approach2-style `let ieee_abstract = [ ... ]` content block (advanced.rst:90-93), which collapses line breaks, so after the fix both snippets render one paragraph.

## Finding: advanced.rst is already bound by docs gates; no gate pins the ieee_abstract text

- **Claim**: advanced.rst is in `REVIEWED_CLAIM_PAGES` (tests/test_docs_contract_claims_gate.py:138) and tests/test_user_template_relative_asset_gate.py:53,223-227 asserts it names the bare-filename reference form; no test references `ieee_abstract` in advanced.rst (only tests/test_template_engine.py:932 uses a single-line value of its own).
- **Source**: `grep -rn ieee_abstract tests docs examples`; both gate files pass (42 passed run above).
- **Confidence**: high
- **Why it matters here**: Editing the code-block will not break existing gates, and nothing currently prevents the pattern from returning; a planner that wants a regression guard has to add one (e.g. a text check that the advanced.rst conf.py block has no triple-quoted abstract, or a render check like tests/test_examples_charged_ieee_gate.py's abstract comparison).

## Finding: examples/charged-ieee/README.md uses ieee_abstract without showing its definition

- **Claim**: The README's approach1 configuration example references `ieee_abstract` (examples/charged-ieee/README.md:48) but its code block does not define it, so it neither shows nor contradicts the fixed single-line form.
- **Source**: examples/charged-ieee/README.md:28-55
- **Confidence**: high
- **Why it matters here**: Only advanced.rst carries the stale triple-quoted pattern in docs/examples; a repo-wide sweep (per the "anywhere" lesson) finds no third occurrence (`grep -rn 'ieee_abstract = """'` matches only advanced.rst:25).

## Finding: v0.10.0 tag not yet pushed; release notes are extracted from CHANGELOG at tag time

- **Claim**: Version is 0.10.0 and the link block already targets `releases/tag/v0.10.0`; `scripts/extract_changelog_section.py 0.10.0` produces the release notes (tests/test_release_0_10_0_docs_gate.py:168-200).
- **Source**: pyproject.toml:7; tests/test_release_0_10_0_docs_gate.py; brief context (tag not pushed).
- **Confidence**: medium (tag state taken from the brief; release.yml not re-read)
- **Why it matters here**: Both follow-up edits change what users see at PyPI/GitHub release only if they land on main before the tag push; pushing the tag is outside observable SCs (Constraints, per prior lesson).

## Apparent intent

- Finish 0.10.0 release hygiene before tagging: complete the release notes (3.14) and remove the last copy of the abstract-rendering pitfall from the docs — based on M006 wave-1 review warnings (.project/archive/006-release-0-10-0/review/wave-1.cycle1.md:22,34,78) and the planned follow-up in the brief.

## Open questions for define

- Which subsection should carry the Python 3.14 line in `## [0.10.0]` (`### Added` vs `### Changed`), and should it also mention the CI/tox matrix?
- For advanced.rst: copy approach1's implicit-concatenation form verbatim (with its explanatory comment), or keep a triple-quoted string and show a cleanup (e.g. `" ".join(...split())`)? Should a regression gate be added?
- Is the docs PDF/HTML build (tox -e docs-*) required evidence for the advanced.rst change, or is a text-level gate sufficient?

## Blocked areas

- none (full test suite and docs builds intentionally not run; release.yml not inspected)
