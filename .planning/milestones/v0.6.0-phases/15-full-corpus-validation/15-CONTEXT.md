# Phase 15: Full-Corpus Validation - Context

**Gathered:** 2026-07-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Validate that Sphinx's own `doc/` tree compiles end-to-end through the `typstpdf`
builder with **no fatal `TypstCompilationError`** (the milestone's stated
acceptance bar, GATE-02), then produce two measurements against that same real
corpus:

1. **Warning catalogue** — the residual `unknown_visit` warnings from the build,
   ranked by frequency (input to the next milestone's backlog).
2. **Empty-URL before/after** — quantify the empty-URL cross-reference
   warning-count reduction delivered by the Phase-12 XREF-01 fix, measured before
   vs. after rather than assumed.

This is a **validation + measurement** phase. No new node handlers, no new
runtime dependencies, no changes to `translator.py` behavior. The only production
surface touched is test/CI scaffolding for the corpus gate.
</domain>

<decisions>
## Implementation Decisions

### Corpus acquisition & scope
- **D-01:** Obtain Sphinx's `doc/` tree by **shallow `git clone` at a pinned tag**
  that matches the installed Sphinx version (the v9.1.x line typsphinx pins to).
  Sphinx's `doc/` tree is **not** shipped in the pip package — it exists only in
  the Sphinx source repo — so the corpus must be fetched. Prefer the tag matching
  `sphinx.__version__` so the corpus and the compiler-facing Sphinx agree.
- **D-02:** Scope is the **full `doc/` tree**, not a curated subset — faithful to
  the GATE-02 wording ("Sphinx's own `doc/` tree") and the "full-corpus" phase
  name. A subset was rejected as diverging from the milestone gate.
- **D-03:** Build with **Sphinx's real `doc/conf.py`** as-is (only adding the
  `typstpdf` builder / `typsphinx` to `extensions`), for real-world fidelity —
  not a stripped minimal conf. The real conf loads Sphinx-internal extensions
  and the source tree's local `sphinxext/` modules; those must be importable from
  the clone. **Researcher risk to resolve:** the real conf may pull doc-build-only
  extensions/deps not in typsphinx's env (e.g. `sphinxcontrib.*`,
  `sphinx-notfound-page`, local `sphinxext/`). Decide install-vs-degrade before
  planning; if a hard block, a documented minimal-conf fallback is the escape
  hatch (but the intent is the real conf).

### Gate character & CI integration
- **D-04:** GATE-02 lands as a **`slow`-marked standing pytest test** (same
  `sphinx-build → typst.compile() → pypdf` lineage as the GATE-01 render gates),
  **excluded from the default/CI fast suite** via the existing `slow` marker
  (`-m "not slow"`). It stays reproducible and on-demand rather than burdening CI
  with a net-dependent, slow, corpus-scale build. Rejected: one-time throwaway
  script (loses regression re-runnability) and a dedicated always-on CI job
  (net-dependent, slow, flaky, high maintenance).
- **D-05:** When the corpus can't be obtained (**no network / clone failure**),
  the test **`pytest.skip`s** (does not fail) — standard slow-test hygiene so
  offline/CI/sandbox runs stay green. The gate is meaningful only when the corpus
  is actually present.

### Measurement recording & methodology (defaults — user opted to lock via defaults)
- **D-06:** Record both measurements in a committed **`15-CORPUS-REPORT.md`** in
  the phase directory: the frequency-ranked `unknown_visit` catalogue and the
  empty-URL before/after numbers. This report is the **next milestone's backlog
  input** — no separate GitHub issue or `.planning` backlog file for this phase.
- **D-07:** Measure empty-URL **before/after** by re-building the *same* corpus
  with the **XREF-01 change reverted via git** (revert/stash the Phase-12
  `translator.py` XREF-01 edits — `depart_reference` `refid` branch +
  `depart_term` `<label>` anchor, landed in `12-02-PLAN`; anchor commit
  `79c9d45 fix(12-02): emit bracket-wrap <label> anchor in depart_term`), then
  diffing the empty-URL / `link("", …)`-class warning counts against the
  as-shipped build. This produces a credible "before" number now that the fix is
  already landed, rather than trusting a remembered baseline.

### Claude's Discretion
- Exact clone mechanism (subprocess `git`, cached temp dir, tag-resolution from
  `sphinx.__version__`), report table shape, and how warnings are captured from
  the Sphinx warning stream vs. typsphinx's own `logger.warning` — planner/
  researcher choice, as long as D-01…D-07 hold.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirement & scope
- `.planning/ROADMAP.md` §"Phase 15: Full-Corpus Validation" — goal + 3 success
  criteria (fatal-free compile, warning catalogue, empty-URL before/after).
- `.planning/REQUIREMENTS.md` — **GATE-02** (line ~55) is the phase's sole
  requirement; note it explicitly asks for the catalogue + before/after measure.

### Gate pattern to extend
- `tests/test_pdf_render_gate.py` — the GATE-01 standing pattern this phase
  scales up: `sphinx-build → typst.compile() → pypdf` text-extraction with
  negative-control leak signatures; fails loudly on `TypstCompilationError`.
- `tests/fixtures/*_render_gate/` — the per-gate fixture-project convention
  (conf.py + rst). For GATE-02 the "fixture" is the fetched Sphinx `doc/` tree.
- `pyproject.toml` §`[tool.pytest.ini_options] markers` — the existing `slow`
  marker (`-m "not slow"`) that D-04 reuses.

### XREF-01 before/after anchor
- `12-02-PLAN.md` + `.planning/phases/12-*/12-VERIFICATION.md` — what the XREF-01
  fix changed (the revert target for D-07). Commit `79c9d45`.

### Production surface (read for integration, not to modify)
- `typsphinx/pdf.py` — `TypstCompilationError`, the `typst.compile()` wrapper.
- `typsphinx/builder.py` — `TypstPDFBuilder.finish()` compile path; source of the
  `unknown_visit` / `logger.warning` stream to catalogue.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_pdf_render_gate.py`: the real-compile gate harness (10 classes after
  Phase 14). GATE-02 adds a `slow`-marked class in the same file (or a sibling
  `test_corpus_gate.py`) reusing its compile/extract/leak-signature helpers.
- `slow` pytest marker: already defined; `-m "not slow"` already the fast-suite
  convention — no new marker needed for D-04.
- `typsphinx/pdf.py::TypstCompilationError`: the exact exception the GATE-02
  assertion keys on.

### Established Patterns
- Every node-handler phase in v0.6.0 shipped a real `typst.compile()` fixture;
  GATE-02 is the corpus-scale terminal instance of that standing bar.
- Warnings surface as Sphinx build warnings + typsphinx `logger.warning`
  (`unknown_visit` for dropped nodes) — the catalogue's raw material.

### Integration Points
- Drive via `sphinx-build -b typstpdf <clone>/doc <out>` on the fetched tree,
  capturing the warning stream; then `typst.compile()` the emitted master `.typ`.
- The XREF-01 before/after (D-07) needs a clean git revert/re-apply of one
  `translator.py` change while holding the corpus constant.
</code_context>

<specifics>
## Specific Ideas

- Report filename fixed by decision: `15-CORPUS-REPORT.md` (phase dir).
- "Gate" means **no fatal error**, not zero warnings — warnings are catalogued,
  not failed on (SC#2 wording).
- **Env caveat (from prior sessions):** the NixOS sandbox fails `uv run` of
  compiled binaries and ~45 integration tests fail environmentally. The corpus
  gate is `slow`-marked + `pytest.skip`-on-unavailable (D-04/D-05), so it should
  not add to the sandbox red set — but the planner should assume it runs
  **outside** the sandbox (real network + full env) for the actual measurement.
</specifics>

<deferred>
## Deferred Ideas

- **Measurement recording as a GitHub issue / `.planning` backlog file** —
  considered for D-06; chose an in-phase `15-CORPUS-REPORT.md` instead. If the
  next milestone wants a tracked backlog, promote the report's catalogue then.
- **Discussing the measurement details interactively** — user opted to lock
  D-06/D-07 via recommended defaults rather than a deep-dive; revisit only if the
  before/after revert proves impractical.
- Broadening `docs-pdf` CI to macOS/Windows (**XOS-01**) and configurable
  `@preview` versions (**CFG-01**) remain v2 out-of-scope (carried from PROJECT.md).

*None of the above are in Phase 15 scope.*
</deferred>

---

*Phase: 15-full-corpus-validation*
*Context gathered: 2026-07-12*
