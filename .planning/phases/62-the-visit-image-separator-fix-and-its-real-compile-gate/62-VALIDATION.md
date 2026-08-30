---
phase: 62
slug: the-visit-image-separator-fix-and-its-real-compile-gate
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-30
---

# Phase 62 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `62-RESEARCH.md` § "Validation Architecture". This is a **product-side
> phase gated RED-first**: the gate must be recorded failing against the unfixed tree before the fix
> lands (ROADMAP SC#2, constraint 1). A green run that was never first recorded RED is evidence of
> nothing here. The RED shape is a single aggregate `ExtensionError` naming 17 masters, each with
> the identical verbatim refusal `expected semicolon or line break` — attribution comes from the
> docname, not from message variety (CONTEXT.md D-02, § Specific Ideas).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (pinned in `pyproject.toml`; exact version via `uv.lock`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — `addopts = "-v --strict-markers"`, `markers = ["slow: ..."]` |
| **Quick run command** | `uv run pytest tests/test_inline_image_separator_render_gate.py -q` |
| **Full suite command** | `uv run pytest -q` (matches CI) |
| **Estimated runtime** | gate module ~1–2 s of compile time for 18 masters / 26 docs (measured: 3-master/6-doc build ≈ 0.44 s vs 1-master/1-doc baseline ≈ 0.31 s) · full suite several minutes |

**No `@pytest.mark.slow` needed** — the 18-master extrapolation (~1–2 s) is far below the threshold
the existing `slow`-marked modules occupy. Logged as research assumption A1 (extrapolated, not timed
at full scale); if the assembled fixture measures materially slower, revisit the marker rather than
trimming the matrix.

**Worktree note (CLAUDE.md § "Worktree-isolated execution", STANDING):** every executor first runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree, then runs
**every** command via `uv run`. Without this, pytest imports the unchanged main-tree package and
gates stay RED after a correct fix.

**Lint authority is CI, not this machine (D-11).** `ruff` is an unrunnable generic-linux ELF in any
freshly `uv sync`-provisioned worktree venv on this host. Do not attempt a local `ruff` verdict; take
it from the dispatched CI run's `Run linters` step.

**Golden-comparison newline hazard (measured, `builder.py:2072`/`:2139`).** Content `.typ` output is
byte-stable across builds (build-twice `diff` clean — no timestamps, no absolute paths, no CR bytes
on this platform), **but** the writes use a bare `open(path, "w", encoding="utf-8")` with no
`newline=""`, so on the `windows-latest` CI lane the same content lands as `\r\n`. Every golden
comparison MUST read both sides with `Path.read_text(encoding="utf-8")` — never `.read_bytes()` —
or the Windows lane fails spuriously while the fix is correct.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_inline_image_separator_render_gate.py -q`
- **After every plan wave:** `uv run pytest -q` (full suite) plus `uv run black --check .` and
  `uv run mypy typsphinx/` (`ruff` deferred to CI, above)
- **Phase-level, not per-wave:** the D-04 RED-evidence choreography (restore
  `typsphinx/translator.py` to the measured phase base SHA → run the gate → transcribe verbatim →
  restore → `git status --porcelain` empty) executes at least once regardless of wave structure,
  because it requires a temporary restore of a product file.
- **Before `/gsd-verify-work`:** full suite green AND `62-RED-EVIDENCE.md` written.
- **Phase gate:** local green complete **before** D-11's single authority CI dispatch on the
  post-fix tip — CI is never first discovery.
- **Max feedback latency:** ~2 s for the per-task quick run.

---

## Per-Task Verification Map

Task IDs are assigned at plan time (`{plan}-T{task}`); this table is the requirement-level contract
each plan's tasks must inherit. `validate-phase` finalizes the per-task rows.

| Req ID | Behavior | Test Type | Automated Command | File Exists | Status |
|--------|----------|-----------|-------------------|-------------|--------|
| IMG-08 | A separator is emitted before `image(` for all 16 measured FAIL shapes | real-compile integration | `uv run pytest tests/test_inline_image_separator_render_gate.py -k fail -q` | ❌ W0 (new module + fixture) | ⬜ pending |
| IMG-09 | Every one of the 18 masters — including the image-free `index` master poisoned only via `#include()` — writes a non-empty `%PDF`-prefixed file | real-compile integration | `uv run pytest tests/test_inline_image_separator_render_gate.py -k full_matrix -q` | ❌ W0 | ⬜ pending |
| IMG-10 | `visit_image()`'s `in_figure` branch is unmodified; the 9 PASS shapes stay **byte-identical** (D-06, stronger than SC#3's "compiling"); zero pre-existing test edits | golden byte-comparison (in-gate) + structural grep (plan verification) | gate's golden class; `git diff --name-status <measured base>..HEAD -- tests/` shows only `A`; repo-wide grep for `endswith("\n")` / `rstrip().endswith` / `[-1:]` over `typsphinx/translator.py` returns nothing; `tests/test_nested_figure_render_gate.py:256` and `tests/test_pdf_render_gate.py:2303` pass unedited | ❌ W0 goldens; ✅ existing byte assertions | ⬜ pending |
| TEST-05 | One real-compile gate module binding 16 FAIL + 9 PASS, recorded RED against the unfixed tree first | real-compile integration + evidence file | the gate module itself (greps positive for `typst.compile` / `TYPST_AVAILABLE`); `62-RED-EVIDENCE.md` transcription | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**D-03 positive control — how "17 red + 1 green" is actually observed.** Measured this session:
`TypstPDFBuilder.finish()`'s aggregate `ExtensionError` (`builder.py:2638-2642`, join format
`"; ".join(f"{docname}: {err}" ...)`) **never names a successful master**. `pass_parent`'s green
verdict inside the RED run must therefore be evidenced by its `.pdf` existing on disk plus its
`Generated PDF: ...` stdout line — not by parsing the exception text. An evidence procedure that
tries to read `pass_parent` out of the exception will find nothing and wrongly conclude the fixture
is uniformly red.

---

## Wave 0 Requirements

- [ ] `tests/fixtures/inline_image_separator_render_gate/` — the 26-document, 18-master fixture
      (D-01). No existing fixture matches this shape; the closest precedent,
      `tests/fixtures/state_guard_three_master_gate/`, has 3 masters / 6 docs.
- [ ] `tests/test_inline_image_separator_render_gate.py` — the single gate module (TEST-05), built
      on `tests/test_paragraph_concat_render_gate.py`'s skeleton with
      `tests/test_abbr_pep_separator_render_gate.py`'s multi-shape FAIL+PASS pairing.
      **Structural delta flagged by research:** both precedents compile *one* master per fixture;
      this gate must assert across 18 masters compiled in a single `sphinx-build` invocation.
- [ ] `tests/fixtures/inline_image_separator_render_gate/goldens/` — the 9 committed **content**
      `.typ` goldens (D-07), captured during the D-04 restore window. Content files only — never
      wrapper files, which carry title/author/date.
- [ ] `62-RED-EVIDENCE.md` — the phase's evidence file (D-05). **Never** `62-VERIFICATION.md`, which
      is `gsd-verifier`'s reserved output name and is clobbered at verify time.

*Framework itself needs no install — pytest, `typst-py`, and `pypdf` are all already present and
import cleanly (verified this session). `pypdf` is dev-extra only; the gate may omit any
pypdf-based extracted-text class without weakening TEST-05.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Milestone branch on `origin` with a **completed** 3-OS CI run; `windows-latest` and `macos-latest` named individually and green | SC#5 (D-10, D-11) | `.github/workflows/ci.yml`'s `push`/`pull_request` triggers are scoped to `main`/`develop`, so the run must be dispatched by hand and waited to completion; no pytest assertion can stand in for it | Push `gsd/v0.9.2-inline-image-blocker-fix-and-release` with `-u` in the phase's first plan (costs zero CI minutes). At phase end: `gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release`, then poll to **completion**; record each OS lane's conclusion individually and take `ruff`'s verdict from that run's `Run linters` step. |
| Phase base SHA is **measured**, not assumed | SC#2 (D-04) | The executor's `worktree_metadata.expected_base` is known-unreliable (it records the executor's own tip in a majority of observed cases); Phase 59's precedent recorded `PHASE_BASE_SHA` via `git rev-parse HEAD` inside the worktree, per-plan rather than as one phase-level constant | The plan must instruct the executor to measure the base itself at RED-evidence time (`git merge-base` against the phase's start point, or `git rev-parse HEAD` before any product edit) and record the literal SHA in `62-RED-EVIDENCE.md`. Never copy it from worktree metadata. |
| Decoy-branch disambiguation | SC#5 (D-12) | Requires a human-observable `git branch -vv` reading at the moment the commit helper may have re-created `gsd/v0.9.2-milestone` | If the decoy reappears, advance the canonical pointer **before** deleting it. Measured at discussion time: exactly one `0.9.2` branch existed, the canonical one, at `6224298e`, local-only with no upstream. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s for the per-task quick run
- [ ] Golden comparisons use `read_text(encoding="utf-8")`, never `read_bytes()` (Windows lane)
- [ ] RED evidence recorded before the fix commit, with a measured base SHA
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
