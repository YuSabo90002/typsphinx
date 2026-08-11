---
phase: 45-documentation-currency-carried-hygiene
verified: 2026-08-10T08:50:00Z
status: passed
score: 5/5 must-haves verified (ROADMAP SC#1-SC#5)
behavior_unverified: 0
overrides_applied: 0
---

# Phase 45: Documentation Currency + Carried Hygiene Verification Report

**Phase Goal:** The README explains `typst_documents` and its new default, the published changelog
page stops being two years stale, and the two remaining code/planning hygiene todos close.
**Verified:** 2026-08-10T08:50:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, independently re-measured)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| 1 | SC#1 — README Quick Start states all five `typst_documents` facts, checked against a real build | ✓ VERIFIED | `README.md:80-101` states what the setting does, that it's optional, the `<project>.typ` stem derivation, explicit-wins precedence, and which documents become PDFs. `grep -c 'required for PDF output' README.md` = 0. Ran `.venv/bin/python -m pytest tests/test_quickstart_docs_gate.py::TestQuickstartFirstPdfGate -v` live: 2/2 passed — real `-b typstpdf` build of a fixture mirroring the published Quick Start emits `myproject.typ`/`myproject.pdf`, no `index.pdf`. `docs/source/quickstart.rst:74` names `build/pdf/myproject.pdf`. |
| 2 | SC#2 — changelog page carries all 12 releases (0.4.4-0.7.0), no stale marker, both builders clean | ✓ VERIFIED | Ran real builds myself: `sphinx-build -b html` and `-b typstpdf` against `docs/source` both exit 0, single pre-existing unrelated `visit_toctree` docstring WARNING (matches recorded baseline of 1/1), zero `changelog`-mentioning WARNING lines. `changelog.html` contains all 12 version strings, exactly one `<hN>Changelog</hN>` heading, no `(Current)` marker. `docs/source/changelog.rst` uses `.. include:: ../../CHANGELOG.md` unclipped (D-06 deviation, documented). `CHANGELOG.md` has `## [0.4.4]` between `0.5.0`/`0.4.3`, exactly one `## [Unreleased]`, zero `✅` chars. |
| 3 | SC#3 — `derive_typst_lang()` emits its rejection warning from exactly one site, byte-identical output | ✓ VERIFIED | Structural scan (docstrings/comments stripped, run by me): `logger.warning(` count = 1 inside the function body (`typsphinx/template_engine.py:141`). `.venv/bin/python -m pytest tests/test_template_engine.py::TestDeriveTypstLang tests/test_typst_lang_gate.py -v` — 39/39 passed. |
| 4 | SC#4 — `.planning/PROJECT.md` has zero unterminated `<!--` | ✓ VERIFIED | Independently re-ran the fence/backtick-aware opener-stack scan (script reproduced from the evidence file, run fresh by me): 34 openers, 34 closers, residual stack `[]`. Matches `45-GATE-EVIDENCE-04-qua03-comment-scan.md`. D-08 closing commit `43a2a78` confirmed to exist and to say what the evidence claims (`git show 43a2a78` reproduced independently). |
| 5 | SC#5 — full suite + lint/type trio green, `typsphinx/` change confined to QUA-02's refactor | ✓ VERIFIED | `.venv/bin/python -m pytest` (full suite, no `-m` filter): **952 passed, 1 skipped** (the expected `TYPSPHINX_CORPUS_REPORT`-gated skip). `black --check .` clean (243 files unchanged). `ruff check .` clean (via `nix-shell -p ruff`, working around the NixOS-incompatible venv shim exactly as the SUMMARYs document). `mypy typsphinx/` clean (6 source files, no issues). `git diff --name-only 8c74b853f81eaac0c9233a9628928528d16f2d18 HEAD -- typsphinx/` → exactly `typsphinx/template_engine.py`, single hunk confined to `derive_typst_lang()`. |

**Backstop truths (edge-probe `verification: backstop`, honest-verifier protocol applied):**

- DOC-12 (plan 45-01): "a missing `CHANGELOG.md` fails loudly rather than rendering an empty page." Independently reproduced by me: moved `CHANGELOG.md` aside, ran `-b html`, got `docs/source/changelog.rst:1: CRITICAL: Problems with "include" directive path: InputError: ... No such file or directory: 'CHANGELOG.md'`, restored the file, `git status --porcelain -- CHANGELOG.md` clean. **✓ VERIFIED by direct observation.**
- DOC-11 (plan 45-03): "with `typst_documents` unset and `project` left at Sphinx's own default sentinel, the typstpdf build still emits exactly one master target named from that default." The plan's own `<flagged_assumptions>` explicitly states no dedicated fixture covers this and that it "abstains to human_needed" absent confirming evidence. I built a throwaway fixture (`conf.py` with only `extensions = ["typsphinx"]`, no `project` line) and ran `-b typstpdf` live: build succeeded, emitted `projectnamenotset.typ`/`projectnamenotset.pdf` (derived from Sphinx's `project` default), no `index.pdf`/`index.typ`. **✓ VERIFIED by direct observation** (honest-verifier.md: "a behavior the verifier directly observed" satisfies the backstop evidence bar) — upgraded from the plan's own anticipated `human_needed` disposition.

**Score:** 5/5 ROADMAP success criteria verified; both backstop truths independently confirmed. 0 present-but-behavior-unverified truths.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `pyproject.toml` | `myst-parser>=5.0` in `docs` extra only | ✓ VERIFIED | Confirmed; `[project].dependencies` unchanged (3 entries) |
| `docs/source/conf.py` | `myst_parser` in `extensions` | ✓ VERIFIED | Present |
| `docs/source/changelog.rst` | delegates to `CHANGELOG.md` | ✓ VERIFIED | `.. include:: ../../CHANGELOG.md` + `:parser: myst_parser.sphinx_`, corrected Migration Guides / Release Process |
| `CHANGELOG.md` | 0.4.4 backfilled, single Unreleased, no emoji | ✓ VERIFIED | All three structural checks pass |
| `README.md` | Quick Start `typst_documents` section | ✓ VERIFIED | All 5 SC#1 statements present |
| `docs/source/quickstart.rst` | corrected output path | ✓ VERIFIED | `build/pdf/myproject.pdf`, no stale `index.pdf` reference |
| `docs/source/user_guide/configuration.rst` | derived-default paragraph | ✓ VERIFIED | Present ahead of the code block; items 3/4 untouched (diff-confirmed) |
| `typsphinx/template_engine.py` | single-site warning refactor | ✓ VERIFIED | 1 call site, byte-identical message |
| `tests/test_changelog_page_gate.py`, `tests/test_quickstart_docs_gate.py` + fixtures | regression gates | ✓ VERIFIED | 11 tests, all pass live |
| `45-GATE-EVIDENCE-01/02/04-*.md` | evidence records | ✓ VERIFIED | All present, contents independently spot-checked and reproduced |
| `docs/source/user_guide/templates.rst` | untouched (Phase 45.1 scope) | ✓ VERIFIED | `git diff <baseline> HEAD -- docs/source/user_guide/templates.rst` empty |

### Key Link Verification

| From | To | Via | Status |
|---|---|---|---|
| `docs/source/changelog.rst` include | repo-root `CHANGELOG.md` | `.. include::` + myst-parser | ✓ WIRED — confirmed by real build content coverage |
| `docs/source/conf.py` extensions | `myst_parser` registration | Sphinx extension load | ✓ WIRED — build succeeds, no import errors |
| `typsphinx/builder.py _default_typst_documents()` | README/quickstart/configuration.rst prose | `make_filename_from_project` derivation | ✓ WIRED — real build emits documented filename |
| `derive_typst_lang()` single warning | `tests/test_template_engine.py` caplog assertion | one call site, byte-identical text | ✓ WIRED — confirmed structurally and behaviorally |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| HTML build clean, all releases present | `sphinx-build -b html docs/source <tmp>` + content scan | exit 0, 12/12 versions present, 1 Changelog heading, 0 changelog warnings | ✓ PASS |
| PDF build succeeds | `sphinx-build -b typstpdf docs/source <tmp>` | exit 0, valid 110-page PDF (`%PDF-1.7`) | ✓ PASS |
| Quick Start fixture build | `pytest tests/test_quickstart_docs_gate.py::TestQuickstartFirstPdfGate -v` | 2/2 passed, `myproject.typ`/`.pdf` emitted, no `index.*` | ✓ PASS |
| `derive_typst_lang` single site + regression | `pytest tests/test_template_engine.py::TestDeriveTypstLang tests/test_typst_lang_gate.py -v` | 39/39 passed | ✓ PASS |
| Full suite | `pytest` (no filter) | 952 passed, 1 skipped (expected) | ✓ PASS |
| Lint/type | `black --check .`, `ruff check .` (via nix-shell), `mypy typsphinx/` | all clean | ✓ PASS |
| PROJECT.md comment balance | independent opener-stack scan | 34/34/0 residual | ✓ PASS |
| Missing-CHANGELOG.md backstop | manual move-aside + `-b html` | `CRITICAL` docutils error, file restored clean | ✓ PASS |
| Unset-`project` sentinel backstop | manual fixture + `-b typstpdf` | exit 0, `projectnamenotset.{typ,pdf}` emitted, no `index.*` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| DOC-11 | 45-03 | README states `typst_documents` behavior, checked against a real build | ✓ SATISFIED | `README.md`, `quickstart.rst`, `configuration.rst` verified directly; `tests/test_quickstart_docs_gate.py` green. **REQUIREMENTS.md checkbox already marked `[x]` Complete** (commit `3bc6459`). |
| DOC-12 | 45-01, 45-02 | Changelog page carries every release, builds clean | ✓ SATISFIED | Verified via independent real builds and content scan. **REQUIREMENTS.md checkbox already marked `[x]` Complete** (commit `a92845f`). |
| QUA-02 | 45-04 | `derive_typst_lang()` single-site warning, byte-identical | ✓ SATISFIED | Verified structurally and via 39/39 passing tests. **REQUIREMENTS.md checkbox still `[ ]`, traceability table still says "Pending"** — the implementation and tests are done and verified, but the bookkeeping mark-complete step that DOC-11/DOC-12 each received (visible as a distinct commit per plan: `3bc6459`, `a92845f`) was not performed for plan 45-04. Not a functional gap — flagged as a follow-up housekeeping item (see Gaps Summary). |
| QUA-03 | 45-04 | `.planning/PROJECT.md` zero unterminated comments, verification-only | ✓ SATISFIED | Verified via independent re-run of the scan (34/34/0). Same REQUIREMENTS.md tracking gap as QUA-02 above. |

No orphaned requirements — `DOC-11`, `DOC-12`, `QUA-02`, `QUA-03` are exactly the four IDs the ROADMAP maps to Phase 45, and all four are claimed across the four plans' `requirements:` frontmatter.

### Anti-Patterns Found

None in phase-modified files (`README.md`, `docs/source/changelog.rst`, `docs/source/quickstart.rst`, `docs/source/user_guide/configuration.rst`, `docs/source/conf.py`, `pyproject.toml`, `typsphinx/template_engine.py`, `tests/test_changelog_page_gate.py`, `tests/test_quickstart_docs_gate.py`) — no `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers introduced. `CHANGELOG.md` contains historical prose mentioning "not yet implemented" / a `TODO-01` label, but these are pre-existing release-notes content describing past project state, not new debt markers from this phase.

**Code review findings (0 critical, 3 warning — `45-REVIEW.md`), assessed against phase goal:**

| ID | Finding | Assessed impact on SC# | Disposition |
|---|---|---|---|
| WR-01 | "Migrating from 0.2.x to 0.3.x" section says "No breaking changes" while `CHANGELOG.md`'s own `## [0.3.0]` entry (now rendered on the same page via the new delegation) describes a breaking package rename | Does not fail SC#2 literally (SC#2 requires release coverage 0.4.4-0.7.0 + no stale marker + clean build — all met) but does undercut the phase's stated goal ("what the project tells a reader matches what it now does"). Plan 45-02 explicitly scoped the 0.2.x/0.1.x subsections out ("historical record, not staleness"), so this is a pre-existing defect the phase's own delegation mechanism newly exposes rather than a regression it introduced. | WARNING — not blocking, recommend a follow-up fix before/at milestone close |
| WR-02 | `CHANGELOG.md`'s `[0.2.0]` section is out of reverse-chronological file order | Explicitly prohibited from being touched by plan 45-02 ("not reordered; file-order changes DO matter to the extractor's positional slicing") | WARNING — pre-existing, explicitly out of scope, correctly left alone |
| WR-03 | A test comment in `tests/test_changelog_page_gate.py` misstates its own version range (says "0.4.4 through 0.7.0", tuple starts at 0.4.1) | Comment-only; test behavior/assertions unaffected | WARNING — cosmetic, no functional impact |

None of these three findings are must-haves or ROADMAP SC's; all were surfaced and correctly triaged by the phase's own code review as Warning, not Critical.

### Human Verification Required

None. Both `verification: backstop` truths were independently confirmed by direct observation during this verification pass (see above), so no item is routed to human_needed.

### Gaps Summary

No blocking gaps. All 5 ROADMAP success criteria are independently re-verified against the live codebase (not inferred from SUMMARY claims), both backstop truths are directly observed, the full test suite (952 passed / 1 expected skip) and lint/type trio are green, and the `typsphinx/` change is confirmed confined to the single QUA-02 refactor.

**One non-blocking housekeeping item, surfaced for the phase-completion step:** `.planning/REQUIREMENTS.md`'s checkboxes and traceability table mark `DOC-11`/`DOC-12` as `[x]` Complete (each via its own dedicated commit — `3bc6459`, `a92845f`) but still mark `QUA-02`/`QUA-03` as `[ ]` / "Pending" even though plan 45-04 fully implemented and this verification independently confirmed both. This is a tracking-document sync gap, not evidence the underlying work is incomplete — the code, tests, and gate evidence all check out. Recommend updating `.planning/REQUIREMENTS.md` (checkbox + traceability table for QUA-02/QUA-03) as part of closing this phase, before `/gsd-complete-milestone`.

---

_Verified: 2026-08-10T08:50:00Z_
_Verifier: Claude (gsd-verifier)_
