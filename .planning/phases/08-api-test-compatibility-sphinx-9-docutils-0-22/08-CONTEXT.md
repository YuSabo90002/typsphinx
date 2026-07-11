# Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) - Context

**Gathered:** 2026-07-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Confirm the translator / writer / builder / config-registration layer is compatible with the
resolved **Sphinx 9.1 + docutils 0.22** stack, modernize the soft-deprecated docutils API, and get
the **full pytest suite (~400 tests, incl. the now-`kai`-free PDF integration tests) green** on the
new stack — with the tree `black`/`ruff`/`mypy` clean.

Requirements covered: **API-01, API-02**.

**Locked scope anchors (carried forward — do NOT re-litigate):**
- **API-01 is mechanical & locked:** replace the deprecated `doctree.traverse(addnodes.toctree)` at
  `typsphinx/template_engine.py:239` with `doctree.findall(...)` (consistent with the existing
  `builder.py:151` `findall` usage). No `traverse()` deprecation warning may remain.
- **Latest-only forward-port** (REQUIREMENTS.md / STATE.md): raise-forward to Sphinx 9.1 / docutils
  0.22; **no** Sphinx-8/docutils-0.21 compatibility range or version-conditional branching.
- **Branch strategy carried from Phase 6/7** (06-CONTEXT.md D-01/D-02): all work stays on
  `release/v0.5.0`; `main` stays green throughout; merge to main only at milestone completion via
  GitHub PR.
- **Done-ness gate = full suite green + clean tree.** SC3 (~400 tests incl. PDF integration pass) +
  SC4 (`black`/`ruff`/`mypy` clean) are the blocking gates. The PDF integration tests are unblocked
  because Phase 7 already closed the `kai` compile break.
- **NOT this phase:** the CI-matrix green observation + dedicated `typst compile` smoke test +
  drift/Dependabot ceiling bumps are **Phase 9** (CI-01/CI-02/CI-03); the `__version__`→0.5.0 fix +
  PyPI release are **Phase 10** (REL-01).

</domain>

<decisions>
## Implementation Decisions

### Deprecated-API sweep breadth (discussed)
- **D-01: Thorough audit — modernize ALL soft-deprecated docutils/Sphinx API, not just the one known
  `traverse()`.** The user explicitly chose the *徹底監査* (exhaustive) stance over the minimal
  "fix only what breaks" and the mid "light grep" options. Phase 8's API-modernization scope is
  therefore **expanded beyond API-01's single `template_engine.py:239` call**: proactively find and
  replace every soft-deprecated docutils/Sphinx call the extension uses (e.g. `traverse()`→`findall()`
  everywhere, deprecated `nodes`/`addnodes` attribute access, deprecated logging/util API, deprecated
  builder/translator hooks), reducing future forward-port debt. The Sphinx-9 changelog audit found no
  *load-bearing* breaks (only `traverse()` known) — this decision converts that into a clean-posture
  sweep rather than a wait-for-breakage patch.

### Deprecation-warning strictness (discussed)
- **D-02: Install a PERMANENT deprecation guard.** The user chose *恒久ガード導入* over the lightweight
  "verify zero warnings by hand, add no gate" option. Add `filterwarnings = error::DeprecationWarning`
  (scoped appropriately) to the pytest config (`pyproject.toml` `[tool.pytest.ini_options]`) so any
  future `DeprecationWarning` fails the suite loudly — this structurally enforces D-01 (the thorough
  sweep) and prevents silent re-accumulation of deprecated API.
  - **Third-party escape hatch:** deprecation warnings originating from *dependencies* (Sphinx,
    docutils, typst-py, pytest plugins) that typsphinx cannot fix must be excluded via targeted
    `ignore::DeprecationWarning:<module>` entries — NOT by weakening the global `error` default. Keep
    the ignore-list minimal, module-scoped, and commented with why each is unfixable-in-our-code.
    Planner/researcher determine the concrete ignore entries empirically from the first suite run.
  - **Interaction with D-01:** turning the guard on will surface *our* remaining deprecations as test
    failures — that failure list IS the work-list for the D-01 sweep. Land the sweep first (or in the
    same wave) so enabling the guard leaves the suite green.

### Claude's Discretion (planner/researcher decide with these defaults)
- **Test-failure fix bias (area surfaced but NOT selected for discussion → default locked here):**
  When a test goes red on the new stack, **prefer fixing the source to preserve the existing `.typ`
  output over rewriting test expectations** — UNLESS the red is caused by a genuine, intended
  docutils/Sphinx output/structure change (e.g. the docutils 0.22 definition-list node shape), in
  which case adapt the translator to the new node shape and update the fixture to the new *correct*
  output. Rationale: this is a forward-port whose core value is "builders produce **correct** output";
  silently loosening assertions to make red go green would hide real regressions. Document any fixture
  change with a one-line why.
- **docutils 0.22 multi-`<term>` definition-list edge case:** implementation-level; planner/researcher
  handle it. Current `visit_term`/`depart_term` (`translator.py:1047-1085`) buffers a **single** term
  per `definition_list_item` (`current_term_buffer` is overwritten, not appended). If docutils 0.22
  emits multiple `<term>` children per item, this silently drops all but the last term — verify against
  the resolved docutils 0.22 and fix if the node shape changed. Spot-check flagged in STATE.md
  Blockers.
- **Sweep mechanics / grep patterns / findall signature:** planner decides how to enumerate deprecated
  calls (changelog cross-ref + grep + running the suite under the new guard) and the exact `findall`
  replacement form.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (locked)
- `.planning/REQUIREMENTS.md` — **API-01** (`traverse()`→`findall()` at `template_engine.py:239`) and
  **API-02** (Sphinx 9.1 + docutils 0.22 compat confirmed, full suite green). Read before planning.
- `.planning/ROADMAP.md` §"Phase 8" — the 4 success criteria (SC1 findall swap + no traverse warning;
  SC2 no `AttributeError`/`TypeError`/deprecation-removal breakage incl. docutils 0.22 multi-`<term>`
  edge case; SC3 ~400-test suite incl. PDF integration passes; SC4 `black`/`ruff`/`mypy` clean).
- `.planning/PROJECT.md` — milestone core value ("builders produce **correct** output, every CI job
  green on the current ecosystem"); Key Decisions table; the Phase-7 follow-up admonition-bug note.

### Carried-forward context
- `.planning/STATE.md` §"Blockers/Concerns" — the two Phase-8 landmines: (1) re-verify Sphinx 9 API
  empirically against the *resolved* deps (runtime `AttributeError`/`TypeError` may surface even though
  the changelog audit found no load-bearing breaks); (2) spot-check the docutils 0.22 multi-`<term>`
  definition-list edge case.
- `.planning/phases/07-bump-preview-packages-typst-0-15-kai-fix/07-CONTEXT.md` — Phase 7 verification
  stance + the "forward-port, not redesign; minimize scope" posture carried into this phase.
- `.planning/phases/07-bump-preview-packages-typst-0-15-kai-fix/deferred-items.md` — the admonition
  rendering bug (see `<deferred>` below); explicitly NOT fixed in this phase.

### Code sites (the modernization targets)
- `typsphinx/template_engine.py:239` — the locked `traverse()`→`findall()` swap (API-01).
- `typsphinx/builder.py:151` — the reference `findall()` usage to stay consistent with.
- `typsphinx/translator.py:1047-1110` — `visit_term`/`depart_term`/`visit_definition` (single-term
  buffering; the docutils 0.22 multi-`<term>` spot-check target).
- `pyproject.toml` `[tool.pytest.ini_options]` — where the `filterwarnings` guard (D-02) lands.
- `CLAUDE.md` — the `N802` ruff-ignore note (docutils visitor PascalCase methods) + the Python-3.10+
  typing-import caveats (still `UP006`/`UP035`-ignored — but note the floor is now 3.12 per Phase 6;
  planner should not "modernize" typing imports even so).

### Deprecation guard reference (external)
- Sphinx 9 / docutils 0.22 changelogs — cross-reference to enumerate soft-deprecated API surfaces for
  the D-01 sweep (planner/researcher fetch as needed; no load-bearing break found in the prior audit
  beyond `traverse()`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`builder.py:151` `doctree.findall(image)`**: the extension already uses the modern `findall`
  iterator — the API-01 swap and any D-01 sweep replacements should mirror this exact call shape for
  consistency.
- **Full pytest suite (~402 tests)**: already green on the prior stack per Phase 7; run it under the
  new deps to surface breakage. The suite is the empirical gate (SC3) and, once the D-02 guard is on,
  the deprecation-detection mechanism.
- **`tests/test_preview_version_sync.py`**: keep green (unaffected by this phase, but part of the
  ~400-test suite).

### Established Patterns
- **docutils visitor pattern (PascalCase methods, `N802` ruff-ignored)**: any new/edited `visit_*`/
  `depart_*` methods keep the PascalCase convention (e.g. `visit_Text`) — do not "fix" the lint.
- **Python 3.10+ typing-import caveat (`Dict`/`List`, `UP006`/`UP035` ignored)**: even though the floor
  is now 3.12 (Phase 6), CLAUDE.md still forbids modernizing these typing imports — the sweep is for
  *docutils/Sphinx* deprecations, NOT a general "modernize the codebase" pass.
- **Single-term definition-list buffering**: `translator.py` assumes one `<term>` per
  `definition_list_item`; a structural change in docutils 0.22 would break this silently (no error,
  wrong output) — the reason SC2 calls out the multi-`<term>` edge case specifically.

### Integration Points
- Deprecated-API calls live across `template_engine.py` (toctree traversal), `translator.py` (node
  visiting), `builder.py` (image collection, write loop), and `__init__.py` (config/builder
  registration) — the D-01 sweep spans all four layers, not just `template_engine.py`.
- The `filterwarnings` guard (D-02) sits in `pyproject.toml` and takes effect for every `pytest`
  invocation (local + the Phase-9 CI matrix), so it must be green before Phase 9's observed CI run.

</code_context>

<specifics>
## Specific Ideas

- The user deliberately chose the **thorough** posture on API modernization (D-01) and the **permanent
  structural guard** (D-02) here — a stronger stance than the Phase-7 "minimize scope" default. The
  intent: leave the API surface clean and self-policing so future forward-ports (Sphinx 10, docutils
  0.23+) surface as loud test failures rather than silent rot. Do NOT under-scope the sweep to just
  the one `traverse()` call.
- Conversely, the user kept the **admonition rendering fix OUT** of this phase — Phase 8 is about API/
  deprecation posture and test-suite green, not translator rendering-correctness features. Keep the
  two concerns cleanly separated.

</specifics>

<deferred>
## Deferred Ideas

- **Admonition rendering bug → its own follow-up phase (within v0.5.0).** The pre-existing
  `translator.py::_visit_admonition` markup/code-mode mismatch (`.. note::` renders literal
  `par({text(...)})` Typst source instead of typeset prose, 4 occurrences in the compiled docs) is
  **explicitly NOT in Phase 8's scope** — it is not a Sphinx-9/docutils-0.22 API break. The user chose
  to fix it in v0.5.0 but as a **dedicated follow-up phase**, keeping Phase 8 crisply API-focused.
  - **Action needed:** add a new phase to the v0.5.0 roadmap via `/gsd-phase` — recommend inserting it
    **before Phase 9** (e.g. an inserted decimal phase `8.5`) so Phase 9's observed all-green CI run and
    the eventual v0.5.0 release ship the *fixed* admonition rendering.
  - **Full write-up:** `.planning/phases/07-bump-preview-packages-typst-0-15-kai-fix/deferred-items.md`
    (root cause + the two candidate fixes: prefix injected content with `#` to re-enter code mode
    inside `[...]`, or switch gentle-clues to pure function-call form `info(par({...}))`).

- (Already tracked in REQUIREMENTS.md v2) **CFG-01** (user-configurable `@preview` versions) and
  **XOS-01** (cross-OS docs-PDF CI) — not in this milestone.

</deferred>

---

*Phase: 8-api-test-compatibility-sphinx-9-docutils-0-22*
*Context gathered: 2026-07-11*
