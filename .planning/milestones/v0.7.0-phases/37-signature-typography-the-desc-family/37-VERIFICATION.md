---
phase: 37-signature-typography-the-desc-family
verified: 2026-08-01T00:00:00Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: null
---

# Phase 37: Signature Typography — the `desc_*` Family Verification Report

**Phase Goal:** An API signature reads as a signature rather than as a run of proportional bold
text — each sub-part carries its own typographic role, the return arrow is a real glyph, a long
fully-qualified signature stays inside the text margin, and a signature is neither split by a page
break nor buried in doubled blank lines.

**Verified:** 2026-08-01
**Status:** passed
**Re-verification:** No — initial verification

This is an initial verification (no prior `37-VERIFICATION.md` existed). All findings below are from
direct inspection of `typsphinx/translator.py` against `37-EMISSION-CONTRACT.md`, direct execution of
the test suite in this worktree (not taken from SUMMARY claims), and direct reading of git history to
confirm RED→GREEN provenance.

## Goal Achievement

### Observable Truths (ROADMAP SC#1..SC#5, cross-referenced with SIG-01..09)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | SC#1 / SIG-01,02,03,04,05 — each signature sub-part (`desc_name`, `desc_annotation`, `desc_addname`, delimiters, `desc_parameter`) emits a distinct, structurally-asserted monospace treatment (`strong(raw(...))` / `raw(...)` / `emph(raw(...))`), never bare `text(...)` | ✓ VERIFIED | Read `typsphinx/translator.py:5129-5310,5635-5700` — matches contract §5/§6 exactly. Ran `tests/test_signature_typography_gate.py` (15/15 pass) myself; confirmed RED-commit `6ca21d6` predates the fix commits (`f63fe8f`, `7674e3f`, `7c8dce0`) via `git log --oneline -- typsphinx/translator.py` between those hashes (zero translator commits between RED and fix) |
| 2 | SC#2 / SIG-06 — `desc_returns` renders a real arrow glyph (U+2192) in compiled-PDF extracted text, no ASCII `->` remaining anywhere in signature output | ✓ VERIFIED | `visit_desc_returns` (`translator.py:5055-5070`) emits `raw(" ") + raw("\u{2192}") + raw(" ")`. Ran `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` and `tests/test_signature_break_and_arrow_gate.py::TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent` myself — both assert `"→ int" in full_text` and `"->" not in full_text`; both pass |
| 3 | SC#3 / SIG-07 — a long fully-qualified signature stays inside the right text margin, overflow strategy derived from real corpus measurements | ✓ VERIFIED (with a documented judgment call — see note below) | `SHARED_INDENT_STEP = "2.5em"` (`translator.py:29`), `_escape_signature_text`'s ZWSP-after-`.` injection (`translator.py:1064-1091`), `par(hanging-indent:...)` wrapper (`translator.py:4962-4965`). Ran `tests/test_signature_overflow_render_gate.py` (6/6 pass), including `test_control_widest_segment_fits_column_before_and_after` (real-corpus GREEN control) |
| 4 | SC#4 / SIG-09 — a signature at a page boundary keeps its name, parameter list, and first body line on the same page | ✓ VERIFIED | `block(sticky: true, ...)` wrapper (`translator.py:4962-4965`). Ran `tests/test_signature_page_boundary_render_gate.py` (3/3 pass), including `test_primary_signature_and_body_share_a_page` |
| 5 | SC#5 / SIG-08 — sibling signatures and nested `desc` separated by exactly one break; phase's own exact-string blast radius migrated by hand, with a recorded census | ✓ VERIFIED | `depart_desc`'s emission-position marker (`translator.py:4798-4854`), correctly using "was anything emitted since" rather than a depth counter (confirmed by reading the code and its control test). Ran `tests/test_signature_break_and_arrow_gate.py` (9/9 pass) and `tests/test_desc_bodyless_concat_render_gate.py` (sibling control, passes). `37-TEST-CENSUS.md` census verified present with Bucket A/B/C tables, 10/8/4 counts, and a documented "honest miss" (two Phase-34 goldens) rather than a silently-corrected one |
| 6 | SIG-02 — `desc_addname` renders in regular-weight monospace, subordinate to the name | ✓ VERIFIED | `visit_desc_addname` is a deliberate no-op (`translator.py:5156-5165`); monospace comes "for free" from `in_signature_text`. `test_sig02_*` family (3 tests) pass |
| 7 | D-11 (folded, not a SIG id) — optional-group separator lands inside the bracket, matching Sphinx's own HTML rendering | ✓ VERIFIED | `depart_desc_optional` (`translator.py:5296-5310`) emits the guarded `+ raw(", ")` before the closing bracket. `TestD11SeparatorStructuralGate` and `TestD11SeparatorPdfGate` (4 tests) pass, including the `printf(fmt[, args[, more]])` non-regression control |
| 8 | Hand-derivation invariant (ROADMAP SC#5 / milestone invariant #4) — no expected string was regenerated from the new translator's own output | ✓ VERIFIED | Cross-checked git history: every RED commit (`6ca21d6`, `e846227`, `dab9a60`, `6113429`) predates the corresponding translator fix commit with zero intervening `typsphinx/translator.py` changes (verified via `git log --oneline <RED>..<GREEN> -- typsphinx/translator.py`). Searched all phase docs for "regenerated/pasted/copied from output" — every hit is a prohibition statement, none is a confession. `golden.typ`'s derivation matches contract §9's hand-worked block text exactly, byte for byte |

**Score:** 9/9 truths verified.

**Judgment call, made explicit per the verification brief's instruction (SC#3 / SIG-07):**
ROADMAP SC#3's literal wording says the long-signature RED fixture is "drawn from the real Sphinx
`doc/` corpus." The RED-triggering fixture is instead a synthetic 111-character dotted identifier
(`typsphinx.overflow.probe.deeply.nested.package.namespace.segment.alpha.beta.gamma.delta.OverflowProbeDocumenter`),
confirmed by reading `tests/fixtures/signature_overflow_render_gate/index.rst` and
`tests/test_signature_overflow_render_gate.py` directly. I independently confirmed the load-bearing
measurement behind this substitution: the full-corpus gate (`tests/test_corpus_gate.py -m slow`)
passes against 1,445 real Sphinx v9.1.0 `doc/` signatures with no overflow, and
`test_control_widest_segment_fits_column_before_and_after` keeps the real corpus's own worst case
(`sphinx.util.parsing.nested_parse_to_nodes`, 41-char qualname, 143pt widest token) as a
non-regression control, GREEN both before and after. A corpus-derived RED fixture is genuinely
impossible here — the untouched translator already passes it, proving nothing. This is a real,
independently-verifiable, transparently-documented measurement-driven amendment of SC#3's letter (not
its intent), not a quietly unmet criterion or a moved goalpost. I classify SC#3 as satisfied.

**Second judgment call, also made explicit per the brief (`EXPECTED_PAGE_COUNT_PRE_PHASE` 6→7):**
I read the test file directly (`tests/test_signature_page_boundary_render_gate.py:109,260-284`): the
assertion is `actual <= EXPECTED_PAGE_COUNT_PRE_PHASE` (a ceiling, not an exact-match), and
`test_primary_signature_and_body_share_a_page` — the actual SIG-09 assertion — passes both before and
after the re-pin. The re-pin is justified by a documented 0em–1.2em spacing sweep that found the page
count crosses 6→7 specifically between 0.85em–0.9em of restored spacing on a deliberately
almost-zero-slack 200pt-page fixture (built that way specifically to make the SIG-09 defect
reproduce). I independently ran the typography and break-and-arrow fixtures at normal A4 geometry
(via the passing render-gate tests) and confirm no page-count field asserts a change there. I classify
this as a legitimate re-derivation of a pinned integration threshold, not a moved goalpost — the
naming ("PRE_PHASE" now holding a post-phase value) is a genuine nit, already filed as
`.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md`.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/translator.py` — `visit/depart_desc_signature` | Composed `block(sticky: true, par(hanging-indent: 2.5em, ...))` wrapper (D-10, post-37-09 correction) | ✓ VERIFIED | `translator.py:4962-4965,4995` — byte-matches contract §3's amended text exactly |
| `typsphinx/translator.py` — `visit_desc_returns` | Real arrow glyph, three-expression form | ✓ VERIFIED | `translator.py:5070` — `raw(" ") + raw("\u{2192}") + raw(" ")` |
| `typsphinx/translator.py` — `depart_desc` | Emission-position marker suppressing the SIG-08 doubled break | ✓ VERIFIED | `translator.py:4851-4854` — matches contract §8; `self._desc_break_marker` initialised at `translator.py:176` |
| `typsphinx/translator.py` — `visit_desc_sig_name` | Three-rule D-05 discriminator | ✓ VERIFIED | `translator.py:5635-5698` — matches contract §5.2 exactly, including the deliberate non-discrimination on `pending_xref` |
| `typsphinx/translator.py` — `visit_Text` | Signature-text monospace branch with ZWSP injection | ✓ VERIFIED | `translator.py:1148-1177` — routes through `_escape_signature_text`, step order (escape then inject) matches contract §4 |
| `typsphinx/translator.py` — `SHARED_INDENT_STEP` | Single module-level constant, `"2.5em"`, D-08 | ✓ VERIFIED | `translator.py:29`, only two consumption sites, both inside `visit_desc_signature`'s docstring/wrapper |
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | 5 signature lines updated to the Phase-37 wrapper shape, rubric/list/bold sections byte-identical | ✓ VERIFIED | Read the file directly — matches contract §9's worked derivation exactly; rubric lines (`strong({text("Options")})`, `strong({text("Trailing Heading")})`) unchanged. `test_desc_rubric_decoupling_render_gate.py` (3/3) pass, including the byte-identity gate |
| `37-TEST-CENSUS.md` | Bucket A/B/C blast-radius census, finalised | ✓ VERIFIED | 194 lines, 10/8/4 bucket counts present, honest predictive-miss section (two Phase-34 goldens) not silently absorbed |
| `37-GATE-EVIDENCE-01..04.md`, `37-GATE-EVIDENCE-09.md`, `37-GATE-EVIDENCE.md` | RED provenance + consolidated verdict table | ✓ VERIFIED | Read all; RED evidence files contain verbatim `FAILED` pytest output, not paraphrased claims |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `visit_desc_sig_name` rule 3 (fallthrough) | `visit_reference`'s `link(...)` wrapping | `in_signature_text` flag read by `visit_Text` beneath an unmodified reference dispatch | ✓ WIRED | `test_sig04_resolved_xref_type_annotation_keeps_hyperlink` passes — confirmed a resolved type xref still emits `link(<label>, raw("Foo"))`, not a flattened string |
| `visit_desc_name`/`visit_desc_annotation` leaf guard | non-leaf C++ `desc_name` → nested `desc_sig_name` rule 1 | `all(isinstance(child, nodes.Text) ...)` guard, falling through instead of flattening via `node.astext()` | ✓ WIRED | `test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name` passes |
| `depart_desc`'s marker | `visit_desc`'s reset | `self._desc_break_marker` scalar, `len(self.body)` comparison | ✓ WIRED, with a documented residual risk | `test_sig08_*` (4 tests) pass. Code review WR-01 (below) identifies the marker is unguarded against non-table `self.body` buffer swaps (e.g. `visit_definition`) — filed as `.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md`, not fixed in this phase |
| `_emit_signature_leaf_wrapper` | `SkipNode`-based mutual exclusion in `visit_desc_sig_name` | Two sequential (not `elif`) `if` blocks, safe only because `SkipNode` aborts after the first match | ✓ WIRED, structurally implicit | Confirmed correct as written; code review IN-04 flags the implicit (exception-dependent) rather than structural mutual exclusion as a low-severity note, no fix required |

### Behavioral Spot-Checks (run directly by the verifier, not taken from SUMMARY claims)

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full default suite | `uv run pytest -m "not slow" -q` | `658 passed, 29 deselected in 43.85s` — I ran `uv run pytest -q` (no `-m` filter) and got `686 passed, 1 skipped` | ✓ PASS |
| Lint / format / types | `uv run black --check .` / `uv run ruff check .` / `uv run mypy typsphinx/` | all clean | ✓ PASS |
| Full-corpus `-b typstpdf` gate | `uv run python -m pytest tests/test_corpus_gate.py -m slow -v` | `1 passed, 1 skipped, 3 deselected in 12.88s` — `test_corpus_compiles_with_no_fatal_error` passed against 1,445 real Sphinx v9.1.0 `doc/` signatures | ✓ PASS |
| SIG-01..05 structural gate | `uv run python -m pytest tests/test_signature_typography_gate.py -v` | `15 passed` | ✓ PASS |
| SIG-06/08/D-11 gate | `uv run python -m pytest tests/test_signature_break_and_arrow_gate.py -v` | `9 passed` | ✓ PASS |
| SIG-07/09 gates | `uv run python -m pytest tests/test_signature_overflow_render_gate.py tests/test_signature_page_boundary_render_gate.py -v` | `9 passed` | ✓ PASS |
| golden.typ byte-identity + rubric/anchor controls | `uv run python -m pytest tests/test_desc_rubric_decoupling_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_desc_sig_space_render_gate.py tests/test_pdf_render_gate.py -v` | `35 passed` | ✓ PASS |
| RED-before-GREEN provenance | `git log --oneline <RED-hash>..<GREEN-hash> -- typsphinx/translator.py` for SIG-01 (`6ca21d6`..`f63fe8f`), SIG-06/08/D-11 (`e846227`..fixes), SIG-07/09 (`dab9a60`/`6113429`..`550b04a`) | zero translator.py commits precede the RED commit in each case — the RED evidence genuinely predates the fix | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| SIG-01 | 37-01, 37-06 | `desc_name` bold monospace | ✓ SATISFIED | `_emit_signature_leaf_wrapper(node, "strong")`, tests pass |
| SIG-02 | 37-01, 37-06 | `desc_addname` regular-weight monospace | ✓ SATISFIED | no-op handler + `in_signature_text` flag, tests pass |
| SIG-03 | 37-01, 37-06 | `desc_annotation` same treatment as `desc_name` | ✓ SATISFIED | identical `_emit_signature_leaf_wrapper` call, byte-identity test passes |
| SIG-04 | 37-01, 37-06 | parameters distinct from `desc_name` (per sub-part) | ✓ SATISFIED | `emph(raw(...))` for name, plain `raw(...)` for type/default, 3 parametrized tests pass |
| SIG-05 | 37-01, 37-07 | delimiters monospace | ✓ SATISFIED | five sites swapped to `raw(...)`, tests pass |
| SIG-06 | 37-02, 37-07 | real arrow glyph, no ASCII | ✓ SATISFIED | U+2192 confirmed present, ASCII absent, in compiled-PDF text |
| SIG-07 | 37-03, 37-06, 37-09 | no margin overflow | ✓ SATISFIED (see judgment-call note above) | hanging-indent + ZWSP, tests pass |
| SIG-08 | 37-02, 37-05 | exactly one break | ✓ SATISFIED | emission-position marker, tests pass |
| SIG-09 | 37-03, 37-06, 37-09 | no page-boundary split | ✓ SATISFIED (see judgment-call note above) | `sticky: true`, tests pass |

No orphaned requirements: `REQUIREMENTS.md`'s Phase 37 mapping (SIG-01..09, all "Complete") matches
exactly the union of `requirements:` fields across all 9 plan frontmatters.

### Anti-Patterns Found

Scanned `typsphinx/translator.py`'s Phase 37 diff for TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER markers,
empty implementations, and hardcoded stub returns.

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `typsphinx/translator.py:4851` | `if not self.in_table and self._desc_break_marker == len(self.body)` | Unguarded buffer-swap hazard (code review WR-01) | ⚠️ Warning | Filed as `.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md` — not a currently-demonstrated failure, a design-soundness gap for a currently-unexercised path (`desc` nested inside `definition`) |
| `typsphinx/translator.py` (3 sites) | `all(isinstance(child, nodes.Text) for child in node.children)` | Vacuous-true-on-empty leaf guard (code review IN-02) | ℹ️ Info | Low-severity; not observed to fire in any real fixture; would emit a harmless empty `raw("")` if it did |
| `tests/test_signature_page_boundary_render_gate.py:109` | `EXPECTED_PAGE_COUNT_PRE_PHASE = 7` | Misleading name (code review IN-03) | ℹ️ Info | Filed as todo, value itself is correct and documented in-comment |

No `TBD`/`FIXME`/`XXX` markers found anywhere in the phase's diff. No unreferenced debt markers. No
console.log-only or `return null`/`return {}` stub patterns found in the touched handlers — every
handler either emits real content or is a deliberate, documented no-op (`desc_addname`,
`desc_sig_keyword`, `desc_sig_space`, `desc_sig_punctuation`, `desc_sig_operator` — all intentionally
no-op per contract §4.3, monospace propagated via the flag, not via a dedicated handler).

### Human Verification Required

None outstanding. The phase's one Manual-Only Verification (RESEARCH.md Assumption A2 — the block
wrapper's non-spacing cosmetic defaults) was discharged 2026-08-01 with a verbatim owner response
("approved"), recorded in `37-08-SUMMARY.md` with a described before/after/current PDF comparison
methodology. I read that record directly; it is not a bare assertion of approval — it names the exact
PDFs shown (`/tmp/sig37-before/index.pdf`, `/tmp/sig37/index.pdf`,
`docs/_build/pdf/typsphinx.pdf`), states the checkpoint was a genuine `checkpoint:human-verify` task
(not auto-advanced), and quotes the owner's literal one-word response.

### Gaps Summary

No gaps found. All 9 SIG requirements plus the folded D-11 defect have working, tested implementations
that I independently confirmed by reading the code against the emission contract and by running the
relevant tests myself (not by trusting SUMMARY claims). The two items flagged for explicit scrutiny in
the verification brief — the SC#3 synthetic-vs-corpus fixture and the `EXPECTED_PAGE_COUNT_PRE_PHASE`
6→7 re-pin — are both legitimate, independently-verifiable, transparently-documented measurement-driven
decisions, not moved goalposts or hidden regressions. No evidence was found anywhere in the phase's
git history or planning documents of an expected string being fitted to the new translator's own
output rather than hand-derived from the contract. One warning-level code-review finding (WR-01, the
`_desc_break_marker` buffer-swap hazard) is real but narrow-scope (an unexercised path, not a
demonstrated failure) and is correctly filed as a follow-up todo rather than fixed or hidden.

---

*Verified: 2026-08-01*
*Verifier: Claude (gsd-verifier)*
