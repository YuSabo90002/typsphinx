# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- 🚧 **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (planning, started 2026-07-20)

## Phases

**Phase Numbering:**

- Integer phases (19, 20, 21): Planned milestone work
- Decimal phases (19.1, 19.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.6.2 continues from v0.6.1's Phase 18, so it starts at Phase 19.

<details>
<summary>✅ v0.4.4 — CI-repair + modernize (Phases 1–5) — SHIPPED 2026-07-05</summary>

Restored a fully green CI pipeline on `main` by pinning the runtime dependency graph back to a
known-good, reproducible combination, then modernized the Python floor (3.10–3.13) and dev tooling
and installed durability guardrails so the drift cannot silently recur. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.4.4-ROADMAP.md`](milestones/v0.4.4-ROADMAP.md).

- [x] Phase 1: Pin Runtime Dependencies to Known-Good (2/2 plans) — completed 2026-07-04
- [x] Phase 2: Verify the Green Baseline (3/3 plans) — completed 2026-07-04
- [x] Phase 3: Modernize Python Floor (3.10–3.13) (2/2 plans) — completed 2026-07-04
- [x] Phase 4: Refresh Dev Tooling (4/4 plans) — completed 2026-07-04
- [x] Phase 5: Durability Guardrails (4/4 plans) — completed 2026-07-05

</details>

<details>
<summary>✅ v0.5.0 — forward-ecosystem (Phases 6–10 + 8.1) — SHIPPED 2026-07-11</summary>

Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1,
docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in
lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the
soft-deprecated docutils/Sphinx API, fixing a long-latent admonition markup/code-mode render bug,
adding a `typst compile` smoke gate, keeping the full 3-OS × Python 3.12–3.13 CI matrix green, and
releasing v0.5.0 to PyPI. Latest-only, no compatibility range. Full phase detail, success criteria,
decisions, and tech-debt notes are preserved in
[`milestones/v0.5.0-ROADMAP.md`](milestones/v0.5.0-ROADMAP.md).

- [x] Phase 6: Raise Runtime Pins + Python Floor (1/1 plan) — completed 2026-07-09
- [x] Phase 7: Bump @preview Packages + typst 0.15 (kai fix) (1/1 plan) — completed 2026-07-11
- [x] Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) (3/3 plans) — completed 2026-07-11
- [x] Phase 8.1: Admonition Rendering Fix (INSERTED) (4/4 plans) — completed 2026-07-11
- [x] Phase 9: Green CI Matrix + Smoke Test + Guardrails (2/2 plans) — completed 2026-07-11
- [x] Phase 10: Version-String Fix + v0.5.0 Release (2/2 plans) — completed 2026-07-11

</details>

<details>
<summary>✅ v0.6.0 — real-world robustness (Phases 11–15) — SHIPPED 2026-07-13</summary>

Compiled a large real-world documentation set (Sphinx's own `doc/` tree) end-to-end through the
`typstpdf` builder with no fatal Typst errors (GATE-02: ~14.4 MiB PDF, 0 errors), and added correct,
compilable rendering for the most-frequent previously-dropped docutils/Sphinx nodes. Driven by
Issue #114: fixed the two fatal figure/image bugs first (px→pt length conversion + `:target:`/caption
buffer-swap), stood up a standing real-`typst.compile()` acceptance gate (GATE-01) extended by every
node-handler phase, then landed the high-frequency handlers (versionmodified, `refid` cross-refs,
autodoc `desc_*`, footnotes via a doctree pre-pass, transition/topic/line_block/glossary/
tabular_col_spec/abbr) and a graphviz/inheritance_diagram graceful-degrade net. Zero new runtime
dependencies; the 3-way `@preview` version-sync surface untouched. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.0-ROADMAP.md`](milestones/v0.6.0-ROADMAP.md).

- [x] Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net (3/3 plans) — completed 2026-07-12
- [x] Phase 12: High-Volume Independent Node Handlers (4/4 plans) — completed 2026-07-12
- [x] Phase 13: Shared Dispatch-Point Changes (topic + line blocks) (3/3 plans) — completed 2026-07-12
- [x] Phase 14: Footnotes (doctree pre-pass) (2/2 plans) — completed 2026-07-12
- [x] Phase 15: Full-Corpus Validation (3/3 plans) — completed 2026-07-12

</details>

<details>
<summary>✅ v0.6.1 — rendering fidelity (Phases 16–18) — SHIPPED 2026-07-19</summary>

Moved `typstpdf` output from "compiles fatal-free" (achieved in v0.6.0) to "renders faithfully":
implemented the last two silently-dropped nodes (`todo_node` → gentle-clues `task()` box gated on
`todo_include_todos`; `manpage` → italic literal page text via `visit_emphasis` delegation),
generalized v0.6.0's `visit_image`-local px→pt fix into one shared `_convert_length_to_typst` helper
reused at every length-bearing figure/table site (LEN-01), then ran a full 151/151-docname
human-assisted visual audit of the Sphinx v9.1.0 `doc/` corpus PDF against its `-b html` baseline —
15 systemic findings catalogued, human-confirmed (14 accepted / 1 rejected), the sole high-severity
finding (F12 wide-table glyph collision + right-margin clip) fixed via fr-weighted `columns:` from
docutils colwidth + in-table U+200B break injection (FID-01a) with a real-compile regression fixture,
and the milestone closed on the full ~684-page corpus regression gate (fatal-free, `unknown_visit`
catalogue empty). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.
The 13 medium/low audit findings are recorded as a Future-Requirements pointer. Full phase detail,
success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.1-ROADMAP.md`](milestones/v0.6.1-ROADMAP.md).

- [x] Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor (3/3 plans) — completed 2026-07-16
- [x] Phase 17: Rendering-Fidelity Audit (4/4 plans) — completed 2026-07-19
- [x] Phase 18: Fidelity Fixes + Regression-Gate Close (2/2 plans) — completed 2026-07-19

</details>

### 🚧 v0.6.2 — rendering fidelity round 2 (Phases 19–23) — IN PROGRESS

**Milestone Goal:** Resolve the 13 medium/low silent mis-render findings the v0.6.1 audit left open
(F1–F15 minus the fixed high-severity F12 and the rejected F4), delivered as **one coherent series of
translator fixes grouped by root cause** (clusters A–F) rather than 13 unrelated tickets — a single
`translator.py` separator/spacing fix typically resolves several findings in a cluster — plus the
independent Issue #117 `typstpdf` target-name PDF bug (a `builder.py`/`pdf.py` change that does NOT
share the translator root causes). Source of record for every FID finding:
[`milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`](milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md)
(D-01a human-confirmed at the 17-03 gate, severity-final).

**Standing bar (inherited GATE-01 convention):** every phase that changes a node handler ships or
extends a real `typst.compile()` acceptance fixture (the `tests/test_pdf_render_gate.py` /
`tests/test_corpus_gate.py` pattern) — string-agreement asserts alone never suffice. The local
environment runs real typst compiles (typst 0.15.0; corpus cached at `~/.cache/typsphinx-corpus-gate`),
so real-compile success criteria are achievable.

**Milestone invariant (every phase):** zero new runtime dependencies, no `@preview` version bump — the
3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) stays untouched.
Every target maps to native Typst 0.15 or already-bundled packages; none is expected to need a bump.
Flag it during planning if a phase is found to need otherwise.

**Release process (`branching_strategy: milestone`, decided 2026-07-20):** the ship unit is the
milestone. The final Phase 23 is a prep-only Release phase (version bump + CHANGELOG + closing
regression gate); the irreversible publish (tag `v0.6.2` → `release.yml` → PyPI) runs later at
`/gsd-complete-milestone`, mirroring the v0.5.0 Phase 10 / v0.6.1 pattern.

- [x] **Phase 19: Block Separation Fixes (Cluster A)** - Restore lost inter-block/inter-element separation across paragraphs-in-list-items, sibling signatures, rubric/option headings, definition terms, and back-to-back confvals — the dominant audit root cause (FID-02..FID-06) (completed 2026-07-20)
- [x] **Phase 20: Signature Token Spacing (Cluster B)** - Restore lost intra-signature token spacing: the `class `/`exception ` annotation prefix, C/C++ inter-token spaces, and `:type:`/`:default:` colon-space (FID-07..FID-09) (completed 2026-07-20)
- [x] **Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F)** - The remaining small-root-cause findings: inline-literal margin overflow, paragraph soft-newline reflow, the codly config-wrapper leak, and meaning-bearing inline styling (FID-10..FID-14) (completed 2026-07-20)
- [x] **Phase 22: typstpdf Target-Name PDF Fix (Issue #117)** - `TypstPDFBuilder.finish()` names the compiled PDF after the `typst_documents` target, not the source docname (PDF-01) (completed 2026-07-21)
- [x] **Phase 22.1: typstpdf Compile-Root Alignment for Nested Masters (INSERTED)** - `-b typstpdf` resolves `include()`/`image()` from the outdir root while the translator emits docname-relative paths; nested masters (`api/index`) are already broken. Align the two builders without moving any output (PDF-02) (completed 2026-07-22)
- [ ] **Phase 22.2: Dead Config-Value Sweep (INSERTED)** - Two documented config values that never affect output: delete `typst_output_dir`, repair the `typst_package` (Typst Universe) path end-to-end, and land a config→output regression fixture so registration-only asserts can no longer hide a dead feature (CONF-01..CONF-03) (promoted from backlog 999.4/999.3 on 2026-07-22)
- [ ] **Phase 22.3: typstpdf Builder Warning Hardening (INSERTED)** - Close the two Phase 22.1 review warnings: a master whose `.typ` is missing is silently skipped so the build "succeeds" with no PDF (WR-01), and the render-gate tests assert on `typst-py` error-message substrings that upstream can rephrase at will (WR-02) (promoted from backlog 999.5 on 2026-07-22)
- [ ] **Phase 23: v0.6.2 Release Prep + Regression-Gate Close** - Bump `pyproject.toml` to 0.6.2 + add the `CHANGELOG.md` `[0.6.2]` entry, close on the full-corpus regression gate; prep-only (publish runs at `/gsd-complete-milestone`)

## Phase Details

### Phase 19: Block Separation Fixes (Cluster A)

**Goal**: The dominant audit root cause — adjacent block or sibling elements emitted with no separator
— is resolved as one coherent set of `visit_*`/`depart_*` separator fixes, so every affected construct
renders with the visible separation the `-b html` authority shows instead of concatenating.
**Depends on**: Nothing (first phase of the milestone; the block-separation cluster is the shared root
cause the rest of the translator series builds on)
**Requirements**: FID-02, FID-03, FID-04, FID-05, FID-06
**Success Criteria** (what must be TRUE):

  1. Consecutive `paragraph`s inside a `list_item` render with visible separation instead of concatenating ("role.For example" → "role. For example"), corpus-wide — proven by a real-compile fixture (FID-02).
  2. Multiple sibling `desc_signature`s (overloads / `alias` groups / multi-option directives) render on separate lines instead of running together on one line (FID-03).
  3. A `rubric` option-group heading (and a directive-option "Options" heading) renders separated from the first following `option`/`:field:` instead of merging onto it (FID-04).
  4. A `definition_list` `term` renders on its own line, separated from its `definition`, when the list is nested in a `list_item` or the definition body opens with a nested list (FID-05); and back-to-back body-less `confval` `desc` nodes render as distinct, separated entries instead of one unbroken blob (FID-06).
  5. Every separator fix ships or extends a real `typst.compile()` regression fixture (GATE-01) that would fail without the fix; zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: 3/3 plans executed

Plans:
**Wave 1**

- [x] 19-01-PLAN.md — Shared `_emit_forced_break` helper + the two `parbreak()` sites (FID-02 paragraphs-in-list-item, FID-06 back-to-back body-less confvals)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 19-02-PLAN.md — The two `linebreak()` sibling sites (FID-03 sibling desc_signatures, FID-04 rubric/option heading)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 19-03-PLAN.md — The `terms(separator: linebreak())` site (FID-05 definition_list term/definition; the non-helper fix)

### Phase 20: Signature Token Spacing (Cluster B)

**Goal**: Intra-signature token spacing that is currently swallowed inside and around signature/field
tokens is restored, so Python and C/C++ signatures and object-description fields read with correct
inter-token spacing matching the `-b html` / `-b text` authority.
**Depends on**: Phase 19 (shares the `desc_*` / signature rendering surface; sequenced after the
block-separation cluster so the separator idiom is settled before token-level spacing is tuned)
**Requirements**: FID-07, FID-08, FID-09
**Success Criteria** (what must be TRUE):

  1. The `desc_annotation` "class "/"exception " keyword prefix keeps its trailing space ("classsphinx.builders…" → "class sphinx.builders…") on every `py:class`/`py:exception`/`autoclass` — proven by a real-compile fixture (FID-07).
  2. C/C++ `desc_signature` and inline `c/cpp:expr` preserve all inter-token spaces (around `*`/`&`, type↔identifier, after the keyword prefix): "Py_ssize_tnitems" → "Py_ssize_t nitems" (FID-08).
  3. `field_list` `:type:`/`:default:` object-description fields render with colon-space and preserved field boundaries ("Type:int (a number)Default:42" → "Type: int (a number)  Default: 42") (FID-09).
  4. Each spacing fix ships or extends a real `typst.compile()` regression fixture (GATE-01); zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: 2/2 plans executed

Plans:
**Wave 1**

- [x] 20-01-PLAN.md — Reduce `visit_desc_sig_space`/`depart_desc_sig_space` to `pass`/`pass` (FID-07 `class `/`exception ` prefix + FID-08 all C/C++ inter-token spaces, one shared fix) + new real-compile render gate

**Wave 2** *(blocked on Wave 1; same-file `translator.py`)*

- [x] 20-02-PLAN.md — `depart_field_name` colon-space + `depart_field` inter-field double-space (FID-09 `:type:`/`:default:`, pinned "Type: int (a number)  Default: 42") + new render gate + update the one pre-existing locked colon assertion

### Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F)

**Goal**: The remaining smaller-root-cause fidelity findings — inline-literal right-margin overflow,
lost paragraph reflow, the codly config-wrapper leak, and meaning-bearing inline styling — are fixed as
the tail of the coherent translator series, each isolated to its own node handler.
**Depends on**: Phase 20 (sequenced last among the translator-fix phases; these are independent,
small-blast-radius edits that land after the two large clusters)
**Requirements**: FID-10, FID-11, FID-12, FID-13, FID-14
**Success Criteria** (what must be TRUE):

  1. A long run of inline `literal` roles wraps within the text margin instead of overflowing and clipping mid-token (clipping = content loss), kin to the fixed F12 — proven by a real-compile fixture (FID-10).
  2. reST soft/semantic line breaks inside a paragraph collapse to a single space instead of rendering as HARD line breaks (no ragged short lines), corpus-wide (FID-11).
  3. A `literal_block` with BOTH a `:caption:` AND nested in a `list_item` no longer leaks its codly config wrapper as visible text (`{ codly(number-format: none)` … `}`) (FID-12).
  4. External named `reference` hyperlinks render with distinguishing styling and correct boundary spacing — no stray space where adjacent inline text exists (FID-13); and `*`/`/` PEP 3102/570 separators render without injecting their hover-title text inline ("* (Keyword-only parameters separator …)" → "*") (FID-14).
  5. Every fix ships or extends a real `typst.compile()` regression fixture (GATE-01); zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: 3/3 plans executed

Plans:
**Wave 1**

- [x] 21-01-PLAN.md — FID-10 conditional leading ZWSP in visit_literal (inline-literal margin overflow, Cluster C) + FID-12 markup-aware list-item wrapper brace in visit_literal_block (codly config leak, Cluster E)

**Wave 2** *(blocked on Wave 1; same-file `translator.py`)*

- [x] 21-02-PLAN.md — FID-11 collapse intra-paragraph soft newline in visit_Text (paragraph reflow, Cluster D) + FID-14 narrow-scope abbr-title suppression in depart_abbreviation (`*`/`/` PEP separators, Cluster F)

**Wave 3** *(blocked on Wave 2; same-file `translator.py`)*

- [x] 21-03-PLAN.md — FID-13 external-link `show link:` styling in base.typ + boundary stray-space fix in visit_target (Cluster F)

### Phase 22: typstpdf Target-Name PDF Fix (Issue #117)

**Goal**: `sphinx-build -b typstpdf` names the compiled PDF after the `typst_documents` target name
(`manual.pdf`), not the source docname (`index.pdf`) — an independent `builder.py`/`pdf.py` fix that
does NOT share the translator root causes of Phases 19–21.
**Depends on**: Independent of Phases 19–21 (separate `builder.py`/`pdf.py` surface); sequenced here
after the translator series and before Release.
**Requirements**: PDF-01
**Success Criteria** (what must be TRUE):

  1. With `typst_documents = [('index', 'manual.typ', 'User Manual', 'Development Team')]`, `sphinx-build -b typstpdf` emits `manual.pdf` (the target name), not `index.pdf` (the source docname) (PDF-01).
  2. `TypstPDFBuilder.finish()` and both `write_doc()` sites derive the output filename from the `typst_documents` target element via one shared helper (`TypstBuilder._resolve_output_stem`), so the compiled `.pdf` and the emitted `.typ` always agree (Issue #117). (Corrected in Phase 22 Plan 03: the original wording asserted a pre-existing correct `.typ` mapping — false, since `doc_tuple[1]` was read nowhere in the package before this phase; per D-01 the phase scope is both filenames.)
  3. A regression test asserts the emitted PDF filename matches the configured `typst_documents` target (extends the builder / render-gate test pattern) and would fail against the pre-fix `index.pdf` behavior.
  4. Zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: 3/3 plans executed

Plans:

**Wave 1**

- [x] 22-01-PLAN.md — `TypstBuilder._resolve_output_stem` (D-03/D-04/D-06/D-07 normalization + degenerate-target fallback) and the three rewired output-path sites; `get_target_uri` deliberately unchanged

**Wave 2** *(both blocked on 22-01; no file overlap, run in parallel)*

- [x] 22-02-PLAN.md — GATE-01 real-compile render gate driven by `tests/roots/test-basic`: `output.typ`/`output.pdf` present AND `index.typ`/`index.pdf` absent
- [x] 22-03-PLAN.md — consumer + prose closure: corpus-gate assertion (D-12), renamed-master cross-reference proof, user-guide corrections, SC#2 correction, D-09 CHANGELOG hand-off

### Phase 22.1: typstpdf Compile-Root Alignment for Nested Masters (INSERTED)

**Goal**: `-b typstpdf` and `-b typst` resolve relative paths on the same basis, so a master at a
nested docname (`api/index`) compiles to PDF with its `#include()`s and images intact.
`compile_typst_to_pdf()` writes its temporary master copy to the **outdir root** (`pdf.py:140-149`,
`dir=root_dir` with `root_dir=self.outdir`), so `-b typstpdf` resolves relative paths from the outdir
root — while the translator emits **docname-relative** paths
(`translator.py:2928` `_compute_relative_include_path`, `translator.py:3043`
`_compute_relative_image_path`). The two coincide only when the master sits at the outdir root
(`index`), which is why every existing test and corpus passes. A nested master is already broken
today: `include("../foo.typ")` resolves against the outdir root and fails. The minimal fix is to
create the temporary file in the same directory as the master's own `.typ` (leaving `root` at
outdir); **no output file moves.**

**Depends on**: Phase 22 (same `builder.py`/`pdf.py` surface; sequenced after so the target-name fix
lands first and the two changes don't collide in `finish()`).
**Requirements**: PDF-02
**Success Criteria** (what must be TRUE):

  1. A regression fixture with a master at a nested docname (e.g. `typst_documents = [('api/index', 'api-reference', …)]`) that `#include()`s a sibling child document and references an image compiles to PDF under `-b typstpdf` with zero Typst errors, via a real `typst.compile()` (GATE-01 form) (PDF-02).
  2. That fixture **fails** against the pre-fix code (the test demonstrably reproduces the file-not-found break, not just passes vacuously).
  3. `-b typstpdf` and `-b typst` + manual `typst compile` resolve `#include()`/`image()` identically for the same project — no basis divergence remains between the two builders.
  4. Output locations are unchanged: `.typ` and `.pdf` still land at their docname-derived paths, and the Phase 22 target-name mapping still holds. Root-level masters (`index`) keep working exactly as before.
  5. Zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Out of scope**: aggregating master artifacts so multiple masters don't scatter across the build
tree — **dropped 2026-07-21** (owner decision; would have required moving output and re-basing
relative paths, and is not worth the churn). Also out of scope: `typst_output_dir` is registered in
`__init__.py:60` and documented in `docs/configuration.rst:255-269` but read nowhere — implement or
remove, tracked in the pending todo
`.planning/todos/pending/2026-07-21-dead-typst-output-dir-config.md`.

**Plans:** 4/4 plans complete

**Wave 1**

- [x] 22.1-01-PLAN.md — the fix: `compile_typst_file_to_pdf()` in `pdf.py` (no temp copy), `finish()` compiles the master's own `.typ` at its real location with `root_dir=self.outdir`, and the failure swallow becomes attempt-all-then-raise (`ExtensionError`); the two stale `tests/test_pdf_generation.py` cases repaired plus the D-08(b) path-basis unit test

**Wave 2** *(blocked on 22.1-01 — the gate is red until the fix lands)*

- [x] 22.1-02-PLAN.md — GATE-01 nested-master render gate: new `tests/fixtures/nested_master_render_gate/` (sole master at docname `api/index`, sibling `#include()`, upward `image("../logo.png")`) and `tests/test_nested_master_render_gate.py` covering SC#1 (real `-b typstpdf` compile), SC#2 (standing pre-fix-basis failure proof, D-08a) and SC#3 (`-b typst` output compiled by hand, D-09)

**Wave 3** *(gap closure — UAT `G-22.1-2`, SC#2 discharge rejected by the reviewer: 追加テストを要求する)*

- [x] 22.1-03-PLAN.md — test-only gap closure for `G-22.1-2`: add `test_sibling_include_fails_at_outdir_root_and_resolves_in_place`, which neutralizes ONLY the masking `../_template.typ` import and proves the sibling `include("usage.typ")` / `image("../logo.png")` basis divergence as an explicit red-then-green pair (red names `usage.typ` and the outdir-root searched path; green compiles the unmodified master in place), and tighten `test_outdir_root_compile_basis_still_fails` to its own single failure class so the two tests partition the failure space

**Wave 4** *(gap closure — UAT `G-22.1-4`, source CR-01 in `22.1-REVIEW.md`; owner ruled 今直す)*

- [x] 22.1-04-PLAN.md — production gap closure for `G-22.1-4`: `typsphinx/writer.py` computes the master's `_template.typ` import from the docname's own directory DEPTH to the outdir root instead of relativizing against a synthetic `"_template"` sentinel target (which collided with a real path component and emitted malformed stem-less references for masters under a `_template/` directory); pinned by a parametrized 7-case matrix (3 repaired + 4 byte-identical anti-regression fence rows) and a new GATE-01 real-compile gate over `tests/fixtures/template_named_dir_master/` (masters at depth 1 and depth 2 under a literal `_template` directory, both compiled for real with `root=outdir`). `typsphinx/translator.py` untouched; WR-01/WR-02 stay deferred to the backlog

### Phase 22.2: Dead Config-Value Sweep (INSERTED)

**Goal**: Two user-facing config values are registered and documented but never affect output —
`typst_output_dir` does nothing at all, and the entire `typst_package` (Typst Universe) path fails to
compile. Both are the *same* escape: the existing tests assert only that the value is **registered**
(`tests/test_config_other_options.py:141-179`) or that its name **appears in the docs**
(`tests/test_documentation_configuration.py:46`), which stays green while the feature is dead. Fix
both together so one regression fixture — asserting a config value **changes the emitted output** —
closes both escapes. Promoted from backlog 999.4 (which absorbed 999.3) on 2026-07-22; the owner
ruled it lands **inside v0.6.2**, before the release phase, so the `typst_output_dir` removal is
carried by the `[0.6.2]` CHANGELOG entry Phase 23 curates.

**Depends on**: Phase 22.1 (shares the `builder.py` / `writer.py` / `template_engine.py` surface that
22.1-04 just touched for the `_template.typ` import path — sequenced after so the two changes don't
collide). Independent of Phases 19–21 (translator-only).
**Requirements**: CONF-01, CONF-02, CONF-03
**Success Criteria** (what must be TRUE):

  1. `typst_output_dir` is gone from every surface: the registration (`__init__.py:60`), the `docs/configuration.rst` "Output Configuration" section (255-269) and its line in the full config example (348), the two registration-only tests (`tests/test_config_other_options.py:141-179`), the `required_configs` entry (`tests/test_documentation_configuration.py:46`), the commented-out lines in `examples/advanced/conf.py:102` and `examples/advanced/README.md:263`, and the mention in `CLAUDE.md:67`. A `### Removed` note is staged for the `[0.6.2]` CHANGELOG entry (CONF-01).
  2. A Sphinx project configured with `typst_package` alone (no `typst_template`) builds under `-b typstpdf` and compiles with **zero** Typst errors, via a real `typst.compile()` (GATE-01 form) — BUG-A..BUG-D below are each demonstrably fixed, and the fixture **fails** against the pre-fix code (CONF-02).
  3. The "Using Typst Universe Packages" examples in `docs/source/examples/advanced.rst` are corrected to match verified behavior — including the `advanced.rst:126-133` important-note (which currently blames combining `typst_package` with `typst_template`, not the observed cause) and the `advanced.rst:59` modern-cv example (CONF-02).
  4. A config→output regression fixture exists that asserts a config value **changes the emitted output**, covering both (1) and (2); registration-only assertions are treated as insufficient going forward (CONF-03).
  5. Zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**No deprecation period for `typst_output_dir`** — decided 2026-07-21 (owner). Sphinx silently ignores
unregistered `conf.py` variables (verified 2026-07-21: a bogus setting under `sphinx-build -W
--keep-going` produced no warning), so removal is behaviorally invisible; a deprecation warning would
only tell users to delete a line that has no effect either way. The config is also structurally
unimplementable as documented — `outdir` comes from the `sphinx-build` CLI argument and is managed by
Sphinx itself, which is why no other builder ships a `latex_output_dir` / `html_output_dir`.

**`typst_package` defect catalogue** (verified 2026-07-21 with a real `sphinx-build -b typst` + real
`typst.compile()`, typst 0.15.0; captured while checking a docs question — `typst_template_function =
{"name": "ieee"}` is *correct*). Full evidence and repro:
[`todos/pending/2026-07-21-verify-template-function-names-in-package-examples.md`](todos/pending/2026-07-21-verify-template-function-names-in-package-examples.md).

- **BUG-A (fatal):** `writer.py:151-153` always passes `template_file="_template.typ"`, so `#import "_template.typ": <func>` is always emitted — but `builder.py:371-374` early-returns from `_write_template_file()` whenever `typst_package` is set, so the file is never written → `file not found (searched at .../_template.typ)`. Fires with `typst_package` **alone**.
- **BUG-B:** `template_engine.py:186-191` injects `title`/`authors`/`date` unconditionally. `charged-ieee`'s `ieee()` takes no `date` → `unexpected argument: date` once BUG-A is worked around. Any package function not accepting all three is unusable.
- **BUG-C:** `typst_authors` / `typst_author_params` are silently ignored — `_format_authors_with_details()` (`template_engine.py:423`) is dead code with no callers. Output is a bare `authors: ("Name",)` string tuple, not the documented dicts.
- **BUG-D (docs):** `advanced.rst:59` modern-cv example is doubly wrong — `"name": "modern-cv"` → `unresolved import` (the entry function is `resume`, `lib.typ:193`), and `resume` accepts neither `title` nor `authors`, so BUG-B kills it anyway. Its `params` are `author`-dict fields, not `resume` arguments.

The "Custom Template Wrapping" path (`typst_template` pointing at a wrapper whose
`project(title:, authors:, date:, body)` absorbs the injected params) is the only package-consuming
route believed to work — unverified; confirming it is in scope for the fixture.

**Root cause of the escape:** no `typst.compile()` regression fixture covers the `typst_package` path,
so it shipped broken. Any fix must land one (GATE-01).

**Plans**: 5 plans (3 waves)

Plans:

**Wave 1** *(parallel — disjoint file sets)*

- [ ] 22.2-01-PLAN.md — CONF-01 dead-config sweep: delete the `typst_output_dir` and `typst_author_params` registrations (D-13, D-07 registration half), purge `typst_output_dir` from `docs/configuration.rst`, `examples/advanced/*`, `CLAUDE.md`, the two registration-only tests and the `required_configs` list, and stage the Phase 23 `### Removed` note so it names BOTH removals
- [ ] 22.2-02-PLAN.md — docs/example correction: delete the modern-cv package example rather than repair it (D-11), align the `advanced.rst` both-set important-note with post-D-03 behavior, and make `examples/charged-ieee/approach1` + its README describe a build that actually works (D-12) — including removal of the `bibliography: "refs.bib"` param, whose target file exists nowhere in the repo
- [ ] 22.2-03-PLAN.md — `template_engine.py` repair: hoist the four `@preview` imports + `codly-init` out of the `template_file` branch so every master gets them (D-02/BUG-F), stop package-path parameter injection at BOTH sites — the ctor `parameter_mapping` default AND the fill-if-missing back-fill (D-05/BUG-B), wire `typst_authors` as a native `list[dict]` through `map_parameters()` (D-07/BUG-C), invert parameter precedence so explicit config wins (D-08/BUG-E), and delete the `typst_author_params` ctor arg, legacy branch, both `getattr` call sites and its backward-compat test

**Wave 2** *(depends on 22.2-03 — shares `writer.py` / `builder.py`)*

- [ ] 22.2-04-PLAN.md — package/template routing: `writer.py` passes `template_file=None` when a package is configured alone so no `_template.typ` reference is emitted (D-01/BUG-A), `builder._write_template_file()`'s early return narrows to "package set AND template unset" with a once-per-build warning naming both configs and `typst_template` winning (D-03), the template+function combination is left first-class (D-04), and no new Typst-error-string coupling is introduced (D-06)

**Wave 3** *(depends on 22.2-02, 22.2-03, 22.2-04)*

- [ ] 22.2-05-PLAN.md — CONF-02/CONF-03 gates: new `tests/fixtures/package_only_config_gate/` (charged-ieee alone, colliding-key params) plus `tests/test_package_only_config_gate.py` with one named assertion per BUG-A/B/C/E/F, a real `-b typstpdf` compile, a standing pre-fix-basis failure proof trio (raises-only, no error-text matching), a config→output difference matrix (D-10), and `tests/test_examples_charged_ieee_gate.py` proving the shipped bundled sample builds end-to-end (D-12)

### Phase 22.3: typstpdf Builder Warning Hardening (INSERTED)

**Goal**: The two warnings the Phase 22.1 `/gsd-code-review` raised — deferred at the Wave 4 UAT gate
by owner ruling, then backlogged as 999.5 — are closed. `TypstPDFBuilder.finish()` no longer reports a
successful build while silently emitting no PDF for a configured master, and the nested-master render
gate stops depending on `typst-py`'s uncontracted error wording. Promoted from backlog 999.5 on
2026-07-22 (owner decision); lands **inside v0.6.2**, before the release phase, so any behavior change
is carried by the `[0.6.2]` CHANGELOG entry Phase 23 curates.
**Depends on**: Phase 22.2 (shares `typsphinx/builder.py` and the `tests/test_nested_master_render_gate.py`
/ config-fixture surface that 22.2 touches — sequenced after so the two changes don't collide).
Independent of Phases 19–21 (translator-only).
**Requirements**: WR-01, WR-02
**Success Criteria** (what must be TRUE):

  1. `sphinx-build -b typstpdf` on a project with a configured master whose `.typ` file was never generated no longer exits 0 with no PDF — the missing-master branch (`builder.py:895-897`, the bare `logger.warning(...); continue`) is aligned with the compile-failure path, and the `finish()` docstring's D-04 "no silent success" claim matches the implemented behavior exactly (WR-01).
  2. The same alignment decision is applied (or explicitly ruled out, with the reason recorded) for the adjacent malformed-`doc_tuple` skip around `builder.py:885-890`, so the two skip branches are not left asymmetric by accident (WR-01).
  3. Whether the fix is behavioral (a build failure) or documentary (weakening the docstring to "compile failures only") is decided at `/gsd-discuss-phase 22.3` — it is **open going in**. If behavioral, the user-visible change is staged for the Phase 23 `[0.6.2]` CHANGELOG entry (WR-01).
  4. `tests/test_nested_master_render_gate.py` (SC#2 / `G-22.1-2`) no longer asserts on `typst-py` error-message literals (`"escape"`, `"not found"`, `"usage.typ"`, `"_template.typ"`); the gate proves the same property through a contract the upstream owns (exit status / raised exception type / emitted-path inspection), so an upstream rewording cannot turn CI red without a real regression (WR-02).
  5. Whatever new behavior lands is pinned by a test that **fails against the pre-fix code**; zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

Source of record for both warnings:
[`todos/pending/2026-07-22-wr01-silent-missing-pdf-wr02-typst-error-substring-coupling.md`](todos/pending/2026-07-22-wr01-silent-missing-pdf-wr02-typst-error-substring-coupling.md)
(with the full repro and the open WR-01 decision), raised as `WR-01`/`WR-02` in
[`phases/22.1-typstpdf-compile-root-alignment-for-nested-masters/22.1-REVIEW.md`](phases/22.1-typstpdf-compile-root-alignment-for-nested-masters/22.1-REVIEW.md).
The same review's Critical `CR-01` was ruled 今直す and already closed inside Phase 22.1 as gap
`G-22.1-4` — it is **not** in this phase's scope.

**Plans**: TBD

Plans:

- [ ] TBD (enumerated at `/gsd-plan-phase 22.3`)

### Phase 23: v0.6.2 Release Prep + Regression-Gate Close

**Goal**: Prepare the v0.6.2 release — bump the version and curate the CHANGELOG — and close the
milestone on a full-corpus regression gate. **Prep-only:** the irreversible publish (tag `v0.6.2` →
`release.yml` → PyPI) is executed later at `/gsd-complete-milestone`, mirroring the v0.5.0 Phase 10 /
v0.6.1 pattern.
**Depends on**: Phases 19, 20, 21, 22, 22.1, 22.2, 22.3 (all fidelity, Issue #117, config-sweep, and
builder-warning fixes land before the version bump and the closing corpus re-run)
**Requirements**: (none — release/close phase; all v1 requirements are delivered by Phases 19–22.3)
**Success Criteria** (what must be TRUE):

  1. `pyproject.toml` version is bumped `0.6.1` → `0.6.2` as the sole version literal, and `uv.lock` is regenerated in lockstep (`uv sync --locked` green).
  2. `CHANGELOG.md` carries a curated `## [0.6.2]` entry (the single source for the eventual Release body) covering the 13 fidelity fixes (clusters A–F) and the Issue #117 target-name fix. Per the Phase 22 Plan 03 D-09 hand-off, the Issue #117 fix MUST be presented as a **user-visible output filename change** — users whose CI references a docname-named build artifact must be able to see it — not buried among internal fixes. The entry MUST also carry a `### Removed` section for the `typst_output_dir` deletion (Phase 22.2 CONF-01) and a fix note for the `typst_package`-path repair (CONF-02) — both user-visible.
  3. The full ~684-page Sphinx `doc/` corpus re-run through `-b typstpdf` is fatal-free (valid `%PDF` magic, 0 errors) and the `unknown_visit` catalogue is still clean — the closing regression gate, mirroring v0.6.1's GATE-03.
  4. The milestone invariant is confirmed held: zero new runtime dependencies, no `@preview` version bump, the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) untouched.
  5. Scope fence held — no tag, no PyPI publish, no GitHub Release in this phase (deferred to `/gsd-complete-milestone`).

**Plans**: TBD

Plans:

- [ ] TBD (enumerated at `/gsd-plan-phase 23`)

## Progress

**Execution Order:**
Active milestone (v0.6.2) phases execute in numeric order: 19 → 20 → 21 → 22 → 22.1 → 22.2 → 22.3 → 23

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Pin Runtime Dependencies to Known-Good | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 2. Verify the Green Baseline | v0.4.4 | 3/3 | Complete | 2026-07-04 |
| 3. Modernize Python Floor (3.10–3.13) | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 4. Refresh Dev Tooling | v0.4.4 | 4/4 | Complete | 2026-07-04 |
| 5. Durability Guardrails | v0.4.4 | 4/4 | Complete | 2026-07-05 |
| 6. Raise Runtime Pins + Python Floor | v0.5.0 | 1/1 | Complete | 2026-07-09 |
| 7. Bump @preview Packages + typst 0.15 (kai fix) | v0.5.0 | 1/1 | Complete | 2026-07-11 |
| 8. API & Test Compatibility (Sphinx 9 / docutils 0.22) | v0.5.0 | 3/3 | Complete | 2026-07-11 |
| 8.1 Admonition Rendering Fix (INSERTED) | v0.5.0 | 4/4 | Complete | 2026-07-11 |
| 9. Green CI Matrix + Smoke Test + Guardrails | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 10. Version-String Fix + v0.5.0 Release | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 11. Issue #114 Fatal Fixes + Graceful-Degrade Net | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 12. High-Volume Independent Node Handlers | v0.6.0 | 4/4 | Complete | 2026-07-12 |
| 13. Shared Dispatch-Point Changes (topic + line blocks) | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 14. Footnotes (doctree pre-pass) | v0.6.0 | 2/2 | Complete | 2026-07-12 |
| 15. Full-Corpus Validation | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 16. Silent-Drop Node Handlers + Length-Converter Refactor | v0.6.1 | 3/3 | Complete | 2026-07-16 |
| 17. Rendering-Fidelity Audit | v0.6.1 | 4/4 | Complete | 2026-07-19 |
| 18. Fidelity Fixes + Regression-Gate Close | v0.6.1 | 2/2 | Complete | 2026-07-19 |
| 19. Block Separation Fixes (Cluster A) | v0.6.2 | 3/3 | Complete    | 2026-07-20 |
| 20. Signature Token Spacing (Cluster B) | v0.6.2 | 2/2 | Complete    | 2026-07-20 |
| 21. Residual Fidelity Fixes (Clusters C/D/E/F) | v0.6.2 | 3/3 | Complete    | 2026-07-20 |
| 22. typstpdf Target-Name PDF Fix (Issue #117) | v0.6.2 | 3/3 | Complete    | 2026-07-21 |
| 22.1 typstpdf Compile-Root Alignment (INSERTED) | v0.6.2 | 4/4 | Complete    | 2026-07-22 |
| 22.2 Dead Config-Value Sweep (INSERTED) | v0.6.2 | 0/TBD | Not started | - |
| 22.3 typstpdf Builder Warning Hardening (INSERTED) | v0.6.2 | 0/TBD | Not started | - |
| 23. v0.6.2 Release Prep + Regression-Gate Close | v0.6.2 | 0/TBD | Not started | - |

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

**Reviewed 2026-07-22** (`/gsd-review-backlog`): 999.1 and 999.2 removed as delivered (999.1 -> Phases
19/20/21, 999.2 -> Phase 22, all Complete; source of record remains
[`milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`](milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md)
and [Issue #117](https://github.com/YuSabo90002/typsphinx/issues/117)). 999.3 was folded into 999.4 and
999.4 was **promoted into v0.6.2 as Phase 22.2** (owner decision) — the BUG-A..BUG-D evidence now lives
in the Phase 22.2 detail above. 999.5 added for the Phase 22.1 review warnings.

**Reviewed 2026-07-22 (second pass)** (`/gsd-review-backlog`): 999.5 was **promoted into v0.6.2 as
Phase 22.3** (owner decision) — the WR-01/WR-02 detail now lives in the Phase 22.3 detail above, and
the open WR-01 decision (behavioral failure vs. weakening the docstring) is deferred to
`/gsd-discuss-phase 22.3`.

**The backlog is currently empty.** New items land here as `999.x` entries.

---
*Roadmap created: 2026-07-04 · Reorganized: 2026-07-05 at v0.4.4 milestone close · v0.5.0 phases (6–10) added: 2026-07-09 · Reorganized: 2026-07-11 at v0.5.0 milestone close · v0.6.0 phases (11–15) added: 2026-07-11 · Reorganized: 2026-07-13 at v0.6.0 milestone close · v0.6.1 phases (16–18) added: 2026-07-13 · Reorganized: 2026-07-19 at v0.6.1 milestone close · Backlog seeded (999.1 — 13 medium/low fidelity findings, grouped A–F): 2026-07-20 · Backlog item 999.2 added (Issue #117 — typstpdf target-name bug): 2026-07-20 · v0.6.2 phases (19–23) added: 2026-07-20 · Backlog item 999.3 added (typst_package path broken end-to-end): 2026-07-21 · Phase 22.1 inserted (typstpdf compile-root alignment, PDF-02): 2026-07-21 · Backlog item 999.4 added and 999.3 merged into it (dead config-value sweep): 2026-07-21 · Backlog reviewed (/gsd-review-backlog): 999.1/999.2 removed as delivered, 999.4 (absorbing 999.3) promoted to Phase 22.2 inside v0.6.2, 999.5 added for the Phase 22.1 WR-01/WR-02 warnings: 2026-07-22 · Backlog reviewed again (/gsd-review-backlog): 999.5 promoted to Phase 22.3 inside v0.6.2, backlog now empty: 2026-07-22*
