# Phase 24: Delete `typst_toctree_defaults` (dead-config sweep round 2, part B) - Context

**Gathered:** 2026-07-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove the registered-but-inert `typst_toctree_defaults` config value from every user-facing
and code surface so it is no longer presented as a supported option. Verified during discussion
that the value has **zero consumers**: `TypstWriter.translate` (`writer.py:215`) calls
`template_engine.extract_toctree_options`, which reads options straight off the docutils
`toctree` node (`toctree.get("maxdepth", 2)`, `toctree.get("numbered", …)`, etc. in
`template_engine.py:290-317`) — never off `app.config.typst_toctree_defaults`. So this is a pure
removal with no config→output change (GATE-01 does not apply). Documented toctree control stays
the per-directive path (`:maxdepth:`, `:numbered:`, `:caption:`).

**Out of scope (belongs to later phases):** deleting the orphan `docs/configuration.rst` file
itself (Phase 27 / DOC-06), any CHANGELOG version-bump or Unreleased entry (Phase 28
release-prep), and the `typst_elements` / other dead-config work (Phase 26).

</domain>

<decisions>
## Implementation Decisions

### Deletion surface set (grep-zero target)
- **D-01:** Remove `typst_toctree_defaults` from exactly these surfaces (SC#1's enumerated set):
  - `typsphinx/__init__.py:47` — the `app.add_config_value("typst_toctree_defaults", …)` registration line.
  - `README.md:208` — the `- \`typst_toctree_defaults\`: Default toctree options` bullet.
  - `examples/advanced/conf.py:86` — the `typst_toctree_defaults = { … }` config block.
  - `examples/advanced/README.md:250` — the doc snippet showing the value.
  - `docs/configuration.rst` — the three occurrences at lines 223 (section heading + body),
    245 (example), and 355 (example block). **Surgical edit only** (see D-03).
  - `tests/test_config_toctree_defaults.py` — **delete the whole file** (registration-only tests; SC#2 explicit).
  - `tests/test_documentation_configuration.py:40` — drop the `"typst_toctree_defaults",` list entry.

### CHANGELOG.md handling
- **D-02:** **Do NOT touch `CHANGELOG.md`.** The one hit at `CHANGELOG.md:553` sits inside a
  historical release entry's `#### Configuration Options` listing — immutable history that
  accurately records the value was announced then. Precedent: the v0.6.2 CONF-01 removal of
  `typst_output_dir` / `typst_author_params` left their historical CHANGELOG listing lines
  intact (`typst_output_dir` still appears at ~line 558 in that same block). SC#1's enumerated
  surfaces deliberately exclude CHANGELOG. The `[Unreleased] → ### Removed` note for this removal
  is **deferred to Phase 28 (release-prep)**, batched with the version bump — not added in Phase 24.
  Consequence: the repo-wide grep for `typst_toctree_defaults` will still match `CHANGELOG.md:553`
  after this phase; that is intended. The grep-zero bar applies to SC#1's enumerated surfaces, not
  literal whole-repo history.

### orphan `docs/configuration.rst` handling
- **D-03:** **Surgical removal, keep the file.** Excise only the `typst_toctree_defaults` content
  from `docs/configuration.rst` (the "Table of Contents" section at ~223-250 and the toctree block
  in the combined example at ~355), leaving the rest of the file in place. Deleting the whole
  orphan file is Phase 27's job (DOC-06) — Phase 24 must not pull that forward and step on Phase
  27's scope. The redundant edit-now-then-delete-later is accepted because Phase 24 runs first and
  SC#1 requires grep-zero on this surface at Phase 24 completion.

### Verification bar (no GATE-01)
- **D-04:** Honest bar = grep-zero on SC#1 surfaces + green suite. After removal: extension still
  imports, both builders (`typst`, `typstpdf`) register, a docs project builds green via
  `sphinx-build -b typst`, and the full existing test suite stays green. No `typst.compile()`
  regression fixture is required (pure removal, zero config→output change — GATE-01 explicitly N/A
  per the ROADMAP note).

### Claude's Discretion
- Exact line-editing mechanics (how much surrounding whitespace/heading to trim in
  `docs/configuration.rst` and `examples/advanced/`) so the surrounding docs read cleanly.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirement
- `.planning/ROADMAP.md` § "Phase 24: Delete `typst_toctree_defaults`" — goal, 3 success criteria,
  and the GATE-01-N/A note (pure removal, grep-proven-inert).
- `.planning/REQUIREMENTS.md` § CONF-05 — the requirement text (surfaces list, zero-consumers claim).

### Sequencing constraints (avoid stepping on later phases)
- `.planning/ROADMAP.md` § "Phase 27: Docs 実測整合" (DOC-06) — owns deletion of the whole orphan
  `docs/configuration.rst`; Phase 24 only surgically edits it.
- `.planning/ROADMAP.md` § "Phase 28: v0.6.3 Release Prep" — owns the CHANGELOG version bump and the
  Unreleased `### Removed` note.

No external ADRs/specs — requirements fully captured in the decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None new. This phase only removes surfaces.

### Established Patterns
- `template_engine.extract_toctree_options` (`template_engine.py:273-317`) reads toctree options
  from the docutils node, not from config — this is why `typst_toctree_defaults` was always inert.
  Nothing in this method changes.
- v0.6.2 CONF-01 removal (`typst_output_dir`, `typst_author_params`) is the exact analog for this
  work: registration line + docs/examples/README/test surfaces removed, historical CHANGELOG lines
  left intact. Mirror that treatment.

### Integration Points
- `typsphinx/__init__.py` `setup(app)` registration block — remove one `add_config_value` line;
  extension must still import and both builders must still register afterward.

</code_context>

<specifics>
## Specific Ideas

Follow the v0.6.2 CONF-01 removal exactly as the template for surface coverage and for the
"leave historical CHANGELOG intact" decision.

</specifics>

<deferred>
## Deferred Ideas

- **Delete the orphan `docs/configuration.rst` file entirely** — Phase 27 / DOC-06. Phase 24 only
  removes the `typst_toctree_defaults` content from it.
- **CHANGELOG `[Unreleased] → ### Removed` note for this removal** — Phase 28 release-prep, batched
  with the 0.6.3 version bump.

None of these are scope creep — they are explicitly other phases' work surfaced during the surface sweep.

</deferred>

---

*Phase: 24-delete-typst-toctree-defaults-dead-config-sweep-round-2-part-b*
*Context gathered: 2026-07-23*
