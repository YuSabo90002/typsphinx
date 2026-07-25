---
phase: 27-docs-orphan-delete-phantom-config-names
verified: 2026-07-24T00:00:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 27: Docs 実測整合 — Orphan Delete + Phantom Config Names Verification Report

**Phase Goal:** Every documented `typst_*` name across the user-facing docs matches a registered config value; the unreachable orphan config doc is removed; and config is documented in ONE canonical place so it cannot re-drift.
**Verified:** 2026-07-24
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (mapped 1:1 to ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 (SC#1) | Orphan `docs/configuration.rst` + collateral test deleted; no live inbound `:doc:`/`:ref:` to the orphan remains | ✓ VERIFIED | `test -f docs/configuration.rst` → absent; `test -f tests/test_documentation_configuration.py` → absent. `grep -rn ':doc:\`configuration\`' docs/source/` → exactly the 3 expected relative refs (`user_guide/builders.rst:187`, `user_guide/index.rst:27`, `user_guide/templates.rst:360`), all of which resolve within `docs/source/user_guide/` to the surviving canonical doc, not the deleted orphan (Sphinx `:doc:` resolves relative to the referencing document's directory — there is no `docs/source/configuration.rst`, only `docs/source/user_guide/configuration.rst`). `uv run pytest tests/test_documentation_usage.py tests/test_documentation_installation.py -q` → 20 passed (siblings untouched, confirmed also absent from `git diff --stat` file list). |
| 2 (SC#2) | `user_guide/configuration.rst`: `typst_author`→`typst_authors`, codly knobs removed, papersize/fontsize rewritten as working `typst_elements` | ✓ VERIFIED | `grep -nE 'typst_use_codly\|typst_code_line_numbers\|typst_papersize\|typst_fontsize\|typst_author\b' docs/source/user_guide/configuration.rst` → zero matches (exit 1). Literal `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` present at 2 sites (lines 172, 222). `typst_use_mitex = True` still present (lines 139, 219). |
| 3 (SC#3) | `api/index.rst` list-table deleted, `See :doc:` pointer retained; `api/index.po` follows, no live phantom msgid | ✓ VERIFIED | `grep -n 'list-table' docs/source/api/index.rst` → zero matches. `grep -n ':doc:' docs/source/api/index.rst` → line 45, the `See :doc:\`/user_guide/configuration\`` pointer. `grep -E 'typst_papersize\|typst_fontsize\|typst_use_codly\|typst_code_line_numbers' docs/locale/ja/LC_MESSAGES/api/index.po \| grep -v '#~'` → zero live lines; 4 inert `#~`-commented obsolete entries confirmed present (correct Babel merge behavior, not a leak). |
| 4 (SC#4) | Every `typst_*` token anywhere under `docs/source/` is one of the 11 registered names | ✓ VERIFIED | `grep -rohE '\btypst_[a-z_]+\b' docs/source/ \| sort -u` → `typst_authors, typst_documents, typst_elements, typst_package, typst_template, typst_template_assets, typst_template_function, typst_use_mitex` — all 8 present names ⊆ the 11 registered (`typst_documents, typst_template, typst_template_mapping, typst_use_mitex, typst_elements, typst_package, typst_package_imports, typst_template_function, typst_authors, typst_debug, typst_template_assets` per `typsphinx/__init__.py:44-60`). `comm -23` diff (found − registered) is empty. This confirms the orchestrator's post-merge gap-closure commit `59bf66d` (removing `typst_use_codly`/`typst_code_line_numbers` from `docs/source/examples/advanced.rst` and `docs/source/examples/basic.rst`, which the plan's original DOC-07 scoping missed) is complete — no phantom survives anywhere under `docs/source/`, not just the two originally-scoped files. |
| 5 (SC#5) | Docs build green (no broken `:doc:`/`:ref:`); test suite green | ✓ VERIFIED | `sphinx-build -b html -q source <tmp>` (en) and `-D language=ja` (ja): only the 1 pre-existing `translator.py:visit_toctree` docstring-spacing ERROR+WARNING pair (baseline, unrelated to this phase — confirmed present on both locales, not newly introduced) — zero `nonexisting document` / `undefined label` / `unknown document` / reference-target warnings. Full `uv run pytest -q` → **604 passed, 1 skipped, 0 failed** in this environment (this exceeds the SUMMARY's claimed sandbox baseline of 45 environmental failures — those are known typst-compiled-binary NixOS-sandbox artifacts from the executor's isolated worktree, not reproduced here; either way, zero failures attributable to this phase). `pytest --collect-only -q \| grep -c test_documentation_configuration` → 0 (no longer collected). |
| 6 (Milestone invariant) | Zero `typsphinx/*.py` changes; no `@preview` bump; 3-way version-sync surface untouched | ✓ VERIFIED | `git diff --name-only 93f87f0 HEAD -- typsphinx/` → empty. `git diff --name-only 93f87f0 HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` → empty. Full changed-file list (`git diff --stat 93f87f0 HEAD`) contains only docs/tests/locale/planning files — 13 files, all within the plan's declared `files_modified` (plus the gap-closure commit's 2 examples files and the tracking commits). |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/configuration.rst` | deleted | ✓ VERIFIED | absent on disk, `git rm` staged in commit `90801cf` |
| `tests/test_documentation_configuration.py` | deleted | ✓ VERIFIED | absent on disk, same commit |
| `docs/source/user_guide/configuration.rst` | modified, phantom-free | ✓ VERIFIED | see Truth #2 |
| `docs/source/api/index.rst` | modified, list-table removed | ✓ VERIFIED | see Truth #3 |
| `docs/locale/ja/LC_MESSAGES/api/index.po` | regenerated | ✓ VERIFIED | diff present, scoped (see Key Links) |
| `docs/locale/ja/LC_MESSAGES/user_guide/configuration.po` | regenerated | ✓ VERIFIED | diff present, includes CJK-markup fix |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `api/index.rst` | `user_guide/configuration.rst` | `See :doc:\`/user_guide/configuration\`` pointer | ✓ WIRED | Line 45, confirmed present and is the sole surviving Configuration-section content besides heading/intro |
| `.po` regen scope | edited `.rst` files only | scoped `sphinx-build -b gettext` + `sphinx-intl update` | ✓ WIRED | `git diff --name-only 93f87f0 HEAD -- docs/locale/` → exactly 4 files (`api/index.{po,mo}`, `user_guide/configuration.{po,mo}`); no drift into `builders.po` / `examples/advanced.po` |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| DOC-06 | 27-01-PLAN.md | Orphan `docs/configuration.rst` deleted after confirming no unique useful content lost, no live reference remains | ✓ SATISFIED | Truth #1; salvage-nothing decision recorded in SUMMARY (superseded content + wrong package name `sphinxcontrib.typst` + phantom `mainfont`/`monofont` keys in the orphan's own example) |
| DOC-07 | 27-01-PLAN.md | Every documented `typst_*` name matches a registered value, both phantom-bearing surfaces | ✓ SATISFIED | Truths #2, #3, #4 |

No orphaned requirements — `.planning/REQUIREMENTS.md` traceability table maps exactly DOC-06 and DOC-07 to Phase 27, and both appear in the plan's `requirements:` frontmatter.

Note (non-blocking, process-only): `.planning/REQUIREMENTS.md` still shows `- [ ]` unchecked boxes and "Pending" in the traceability table for DOC-06/DOC-07, and `.planning/ROADMAP.md` line 180 still shows the Phase 27 summary line unchecked. This is the standing pattern observed for prior phases (24-26) — the checkbox flip is a post-verification tracking commit (`docs(phase-N): ...`), not part of the phase's code truth. Not a gap; expected to be closed by the next tracking step.

### Anti-Patterns Found

None. Scanned all phase-modified content (`docs/source/user_guide/configuration.rst`, `docs/source/api/index.rst`, `docs/source/examples/advanced.rst`, `docs/source/examples/basic.rst`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/"coming soon"/"not yet implemented" — zero matches in phase-authored lines. One incidental case-insensitive grep hit (`docs/source/examples/advanced.rst:322`, `pip install sphinx furo sphinx-autodoc-typehints`) is pre-existing, unrelated content, not part of this phase's diff (confirmed via `git diff 93f87f0 HEAD -- docs/source/examples/advanced.rst`).

### Prohibitions Check (from PLAN frontmatter, judgment-tier)

| # | Prohibition | Status | Evidence |
|---|-------------|--------|----------|
| 1 | No bulk-migration of the orphan's 489 lines back | ✓ resolved | `configuration.rst` diff is 38 lines changed (net removal), not a 489-line import; SUMMARY records explicit salvage-nothing decision |
| 2 | No `typst_authors = (tuple)` rewrite | ✓ resolved | `typst_author\b` grep-zero; dict `typst_authors` is the sole surviving author example |
| 3 | No top-level `typst_papersize`/`typst_fontsize` introduced | ✓ resolved | grep-zero across both edited files and all of `docs/source/` |
| 4 | Sibling `test_documentation_usage.py`/`test_documentation_installation.py` untouched | ✓ resolved | absent from `git diff --stat` file list; both pass (20/20) |
| 5 | No bare unscoped `sphinx-build -b gettext` | ✓ resolved | `docs/locale/` diff is scoped to exactly the 2 target catalogs |
| 6 | No hand-deletion of `#~` obsolete msgids | ✓ resolved | 4 inert `#~` phantom-name entries present in `api/index.po`, consistent with normal Babel merge, not hand-stripped |
| 7 | Milestone invariant (zero new deps, no `@preview` bump, 3-way surface untouched) | ✓ resolved | see Truth #6 |

### Human Verification Required

None. All must-haves are grep/build/test-verifiable; no visual, real-time, or external-service behavior involved (docs-content phase).

### Gaps Summary

No gaps. All 5 ROADMAP success criteria plus the milestone invariant are verified against the live `HEAD` of the milestone branch (`gsd/v0.6.3-config-docs-captioned-tables`), not merely SUMMARY.md claims. The orchestrator's post-merge gap-closure commit (`59bf66d`, extending SC#4's "anywhere under docs/source/" clause to `examples/advanced.rst` + `examples/basic.rst`, which the original plan scoping missed) is confirmed complete via direct `docs/source/`-wide grep cross-check — zero unregistered `typst_*` survivors anywhere in the built documentation tree.

---

_Verified: 2026-07-24_
_Verifier: Claude (gsd-verifier)_
