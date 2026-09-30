# Phase 51: Two-Layer Output Documentation - Context

**Gathered:** 2026-08-14
**Status:** Ready for planning

<domain>
## Phase Boundary

The published documentation catches up with the output shape Phases 47 and 49 built. A reader must
be able to tell, from the docs alone, which of the two `.typ` files typsphinx now writes is the one
to compile, what happens if they compile the other one, what a `typst_documents` target means now
that it is a path, and what changed from v0.7.x in old→new file names.

This phase writes prose and one verification gate. It changes **no** behaviour in `typsphinx/` —
every claim it publishes is a claim about code that already shipped in Phases 47–50.

The surface is wider than `docs/source/`: the docs were last touched in Phase 46 (v0.7.1), so
`configuration.rst` currently publishes the *reversed* OUT-01 contract, and `README.md` and
`examples/**/README.md` carry claims the two-layer split falsified.

</domain>

<decisions>
## Implementation Decisions

### Placement and page structure

- **D-01:** The two-layer explanation gets its **own new page under `docs/source/user_guide/`**
  (working name `output_layout.rst`), added to `user_guide/index.rst`'s toctree, carrying: the
  wrapper/content split and which file to compile, target-as-path with worked examples, the refusal
  cases, the standalone-content behaviour, the collision rules, and the shared-child composition
  behaviour. `builders.rst` and `configuration.rst` link to it rather than duplicating it —
  **Reversibility:** reversible — a new page is additive; the alternative (growing the existing
  four-line `Output` sections in `builders.rst` and the tuple contract at
  `configuration.rst:43-79`) was rejected because the content volume plainly exceeds those sections'
  granularity and would scatter one explanation across two pages with no home for the
  standalone/composition material.

- **D-02:** "What changed from v0.7.x" lives in **`docs/source/changelog.rst`'s existing
  `Migration Guides` section**, as a new `Migrating from 0.7.x to 0.8.0` subsection following the
  `Migrating from 0.7.0 to 0.7.1` pattern Phase 46 established (before/after code blocks, one bullet
  per breaking change). The new user-guide page states the *current* contract only —
  **Reversibility:** reversible — this keeps migration information in exactly one place and matches
  the shape a reader already found for the previous release.

- **D-03:** `README.md` **is in scope**, limited to **correcting the false claims** and linking to
  the new page. `README.md:82-85` ("each entry produces one emitted `.typ` file") and the
  `typst_documents` line at `README.md:228` are false after the split. No full two-layer explanation
  and no worked examples are added to `README.md` — **Reversibility:** reversible — README is the
  PyPI front page, so shipping v0.8.0 with a false statement there is not acceptable, but
  duplicating the contract would create a second surface to keep in sync.

### Stale-claim sweep

- **D-04:** The search for falsified claims is **repo-wide at discovery time**, not limited to the
  pages named in this discussion. The sweep covers `docs/source/**`, `README.md`, and
  `examples/**/README.md`; `.planning/`, `tests/`, and `typsphinx/` are excluded. Every falsified
  claim found is fixed in this phase — **Reversibility:** reversible — a repo-wide grep is the only
  way this closes; measured examples already outside `docs/source`:
  `examples/advanced/README.md:60-64` claims "The master document (`advanced-example.typ`) uses
  `#include()` directives" when `advanced-example.typ` is now the wrapper that includes `index.typ`,
  with the chapter includes living state-guarded inside `index.typ`.

  Known-false sites measured during this discussion (a starting set for the sweep, **not** the
  closed list — the plan must re-derive the list by grep):
  - `docs/source/user_guide/configuration.rst:46-52` — "Output filename stem … A path component is
    not supported: a path-bearing value produces a build warning and the file is written under its
    basename next to the source document". OUT-01 reversed this; recorded as inherited by DOC-14 in
    `47-08-SUMMARY.md:212` and `47-SECURITY.md` R-47-01.
  - `docs/source/user_guide/builders.rst:114-121` — the "second tuple element is the output filename
    stem" paragraph and its CLI-walkthrough caveat.
  - `docs/source/user_guide/builders.rst:61` and `:170`, `docs/source/user_guide/templates.rst:458-462`
    — `typst compile build/typst/index.typ output.pdf` / `cat build/typst/index.typ`.
  - `README.md:82-85`, `README.md:228`.
  - `examples/advanced/README.md:60-64`.

- **D-05:** The Phase 47 **collision hard-error is documented in both places** — as a contract on
  the new page ("which targets are refused") and as a migration bullet in `changelog.rst`. Measured:
  `typsphinx/builder.py:611` raises `ExtensionError("typst: N output path collision(s): …")` and no
  output file is written when any collision is found; the four claimants are the reserved
  `_template.typ`, every docname's own content file, every entry's wrapper, so
  `typst_documents = [("index", "index.typ", …)]` **builds in v0.7.x and fails in v0.8.0** —
  **Reversibility:** reversible as documentation; the underlying behaviour is one-way. SC#1/SC#2 do
  not name collisions, so this is a deliberate widening of the page's contract coverage, taken
  because a user choosing a target needs the refusal rules in the same place as the path rules.

- **D-06:** Every `typst compile …` / `cat …` command example is rewritten to **the wrapper name
  that example's own `conf.py` actually produces** (for an unset `typst_documents`, `<project>.typ`),
  rather than being replaced by a generic "read the builder's `compile these:` line" instruction —
  **Reversibility:** reversible. Measured basis: while a docname `index` exists, `index.typ` is
  always the *content* file, because a target of `index.typ` for docname `index` is the
  self-collision D-05 refuses. Today's examples therefore silently produce a child-less PDF.

### How behaviours and limitations are written

- **D-07 (owner override):** The `:numref:` divergence is **not documented at all** in v0.8.0. The
  owner classifies it as a bug to be fixed in a later milestone, not a limitation to publish, so it
  appears in no page, no admonition, and no sentence of `docs/source/**` or `README.md` —
  **Reversibility:** costly — it reverses a decision recorded across three prior artifacts, and
  reversing it again means re-deriving prose from the measurement. **This directly contradicted
  ROADMAP Phase 51 SC#3 as written**, which required "open question #2's `:numref:` divergence …
  appears here in the user's language"; on the owner's instruction, `ROADMAP.md` SC#3 was amended in
  this discussion (2026-08-14) to exclude `:numref:` explicitly and to name this decision. Prior
  artifacts that still record the superseded "document it" plan, and must **not** be read as live
  instructions: `49-CONTEXT.md` D-01, `49-EVIDENCE.md` §"numref measurement" (its "Fix-or-document
  decision" paragraph and handoff item 3), and
  `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`.
  The measurement itself stays on the record in `49-EVIDENCE.md` — only its publication is dropped.

  **Extended to Phase 52 on the same owner instruction (2026-08-14):** the decision covers the
  v0.8.0 CHANGELOG as well, so `:numref:` appears in neither `docs/source/**`, `README.md`, nor
  `CHANGELOG.md` for this release. `ROADMAP.md` Phase 52 SC#2 was amended to exclude it explicitly,
  and the tracking todo's `resolves_phase` was moved from `52` to `null` with its superseded Phase
  51 / Phase 52 obligations struck through in place — no v0.8.0 phase resolves it, and a later
  milestone picks it up.

- **D-08:** The **standalone content-file behaviour is written as prose inside the "which file to
  compile" section**, not as a `.. note::` or a limitation entry. Measured (Phase 49, real build):
  compiling `shared.typ` directly with no wrapper **succeeds** and yields only that document's own
  body — its state-guarded children are absent, with no error and no warning at any layer —
  **Reversibility:** reversible. This satisfies SC#1's requirement that it read as intended,
  well-defined behaviour rather than something to be reported as a bug; an admonition would give it
  a warning tone inconsistent with D-07's treatment of the genuinely defective case.

- **D-09:** The **shared-child composition behaviour is documented as part of the two-layer
  specification**: a document reachable from several masters renders in each master's PDF exactly
  once, at that master's own traversal position, and its heading level varies per master. Measured
  (Phase 49 `state_guard_three_master_gate`): `COMMON-B-MARKER` count = 1 in all three masters'
  PDFs; resolved heading levels for `common_b` = `[3]` in m1 (nested under `mid`) and `[2]` in m2
  and m3 — **Reversibility:** reversible. This is the milestone's headline behaviour change (v0.7.x
  could only place a shared child in one master — defect A), so a reader needs it to confirm the fix
  landed.

### SC#3 verification

- **D-10:** SC#3 is discharged by **one new permanent gate test** under `tests/`, not by a
  throwaway harness with recorded evidence. Precedent chosen: `tests/test_quickstart_docs_gate.py`
  (real `sphinx-build` subprocess + published prose read from disk). The rejected alternative is
  Phase 45.1's D-J pattern (build twelve examples in a scratch harness, record the transcript, put
  nothing under `tests/`) — **Reversibility:** reversible — a permanent gate is chosen precisely
  because the failure this phase is fixing is *documentation drifting unnoticed across four phases*;
  a one-shot transcript cannot catch the next drift.

- **D-11:** The gate follows the **existing gate's shape**: fixtures live under `tests/fixtures/`,
  and the test reads the published `.rst` / `.md` text from disk with `Path` and asserts the file
  names the page claims against the file set a real build emits, deriving expected values from the
  same helpers the builder uses rather than hard-coding them. `literalinclude`-ing a fixture
  `conf.py` into the page, and parsing config out of the page's code blocks, are both rejected —
  **Reversibility:** reversible — the chosen shape keeps the page readable and does not make the
  docs build depend on `tests/`.

- **D-12:** The gate builds with **`-b typst` only** and must **never skip**: it asserts the emitted
  `.typ` file set, which is exactly what SC#3 asks for, and takes no `typst-py` dependency.
  PDF-level verification is out of the gate — **Reversibility:** reversible — measured constraint:
  `typst-py` is unavailable in this project's NixOS sandbox, and a gate that skips there is a gate
  that does not run where the docs are most often edited.

### Claude's Discretion

- The new page's final filename, title, and section order (D-01 fixes only that it is a new page
  under `user_guide/` and what it must contain).
- The exact worked-example configurations used on the page and in the gate fixtures, provided each
  one is actually built (SC#3) and covers: a bare target at the output root, an explicit path
  target, and the refusal cases (`..`, absolute, drive-qualified).
- Whether the sweep's fixes to `examples/**/README.md` also touch those examples' `conf.py` files,
  as long as no documented claim is left false.
- All wording, including the user-facing name for the docname-named file ("content file" is the
  planning vocabulary; "wrapper" is already user-visible in the builder's own
  `typst: wrote N wrapper file(s) -- compile these: …` message at `builder.py:767-770` and should
  stay).

### Folded Todos

- `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`
  — folded only to be **explicitly dismissed for this phase** by D-07. Its `resolves_phase` is 52
  and its Phase 51 documentation obligation is superseded by the owner decision recorded above. Do
  not treat its text as a live instruction for this phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` §"Phase 51: Two-Layer Output Documentation" (lines 830-863) — the goal and
  the three success criteria. **SC#3 was amended on 2026-08-14** by D-07; read the amended text, not
  any quotation of the original elsewhere.
- `.planning/REQUIREMENTS.md:97-99` — DOC-14, the phase's single requirement.
- `.planning/PROJECT.md:134-144` — the "Known residual risk" note (standalone content compile sees
  an empty state, includes no children) and the "User-visible output-shape change" note naming the
  `manual.typ` / `index.typ` pair and v0.7.1's own `index.typ` → `<project>.typ` default-derivation
  rename that must not be confused with it.

### The behaviour being documented (measurements, not design)

- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md`
  §"Handoff to Phase 51 and Phase 52" — the standalone-compile measurement (real build transcript)
  and the completed two-layer shape description. **Item 3 of that handoff and the whole §"numref
  measurement" are superseded for publication purposes by D-07** — read them for the facts, not for
  the obligation.
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md`
  §"Degenerate-shape closure" — the three-master shared-child measurement D-09 documents, plus the
  cycle / self-reference / `self` / external-URL / `:glob:` / `:orphan:` / duplicate-entry outcomes.
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-CONTEXT.md`
  — D-01..D-09, in particular D-01/D-03 (collisions are errors, not warnings) and D-07 (the
  `-b typst` builder names the wrapper files to compile).
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-08-SUMMARY.md:212`
  — the verbatim record of the OUT-01-falsified `configuration.rst` claim, explicitly handed to
  DOC-14.
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-SECURITY.md`
  R-47-01 — the same handoff as an accepted residual risk with an owner and a date.

### Code the documentation must agree with

- `typsphinx/builder.py:296-420` — `_resolve_target_stem()`: `.typ` stripping, backslash
  normalization, the OUT-02 escape guard and its basename fallback, the degenerate-target docname
  fallback, and the exact warning strings.
- `typsphinx/builder.py:36-114` — `_is_drive_qualified()` and `_escapes_outdir()`, the predicates
  behind "refused with a warning and a safe fallback".
- `typsphinx/builder.py:502-613` — `_validate_output_path_collisions()`: the four claimant kinds and
  the single aggregated `ExtensionError` D-05 documents.
- `typsphinx/builder.py:755-770` — the `typst: wrote N wrapper file(s) -- compile these: …` message
  that is already user-visible vocabulary.
- `typsphinx/builder.py:967-1011` — `_content_output_path()` and `_wrapper_output_relpath()`, the
  two file names every worked example must match.
- `typsphinx/builder.py:169-190` — `_default_typst_documents()`, the derived entry behind
  `<project>.typ`.

### Documentation surfaces in scope

- `docs/source/user_guide/index.rst` — the toctree the new page joins.
- `docs/source/user_guide/configuration.rst:23-79` — the `typst_documents` tuple contract, element
  by element; element 2 is the falsified one.
- `docs/source/user_guide/builders.rst` — `Output` sections (lines 35-41, 75-81),
  `Manual Compilation` (50-61), `Document Definitions` (103-121), `Common Workflow` (145-183).
- `docs/source/user_guide/templates.rst:453-462` — the `.typ`-inspection walkthrough.
- `docs/source/changelog.rst:1-130` — the `.. include::` of `CHANGELOG.md` plus the
  `Migration Guides` section D-02 extends.
- `docs/source/quickstart.rst:38,72-74,92-102` — build steps and output file naming.
- `README.md:80-102`, `README.md:228` — the `typst_documents` description D-03 corrects.
- `examples/basic/README.md`, `examples/advanced/README.md` — the example walkthroughs D-04's sweep
  reaches.

### Verification precedents

- `tests/test_quickstart_docs_gate.py` — the shape D-10/D-11 adopt: a real `sphinx-build`
  subprocess against a `tests/fixtures/` project, a second class that reads the published prose and
  never skips, and expected values derived from `make_filename_from_project` rather than
  hard-coded.
- `tests/test_docs_contract_claims_gate.py` — the prose-versus-code guard, including its explicit
  "do not extend across the D-J fence" boundary; a new gate must not be bolted onto it.
- `tests/test_typst_documents_collision_gate.py`, `tests/test_builder_output_stem.py` — the current
  assertions about target resolution and collisions; the documentation must not contradict them.

### Project conventions

- `CLAUDE.md` — the mandatory per-worktree provisioning protocol
  (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then everything via
  `uv run`), which applies to every executor in this phase too.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tests/test_quickstart_docs_gate.py` is a working two-class template for D-10: one class runs a
  real `sphinx-build` subprocess (`sys.executable -m sphinx`) against a fixture and asserts the
  emitted file names; the other reads `README.md` / `quickstart.rst` from disk and asserts the
  published text, with no optional dependency so it never skips.
- `tests/fixtures/state_guard_two_master_gate` and `tests/fixtures/state_guard_three_master_gate`
  already encode multi-master projects whose emitted file sets demonstrate the two-layer shape; a
  documentation gate can reuse their shapes rather than inventing new ones.
- `docs/source/changelog.rst`'s `Migrating from 0.7.0 to 0.7.1` subsection (added in `27cff2af`) is
  the literal format D-02 follows: one bullet per breaking change, each with a "what you have today"
  and a "what to replace it with" code block.

### Established Patterns

- Docs claims in this project are guarded by tests that read the published file from disk, never by
  duplicating the claim in a docstring — both existing gates do it that way.
- The builder emits its own inventory of files to compile (`builder.py:767-770`), so the docs can
  point at a real runtime signal instead of asking the reader to compute a filename.
- `docs/source/conf.py:72-74` sets `typst_documents = [("index", "typsphinx", project, author,
  "typst")]`, so this project's own docs build is itself a two-layer example: wrapper
  `typsphinx.typ`, content `index.typ`. `tox -e docs-pdf` exercises it.

### Integration Points

- `docs/source/user_guide/index.rst`'s toctree and its `Main Topics` definition list both need the
  new page added — the second one is easy to miss.
- `docs/source/changelog.rst` renders `CHANGELOG.md` through `myst_parser` (DOC-12's mechanism), so
  the Migration Guides section is the only hand-written part of that page; Phase 52 edits the
  repo-root `CHANGELOG.md` and must not need a second edit here.
- Any new gate joins the suite `pytest -m "not slow"` runs; it must stay dependency-free per D-12.

</code_context>

<specifics>
## Specific Ideas

- The worked examples must show target-as-path in the three shapes SC#2 names: a bare target
  (`"manual"` → `manual.typ` at the output root), an explicit path target
  (`"manuals/guide.typ"` → `manuals/guide.typ`), and a refused target (`..`-bearing, absolute, or
  drive-qualified → warning + basename fallback).
- The "what changed" bullet must name a concrete config and its concrete before/after file set, and
  must sit next to v0.7.1's own `index.typ` → `<project>.typ` default-derivation rename so a reader
  cannot confuse the two renames. The canonical illustration is
  `typst_documents = [("index", "manual.typ", …)]`: v0.7.x wrote `manual.typ` as the whole document;
  v0.8.0 writes `manual.typ` as the wrapper and `index.typ` as the body.
- `examples/advanced/README.md:60-64,118-123` is the highest-value sweep target after the user-guide
  pages: it shows the master document's `#include()` block verbatim, which the state-guarded
  emission has changed in both location and form.

</specifics>

<deferred>
## Deferred Ideas

- **`:numref:` numbering divergence.** Not documented anywhere in v0.8.0 by owner decision (D-07) —
  not in `docs/source/**`, not in `README.md`, not in `CHANGELOG.md` — and to be fixed as a bug in a
  later milestone. ROADMAP SC#3 (Phase 51) and SC#2 (Phase 52) were both amended on 2026-08-14 to
  exclude it. Tracked, with `resolves_phase: null`, in
  `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`.
- **A short two-layer explanation in `README.md`.** Considered and declined (D-03) — README gets
  only the false-claim corrections plus a link.
- **Cross-reference degradation when a content file is compiled standalone.** Raised in Phase 48 Q4;
  the owner's answer there was "手当の必要があると思えない" — no mitigation and no handoff note. Not
  reopened here.

### Reviewed Todos (not folded)

- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — a CI job, not documentation content; unrelated to
  DOC-14.
- `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`,
  `2026-08-14-escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide.md`,
  `2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide.md`,
  `2026-08-14-unbounded-recursion-in-derive-master-edge-keys.md` — code defects from Phases 48-50
  reviews, not documentation obligations.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — toolchain, `resolves_phase: null`.

</deferred>

---

*Phase: 51-Two-Layer Output Documentation*
*Context gathered: 2026-08-14*
