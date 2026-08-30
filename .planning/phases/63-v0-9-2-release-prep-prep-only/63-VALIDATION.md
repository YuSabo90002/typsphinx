---
phase: 63
slug: v0-9-2-release-prep-prep-only
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-30
---

# Phase 63 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `63-RESEARCH.md` § "Validation Architecture". This is a **prep-only
> release phase**: it changes no `typsphinx/` behaviour, so there is no product-side RED-first gate.
> What it validates instead is (a) that the version-literal lockstep holds across four files, (b)
> that the release body the extractor actually emits is *read*, not reasoned about, (c) that the
> bumped tree is green on runs executed **in this phase**, and (d) that the phase took **zero
> irreversible action** and REL-09's checkbox never moved.
>
> **The unit of proof here is a recorded observation, not a passing assertion.** Several rows below
> are audits whose evidence is a transcript in an evidence file, not a test exit code. A row that
> cannot be run is never recorded as a pass — see § "Skipped is not passed".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), orchestrated via `tox` (`env_list = py312, py313, lint, type, cov, docs`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; `tox.ini` |
| **Quick run command** | `uv run pytest -m "not slow"` |
| **Full suite command** | `uv run pytest` (matches CI; includes the `@pytest.mark.slow` corpus/docs-build gates) |
| **Estimated runtime** | full suite several minutes · one CI dispatch ≈ 7 min wall clock (Phase 61's run `33260111745`) |

**Worktree note (CLAUDE.md § "Worktree-isolated execution", STANDING):** every executor first runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree, then runs
every command via `uv run`. This is mandatory, not conditional on parallelism.

**The `docs` extra is required for two specific proofs.** `myst_parser` lives in the `docs` extra
only (`pyproject.toml:49-54`), and `tests/test_changelog_page_gate.py` guards on
`import myst_parser`. A worktree provisioned with `--extra dev` alone therefore **silently skips**
both content-coverage classes — the exact two classes that enforce D-11's `RELEASE_VERSIONS`
addition. Wherever D-11's proof or the docs-warning baseline runs, sync `--extra dev --extra docs`.

### Baselines carried in (to be re-measured, never inherited)

| Baseline | Value | Source | Obligation |
|----------|-------|--------|------------|
| Full pytest suite | **1543 passed, 5 skipped** | `62-VERIFICATION.md` line 66, Phase 62's close, 2026-08-30 | Re-run fresh on the **bumped** tree; record this phase's own count. Expect 1543/5 exactly — none of D-01..D-21 adds a test case. |
| Skips, itemised | 4× myst-parser docs-extra gap · 1× env-gated corpus report | same | All 5 pre-existing and unrelated. A **sixth** skip is a finding, not noise. |
| `tox -e docs-html` warnings | **3** | Phase 61's close, 2026-08-29 | Re-measure from a **clean** build (`rm -rf docs/_build` first) per D-21. |
| `tox -e docs-pdf` warnings | **5** | Phase 61's close, 2026-08-29 | Same. An incremental rebuild under-reports and manufactures a false "baseline match" — a repeat finding in this project, not a theoretical hazard. |

---

## Sampling Rate

- **After every task commit:** no product-behaviour code changes, so there is no per-commit product
  gate beyond the task's own evidence artifact being written and readable.
- **After every plan wave:** `uv run pytest` (full suite) plus `uv run black --check .` and
  `uv run mypy typsphinx/`. `ruff` is **deferred to CI** (D-18 AMENDED / QUA-10) — it is an
  unrunnable generic-linux ELF in a freshly `uv sync`-provisioned worktree venv on this host.
- **After the CHANGELOG edit and after the `RELEASE_VERSIONS` edit specifically:**
  `rm -rf docs/_build && uv run tox -e docs-html`, same for `docs-pdf`, warning counts compared
  against the 3 / 5 baseline; and `uv run --extra dev --extra docs pytest
  tests/test_changelog_page_gate.py -v` for D-11's own proof (all tests PASSED, **none SKIPPED**).
- **Phase gate:** one fresh 3-OS CI dispatch on the phase's final tip, **after** the bump commit
  (D-18), all 12 jobs green, both `windows-latest` lanes named individually.
- **Max feedback latency:** local suite minutes; CI dispatch ≈ 7 min wall clock.

---

## Per-Task Verification Map

Task IDs are assigned at plan time (`63-{plan}-T{task}`). This table is seeded with the phase's known
verification surfaces; **the planner fills in the concrete task IDs, plan and wave columns.** Every
row's command is runnable today — there is no Wave 0 gap.

| Task ID | Plan | Wave | Requirement | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------------|-----------|-------------------|-------------|--------|
| _(planner)_ | _(planner)_ | _(planner)_ | REL-11 / D-16 / SC#3 — closeout guard, **phase head** | the `phase.complete` REL-09 auto-flip is detected rather than shipped | audit (checksum) | `sha256sum .planning/REQUIREMENTS.md` · `wc -l .planning/REQUIREMENTS.md` · `git rev-parse HEAD` (PHASE_BASE_SHA) · `grep -n 'REL-09' .planning/REQUIREMENTS.md` — all four recorded verbatim into `63-CLOSEOUT-GUARD.md` | ✅ N/A — created by the task | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | SC#5 / D-16 — fence probe, **observation 1 of 2** | no irreversible action has occurred, and the probe provably reached its source | audit | `git tag -l 'v0.9.2'` empty · **unfiltered** `git ls-remote --tags origin` with ≥1 `v0.9.0` reference as the positive control and **0** `v0.9.2` references · `gh release list` with a `Latest` marker (positive control) and no `v0.9.2` row · `gh run list --workflow=release.yml` showing no v0.9.2 run | ✅ N/A — created by the task (`63-SC5-INVARIANTS.md`) | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | REL-09 (coverage only) / SC#1 — version-literal lockstep | a partial bump (the shape killing every dependabot PR) cannot reach a commit | unit + lock | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` · `uv sync --extra dev --locked` (exit 0) · `git show --name-only <bump>` listing `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md` together | ✅ exists | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | REL-10 / D-20 — extractor stdout **read**, not assumed | the published GitHub Release body cannot silently carry the scratch block | subprocess/integration | `uv run python scripts/extract_changelog_section.py 0.9.2` (exit 0, non-empty stdout, transcribed verbatim into `63-CHANGELOG-EVIDENCE.md`) · stdout piped through `grep -c 'Planned for Future Releases'` → **0** · `grep -c '^## \[0\.9\.1\]' CHANGELOG.md` → **0** · `grep -c '^\[0\.9\.1\]:' CHANGELOG.md` → **0** | ✅ exists (`tests/test_changelog_extraction.py` exercises the script) | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | REL-10 / D-11 — `RELEASE_VERSIONS` gains `"0.9.2"` | a version string missing from the rendered page cannot pass as covered | docs build (slow, **docs-extra-gated**) | `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` — all tests **PASSED**, **none SKIPPED** (a `--extra dev`-only run silently skips both content classes; see § "Skipped is not passed") | ✅ exists | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | SC#4 — green-tree proof, executed **in this phase** | a green inherited from Phase 62's word is never recorded as this phase's | full-suite + lint/type | `uv run pytest` (full suite, count recorded and compared to 1543/5) · `uv run black --check .` · `uv run mypy typsphinx/` — plus a worktree-identity check that `typsphinx.__file__` resolves inside this worktree | ✅ exists | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | SC#4 / D-21 — docs builds on a **clean** baseline | an incremental rebuild cannot manufacture a false "baseline match" | docs build | `rm -rf docs/_build && uv run tox -e docs-html` (warnings vs **3**) · `rm -rf docs/_build && uv run tox -e docs-pdf` (warnings vs **5**) — the `rm -rf` is part of the command, not a preamble | ✅ exists | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | SC#4 / D-17 / D-18 AMENDED — one 3-OS CI dispatch on the **bumped** tip | the green is observed here, never inherited; and `ruff`'s verdict comes from CI, never this host | CI | `uv sync --extra dev --locked` (pre-dispatch, D-17) → `gh workflow run ci.yml --ref <branch>` → `gh run list --workflow=ci.yml --branch <branch> --limit 1` → `gh run watch <id> --exit-status` → `gh run view <id> --json jobs`. Both `windows-latest` lanes and `macos-latest` named individually. **`ruff`'s verdict = the `Lint and Format Check` job's conclusion, step `Run lint with tox` (`ci.yml:69`) — `ci.yml` has NO step named `Run linters`; see § "The lint-step name".** | ✅ `.github/workflows/ci.yml` | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | SC#5 / D-16 — fence probe, **observation 2 of 2** | the fence held for the *whole* phase, not just at its head | audit | the same probes with the same positive controls at a later timestamp, in a **later wave** (SC#5 requires separation by intervening waves, not by wall-clock luck) · `git diff <PHASE_BASE_SHA>..HEAD -- typsphinx/` **empty**, paired with the same-anchor widened diff as the positive control · ≥2 distinct UTC timestamps in the file | ✅ N/A — created by the task | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | REL-11 / D-16 / SC#3 — closeout guard, **phase close** | a detected flip is reverted by hand and reported, never committed | audit (checksum) | live `sha256sum` / `wc -l` / `grep -n 'REL-09'` compared line-for-line to the recorded Baseline · `git diff --name-only -- .planning/REQUIREMENTS.md` empty · on divergence: `git checkout -- .planning/REQUIREMENTS.md` and report | ✅ N/A — created by the task | ⬜ pending |
| _(operator, outside any plan)_ | — | post-phase | REL-11 / D-16 / SC#3 — **third observation, after `phase.complete`-family tooling** | the flip that historically lands *after* the last plan is caught | audit (checksum) | the same three commands re-run once more after `phase.complete` has run — recorded in `63-CLOSEOUT-GUARD.md`'s "For the operator running phase.complete" section. **This is the observation that actually catches the flip, because it runs outside any plan's reach.** | ✅ N/A — created by the plan | ⬜ pending |
| _(planner)_ | _(planner)_ | _(planner)_ | SC#5 / D-13 / D-14 / D-15 — the standalone handoff | the handoff cannot be read as authorising a publish, and cannot omit a step | audit | `63-HANDOFF.md` opens by stating the POSITIVE (this milestone **does** publish) · the `v0.9.2` tag push, the `pypi` Environment approval named as an **expected** gate *before* the step that triggers it, the Release body's byte-identity to the extractor's stdout, the `update-pin.yml` **manual dispatch**, and the RTD `en`/`ja` `stable` checks all present · D-14's four REL-04 items present | ✅ N/A — created by the task | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Every plan's `SUMMARY.md` frontmatter declares `requirements-completed: []` for REL-09** (D-16).
REL-09 is cited as a coverage ID only; no plan closes it and no plan touches its checkbox.

---

## Wave 0 Requirements

**None. Existing infrastructure covers every phase requirement.** The full pytest suite, the `tox`
lint/type/docs environments, `ci.yml`'s 3-OS matrix, `scripts/extract_changelog_section.py` with its
pytest coverage (`tests/test_changelog_extraction.py`), and `tests/test_changelog_page_gate.py` are
all already in place and were exercised as recently as CI run `33302087913` (Phase 62's close) and
the local suite recorded in `62-VERIFICATION.md`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The `## [0.9.2]` lead paragraph reads as prose a user reads, names the 0.9.0 upgrade urgency in one sentence, and **never names 0.9.1** | REL-10 / D-01, D-02, D-08 | Prose quality and the absence of a version name are judgements, not assertions; the greps below catch only the mechanical half | `grep -c '0\.9\.1' CHANGELOG.md` → 0 inside the new section; then read the paragraph against `## [0.6.5]` (`CHANGELOG.md:381-403`), the measured structural analog |
| The three promoted `### Unreleased` bullets are **verbatim**, with the MSG bullet's apostrophe-path clause intact | REL-10 / D-04 | "Verbatim except a clause the lead paragraph makes literally redundant" is a judgement about redundancy | `git diff` the promoted region against `CHANGELOG.md:10-36` at `PHASE_BASE_SHA`; confirm the POSIX-apostrophe clause survives (the release is **not** Windows-exclusive) |
| Each `### Verified` bullet is backed by a run recorded in **this** phase's or Phase 62's evidence | REL-10 / D-06 | Provenance of a claim cannot be asserted by a test | For each of the three bullets, name the evidence file and line it rests on. **Do not copy prior entries' "full-corpus `-b typstpdf` re-run remains fatal-free" sentence** — this phase does not run that corpus (D-06's explicit warning) |
| `63-HANDOFF.md` is standalone — an operator who reads only it can execute `/gsd-complete-milestone` | SC#5 / D-13 | Standalone-ness is a reading test | Read it cold against SC#5's five enumerated steps; every one present, in the operator's own execution order |

---

## Skipped is not passed

Two failure modes in this phase record a **skip** as if it were a pass:

1. **`tests/test_changelog_page_gate.py` under a `--extra dev`-only sync.** `myst_parser` is in the
   `docs` extra only; both content-coverage classes are guarded on importing it, so they SKIP
   silently. A green worktree `pytest` **does not prove D-11**. The proof must come from a
   `--extra dev --extra docs` run, or from the dispatched CI run, and the plan must say which. Assert
   on **`PASSED` counts with zero `SKIPPED`**, not on exit code.
2. **`ruff` on this host.** It is an unrunnable generic-linux ELF in a freshly provisioned worktree
   venv. A `black`+`mypy` green is **not** "lint clean". `ruff`'s verdict comes from CI (below) —
   never from a local attempt, and never from silence.

The 5-skip full-suite baseline is itemised above precisely so that a *sixth* skip is visible as a
finding rather than absorbed into "5 skipped, as expected".

---

## The lint-step name (D-18 AMENDED)

`ci.yml` carries **no** step named `Run linters`. Measured 2026-08-30 with
`grep -rn 'Run linters' .github/`: exactly one hit, `.github/workflows/release.yml:84` — the
workflow this prep-only phase must **never** trigger. `ci.yml`'s `lint` job (`ci.yml:51-70`, display
name **`Lint and Format Check`**) has one substantive step, **`Run lint with tox`** (`ci.yml:69`),
running `uv run tox -e lint` → `tox.ini`'s `[testenv:lint]` → `black --check .` then `ruff check .`.

Read `ruff`'s verdict as the `Lint and Format Check` job's conclusion in
`gh run view <id> --json jobs`, and quote the `Run lint with tox` step's own `ruff check .` output
verbatim in `63-CI-EVIDENCE.md`. See `63-CONTEXT.md` § Amendments item 1 — this is the third
recurrence of the wrong name and the first fixed at the source.

---

## Evidence-file naming constraint (D-19)

`{padded_phase}-VERIFICATION.md` is `gsd-verifier`'s **reserved output name**; a plan-authored file
there is clobbered at verify time. **No plan may write `63-VERIFICATION.md`.** The permitted set,
mirroring Phase 61's: `63-CLOSEOUT-GUARD.md`, `63-CHANGELOG-EVIDENCE.md`,
`63-GREEN-TREE-EVIDENCE.md`, `63-CI-EVIDENCE.md`, `63-SC5-INVARIANTS.md`, `63-HANDOFF.md`.

---

## `uv lock` sequencing constraint (D-17)

`uv lock` runs and is **committed before** the CI dispatch. Every CI job begins with
`uv sync --extra dev --locked`; `uv.lock:1467` currently reads `version = "0.9.0"` for the
self-package, independently of `pyproject.toml:7`. Dispatching before regenerating reproduces the
exact refusal already killing every dependabot PR, and it fails at the *install* step — before any
test, lint or type signal exists. `uv.lock` is regenerated with `uv lock` and **never hand-edited**.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or a recorded-observation audit with a stated positive control
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references — *(none; existing infrastructure suffices)*
- [ ] No watch-mode flags
- [ ] Feedback latency < 10 min (local suite minutes; CI dispatch ≈ 7 min)
- [ ] D-11's proof recorded from a `--extra docs` run or from CI — never from a `--extra dev`-only skip
- [ ] `ruff` verdict recorded from `ci.yml`'s `Lint and Format Check` job, not from this host
- [ ] The two SC#5 fence observations sit in **different waves**
- [ ] No plan writes `63-VERIFICATION.md`
- [ ] Every plan declares `requirements-completed: []` for REL-09
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
