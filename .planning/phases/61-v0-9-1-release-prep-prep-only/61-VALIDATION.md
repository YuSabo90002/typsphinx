---
phase: 61
slug: v0-9-1-release-prep-prep-only
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-29
---

# Phase 61 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `61-RESEARCH.md` § "Validation Architecture".
>
> **This is a process-verification phase, not a product-behaviour phase.** No `typsphinx/` code
> changes (the prep-only fence is absolute — `61-CONTEXT.md` `<domain>` "Out of scope"), so there is
> no new unit or integration test to write and **no RED-first gate applies**. What is being validated
> is that the milestone-final tree is green on *live runs observed in this phase* rather than
> inherited from Phases 59/60's word (D-09), and that no irreversible action occurred (D-10).
>
> **The ROADMAP's SC#1 and SC#2 do not bind this phase.** `61-CONTEXT.md` D-11 maps SC#1 to DROPPED
> and SC#2 to REWORDED: there is no version bump and no `## [0.9.1]` section. Any validation item
> below that appears to assume a bump is absent by design, not by omission.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), orchestrated via `tox` (`env_list = py312, py313, lint, type, cov, docs`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; `tox.ini` |
| **Quick run command** | `uv run pytest -m "not slow"` |
| **Full suite command** | `uv run pytest` (full suite, including the `@pytest.mark.slow` corpus gate) |
| **Estimated runtime** | quick ~tens of seconds · full suite several minutes (PDF-compiling integration tests dominate) |

**Worktree note (CLAUDE.md § "Worktree-isolated execution", STANDING):** worktree isolation is the
standing execution mode. Every executor first runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree, then runs
**every** command via `uv run`. Without this, pytest imports the unchanged main-tree package.

**Docs-warning baseline (measured, reusable — `61-RESEARCH.md`):** `tox -e docs-html` → **3**
warnings, `tox -e docs-pdf` → **5** warnings, established at Phase 56 close and reconfirmed
byte-identical at Phase 57's close. `git log 130f614e..HEAD -- docs/source CHANGELOG.md` is empty as
of research time, so the baseline still applies — but a **fresh** run of both environments is still
required *after* the `## [Unreleased]` bullets land, because the point of the check is to prove that
the CHANGELOG edit itself introduces no new warning. A reused baseline number is not a substitute for
running the build.

---

## Sampling Rate

- **After every task commit:** no product code changes, so there is no per-commit product gate. The
  per-task gate is the task's own evidence artifact being written and readable.
- **After every plan wave:** `uv run pytest` (full suite) plus `uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`.
- **After the CHANGELOG edit specifically:** `uv run tox -e docs-html` and `uv run tox -e docs-pdf`,
  warning counts compared against the 3 / 5 baseline above.
- **Phase gate:** a fresh 3-OS CI dispatch (`gh workflow run ci.yml --ref <branch>`) on the phase's
  final tip, with **both `windows-latest` lanes green** — the milestone's own acceptance bar
  (REQUIREMENTS.md § "Standing constraints" #6), observed here per D-09. One dispatch on the final
  code tip is the default; a second is warranted only if a plan lands a code-affecting change
  mid-phase.
- **Max feedback latency:** local suite minutes; CI dispatch ~7 min wall clock (prior run
  `33252336287` took 6m37s).

---

## Per-Task Verification Map

Task IDs are assigned at plan time (`61-{plan}-T{task}`). This table is seeded with the phase's known
verification surfaces; the planner fills in the concrete task IDs. Every row's command is runnable
today — there is no Wave 0 gap.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD (closeout guard, phase head) | TBD | 1 | D-10 / SC#4 | T-61-02 | the `phase.complete` REL-09 auto-flip is detected rather than shipped | audit (checksum) | `sha256sum .planning/REQUIREMENTS.md` recorded at phase head + guarded-line quote; re-verified at close | ✅ exists | ⬜ pending |
| TBD (fence probe #1) | TBD | 1 | D-10 / SC#4 | T-61-02 | no irreversible action has occurred | audit | `git tag -l 'v0.9.1'` (empty) · `git ls-remote --tags origin 'v0.9.1'` (empty) · `gh release list` (latest is `v0.9.0`) | ✅ exists | ⬜ pending |
| TBD (CHANGELOG authoring) | TBD | — | D-03 / SC#2-reworded | T-61-01 | a malformed bullet cannot reach a published surface | docs build | `uv run tox -e docs-html` and `uv run tox -e docs-pdf`, warning counts == 3 / 5 | ✅ exists | ⬜ pending |
| TBD (green-tree proof) | TBD | — | D-09 / SC#3 | — | N/A | full-suite + lint/type | `uv run pytest` · `uv run black --check .` · `uv run ruff check .` · `uv run mypy typsphinx/` | ✅ exists | ⬜ pending |
| TBD (3-OS CI dispatch) | TBD | — | D-09 / SC#3 | — | N/A | CI | `gh workflow run ci.yml --ref <branch>` → `gh run list --workflow=ci.yml --branch <branch> --limit 1` → `gh run watch <run-id>` → `gh run view <run-id> --json jobs`; both `windows-latest` lanes green | ✅ `.github/workflows/ci.yml` | ⬜ pending |
| TBD (fence probe #2, separated) | TBD | last | D-10 / SC#4 | T-61-02 | the fence held for the *whole* phase, not just at its head | audit | same probes as #1, at a genuinely later timestamp; plus `git diff <phase-base>..HEAD -- typsphinx/` empty | ✅ exists | ⬜ pending |
| TBD (handoff) | TBD | last | D-12 / D-13 / SC#5-reaimed | — | N/A | audit | `61-HANDOFF.md` exists, opens with the negative (this milestone publishes nothing), and names all three inherited publish steps | ✅ N/A — created by the task | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No framework install, no new fixture, no new
test file, and no new `conftest.py` entry is needed — the full pytest suite, the `tox` lint / type /
docs environments, and `ci.yml`'s 3-OS matrix are all already in place and were exercised as recently
as CI run `33252336287`.

The version-sync guard family (`tests/test_readme_version_sync.py`,
`tests/test_extension.py::test_version_matches_pyproject_toml`, `tests/test_preview_version_sync.py`)
stays green trivially under D-01 because nothing moves — but it must still be **run** as part of the
SC#3 suite rather than reasoned about as un-failable.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 3-OS CI matrix green on the phase-final tip | D-09 / SC#3 | Requires a GitHub Actions dispatch; cannot run inside a worktree. `ci.yml`'s push trigger is `[main, develop]` only, so `workflow_dispatch` is the only route that does not require opening a PR (which is out of scope). | Push the phase tip, dispatch `ci.yml` fresh on the branch, confirm all 12 jobs green with **both** `windows-latest` lanes among them; record the run id and URL in the CI evidence file. |
| "Probed twice at separated times" for the fence | D-10 / SC#4 | Separation in time is the point of the check; it cannot be collapsed into one command run. | Record probe #1 at phase head (with its wall-clock timestamp) and probe #2 in the phase's last wave, and show the two timestamps are genuinely apart. |

Every other phase behavior has automated verification.

---

## Evidence-File Naming Constraint (CONTEXT.md § Claude's Discretion)

Evidence files follow `{padded_phase}-{TOPIC}-EVIDENCE.md`, the precedent set by the `52-*` family and
followed by `60-01-EVIDENCE.md` … `60-05-EVIDENCE.md`. **No file in this phase may be named
`61-VERIFICATION.md`** — that name is reserved by `gsd-verifier` and is overwritten wholesale
(58 D-07, 59 D-11, and the standing note in `61-CONTEXT.md`).

---

## `uv.lock` sequencing constraint (57-CONTEXT D-13 AMENDED)

Every CI job begins with `uv sync --extra dev --locked` (10 steps across four workflows). Nothing in
this phase should change dependencies — but if anything does, `uv.lock` must be regenerated and
committed **before** the CI dispatch, or every lane fails on the lock mismatch rather than on
anything this phase did.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (none — existing infrastructure suffices)
- [ ] No watch-mode flags
- [ ] Docs-warning counts re-measured on this tree after the CHANGELOG edit and compared to 3 / 5
- [ ] Fence probed twice at genuinely separated timestamps
- [ ] `REQUIREMENTS.md` checksum recorded at phase head and re-verified at close
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
