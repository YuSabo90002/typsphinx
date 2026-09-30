---
phase: 21-residual-fidelity-fixes-clusters-c-d-e-f
plan: 03
subsystem: rendering
tags: [typst, translator, template, hyperlinks, show-rule, pypdf, render-gate]

requires:
  - phase: 21-residual-fidelity-fixes-clusters-c-d-e-f (21-01, 21-02)
    provides: the FID-10/FID-11/FID-12/FID-14 fixes landing in earlier waves of the same phase
provides:
  - "A `#show link:` rule in the default `templates/base.typ` that colors + underlines external hyperlinks only (D-01/D-02)"
  - "A one-line `visit_target` fix that drops the stray leading `\\n` before an invisible `#label(...)` call (D-03)"
  - "The shared `external_link_style_render_gate` fixture + GATE-01 test module proving both halves fail pre-fix and pass post-fix"
affects: [21-residual-fidelity-fixes-clusters-c-d-e-f (phase-gate corpus/version-sync re-run after all three plans merge)]

tech-stack:
  added: []
  patterns:
    - "Template-tier `show` rule scoped by Typst's own `type(it.dest)` discriminator, avoiding any duplicate external/internal classification logic in the translator"
    - "Shared render-gate fixture exercising two independent fixes (styling + boundary) in one real compile"

key-files:
  created:
    - tests/fixtures/external_link_style_render_gate/conf.py
    - tests/fixtures/external_link_style_render_gate/index.rst
    - tests/test_external_link_style_render_gate.py
  modified:
    - typsphinx/templates/base.typ
    - typsphinx/translator.py

key-decisions:
  - "FID-13 styling landed in templates/base.typ (not per-node in translator.py) per D-01 -- Typst show rules are the template-tier equivalent of CSS."
  - "FID-13 boundary fix site is visit_target (~2801-2820), NOT visit_reference/depart_reference -- corrects 21-CONTEXT.md's provisional pointer per RESEARCH.md's real-compile root-cause finding."
  - "One shared fixture/test module covers both FID-13 halves (styling structural assert + boundary structural + pypdf adjacency assert), split into two atomic commits matching the two tasks."

requirements-completed: [FID-13]

coverage:
  - id: D1
    description: "The default template distinguishes external hyperlinks with color+underline (external URLs only via type(it.dest) == str); internal cross-references stay unstyled"
    requirement: "FID-13"
    verification:
      - kind: integration
        ref: "tests/test_external_link_style_render_gate.py::TestExternalLinkStyleRenderGate::test_typstpdf_show_link_rule_present_and_scoped_to_external"
        status: pass
    human_judgment: false
  - id: D2
    description: "A named external reference followed by a period renders with a single space, not a stray double space (D-03), verified via pypdf-extracted PDF text"
    requirement: "FID-13"
    verification:
      - kind: integration
        ref: "tests/test_external_link_style_render_gate.py::TestExternalLinkBoundaryRenderGate::test_typstpdf_boundary_no_leading_newline_before_label"
        status: pass
      - kind: integration
        ref: "tests/test_external_link_style_render_gate.py::TestExternalLinkBoundaryRenderGate::test_pdf_extracted_text_has_single_space_boundary"
        status: pass
    human_judgment: false
  - id: D3
    description: "Milestone invariant held: base.typ's four @preview version declarations stay byte-unchanged; test_preview_version_sync.py stays green; no new runtime dependency; pypdf stays test-only"
    requirement: "FID-13"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites"
        status: pass
      - kind: unit
        ref: "tests/test_preview_version_sync.py::test_all_four_packages_declared"
        status: pass
    human_judgment: false
  - id: D4
    description: "No regression to the non-markup-wrapped target-anchor path or internal-reference rendering"
    requirement: "FID-13"
    verification:
      - kind: integration
        ref: "tests/test_target_label_render_gate.py::TestTargetLabelRenderGate::test_typstpdf_emits_valid_anchors_and_produces_pdf"
        status: pass
      - kind: unit
        ref: "tests/test_inline_references.py (15 tests, full module)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-07-20
status: complete
---

# Phase 21 Plan 03: FID-13 External Link Styling + Boundary Summary

**A `show link:` rule in the default Typst template colors+underlines external hyperlinks only, and a one-line `visit_target` fix drops a stray leading newline that was doubling the space before a following period.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-07-20T13:01:00Z (approx, first branch-check bash call)
- **Completed:** 2026-07-20T13:56:13Z
- **Tasks:** 2
- **Files modified:** 5 (2 modified, 3 created)

## Accomplishments

- **FID-13 styling (D-01/D-02):** Added `#show link: it => { if type(it.dest) == str { underline(text(fill: blue, it.body)) } else { it } }` to `typsphinx/templates/base.typ`, inserted between the existing `#codly(languages: codly-languages)` line and `#let project(`. The translator's `visit_reference`/`depart_reference` emit `link(...)` completely unchanged — external references produce `link("url", ...)` (a `str` dest, styled), internal cross-references produce `link(<label>, ...)` (a `label` dest, unstyled). Verified structurally (D-10, color+underline is not pypdf-extractable): the rule's presence is asserted in the build's rendered `_template.typ`, and a real `typst.compile()` produces a valid `%PDF`.
- **FID-13 boundary (D-03):** Root-caused (per RESEARCH.md, confirmed again this session via a real pre-fix compile) to `visit_target`'s `_in_reference_with_target` branch, which prepended `f'\n#label("{label_id}")'` before the invisible label-attachment call. A newline inside Typst MARKUP mode renders as a visible space; combined with the genuinely-source-present following space (the RST `` `text <url>`_ . `` boundary), this produced a stray double space — exactly the audit catalogue's "RTD  PDF" symptom. Fix: drop the leading `\n`, since the preceding content is always the closing `)` of the reference's `link(...)` call, so `)#label(` is syntactically unambiguous with no separator needed.
- **Shared GATE-01 fixture:** `tests/fixtures/external_link_style_render_gate/` contains one document with a named external hyperlink (`` `external reference <https://example.com/>`_ ``, sentinel-prefixed) immediately followed by a period, PLUS a same-document internal `:ref:` reference — proving D-02's external-vs-internal scoping and D-03's boundary fix in a single real compile.
- Confirmed both directions via real `sphinx-build -b typstpdf` compiles this session: pre-fix, the extracted PDF text read `"FIDTHIRTEENSENTINEL external reference  ."` (two spaces); post-fix it reads `"FIDTHIRTEENSENTINEL external reference ."` (one space). The styling structural assert (`show link:` rule presence) also confirmed FAILING against the pre-fix `base.typ` before the edit was applied.

## Task Commits

Each task was committed atomically:

1. **Task 1: FID-13 styling — `#show link:` rule in base.typ + shared fixture + structural gate** - `636eea3` (feat)
2. **Task 2: FID-13 boundary — drop leading `\n` before `#label(...)` in visit_target + pypdf boundary gate** - `2a598b9` (fix)

**Plan metadata:** SUMMARY.md commit follows (docs commit, this executor).

## Files Created/Modified

- `typsphinx/templates/base.typ` — new `#show link:` rule (external-URL-only color+underline), inserted between the existing codly config line and `#let project(`; the four `@preview` version declarations are byte-unchanged.
- `typsphinx/translator.py::visit_target` — the `_in_reference_with_target` branch drops the leading `\n` before `#label(...)` (one-line change, plus a comment explaining the markup-mode newline hazard).
- `tests/fixtures/external_link_style_render_gate/conf.py` — new minimal Sphinx project (`typst_documents` master-doc config).
- `tests/fixtures/external_link_style_render_gate/index.rst` — new fixture document: a named external hyperlink (sentinel-prefixed link text) immediately followed by a period, plus a same-document `:ref:` internal reference.
- `tests/test_external_link_style_render_gate.py` — new GATE-01 module: `TestExternalLinkStyleRenderGate` (structural styling assert, Task 1) and `TestExternalLinkBoundaryRenderGate` (structural + pypdf boundary asserts, Task 2).

## Decisions Made

- Reused `blue` as the link color (Typst's built-in named color) per RESEARCH.md's Assumption A3 — D-01 specifies "color + underline" without pinning an exact value; this is a discretionary, cosmetic-only choice.
- Split the shared render-gate module into two commits (Task 1: styling assert only; Task 2: adds the boundary test class) so each commit's diff matches its task's scope exactly, rather than writing all three test methods in one commit.
- Kept the internal-reference fixture section minimal (a single `.. _fidthirteeninternalsentinel:` target + `:ref:` back-reference) rather than adding a second external link, since one external + one internal reference is sufficient to prove D-02's `type(it.dest)` scoping.

## Deviations from Plan

None - plan executed exactly as written. Both fix sites, the fixture shape, and the verification split (structural-only for styling per D-10, structural + pypdf for boundary per D-09) matched the plan's `must_haves`/`key_links` exactly, including the corrected line-number pointer to `visit_target` (not `visit_reference`) already established in the plan and RESEARCH.md.

## Issues Encountered

- 3 pre-existing, environment-caused failures in `tests/test_examples_basic.py` (`test_build_typst_succeeds`, `test_build_generates_typ_file`, `test_generated_typ_is_valid`) surfaced during the full-suite sanity run — these invoke `subprocess.run(["uv", "run", "sphinx-build", ...])` directly rather than `sys.executable -m sphinx`, which is the documented NixOS-sandbox PATH-shadowing hazard (project MEMORY.md). This file is not in this plan's `files_modified`, was not touched this session, and the failure is unrelated to the FID-13 changes — confirmed out of scope per the deviation rules' scope boundary (pre-existing failure in an unrelated file). Not fixed; noted here for visibility.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FID-13 (the final finding of Phase 21's Cluster C/D/E/F series) is complete. All three plans (21-01, 21-02, 21-03) covering FID-10 through FID-14 have landed in this worktree.
- The phase-level standing regression gates (`tests/test_corpus_gate.py -m slow` and `tests/test_preview_version_sync.py`) are described in the plan as run "once at end of phase, after all three plans merge" — this is the orchestrator's/merge-time responsibility, not re-run individually by this executor; `test_preview_version_sync.py` was re-confirmed green in this session as part of Task 1's acceptance criteria.
- No blockers for phase completion.

---

*Phase: 21-residual-fidelity-fixes-clusters-c-d-e-f*
*Completed: 2026-07-20*

## Self-Check: PASSED

- FOUND: typsphinx/templates/base.typ
- FOUND: typsphinx/translator.py
- FOUND: tests/fixtures/external_link_style_render_gate/conf.py
- FOUND: tests/fixtures/external_link_style_render_gate/index.rst
- FOUND: tests/test_external_link_style_render_gate.py
- FOUND commit: 636eea3
- FOUND commit: 2a598b9
