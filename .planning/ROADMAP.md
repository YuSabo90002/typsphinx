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

**No active milestone.** Start the next one with `/gsd-new-milestone`.

Phase numbering is **continuous across milestones** — v0.9.0 ran Phases 53–57, so the next
milestone starts at **Phase 58**.

## Phases

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

**Still open and deferred after the v0.9.0 close** (2026-08-22) — full dispositions in
`.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md`
§ "Deferrals carried forward", and one row each in STATE.md's Deferred Items ledger:

- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` — **kept open with a live 2026-08-22
  recurrence annotated**, which falsified this milestone's own 2026-08-16 "ruff works here"
  measurement. The main tree's stale binary masks it; only a freshly-provisioned venv reproduces it.
- `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages` — the `!r`-path-escaping shape at
  the sites Phase 57's one fence exception deliberately left alone, widened at the close to cover the
  fixed-`'...'`-delimiter defect the code review found. One delimiter-aware helper closes both.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch` — `severity: major`; its `--locked`
  census is what made v0.9.0's D-13 sequencing constraint concrete.
- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized` and
  `2026-08-16-track-image-escape-branch-basename-not-normalized` — two `builder.py` path predicates
  held behind Phase 57's prep-only fence.
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
  equivalent compile path. The largest structural risk on the horizon; never scoped into a milestone.

**Known limitations shipped in v0.9.0**, deferred by owner decision with no published surface:
WR-02 (`templates_path` resolved against `srcdir`, not `confdir`, so `-c`/confdir projects keep the
republication hole — shipped *silent*, making the CHANGELOG's validation sentence read
unconditional), the tripled "Custom template not found" warning, and the fixed-delimiter path
quoting above.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22). Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
