# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- ✅ **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (shipped 2026-07-29) → [archive](milestones/v0.6.5-ROADMAP.md)
- ✅ **v0.7.0 — API rendering design overhaul** — Phases 36–42 (+40.1) (shipped 2026-08-04) → [archive](milestones/v0.7.0-ROADMAP.md)
- ✅ **v0.7.1 — bug-fix round** — Phases 43–46 (+44.1, 44.2, 45.1, 45.2) (shipped 2026-08-11) → [archive](milestones/v0.7.1-ROADMAP.md)
- ✅ **v0.8.0 — multi-master composition** — Phases 47–52 (shipped 2026-08-15) → [archive](milestones/v0.8.0-ROADMAP.md)
- ✅ **v0.9.0 — per-document templates** — Phases 53–57 (+54.1) (shipped 2026-08-22) → [archive](milestones/v0.9.0-ROADMAP.md)
- ✅ **v0.9.1 — Windows path correctness** — Phases 58–61 (completed 2026-08-30, **never published**) → [archive](milestones/v0.9.1-ROADMAP.md)
- ✅ **v0.9.2 — Inline image blocker fix and release** — Phases 62–63 (shipped 2026-08-31) → [archive](milestones/v0.9.2-ROADMAP.md)
- ✅ **v0.9.3 — Toolchain and dependency-update repair** — Phases 64–69 (completed 2026-09-13, merged to `main`, **not published**) → [archive](milestones/v0.9.3-ROADMAP.md)
- ✅ **v0.9.4 — Typing Modernization** — Phases 70–71 (completed 2026-09-13, merged to `main`, **not published**) → [archive](milestones/v0.9.4-ROADMAP.md)
- ✅ **v0.9.5 — Docs Link Check and Navigation** — Phases 72–73 (completed 2026-09-16, merged to `main`, **not published**) → [archive](milestones/v0.9.5-ROADMAP.md)
- ✅ **v0.9.6 — Doctest block rendering and release** — Phases 74–75 (**shipped 2026-09-22, PUBLISHED**) → [archive](milestones/v0.9.6-ROADMAP.md)

**No milestone is active.** v0.9.6 shipped and was published to PyPI on 2026-09-22, ending a
three-milestone run in which v0.9.3, v0.9.4 and v0.9.5 were completed and merged but never
released — all three went out under `## [0.9.6]`. The next milestone is scoped by
`/gsd-new-milestone`, which writes a fresh `REQUIREMENTS.md`.

Phase numbering is **continuous across milestones**: v0.9.6 ran Phases 74–75, so the next milestone
starts at **Phase 76**.

## Phases

**Phase Numbering:**

- Integer phases (76, 77): Planned milestone work
- Decimal phases (76.1, 76.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1).

<details>
<summary>✅ v0.9.6 Doctest block rendering and release (Phases 74–75) — SHIPPED 2026-09-22, PUBLISHED</summary>

- [x] Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors (7/7 plans) — completed 2026-09-20
- [x] Phase 75: v0.9.6 Release Prep (prep-only) (7/7 plans) — completed 2026-09-22

5/5 v1 requirements complete. REL-15 was checked at the close, by hand, against the four
observations its own text names: the merge commit `6fcc5adb` on `origin/main`'s first-parent
history (PR #156, 15/15 checks green), `refs/tags/v0.9.6`, a PyPI 200 for `0.9.6` against a 404 for
`0.9.5` as negative control, and the Release in `gh release list`. `release.yml` run `35730551619`
succeeded on every job, `create-release` included — it had never run on a v0.9.x tag before.
`override_closeout` (both phases' verifications read fingerprint-stale from later `.planning/`
tracking commits while both VERIFICATION.md files themselves read `passed`; the same-day audit
stood in — the fourth consecutive close with that exact reading). The pre-close artifact audit
found 2 open todos and **both were fixed rather than acknowledged**, as quick tasks `260922-tbe`
and `260922-tkt`, because the prep-only fence that had deferred them lapsed once `origin/main`
moved and a CI re-dispatch became mandatory anyway. Full phase detail, the binding constraints,
success criteria and decisions: [milestones/v0.9.6-ROADMAP.md](milestones/v0.9.6-ROADMAP.md).
Audit: [milestones/v0.9.6-MILESTONE-AUDIT.md](milestones/v0.9.6-MILESTONE-AUDIT.md).
Quick tasks: `milestones/v0.9.6-quick/`.

</details>

<details>
<summary>✅ v0.9.5 Docs Link Check and Navigation (Phases 72–73) — COMPLETED 2026-09-16, MERGED, NOT PUBLISHED</summary>

- [x] Phase 72: `tox -e linkcheck` and Root Toctree Deduplication (6/6 plans) — completed 2026-09-14
- [x] Phase 73: v0.9.5 Close Prep (prep-only, unpublished) (7/7 plans) — completed 2026-09-16

4/4 v1 requirements complete; REL-14 checked at the close on the observed merge of PR #151
(`43fd7c13`). QUA-08, the weekly advisory linkcheck CI workflow, was scoped in at roadmap creation
and deferred to Future the same day, so it maps to no phase. `override_closeout` (both phases'
verifications read fingerprint-stale from later `.planning/` tracking commits while both
VERIFICATION.md files themselves read `passed`; the same-day audit stood in). Full phase detail, the
binding constraints, success criteria and decisions:
[milestones/v0.9.5-ROADMAP.md](milestones/v0.9.5-ROADMAP.md).
Audit: [milestones/v0.9.5-MILESTONE-AUDIT.md](milestones/v0.9.5-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v0.9.4 Typing Modernization (Phases 70–71) — COMPLETED 2026-09-13, MERGED, NOT PUBLISHED</summary>

- [x] Phase 70: Typing Modernization and Its Behaviour-Identity Evidence (13/13 plans) — completed 2026-09-13
- [x] Phase 71: v0.9.4 Close Prep (prep-only, unpublished) (7/7 plans) — completed 2026-09-13

6/6 v1 requirements complete; REL-13 checked at the close on the observed merge of PR #145
(`383a07e9`). `override_closeout` (Phase 70's verification fingerprint-stale after REL-13's AMENDED
block landed in `REQUIREMENTS.md`; the same-day audit stood in). Full phase detail, the 13 binding
constraints, success criteria and decisions: [milestones/v0.9.4-ROADMAP.md](milestones/v0.9.4-ROADMAP.md).
Audit: [milestones/v0.9.4-MILESTONE-AUDIT.md](milestones/v0.9.4-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v0.9.3 Toolchain and dependency-update repair (Phases 64–69) — COMPLETED 2026-09-13, MERGED, NOT PUBLISHED</summary>

- [x] Phase 64: FHS Wrapper and Command Shims in `flake.nix` (6/6 plans) — completed 2026-09-12
- [x] Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves (2/2 plans) — completed 2026-09-12
- [x] Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem (4/4 plans) — completed 2026-09-12
- [x] Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128 (5/5 plans) — completed 2026-09-12
- [x] Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` (4/4 plans) — completed 2026-09-13
- [x] Phase 69: v0.9.3 Close Prep (prep-only, unpublished) (6/6 plans) — completed 2026-09-13

21/21 v1 requirements complete; REL-12 checked at the close on the observed merge of PR #143.
`override_closeout` (all six verifications fingerprint-stale after later legitimate edits; the
same-day audit stood in). Full phase detail, the 15 binding constraints, success criteria and
decisions: [milestones/v0.9.3-ROADMAP.md](milestones/v0.9.3-ROADMAP.md). Audit:
[milestones/v0.9.3-MILESTONE-AUDIT.md](milestones/v0.9.3-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v0.9.2 Inline image blocker fix and release (Phases 62–63) — SHIPPED 2026-08-31</summary>

- [x] Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate (4/4 plans) — completed 2026-08-30
- [x] Phase 63: v0.9.2 Release Prep (prep-only) (6/6 plans) — completed 2026-08-30

7/7 v1 requirements complete; `verified_closeout`. Full phase detail, the 14 binding constraints,
success criteria and decisions: [milestones/v0.9.2-ROADMAP.md](milestones/v0.9.2-ROADMAP.md)

</details>

<details>
<summary>✅ v0.9.1 Windows path correctness (Phases 58–61) — COMPLETED 2026-08-30, NOT PUBLISHED</summary>

- [x] Phase 58: `repr()`-Format Decoupling (test-side only) (3/3 plans) — completed 2026-08-28
- [x] Phase 59: Path-Shape Predicate and Image-URI Correctness (5/5 plans) — completed 2026-08-29
- [x] Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere (5/5 plans) — completed 2026-08-29
- [x] Phase 61: v0.9.1 Release Prep (prep-only) (4/4 plans) — completed 2026-08-30

10/11 v1 requirements complete. REL-09 (publish to PyPI) deliberately unmet — the release was
cancelled, not missed. It carried forward into v0.9.2 and closed there. Full phase detail:
[milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md)

</details>

<details>
<summary>✅ v0.4.4 – v0.9.0 (Phases 1–57) — SHIPPED 2026-07-05 → 2026-08-22</summary>

Each milestone's phase detail lives in its own archive, linked from the **Milestones** list above.

</details>

## Progress

Phases 1–75 shipped or completed across v0.4.4 → v0.9.6; their per-phase plan counts, statuses and
completion dates are preserved in each milestone's archived roadmap under `milestones/`. The table
below tracks the active milestone only, and is empty until `/gsd-new-milestone` writes the next one.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.6's live in
[milestones/v0.9.6-ROADMAP.md](milestones/v0.9.6-ROADMAP.md): the one-work-phase-plus-close-prep
shape, the acceptance gate being this project's own documentation build rather than a scratch
fixture, and REL-15 mapped to Phase 75 for coverage only while REL-16 closed inside it — which is
why that phase's `REQUIREMENTS.md` fence was line-scoped for the first time.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog has been empty since
2026-08-04. Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst
error) was promoted into v0.6.5 as Phase 34 / requirement MATH-01 and shipped 2026-07-29. Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** and shipped in v0.7.0. Numbering does not reuse
retired numbers, so the next item filed here is **999.3**.

**Closed at the v0.9.6 close (2026-09-22):**

- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line` (TRN-01) — closed by Phase 74.
- `2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node` (IN-01) — closed
  by quick task `260922-tbe`, not deferred a second time.
- `2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck` — closed
  by quick task `260922-tkt`. Its own proposed fix would have been a silent no-op: Sphinx's
  `_check_uri` strips the fragment **before** matching `linkcheck_anchors_ignore_for_url`, so a
  pattern carrying `#history` never matches, and a bare `pypi\.org` entry would prefix-match every
  PyPI project page. The landed pattern is end-anchored at the bare project URL.

**Still open after v0.9.6, not scoped:**

- `2026-07-22-add-sphinx-linkcheck-ci-job` — **half closed; it stays in `pending/`.** Phase 72 (v0.9.5)
  landed the `tox -e linkcheck` environment (QUA-13) and listed it on all three surfaces (DOC-24).
  The CI job the todo is actually about (QUA-08, superseding LNK-01) is Future. **Its stated obstacle
  is now gone and has been for two consecutive milestones** — a new workflow file cannot be scheduled
  or `workflow_dispatch`-ed from an unmerged milestone branch, but the environment it would call has
  been on `main` since v0.9.5, so a side PR to `main` is the route whenever it is picked up. Note
  that `links.yml`'s lychee job is **not** this: it scans the repository over HTTP and cannot see
  `#anchor` existence or URLs reached through autodoc docstrings, which is exactly what
  `-b linkcheck` adds. The todo's "Solution" section proposed `linkcheck_ignore` up front; the one
  `linkcheck_*` key this project now has was earned by a measured failure (the PyPI interstitial),
  and nothing else has been.

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — **now disclosed but still unfixed.** REL-16 settled the question at v0.9.6:
  `## [0.9.6]`'s `### Known Limitations` names it with its precondition (multi-master only), both
  symptoms (diverging number; fallback to raw label text) and a workaround. D-07's five-milestone
  exclusion from every published surface is therefore over; the underlying divergence is unchanged.

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — `translator.py`'s two relative-path DEBUG logs carry the same
  hardcoded-`'...'` delimiter shape Phase 60 closed in three other modules; the one-line fix is
  `quote_path()`, which exists. Deferred once more under Phase 75's prep-only fence and **not**
  picked up when its two siblings were closed at the v0.9.6 close.

- **ATT-01** (filed 2026-09-22, no todo file yet) — `release.yml` passes `attestations: true` to
  `pypa/gh-action-pypi-publish` alongside an explicit password, which disables Trusted Publishing and
  makes the attestations input a no-op. Surfaced as an annotation on release run `35730551619`; the
  upload succeeded, so this is a supply-chain-provenance gap, not a release blocker.

**Dormant seeds:**
- **`SEED-001-readme-quickstart-typst-documents-pdf`** — substantially discharged by v0.7.1's
  CONF-08 + DOC-11 and v0.8.0's DOC-14.
- **`SEED-003-tox-dependency-groups-per-env`** (Future QUA-07) — splitting the `dev` extra into PEP
  735 `[dependency-groups]`. A phase touching `pyproject.toml` or `tox.ini` must not absorb it
  opportunistically.
- **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`** — `typst-py` upstream maintenance
  is slowing, and typsphinx may eventually need to carry an equivalent compile path. It is still the
  single largest structural risk on the horizon, and it has never been scoped into any milestone
  across eleven consecutive scopings.
- **`SEED-005-gsd-workstreams-for-parallel-roadmap-tracks`** — adopt GSD workstreams so independent
  roadmap tracks run in parallel; dormant since v0.9.3.

**Known limitations still shipped, now with one published surface.** After v0.9.6, WR-02's `confdir`
gap and the tripled "Custom template not found" warning remain silent on every public surface;
NUM-01 no longer does. Phase 75's `VALIDATION.md` is at `status: draft` — the third consecutive
release-prep phase to skip `/gsd-validate-phase`, which is worth deciding about deliberately rather
than re-discovering at a fourth close.

**Standing risk carried from v0.9.3:** `flake.nix` is load-bearing while keeping **zero CI
coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only when the
maintainer next enters the shell, and the darwin branch of the per-system guard cannot be exercised
from a Linux machine at all. Accepted deliberately (owner decision 2026-09-02); documented on the
surface itself by v0.9.3's DOC-21.

**Risk discharged at v0.9.6:** `release.yml`'s `create-release` job, which had never run on a v0.9.x
tag, ran on `v0.9.6` and succeeded (run `35730551619`).

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31), v0.9.3 (2026-09-13 — merged, not published), v0.9.4 (2026-09-13 — merged, not published), v0.9.5 (2026-09-16 — merged, not published), v0.9.6 (2026-09-22 — **shipped and published**). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. No milestone is active; the next is scoped by `/gsd-new-milestone`, continuing at **Phase 76**.*
