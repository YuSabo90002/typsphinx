# Backlog

Tracked items surfaced during planning/execution that are out of the current phase's scope.

---

## BUG: `block_quote` / `attribution` / `.. epigraph::` Typst emission (pre-existing)

**Surfaced:** 2026-07-12 (Phase 13 research, `gsd-phase-researcher`, Pitfall 4)
**Scope:** Out of Phase 13 (BLK-02/BLK-03). Filed for a future phase.
**Severity:** High — one produces a hard compile fatal, the other silently corrupts output.

`typsphinx/translator.py` `visit_block_quote`/`visit_attribution` (~:1540–:1591) mis-emit for the
`.. epigraph::` directive:

- **With attribution:** `.. epigraph::` compiles to Typst that aborts the whole PDF — `unclosed
  delimiter`.
- **Without attribution:** no fatal, but literal Typst source **leaks into the rendered PDF** text
  (a silent-corruption class bug — worse than a loud fatal because the render gate's leak signatures
  are the only thing that would catch it).

**Verified:** reproduced against the unmodified current codebase via real `typst.compile()` + `pypdf`
extraction during Phase 13 research (exact error message and leaked source captured in
`.planning/phases/13-shared-dispatch-point-changes-topic-line-blocks/13-RESEARCH.md` § Pitfall 4).

**Phase 13 mitigation (already accounted for):** the Phase 13 render-gate fixture uses a plain
top-level `line_block` for its "epigraph"/poem shape instead of the `.. epigraph::` directive, so it
sidesteps this bug entirely. A proper fix (compile-safe `block_quote`/`attribution` emission +
real-compile leak-signature coverage) belongs to a dedicated future phase.
