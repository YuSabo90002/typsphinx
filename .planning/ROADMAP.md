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

**No milestone is active.** v0.9.5 completed 2026-09-16 and merged to `main` via PR #151
(`43fd7c13`), with nothing published — no tag, no PyPI upload, no GitHub Release, and
`pyproject.toml` still at `0.9.2`. `## [Unreleased]` now carries six CHANGELOG bullets from three
unpublished milestones (v0.9.3, v0.9.4, v0.9.5); the next release-prep phase promotes all six into
its own versioned section.

Start the next milestone with `/gsd-new-milestone`. Phase numbering is **continuous across
milestones**: v0.9.5 ran Phases 72–73, so the next milestone starts at **Phase 74**.

## Phases

**Phase Numbering:**

- Integer phases (74, 75, …): Planned milestone work
- Decimal phases (74.1, 74.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.5 ran Phases 72–73, so the next milestone starts at **Phase 74**.

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

**Todos closed by v0.9.5** (2026-09-16):

- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` → closed by **Phase 72**
  (DOC-18) and moved to `todos/completed/`. It recorded 4 `multiple toctrees` messages; 5 were
  measured on 2026-09-13, because `examples/advanced` now also appears, and the tip measured 0.

**Still open after v0.9.5:**

- `2026-07-22-add-sphinx-linkcheck-ci-job` — **half closed; it stays in `pending/`.** Phase 72
  landed the `tox -e linkcheck` environment (QUA-13) and listed it on all three surfaces (DOC-24),
  and the todo carries a status note recording that. The CI job the todo is actually about (QUA-08,
  superseding LNK-01) is deferred to Future, so the todo stays open for that half. Three notes for
  whoever picks it up:
  - Its "Solution" section proposed `linkcheck_ignore` for external domains up front. QUA-13 forbade
    speculative settings, so only a measured failure earns one; none has been measured (95/95
    `working`).
  - It named `ci.yml` / `docs.yml` as candidate hosts. Both trigger on push and PR, which QUA-08's
    shape excludes.
  - The obstacle that deferred QUA-08 — a new workflow file cannot be scheduled or dispatched from
    an unmerged milestone branch — still applies, but the environment the job would call is now on
    `main`, so a side PR to `main` is the route.

**Still open and deferred** (3 of the 4 remaining pending todos, besides the half-closed linkcheck
todo above):

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — still excluded from every published surface by owner override D-07.

- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line` (TRN-01, `severity: major`) —
  `doctest_block` has no translator handler, so `>>>` examples lose every line break. Captured
  2026-09-13 during the Issue #91 re-measurement; acknowledged at the v0.9.4 close. A behaviour
  change under `typsphinx/`, which v0.9.5 excluded by construction.

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — `translator.py`'s two relative-path DEBUG logs carry the same
  hardcoded-`'...'` delimiter shape Phase 60 closed in three other modules; the one-line fix is
  `quote_path()`, which now exists. Also a `typsphinx/` edit, so v0.9.5 excluded it too.

**Dormant seeds:**
- **`SEED-001-readme-quickstart-typst-documents-pdf`** — substantially discharged by v0.7.1's
  CONF-08 + DOC-11 and v0.8.0's DOC-14.
- **`SEED-003-tox-dependency-groups-per-env`** (Future QUA-07) — splitting the `dev` extra into PEP
  735 `[dependency-groups]`. A phase touching `pyproject.toml` or `tox.ini` must not absorb it
  opportunistically; Phase 72 edited `tox.ini` and did not.
- **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`** — `typst-py` upstream maintenance
  is slowing, and typsphinx may eventually need to carry an equivalent compile path. It is still the
  single largest structural risk on the horizon, and it has never been scoped into any milestone
  across nine consecutive scopings.
- **`SEED-005-gsd-workstreams-for-parallel-roadmap-tracks`** — adopt GSD workstreams so independent
  roadmap tracks run in parallel; dormant since v0.9.3.

**Known limitations still shipped with no published surface** after v0.9.2, carried unchanged
through v0.9.3 and v0.9.4 and into v0.9.5, none of which changes product behaviour: WR-02's `confdir`
gap, the tripled "Custom template not found" warning, and NUM-01's `numref` per-master divergence.
The `### Known Limitations` decision stays open for the next *published* release; v0.9.5 published
nothing, so it did not force it.

**Standing risk carried from v0.9.3:** `flake.nix` is load-bearing while keeping **zero CI
coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only when the
maintainer next enters the shell, and the darwin branch of the per-system guard cannot be exercised
from a Linux machine at all. Accepted deliberately (owner decision 2026-09-02); documented on the
surface itself by v0.9.3's DOC-21. v0.9.5 added no workflow and did not touch `flake.nix`; QUA-08,
the one workflow it considered, was deferred to Future.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31), v0.9.3 (2026-09-13 — merged, not published), v0.9.4 (2026-09-13 — merged, not published), v0.9.5 (2026-09-16 — merged, not published). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. No milestone is active; the next one starts at Phase 74 via `/gsd-new-milestone`.*
