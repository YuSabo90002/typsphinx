---
phase: 21-residual-fidelity-fixes-clusters-c-d-e-f
verified: 2026-07-20T00:00:00Z
status: passed
score: 5/5 must-haves verified (requirements) / 20/20 plan-level truths verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F) Verification Report

**Phase Goal:** The remaining smaller-root-cause fidelity findings — inline-literal right-margin
overflow (FID-10), lost paragraph reflow (FID-11), the codly config-wrapper leak (FID-12), and
meaning-bearing inline styling (FID-13 external-link styling+boundary, FID-14 PEP-separator
hover-title) — are fixed, each isolated to its own node handler, each shipping a real
`typst.compile()` regression fixture (GATE-01), with zero new runtime deps, no `@preview` version
bump, and the 3-way version-sync surface untouched.
**Verified:** 2026-07-20
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | FID-10: colon-leading inline-literal run emits leading U+200B in non-`in_table` `visit_literal` branch, gated to narrow no-break-before class | ✓ VERIFIED | `typsphinx/translator.py:1259-1273` — new `elif` sibling to `if self.in_table:`; `code_content[0] in ":;,)]}!?"` predicate; ZWSP prepended before `escape_typst_string`. Real-compile fixture passes (`tests/test_inline_literal_overflow_render_gate.py`, 2/2 pass). |
| 2 | FID-10: 44 existing `raw("...")` exact-match assertions stay byte-unchanged (A1, backstop) | ✓ VERIFIED (backstop, confirmed) | `grep -n 'raw("' tests/*.py` inspected directly: existing literal strings (`"code"`, `"make.bat"`, `"Makefile"`, `"code_reference"`, `"print()"`, `"SUBSTLITERAL*"`, …) — none start with a character in `":;,)]}!?"`. Full non-slow suite green (451 passed, 0 failed). |
| 3 | FID-10 encoding-probe: ZWSP fix is character-class-gated only, not a length/normalization test (backstop) | ✓ VERIFIED (backstop, confirmed) | Code inspection: `code_content[0] in ":;,)]}!?"` is a single-character-membership test, no length/byte counting. |
| 4 | FID-12: captioned `literal_block` nested in `list_item` opens wrapper as `#{` (re-enters code mode) | ✓ VERIFIED | `typsphinx/translator.py:1612-1618` — `wrapper_prefix = "#" if (self.in_captioned_code_block and self.code_block_caption) else ""`. `in_markup_context`/`codly_prefix` predicate below is untouched (byte-identical to pre-fix). Real-compile fixture passes (`tests/test_codly_caption_listitem_leak_render_gate.py`, 2/2 pass). |
| 5 | FID-12: non-list-item captioned block and non-captioned list-item block stay byte-unchanged (boundary-probe) | ✓ VERIFIED | Predicate is a conjunction of both conditions; either alone yields bare `{`. `tests/test_pdf_render_gate.py::TestCodlyConfigLeakRenderGate` (pre-existing, differently-scoped) confirmed green — no regression. |
| 6 | FID-12: config call + wrapper sequence deterministic, only the `#` added (ordering-probe) | ✓ VERIFIED | Code diff is a single conditional prefix; no reordering of surrounding emission logic. |
| 7 | FID-12 encoding-probe: fix touches only fixed `#`/`{`/`""` literals, no new classification (backstop) | ✓ VERIFIED (backstop, confirmed) | Code inspection confirms — boolean conjunction of two existing state flags, no string-length/equality classification introduced. |
| 8 | FID-11: intra-paragraph soft `\n` collapses to a single space before escaping | ✓ VERIFIED | `typsphinx/translator.py:988` — `text_content = text_content.replace("\n", " ")` inserted after the `in_literal_block` early-return and before `escape_typst_string`. Real-compile structural fixture passes (`tests/test_paragraph_soft_newline_render_gate.py`, 1/1 pass, Shape-A/no-pypdf per D-08). |
| 9 | FID-11 collapse does not touch `in_literal_block`, inline `raw()`, or `line_block` hard breaks (guard set) | ✓ VERIFIED | `in_literal_block` early-return precedes the collapse line (line 968 vs 988); `visit_literal` never routes through `visit_Text`; `tests/test_line_blocks.py` (3 tests) stays green. |
| 10 | FID-14: PEP `*`/`/` separator (`astext()` exactly `"*"`/`"/"`) emits no inline explanation; genuine `:abbr:` still appends `(expansion)` | ✓ VERIFIED | `typsphinx/translator.py:4384` — `if explanation and node.astext() not in ("*", "/"):`. Real-compile fixture proves both directions in one document (`tests/test_abbr_pep_separator_render_gate.py`, 2/2 pass, pypdf confirms separator titles absent + genuine expansion present). |
| 11 | FID-14: empty `explanation` still appends nothing (empty-probe) | ✓ VERIFIED | Guard retains the original `if explanation` clause unmodified — only ANDed with the new predicate. |
| 12 | FID-14: genuine `:abbr:` expansion order unchanged (ordering-probe) | ✓ VERIFIED | Only the emit condition changed; the dummy-`Text`→`visit_Text` append path is untouched. |
| 13 | FID-14 encoding-probe: exact string-equality predicate, ASCII single-codepoint separators only (backstop) | ✓ VERIFIED (backstop, confirmed) | Code inspection: `node.astext() not in ("*", "/")` is exact tuple-membership, not length-based. |
| 14 | FID-13 styling: `#show link:` rule in `base.typ` colors+underlines only when `type(it.dest) == str` (external) | ✓ VERIFIED | `typsphinx/templates/base.typ:31-36` — inserted after line 25 (`#codly(...)`) and before `#let project(`, outside the 4 `@preview` import lines (8-19). Real-compile structural assert passes (`tests/test_external_link_style_render_gate.py::TestExternalLinkStyleRenderGate`, 1/1 pass). |
| 15 | FID-13 styling: external vs. internal `it.dest` scoping proven in one compile (boundary-probe) | ✓ VERIFIED | Same fixture pairs an external named hyperlink + a same-document `:ref:`; structural assert confirms `link("http...` external emission separately from the unstyled internal `link(<label>, ...)`. |
| 16 | FID-13 boundary: `visit_target` drops the leading `\n` before `#label(...)`, eliminating the stray double space | ✓ VERIFIED | `typsphinx/translator.py:2828` — `self.add_text(f'#label("{label_id}")')` (no leading `\n`). pypdf adjacency test confirms single-space form present, double-space form absent (`tests/test_external_link_style_render_gate.py::TestExternalLinkBoundaryRenderGate`, 2/2 pass). |
| 17 | FID-13 boundary: named external reference with no following text compiles to valid `%PDF` (empty-probe) | ✓ VERIFIED | Real-compile assert in the same test module confirms valid `%PDF` magic bytes. |
| 18 | FID-13 encoding-probe: leading-`\n` drop is a fixed transform, label id routes through unchanged `_namespace_label` (backstop) | ✓ VERIFIED (backstop, confirmed) | Code inspection: `label_id = self._namespace_label(...)` call is unchanged; only the surrounding `add_text` f-string literal lost its `\n` prefix. |
| 19 | Every fix ships or extends a real `typst.compile()` regression fixture (GATE-01) | ✓ VERIFIED | All 5 new gate modules run a real `sphinx-build -b typstpdf` subprocess and assert `%PDF` magic bytes; 10/10 new gate tests pass (executed live, see Behavioral Spot-Checks). |
| 20 | Zero new runtime deps, no `@preview` bump, version-sync surface untouched | ✓ VERIFIED | `pyproject.toml`/`uv.lock` diff across the whole phase is empty; `tests/test_preview_version_sync.py` (2/2) green; the 4 `@preview` import lines in `base.typ`/`writer.py`/`template_engine.py` are byte-identical. |

**Score:** 20/20 truths verified (0 present-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::visit_literal` | New elif sibling, conditional ZWSP (FID-10) | ✓ VERIFIED | Present, wired, exercised by passing gate test |
| `typsphinx/translator.py::visit_literal_block` | Conditional `#` wrapper prefix (FID-12) | ✓ VERIFIED | Present, wired, exercised by passing gate test |
| `typsphinx/translator.py::visit_Text` | `\n`→space collapse before escape (FID-11) | ✓ VERIFIED | Present, wired, exercised by passing gate test |
| `typsphinx/translator.py::depart_abbreviation` | Narrowed guard excluding `*`/`/` (FID-14) | ✓ VERIFIED | Present, wired, exercised by passing gate test |
| `typsphinx/templates/base.typ` | `#show link:` rule, external-only (FID-13 styling) | ✓ VERIFIED | Present, wired, exercised by passing gate test |
| `typsphinx/translator.py::visit_target` | Dropped leading `\n` before `#label(...)` (FID-13 boundary) | ✓ VERIFIED | Present, wired, exercised by passing gate test |
| `tests/test_inline_literal_overflow_render_gate.py` + fixture | GATE-01 for FID-10 | ✓ VERIFIED | Real `-b typstpdf` compile + pypdf, 2/2 pass |
| `tests/test_codly_caption_listitem_leak_render_gate.py` + fixture | GATE-01 for FID-12 | ✓ VERIFIED | Real `-b typstpdf` compile + pypdf, 2/2 pass |
| `tests/test_paragraph_soft_newline_render_gate.py` + fixture | GATE-01 for FID-11 (structural-only, D-08) | ✓ VERIFIED | Real `-b typstpdf` compile, 1/1 pass, no pypdf (correct per D-08) |
| `tests/test_abbr_pep_separator_render_gate.py` + fixture | GATE-01 for FID-14 | ✓ VERIFIED | Real `-b typstpdf` compile + pypdf, 2/2 pass |
| `tests/test_external_link_style_render_gate.py` + fixture | GATE-01 for FID-13 (styling + boundary) | ✓ VERIFIED | Real `-b typstpdf` compile + pypdf, 3/3 pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `visit_literal` non-`in_table` branch | `escape_typst_string` | ZWSP prepended before escaping call | ✓ WIRED | Confirmed at translator.py:1273/1277 |
| `self.in_table` ZWSP block | (unchanged) | Isolated sibling, not extended (D-05) | ✓ WIRED / ISOLATED | `.`/`_` splitting logic byte-identical to pre-phase |
| `visit_literal_block` wrapper brace | `in_markup_context`/`codly_prefix` predicate | Predicate below stays unchanged (D-Disc-2) | ✓ WIRED | Confirmed unchanged at ~1632-1642 |
| `visit_Text` collapse | `escape_typst_string` | Collapse precedes escape call | ✓ WIRED | Confirmed at translator.py:988 vs 992 |
| `depart_abbreviation` guard | `visit_Text` (dummy Text delegate) | Narrowed condition, same append path | ✓ WIRED | Confirmed at translator.py:4384-4386 |
| `base.typ` `#show link:` | builder's `_write_template_file` | Verbatim copy into `_template.typ` | ✓ WIRED | Structural test reads `_template.typ` and confirms rule present |
| `visit_target` `_in_reference_with_target` branch | `_namespace_label` | Label id sanitization unchanged | ✓ WIRED | Confirmed unchanged call at translator.py:2825-2828 |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 5 new GATE-01 modules pass (10 tests) | `uv run pytest tests/test_inline_literal_overflow_render_gate.py tests/test_codly_caption_listitem_leak_render_gate.py tests/test_paragraph_soft_newline_render_gate.py tests/test_abbr_pep_separator_render_gate.py tests/test_external_link_style_render_gate.py -v` | 10 passed | ✓ PASS |
| Full non-slow suite (excl. 4 documented environmental integration files) | `uv run pytest -m "not slow" -q --ignore=tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py` | 451 passed, 23 deselected, 0 failed | ✓ PASS |
| `test_examples_basic.py` (3 subprocess tests flagged as env-flaky in SUMMARYs) | included in full-suite run above | 15/15 passed in this environment | ✓ PASS (no regression observed) |
| Version-sync surface untouched | `uv run pytest tests/test_preview_version_sync.py -v` | 2 passed | ✓ PASS |
| Corpus gate (fatal-free, ~684 pages) | `uv run pytest tests/test_corpus_gate.py -m slow -v` | 1 passed, 1 skipped (env-gated reporting test, pre-existing, unrelated) | ✓ PASS |
| No new runtime dependency | `git diff 5512d84~1 24070c7 -- pyproject.toml uv.lock` | empty diff | ✓ PASS |
| CI-parity lint/format/type checks | `uv run black --check .`, `ruff check .` (via nix-shell), `uv run mypy typsphinx/` | all clean | ✓ PASS |
| A1 backstop: no existing `raw("...")` literal starts with gated class | `grep -n 'raw("' tests/*.py` (manual review) | none match `":;,)]}!?"` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FID-10 | 21-01 | Inline-literal margin overflow (Cluster C) | ✓ SATISFIED | `visit_literal` elif branch + GATE-01 fixture, all tests pass |
| FID-11 | 21-02 | Paragraph soft-newline reflow (Cluster D) | ✓ SATISFIED | `visit_Text` collapse + GATE-01 fixture, all tests pass |
| FID-12 | 21-01 | Codly config-wrapper leak (Cluster E) | ✓ SATISFIED | `visit_literal_block` conditional `#{` + GATE-01 fixture, all tests pass |
| FID-13 | 21-03 | External-link styling + boundary spacing (Cluster F) | ✓ SATISFIED | `base.typ` show-rule + `visit_target` fix + shared GATE-01 fixture, all tests pass |
| FID-14 | 21-02 | PEP-separator hover-title suppression (Cluster F) | ✓ SATISFIED | `depart_abbreviation` narrowed guard + GATE-01 fixture, all tests pass |

No orphaned requirements — all 5 requirement IDs in REQUIREMENTS.md's Phase 21 traceability table are claimed by exactly one plan each (21-01: FID-10/FID-12; 21-02: FID-11/FID-14; 21-03: FID-13), matching ROADMAP.md's 5-item success-criteria list.

**Note (informational, not a gap):** `.planning/REQUIREMENTS.md`'s checkboxes (`- [ ]`) and its Traceability table (`Status: Pending`) for FID-10..FID-14 have not yet been flipped to `[x]`/`Complete`, unlike Phase 19/20's entries. Cross-checking git history, this mirrors the expected lifecycle stage: Phases 19/20 already went through ship/complete steps that updated this bookkeeping, while Phase 21 has not yet been shipped. This is a documentation-bookkeeping item for the ship/progress step, not evidence the fixes are missing — all 5 fixes are independently confirmed present, wired, and gated in the code itself.

### Edge-Probe Coverage Cross-Check

The plans' `must_haves.truths` collectively carry forward 15 "-probe: covered" / `backstop`-tagged truths (5 in 21-01 probe-covered + 2 backstop, 4 in 21-02 probe-covered + 1 backstop, 2 in 21-03 probe-covered + 1 backstop = 11 covered + 4 backstop = 15) plus 2 explicitly flagged-as-not-applicable assumptions (21-01's FID-12 precision-probe, 21-03's FID-13 precision-probe) — matching the phase brief's "15 covered/backstop + 2 flagged assumptions" expectation exactly. Both flagged assumptions are surfaced in each plan's `<flagged_assumptions>` block, not silently dropped. All 4 backstop truths were independently confirmed via direct code inspection above (Observable Truths #2, #3, #7, #13, #18 — 5 backstop items total across all three plans, all confirmed with explicit evidence, none left at `insufficient_spec`).

### Locked-Decision Spot-Checks

| Decision | Check | Result |
|----------|-------|--------|
| D-04/D-05 (FID-10 in_table ZWSP isolated) | `self.in_table` block vs. new `elif` sibling | ✓ Isolated — no shared code path, `.`/`_` splitting logic untouched |
| D-02 (FID-13 external-only via `it.dest` type) | `#show link:` rule body | ✓ `type(it.dest) == str` gate confirmed; internal `link(<label>, …)` untouched |
| D-Disc-3 (FID-14 narrow scope) | `depart_abbreviation` guard | ✓ Exact-match `("*", "/")` tuple, no broader heuristic |

### Anti-Patterns Found

None. Scanned all phase-modified/created files (`typsphinx/translator.py`, `typsphinx/templates/base.typ`, all 5 new test modules, all 5 new fixture `index.rst` files) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER|placeholder|not yet implemented|coming soon`. The only matches in `translator.py` are pre-existing, out-of-scope lines (a `TODO-01` cross-reference comment from an earlier phase and the pre-existing graphviz/inheritance-diagram graceful-degrade "placeholder" feature) — neither touched by this phase's diff.

### Human Verification Required

None. All truths were confirmable via direct code inspection plus live execution of the shipped GATE-01 regression fixtures (real `sphinx-build -b typstpdf` compiles producing valid `%PDF` output, with pypdf-extracted-text adjacency assertions where the finding is text-extractable). No visual-only, real-time, or external-service-dependent behavior in this phase.

### Gaps Summary

No gaps found. All 5 requirements (FID-10 through FID-14) are implemented, isolated to their own node handlers as required, each ships a real-compile GATE-01 fixture that was executed live and passes, all milestone invariants hold (zero new runtime deps, no `@preview` bump, 3-way version-sync surface byte-unchanged, pypdf test-only), and the full regression suite (451 non-slow tests + the corpus gate) is green with no failures.

---

_Verified: 2026-07-20_
_Verifier: Claude (gsd-verifier)_
