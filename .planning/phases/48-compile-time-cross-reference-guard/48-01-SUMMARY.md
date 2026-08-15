---
phase: 48-compile-time-cross-reference-guard
plan: 01
subsystem: testing
tags: [sphinx, typst, cross-reference, xref, pytest, autosectionlabel, red-evidence]

# Dependency graph
requires:
  - phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
    provides: the content/wrapper split fixture conventions and the 47-EXPECTED-STRUCTURE.md shape this plan imitates
provides:
  - Three new fixture projects reproducing the compile-time guard's defect classes (per-master divergence, citation-in-caption, label-namespace collision)
  - 48-RED-EVIDENCE.md — verbatim pre-fix transcripts for both reachable fatals plus the D-04 enumerated impossibility argument
  - 48-EVIDENCE.md's Body-mode measurement — the D-08 syntax question settled by real typst.compile() probes, adopting `[#{ ... }]`
  - 48-EXPECTED-STRUCTURE.md — every assertion this phase flips, with its new post-fix value, derived before any emitter change
  - Two new gate test modules recording the pre-fix RED as strict xfails (5 + 2), ready for 48-02/48-03 to flip green
affects: [48-02, 48-03, 48-04]

# Actuals (#2632)
actuals:
  tokens: 26215
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "sphinx.ext.autosectionlabel used in a fixture's own conf.py to make a :ref: resolve directly to a heading's own auto id (no separate metadata anchor), which is the only way Typst's PDF export registers a Named Destination recoverable via pypdf"
    - "Class-scoped pytest fixtures that tolerate a non-zero sphinx-build result, letting each xfail test record its own RED instead of erroring at fixture setup"
    - "Short, INLINE xfail reason= string literals (not named constants) so a literal grep-based scan finds the plan id immediately after 'xfail(strict=True'"

key-files:
  created:
    - .planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md
    - .planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md
    - .planning/phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md
    - tests/fixtures/xref_per_master_guard_gate/
    - tests/fixtures/citation_caption_dangling_label_gate/
    - tests/fixtures/xref_label_collision_guard_gate/
    - tests/test_xref_compile_time_guard_render_gate.py
    - tests/test_citation_caption_dangling_label_gate.py
  modified: []

key-decisions:
  - "xref_per_master_guard_gate's target section is referenced via sphinx.ext.autosectionlabel, not an explicit '.. _label:' target — an explicit target creates a SEPARATE metadata-only anchor that Typst's PDF export never registers as a Named Destination, making the plan's own destination-based PDF assertions unwritable"
  - "Adopted code_mode_body=True ([#{ ... }]) for D-07/D-08's guard syntax, per real typst.compile() measurement of all five probe cases (including the own-anchor composition) in both target-present and target-absent configurations"
  - "Test 2 in the xref gate module (alpha's PDF has the target's link) is written as a plain, non-xfail invariance guard, not a strict xfail — alpha's own outcome is empirically unchanged by this phase (its wrapper legitimately includes target.typ both before and after), so marking it xfail would XPASS and violate the plan's own zero-XPASS gate"

patterns-established:
  - "Fixture design for PDF-destination-based gate tests: route the :ref: at a genuine heading anchor (via autosectionlabel or an un-labelled section), never at a bare explicit-target-only metadata anchor, or _link_annotation_dests-style helpers cannot recover the label string from the compiled PDF"

requirements-completed: []  # XREF-03/XREF-04 close in later plans (48-02/48-03); this plan only records the pre-fix RED and expected post-fix values

# Coverage metadata — no user-facing deliverable this plan; it is a planning-artifact
# and test-authoring plan producing RED-state test fixtures/modules, not shipped behavior.
coverage: []

# Metrics
duration: 34min
completed: 2026-08-12
status: complete
---

# Phase 48 Plan 01: Compile-Time Cross-Reference Guard — RED + Expected Structure Summary

**Three new fixtures reproducing the compile-time guard's defect classes, the D-08 body-mode syntax settled by real `typst.compile()` measurement, every flipping assertion's new value derived before any emitter change, and two gate modules recording the pre-fix RED as strict xfails.**

## Performance

- **Duration:** 34 min
- **Started:** 2026-08-12T13:27:55+09:00 (Task 1 commit)
- **Completed:** 2026-08-12T14:02:09+09:00 (Task 3 commit)
- **Tasks:** 3
- **Files modified:** 15 (11 new fixture files, 3 new `.planning` artifacts, 2 new test modules — one fixture file set touched twice, once initially and once in the Rule-1 auto-fix commit)

## Accomplishments

- Three new fixture projects (`xref_per_master_guard_gate`, `citation_caption_dangling_label_gate`, `xref_label_collision_guard_gate`) reproduce XREF-03's per-master divergence, D-05's citation-in-caption dangling label, and the label-namespace collision false-negative — all measured, real `sphinx-build` reproductions, nothing reconstructed.
- `48-RED-EVIDENCE.md` records the verbatim pre-fix transcripts for both reachable fatals (direct `sphinx-build -b typstpdf` failures, exit 2, `does not exist in the document`) plus D-04's enumerated impossibility argument (Sphinx's `ReferencesResolver` replaces every `pending_xref` unconditionally before the writer runs) and the collision fixture's pre-fix baseline.
- `48-EVIDENCE.md`'s Body-mode measurement settles D-08: five hand-written Typst probes (including the `_reference_own_anchor` composition) all compiled clean in both target-present and target-absent configurations, adopting `code_mode_body=True` (`[#{ ... }]`) as the D-07 guard's body spelling.
- `48-EXPECTED-STRUCTURE.md` derives the exact post-fix value for every assertion this phase flips — three fixtures, three existing test modules (`test_xref_orphan_degrade_render_gate.py`, `test_master_include_set_predicate_gate.py`, `test_citation_degradation_gate.py`) — closing with a D-06 invariance list and two repo-wide greps proving the enumeration is complete (including due-diligence triage of eight files a broader grep surfaced but that turned out robust to the guard wrap).
- Two new gate modules (`test_xref_compile_time_guard_render_gate.py`, `test_citation_caption_dangling_label_gate.py`) record the pre-fix RED as strict `xfail`s (5 + 2), verified `uv run pytest` on these two modules reports 2 passed / 7 xfailed / zero failures / zero XPASS, and the full non-slow suite (1001 passed) shows no regressions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the three new fixture projects and capture pre-fix RED transcripts** — `e72dc32` (test)
2. **Task 2: Settle body-mode syntax by measurement, derive `48-EXPECTED-STRUCTURE.md`** — `5184f3e` (docs)
3. **[Rule 1 auto-fix] Use `autosectionlabel` so the per-master fixture's target gets a Named PDF Destination** — `504d075` (fix)
4. **Task 3: Author the two new gate modules, recording pre-fix RED as strict xfails** — `c010f85` (test)

**Plan metadata:** (this commit, following) — `docs: complete plan`

## Files Created/Modified

- `.planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md` — verbatim pre-fix transcripts, D-04 impossibility argument, collision baseline
- `.planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md` — Body-mode measurement (5 probes) settling D-08
- `.planning/phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md` — every flipping assertion's new post-fix value, derived first-principles
- `tests/fixtures/xref_per_master_guard_gate/` (`conf.py`, `index.rst`, `bravo.rst`, `target.rst`) — SC#1 two-master acceptance fixture
- `tests/fixtures/citation_caption_dangling_label_gate/` (`conf.py`, `index.rst`) — D-05 pre-fix RED fixture
- `tests/fixtures/xref_label_collision_guard_gate/` (`conf.py`, `index.rst`, `a_u2f_b.rst`, `a/b.rst`) — label-collision false-negative fixture
- `tests/test_xref_compile_time_guard_render_gate.py` — 6 tests (5 strict xfail + 1 plain invariance guard) for XREF-03/SC#1
- `tests/test_citation_caption_dangling_label_gate.py` — 3 tests (1 plain invariance guard + 2 strict xfail) for D-05/XREF-04

## Decisions Made

- **`xref_per_master_guard_gate` uses `sphinx.ext.autosectionlabel` instead of an explicit `.. _label:` target.** Discovered mid-Task-3 (Rule 1 auto-fix): Typst's PDF export registers a Named Destination (recoverable via `pypdf`'s `/Dest` as a plain string) only for a label that participates in the document's `#outline()` — a heading anchor. An explicit target directly above a section makes typsphinx emit a SEPARATE `#metadata(none) <label>` anchor (matching the established, documented behavior of `xref_orphan_degrade_render_gate/orphan.rst`), and a link to THAT anchor compiles fine but its PDF destination is an unnamed positional array with no string to recover — making the plan's own destination-based PDF assertions structurally unwritable. `autosectionlabel` resolves `:ref:` directly to the section's own auto id with no separate node, so the referenced label IS the heading anchor. Verified against a real compiled PDF's `/Names/Dests` name tree before and after the fix.
- **Adopted `code_mode_body=True` for D-07/D-08's guard syntax.** All five Body-mode measurement probes — including the previously-unmeasured `_reference_own_anchor` bracket-wrap composition — compiled clean in both target-present and target-absent configurations, confirming the code-mode-body spelling preserves today's child-emission bytes exactly.
- **Test 2 (`test_alpha_pdf_links_to_target`) is a plain invariance guard, not a strict xfail** — see Deviations below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `xref_per_master_guard_gate`'s explicit target could never satisfy a destination-based PDF assertion**
- **Found during:** Task 3 (writing `_link_annotation_dests` and the tests that consume it)
- **Issue:** The fixture's original `.. _guarded-target-section:` explicit label produced a metadata-only anchor with no Named PDF Destination — `_link_annotation_dests` (as specified by the plan) could never recover the target label string from the compiled PDF for this specific link.
- **Fix:** Switched `target.rst` to a single section referenced via `sphinx.ext.autosectionlabel`; verified the resulting link's `/Dest` is now a plain string in the compiled PDF's `/Names/Dests` tree, both before and after the fix.
- **Files modified:** `tests/fixtures/xref_per_master_guard_gate/conf.py`, `index.rst`, `bravo.rst`, `target.rst`; `48-RED-EVIDENCE.md`, `48-EXPECTED-STRUCTURE.md` updated to the new label/title.
- **Verification:** Re-ran the direct build fatal (`-b typstpdf` still exits 2 with `does not exist in the document`) and all previously-passing Task 1/2 acceptance-criteria greps, confirming nothing else broke.
- **Committed in:** `504d075`

**2. [Rule 1 - Bug] Test 2 in `test_xref_compile_time_guard_render_gate.py` cannot be a strict xfail without violating the plan's own zero-XPASS gate**
- **Found during:** Task 3, running the new module against the unfixed tree
- **Issue:** `48-01-PLAN.md`'s Task 3 text lists all six tests in this module as strict xfails. Empirically, alpha's own destination-based assertion ("alpha's compiled PDF has the target's link") is TRUE on the unfixed tree today — alpha's wrapper legitimately `#include()`s `target.typ` via its own toctree both before and after this phase, unaffected by the guard. Marking it `xfail(strict=True)` XPASSes, which the plan's own acceptance criteria (`zero XPASS`) forbids.
- **Fix:** Written as a plain, non-xfail invariance guard instead — mirroring the exact reasoning the plan's own text already applies to test 4 in the opposite direction ("test 4 must NOT be written as a plain non-xfail invariance guard [because it's false pre-fix]"). Documented explicitly in the module's own docstring.
- **Files modified:** `tests/test_xref_compile_time_guard_render_gate.py`
- **Verification:** `uv run pytest tests/test_xref_compile_time_guard_render_gate.py -q -rxX` reports 1 passed / 5 xfailed / zero failures / zero XPASS.
- **Committed in:** `c010f85`

---

**Total deviations:** 2 auto-fixed (both Rule 1 — correctness of the plan's own verification gate).
**Impact on plan:** Both auto-fixes were necessary for the plan's own stated acceptance criteria (zero XPASS, real destination-based assertions) to be satisfiable at all. No scope creep — both stayed within Task 3's boundary (writing the gate modules and, transitively, the fixture that feeds them).

## Issues Encountered

- **`48-EXPECTED-STRUCTURE.md`'s initial "How to find any assertion I missed" section overclaimed completeness.** The second repo-wide grep (`link(<[a-z_]*[a-z0-9_]*:`) surfaced eight files beyond the six explicitly enumerated sites. Rather than silently narrowing the grep to hide this, each file was individually triaged: seven use robust positive substring/regex membership assertions that stay true regardless of the guard's `if`/`else` wrapping (since the guard's SOURCE text always contains both branches' bytes), and the two genuinely negative assertions found (`test_citation_render_gate.py` lines 603/779) are both unrelated mechanisms (an unresolved citation key, a zero-backref uncited citation) that never reach the D-07 guard. The section was rewritten to record this due-diligence honestly rather than assert an unverified completeness claim.
- **A naive `grep 'xfail(strict=True'` scan for the "reason names the flipping plan" acceptance criterion breaks under `black`'s line-wrapping** once a `reason=` string is long enough to force the decorator across multiple lines, and (separately) breaks if the reason is a named module-level constant rather than an inline literal (the plan id text is then textually absent at the decorator site). Resolved by keeping every `reason=` a SHORT inline string literal (with the flipping plan id, e.g. `"48-02 lands the guard (RED-EVIDENCE #1)"`) that fits on one physical line under `black`, with the full explanation moved to a code comment directly above each decorator. Also had to rephrase every PROSE mention of the literal substring `xfail(strict=True)` in module docstrings/comments (which the same literal split would otherwise have counted as a spurious decorator with no plan id nearby).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plans 48-02/48-03 have every value they need to implement the compile-time guard already written down: the exact `_label_existence_guard` open/close string contract (`48-EXPECTED-STRUCTURE.md` "Guard contract"), the adopted body-mode spelling (`48-EVIDENCE.md`), and the exact post-fix expected value for every assertion that flips at all six identified change sites.
- Both new gate modules are RED exactly as designed (5+2 strict xfails) and will XPASS-fail loudly (via `strict=True`) the moment 48-02/48-03 land the guard incorrectly or incompletely, or flip cleanly green when it lands correctly.
- No blockers. `typsphinx/` remains completely untouched throughout this plan (`git status --porcelain typsphinx/` prints nothing at every commit), satisfying binding constraint #6 for the next plan to build on.

---
*Phase: 48-compile-time-cross-reference-guard*
*Completed: 2026-08-12*
