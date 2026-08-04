---
phase: 44-typst-documents-default-derivation-builder-input-hardening
verified: 2026-08-04T07:00:00Z
status: gaps_found
score: 5/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "A user who follows the Quick Start exactly gets a PDF, without a reachable configuration-free path to silent content loss or a hard build failure (ROADMAP Phase 44 goal statement; CR-01, 44-REVIEW.md)."
    status: failed
    reason: >
      Neither `_default_typst_documents` (typsphinx/builder.py:28-47) nor
      `_resolve_output_stem` (typsphinx/builder.py:156-261), the single normalization
      site every derived AND explicit `typst_documents` target name flows through,
      checks a resolved output stem for collision against another real docname in
      `self.env.found_docs`, or against the reserved `_template.typ` basename that
      `_write_template_file()` unconditionally writes at outdir root before any
      document is written. Before this phase, triggering the collision required an
      explicit, deliberately-crafted `typst_documents` entry. After this phase it is
      reachable with ZERO configuration: an ordinary `project` name whose
      `make_filename_from_project` slug happens to equal an existing docname (e.g.
      `project = "Chapter 1"` alongside a toctree-included `chapter1.rst` -- a
      thoroughly ordinary docs layout, a project named after its first chapter) makes
      the derived master's `-b typst` write silently overwrite `chapter1.rst`'s own
      output with the index master's content, and its content is then gone from disk
      with exit 0 and no warning; `-b typstpdf` on the identical input hard-fails with
      `TypstError: cyclic import`. A `project` name that slugifies to `_template`
      (e.g. `"_Template"`) clobbers the shared `_template.typ` infrastructure file
      itself, breaking every master's `#import "_template.typ": project`.

      Independently reproduced by this verifier on the current HEAD (6aa452b), not
      merely re-read from 44-REVIEW.md: a fresh fixture with `project = "Chapter 1"`,
      `index.rst` toctree-including `chapter1.rst` (body marker
      `UNIQUE-CHAPTER-MARKER-XYZ`), built with `sphinx-build -b typst`, exits 0,
      writes only `chapter1.typ` (no `index.typ`), and
      `grep -c UNIQUE-CHAPTER-MARKER-XYZ out/chapter1.typ` returns `0` -- the real
      chapter's rendered body is gone. This matches CR-01 and the orchestrator's own
      independent re-measurement in `44-REVIEW.md` ("## Orchestrator independent
      re-measurement of CR-01") exactly.

      This is not a pre-existing, unrelated defect merely surfaced by this phase: the
      collision *mechanism* in `_resolve_output_stem` is pre-existing, but it was only
      reachable by an explicit, deliberately-crafted `typst_documents` entry before
      CONF-08. CONF-08 is precisely the change that makes it reachable by an ordinary,
      unset-config Quick Start project with a common docs layout -- on the exact path
      the phase goal ("a user who follows the Quick Start exactly gets a PDF") exists
      to make reliable. None of this phase's own new gate fixtures
      (`default_typst_documents_gate`, `explicit_typst_documents_wins_gate`,
      `non_str_docname_gate`, `empty_typst_documents_optout_gate`) exercises this
      scenario -- every fixture's `project` value was chosen so its derived stem never
      collides with an existing docname or `_template`, so no test in the phase's own
      suite would catch a regression here.
    artifacts:
      - path: "typsphinx/builder.py"
        issue: "_resolve_output_stem (lines 156-261) resolves both the derived and any explicit typst_documents target name with no check against self.env.found_docs or the reserved \"_template\" basename before the stem is handed to write()/_write_template_file()."
    missing:
      - "A collision check in _resolve_output_stem (or immediately after it) that rejects any resolved stem equal to another docname actually present in self.env.found_docs (other than the docname being resolved) or equal to \"_template\", with a logger.warning and a safe fallback to the docname itself -- matching the existing D-06/D-07 degenerate-target handling style (44-REVIEW.md CR-01 fix sketch)."
      - "A new gate test mirroring both reproduced cases (derived-default-triggered docname collision, e.g. project=\"Chapter 1\" + chapter1.rst; and the _template.typ clobber, e.g. project=\"_Template\") asserting no file is silently overwritten and a warning fires, for both the derived-default path and an explicit typst_documents entry that produces the same collision."
prohibitions_flagged: []
human_verification: []
---

# Phase 44: `typst_documents` Default Derivation + Builder Input Hardening Verification Report

**Phase Goal:** A user who follows the Quick Start exactly gets a PDF. Today `typst_documents`
defaults to `[]` and `TypstPDFBuilder.finish()` returns early on it, so `sphinx-build -b typstpdf`
exits 0, emits one `WARNING`, and produces zero PDFs. This phase derives a Sphinx-native default
(mirroring `latex_documents`) and hardens `TypstPDFBuilder.finish()` against a non-`str` docname
(BLD-01).
**Verified:** 2026-08-04T07:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1 — a project whose `conf.py` never mentions `typst_documents`, built with `sphinx-build -b typstpdf`, produces a PDF named `make_filename_from_project(project)`, warning gone | ✓ VERIFIED | `44-GATE-EVIDENCE-01.md` §§1,3: RED against unchanged code (exit 0, `index.typ`, zero PDFs, `WARNING: No documents defined...`) → GREEN after the derivation (exit 0, `quickstartdefaultgate.typ`+`.pdf`, template applied, no warning). Re-confirmed by this verifier: `uv run python -m pytest tests/test_default_typst_documents_gate.py -q` passes in the full-suite run below, and `typsphinx/builder.py:28-47` (`_default_typst_documents`) and `typsphinx/__init__.py`'s registration were read directly and match the derivation described. |
| 2 | SC#2 — an explicit `typst_documents` always wins, producing exactly the targets it names and nothing else | ✓ VERIFIED | `44-GATE-EVIDENCE-01.md` §5: real `sphinx-build -b typstpdf` over `tests/fixtures/explicit_typst_documents_wins_gate` produces exactly `manual.typ`+`manual.pdf`; `ls -la` confirms no `explicitwinsgate.*` and no `index.*`. |
| 3 | SC#3 — a non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable typsphinx-level error naming the offending value, not a raw `TypeError` | ✓ VERIFIED | `44-GATE-EVIDENCE-02.md` §§1-2: RED (bare `TypeError` from `posixpath.dirname`, exit 2, whole build dies, no aggregate message) → GREEN (`isinstance(docname, str)` guard at `typsphinx/builder.py:966`, typsphinx-authored `WARNING: typst_documents entry has a non-str docname: 123 -- expected a str`, aggregate `ExtensionError`, `TypeError` absent, the valid master's `index.typ`/`.pdf` still written). Guard code read directly and confirmed present at HEAD. |
| 4 | SC#4 — the output-filename rename is measured, not assumed, and the measured pair is handed to Phase 46 as CHANGELOG source text | ✓ VERIFIED | `44-GATE-EVIDENCE-03.md` §§1-9: two named commits, per-side `typsphinx.__file__` isolation proofs (distinct paths, neither the main checkout), four real builds (pre: `index.typ`/412B/no template/0 PDFs/1 warning; post: `quickstartdefaultgate.typ`/532B/templated/1 PDF/0 warnings), paired table, quotable CHANGELOG block in §7. `44-GATE-EVIDENCE-04.md` §8 (orchestrator addendum) independently re-confirms this post-merge, reading the file's own sections rather than trusting 44-03's SUMMARY. |
| 5 | SC#5 — every existing test that encoded the old `[]`-default is updated deliberately and traceably; full suite, `black`/`ruff`/`mypy`, and the full-corpus `-b typstpdf` gate are green | ✓ VERIFIED | `44-GATE-EVIDENCE-04.md` §§1-7: repo-wide census (107 `conf.py` files, 2 intentional new exceptions), corrected blast-radius grep surfacing `tests/test_builder.py` (missed by `44-RESEARCH.md`'s original pattern set) plus the reconciled `tests/test_builder_requirement13.py` discovery, per-file verdict table (2 CHANGED, 9 VERIFIED-NO-CHANGE, each with a proof), full suite `855 passed, 1 skipped` including `test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` by node id, `black`/`ruff`/`mypy` all exit 0, `pyproject.toml`/`uv.lock` diff empty. **Independently re-run by this verifier** on the current checkout (HEAD `6aa452b`, main tree, not a worktree): `uv run python -m pytest -q` → `855 passed, 1 skipped in 78.39s`; `uv run black --check .` → clean; `uv run ruff check .` → clean; `uv run mypy typsphinx/` → clean. Matches the recorded baseline exactly. |
| 6 | A user who follows the Quick Start exactly gets a PDF, without a reachable configuration-free path to silent content loss or a hard build failure (phase goal statement, judged goal-backward against CR-01) | ✗ FAILED | See Gaps Summary and the `gaps` frontmatter entry. Independently reproduced by this verifier (not merely re-read from `44-REVIEW.md`): `project = "Chapter 1"` + toctree-included `chapter1.rst` → `sphinx-build -b typst` exits 0, writes only `chapter1.typ` (the index master's content, self-referential `include`), and `chapter1.rst`'s own rendered body (`UNIQUE-CHAPTER-MARKER-XYZ`) is verified absent from disk (`grep -c` → `0`). |

**Score:** 5/6 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py::_default_typst_documents` | Pure derivation callable, `(root_doc, <slug>.typ, project, author, "typst")` | ✓ VERIFIED | Present at lines 28-47, matches D-01/D-02 exactly; body is a single `return`, no memoization, confirmed by reading the source directly. |
| `typsphinx/__init__.py` registration | `add_config_value("typst_documents", _default_typst_documents, "html", [list])` | ✓ VERIFIED | Import and registration both present (`grep -c '_default_typst_documents' typsphinx/__init__.py` == 2 per `44-GATE-EVIDENCE-01.md`). |
| `typsphinx/builder.py` BLD-01 guard | `isinstance(docname, str)` guard before the path helpers, joining the existing `failures` list | ✓ VERIFIED | Present at line 966, matches the sibling empty-entry guard's warn/append/continue shape, confirmed by direct read. |
| `typsphinx/builder.py` D-03 wording | Opt-out warning restated as "explicitly set to an empty list" | ✓ VERIFIED | Present at lines 936-940, WARNING severity unchanged. |
| `typsphinx/builder.py` collision guard (CR-01 fix) | A check rejecting a resolved stem that collides with `self.env.found_docs` or `"_template"` | ✗ MISSING | `_resolve_output_stem` (lines 156-261) contains no reference to `self.env.found_docs` or `"_template"` anywhere in its body — confirmed by direct read and by `grep -n "found_docs" typsphinx/builder.py`, whose three matches (307, 379, 979) are all unrelated to this method. |
| Four `44-GATE-EVIDENCE-*.md` files | RED/GREEN records for CONF-08, BLD-01, SC#4, SC#5 | ✓ VERIFIED | All four exist, read in full, and their commands/outputs are internally consistent with the code at HEAD. |
| `44-REVIEW.md` | Code review with CR-01 blocker + orchestrator independent reproduction | ✓ VERIFIED | Present, committed, contains both the reviewer's findings and a distinct orchestrator re-measurement section. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `typsphinx/__init__.py::setup` | `typsphinx/builder.py::_default_typst_documents` | `add_config_value("typst_documents", _default_typst_documents, ...)` | ✓ WIRED | Confirmed by direct read of both files. |
| `typsphinx/builder.py::_default_typst_documents` | `sphinx.util.osutil.make_filename_from_project` | target name derivation | ✓ WIRED | Import present, call present in the function body. |
| `sphinx.config.Config.__getattr__` | `typsphinx/writer.py::_is_master_document` | unset config resolves to the derived list, root_doc becomes a master | ✓ WIRED | Confirmed by `44-GATE-EVIDENCE-01.md` §3's emitted `.typ` carrying the template import/call, and independently by this verifier's own repro build (root_doc's output was templated). |
| `TypstPDFBuilder.finish` loop | terminal `ExtensionError` | non-str-docname failures append to the existing `failures` list | ✓ WIRED | Confirmed by direct read at lines 966-971 and `44-GATE-EVIDENCE-02.md`'s GREEN transcript. |
| `_default_typst_documents` output / any explicit `typst_documents` target | `self.env.found_docs` / `"_template"` reserved name | collision check | ✗ NOT_WIRED | No such check exists anywhere in `_resolve_output_stem`, `write()`, or `_write_template_file()`. This is the CR-01 gap. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CONF-08 | 44-01, 44-02, 44-03, 44-04 | With `typst_documents` unset, `-b typstpdf` produces a PDF; derived from `root_doc`/`project`/`author`; explicit setting always wins | ✓ SATISFIED (for the non-colliding case) | `.planning/REQUIREMENTS.md:73` marked `[x]` and `Complete` at line 179. The core derivation, precedence, and opt-out behavior are all verified truths 1/2/5 above. Truth 6 (CR-01) shows the derivation is not yet safe against a docname/`_template` collision — a gap within CONF-08's surface, not a separate requirement. |
| BLD-01 | 44-02, 44-04 | A non-`str` docname reaching `finish()` fails with an actionable typsphinx-level error | ✓ SATISFIED | `.planning/REQUIREMENTS.md:87` marked `[x]` and `Complete` at line 180 (the tracking gap noted by `44-GATE-EVIDENCE-04.md` and `44-WINDOWS.md` window #2 was closed by the orchestrator, confirmed: `WINDOWS.md` shows `open_count: 0`, window #2 `status: fixed`). Truth 3 above verifies the implementation directly. |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s "Phase 44" mappings cover exactly CONF-08 and BLD-01, both of which appear in every plan's `requirements:` frontmatter across the phase.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/builder.py` | 929 | `if not typst_documents:` also fires for `typst_documents = None`, but the message at 936-940 unconditionally asserts "explicitly set to an empty list" | ⚠️ Warning (WR-01, `44-REVIEW.md`) | Cosmetic/diagnostic-accuracy only — the *behavior* (nothing compiled, WARNING severity) is correct for `None`; only the wording is misleading. Does not block the phase goal. Confirmed still present at HEAD. |
| `tests/test_default_typst_documents_gate.py` | 120 | `assert "Nothing to compile" not in result.stderr` — the *old* pre-phase wording, which can never appear post-phase regardless of correctness (current wording is "...nothing will be compiled...") | ℹ️ Info (IN-01, `44-REVIEW.md`) | Vacuous assertion; the surrounding `pdf_file.exists()` checks already prove the derived default was consulted, so this doesn't mask a real gap, but it can't catch a future wording regression either. Confirmed still present at HEAD. |

Neither WR-01 nor IN-01 rises to blocker severity — both are cosmetic/test-hygiene issues that do not affect whether the phase goal is achieved, consistent with `44-REVIEW.md`'s own classification (`warning`/`info`, not `critical`).

### Human Verification Required

None. CR-01 is a code-level, deterministically-reproducible defect (reproduced twice: once by the code reviewer, once independently by the execute-phase orchestrator, once again independently by this verifier) — it does not require human judgment to confirm, only a fix.

### Gaps Summary

**CR-01 — the derivation makes a pre-existing collision mechanism reachable with zero configuration, undermining the phase goal for a plausible subset of Quick Start users.**

The phase's four Success Criteria (SC#1-SC#5) are each independently and narrowly satisfied: the derivation function is correct and pure, explicit settings win, the non-`str` docname hardening works and reports through the existing aggregate mechanism, the filename/content rename is measured and handed to Phase 46, and the full test/lint/type/corpus gate is green. All five are re-confirmed here against the live codebase, not merely against the SUMMARY/GATE-EVIDENCE narrative — this verifier independently re-ran the full suite (`855 passed, 1 skipped`), `black`, `ruff`, `mypy`, and read every piece of production code named above directly.

However, the ROADMAP phase goal is broader than the five enumerated SCs: **"A user who follows the Quick Start exactly gets a PDF."** None of SC#1-SC#5 was written to cover a project with more than one document, and the phase's own new fixtures are all single-document or deliberately collision-free by construction — so nothing in the phase's own verification surface would ever exercise the scenario CR-01 describes. But a Sphinx project with a toctree and a docname that happens to match the project-name slug is not an edge case; it is an entirely ordinary documentation layout (a project named after its main topic or first chapter — the code review's own example, `project = "Chapter 1"` next to `chapter1.rst`, is about as vanilla as a docs layout gets). Before this phase, that same project would have needed an explicit, deliberately-crafted `typst_documents` entry to hit the collision. After this phase, with `typst_documents` left completely unset — i.e., exactly the "follows the Quick Start exactly" user this phase exists to serve — the same collision fires automatically, silently destroying a real document's content on `-b typst` (exit 0, no warning) or hard-failing `-b typstpdf` with an opaque `TypstError: cyclic import` that gives the user no indication their project name is the cause.

This verifier independently reproduced both failure modes against the current HEAD (6aa452b) rather than relying on `44-REVIEW.md`'s transcript or the orchestrator's re-measurement: a fresh two-document fixture (`project = "Chapter 1"`, `index.rst` toctree-including `chapter1.rst`) built with `sphinx-build -b typst` exits 0 and leaves only `chapter1.typ` on disk, containing the index master's content; a `grep` for the real chapter's unique body marker in that file returns zero matches. The `_template.typ`-clobber variant reported in `44-REVIEW.md` (`project = "_Template"`) was not independently re-run here but was not needed to be — the mechanism (no collision check anywhere in `_resolve_output_stem`) is the same code path, confirmed present by direct source read.

**Judgment on SC#1 specifically, as instructed:** SC#1's literal wording ("a Sphinx project whose `conf.py` never mentions `typst_documents`... produces a PDF... measured on a real build") is satisfied for the specific fixture that discharges it — a single-document project with no toctree, where no collision can occur. SC#1 is not FAILED by CR-01; it is narrowly true and its own evidence is sound. What CR-01 undermines is the broader, unenumerated phase-goal claim that sits above SC#1-SC#5 in `ROADMAP.md`'s prose — a goal-backward gap the task list did not anticipate, which is exactly the class of shortfall this verification step exists to catch. SC#2 through SC#5 are unaffected by CR-01: SC#2's fixture is a single explicit entry with no collision; SC#3's fixture is a valid+malformed pair with no filename collision; SC#4 measures the rename/content-change pair on the same collision-free fixture SC#1 uses; SC#5 is a test/lint/type/manifest audit that CR-01 does not touch.

The project owner has already decided to close this gap inside Phase 44 via gap closure (per this verification's brief). `44-REVIEW.md` provides a concrete fix sketch (a collision check in `_resolve_output_stem` falling back to the docname itself with a `logger.warning`, mirroring the existing D-06/D-07 degenerate-target handling), which the `missing` list above carries forward for `/gsd-plan-phase 44 --gaps` to consume, along with a requirement for a new gate test covering both reproduced cases (docname collision and `_template.typ` clobber) for both the derived-default path and an explicit `typst_documents` entry.

---

*Verified: 2026-08-04T07:00:00Z*
*Verifier: Claude (gsd-verifier)*
