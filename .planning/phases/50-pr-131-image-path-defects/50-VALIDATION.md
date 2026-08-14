---
phase: 50
slug: pr-131-image-path-defects
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-14
---

# Phase 50 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by `/gsd-plan-phase 50` from `50-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`, per `CLAUDE.md`) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_builder.py tests/test_absolute_image_render_gate.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | quick ~15s · full suite several minutes (PDF render gates dominate) |

**Worktree note (mandatory, per `CLAUDE.md`):** executors run in isolated git worktrees. Provision with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` **before** any command above, and run
every command through `uv run`. Sphinx subprocess builds use `sys.executable -m sphinx`, never a
console-script shim (NixOS PATH-shadowing hazard).

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_builder.py tests/test_absolute_image_render_gate.py -x`
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd-verify-work`:** Full suite green, plus `black --check .` / `ruff check .` / `mypy typsphinx/` (matching CI exactly)
- **Max feedback latency:** ~15 seconds (quick command)

---

## Per-Task Verification Map

Task IDs are assigned by the planner; this draft maps at requirement granularity and is refined at
execution time.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | IMG-01 | — | Both a rehomed converted image and a real source image of the same basename are copied; each document embeds its own picture (proved from the compiled PDF, not the copy list) | render-gate (structural `.typ` + `pypdf` embedded-image extraction) | `uv run pytest tests/<new D-10 gate module> -x` | ❌ W0 — new sibling fixture (D-10) | ⬜ pending |
| TBD | TBD | 0 | IMG-01 | — | `_track_image()` relocates to the reserved namespace on a filesystem collision, silently (D-04) | unit | `uv run pytest tests/test_builder.py -k rehome -x` | ❌ W0 — NEW test; `test_post_process_images_rehomes_absolute_uri` stays pinned unedited (D-12) | ⬜ pending |
| TBD | TBD | 0 | IMG-02 | T-50-01 (path traversal) | Every destination `copy_image_files()` writes lands under `outdir`; `src == dest` never occurs; a `../`-prefixed rehome is relocated **and** warned (D-06) | unit + render-gate | `uv run pytest tests/test_builder.py -k escape -x` | ❌ W0 — new tests for the escape branch | ⬜ pending |
| TBD | TBD | 0 | IMG-02 | T-50-02 (cross-drive DoS) | `path.relpath`'s cross-drive `ValueError` is caught and routed into the same relocation, not propagated (D-07) | unit | `uv run pytest tests/test_builder.py -k cross_drive -x` | ❌ W0 — new test | ⬜ pending |
| TBD | TBD | — | SC#3 | — | Ordinary image destinations are byte-identical across the change | one-time recorded measurement, **not** a standing test (D-11) | see § D-11 mechanics below | N/A — not a pytest module | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New **sibling** fixture directory under `tests/fixtures/` for D-10 — `conf.py` carrying a
      `FakeImageConverter` post-transform copied from `tests/fixtures/absolute_image_render_gate/conf.py`,
      a master `index.rst` toctree'ing two content documents, one real source image at the colliding
      location, and two distinctly-dimensioned PNGs (D-09). **Must not reuse or mutate**
      `tests/fixtures/absolute_image_render_gate/` — D-12 pins its assertions.
- [ ] New test module driving the D-10 fixture through `-b typstpdf`, asserting the **written-first**
      pre-fix RED (only one file copied / both `.typ` files emitting the identical `image(...)` call /
      the single PDF's extracted-image list holding one picture or the same picture twice) and the
      post-fix GREEN (`extracted_sizes == {dims_a, dims_b}`).
- [ ] New unit tests in `tests/test_builder.py` for `_track_image()`'s new branches (srcdir-collision
      relocation, escape relocation + warning, `ValueError` catch) — **additive only**; the two
      D-12-pinned tests in this file must not be edited.
- [ ] D-11's before/after manifest recording — a one-time measurement recorded as phase evidence, not a
      pytest module.

---

## D-11 Two-Build Comparison Mechanics

One-time recorded measurement (D-11). Run the BEFORE half **before** touching `typsphinx/builder.py`.

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev

# BEFORE (first task, pre-change)
uv run python -m sphinx -b typst docs/source        /tmp/img50-before/docs-source
uv run python -m sphinx -b typst tests/roots/test-basic /tmp/img50-before/test-basic
find /tmp/img50-before -type f -exec sha256sum {} \; \
  | sed 's#/tmp/img50-before/##' | sort > /tmp/img50-before-manifest.txt

# ... implement the IMG-01 / IMG-02 fix ...

# AFTER (same worktree, same env)
uv run python -m sphinx -b typst docs/source        /tmp/img50-after/docs-source
uv run python -m sphinx -b typst tests/roots/test-basic /tmp/img50-after/test-basic
find /tmp/img50-after -type f -exec sha256sum {} \; \
  | sed 's#/tmp/img50-after/##' | sort > /tmp/img50-after-manifest.txt

diff /tmp/img50-before-manifest.txt /tmp/img50-after-manifest.txt   # expect EMPTY
```

`-b typst` (not `typstpdf`) is correct — destinations are what is compared, so no PDF compile is needed.
`tests/roots/test-basic` is the only root under `tests/roots/` and carries no image references, so its
manifest is a structural control rather than an image-destination proof; `docs/source` carries the real
ordinary-image case (`docs/source/examples/basic.rst:128` → `_static/diagram.png`). Record the `diff`
output plus both manifests as phase evidence.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Windows cross-drive `ValueError` (D-07) on a genuine two-drive filesystem | IMG-02 | Cannot be reproduced on this Linux host; the automated test simulates it by patching `os.path.relpath` to raise | Optional: confirm on a Windows CI lane that the build does not abort for a cross-drive absolute image URI |

All other phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
