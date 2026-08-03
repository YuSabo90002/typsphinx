---
phase: 42
slug: captioned-table-drops-preceding-target-label
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-03
---

# Phase 42 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `42-RESEARCH.md` § 7 "Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "-v --strict-markers"`, markers `slow`/`integration`, `filterwarnings = ["error::DeprecationWarning", "error::PendingDeprecationWarning"]`) |
| **Quick run command** | `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v` (per-task; add `tests/test_figure_propagated_target_render_gate.py` once it exists) |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~60–120 seconds full suite (real Typst compiles dominate); ~5–15 seconds per render-gate module |
| **Baseline** | 805 passed / 1 skipped (measured during Phase 42 research, unchanged from Phase 41's recorded number) |
| **Worktree note** | Under worktree-isolated execution, provision first with `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then run every command via `uv run` (CLAUDE.md standing rule) |

---

## Sampling Rate

- **After every task commit:** Run the new render-gate module(s) for the artifact just touched — `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v` (and the figure module once it exists).
- **After every plan wave:** Run `uv run pytest` (full suite).
- **Before `/gsd-verify-work`:** Full suite green **and** `black --check .`, `ruff check .`, `mypy typsphinx/` all clean.
- **Max feedback latency:** ~15 seconds (single render-gate module).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD (planner assigns) | TBD | 0 | TBL-03 (SC#1/SC#5) | — | N/A | classic real-compile RED (`TypstError` / `does not exist in the document`) recorded against the unfixed `depart_table`, for all four D-01 shapes | `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v` | ❌ W0 — new fixture + module | ⬜ pending |
| TBD (planner assigns) | TBD | 1 | TBL-03 (SC#3) | — | N/A | same module re-run to GREEN after the `_emit_id_anchors` call-ordering move; both labels resolve, no duplicate-label fatal | `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v` | ❌ W0 | ⬜ pending |
| TBD (planner assigns) | TBD | 1 | TBL-03 (SC#2 / D-09, D-10) | — | N/A | permanent figure regression gate — real compile over D-10's three figure shapes | `uv run pytest tests/test_figure_propagated_target_render_gate.py -v` | ❌ W0 — new fixture + module (NOT an extension of `figure_target_caption_render_gate/`) | ⬜ pending |
| TBD (planner assigns) | TBD | 1 | TBL-03 (SC#4 / D-04) | — | N/A | two-worktree byte-diff over the caption-less path, recorded as evidence (not a pytest assertion) | `diff <pre-fix-build>/index.typ <post-fix-build>/index.typ` must be empty, exit 0 — see `42-RESEARCH.md` § 4 | N/A — evidence-file method | ⬜ pending |
| TBD (planner assigns) | TBD | 1 | TBL-03 (D-06 / D-07) | — | N/A | repo-wide sweep for the same misrouting class, recorded as evidence including a null result | `grep -n "_emit_id_anchors(" typsphinx/translator.py` + classification per `42-RESEARCH.md` § 5 | N/A — evidence-file method | ⬜ pending |
| TBD (planner assigns) | TBD | 2 | TBL-03 (SC#6) | — | N/A | Phase 41 reconciliation — CHANGELOG TBL-03 line + SC#4 invariant sweep re-measured over a SHA range including Phase 42 | see `42-RESEARCH.md` § 6 | N/A — docs/evidence | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task IDs are assigned by the planner; this table is the coverage contract, not the task list.*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/captioned_table_propagated_target_render_gate/` — `conf.py` (master `typst_documents`, `numfig = True` if `:numref:` is used) + `index.rst` covering D-01's four shapes (target + `:name:`-carrying captioned table; target + captioned table with no `:name:`; captioned table inside a bullet-list item; two consecutive standalone targets before one captioned table) plus a caption-less control table.
- [ ] `tests/test_captioned_table_propagated_target_render_gate.py` — classic RED→GREEN module, driving `-b typstpdf`, shaped after `tests/test_paragraph_propagated_target_render_gate.py`.
- [ ] `tests/fixtures/figure_propagated_target_render_gate/` — new fixture for D-10's three figure shapes, reusing an existing image asset (e.g. a copy of `figure_target_caption_render_gate/image.png`). Must NOT extend `figure_target_caption_render_gate/`, which exercises a different docutils mechanism (`:target:` → `reference`-wrapped figure).
- [ ] `tests/test_figure_propagated_target_render_gate.py` — the permanent D-09 regression gate.
- [ ] No framework install needed — pytest, `typst-py`, and `pypdf` are already present and exercised by the existing render-gate suite.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Caption-less table byte invariance (SC#4 / D-04) | TBL-03 | The proof is a diff between two *named commits* built in separate worktrees — it cannot be expressed as an assertion inside a single working tree | Follow `42-RESEARCH.md` § 4 verbatim: two `git worktree add` checkouts at the named pre-fix and post-fix SHAs, per-worktree `uv sync --extra dev`, `uv run python -m sphinx -b typst -q -E` from each, then `diff` the two `index.typ`. Record both SHAs, both build commands with exit statuses, and the empty diff in a `42-GATE-EVIDENCE-NN.md`. |
| Repo-wide misrouting sweep (D-06 / D-07) | TBL-03 | Classification of each call site as image-path vs non-image-path is a judgement, not an assertion; a null result must still be recorded | Enumerate `_emit_id_anchors` call sites and buffer-diverting `self.in_*` flags per `42-RESEARCH.md` § 5, classify each, file non-image findings as todos, fix any image-path finding inside this phase, and record the result (including a null result) as evidence. |
| SC#6 release reconciliation | TBL-03 | Editing curated release artifacts and re-measuring a SHA-range sweep are one-off documentation acts | Per `42-RESEARCH.md` § 6: add the TBL-03 line to `CHANGELOG.md` § `## [0.7.0]` → `### Fixed`; re-measure Phase 41's SC#4 invariant sweep over a SHA range that includes Phase 42, written as a **new** evidence file under this phase's directory (never editing a `41-*` artifact); and revert any `phase.complete` flip of the REL-04 / REL-05 checkboxes or traceability rows before committing. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s (single render-gate module)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
