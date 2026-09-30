---
phase: 37
slug: signature-typography-the-desc-family
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-01
---

# Phase 37 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `37-RESEARCH.md` § "Validation Architecture" (all figures measured 2026-08-01).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`), plus the project's own GATE-01 real-`typst.compile()` render-gate pattern |
| **Config file** | `pyproject.toml`; the render-gate pattern needs no separate config — plain pytest fixtures calling `sys.executable -m sphinx` + `typst.compile()`, e.g. `tests/test_pdf_render_gate.py::_run_sphinx_build_typst` |
| **Quick run command** | `uv run pytest tests/test_translator.py -k "desc or signature" -x` |
| **Full suite command** | `uv run pytest -m "not slow"` |
| **Estimated runtime** | quick ~5s · full suite ~90s · `-m slow` full-corpus gate several minutes |

**Environment constraint (non-negotiable):** new fixtures MUST use the `sys.executable -m sphinx`
pattern, never `subprocess.run(["uv", "run", "sphinx-build", ...])` — the latter hits the NixOS
stub-ld hazard and false-fails. Executors running in isolated worktrees must provision with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and then
`for t in uv ruff; do ln -sf "$(command -v $t)" ".venv/bin/$t"; done` before any test run.

**Measurement method (from research):** `pypdf`'s `extract_text(visitor_text=...)` was found
unreliable for per-glyph x/y positions on Typst-generated PDFs in this sandbox (returns `x=0, y=0`).
Geometric assertions must use Typst-side `context measure(...)` / `context layout(size => ...)`
probes compiled through `typst.compile()`, cross-checked with plain `pypdf.extract_text()` for
content and ordering. Available production column width, measured this way: **453.54pt**.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_translator.py -k "desc or signature" -x`
  (fast, no `typst.compile()`)
- **After every plan wave:** `uv run pytest -m "not slow"` — includes every GATE-01 real-compile
  render gate, excludes the `@pytest.mark.slow` full-corpus gate
- **Before `/gsd-verify-work`:** `uv run pytest -m "not slow"` green, PLUS an explicit
  `uv run pytest tests/test_corpus_gate.py -m slow` full-corpus run (milestone standing practice)
- **Max feedback latency:** ~5 seconds for the per-commit sample

---

## Phase Requirements → Sampling Map

Every SIG requirement is sampled by an **observable signal**, not by "the test passes". The signal
column names what physically proves the requirement, so a degenerate implementation cannot satisfy it.

| Req ID | Behavior | Observable signal | Test type | File | Exists? |
|--------|----------|-------------------|-----------|------|---------|
| SIG-01 | `desc_name` emits `strong(raw(...))` | emitted `.typ` contains `strong(raw(` at the name site — structural, not a `text(...)` match | unit + render-gate | `tests/test_translator.py::test_desc_with_annotation_and_name` | ✅ needs rewrite |
| SIG-02 | `desc_addname` emits `raw(...)` with **no** enclosing `strong()` | emitted `.typ`: addname site is `raw(` and is not inside `strong(` | unit + render-gate | `tests/test_translator.py` (new case) | ❌ Wave 0 |
| SIG-03 | `desc_annotation` emits the **same** `strong(raw(...))` as `desc_name` | emitted `.typ`: annotation and name sites are byte-identical in wrapper shape | unit + render-gate | rewritten `test_desc_with_annotation_and_name` | ✅ needs rewrite |
| SIG-04 | Per-sub-part distinct treatment inside `desc_parameter` (D-03: per sub-part, **never** one blanket check) | emitted `.typ`: param name → `emph(raw(`; type annotation and default → `raw(` without `emph` | unit, parametrized over all 8 measured parameter shapes | new parametrized test | ❌ Wave 0 |
| SIG-05 | Delimiters `(` `)` `,` `=` `:` and `desc_optional`'s `[` `]` emit `raw(...)` | emitted `.typ`: each delimiter site is a `raw(` call, no bare `text(` remains in the parameter list | unit + render-gate | rewritten `test_desc_parameterlist` + new `desc_optional` case | ⚠️ partial |
| SIG-06 | `desc_returns` emits a real arrow glyph | compiled-PDF `pypdf` text: `'→' in text` **and** `'->' not in text` anywhere in signature output | render-gate (compiled PDF) | `tests/test_pdf_render_gate.py::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` | ✅ needs rewrite |
| SIG-07 | Long dotted signature stays inside the right text margin | Typst `context measure(...)` width of the widest unbroken token < 453.54pt column width, on a **synthetic ~90+ char identifier** fixture; real-corpus worst case (311-char sig / 41-char qualname / 143pt token) as a non-regression control | new render-gate | `tests/test_signature_overflow_render_gate.py` | ❌ Wave 0 |
| SIG-08 | Exactly one break between sibling signatures and around nested `desc` | emitted `.typ`: `output.count("parbreak()")` equals the hand-derived expected count for a `py:class::` + nested `py:method::` fixture | render-gate + structural `.typ` assertion | extends `tests/test_desc_bodyless_concat_render_gate.py` pattern | ❌ Wave 0 |
| SIG-09 | Signature + parameter list + first body line share a page | `pypdf` **per-page** text containment under a forced page-break fixture (`#set page(height:, margin:)` + `block(sticky:)`) | render-gate (compiled PDF, per-page) | `tests/test_signature_page_boundary_render_gate.py` | ❌ Wave 0 |
| D-11 (no SIG id) | Optional-group separator lands **inside** the bracket, matching Sphinx HTML `[timeout, ]` | emitted `.typ` and compiled-PDF text both show `[timeout, ]**kwargs`, not `[timeout]**kwargs`; expressions explicitly `+`-joined | unit + render-gate | own fixture (must NOT be smuggled into a SIG-05 assertion) | ❌ Wave 0 |

**GATE-01 RED requirement (milestone invariant #4):** every assertion above must be recorded RED
against the pre-phase translator. Because the current output *compiles fine*, RED must come from a
**structural** assertion (monospace primitive present / `text(` absent / break count / glyph identity
/ page containment), never from a compile failure.

**SC#5 binding constraint:** expected strings are **hand-derived**. Copying whatever the new code
emits into a golden file is forbidden by milestone invariant #4 and voids the phase's evidence.

---

## Per-Task Verification Map

*Finalised by `37-08` Task 2 (phase closeout), against every plan's own SUMMARY and task commit.*
One row per task across the eight executed plans (`37-01`..`37-07`, `37-09` — `37-08` is this
closeout plan itself and is not a row in its own map).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|--------------------|-------------|--------|
| 37-01 T1 | 37-01 | 1 | SIG-01..05 (fixture) | — | N/A | integration | `sphinx-build -b typst` exits 0, `.typ` non-empty | ✅ | ✅ green |
| 37-01 T2 | 37-01 | 1 | SIG-01..05 | T-37-01 (escaping reuse) | mitigate | unit | `pytest tests/test_signature_typography_gate.py -v` | ✅ | ✅ green (14 RED, as intended) |
| 37-01 T3 | 37-01 | 1 | SIG-01..05 | — | N/A | other | evidence file + `black`/`ruff` on the new module | ✅ | ✅ green |
| 37-02 T1 | 37-02 | 1 | SIG-06/SIG-08/D-11 (fixture) | — | N/A | integration | `sphinx-build -b typst`, `.typ` non-empty | ✅ | ✅ green |
| 37-02 T2 | 37-02 | 1 | SIG-06/SIG-08/D-11 | T-37-01 | mitigate | unit + integration | `pytest tests/test_signature_break_and_arrow_gate.py -v` | ✅ | ✅ green (5 RED / 4 control-green, as intended) |
| 37-02 T3 | 37-02 | 1 | SIG-06/SIG-08/D-11 | — | N/A | other | evidence file + lint | ✅ | ✅ green |
| 37-03 T1 | 37-03 | 1 | SIG-07 (fixture + gate) | — | N/A | unit | `pytest tests/test_signature_overflow_render_gate.py -v` | ✅ | ✅ green (3 RED / 2 control-green, as intended) |
| 37-03 T2 | 37-03 | 1 | SIG-09 (fixture + gate) | — | N/A | unit | `pytest tests/test_signature_page_boundary_render_gate.py -v` | ✅ | ✅ green (1 RED / 2 guard-green, as intended) |
| 37-03 T3 | 37-03 | 1 | SIG-07/SIG-09 | — | N/A | other | evidence file + lint | ✅ | ✅ green |
| 37-04 T1 | 37-04 | 2 | SC#5 (census) | — | N/A | other | `test -s 37-TEST-CENSUS.md && grep -qi "must not touch"` | ✅ | ✅ green |
| 37-04 T2 | 37-04 | 2 | SIG-01..06 (migration) | T-37-01 | mitigate | unit + integration | `pytest tests/test_translator.py::test_rubric_rendering tests/test_rubric_option_concat_render_gate.py -v` | ✅ | ✅ green |
| 37-04 T3 | 37-04 | 2 | SIG-03 (golden.typ) | T-37-01, T-37-04 | mitigate | unit | plan's own verify literal `"7/7"` **fails as written** (actual diff is `9/9`, correctly derived — see `37-GATE-EVIDENCE-04.md` §1); functional outcome (hand-derived RED, correctly scoped diff) is green | ✅ | ✅ green (verify-command discrepancy reported, not silently forced) |
| 37-05 T1 | 37-05 | 2 | SIG-08 | — | N/A | unit | `pytest tests/test_signature_break_and_arrow_gate.py tests/test_desc_bodyless_concat_render_gate.py -v` | ✅ | ✅ green |
| 37-05 T2 | 37-05 | 2 | SIG-08 | — | N/A | other | `pytest -m "not slow" -q; black --check .; ruff check .; mypy typsphinx/` | ✅ | ✅ green |
| 37-06 T1 | 37-06 | 3 | SIG-07/SIG-09 (wrapper) | T-37-11 (font shadow) | mitigate | integration | `pytest tests/test_signature_page_boundary_render_gate.py tests/test_desc_signature_anchor_render_gate.py tests/test_signature_break_and_arrow_gate.py -v` | ✅ | ✅ green |
| 37-06 T2 | 37-06 | 3 | SIG-02/SIG-07 (monospace + ZWSP) | T-37-01 | mitigate | integration | `pytest tests/test_signature_overflow_render_gate.py tests/test_deflist_term_inline_children_gate.py tests/test_confval_field_body_render_gate.py -v` | ✅ | ✅ green |
| 37-06 T3 | 37-06 | 3 | SIG-01/03/04 (D-05) | T-37-07 (hyperlink preservation) | mitigate | unit + other | `pytest tests/test_signature_typography_gate.py -v; black --check .; ruff check .; mypy typsphinx/` | ✅ | ✅ green |
| 37-07 T1 | 37-07 | 4 | SIG-05 | T-37-01 | mitigate | unit | `pytest tests/test_signature_typography_gate.py tests/test_desc_signature_concat_render_gate.py -v` | ✅ | ✅ green |
| 37-07 T2 | 37-07 | 4 | D-11 | T-37-09 (bracket count) | mitigate | unit + integration | `pytest tests/test_signature_break_and_arrow_gate.py tests/test_pdf_render_gate.py -k "desc_signature or D11 or optional" -v` | ✅ | ✅ green |
| 37-07 T3 | 37-07 | 4 | SIG-06 | — | N/A | other | `pytest -m "not slow" -q; black --check .; ruff check .; mypy typsphinx/` | ✅ | ✅ green |
| 37-09 T1 | 37-09 | 5 | SIG-07/SIG-09 (contract amendment) | — | N/A | manual | re-read §3/§9 for identical wrapper text | ✅ | ✅ green |
| 37-09 T2 | 37-09 | 5 | SIG-01..04/07/09 (wrapper fix) | T-37-01 | mitigate | integration | `pytest tests/test_signature_typography_gate.py tests/test_signature_page_boundary_render_gate.py tests/test_signature_overflow_render_gate.py tests/test_signature_break_and_arrow_gate.py tests/test_desc_rubric_decoupling_render_gate.py tests/test_desc_bodyless_concat_render_gate.py -q` | ✅ | ✅ green |
| 37-09 T3 | 37-09 | 5 | SIG-09 (Phase 34 goldens) | — | N/A | integration + other | `pytest -q --tb=short` (whole suite) | ✅ | ✅ green — first fully-green whole-suite result of the phase |
| GAP-1 | validate-phase audit | — | Multi-signature spacing compounding (T-37-08 residue) | T-37-08 | mitigate | integration (real compile) | `uv run pytest tests/test_signature_typography_multi_signature_page_count_gate.py -v` | ✅ | ✅ green — added 2026-08-01 by this audit |

*Status legend: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. Rows 37-01…37-09 were independently
re-confirmed green in `37-08` Task 1's whole-suite run (`658 passed, 29 deselected`), and again by
this audit on the main checkout at the same count before GAP-1 was added (`659 passed` after).*

---

## Wave 0 Requirements

- [x] `tests/test_signature_overflow_render_gate.py` — SIG-07 (synthetic overflow RED fixture plus
      the real-corpus non-regression control; research Pitfall 2 established that the real corpus does
      **not** overflow at production width, so the corpus alone cannot produce RED) — shipped `37-03`
      Task 1, RED confirmed `37-GATE-EVIDENCE-03.md`, GREEN at `37-06`
- [x] `tests/test_signature_page_boundary_render_gate.py` — SIG-09 (forced page-break fixture using
      the `#set page(height:, margin:)` + `block(sticky:)` pattern proven this session) — shipped
      `37-03` Task 2, RED confirmed `37-GATE-EVIDENCE-03.md`, GREEN at `37-06`, page-count baseline
      re-measured at `37-09`
- [x] A parametrized `desc_parameter` sub-part unit test covering all **8** parameter shapes measured
      in RESEARCH.md's D-05 table (SIG-04) — no existing test covers the union-type, resolved-xref, or
      quoted-forward-ref cases — shipped `37-01` Task 2 (`test_sig04_*` family), GREEN at `37-06`
- [x] A nested-`desc` fixture in the `test_desc_bodyless_concat_render_gate.py` style proving SIG-08's
      "exactly one break" for `py:class::` + `py:method::` nesting (the existing fixture covers
      body-less *sibling* desc, not *nested* desc) — shipped `37-02` Task 1
      (`signature_break_and_arrow_gate`), GREEN at `37-05`
- [x] A D-11 optional-group-separator fixture, separate from any SIG-05 assertion — shipped `37-02`
      Task 1/2, GREEN at `37-07`

*Framework install: not required — pytest, `typst-py` 0.15.0 and `pypdf` 6.14.2 are all present.*
*All five Wave 0 requirements delivered and later flipped GREEN — confirmed in this plan's Task 1
whole-suite run.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Status |
|----------|-------------|------------|--------------------|--------|
| Visual confirmation that `block()`'s non-spacing cosmetic defaults (`inset`, `fill`, `stroke`) introduce no visible artifact | D-10 / Assumption A2 | Automated assertions cover spacing (measured) and page containment, but not "does it look wrong" | Build the phase's own GATE-01 fixture to PDF and eyeball the signature block against the pre-phase render | **Discharged 2026-08-01.** Owner reviewed `/tmp/sig37-before/index.pdf` (phase-start), `/tmp/sig37/index.pdf` (current), and `docs/_build/pdf/typsphinx.pdf` (the project's own API pages) against `37-08` Task 3's checkpoint. Verbatim verdict: **"approved"**. See `37-08-SUMMARY.md` for the full record. |

*Every other phase behavior has automated verification. Note this row is narrower than it may look:
the owner already saw a before/after/final rendering comparison during `37-09`'s own gap-closure
decision (2026-08-01) and approved fixing the spacing defect inside the phase — but that comparison
did not put RESEARCH.md Assumption A2's specific question (do the wrapper's NON-spacing cosmetic
defaults introduce any artifact) to the owner. `37-08` Task 3 asks exactly that narrower, still-open
question.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (23/23 task rows in the Per-Task
      Verification Map carry an automated or explicitly-manual verify method; `37-09` Task 1's manual
      re-read verify is the one exception, immediately followed by two automated-verify tasks)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (the only manual-verify
      task, `37-09` T1, is bracketed by automated-verify tasks on both sides)
- [x] Wave 0 covers all ❌ references above (all five Wave 0 requirements shipped and later flipped
      GREEN — see the checked boxes above)
- [x] No watch-mode flags (every command in the Per-Task Verification Map and this plan's own Task 1
      is a single, non-watching invocation)
- [x] Feedback latency < 10s for the per-commit sample (the per-commit sample command,
      `pytest tests/test_translator.py -k "desc or signature" -x`, completes in ~1-2s on this
      worktree — well under the 10s bar; the full `-m "not slow"` suite itself completes in 43.85s,
      which is the *phase-boundary* sample, not the per-commit one)
- [x] `nyquist_compliant: true` set in frontmatter — flipped 2026-08-01, after the owner's
      "approved" verdict on `37-08` Task 3's checkpoint discharged the phase's one remaining
      Manual-Only Verification row. Every mechanical box above was already checked before this one;
      this was the last outstanding item.

**Approval:** approved — owner's verbatim response to `37-08` Task 3, 2026-08-01: "approved". Full
record in `37-08-SUMMARY.md`.

---

## Validation Audit 2026-08-01

| Metric | Count |
|--------|-------|
| Gaps found | 1 |
| Resolved | 1 |
| Escalated | 0 |

Run by `gsd-nyquist-auditor` (haiku) under `/gsd-validate-phase 37`, State A.

### What was audited

Every test file and node ID named in the Per-Task Verification Map was confirmed to exist, and the
suite was re-run on the main checkout: `uv run pytest -q -m "not slow"` → **658 passed, 29 deselected
in 42.82s**, byte-matching the count `37-08` Task 1 recorded. SIG-01…SIG-09 and D-11 all classify
COVERED. One requirement had no automated sampling at all.

### GAP-1 — multi-signature spacing compounding (MISSING → COVERED)

Surfaced by the security audit the same day (`37-SECURITY.md`, threat T-37-08). Phase 37 moved the
`desc_signature` wrapper from an explicitly pinned spacing value to inheriting Typst's own default
(Wave 3 zeroed `above`/`below`; Wave 4 reversed the zeroing because it made signatures overlap their
bodies). The pin T-37-08 named, `test_page_count_does_not_inflate`, had its baseline re-pinned 6→7
in the same plan — moving its firing point to ≥16em — and its fixture holds exactly one signature,
so it structurally cannot measure compounding at all.

**Filled by** `tests/test_signature_typography_multi_signature_page_count_gate.py::TestSignatureTypographyMultiSignaturePageCountGate::test_multi_signature_document_page_count_at_real_geometry`
— builds `tests/fixtures/signature_typography_gate` (13 signature wrappers) through
`sphinx-build -b typst`, compiles with `typst.compile()`, and asserts 4 A4 pages, with a
wrapper-count guard so it cannot pass silently on a changed fixture. Baseline re-derived
independently by both the auditor and the orchestrator: 13 wrappers → 4 pages.

**Measured sensitivity (orchestrator sweep, variant-swap on the emitted `.typ`, 2026-08-01):**

| per-side spacing | shipped | 0pt | 0.5em | 1.0em | 2.0em | 2.2em | 2.3em | 3.0em | 6em |
|---|---|---|---|---|---|---|---|---|---|
| pages | 4 | 4 | 4 | 4 | 4 | 4 | **5** | 5 | 6 |

The gate fires at **≥2.3em** per side — roughly 7× tighter than the ≥16em guard it supplements, and
it is the only assertion in the suite that measures compounding across more than one signature.

The auditor's returned claim that 1.0em "would inflate to 5+ pages" is **not correct** — measured,
1.0em still renders 4 pages. The test's docstring was corrected to carry the sweep above instead of
that estimate, so the file does not repeat the overstated-sensitivity problem this same day's
security audit flagged in `37-09`'s own justification text.

**What the gate does not catch, and what does:** the collapse direction (`above: 0pt, below: 0pt`,
the Wave-3 overlap defect) still renders 4 pages, so page count cannot see it. It is pinned
automatically elsewhere — the Phase 34 MATH-02 golden
`tests/fixtures/inline_math_pdf_text_mitex.golden.txt:19` keeps `math_inline_default` on its own
extracted-text line and re-merges the moment the overlap returns, and the wrapper string itself is
byte-pinned by `desc_rubric_decoupling_render_gate/golden.typ` and
`tests/test_translator.py::test_desc_signature_rendering`. The residual exposure the new gate
targets is an upstream `typst-py` default-spacing change, which no in-repo string pin would catch
and which `drift.yml` re-resolves weekly.

**Post-audit suite:** `uv run pytest -q -m "not slow"` → **659 passed, 29 deselected in 43.24s**.
`black --check` and `ruff check` pass on the new file.
