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

**No active milestone.** Run `/gsd-new-milestone` to scope the next one.

**v0.9.1 completed but was never released, and the next published version is 0.9.2.** Its three
Windows path defect families closed on the product side; the release was then cancelled for an
unrelated, pre-existing `blocker` — an inline image not first in its paragraph aborts the whole
Typst compile, so `-b typstpdf` writes no PDF at all. No `v0.9.1` tag exists, locally or on the
remote; `pyproject.toml` is still `0.9.0` and the milestone's CHANGELOG bullets wait under
`## [Unreleased]`. **v0.9.2's first requirement is already known**: the blocker, tracked as
`.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`.
REL-09 carries forward unmet with its literal wording — including its `v0.9.1` version string —
unchanged by owner decision D-08.

## Phases

**Phase Numbering:**

- Integer phases (62, 63, …): Planned milestone work
- Decimal phases (62.1, 62.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.1 ran Phases 58–61, so the next milestone starts at **Phase 62**.

<details>
<summary>✅ v0.9.1 Windows path correctness (Phases 58–61) — COMPLETED 2026-08-30, NOT PUBLISHED</summary>

- [x] Phase 58: `repr()`-Format Decoupling (test-side only) (3/3 plans) — completed 2026-08-28
- [x] Phase 59: Path-Shape Predicate and Image-URI Correctness (5/5 plans) — completed 2026-08-29
- [x] Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere (5/5 plans) — completed 2026-08-29
- [x] Phase 61: v0.9.1 Release Prep (prep-only) (4/4 plans) — completed 2026-08-30

10/11 v1 requirements complete. REL-09 (publish to PyPI) deliberately unmet — the release was
cancelled, not missed. Full phase detail, the 14 binding constraints, success criteria and
decisions: [milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md)

</details>

<details>
<summary>✅ v0.9.0 per-document templates (Phases 53–57, +54.1) — SHIPPED 2026-08-22</summary>

- [x] Phase 53: Template Registry Foundation (10/10 plans) — completed 2026-08-15
- [x] Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions (7/7 plans) — completed 2026-08-16
- [x] Phase 54.1: Bundle Directory Safety — `templates_path` Collision Refusal and Pre-Write Path Validation (INSERTED) (5/5 plans) — completed 2026-08-16
- [x] Phase 55: v0.8.0-Derived Defects (4/4 plans) — completed 2026-08-16
- [x] Phase 56: Per-Document Template Documentation (5/5 plans) — completed 2026-08-16
- [x] Phase 57: v0.9.0 Release Prep (prep-only) (11/11 plans) — completed 2026-08-22

Full phase detail, success criteria, and decisions: [milestones/v0.9.0-ROADMAP.md](milestones/v0.9.0-ROADMAP.md)

</details>

<details>
<summary>✅ v0.4.4 – v0.8.0 (Phases 1–52) — SHIPPED 2026-07-05 → 2026-08-15</summary>

Each milestone's phase detail lives in its own archive, linked from the **Milestones** list above.

</details>

## Progress

**No milestone is active.** Phases 1–61 shipped or completed across v0.4.4 → v0.9.1; their per-phase
plan counts, statuses and completion dates are preserved in each milestone's archived roadmap under
`milestones/`. This table is re-created for the active milestone by `/gsd-new-milestone`.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| — | — | — | No active milestone | — |

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.1's — the three structural
decisions baked into the 58–61 phase split, the `gsd/v0.9.1-milestone` decoy-branch correction, and
the deliberate decision to give the 3-OS matrix run no REQ-ID — live in
[milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md).

- **2026-08-30** — v0.9.1 closed and reorganized here. The milestone completed all four phases and
  **published nothing**: the close performed no tag, no PyPI upload, no GitHub Release and no pull
  request (D-02, D-12), the first time in this project's history. Phase detail, requirements and the
  milestone audit archived to `milestones/v0.9.1-*`.

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

**Todos and seeds promoted into v0.8.0** (2026-08-11) — the three-defect `typst_documents`-modelling
cluster the v0.7.1 close named first among next-milestone candidates, plus the two image defects that
shipped in v0.7.1 unfixed by owner decision D-27:

- `shared-document-silently-dropped-from-all-but-first-master` → Phase 49 (defect A: COMP-07, and the
  whole COMP-05..COMP-12 include-graph set that closes it)

- `a-master-that-is-also-a-toctree-child-is-unrepresentable` → Phase 47 (B-1: COMP-03)
- `duplicate-typst-documents-target-silently-drops-a-master` → Phase 47 (BLD-02) — re-measured live in
  Phase 46 and still reachable, because Phase 44's guard compares only against `env.found_docs` and
  the reserved `_template`, never against already-resolved targets

- `rehomed-converted-image-collides-with-srcdir-images-dir` → Phase 50 (IMG-01, major — a regression
  in failure mode: the same project used to abort loudly)

- `track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` → Phase 50 (IMG-02, minor)

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred, not in v0.8.0 scope:**

- `modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*, since
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands", and
  binding constraint #9 forbids it this milestone.

- `add-sphinx-linkcheck-ci-job` — tracked as Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the links each release adds.

- `ruff-generic-linux-elf-unrunnable-on-nixos` — a `flake.nix`-side toolchain repair in the same
  family as QUA-04 (Future requirement QUA-06); CI holds lint authority, so it blocks nothing.

- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by v0.7.1's
  CONF-08 + DOC-11) and `SEED-003-tox-dependency-groups-per-env` (Future requirement QUA-07).

**Todos and seeds promoted into v0.9.0** (2026-08-15) — the five v0.8.0-derived defects that shipped
unfixed by decision D-01 or with only a test-side fix, all closed on the product side by Phase 55:

- `label-collision-false-negative-in-compile-time-xref-guard` → Phase 55 (XREF-05)
- `include-edge-key-separators-unescaped-two-edges-can-collide` → Phase 55 (BLD-07)
- `unbounded-recursion-in-derive-master-edge-keys` → Phase 55 (BLD-08)
- `escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide` → Phase 55 (IMG-03)
- `track-image-isabs-not-drive-aware-on-py313-windows` → Phase 55 (BLD-09)

**Todos promoted into v0.9.1** (2026-08-27) — the three path-handling records Phase 57's prep-only
fence held back, each now carrying a REQ-ID and a phase:

- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized` → Phase 59 (**PATH-01**). Re-measured at
  roadmap time: **not reachable from either production call site**, because both pre-normalize. Kept
  in scope deliberately as hardening of the function's own contract — a future third call site would
  inherit the gap silently — with the standing instruction that its gate call `_escapes_outdir()`
  directly, since an integration test through either call site is tautologically green.

- `2026-08-16-track-image-escape-branch-basename-not-normalized` → Phase 59 (**IMG-04**), together
  with its two never-filed siblings scoped in alongside it: the unescaped `image("...")` emission
  (**IMG-05**) and the unbounded key length (**IMG-06**). IMG-04 and IMG-05 are coupled by Typst's
  value-level backslash refusal, so the real-compile gate (**IMG-07**) closes both at once.

- `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages` → Phase 60 (**MSG-02** through
  **MSG-05**), with its test-side prerequisite split out as **MSG-01** in Phase 58. This record
  carries **both** halves of the defect — the `!r` backslash-doubling at the sites 57-11 left alone,
  and 57-REVIEW WR-01's fixed-`'...'` delimiter that closes early on a path containing a single
  quote — and one delimiter-aware helper closes both.

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred after the v0.9.0 close** (2026-08-22), and **not** in v0.9.1 scope — full
dispositions in
`.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md`
§ "Deferrals carried forward", and one row each in STATE.md's Deferred Items ledger:

- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` — **kept open with a live 2026-08-22
  recurrence annotated**, which falsified v0.9.0's own 2026-08-16 "ruff works here" measurement. The
  main tree's stale binary masks it; only a freshly-provisioned venv reproduces it. Tracked as Future
  requirement QUA-06. CI holds lint authority, so it blocks nothing — including this milestone's
  worktree-isolated executors.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` — `severity: major`; its `--locked`
  census is what made v0.9.0's D-13 sequencing constraint concrete. Tracked as a Future CI requirement.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` — an HTML sidebar defect in
  this project's own docs.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` — still
  excluded from every published surface by owner override D-07.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end` — REL-04's own record, whose acceptance
  criteria were met at the v0.7.1 publish and again at v0.8.0 and v0.9.0. Raised for the third close
  with the settling measurement attached; the disposition is the owner's.
- `2026-07-22-add-sphinx-linkcheck-ci-job` (Future LNK-01) and
  `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` (forbidden by `CLAUDE.md` until the
  todo itself lands) — both deferred again.
- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf`,
  `SEED-003-tox-dependency-groups-per-env` (Future QUA-07), and **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`**
  — `typst-py` upstream maintenance is slowing and typsphinx may eventually need to carry an
  equivalent compile path. The largest structural risk on the horizon; never scoped into a milestone,
  and explicitly not scoped into this bug-fix round either.

**Known limitations shipped in v0.9.0**, deferred by owner decision with no published surface:
WR-02 (`templates_path` resolved against `srcdir`, not `confdir`, so `-c`/confdir projects keep the
republication hole — shipped *silent*, making the CHANGELOG's validation sentence read
unconditional) and the tripled "Custom template not found" warning; both are carried forward as v2
requirements and are **not** in v0.9.1 scope. The third — the fixed-`'...'`-delimiter path quoting —
**is** closed this milestone, by MSG-02's delimiter-aware helper.

**Closed by v0.9.1** (2026-08-30) — the three records promoted above all executed:
`2026-08-16-escapes-outdir-isabs-not-backslash-normalized` (PATH-01),
`2026-08-16-track-image-escape-branch-basename-not-normalized` (IMG-04), and
`2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages` — **both** halves, by MSG-01
through MSG-05.

**Filed during v0.9.1 and open** (2026-08-30), both in `translator.py`, neither in that milestone's
requirement scope:

- `2026-08-29-inline-image-in-paragraph-emits-unseparated-expression` — `severity: blocker`, and
  **the single strongest candidate for the next milestone**. An image node that is not the first
  thing in its paragraph is emitted adjacent to the preceding code-mode expression, so Typst refuses
  the file with `expected semicolon or line break` and `-b typstpdf` raises `ExtensionError`
  rather than degrading — **no PDF is produced for any master document in the project**. Owner-
  reported 2026-08-29 and root-caused the same day; measured **pre-existing, not a v0.9.1
  regression** (D-06), so it is live in the published 0.9.0. It is the reason v0.9.1 was never
  released (D-02), was deliberately not fixed in that milestone (D-07), and has **no public-surface
  disclosure** (D-05).
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` —
  `severity: minor`. `translator.py`'s two relative-path DEBUG logs carry the same
  hardcoded-`'...'`-delimiter shape Phase 60 closed in three other modules; found by that phase's own
  repo-wide discovery grep and filed rather than fixed, being a fourth module outside
  MSG-02..MSG-05's scope. The one-line fix is `quote_path()`, which now exists.

**Still open and deferred after the v0.9.1 close** (2026-08-30), one row each in STATE.md's Deferred
Items ledger: `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` (Future QUA-06),
`2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` (`severity: major`),
`2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar`,
`2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (still
excluded from every published surface by D-07),
`2026-08-04-release-create-job-missing-uv-verify-end-to-end` (untestable at this close, since
nothing was published), `2026-07-22-add-sphinx-linkcheck-ci-job` (Future LNK-01),
`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` (forbidden by `CLAUDE.md` until the
todo itself lands), and the three dormant seeds — SEED-001, SEED-003 (Future QUA-07) and
**SEED-004** (`typst-py` upstream maintenance slowing; the largest structural risk on the horizon,
never scoped into any milestone across three consecutive closes).

**Known limitations still shipped with no published surface** after v0.9.1: WR-02's `confdir` gap
and the tripled "Custom template not found" warning, both carried unchanged from v0.9.0, joined now
by the inline-image blocker. That is the **fourth consecutive** cycle at which a
`### Known Limitations` section was declined.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`.*
