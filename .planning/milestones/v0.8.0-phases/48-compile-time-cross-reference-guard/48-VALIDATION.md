---
phase: 48
slug: compile-time-cross-reference-guard
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-12
---

# Phase 48 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

Derived from `48-RESEARCH.md` §Validation Architecture. All runtimes below were measured on
2026-08-12 in the main tree; worktree executors must re-provision per CLAUDE.md
(`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`) and prefix every command
with `uv run`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (`sphinx.testing.fixtures` loaded as a plugin) |
| **Config file** | `pyproject.toml` |
| **Phase-scoped run command** | `uv run pytest tests/test_translator.py tests/test_citation_degradation_gate.py tests/test_master_include_set_predicate_gate.py tests/test_xref_orphan_degrade_render_gate.py -q` |
| **Quick run command** | `uv run pytest -m "not slow"` |
| **Full suite command** | `uv run pytest` (adds the 44 `-m slow` corpus/render-gate tests) |
| **Estimated runtime** | phase-scoped **4.1s** (142 tests) · quick **172.7s** (1000 passed, 44 deselected) · corpus gate alone **~29s** |

**Measured 2026-08-12:**
- `uv run pytest tests/test_translator.py tests/test_citation_degradation_gate.py tests/test_master_include_set_predicate_gate.py tests/test_xref_orphan_degrade_render_gate.py -q` → `142 passed in 4.11s`
- `uv run pytest -m "not slow" -q` → `1000 passed, 44 deselected in 172.71s`
- `tests/test_corpus_gate.py` full-corpus `-b typstpdf` → **28.93s / 28.56s** (D-11 "before" baseline)

---

## Sampling Rate

- **After every task commit:** Run the **phase-scoped** command (4.1s). At ~4 seconds it is cheap
  enough to run on every commit, and it covers all four test files `48-CONTEXT.md` lists under
  "Tests this phase changes" plus the two existing `pending_xref` unit tests.
- **After every plan wave:** Run `uv run pytest -m "not slow"` (172.7s).
- **Before `/gsd-verify-work`:** Full suite (`uv run pytest`) must be green — binding constraint #8
  requires the phase to close green, and the corpus gate is `-m slow`, so the quick run alone does
  not satisfy it.
- **D-11 "after" measurement:** once the guard has landed on every emission site, run
  `time uv run pytest tests/test_corpus_gate.py -m slow` and record the number against the
  28.93s / 28.56s baseline, applying the tier thresholds **already fixed in D-11** (under +20%:
  record only · +20%–+100%: record as an explicit finding and file an improvement todo · above
  +100%: escalate as a blocker attached to Phase 49's scope). The tiers are fixed before the
  measurement by D-11's own instruction — do not renegotiate them after seeing the number.
- **Max feedback latency:** **5 seconds** per task commit; 180 seconds per wave.

---

## Per-Task Verification Map

> Seeded by plan-phase before tasks exist. `/gsd-execute-phase` fills one row per task as plans
> are executed; `/gsd-validate-phase` audits completeness.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 48-01-01 | 01 | 1 | XREF-03 | — | N/A (no security surface — see below) | integration | `uv run pytest tests/test_xref_orphan_degrade_render_gate.py -x` | ✅ | ⬜ pending |

**Requirement → test mapping the plans must satisfy** (from `48-RESEARCH.md`):

| Req | Behavior | Test type | Command | File exists |
|-----|----------|-----------|---------|-------------|
| XREF-03 | A reference to a target absent from the compiling master degrades to plain text and the compile succeeds | integration — real `typst.compile()` + `pypdf` readback | `uv run pytest tests/test_xref_orphan_degrade_render_gate.py -x` | ✅ (premise moves build-time → compile-time; content changes) |
| XREF-03 | SC#1's two-master fixture: one master's PDF carries a real `/Link` annotation, the other's carries none, neither raises `TypstError` | integration | new fixture + gate | ❌ Wave 0 |
| XREF-03 | Pre-fix RED recorded verbatim **before** the new emitter runs (binding constraints #4, #6) | evidence artifact | `xfail(strict=True)` or a committed `48-*-RED-EVIDENCE.md` (Claude's Discretion) | ❌ Wave 0 |
| XREF-04 | `grep -rn master_included_docnames typsphinx/` returns nothing | structural | grep assertion embedded in a test | ❌ Wave 0 |
| XREF-04 | The four unit tests bound to `_compute_master_included_docnames()` are gone; the three end-to-end tests survive unchanged | unit + integration | `uv run pytest tests/test_master_include_set_predicate_gate.py -x` | ✅ |
| XREF-04 (D-05) | A `[Cite]_` inside a `code-block` `:caption:` compiles without a dangling-label fatal | integration — real `typst.compile()` | new fixture (RED reproduced this research session: `label <index:id1> does not exist in the document`) | ❌ Wave 0 |
| XREF-04 (D-04) | `visit_pending_xref` / `depart_pending_xref` route through the shared guard | unit | `uv run pytest tests/test_translator.py -k pending_xref -x` | ✅ (lines 1973, 2001 — unit-level only) |
| XREF-04 (D-06) | Same-document anchors outside the citation back-reference case keep their **unguarded** form | unit — explicit negative assertion | asserted in a translator unit test | ❌ Wave 0 |
| D-11 | Full-corpus `-b typstpdf` compile time recorded before and after | **manual one-off measurement, not a permanent assertion** — `test_corpus_gate.py` carries no timing instrumentation and a wall-clock assert would be flaky across CI machines | `time uv run pytest tests/test_corpus_gate.py -m slow` | ✅ (gate exists; timing is manual) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Binding constraint #6 (no laundered gates) means every expected value below must be derived from the
fixture's `conf.py` and `.rst` alone and **written down before the new emitter runs** — the
`47-EXPECTED-STRUCTURE.md` procedure D-03 tells this phase to imitate.

- [ ] **XREF-03 two-master acceptance fixture** — one target document included by master A only;
      a shared content file referencing it. Follows the
      `sphinx-build → typst.compile() → pypdf` pattern established by `tests/test_pdf_render_gate.py`.
      Fixture `conf.py` must carry the "Load-bearing properties — do NOT touch any of these" comment
      block per the project's fixture convention.
- [ ] **XREF-03 pre-fix RED evidence** — the unguarded form's verbatim
      `label <...> does not exist in the document` transcript, recorded before the guard lands.
- [ ] **D-05 citation-in-caption fixture** — the research session reproduced this end-to-end
      (`build succeeded`, no Sphinx warnings, then `TypstError: label <index:id1> does not exist in
      the document`). That reproduction must become a committed test asset as the pre-fix RED
      (binding constraint #4).
- [ ] **D-03 flipped-assertion expected values, written first** — two assertions flip direction:
      - `tests/test_master_include_set_predicate_gate.py::TestBld03GhostEntryXref::test_ghost_entry_subtree_xref_degrades_typst`
        (line 103): asserts degrade-to-plain-text today; must assert a guarded `link()` after.
      - `tests/test_citation_degradation_gate.py` case (iii)
        (`_wr03_case_refuri_excluded_document`, line 1007): `opens_wrapper` becomes unconditional
        under D-09, so a citation back-reference marker that previously did not appear now does.
- [ ] **D-11 "before" number** — already captured: **28.93s / 28.56s**. No Wave 0 work; carry it
      forward into the phase evidence.

*No framework install needed — pytest, typst-py 0.15.0, pypdf, and Sphinx 9.1.0 are all installed
and working in `.venv`.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full-corpus `-b typstpdf` compile-time before/after comparison | D-11 | `tests/test_corpus_gate.py` carries no timing instrumentation, and a wall-clock assertion would be flaky across CI machines. D-11 explicitly specifies a one-off manual record in the phase artifacts, not a permanent assertion. | Run `time uv run pytest tests/test_corpus_gate.py -m slow` twice after the guard lands; record both numbers in the phase evidence next to the 28.93s / 28.56s baseline; apply D-11's pre-fixed tier thresholds. |
| D-04 unconstructible-RED record | XREF-04 | Research established that Sphinx 9.1.0's `ReferencesResolver` unconditionally `replace_self()`s every `pending_xref`, so no source shape reaches `visit_pending_xref`'s fallback. Per the Phase 40.1 D-01 precedent this is recorded as an enumerated impossibility argument, not reported as "not reproducible" — and an argument is read, not asserted. | The phase artifacts must enumerate the four measured source shapes (`:ref:`, `:doc:`, `:any:`, unknown role) and the `ReferencesResolver` code path that makes each unreachable. The guard is still applied to the site (D-04) as defence in depth. |
| No published contract changes from deleting the D-01 warning | D-01 | Confirms an absence across the docs tree; cheap to re-check but not worth a permanent gate. | Run `grep -rn "non-included\|degrade" docs/source/` at implementation time and confirm it still returns zero, rather than assuming the discussion-time result still holds. |

---

## Security Domain

**Not applicable.** This phase is a compile-time correctness/degradation-behaviour change to a
document-generation pipeline with no authentication, session, access-control, network-input, or
cryptographic surface. ASVS V2/V3/V4/V6 are structurally inapplicable to a local Sphinx/Typst
build tool exposing no network service. V5 (Input Validation) is already covered by the existing
`escape_typst_string` / `_sanitize_label` machinery, which this phase does not change — the guard
reuses `_namespace_label`, which already routes through `_sanitize_label`.

Each PLAN.md still carries a `<threat_model>` block (ASVS L1, block on `high`) recording this
determination explicitly rather than omitting the block.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s (phase-scoped) / < 180s (quick suite)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
