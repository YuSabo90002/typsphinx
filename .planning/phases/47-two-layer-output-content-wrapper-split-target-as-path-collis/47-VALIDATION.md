---
phase: 47
slug: two-layer-output-content-wrapper-split-target-as-path-collis
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-11
---

# Phase 47 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `47-RESEARCH.md` §"Validation Architecture". The Per-Task Verification Map is
> filled once PLAN.md files exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`); the suite already contains real-subprocess `sphinx-build` gates |
| **Config file** | `pyproject.toml` — no new config needed |
| **Quick run command** | `pytest tests/test_builder_output_stem.py tests/test_two_layer_output_gate.py tests/test_collision_validator_gate.py -x` |
| **Full suite command** | `pytest` (or `tox -e py313`) |
| **Estimated runtime** | TBD — measure at Wave 0 and record here; do not assume |

---

## Sampling Rate

- **After every task commit:** Run the quick run command above
- **After every plan wave:** Run `pytest` in full, plus `black --check .`, `ruff check .`, `mypy typsphinx/`
- **Phase gate (before `/gsd-verify-work`):** Full suite green, plus a real `-b typst` and `-b typstpdf`
  build of the B-1/B-2 fixture and the collision fixtures
- **Max feedback latency:** TBD — set from the Wave 0 runtime measurement

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| _pending_ | — | — | — | — | — | — | — | — | ⬜ pending |

*Filled after PLAN.md files are written. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement → evidence contract (from RESEARCH.md, binding constraint #4)

| Req ID | Evidence that proves it | Pre-fix RED required? | RED shape |
|--------|-------------------------|------------------------|-----------|
| COMP-01 | Real `sphinx-build` subprocess; emitted `.typ` structural assertion | Yes | Content file has NO `#show: project.with(` and no template import |
| COMP-02 | Real `sphinx-build` subprocess; path assertion | Yes | Wrapper exists at the target-derived path (pre-fix: today's single-file shape) |
| COMP-03 | Real `sphinx-build` + real `typst.compile()` | Yes | **Classic `TypstError`** — `file not found (searched at .../guide/index.typ)`, measured this session |
| COMP-04 | Real `typst.compile()` + `pypdf` text extraction | Yes | **Structural `pypdf` assertion, NOT `TypstError`** — B-2 was measured as compiles-fine-but-wrong-output: a second title-page-shaped block and a second `"Contents"` heading appear before the nested content's body marker |
| OUT-01 | Unit (`_resolve_output_stem`) + real `sphinx-build` | No — behavior change, existing expectations move | n/a |
| OUT-02 | Unit + integration, one fixture per escape shape | No — preserved behavior; regression test proves it survives the OUT-01 rewrite | n/a |
| OUT-03 | Real `sphinx-build`; structural invariant | No | n/a |
| BLD-02 | Real `sphinx-build` subprocess; marker-string presence in emitted `.typ` | Yes | **Structural** — exit 0, the surviving file contains only one master's marker, no collision warning anywhere in stdout/stderr |
| BLD-03 | Real `sphinx-build` subprocess | Yes | **Structural** — `[("index","index.typ",…)]` exits 0 with no warning today |
| BLD-04 | Unit assertion on the comparison function + Windows/macOS CI lanes | Yes | **Structural, at the unit level** — the comparison does not `casefold()`. The physical collision is unobservable on Linux, so the fixture must assert the comparison itself folds case |

---

## Wave 0 Requirements

- [ ] `tests/test_two_layer_output_gate.py` — new module; COMP-01, COMP-02, COMP-03, COMP-04, OUT-03
- [ ] `tests/test_collision_validator_gate.py` — new module; BLD-02, BLD-03, BLD-04, each with its own
      pre-fix RED per binding constraint #4
- [ ] `tests/test_builder_output_stem.py` — existing; OUT-01 expectations move (path targets no longer
      truncated), the three OUT-02 escape cases stay as regression tests, and lines 334/352 move from
      asserting a fallback to expecting `ExtensionError` per D-03 replacing CR-01
- [ ] `tests/test_typst_documents_collision_gate.py` — existing; every test asserts `returncode == 0`
      plus a warning substring for what D-01/D-03 now make an `ExtensionError`. The module's
      assertions invert
- [ ] `tests/test_preview_version_sync.py` — not expected to change, but must be re-run once content
      files carry the D-06 preamble unconditionally

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Branch is on `origin` with a completed CI run over the Windows and macOS lanes | Milestone invariant #5 / binding constraint #2 | Requires a real push and a real GitHub Actions run — not reproducible in-process | `git push -u origin gsd/v0.8.0-multi-master-composition`, then `git ls-remote --heads origin` must hit, and `gh run list --branch gsd/v0.8.0-multi-master-composition` must show a completed run including the Windows and macOS lanes |
| BLD-04's physical collision consequence on a case-insensitive filesystem | BLD-04 | Linux CI cannot observe a case-insensitive overwrite; only the Windows/macOS lanes can | Confirm the Windows and macOS CI lanes run the `test_collision_validator_gate.py` BLD-04 case |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency measured at Wave 0 and recorded above
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
