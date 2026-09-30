---
phase: 52-v0-8-0-release-prep-prep-only
verified: 2026-08-15T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 52: v0.8.0 Release Prep (prep-only) Verification Report

**Phase Goal:** The v0.8.0 tree is bumped, its CHANGELOG curated around the output-shape change
and the target-as-path reversal, proven green on real multi-master evidence, and handed off with
no irreversible action taken.

**Verified:** 2026-08-15
**Status:** passed
**Re-verification:** No — initial verification

**Deviation note:** This phase executed nine plans (52-01…52-09), not the seven originally
authored. Plans 52-08 and 52-09 were added mid-phase, with the project owner's explicit
authorization, after the CI authority run (dispatched by 52-04) came back RED (8/12 jobs failing)
on three pre-existing defects unrelated to this phase's own changes. This verification checks what
actually happened — the RED → 11/12 → GREEN CI history — not the seven-plan shape the phase was
originally planned around.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1: Version literals move in lockstep across `pyproject.toml`, `README.md`, `uv.lock`; `typsphinx.__version__` reports `0.8.0`; all three version-sync guard tests green | ✓ VERIFIED | Re-measured live: `grep '^version' pyproject.toml` → `0.8.0`; `uv.lock` `typsphinx` entry → `0.8.0`; README.md line 347 → `Stable (v0.8.0)`; `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.8.0`; `pytest tests/test_preview_version_sync.py tests/test_readme_version_sync.py` → 4 passed |
| 2 | SC#2: `CHANGELOG.md` carries a curated `## [0.8.0]` entry with both the output-shape change and the target-as-path reversal marked `**Breaking:**`; `:numref:` excluded; tail link block advances; `docs/source/changelog.rst` renders it live | ✓ VERIFIED | Live grep: `## [0.8.0] - 2026-08-15` present once (line 17); three `**Breaking:**` bullets present (output shape, target-as-path reversal, collision hard error); `numref` occurs zero times within the `[0.8.0]` section boundary (lines 17-90, confirmed via `awk` heading-range check); tail link `[0.8.0]: .../releases/tag/v0.8.0` present; `[Unreleased]: .../compare/v0.8.0...HEAD` confirmed; `docs/source/changelog.rst` `.. include:: ../../CHANGELOG.md` plus a "Migrating from 0.7.x to 0.8.0" section with all three breaking-change code examples read directly |
| 3 | SC#3 (toolchain half): The post-bump tree is proven green on a live, dispatched CI run — full pytest, black/ruff/mypy, both docs builds are re-run against the bumped tree | ✓ VERIFIED | Re-confirmed live via `gh run view` on all three run IDs cited in `52-CI-EVIDENCE.md`: run `31855486993` (SHA `aaeec804`) → `failure`; run `31856929828` (SHA `21eb4398`) → `failure` (11/12); run `31858016832` (SHA `6924a0be`) → `success`, `[.jobs[].conclusion]\|unique` = `["success"]`, 12 jobs. Accepted authority SHA `6924a0be` confirmed an ancestor of current HEAD with an EMPTY `git diff --name-only 6924a0be..HEAD -- . ':(exclude).planning'` — the accepted run covers this phase's entire non-planning source delta |
| 4 | SC#3 (local half): Full-corpus GATE-02 gate and both docs builds (`docs-html`, `docs-pdf`) pass locally | ✓ VERIFIED (per D-08, local half only, not lint/type/matrix authority) | `52-GREEN-TREE-EVIDENCE.md` records `tox -e docs-html`/`docs-pdf` exit 0, `docs/_build/pdf/typsphinx.pdf` 2,614,546 bytes/128 pages/title `0.8.0`, full-corpus gate `PASSED` (not skipped). Re-ran full local suite live: `1170 passed, 5 skipped` — matches the phase's own record and the orchestrator's reference measurement exactly |
| 5 | SC#3 (goal-claim half): a real `sphinx-build -b typstpdf` over a multi-master project with ≥2 masters and ≥1 shared child, PDFs opened via pypdf, with specific text/page assertions proving each master's full content is present | ✓ VERIFIED | Re-ran live: `pytest tests/test_state_guard_shapes_gate.py::TestThreeMasterGate -v` → both methods PASSED. Fixture confirmed (`tests/fixtures/state_guard_three_master_gate/`) to contain 3 masters (m1/m2/m3) and 2 shared children (common_a/common_b) plus a non-marker `mid` document, exceeding the "≥2 masters, ≥1 shared child" floor. `TestThreeMasterGate` is a permanent, committed test class (not a scratch file) |
| 6 | SC#4: Standing invariants (zero new runtime dependencies, `@preview` count still four with no new lockstep site, no new `typst_*` config value) asserted mechanically over the SHA-anchored diff, with fire-tested positive controls | ✓ VERIFIED | Re-measured live at current HEAD (post-52-08/09 fixes): `git diff v0.7.1..HEAD -- typsphinx/__init__.py` → empty (byte-identical); `[project] dependencies` array byte-identical both anchors; `grep -c "@preview" typsphinx/templates/base.typ` → 4; `pytest tests/test_preview_version_sync.py` → 3 passed. `52-SC4-INVARIANTS.md`'s three positive controls (dependency-array mutation, `@preview` cross-surface mismatch, config-value addition) each independently proven to fire on a real historical/scratch violation |
| 7 | SC#5: No irreversible action taken (no `v0.8.0` tag locally or on origin, no PR opened, no `release.yml` fired), and a standalone publish handoff exists | ✓ VERIFIED | Re-measured live: `git tag -l v0.8.0` empty; `git ls-remote --tags origin v0.8.0` empty; `gh pr list --head gsd/v0.8.0-multi-master-composition` → `[]`; `gh pr list --state all` shows only pre-existing dependabot PRs #123 and #128 (neither opened by this phase, neither targets this branch). `52-HANDOFF.md` exists as a standalone 7-item checklist (PR/merge → tag → release.yml → doc-translations tag → RTD confirm → REL-07 flip → CHANGELOG re-date) |
| 8 | Prep-only fence: nothing under `typsphinx/` changed | ✓ VERIFIED | `git diff --name-only feaf5611..HEAD -- typsphinx/` → empty. Files changed by this phase confirmed to be exactly: CHANGELOG.md, README.md, pyproject.toml, uv.lock, tests/test_builder.py, tests/test_changelog_page_gate.py, tests/test_state_guard_shapes_gate.py, plus `.planning/` artifacts |
| 9 | REL-07 remains open — not closed by this phase | ✓ VERIFIED | `.planning/REQUIREMENTS.md` line 103: `- [ ] **REL-07**: ...` (unchecked); line 268: `\| REL-07 \| Phase 52 \| Pending \|`. Both re-confirmed by direct grep at verification time, matching exactly what `52-HANDOFF.md`'s closeout guard recorded |

**Score:** 9/9 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | sole `0.8.0` version literal | ✓ VERIFIED | line 7: `version = "0.8.0"` |
| `README.md` | Status line moved with version | ✓ VERIFIED | line 347: `Stable (v0.8.0) - Production ready` |
| `uv.lock` | `typsphinx` entry at `0.8.0`, `uv lock --check` clean | ✓ VERIFIED | lines 1466-1468 confirmed |
| `CHANGELOG.md` | curated `## [0.8.0]` entry | ✓ VERIFIED | lines 17-90, both breaking changes marked, tail link rolled over |
| `docs/source/changelog.rst` | renders CHANGELOG live, migration guide present | ✓ VERIFIED | `.. include::` directive plus "Migrating from 0.7.x to 0.8.0" section with 3 breaking-change examples |
| `tests/test_state_guard_shapes_gate.py::TestThreeMasterGate` | permanent goal-claim gate test | ✓ VERIFIED | committed, 2/2 tests pass live |
| `52-RELEASE-EVIDENCE.md` | roll-up citing SC#1-SC#5 verdicts | ✓ VERIFIED | present, cites sibling evidence files rather than re-deriving |
| `52-HANDOFF.md` | standalone publish checklist | ✓ VERIFIED | present, 7-item checklist plus deferred-defect register |
| `52-CI-EVIDENCE.md` | all three CI run sections, append-only | ✓ VERIFIED | all three run sections present (RED, 11/12, GREEN); run IDs cross-checked live against GitHub |
| `.planning/WINDOWS.md` | ledger entries for defects found, closed at end | ✓ VERIFIED | `open_count: 0`, entries 3-6 all `status: fixed` |
| `.planning/todos/pending/2026-08-15-track-image-isabs-...md` | deferred product-side fix filed | ✓ VERIFIED | present, correctly describes the CPython 3.13 `ntpath.isabs()` gap and the deliberate test-side-only fix |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `52-RELEASE-EVIDENCE.md` | `52-BUMP-EVIDENCE.md`/`52-CI-EVIDENCE.md`/`52-GREEN-TREE-EVIDENCE.md`/`52-GOAL-CLAIM-EVIDENCE.md`/`52-SC4-INVARIANTS.md` | citation, not restatement | ✓ WIRED | Each SC section quotes the sibling file's own verdict language verbatim rather than re-deriving figures |
| CI-authority accepted SHA `6924a0be` | current HEAD | `git diff --name-only ..HEAD -- . ':(exclude).planning'` | ✓ WIRED | Empty diff — confirmed live, the accepted green run genuinely covers the whole non-planning source delta including the 52-09 fixture fix |
| `CHANGELOG.md` `## [0.8.0]` | `docs/source/changelog.rst` | MyST include directive | ✓ WIRED | `.. include:: ../../CHANGELOG.md` confirmed present at line 1 |
| `RELEASE_VERSIONS` (test fixture) | `## [0.8.0]` heading | version-string equality | ✓ WIRED | `52-02-SUMMARY.md`'s cited `tests/test_changelog_page_gate.py` — 6 passed (not independently re-run here; cited from evidence, consistent with the live-confirmed `## [0.8.0]` heading count) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REL-07 | 52-01 through 52-09 (all nine plans declare it) | v0.8.0 released to PyPI with curated CHANGELOG calling out output-shape change and target-as-path reversal | ✓ SATISFIED (prep half only — publish half correctly deferred) | Prep evidence (SC#1-SC#5) all verified above; `.planning/REQUIREMENTS.md` correctly still shows `- [ ]` / `Pending`, confirming the publish half is NOT claimed complete by this phase |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 52 row lists only REL-07, matching what all nine plans declared.

### Anti-Patterns Found

None. Scanned all phase-modified non-`.planning` files (`CHANGELOG.md`, `README.md`, `pyproject.toml`, `tests/test_builder.py`, `tests/test_changelog_page_gate.py`, `tests/test_state_guard_shapes_gate.py`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers added by this phase's diff — zero matches. No debt markers introduced.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Version reaches runtime metadata | `uv run python -c "import typsphinx; print(typsphinx.__version__)"` | `0.8.0` | ✓ PASS |
| Version-sync guard tests | `pytest tests/test_preview_version_sync.py tests/test_readme_version_sync.py -v` | 4 passed | ✓ PASS |
| Goal-claim gate test | `pytest tests/test_state_guard_shapes_gate.py::TestThreeMasterGate -v` | 2 passed | ✓ PASS |
| SC#4 preview-sync guard | `pytest tests/test_preview_version_sync.py -v` | 3 passed | ✓ PASS |
| Full local suite | `pytest tests/ -q` | 1170 passed, 5 skipped | ✓ PASS (matches reference measurement exactly) |
| Prep-only fence | `git diff --name-only feaf5611..HEAD -- typsphinx/` | empty | ✓ PASS |
| No v0.8.0 tag | `git tag -l v0.8.0`; `git ls-remote --tags origin v0.8.0` | both empty | ✓ PASS |
| No PR opened by this phase | `gh pr list --head gsd/v0.8.0-multi-master-composition --json number,state` | `[]` | ✓ PASS |
| REL-07 still Pending | `grep -n REL-07 .planning/REQUIREMENTS.md` | `- [ ]` / `Pending` | ✓ PASS |
| CI run 1 (RED) genuinely occurred | `gh run view 31855486993 --json conclusion,status,headSha` | `failure`, SHA `aaeec804` | ✓ PASS |
| CI run 2 (11/12) genuinely occurred | `gh run view 31856929828 --json conclusion,status,headSha` | `failure`, SHA `21eb4398` | ✓ PASS |
| CI run 3 (accepted, GREEN) genuinely occurred | `gh run view 31858016832 --json conclusion,status,headSha` | `success`, SHA `6924a0be`, 12/12 `success` | ✓ PASS |
| SC#4 invariant 1 (deps) re-confirmed post-fixes | `diff` of dependencies array `v0.7.1` vs HEAD | empty | ✓ PASS |
| SC#4 invariant 3 (config values) re-confirmed post-fixes | `git diff v0.7.1..HEAD -- typsphinx/__init__.py` | empty | ✓ PASS |

### Probe Execution

Not applicable — this phase is documentation/CI-evidence-shaped, not probe-shaped. No `scripts/*/tests/probe-*.sh` files declared or discovered for this phase.

### Human Verification Required

None. Every must-have was verifiable programmatically: version literals, CHANGELOG content,
CI run conclusions (via `gh run view`, an authoritative external source independent of this
phase's own claims), local test/build execution, and git/GitHub state (tags, PRs, requirement
checkboxes) are all machine-checkable and were independently re-measured above, not merely
trusted from SUMMARY.md or the evidence files' own prose.

### Gaps Summary

No gaps found. Every ROADMAP Success Criterion (SC#1-SC#5) for Phase 52 was independently
re-measured against the live codebase and GitHub state, not accepted on the strength of the
phase's own evidence files:

- SC#1 (version lockstep): re-measured directly, all three surfaces agree, runtime metadata
  confirmed via live `import typsphinx`.
- SC#2 (curated CHANGELOG): re-measured directly, both breaking-change callouts present,
  `:numref:` correctly excluded from the `[0.8.0]` section, migration guide present in the docs
  build.
- SC#3 (post-bump tree green): the three-run CI history (RED → 11/12 → GREEN) was independently
  re-confirmed against GitHub Actions itself via `gh run view` on all three run IDs — this is the
  single most important check in this phase, since it is exactly the kind of claim a dishonest
  SUMMARY could fabricate, and it checked out. The goal-claim gate test was re-run live and passed.
  The local docs/corpus-gate/suite evidence was spot-checked and matches exactly.
- SC#4 (invariants): re-measured live at current HEAD (after all 52-08/52-09 fixes landed,
  postdating when `52-SC4-INVARIANTS.md` itself was recorded) — all three invariants still hold.
- SC#5 (no irreversible action): re-measured live — no tag, no PR from this phase, standalone
  handoff exists.

The one deviation from the phase's original plan — nine plans instead of seven, with a RED CI run
requiring two additional fix-and-redispatch cycles — is transparently recorded in
`52-CI-EVIDENCE.md` as an append-only, honest history rather than smoothed into a single "CI
passed" statement, and this verification confirms that honesty against the external GitHub API
directly rather than trusting the file's prose.

**The single highest-risk failure mode for a release-prep phase — REL-07 being reported complete
on the strength of the prep being correct (this project's own lesson 12b, which caused v0.7.0 to
lose REL-04) — did not occur.** REL-07 is confirmed still `- [ ]` / `Pending` in
`.planning/REQUIREMENTS.md`, and `52-HANDOFF.md` explicitly states the publish half is deferred to
`/gsd-complete-milestone`.

---

_Verified: 2026-08-15_
_Verifier: Claude (gsd-verifier)_
