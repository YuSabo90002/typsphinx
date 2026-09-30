---
phase: 40
slug: citations-full-round-trip
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-02
---

# Phase 40 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `40-RESEARCH.md` § "Validation Architecture" (all commands verified against the
> project's real pytest configuration this session).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (project pin `pytest>=8.4,<10`) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`, markers `slow` / `integration`, `filterwarnings = ["error::DeprecationWarning", "error::PendingDeprecationWarning"]`) |
| **Quick run command** | `uv run pytest tests/test_citation_render_gate.py -x` (new module — Wave 0 creates it) |
| **Full suite command** | `uv run pytest -m "not slow"` (fast tier) / `uv run pytest` (full, includes real-compile fixtures) |
| **Estimated runtime** | ~5 s quick tier; full tier dominated by `typst.compile()` render gates |

**Worktree note (CLAUDE.md "Worktree-isolated execution" — standing mode):** every executor worktree
runs `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` against **its own**
`pyproject.toml`, then runs everything through `uv run`. This phase adds **no** dependency and moves
**no** `@preview` pin, so no cross-worktree ordering hazard exists here — but the provisioning step
itself is still mandatory, or pytest imports the unchanged main-tree `typsphinx` package and every
gate stays RED after a correct fix.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_citation_render_gate.py -x`
  (keep no `slow` marker on the translate + single-document-compile assertions so this stays sub-5 s)
- **After every plan wave:** `uv run pytest -m "not slow"` plus
  `uv run pytest tests/test_examples_charged_ieee_gate.py -x`
- **Before `/gsd-verify-work`:** full suite green (`uv run pytest`)
- **Phase gate (SC#5 / D-14 non-regression):** `uv run pytest tests/test_corpus_gate.py -m slow` must
  **actually run** green at least once before phase close. It skips gracefully offline —
  **a skip is not a pass.**
- **Max feedback latency:** ~5 s (quick tier)

---

## Per-Task Verification Map

*Seeded by plan-phase; task IDs are filled in by `/gsd-execute-phase` once PLAN.md tasks exist. The
requirement→command mapping below is fixed and comes from `40-RESEARCH.md` § Validation Architecture.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | CIT-01 (classic GATE-01 RED) | T-40-02 | Grid-open/grid-close separator count is exact, not merely "compiles" | real-compile gate (`-b typstpdf`, RED→GREEN flip) | `uv run pytest tests/test_citation_render_gate.py -k compile -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CIT-02 | — | N/A | compiled-PDF `pypdf` structural (`extraction_mode="layout"`) | `uv run pytest tests/test_citation_render_gate.py -k layout -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CIT-03 | T-40-03 | Dangling `refid` warns + skips, never emits `link(<missing>)` | compiled-PDF `/Annots` + `.typ`-string assert | `uv run pytest tests/test_citation_render_gate.py -k link -x` | Partial — `test_cross_doc_label_namespace_render_gate.py` is the closest existing precedent; the D-14 anchor half is new | ⬜ pending |
| TBD | TBD | TBD | CIT-04 | — | N/A | compiled-PDF `/Annots` + `visitor_text` `cm[4]`/`cm[5]` | `uv run pytest tests/test_citation_render_gate.py -k backref -x` | ❌ W0 — fixture must include 2+ citations of the same key | ⬜ pending |
| TBD | TBD | TBD | CIT-05 | — | N/A | existing end-to-end example gate (`_assert_no_warnings`) | `uv run pytest tests/test_examples_charged_ieee_gate.py -x` | ✅ exists — re-run, no code change | ⬜ pending |
| TBD | TBD | TBD | CIT-06 | — | N/A | compiled-PDF extracted-text order assert | `uv run pytest tests/test_citation_render_gate.py -k order -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-13 (label namespacing) | T-40-01 | Every label routed through existing `_namespace_label`/`_sanitize_label`; no second sanitizer | unit, `.typ`-string | `uv run pytest tests/test_citation_render_gate.py -k namespace -x` | ❌ W0 — duplicate key across 2 documents (D-10) | ⬜ pending |
| TBD | TBD | TBD | D-14 (citing-site anchor, non-regression) | — | N/A | full-corpus regression | `uv run pytest tests/test_corpus_gate.py -m slow` | ✅ exists — re-run as the phase's final gate | ⬜ pending |
| TBD | TBD | TBD | SC#5 (three separator protocols) | T-40-02 | Exactly one separator per protocol boundary | regex/count, real `-b typst`, incl. citation nested in a list item | `uv run pytest tests/test_citation_render_gate.py -k separator -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-07 (uncited entry renders) | — | N/A | `.typ`-string + compiled PDF | `uv run pytest tests/test_citation_render_gate.py -k uncited -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New fixture directory (suggested `tests/fixtures/citation_render_gate/`): **2 documents**, a
      **forward reference** (definition placed after its first use), **2+ citations of the same key**
      (the multi-backref D-03 shape and CIT-04's proof), a **cross-document citation**, a
      **duplicate key defined in both documents** (D-10), an **uncited definition** (D-07), a
      **citation run broken by a non-citation sibling** (D-06), and a **citation nested in a list
      item** (SC#5 — RESEARCH found this fails today with a *different* error,
      `label ... does not exist`, than the top-level syntax fatal)
- [ ] New test module (suggested `tests/test_citation_render_gate.py`) covering
      CIT-01..CIT-04, CIT-06 and D-06/D-07/D-13/SC#5 per the table above
- [ ] `40-GATE-EVIDENCE-01.md` recording, verbatim and against the plan-start commit hash: the fixture
      `.rst` source, the pre-fix emitted `.typ` fragment
      (`text("Krizhevsky2012")par({text("Krizhevsky, A. …")})`), and the exact exception
      (`ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed:
      TypstError: expected semicolon or line break`) — mirroring the `39-GATE-EVIDENCE-0N.md`
      convention
- [ ] `examples/charged-ieee/{approach1,approach2}/source/index.rst` restoration — verbatim revert of
      what `8bed1a3` / `c014a0b` stripped, plus deletion of both "no citations" RST comments (D-12)
- [ ] Re-run (do **not** edit) `tests/test_examples_charged_ieee_gate.py` after the restoration — its
      `_assert_no_warnings` fails pre-fix on the unknown-node warnings and passes post-fix, doubling
      as SC#5's separator-protocol proof on real shipped content
- [ ] A D-14 own-`ids` anchor-guard assertion — either extending
      `tests/test_cross_doc_label_namespace_render_gate.py` or a dedicated small module

**Explicitly NOT Wave 0 (measured):** `tests/test_corpus_gate.py:210-241, 490-503` needs **no change**
— RESEARCH confirmed both `citation` mentions there are synthetic unit-test strings feeding the
warning-parser, not live-build assertions.

---

## Manual-Only Verifications

*None.* Every Phase 40 behavior has an automated verification: the layout claim (CIT-02) is a `pypdf`
bounding-box assertion rather than an eye check (SC#2 says so explicitly), the navigation claims
(CIT-03/CIT-04) are `/Annots` link-destination assertions, and the ordering claim (CIT-06) is an
extracted-text index comparison. This phase carries no `[V]`-class requirement.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5 s
- [ ] GATE-01 RED captured verbatim against the unfixed translator **before** any handler code lands
- [ ] SC#5 corpus gate actually ran (not skipped) and was green
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
