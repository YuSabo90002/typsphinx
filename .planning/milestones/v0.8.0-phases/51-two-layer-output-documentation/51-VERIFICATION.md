---
phase: 51-two-layer-output-documentation
verified: 2026-08-15T00:00:00Z
status: passed
score: 3/3 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 51: Two-Layer Output Documentation Verification Report

**Phase Goal:** A user reading the published documentation can tell which of the two files
typsphinx now writes is the one to compile, and what happened to the file they used to compile.
**Verified:** 2026-08-15T00:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | Docs name the two layers, state the wrapper is the file to compile, and document the standalone-content-compile behaviour as intended (not a bug); `-b typst` users are told to compile the wrapper. | ✓ VERIFIED | `docs/source/user_guide/output_layout.rst` "Wrapper and Content Files" and "Which File to Compile" sections; `builders.rst` "Manual Compilation" explicitly says "Compile the **wrapper**, not the docname-named content file." Standalone-compile claim is honestly cited to `49-EVIDENCE.md`'s real-build transcript (`SHARED-CHAPTER-MARKER` present / `NESTED-DOCNAME-BODY-MARKER` absent), not re-derived (sandbox has no `typst.compile()`), per D-08/D-12. |
| 2 | Target-as-path semantics documented with worked examples (bare/explicit/refused); v0.7.x→v0.8.0 change stated in concrete old→new file names, distinct from v0.7.1's `index.typ`→`<project>.typ` rename. | ✓ VERIFIED | Rebuilt all 5 `tests/fixtures/output_layout_*_gate/` fixtures live via `sphinx-build -b typst`: bare target → `manual.typ`/`index.typ`/`_template.typ`; explicit path → `manuals/guide.typ`; absolute/drive/parent-traversal targets all produced the exact warning text quoted in the docs (`WARNING: a path is not supported in a typst_documents target name: '...' -- using '...' instead`) and fell back to basename at the root. `docs/source/changelog.rst`'s "Migrating from 0.7.x to 0.8.0" section states old→new file sets for all three breaking changes and an explicit paragraph distinguishing the v0.7.1 rename from the v0.8.0 shape change ("Two different renames touch `typst_documents` targets across these releases, and they are easy to confuse..."). |
| 3 | Every documented claim is verified against a real build, not written from design; the shared-child composition consequence appears in the user's language; `:numref:` divergence is excluded per D-06/D-07. | ✓ VERIFIED | Independently rebuilt (not just trusting the gate) every example config this phase publishes: bare-target (3 files), explicit-path, all 3 refusal fixtures, the self-collision fixture (exact `ExtensionError` text reproduced, zero `.typ` files left behind), the three-master fixture (`tests/fixtures/state_guard_three_master_gate` — real build produced exactly 10 `.typ` files, matching the page's "ten" claim), `docs/source/examples/advanced.rst`'s three-entry example (real build: 7 files, matches the now-accurate non-overclaiming prose), and both bundled examples (`examples/basic` → 3 files matches README; `examples/advanced` → 5 files matches README). `grep -rn ':numref:' docs/source/ README.md examples/` = 0 hits; `CHANGELOG.md`'s 2 pre-existing occurrences are unrelated v0.7.x table-anchor mentions, confirmed unrelated to the excluded divergence. Full suite: `uv run python -m pytest -q -m "not slow"` → 1101 passed, 0 failed. Real `-b html` docs build: exit 0, only 3 pre-existing unrelated `visit_toctree` docstring warnings, `output_layout.html` renders, zero undefined-label/unknown-document warnings. |

**Score:** 3/3 truths verified (0 present, behavior-unverified)

### Post-SUMMARY Orchestrator Fixes — Independently Re-Verified

| # | Defect (found after 6 plans reported complete) | Fix commit | Verified how | Result |
|---|---|---|---|---|
| 1 | README link-inventory guard pinned 7 links; plan 51-05 added an 8th (`output_layout.html`) | `d4c0ed7c` | Read `tests/test_no_stale_github_io_links.py:56-67` | `_EXPECTED_DEEP_LINK_SUFFIXES` is an 8-tuple, `output_layout.html` present in correct order, count derived from `len()` |
| 2 | 4 published file-set claims omitted `_template.typ` (CR-01) | `0ebdaecf` | Read all 4 files + rebuilt each config live | `output_layout.rst` states 3 files incl. `_template.typ`; `builders.rst` states 5; `examples/basic/README.md` states 3 (real build: 3); `examples/advanced/README.md` states 5 (real build: 5) |
| 3 | Vacuous `assert "ten" in text` (WR-01) | `015f760b` | Read `tests/test_output_layout_docs_gate.py:445-462` | Assertion now checks `"writes ten \`\`.typ\`\` files" in text` — a substring only the real sentence satisfies |
| 4 | Two sweep residuals in `examples/advanced.rst:160` and `examples/advanced/index.rst:37-40` | `be794ed0` | Read both files, rebuilt the equivalent config live | `advanced.rst:159-163` no longer undercounts, names wrappers, links to the contract page; `index.rst:37-40` attributes chapter inclusion to guarded state-read `#include()` rather than an unconditional one |

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `docs/source/user_guide/output_layout.rst` | New page: wrapper/content split, target-as-path, refusal, standalone behaviour, collisions, shared-child composition | ✓ VERIFIED | Exists, substantive (163 lines of prose + code blocks), wired into `user_guide/index.rst` toctree (line 12) and definition list (`:doc:` reference line 37), every claim checked against a real build above |
| `docs/source/changelog.rst` | "Migrating from 0.7.x to 0.8.0" subsection | ✓ VERIFIED | Present, 3 breaking-change bullets with before/after code blocks, exact `ExtensionError` text matches a live build, explicit v0.7.1-vs-v0.8.0 rename disambiguation paragraph |
| `docs/source/user_guide/builders.rst` | Output/Manual Compilation/Document Definitions sections corrected | ✓ VERIFIED | Wrapper/content language present, `myproject.typ` walkthrough matches `make_filename_from_project("My Project")` output, 5-file count for two-entry example matches a live rebuild |
| `docs/source/user_guide/configuration.rst` | `typst_documents` element-2 contract reversed from OUT-01-falsified text | ✓ VERIFIED | "A path component is not supported" language is gone; path-honoured and refused-shape text present and matches `_resolve_target_stem()`/`_is_drive_qualified()`/`_escapes_outdir()` behaviour |
| `docs/source/user_guide/templates.rst` | `.typ`-inspection walkthrough corrected | ✓ VERIFIED | `cat build/typst/myproject.typ` (not `index.typ`), with explanatory prose on why the content file can't show a template problem |
| `README.md` | False claims (`:82-85`, `:228`) corrected + new link | ✓ VERIFIED | Both sites read accurate wrapper/content-file language; `docs/source/user_guide/output_layout.rst` linked at line 88 and in the Documentation quick-links section |
| `examples/basic/README.md`, `examples/advanced/README.md` | Rewritten from real builds | ✓ VERIFIED | Both file lists match live rebuilds exactly (3 and 5 files respectively) |
| `docs/source/examples/advanced.rst` | Sweep residual fix | ✓ VERIFIED | Rewritten, matches a live 7-file rebuild in framing (no false undercount) |
| `examples/advanced/index.rst` | Sweep residual fix | ✓ VERIFIED | State-guarded `#include()` framing, no longer claims unconditional combination |
| `tests/test_output_layout_docs_gate.py` | Permanent D-10/D-11/D-12 gate, never skips | ✓ VERIFIED | 13 tests, all pass, no `pytest.mark.skip`/`importorskip`; expected values derived from `make_filename_from_project` per D-11 |
| `tests/fixtures/output_layout_*_gate/` (5 fixtures) | Real build fixtures backing the gate | ✓ VERIFIED | All 5 rebuilt independently this verification, output matches gate assertions and page prose |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `docs/source/user_guide/index.rst` | `output_layout.rst` | toctree + `:doc:` reference | WIRED | Confirmed present at lines 12 and 37 |
| `builders.rst`/`configuration.rst`/`templates.rst` | `output_layout.rst` | `:doc:` cross-references | WIRED | Each page links rather than duplicating (D-01); real `-b html` build resolves every cross-reference with zero undefined-label warnings |
| `changelog.rst` migration section | `output_layout.rst` | `:doc:` reference | WIRED | "See :doc:`/user_guide/output_layout` for the full current output-layout contract." confirmed present |
| `README.md` | `output_layout.rst` | Markdown link + quick-links list | WIRED | Both occurrences confirmed (lines 88, 306) |
| `tests/test_output_layout_docs_gate.py` | `docs/source/user_guide/output_layout.rst` prose | `Path.read_text()` assertions | WIRED | Gate reads the live file from disk; 13/13 tests pass against current prose |

### Data-Flow / Build Verification (Level 4 — SC#3's own requirement)

| Claim | Config | Real build result | Status |
|---|---|---|---|
| Bare target writes 3 files | `output_layout_bare_target_gate` | `manual.typ`, `index.typ`, `_template.typ` | ✓ FLOWING |
| Explicit path honoured | `output_layout_explicit_path_gate` | `manuals/guide.typ` | ✓ FLOWING |
| `..`/absolute/drive refused with fallback | 3 refusal fixtures | Warning text matches docs verbatim; fallback basename written at root | ✓ FLOWING |
| Collision aborts, zero files written | `bld03_self_collision_gate` (Phase 47) | `ExtensionError` text byte-matches changelog/page quote; zero `.typ` files present | ✓ FLOWING |
| Three-master project writes ten files | `state_guard_three_master_gate` | Exactly 10 `.typ` files | ✓ FLOWING |
| `basic` example emits 3 files | `examples/basic` | 3 files, matches README | ✓ FLOWING |
| `advanced` example emits 5 files | `examples/advanced` | 5 files, matches README | ✓ FLOWING |
| `advanced.rst` 3-entry example | reconstructed config | 7 files (wrappers + content + `_template.typ`); prose no longer overclaims a count | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full test suite | `uv run python -m pytest -q -m "not slow"` | 1101 passed, 73 deselected, 0 failed | ✓ PASS |
| Docs-gate + link-inventory tests | `uv run python -m pytest -q tests/test_output_layout_docs_gate.py tests/test_no_stale_github_io_links.py` | 17 passed | ✓ PASS |
| Real HTML docs build | `sphinx-build -b html -q docs/source <out>` | exit 0, `output_layout.html` produced, only 3 pre-existing unrelated docstring warnings, no undefined-label/unknown-document warnings | ✓ PASS |
| `typsphinx/` untouched (pure docs phase) | `git diff --name-only 30c8b289..HEAD -- typsphinx/ \| wc -l` | `0` | ✓ PASS |
| Black/Ruff on changed Python files | `black --check`, `ruff check` on the two test files | clean | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| DOC-14 | 51-01..51-06 (all 6 plans declare it) | Published docs describe the two-layer output: which file to compile, standalone-compile behaviour, target-as-path semantics, what changed from v0.7.x | ✓ SATISFIED | All three roadmap SCs independently verified above against real builds; `REQUIREMENTS.md:267` already marks `DOC-14 | Phase 51 | Complete` and no other phase claims it — no orphaned requirements |

### Anti-Patterns Found

None. Grepped every file this phase touched (`docs/source/**`, `README.md`, `examples/**/README.md`, `examples/advanced/index.rst`, `tests/test_output_layout_docs_gate.py`, `tests/test_no_stale_github_io_links.py`, `tests/fixtures/output_layout_*_gate/**`) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER|not yet implemented|coming soon` — zero matches.

### Documentation-Accuracy Finding (info, not a gap)

`51-SWEEP-AUDIT.md`'s "Residual sweep findings" section (lines 165-201) still describes the two
`docs/source/examples/advanced.rst` / `examples/advanced/index.rst` findings as "OUTSTANDING, not
fixed," which is now stale relative to `be794ed0` (which fixed both, confirmed above by direct
file read and a live rebuild). This is a planning-artifact staleness issue in an internal audit
document, not in the published, user-facing documentation this phase's success criteria govern —
it does not affect any of the three observable truths and is not counted as a gap. No action is
required for phase completion; noted here so the phase-closing record isn't silently wrong if
anyone reads `51-SWEEP-AUDIT.md` after this verification.

### Human Verification Required

None. All three success criteria are documentation-content and build-output claims, fully
checkable by direct file reads and live `sphinx-build` rebuilds — no runtime UI, visual rendering,
or external-service behaviour is in scope for this phase.

### Gaps Summary

None. All three roadmap Success Criteria are VERIFIED with direct evidence (live rebuilds, not
just re-reading the gate module or trusting SUMMARY.md). All four defects the orchestrator found
and fixed after the six plans reported complete are confirmed genuinely fixed by independent
re-derivation, not by re-reading the fix commits' own claims. Zero `typsphinx/` lines changed
(pure documentation phase, as scoped). Full suite green (1101/1101). D-07's `:numref:` exclusion
is measured clean. No orphaned requirements, no debt markers, no stub content.

---

_Verified: 2026-08-15T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
