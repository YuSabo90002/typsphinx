# Phase 55: v0.8.0-Derived Defects - Context

**Gathered:** 2026-08-16
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase closes the five defects v0.8.0 created and shipped unfixed — four by owner decision
D-01 at the v0.8.0 close, and one (BLD-09) whose product side is still open after plan 52-09 fixed
only the test. Every one of them is a "compiles fine, produces wrong output" or "wrong exception
type" shape, so binding constraint #6's amended RED applies to all five: the pre-fix assertion is
written down before implementation starts.

The five, with their current measured sites:

- **XREF-05** — `_sanitize_label` is not injective, so two distinct docnames can share one label
  and a cross-reference whose real target is absent links to a same-spelled decoy
  (`translator.py:5023-5069`, `:5114`; guard at `:3550`).
- **BLD-07** — `make_include_edge_key` does not escape its own `#`/`>` separators, so two
  structurally different include edges can collide onto one key (`translator.py:195-231`).
- **BLD-08** — `derive_master_edge_keys`'s nested `walk()` has no depth bound, so a long include
  chain escapes as a raw `RecursionError` (`translator.py:291-299`).
- **BLD-09** — `_track_image()` gates its whole rehome/relocate/warn branch on bare
  `path.isabs()`, which CPython 3.13's `ntpath` no longer satisfies for a driveless-absolute
  Windows URI (`builder.py:1561`).
- **IMG-03** — the escape branch keys relocation on `basename` alone while the collision branch
  keeps the full `rel_uri`; two escaping URIs sharing a basename collapse onto one key
  (`builder.py:1589` vs `:1602`).

**Not in this phase** (recorded so planning does not drift): the template registry (Phases 53/54)
and the two bundle-directory safety findings (Phase 54.1) are closed and not re-opened; the
documentation rewrite is Phase 56; CHANGELOG *curation* is Phase 57 (this phase authors its own
`Unreleased` entry, per D-03 below). This phase carries **no dependency on the registry** — the
ROADMAP sequences it after 54/54.1 only because those phases concentrate their changes in
`builder.py` and `writer.py`.

</domain>

<decisions>
## Implementation Decisions

### XREF-05 — where the label-collision fix lands

- **D-01:** The fix lands in **`_sanitize_label` (`translator.py:5065`), by making the sanitization
  injective** — the input's own literal escape-token pattern is re-escaped so two distinct
  docnames can never produce one label. It is **not** a Typst-side "does the intended document
  exist" mechanism. Measured basis for the choice: both the definition sites and the reference
  sites already route through this single function (9 call sites in `translator.py`), so the
  demand/supply byte-match XREF-03 depends on is preserved by construction and **zero new Typst
  machinery is introduced**. The two rejected alternatives, and why:
  - *A shared-label `metadata` marker carrying the raw docname as its value* (the direction the
    todo sketches, explicitly "a direction, not a spec"): the existing per-document marker
    `[#metadata(none) <docname:__tsx-doc__>]` (`translator.py:947-950`) cannot serve — its own
    label is on the colliding side. A second, never-linked marker with a document-shared label
    would be needed, and whether a duplicated Typst label is safe under `query()` alone is
    unmeasured. It also adds Typst to every guarded reference site.
  - *Reusing Phase 49's `state("typsphinx:include-edges")`* (`translator.py:192`, `:303-335`): the
    published array holds `parent#0>child` edge keys, not docnames, and a master never appears as
    a child of itself — a separate docname array would have to be published, and the XREF guard
    would acquire a dependency on the include graph.
  — **Reversibility:** reversible — the change is confined to one function; the measured in-tree
  churn is a single fixture docname, and no consumer outside this repository is known to depend on
  emitted label spellings.

- **D-02:** The re-escape targets **the full `_u<hex>_` token pattern only**, not every `_u`
  occurrence — so ordinary ids (`foo_util` and friends) keep byte-identical labels. Measured
  churn: the *products* of the transform are untouched (23 `_u2f_` and 19 `_u40_` expected-value
  occurrences across `tests/` stay as they are, because they come from `/` and `@` inputs that
  contain no escape token); what changes is only a docname/id that **literally spells** `_u<hex>_`,
  and the only such name in the tree is `tests/fixtures/xref_label_collision_guard_gate/a_u2f_b.rst`.
  No second escaping primitive is minted — the rule lives inside `_sanitize_label` and nowhere else.

- **D-03:** The fix is announced in the **`Unreleased` section of `CHANGELOG.md` as `Fixed`, written
  in THIS phase**, not left to Phase 57 (Phase 54's plan `54-03` and Phase 54.1 both set that
  precedent; Phase 57 curates rather than authors). It is **not** a breaking change — v0.9.0's two
  declared breaking axes (template output location, removed config values) stay two. The entry may
  note in passing that a label name changes for an id literally containing the escape token; PDF
  appearance is unchanged, only the `.typ` label name and the PDF link destination name.

- **D-04:** `tests/test_xref_compile_time_guard_render_gate.py::test_label_collision_guard_links_to_decoy`
  is today's **characterization test of the bug** — it asserts that `manual.pdf`'s link destinations
  DO include `a_u2f_b:nested-target`, resolving to the decoy. That currently-passing assertion **is**
  SC#1's "pre-fix link-to-decoy behaviour recorded first"; it is captured as RED evidence and then
  inverted, and the fixture's own `conf.py` load-bearing-properties comment block (a)–(d) is updated
  in the same change so it stops describing an accepted limit.

### Evidence bar per defect

- **D-05:** RED evidence levels, decided per defect rather than uniformly:
  - **XREF-05** — real two-master `sphinx-build -b typstpdf` + `typst.compile()`, as SC#1 already
    requires (the existing collision fixture is that compile).
  - **BLD-07** — **a real `sphinx-build → typst.compile()` fixture** with a `#`-bearing docname.
    Reason: a collided key makes a guard that must not fire, fire, and the child's content silently
    drops out of the emitted output — an output-visible defect. Nearest precedent for fixture shape:
    `tests/fixtures/state_guard_substring_key_gate/`.
  - **BLD-08** — **unit level**, in `tests/test_include_edge_derivation_unit.py`. The defect never
    reaches output (it is an exception-type problem), and the todo states explicitly that a real
    1000-deep fixture is not needed; a synthesized `toctree_includes` mapping is enough.
  - **IMG-03** — **unit level**, in `tests/test_builder.py`, beside the Phase 50 relocation tests
    already there (`test_post_process_images_rehomes_absolute_uri`,
    `test_post_process_images_rehome_collision_relocates_silently`,
    `test_post_process_images_rehome_escape_relocates_with_warning`,
    `test_post_process_images_rehome_cross_drive_value_error_relocates`).
  - **BLD-09** — platform-independent **string-shape** test, as SC#4 already requires, and the fix
    lands on the **product** side (`builder.py:1561`); the 52-09 test-side repair is explicitly not
    accepted as closing it.

### Claude's Discretion

Recorded with a recommendation each; the user deliberately left these to implementation.

- **IMG-03 key derivation.** Recommendation: take the todo's own escape hatch,
  `key = f"{RESERVED_IMAGE_NAMESPACE}/{sha1(resolved_uri)[:8]}-{basename}"` — a pure function of
  `resolved_uri`, so D-02's write-order independence holds, and it contains no `..`, so Phase 50's
  SC#2 outdir containment holds. Whether the **collision** branch (`builder.py:1602`) changes too:
  recommendation **no** — it already keeps the full `rel_uri` and is injective; the defect is the
  asymmetry's escape half only. The existing warning text at `:1590-1593` already names the original
  URI and the new key, so it needs no new content.
- **BLD-08 depth bound.** Recommendation: keep the recursion (COMP-05's sibling-order requirement is
  why it is recursive, and `49-EXPECTED-STRUCTURE.md` names a forward-push LIFO stack as a forbidden
  shape) and thread a depth counter through `walk()`; raise `sphinx.errors.ExtensionError` above a
  **module-level constant with a commented rationale**, not a value read from
  `sys.getrecursionlimit()`. Note when writing the message: a *cycle* cannot reach this bound —
  `traversed` membership only grows, so a cycle is already dark. The message should therefore name
  the depth and the chain (at least head and tail docnames), and should not claim to have found a
  cycle it did not measure.
- **BLD-07 escape spelling.** Recommendation: one replacement rule, written exactly once, inside
  `make_include_edge_key` and applied to the **two docnames only** — never to the `#`/`>` the format
  itself inserts. `escape_typst_string` keeps its current four-character contract; do not widen it,
  since it is used at many sites that do not want `#` escaped.
- **BLD-09 fixture disposition.** Plan 52-09 drive-qualified the fixture in
  `test_post_process_images_rehome_escape_relocates_with_warning` so it stays absolute on Windows
  under CPython 3.13. Recommendation: **add** a driveless-absolute case rather than reverting that
  fixture — reverting would re-red the Windows lane for the wrong reason.
- Plan/wave decomposition, test file naming and placement, and whether the two `translator.py`
  defects (BLD-07, BLD-08) share one plan.

### Folded Todos

All five pending todos `todo.match-phase 55` returned at score 0.9 are folded — each is a 1:1 match
for one of this phase's five assigned requirements, and Phase 54.1 already reviewed and declined
them precisely because they belong here:

- `.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`
  → XREF-05.
- `.planning/todos/pending/2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide.md`
  → BLD-07.
- `.planning/todos/pending/2026-08-14-unbounded-recursion-in-derive-master-edge-keys.md` → BLD-08.
- `.planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md`
  → BLD-09.
- `.planning/todos/pending/2026-08-14-escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide.md`
  → IMG-03.

Each todo carries its own measured reproduction and disposition history; they are the primary
reading for their requirement, listed under Canonical References below.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The five defects, verbatim (primary reading)

- `.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`
  — XREF-05: the collision mechanism, the fixture that characterizes it, and the note that the
  proposed Typst-side remedy is "a direction, not a spec" (superseded by D-01).
- `.planning/todos/pending/2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide.md`
  — BLD-07: the two colliding calls, reproduced independently by orchestrator and verifier, plus
  three candidate repairs.
- `.planning/todos/pending/2026-08-14-unbounded-recursion-in-derive-master-edge-keys.md` — BLD-08:
  why the recursion is deliberate and only the bound is missing.
- `.planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md` —
  BLD-09: the measured `ntpath.isabs()` behaviour change, the sibling idiom to mirror, and why the
  52-09 test-side fix does not close it.
- `.planning/todos/pending/2026-08-14-escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide.md`
  — IMG-03: the branch asymmetry, the write-order dependence it creates, and the hashed-key escape
  hatch T-50-03 already documented.

### Requirements and success criteria

- `.planning/ROADMAP.md` §"Phase 55: v0.8.0-Derived Defects" — the five success criteria. SC#2
  locks "escapes `#` and `>`" for BLD-07; SC#4 locks the
  `posixpath.isabs(…) or _is_drive_qualified(…)` predicate and the product-side placement for
  BLD-09. Neither is re-opened here.
- `.planning/REQUIREMENTS.md` lines 73-87 — XREF-05, BLD-07, BLD-08, BLD-09, IMG-03 requirement
  text; lines 204-208 — the traceability rows this phase flips.

### Milestone contract (binding — do not re-litigate)

- `.planning/ROADMAP.md` lines 392-472 — the eleven binding constraints. Binding here: **#6**
  (RED recorded against the unfixed tree before implementation — D-05 sets the level per defect),
  **#2** (green at every phase boundary), **#11** (zero new runtime deps — note `hashlib` is stdlib;
  `@preview` count stays four with no new lockstep site; typing-import modernization forbidden;
  full pytest + `black`/`ruff`/`mypy` green), **#9** (milestone branch stays pushed to `origin`).
- `.planning/PROJECT.md` §"Current Milestone: v0.9.0 per-document templates".

### Origin of the defects (archived v0.8.0 phases)

- `.planning/milestones/v0.8.0-phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md:519`
  §"Accepted limit — label-collision false negative" — the measurement XREF-05 rests on.
- `.planning/milestones/v0.8.0-phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md`
  §"Fixture: xref_label_collision_guard_gate" — the emission contract the inverted test must keep.
- `.planning/milestones/v0.8.0-phases/49-per-master-include-graph-with-state-guarded-includes/49-REVIEW.md`
  — WR-01 (BLD-07) and WR-02 (BLD-08) verbatim.
- `.planning/milestones/v0.8.0-phases/49-per-master-include-graph-with-state-guarded-includes/49-EXPECTED-STRUCTURE.md`
  §"Emission contract" — the single edge-key derivation point, and the LIFO work-stack named as a
  forbidden shape (load-bearing for BLD-08's "keep the recursion" recommendation).
- `.planning/milestones/v0.8.0-phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md`
  — the state-syntax probes (Probe 5's single-element trailing-comma hazard, Probe 7's one-line
  `if`), which any change to key emission must not invalidate.
- `.planning/milestones/v0.8.0-phases/50-pr-131-image-path-defects/50-REVIEW.md` (CR-01) and
  `50-CONTEXT.md` (D-01…D-07, especially D-02's write-order independence and D-05/D-06's escape
  branch) — the contract IMG-03's new key must not break.
- `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md` — the
  `ntpath.isabs()` measurement and CI job log BLD-09 is built from.

### Prior phase context (do not re-litigate)

- `.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-CONTEXT.md`
  §"Reviewed Todos (not folded)" — records that these five todos were deliberately left for this
  phase.
- `.planning/phases/53-template-registry-foundation/deferred-items.md` — the pre-existing
  `tests/test_state_guard_shapes_gate.py` failure (7 tests reading an archived `.planning/` path,
  moved by commit `2ea4db0f`). It predates Phase 53, is still open, and **will** surface in this
  phase's full-suite green gate. It is not a regression this phase caused — and note that the file
  is a Phase 49 artifact, so an executor touching BLD-07/BLD-08 will meet it.

### Source of truth in code

- `typsphinx/translator.py:141-172` — `escape_typst_string()`, the four-character contract BLD-07
  must not widen.
- `typsphinx/translator.py:195-231` — `make_include_edge_key()`, the single edge-key derivation
  point (BLD-07).
- `typsphinx/translator.py:234-300` — `derive_master_edge_keys()` and its nested `walk()` (BLD-08).
- `typsphinx/translator.py:303-335` / `:338-377` — `render_include_edge_state()` /
  `render_include_guard()`, the two emission sites a changed key format flows into.
- `typsphinx/translator.py:3480-3554` — `_label_existence_guard()`, the single guard-string
  derivation point (XREF-05; unchanged under D-01).
- `typsphinx/translator.py:5023-5069` — `_sanitize_label()`, where D-01/D-02 land;
  `:5080-5116` — `_namespace_label()`, its only caller for docname-namespaced labels.
- `typsphinx/translator.py:935-950` — `visit_document`'s whole-document self-anchor, the marker
  D-01 considered and rejected as an existence mechanism.
- `typsphinx/builder.py:85-118` — `_is_drive_qualified()`; `:120-161` — `_escapes_outdir()`, whose
  own comment states the platform-independence reasoning BLD-09 must mirror.
- `typsphinx/builder.py:1499-1616` — `_track_image()`: `:1561` is BLD-09's bare `path.isabs()`,
  `:1589` is IMG-03's basename-only key, `:1602` is the asymmetric collision-branch key.

### Tests and fixtures

- `tests/test_xref_compile_time_guard_render_gate.py:328-360` —
  `test_label_collision_guard_links_to_decoy`, the characterization test D-04 inverts;
  `:50`, `:71`, `:190-225` — the fixture path, guard pattern and per-class build fixture it uses.
- `tests/fixtures/xref_label_collision_guard_gate/` — `conf.py` (load-bearing properties (a)–(d)),
  `index.rst`, `a/b.rst` (`:orphan:`), `a_u2f_b.rst` (the decoy).
- `tests/test_include_edge_derivation_unit.py` — the unit home for BLD-07's and BLD-08's REDs.
- `tests/fixtures/state_guard_substring_key_gate/` — the nearest fixture precedent for BLD-07's
  real-compile gate.
- `tests/test_builder.py:392-660` — the Phase 50 relocation unit tests IMG-03's RED sits beside,
  including `test_post_process_images_rehome_escape_relocates_with_warning` (:511), the one plan
  52-09 drive-qualified, and `test_copy_image_files_relocated_key_destination_stays_under_outdir`
  (:629), which pins the outdir-containment property a new key must keep.
- `tests/test_state_guard_shapes_gate.py` — currently 7 failing tests for the archived-path reason
  above; a BLD-07 key-format change also passes through this file's warning-baseline assertions.

### Project conventions

- `CLAUDE.md` §"Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then everything through
  `uv run`. Worktree isolation is the standing execution mode.
- `CLAUDE.md` §"The `@preview` version-sync hazard" — three sites in lockstep; this phase adds no
  fourth.
- `CLAUDE.md` §"Conventions & gotchas" — typing-import modernization forbidden; line length 88.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `_is_drive_qualified()` + `posixpath.isabs()` (`builder.py:85-118`, used at `:161`) — the exact
  platform-independent predicate BLD-09 routes `_track_image()` onto. No new predicate is minted;
  `_escapes_outdir()`'s own inline comment already carries the measured rationale.
- `escape_typst_string()` (`translator.py:141`) — stays as-is; BLD-07's separator escaping is a
  *second, narrower* rule applied inside `make_include_edge_key` only.
- `_sanitize_label()` (`translator.py:5023`) — the single label-alphabet primitive, reached by all
  9 label-emitting sites through `_namespace_label()`. XREF-05's whole fix fits inside it.
- The Phase 50 relocation test cluster (`tests/test_builder.py:392-660`) — the established shape for
  an IMG-03 RED: build a `temp_sphinx_app`, plant the URI, assert on `self.images` keys.

### Established Patterns

- **One derivation point per shared string.** `make_include_edge_key`, `_sanitize_label`,
  `_label_existence_guard` and `_collision_key` each exist because a second, independently-spelled
  expression is the drift class this codebase rejects. Every fix in this phase must land *inside*
  the existing single point, never beside it.
- **A collided/mismatched key fails silently, by design of the surrounding machinery.** BLD-07's
  guard fires wrongly, IMG-03's image is replaced, XREF-05's link lands on a decoy — none raises.
  That is why D-05 puts BLD-07 on a real compile: only the output shows it.
- **Emission changes are pinned by real `typst.compile()` fixtures recorded RED first** (GATE-01
  since v0.6.0, amended in v0.7.0 to require the pre-fix assertion be written down).
- **Warnings carry no `type`/`subtype`** (Phase 54 D-08) — nothing here becomes the first
  individually-suppressible warning.

### Integration Points

- `derive_master_edge_keys()` is imported by `builder.py:27` and called at `:459` inside
  `_build_include_edge_map()` — BLD-08's `ExtensionError` surfaces through that call path.
- `make_include_edge_key()` has exactly two callers — the graph side (`translator.py:294`) and the
  emission side (`translator.py:5336`, `visit_toctree`) — so a key-format change reaches both
  automatically; the risk is *fixture expected-bytes*, not drift.
- `_track_image()` is called from `builder.py:1461` and `:1497`; its `self.images` keys feed
  `copy_image_files()` and the translator's `_compute_relative_image_path()`.
- `_sanitize_label()` output reaches the `.typ` as both `<label>` definitions and
  `link(<label>, …)` / `query(<label>)` arguments — so any change shows up in every render-gate
  test that asserts emitted label bytes.

</code_context>

<specifics>
## Specific Ideas

- The five defects are independent by subject matter; nothing forces one order. The only real
  coupling is file contention (`translator.py` for XREF-05/BLD-07/BLD-08, `builder.py` for
  BLD-09/IMG-03), which is a wave-packing concern, not a dependency.
- BLD-07 and BLD-08 are both Phase 49 artifacts and sit in adjacent code; treating them as one plan
  is reasonable, but their evidence levels differ (real compile vs unit) — do not let the shared
  plan blur that.
- BLD-09 and IMG-03 both live in `_track_image()` and both were surfaced by Phase 50/52. A single
  plan touching that function twice is likely cheaper than two, but each still needs its own RED.
- The pre-existing `tests/test_state_guard_shapes_gate.py` failure will be present at this phase's
  green gate. Planning should decide up front whether to fix the archived path as an in-scope
  side-repair or to record it as a known pre-existing red — silently absorbing it into "the suite
  is green" is the failure mode to avoid.

</specifics>

<deferred>
## Deferred Ideas

- **Typst-side "does the intended document exist" evidence** (a shared-label `metadata` marker
  carrying the raw docname, or a published docname array alongside the include-edge state). Rejected
  for XREF-05 under D-01 because the sanitizer fix closes the same gap with no new Typst machinery.
  If a future requirement needs docname-level evidence at compile time (e.g. distinguishing
  "target absent" from "target present but unlabelled"), it deserves its own requirement.
- **Widening `escape_typst_string()` to escape `#`/`>`** — rejected under Claude's Discretion above:
  it is used at many sites that do not want `#` escaped, and widening it would churn unrelated
  emitted bytes.
- **Reverting plan 52-09's drive-qualified fixture** — recommendation is to add a driveless case
  instead; if a later phase wants the original fixture shape back, it is a separate decision.
- **Making `_track_image()`'s collision branch hash-keyed too** — recommendation is no; the branch
  is already injective. Recorded so a reviewer does not read the remaining asymmetry as an
  oversight.

### Reviewed Todos (not folded)

- `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`
  (score 0.6, area `ci, release`) — REL-04's end-to-end proof that `release.yml`'s `create-release`
  job works. Matched only on the generic keywords "phase"/"milestone"; it is release-pipeline work
  and belongs with a release phase, not with the five product defects scoped here.

</deferred>

---

*Phase: 55-v0-8-0-derived-defects*
*Context gathered: 2026-08-16*
