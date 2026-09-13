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

**No milestone is active.** v0.9.3 completed 2026-09-13 and was merged to `main` via PR #143 with
no tag, no PyPI upload and no GitHub Release; `pyproject.toml` stays at `0.9.2` and its CHANGELOG
bullets wait under `## [Unreleased]`. The version number `0.9.3` is unclaimed, not decided — the
next milestone's scoping settles whether the next published release uses it. Start the next
milestone with `/gsd-new-milestone`; phase numbering continues at **Phase 70**.

## Phases

**Phase Numbering:**

- Integer phases (70, 71, …): Planned milestone work
- Decimal phases (70.1, 70.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.3 ran Phases 64–69, so the next milestone starts at **Phase 70**.

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

No active milestone. Phases 1–69 shipped or completed across v0.4.4 → v0.9.3; their per-phase plan
counts, statuses and completion dates are preserved in each milestone's archived roadmap under
`milestones/`.

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.3's — the two-track structure
adopted from `research/SUMMARY.md`, the inverted `gsd/v0.9.3-milestone` decoy-branch correction, the
native-`uv`-ecosystem amendment that replaced a custom lockfile workflow, and the AMENDED blocks on
constraints 2 and 12 — live in [milestones/v0.9.3-ROADMAP.md](milestones/v0.9.3-ROADMAP.md).

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

**Todos closed by v0.9.3** (2026-09-13): `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos`
(Phase 64, NIX-01..NIX-08) and `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` (Phases
66–67, DEP-01..DEP-05), both moved to `todos/completed/` when their phases executed.

**Still open and deferred** (the 5 pending todos, carried out of v0.9.3 unchanged):

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — still excluded from every published surface by owner override D-07.

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — `translator.py:5047,5152` carry the same hardcoded-`'...'` delimiter shape
  Phase 60 closed in three other modules; the one-line fix is `quote_path()`, which now exists.
  **Was out of reach in v0.9.3**: it is a change under `typsphinx/`, which constraint 13
  forbids.

- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` — an HTML sidebar defect in
  this project's own docs `index.rst`.

- `2026-07-22-add-sphinx-linkcheck-ci-job` (Future LNK-01) — deferred again; a CI job, which
  constraint 3 puts out of scope by construction. Seventh consecutive close at which it is raised.

- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*:
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands", and it
  is a change under `typsphinx/`.

**Dormant seeds:** `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by
v0.7.1's CONF-08 + DOC-11 and v0.8.0's DOC-14), **`SEED-003-tox-dependency-groups-per-env`** (Future
QUA-07 — splitting the `dev` extra into PEP 735 `[dependency-groups]`; **adjacent to this milestone's
`tox.ini` work and explicitly kept dormant by PROJECT.md's scope statement**, so a phase touching
`tox.ini` must not absorb it opportunistically), and **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`**
— `typst-py` upstream maintenance is slowing and typsphinx may eventually need to carry an equivalent
compile path. Still the single largest structural risk on the horizon, and still never scoped into
any milestone across five consecutive closes. **`SEED-005-gsd-workstreams-for-parallel-roadmap-tracks`**
— adopt GSD workstreams so independent roadmap tracks run in parallel; planted during v0.9.3 and
acknowledged dormant at its close.

**Known limitations still shipped with no published surface** after v0.9.2, carried unchanged into
this milestone because it touches no product code: WR-02's `confdir` gap, the tripled "Custom
template not found" warning, and NUM-01's `numref` per-master divergence. That is the **fifth
consecutive** cycle at which a `### Known Limitations` section was declined; the decision remains
open for the next release cycle, and v0.9.3 does not force it, because v0.9.3 publishes nothing.

**Standing risk arising from v0.9.3:** `flake.nix` becomes load-bearing while keeping
**zero CI coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only
when the maintainer next enters the shell, and the darwin branch of the per-system guard cannot be
exercised from a Linux machine at all. Accepted deliberately as the consequence of leaving CI
unchanged (owner decision 2026-09-02). Recorded in REQUIREMENTS.md § Future Requirements → "Arising
from this milestone", carried as constraint 8 above, and documented on the surface itself by DOC-21.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31), v0.9.3 (2026-09-13 — merged, not published). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. No active milestone.*
