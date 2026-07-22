# Milestones: typsphinx

## v0.6.2 rendering fidelity round 2 (Shipped: 2026-07-23)

**Closeout:** override_closeout (pre-close artifact audit surfaced one non-blocking item — Phase 22.3's verification abstained to `human_needed` for a single `verification: backstop` truth: exercising the two GATE-01 fixtures under a real `pytest-xdist` parallel run, which the project does not depend on. All five ROADMAP success criteria for 22.3 were independently verified with direct evidence, including two live revert-and-restore reproductions of the pre-fix defects. Every other phase (19, 20, 21, 22, 22.1, 22.2, 22.4, 23) is `phase_complete` + verification `passed`. Operator acknowledged the backstop item plus 9 pending-todo backlog entries as deferred at close — see STATE.md Deferred Items. **Known verification overrides: 1** (Phase 22.3 pytest-xdist backstop).)
**Phases:** 9 (19, 20, 21, 22, 22.1, 22.2, 22.3, 22.4, 23) · **Plans:** 30 · **Tasks:** 65
**Requirements:** 25/25 v1 requirements complete (FID-02..FID-14, PDF-01, PDF-02, CONF-01..CONF-03, WR-01, WR-02, DOC-01..DOC-05) · **Known gaps:** none milestone-blocking
**Git:** milestone work on `gsd/v0.6.2-rendering-fidelity-round-2` (branching strategy `milestone`); tagged `v0.6.2` at close
**Milestone invariant held:** zero new runtime dependencies, no `@preview` version bump, the 3-way version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) untouched

**Delivered:** Round 2 of rendering fidelity — resolved the 13 medium/low silent mis-render findings the v0.6.1 audit left open as one coherent `translator.py` fix series grouped by root cause (clusters A–F), each pinned by a fail-pre-fix real-`typst.compile()` GATE-01 fixture, plus five inserted builder/config/docs phases: the Issue #117 `typstpdf` target-name PDF fix, nested-master compile-root alignment, a dead-config sweep that also repaired the entirely-broken `typst_package` Typst-Universe path end-to-end, builder-warning hardening (a missing/malformed master now fails loudly instead of a silent successful build), and a full-text README/CLAUDE.md accuracy pass. Closed on the full ~684-page Sphinx `doc/` corpus regression gate (fatal-free, valid `%PDF`, `unknown_visit` catalogue empty).

**Key accomplishments:**

- **Block-separation cluster (Phase 19, FID-02..FID-06):** adjacent block / sibling elements — paragraphs-in-list-items, sibling `desc_signature`s, rubric/option headings, definition-list term↔definition, back-to-back body-less `confval`s — now render with the visible separation the `-b html` authority shows instead of concatenating, via a coherent set of `parbreak()`/`linebreak()`/`terms(separator:)` separator fixes.
- **Signature token spacing + residual fidelity (Phases 20–21, FID-07..FID-14):** intra-signature token spacing restored (`class `/`exception ` prefix, C/C++ inter-token spaces, `:type:`/`:default:` colon-space) by reducing `desc_sig_space` to pass-through; long inline-literal runs wrap at UAX14 boundaries instead of clipping, paragraph soft-newlines collapse to a space, the codly config wrapper stops leaking as prose, external links get `show link:` styling, and PEP 3102/570 separators stop injecting their hover-title text inline.
- **Issue #117 target-name PDF fix + nested-master alignment (Phases 22, 22.1, PDF-01/PDF-02):** a single guarded `TypstBuilder._resolve_output_stem()` now governs all three `.typ`/`.pdf` output-path sites so `typst_documents = [('index', 'manual.typ', …)]` emits `manual.pdf`, not `index.pdf`; `TypstPDFBuilder.finish()` compiles each master's own on-disk `.typ` at its real docname-derived location so nested masters (`api/index`) resolve their `#include()`s and images — the compile basis now matches the translator's emission basis.
- **Dead-config sweep + `typst_package` repair (Phase 22.2, CONF-01..CONF-03):** deleted `typst_output_dir` and `typst_author_params` from every surface, and made the Typst-Universe `typst_package` path — previously unable to compile at all — work end-to-end (BUG-A `_template.typ` never written, BUG-B unconditional param injection, BUG-C dead author wiring, BUG-D wrong docs examples), all locked by a standing config→output regression gate so a registration-only assert can no longer hide a dead feature.
- **Builder-warning hardening + docs accuracy (Phases 22.3, 22.4, WR-01/WR-02, DOC-01..DOC-05):** a missing or malformed master now joins the aggregate `ExtensionError` instead of a silent successful build, the render gate stops asserting on `typst-py`'s uncontracted error wording, and README/CLAUDE.md/pyproject comments were re-derived from measured behavior — unverifiable numeric claims (test count, coverage %) removed rather than re-measured, with a `README`↔`pyproject` version-sync ratchet test added.
- **Release prep + regression-gate close (Phase 23):** bumped `pyproject.toml` → 0.6.2 (sole literal) with `uv.lock` in lockstep, curated the `## [0.6.2]` CHANGELOG entry covering all 25 ledger IDs (Issue #117 presented as a user-visible output-filename change; `### Removed` for the config deletions), and closed on a live full-corpus `-b typstpdf` gate.
---

## v0.6.1 rendering fidelity (Shipped: 2026-07-19)

**Closeout:** override_closeout (pre-close artifact audit clear; Phase 16 & 18 verified `passed`; Phase 17 — a pure audit/documentation phase — has no machine `VERIFICATION.md`, so `init.manager` could not certify `verified_closeout`. Its verification was instead the human confirmation gate 17-03 (D-01a: 14 accepted / 1 rejected of the 15 candidate findings, final severities signed off) plus `17-VALIDATION.md` (five mechanical consistency checks PASS), and its output — FID-01a — was proven downstream by Phase 18's real-compile regression fixture + the closing full-corpus gate. Verification override accepted by operator at close.)
**Phases:** 3 (16–18) · **Plans:** 9 · **Tasks:** 18
**Requirements:** 6/6 v1 requirements complete (TODO-01, MAN-01, LEN-01, AUD-01, FID-01→FID-01a, GATE-03) · **Known gaps:** none (13 medium/low audit findings recorded in `17-AUDIT-CATALOGUE.md` as a Future-Requirements pointer, not milestone-blocking)
**Git:** milestone work on `main` (branching strategy `none`), commits from `dcd03eb` (2026-07-13) through `cc7c64a` (2026-07-19); tagged `v0.6.1`
**Code delta (milestone scope):** ~15 source/test files, +1229 / −13 lines (`typsphinx/translator.py` + `tests/`); zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched

**Delivered:** Moved `typstpdf` output from "compiles fatal-free" (v0.6.0) to "renders faithfully" — implemented the last two silently-dropped nodes (`todo_node`, `manpage`), generalized the CSS-length converter into one shared helper (LEN-01), ran a full 151/151-docname human-assisted visual audit of the Sphinx v9.1.0 `doc/` corpus PDF against its `-b html` baseline (15 findings catalogued, human-confirmed), fixed the sole high-severity finding (F12 wide-table overflow → FID-01a) with a real-compile regression fixture, and closed on the full ~684-page corpus regression gate (fatal-free, `unknown_visit` catalogue empty).

**Key accomplishments:**

- `.. todo::` now renders as a gentle-clues `task()` box with its own dynamic title, gated on `todo_include_todos` via `nodes.SkipNode` exactly like every official Sphinx builder — proven through a real `sphinx-build -> typst.compile() -> pypdf` round trip in both the enabled and disabled configurations.
- `visit_manpage`/`depart_manpage` delegate wholesale to `visit_emphasis`/`depart_emphasis`, rendering `:manpage:` page-reference text (e.g. `ls(1)`) italic in every separator/mode context, proven by a real `typst.compile()` + pypdf GATE-01 fixture spanning a paragraph, a list item, and a figure caption.
- Wired `_convert_length_to_typst` into `visit_figure`/`depart_figure` (`:figwidth:`) and `depart_table` (`:width:`, covering `.. table::`/`.. csv-table::`/`.. list-table::`), closing LEN-01 as the single shared CSS-length -> Typst-length helper used at every length-bearing docutils site.
- Built the rendering-fidelity audit scaffold — three same-corpus baselines (typstpdf/html/text), a corrected exact docname-to-page mapping for all 151 docnames, and the committed `17-AUDIT-CATALOGUE.md` skeleton with fresh provenance, so Plan 17-02's page-by-page visual pass can start immediately.
- Full 151/151-docname visual audit of the sphinx-doc/sphinx v9.1.0 corpus PDF vs. its `-b html` baseline complete, yielding 15 classified systemic findings (1 high / 12 medium / 2 low severity) ready for the Plan 17-03 human confirmation gate.
- Grouped the human-confirmed catalogue's single high-severity finding (F12, wide-table overflow) into `FID-01a`, appended it plus a medium/low pointer to REQUIREMENTS.md, and passed all five mechanical consistency checks against a freshly rebuilt corpus.
- depart_table now emits fr-weighted `columns: (Nfr, ...)` from docutils colwidth, and visit_literal injects U+200B after `.`/`_` in in-table raw() content, closing the audit's sole high-severity wide-table collision bug.
- Re-ran the real ~684-page Sphinx v9.1.0 corpus through `-b typstpdf` post-FID-01a: fatal-free (689-page `index.pdf`, valid `%PDF` magic), `unknown_visit` catalogue empty, and the SC#4 no-new-deps/no-`@preview`-bump invariant confirmed untouched — milestone v0.6.1's regression gate is closed.

---

## v0.6.0 real-world robustness (Shipped: 2026-07-13)

**Closeout:** override_closeout (milestone audit passed — 19/19 requirements, 16/16 integration seams wired, 5/5 E2E flows; pre-close artifact audit found 13 open debug sessions — non-fatal post-GATE-02 rendering-polish, acknowledged and deferred to the next milestone, see STATE.md Deferred Items)
**Phases:** 5 (11–15) · **Plans:** 15 · **Tasks:** 33
**Requirements:** 19/19 v1 requirements complete · **Known gaps:** none (13 non-fatal render-polish items deferred as next-milestone backlog)
**Git:** milestone work (173 commits) delivered via PR #115 (`release/v0.6.0 → main`, closes #114), merge commit `cc26b47`; tagged `v0.6.0` on the merge commit. A Windows-only CI false-negative (the corpus SC#2 `unknown_visit` parser was `^`-anchored and missed CRLF/leading-CR/location-prefixed warning lines) was root-cause-fixed on the PR before merge — the real gate (SC#1 fatal-free compile) passed on all platforms throughout.
**Released:** PyPI `typsphinx 0.6.0` (wheel + sdist) + GitHub Release `v0.6.0`, via `release.yml` (run 29210840198, green end-to-end)
**Code delta (milestone scope):** all work in `typsphinx/translator.py` (+ tests/fixtures); zero new runtime dependencies

**Delivered:** Sphinx's own full `doc/` tree now compiles end-to-end through the `typstpdf` builder with no fatal `TypstCompilationError` (Issue #114 closed) — fixing the two fatal figure/image bugs (px→pt length conversion + `:target:`/caption buffer-swap), adding correct rendering for the highest-frequency previously-dropped nodes (version directives, `refid` cross-references, autodoc `desc_*`, footnotes via a doctree pre-pass, transition/topic/line_block/glossary/tabular_col_spec/abbr), and a graceful-degrade net for out-of-scope graphical nodes — all behind a standing real-`typst.compile()` acceptance gate (GATE-01) and validated against the real corpus (GATE-02). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.

**Key accomplishments:**

- New `_convert_length_to_typst()` regex-based CSS-length-to-Typst converter wired into `visit_image` (fixes Issue #114's fatal `width: 200px` compile abort), plus a shared `_visit_graphical_placeholder()` helper giving `graphviz`/`inheritance_diagram` a visible bordered Typst `rect()` block + one warning + clean `SkipNode` instead of leaking source or aborting
- Figure captions now render through the normal visitor chain via buffer-swap (never `node.astext()`), consumed as a `{...}` code-block `caption:` argument, plus a new `refid` fallback branch in `visit_reference` so internal same-document `:target:` links compile alongside external-URL ones
- Extended `tests/test_pdf_render_gate.py` with three `slow`-marked real-compile test classes proving FIG-01/FIG-02/DEG-01/DEG-02 through `sphinx-build -> typst.compile() -> pypdf` — and, in the process, discovered and fixed a third, previously-hidden fatal Typst-compile bug (labels attached to code-mode statements are invalid Typst syntax) that this gate's own real-compile methodology was the only way to surface
- Unboxed italic version-directive labels (`versionadded`/`versionchanged`/`deprecated`/`versionremoved`) rendered by detecting Sphinx's own classed inline, with a real-compile GATE-01 fixture proving all four kinds plus the content-less case.
- Fixed the fatal dangling-`:term:`-anchor bug by emitting a bracket-wrap Typst `<label>` in `depart_term`, confirmed `visit_reference`'s refid branch was already correct, and proved both fixes with a real-compile `TestXrefRefidRenderGate` gate that would abort without them.
- Landed the four autodoc signature sub-part handlers -- `desc_returns` (return arrow), `desc_signature_line` (genuine `linebreak()`, resolving Open Question 1 empirically), `desc_optional` (recursion-safe nested brackets), and `desc_inline` (transparent pass-through, D-06) -- plus a real-compile GATE-01 fixture proving all four via `pypdf` text-extraction.
- Four small additive translator.py handlers -- transition-to-rule, glossary pass-through, tabularcolumns SkipNode, and stateless abbreviation-expansion -- proven correct through a real sphinx-build -> typst.compile() -> pypdf round-trip.
- Widened the load-bearing `visit_title`/`depart_title` buffer-swap to cover `nodes.topic` parents alongside `nodes.Admonition`, added `visit_topic`/`depart_topic` reusing the `clue` box helper, and fixed a pre-existing multi-child-title compile fatal — all four locked decisions (D-01/D-02/D-05/D-06) plus the Pitfall-1 fix landed as one atomic change per RESEARCH.md's atomicity mandate.
- Added visit_line_block/visit_line to translator.py so line-block content (addresses, epigraph shapes, poetry stanzas) renders with every line break preserved via a real `linebreak()`, and nested line blocks reproduce their structural indentation via a per-depth `h()` spacer — both compile-safe with zero markup-mode involvement.
- New `topic_line_block_render_gate` fixture + `TestTopicLineBlockRenderGate` class prove, via an uncaught real `typst.compile()`, that topic titles and `.. contents::` never leak into Typst's auto-outline (count==1), address/poem `line_block`s produce genuine `linebreak()`s (never source-`\n`-only concatenation), and the pre-existing multi-child admonition-title path (Pitfall 1) still renders correctly.
- Typst-native footnote rendering via a document-order pre-pass index in `visit_document`, with `visit_footnote_reference` emitting the compile-proven `[#footnote({body}) <fn-id>]` / `footnote(<fn-id>)` definition/reuse forms and `visit_footnote` suppressing the definition at its natural docutils location.
- A real `typst.compile()` acceptance fixture (`footnote_render_gate`) and `TestFootnoteRenderGate` class prove the Plan 14-01 footnote handlers compile cleanly end-to-end (SC#1-4), and in doing so caught and fixed a genuine paragraph-state-clobbering bug in `visit_footnote_reference`'s buffer-swap that would have made every realistic footnote citation a fatal compile abort.
- New `tests/test_corpus_gate.py` slow-marked pytest module that shallow-clones Sphinx's own `doc/` tree, wires in typsphinx, builds the full tree through `typstpdf`, and asserts the fatal-free PDF triple plus a frequency-ranked `unknown_visit` catalogue.
- Git-worktree-isolated depart_term XREF-01 revert + env-gated before/after empty-URL warning counter, both builds translate-phase-only (`-b typst`), added to `tests/test_corpus_gate.py`

---

A historical record of shipped versions. Full detail per milestone lives in `.planning/milestones/`.

---

## v0.5.0 — forward-ecosystem

**Shipped:** 2026-07-11
**Closeout:** verified_closeout (pre-close artifact audit clear; all 6 phases verified; milestone audit passed — 14/14 requirements, 5/5 integration seams, E2E release flow ready)
**Phases:** 6 (6–10 + 8.1) · **Plans:** 13 · **Tasks:** 29
**Requirements:** 14/14 v1 requirements complete · **Known gaps:** none
**Git:** milestone work on `release/v0.5.0`, merged to `main` via PR #112; tagged `v0.5.0` (on `main`)
**Released:** PyPI `typsphinx 0.5.0` (wheel + sdist) + GitHub Release, via `release.yml` (green end-to-end)
**Code delta (milestone scope, excl. `.planning/`):** 29 source/config files, +1025 / −467 lines

**Delivered:** Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1, docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the soft-deprecated docutils/Sphinx API surface, fixing a long-latent admonition markup/code-mode render bug (discovered once `docs-pdf` first compiled post-`kai`-fix), adding a `typst compile` smoke gate that guards all four packages, and releasing v0.5.0 to PyPI with the full 3-OS × Python 3.12–3.13 CI matrix observed green. Latest-only, no compatibility range.

**Key accomplishments:**

1. **Raised runtime pins + Python floor (Phase 6):** Re-pinned `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` and raised the Python floor to 3.12–3.13 across all 21 declaration sites (pyproject `requires-python`/classifiers, regenerated `uv.lock`, `tox.ini`, and the four GitHub Actions workflows) as one atomic pin-raise — both builders confirmed registering and a live `-b typst` build passing under Sphinx 9.1.
2. **Bumped `@preview` packages + typst 0.15 — the `kai` fix (Phase 7):** Raised `typst>=0.15.0,<0.16` and bumped mitex `0.2.4`→`0.2.7` (the actual fix, mitex PR #201), gentle-clues `1.2.0`→`1.3.1`, codly-languages `0.1.1`→`0.1.10` (codly `1.3.0` unchanged, registry ceiling), in lockstep across the 3-way version-sync — empirically closing the `unknown variable: kai` compile break via a real `tox -e docs-pdf` run producing a clean 101-page PDF.
3. **API & test compatibility (Phase 8):** Landed `traverse()`→`findall()` and modernized all soft-deprecated docutils/Sphinx call sites (`OptionParser`→`get_default_settings`, `builder.app`→`_app`, `writer_name`→`writer=get_writer_class(...)()`), then installed a permanent pytest `filterwarnings` guard escalating both `DeprecationWarning` and `PendingDeprecationWarning` — full suite green, zero `traverse()` remaining.
4. **Admonition rendering fix (Phase 8.1, inserted):** Rewrote `_visit_admonition`/`_depart_admonition` to emit gentle-clues code-mode content-blocks (`info({...})`) instead of markup-mode brackets (`info[...]`), preserved inline-markup titles via a buffer-swap (also fixing a latent title double-emission bug), added the five previously-unimplemented types (`hint`/`error`/`danger`/`attention`/generic `.. admonition::`), and proved it with a real `sphinx-build → typst.compile() → pypdf` PDF-text-extraction acceptance gate.
5. **Green CI matrix + smoke gate + guardrails (Phase 9):** Observed all 13 CI jobs green for the first time on Sphinx 9.1/docutils 0.22/typst 0.15 across all 3 OS runners (PR #112); added a `typst compile` smoke gate (`tests/test_preview_smoke_gate.py`) exercising all four `@preview` packages via real calls — closing the coverage gap the historical `kai` regression slipped through, proven with a negative control; reconciled stale `main` branch-protection required-checks; confirmed the dependency-ceiling guardrails (`sphinx<10`/`typst<0.16`/`docutils<0.23`).
6. **Version single-source + v0.5.0 release (Phase 10 + milestone close):** `typsphinx.__version__` now derives from `importlib.metadata` (retiring the stale `0.4.3`) with `pyproject.toml` the sole `0.5.0` literal, `uv.lock` regenerated, plus an independent `tomllib` drift-guard test; curated `CHANGELOG.md` `## [0.5.0]` entry as the Release-body source; publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI + GitHub Release) executed at milestone close, mirroring the v0.4.4 precedent.

**Deferred:** CFG-01 (was FWD-03 — user-configurable `@preview` versions) and XOS-01 (cross-OS docs-PDF CI on macOS/Windows) → v2. Phase 8's multi-`<term>` definition-list hardening deferred as forward-looking (no current docutils 0.22.4 rST syntax emits a multi-`<term>` node).

**Archives:** `milestones/v0.5.0-ROADMAP.md`, `milestones/v0.5.0-REQUIREMENTS.md`, `milestones/v0.5.0-MILESTONE-AUDIT.md`

---

## v0.4.4 — CI-repair + modernize

**Shipped:** 2026-07-05
**Closeout:** verified_closeout (pre-close artifact audit clear; all 5 phases verified)
**Phases:** 5 (1–5) · **Plans:** 15 · **Tasks:** ~35
**Requirements:** 23/23 v1 requirements complete · **Known gaps:** none
**Git:** milestone work merged to `main` via PRs #104 / #105 / #106; close + release-prep via #109; tagged `v0.4.4` (on `main` dae500a)
**Released:** PyPI `typsphinx 0.4.4` (wheel + sdist) + GitHub Release, via release run 28731646924 (green end-to-end)
**Code delta (milestone scope):** ~15 source/config files, +217 / −1202 lines (net, incl. `uv.lock` collapse)

> **Release note:** The first `v0.4.4` tag push failed at the `release.yml` Validate gate — the
> version-verify step imported stdlib-only `tomllib` on the 3.10 floor (a PYVER-02 side effect
> only exercised at tag time). Fixed with a `tomllib`/`tomli` fallback (PR #110), tag re-pointed,
> release re-run green. This also resolved D-11 (`softprops/action-gh-release@v3` ran green).

**Delivered:** Restored a fully green CI pipeline on `main` — lint, the 3-OS × Python 3.10–3.13 test matrix (19 jobs), coverage, and the docs PDF build — by pinning the runtime dependency graph back to a known-good, reproducible combination, then modernized the Python floor and dev tooling and installed durability guardrails so the drift can't silently recur.

**Key accomplishments:**

1. **Root-cause pin (Phase 1):** Pinned `typst>=0.14.1,<0.15` (with precautionary `sphinx<9` / `docutils<0.22` ceilings), regenerated `uv.lock`, mirrored tox ceilings, and removed the dead `sphinx-testing` dep — fixing the `typst.TypstError: unknown variable: kai` break from a bundled `@preview` package under typst 0.15.
2. **Verified green baseline (Phase 2):** Confirmed every previously-red CI job green across the full matrix (incl. the 7 PDF-integration tests and `docs.yml` multi-language PDF-copy), and guarded the 3-way `@preview` version sync with an automated desync test.
3. **Modernized Python floor (Phase 3):** Bumped the supported range to 3.10–3.13 across every config surface (pyproject, tox, CI/docs/release workflows, black/ruff/mypy target-versions) as one atomic, CI-verified batch.
4. **Refreshed dev tooling (Phase 4):** Conservative floor+ceiling bumps for pytest/mypy/black/ruff/tox; artifact actions to node24 ahead of GitHub's 2026-09-16 Node-20 removal; removed the stale `Test Python 3.9` required check.
5. **Durability guardrails (Phase 5):** `uv sync --locked` at all 9 sites (DUR-01), a standalone weekly + dispatch `drift.yml` forward-drift detector with deduplicated issue reporting (DUR-02), a scoped `sphinx-typst-stack` Dependabot group (DUR-03), and a README CI status badge (DUR-04).

**Deferred:** D-11 (`softprops/action-gh-release@v3` tag-gated runtime confirmation) — signed off to the next real release tag (this v0.4.4 release exercises it). v2 forward-ecosystem support (FWD-01/02/03: Sphinx 9, typst 0.15+, configurable `@preview` versions) remains out of scope.

**Archives:** `milestones/v0.4.4-ROADMAP.md`, `milestones/v0.4.4-REQUIREMENTS.md`

---
