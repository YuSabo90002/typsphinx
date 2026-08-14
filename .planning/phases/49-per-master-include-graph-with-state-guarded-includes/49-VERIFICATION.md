---
phase: 49-per-master-include-graph-with-state-guarded-includes
verified: 2026-08-14T20:15:00Z
status: human_needed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Decide disposition of code-review WR-01 (edge-key separator collision: `make_include_edge_key('a', 'b#1>c', occurrence=0) == make_include_edge_key('a#0>b', 'c', occurrence=1)` — a docname containing a literal `#` or `>` can silently collide two structurally different include edges onto the same key string, causing a guard to fire for the wrong edge with zero diagnostic)."
    expected: "Either fixed in this phase (escape `#`/`>` in `make_include_edge_key`'s components) or explicitly filed as a tracked pending todo the same way the numref divergence was (`.planning/todos/pending/...`), before the phase ships."
    why_human: "No stated Success Criterion or requirement (COMP-05..12) tests a docname containing `#`/`>`, so this is not a FAILED truth against the roadmap contract — but it is squarely the class of defect (silent content mis-inclusion with no diagnostic) this phase's own prohibitions forbid trading one instance of for another. It was found by the committed 49-REVIEW.md code review and reproduced independently below, but unlike the numref finding it was never filed as a todo or otherwise closed. This is an owner judgment call, not a mechanically-decidable one."
  - test: "Decide disposition of code-review WR-02 (unbounded recursion in `derive_master_edge_keys`'s nested `walk()` — a sufficiently deep/long linear include chain raises `RecursionError` and crashes the whole Sphinx build with a raw Python traceback instead of a controlled `ExtensionError`)."
    expected: "Either fixed (iterative traversal, or a guarded recursion-limit raise producing an actionable error) or filed as a tracked pending todo before the phase ships."
    why_human: "Same reasoning as WR-01: no SC/requirement exercises a chain anywhere near Python's recursion limit, so this does not FAIL a stated truth, but it is an unhandled crash risk introduced by this phase's own new traversal function, found by the committed review and left untracked."
---

# Phase 49: Per-Master Include Graph with State-Guarded Includes Verification Report

**Phase Goal:** The include decision moves from write time to compile time — the builder computes
each master's include graph by mirroring `sphinx/util/nodes.py`'s `inline_all_toctrees`
(document-order depth-first, first-encounter-wins, `traversed` re-initialised per master), and each
wrapper publishes its master's edge set as a Typst `state` before including its master's content.
`visit_toctree` emits a state-guarded include at the toctree's own position instead of an
unconditional `include()`, and `builder.py`'s build-scoped `_included_docnames` ledger becomes
unnecessary. This closes defect A and the diamond shape no write-time ledger can serve.

**Verified:** 2026-08-14T20:15:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC#1 | Defect A closed on generated evidence: two masters both toctreeing `shared` produce two PDFs each containing the shared chapter's marker, read back through `pypdf`, against the recorded pre-fix 0/1 baseline | ✓ VERIFIED | `tests/test_state_guard_composition_gate.py::test_shared_chapter_appears_in_both_masters_pdf` passes (re-ran independently: 1 test, green). Pre-fix RED recorded verbatim in `49-RED-EVIDENCE.md` "Failure mode 1" (0 occurrences in `manual.pdf`, 1 in `bmanual.pdf`, exit 0, no warning) — matches the 2026-08-11 PROJECT.md baseline. |
| SC#2 | The diamond compiles correctly from one shared file; ≥5 degenerate shapes each have a decided outcome, decided at plan time not discovered as a test failure | ✓ VERIFIED | `49-EXPECTED-STRUCTURE.md`'s `## Degenerate-shape outcome table` (wave 1, committed before wave-2 fixtures) fixes the outcome for cycle, self-reference, `self`/URL, glob, orphan, duplicate-entry. `tests/test_state_guard_shapes_gate.py` (17 tests, all green, 0 xfail) and `tests/test_state_guard_composition_gate.py`'s diamond test (`test_diamond_shared_content_file_identical_across_masters`) both pass, asserting SHA-256-identical `shared.typ` bytes and exactly-once-per-master rendering. |
| SC#3 | Traversal matches Sphinx's own selection rule (document-order DFS, first-encounter-wins, not the deleted LIFO stack-walk); heading depth follows source order, asserted on resolved levels via `typst.query(...)`, not `.typ` grepping | ✓ VERIFIED | `derive_master_edge_keys()` (`translator.py:234-300`) is a genuine recursive walk with `traversed` seeded per master, matching Sphinx's `inline_all_toctrees`. `test_mirror_pair_resolved_heading_levels_and_source_divergence` calls `_query_heading_outline()`, which invokes `typst.query(str(typ_path), "heading", root=...)` against the real compiled `.typ` — confirmed by reading the helper (`test_state_guard_composition_gate.py:171-179`), not a text grep. Passes. |
| SC#4 | Prose keeps position relative to included content (`PROSE-BEFORE` → chapters → `PROSE-AFTER`); `visit_toctree` emits no unconditional `include()`; `_included_docnames` and its resets are deleted, verified by repo-wide grep | ✓ VERIFIED | `test_document_order_interleaving_preserved` passes (pypdf text-order assertion). `_included_docnames` returns zero matches anywhere under `typsphinx/`, `tests/`, `docs/`, `examples/` — independently confirmed via `grep -rn` (only hits are in `.planning/` history and a different, already-Phase-48-deleted symbol `master_included_docnames`, correctly distinguished in the codebase's own comments). `tests/test_include_ledger_removal_gate.py`'s structural AST-based gate (10 tests, all green) independently re-derives and re-checks this at every future change. |
| SC#5 | Holds at corpus scale (GATE-02 fatal-free, empty unknown-visit catalogue); `:numref:` question answered by live two-master measurement, fix-or-document decision recorded | ✓ VERIFIED | `tests/test_corpus_gate.py` re-run independently: `1 passed`, `Unknown Visit Catalogue: []`, exit 0 — matches orchestrator's measurement. `tests/test_state_guard_numref_gate.py` (6 tests) passes; `49-EVIDENCE.md`'s `## numref measurement` records both cases verbatim (Case (a) diverges 1 vs 3, Case (b) falls back to raw label — and explicitly corrects its own D-01 hypothesis that Case (b) produces "zero warning", since Sphinx 9.1.0 does emit one). D-01's fix-or-document decision (document, don't fix) was owner-approved at the 49-06 blocking checkpoint, and filed as `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`, `resolves_phase: 52`. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py` — `INCLUDE_STATE_KEY`, `make_include_edge_key`, `derive_master_edge_keys`, `render_include_edge_state`, `render_include_guard`, `visit_toctree` | The five new symbols plus the rewritten toctree visitor | ✓ VERIFIED | All present, substantive (real logic, not stubs), read and traced against `sphinx/directives/other.py`/`sphinx/environment/adapters/toctree.py` by the code review; independently spot-checked here. |
| `typsphinx/builder.py` — `_build_include_edge_map`, `_master_include_edges`, `write()`/`_write_typst_files()` wiring | Per-master edge mapping derivation and consumption | ✓ VERIFIED | `_master_include_edges` derived unconditionally in `write()` before the per-docname loop; lazily re-derived in `_write_typst_files()` for the direct-call unit-test path; `edge_keys=` passed into `render_wrapper()`. |
| `typsphinx/writer.py` — `render_wrapper(..., edge_keys=...)` | Wrapper emits state publication line before `#include()` | ✓ VERIFIED | `state_line = render_include_edge_state(edge_keys)`; body is `f'{state_line}\n#include("{include_path}")\n'` — publication immediately precedes the include, matching the emission contract. |
| Deleted: `TypstBuilder._included_docnames` (build-scoped ledger) | Zero occurrences anywhere in shippable source (COMP-11) | ✓ VERIFIED | `grep -rn "_included_docnames"` across `typsphinx/`, `tests/`, `docs/`, `examples/` returns zero matches; only the phase's own removal-gate test module names the deleted symbol (deliberately, as its own constant). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `visit_toctree` (translator.py) | `make_include_edge_key`/`render_include_guard` | Direct call, one emission site per include-file entry | ✓ WIRED | Confirmed by reading the visitor body; `test_include_ledger_removal_gate.py::TestToctreeVisitorEmitsNoUnconditionalInclude` structurally re-asserts this on every future change (AST-based, not a one-time check). |
| `TypstBuilder._build_include_edge_map` | `derive_master_edge_keys` | Direct call, once per usable `typst_documents` entry | ✓ WIRED | `builder.py:283-285`. |
| `TypstWriter.render_wrapper` | `render_include_edge_state` | Direct call with the master's derived `edge_keys` | ✓ WIRED | `writer.py:318`. |
| Graph-side and emission-side edge-key derivation | `make_include_edge_key` (single shared function) | Both `derive_master_edge_keys()` (builder→translator import) and `visit_toctree()` call the same function | ✓ WIRED | Confirmed by reading both call sites; `tests/test_include_edge_derivation_unit.py` (25 tests, green) unit-tests byte-identical output across both call shapes. |

### Behavioral Spot-Checks (independently re-run, not trusted from SUMMARY)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Phase 49 composition gate | `uv run pytest tests/test_state_guard_composition_gate.py` | 11 passed | ✓ PASS |
| Phase 49 shapes gate | `uv run pytest tests/test_state_guard_shapes_gate.py` | 17 passed | ✓ PASS |
| COMP-11 removal gate | `uv run pytest tests/test_include_ledger_removal_gate.py` | 10 passed | ✓ PASS |
| numref two-case gate | `uv run pytest tests/test_state_guard_numref_gate.py` | 6 passed | ✓ PASS |
| GATE-02 corpus gate (unmodified) | `uv run pytest tests/test_corpus_gate.py` | 4 passed, 1 skipped (env-gated) | ✓ PASS |
| Edge-key unit tests, toctree/builder requirement suites, translator/builder regression suites | `uv run pytest tests/test_include_edge_derivation_unit.py tests/test_toctree_requirement13.py tests/test_builder_requirement13.py tests/test_translator.py tests/test_builder.py` | 179 passed | ✓ PASS |
| Zero xfail markers remain in either gate module | `grep -c xfail tests/test_state_guard_composition_gate.py tests/test_state_guard_shapes_gate.py` | Only docstring-narrative mentions (not `pytest.mark.xfail`); 0 active | ✓ PASS |
| `black --check` / `ruff check` / `mypy` on the three touched production files | `uv run black --check / ruff check / mypy typsphinx/{translator,builder,writer}.py` | All clean | ✓ PASS |

### Binding constraint spot-checks

**#6, no laundered gates:** `49-EXPECTED-STRUCTURE.md`'s `## Emission contract` and `## Fixture specification` sections are dated/positioned as wave-1 output (49-01-PLAN.md, committed before any wave-2 fixture or wave-3 emitter code exists in history). Spot-checked `test_mirror_pair_resolved_heading_levels_and_source_divergence` and `test_shared_chapter_appears_in_both_masters_pdf`: both assert against hand-derived expected values (`.rst` toctree order, marker-count expectations) traceable to the fixture spec, not against a value read off the emitter. No laundering found in the sampled assertions, consistent with 49-REVIEW.md's independent finding.

**#4, pre-fix RED named before implementation:** `49-RED-EVIDENCE.md` and `49-SHAPES-RED-EVIDENCE.md` carry verbatim pre-fix transcripts (worktree provenance confirmed, dependency versions pinned, real `sphinx-build`/`pypdf` output pasted) predating `typsphinx/` changes in the same worktree (`git status --porcelain typsphinx/` printed nothing at capture time, per the RED-EVIDENCE file's own statement).

**"must not trade one silent omission for another":** Held for every fixture and success criterion exercised by this phase's own gates. **Not fully held in the general case** — see WR-01 below, a residual gap in exactly this class, found by code review and left untracked.

**SC#2, decided at plan time:** Confirmed — the degenerate-shape outcome table exists in `49-EXPECTED-STRUCTURE.md` (49-01, wave 1) before the shape fixtures (49-03, wave 2) and the emitter (49-04, wave 3).

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| COMP-05 | 49-01, 49-03, 49-04, 49-05 | Document-order DFS, first-encounter-wins, matching `inline_all_toctrees` | ✓ SATISFIED | `derive_master_edge_keys` + mirror-pair fixture. |
| COMP-06 | 49-01, 49-03, 49-04, 49-05 | Wrapper publishes edge set as Typst `state`; content emits state-guarded includes | ✓ SATISFIED | `render_include_edge_state`/`render_include_guard`, exactly-one-state-key-spelling gate. |
| COMP-07 | 49-02, 49-04 | Document toctree'd by two masters appears in both PDFs | ✓ SATISFIED | SC#1 evidence above. |
| COMP-08 | 49-02, 49-04 | Prose keeps position relative to included content | ✓ SATISFIED | SC#4 interleaving test. |
| COMP-09 | 49-02, 49-03, 49-04 | Diamond shape: shared content appears exactly once per master | ✓ SATISFIED | Diamond test, three-master fixture. |
| COMP-10 | 49-02, 49-04 | Heading levels follow traversal order, asserted on resolved levels | ✓ SATISFIED | Mirror-pair `typst.query()` assertion. |
| COMP-11 | 49-04, 49-05 | `visit_toctree` emits no unconditional include; ledger removed | ✓ SATISFIED | Removal gate, repo-wide grep. |
| COMP-12 | 49-01, 49-06 | Full corpus compiles fatal-free; state/context convergence holds at scale | ✓ SATISFIED | GATE-02 re-run, corpus evidence. |

No orphaned requirements: REQUIREMENTS.md's Phase 49 row set (COMP-05..12, 8 total) is identical to the union of all six plans' `requirements:` frontmatter fields.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/translator.py:195-231` (`make_include_edge_key`) | — | Unescaped structural separators (`#`, `>`) in edge-key components — a docname literally containing `#` or `>` can make two different `(parent, occurrence, child)` triples collide onto the same key string, independently reproduced here (`make_include_edge_key('a', 'b#1>c', 0) == make_include_edge_key('a#0>b', 'c', 1)`) | ⚠️ Warning | Not exercised by any of this phase's fixtures or SCs; both graph-side and emission-side agree on the (wrong) key, so it is not a cross-side drift bug, but a colliding key can silently include/exclude the wrong document with zero diagnostic — precisely the failure class this phase exists to close. Previously reported in 49-REVIEW.md (WR-01), not yet fixed or filed as a todo. |
| `typsphinx/translator.py:280-297` (`derive_master_edge_keys`, nested `walk()`) | — | Unbounded recursion with no depth guard | ⚠️ Warning | Not exercised by any fixture (none approach Python's default recursion depth). A sufficiently deep/long include chain crashes the whole build with a raw `RecursionError` traceback instead of a controlled error. Previously reported in 49-REVIEW.md (WR-02), not yet fixed or filed as a todo. |
| No `TBD`/`FIXME`/`XXX` markers found in any file touched by this phase | — | — | — | Debt-marker gate: clean. |

Both warnings were found and reported by the phase's own committed code review (`49-REVIEW.md`, 0 critical / 2 warning / 1 info) and are re-confirmed here by independent reproduction. Neither undermines a stated Success Criterion or requirement (COMP-05..12) — none of the fixtures or gates exercise a docname containing `#`/`>` or a chain deep enough to hit Python's recursion limit — so this verification does not mark any truth FAILED on their account. They are, however, unresolved instances of exactly the "silent content mis-inclusion with no diagnostic" class this phase's own prohibitions target, and — unlike the `:numref:` divergence, which was explicitly triaged and filed as a tracked todo at the 49-06 owner checkpoint — neither has been fixed nor filed. This is an open completion-quality question for the owner, not a mechanically-decidable gap.

### Human Verification Required

1. **WR-01 disposition** — fix now, or file as a tracked pending todo (mirroring how the numref finding was handled)?
2. **WR-02 disposition** — fix now, or file as a tracked pending todo?

Both are detailed in the frontmatter `human_verification` block above.

### Gaps Summary

No gaps against the stated Success Criteria or requirement IDs. All 8 requirement IDs (COMP-05..12)
are genuinely satisfied by evidence independently re-derived in this verification pass (re-run gate
modules, re-run linters/type-checker, direct source reading of the three touched production files,
independent reproduction of both code-review warnings). The phase's own binding constraints (#4 RED-
first, #5 GATE-02 as an explicit SC, #6 no laundered gates, #7 no new dependency/config/package) all
hold on inspection. The one open item is a disposition decision on two known, review-reported,
unresolved defects (WR-01, WR-02) that fall outside every stated SC's test coverage but inside the
phase's own stated intent — routed to the owner rather than assumed.

---

_Verified: 2026-08-14T20:15:00Z_
_Verifier: Claude (gsd-verifier)_
