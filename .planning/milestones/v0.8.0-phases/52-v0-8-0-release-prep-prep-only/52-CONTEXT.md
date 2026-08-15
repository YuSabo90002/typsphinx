# Phase 52: v0.8.0 Release Prep (prep-only) - Context

**Gathered:** 2026-08-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Prep-only release work for v0.8.0: bump the version in lockstep, curate the `## [0.8.0]` CHANGELOG
entry, prove the post-bump tree green live (including the milestone's own goal claim on generated
evidence), assert the standing invariants over the milestone diff, and hand off a standalone
publish checklist — with **zero irreversible action taken**. Requirement: **REL-07**, whose
prep half only. REL-07 itself does **not** close here; it closes at `/gsd-complete-milestone`.

**In scope:**

- `pyproject.toml:7` — `version = "0.7.1"` → `"0.8.0"` (measured this session: still the sole
  version literal), with `uv.lock` and `README.md:347` (`**Status**: Stable (v0.7.1) - Production
  ready`) moved in lockstep and the editable-install metadata regenerated so
  `typsphinx.__version__` reports `0.8.0`. The three version-sync guard tests stay green.
- A curated `## [0.8.0]` entry in `CHANGELOG.md` per D-02, D-04, D-05, D-06, **plus the tail
  link-block rollover** — add the `[0.8.0]` release-tag line and advance `[Unreleased]` to
  `v0.8.0...HEAD`. The `## [Unreleased]` block holds **no** accumulated v0.8.0 material (measured:
  only a "Planned for Future Releases" list), so the entry is written from the milestone's own
  requirements rather than compressed from an existing draft.
- Confirming `docs/source/changelog.rst` still renders the repo-root file live through DOC-12's
  `.. include::` mechanism, and the `RELEASE_VERSIONS` tuple question in
  `tests/test_changelog_page_gate.py:49-63` (see Claude's Discretion).
- SC#3 live-run evidence on the post-bump tree, in two halves: the toolchain half (pytest,
  `black`/`ruff`/`mypy`, the full-corpus `-b typstpdf` GATE-02 gate, `docs-html`, `docs-pdf`) and
  the **goal-claim half** (a real multi-master `-b typstpdf` round trip read back through `pypdf`).
  See D-07 and D-08.
- SC#4's invariant proof over the SHA-anchored full milestone diff (D-09).
- SC#5 handoff: a standalone `52-HANDOFF.md` following the `46-HANDOFF.md` precedent, and the
  explicit statement that REL-07 remains open until the publish.
- Close-out disposition of the 9 pending todos per D-01 and D-03.

**Out of scope:**

- **Any publish or otherwise irreversible action** — `git tag v0.8.0`, triggering `release.yml`,
  PyPI, the GitHub Release, opening or merging the PR, and the second tag on
  `typsphinx-doc-translations`. `git tag -l v0.8.0` and `git ls-remote --tags origin v0.8.0` must
  both be empty at phase close (measured this session: both already empty). The prep/publish fence
  is absolute — Phase 33 / 35 / 41 / 46 precedent.
- **Any `typsphinx/` code change**, including fixes for the four minor defects this milestone's own
  reviews filed (D-01). The prep-only fence is held even though all four are real.
- **Merging `origin/main`** — measured this session: `origin/main` (`a97fe73`) is already an
  ancestor of HEAD, and the `.planning/`-excluded code diff from the `v0.7.1` tag and from
  `origin/main` are byte-identical in shape (341 files, +15,141 / −2,472 either way). There is
  nothing to take in. A re-check at the head of the phase is cheap and should still be made.
- Revisiting the version number — `0.8.0` is fixed by the milestone name, `ROADMAP.md` SC#1, and
  `PROJECT.md`'s milestone header.
- Editing historical CHANGELOG entries.
- **`:numref:` in any form** — 51-CONTEXT D-07 extends to this phase's CHANGELOG by explicit owner
  instruction (2026-08-14). It appears in neither `docs/source/**`, `README.md`, nor `CHANGELOG.md`
  for this release.

</domain>

<decisions>
## Implementation Decisions

Every measured value below was taken **this session (2026-08-15)** against the live tree, not from
recall.

### Disclosure of the defects this milestone filed against itself

- **D-01: The four minor defects this milestone's own reviews filed ship in v0.8.0 unfixed and disclosed internally only.** The records stay in `todos/pending/` and are named in
  `52-HANDOFF.md`; **no `### Known Limitations` section is added to the CHANGELOG and no GitHub
  issue is filed.** This is the v0.7.1 D-27 shape applied a second time, and it is *a fortiori*
  consistent: D-27 kept silent about two **major** defects whose reachability was the most common
  Sphinx asset layout (`images/` plus an image-conversion extension), whereas all four here are
  `severity: minor` with the reachability conditions measured below (`<specifics>` item 6). The
  counter-case that was put and declined: all four are **new** failure classes created by features
  this milestone shipped (Phase 48's compile-time xref guard, Phase 49's include graph, Phase 50's
  image relocation), which is not true of the v0.7.1 pair. Owner decision with that distinction on
  the table. — **Reversibility:** reversible — adding a `### Known Limitations` section or filing
  issues later costs nothing structural.

- **D-02: The two behaviours Phase 49 measured and Phase 51 documented are written into the descriptive bullets, not into a limitations section.** These are the two items ROADMAP SC#2's
  "any limitation Phase 49 measured and documented appears here too" resolves to (measured: Phase 51
  documented exactly two, `:numref:` excluded by D-07):
  (a) a content file compiled standalone yields only its own body, its state-guarded children
  absent, with no error or warning (`docs/source/user_guide/output_layout.rst:51`);
  (b) a document reachable from several masters renders once in each master's PDF, at that master's
  own traversal position, with its heading level varying per master.
  Both go inside the output-shape / composition bullets. Rejected: a `### Known Limitations`
  section holding these two — 51-CONTEXT D-08 deliberately wrote (a) as prose rather than a
  `.. note::` precisely so it reads as intended behaviour, and a limitations heading in the
  CHANGELOG would give it the warning tone that decision rejected; and a docs-link-only treatment,
  which would not reach a reader of the GitHub Release body. — **Reversibility:** reversible.

- **D-03 — The four defects plus the `:numref:` record are carried forward as todos, not promoted to the ROADMAP backlog.** They stay in `.planning/todos/pending/` and are enumerated with
  reasons in `52-HANDOFF.md` and this file's `<deferred>` — the 46-CONTEXT D-16 shape. Measured
  context: the ROADMAP `## Backlog` has been empty since 2026-08-04 and would next number `999.3`,
  but v0.8.0's own scope was assembled from the todo ledger directly at `/gsd-new-milestone`, so
  the ledger is the path that has actually worked. Rejected: promoting them to `999.3`+ (creates a
  second ledger for the same records) and writing them into PROJECT.md's "Next" (PROJECT.md is
  updated by phase-complete / milestone-close, not by a prep phase). — **Reversibility:**
  reversible.

### The `## [0.8.0]` CHANGELOG entry

- **D-04: Breaking changes are marked two ways — a lead-paragraph declaration plus a `**Breaking:**` prefix on each affected bullet.** This is v0.7.1's D-02 triple marking with its
  third channel dropped, because that channel has no candidate here: measured this session, the
  milestone diff of `typsphinx/__init__.py` contains **zero** `add_config_value` additions or
  removals, so nothing public was removed and `### Removed` would be an empty section. The three
  bullets carrying the prefix are the wrapper/content split, the target-as-path reversal, and the
  collision hard error — the third of which **stops a build that used to succeed**, for the most
  common configuration shape (`("index", "index.typ", …)`). Rejected: a new `### Breaking Changes`
  section (adds a second never-before-used heading to a release that already carries a large
  structural change), and lead-declaration-only in the Phase 41 D-03 shape (that was justified
  there by the measured fact that nothing broke — a premise that does not hold here). v0.7.1's
  vocabulary is reused verbatim so the two releases read consistently. — **Reversibility:**
  reversible.

- **D-05: The lead paragraph's axis is the milestone goal itself — a `typst_documents` configuration declaring more than one master now produces a complete PDF for each of them.**
  The breaking-change declaration lives in the **second half of the same paragraph**, per D-04.
  Weighed explicitly and rejected: leading with the output-shape change (it lands on every user,
  including single-master ones, but leading with it buries the fact that this release is the one
  that makes multi-master work at all), and leading with the repair narrative "content that was
  silently dropped no longer is" (accurate for defect A / B-1 / B-2, but told as a defect list
  rather than as a capability). The owner chose the capability framing with the "it hits every user
  vs. it hits only multi-master users" asymmetry on the table. — **Reversibility:** reversible.

- **D-06: `### Verified` carries the same three items as 0.7.0 and 0.7.1, unchanged.** Measured:
  those two releases carry an identical three-item list (no new **runtime** dependencies across the
  full milestone diff; the four bundled `@preview` version strings unchanged across all four sync
  surfaces; the full-corpus Sphinx `doc/` `-b typstpdf` re-run remains fatal-free). SC#4's fourth
  mechanical assertion (**no new `typst_*` config value**) and SC#3's multi-master round-trip
  evidence are recorded in the phase's own evidence artifacts, **not** promoted into `### Verified`.
  Rejected: a fourth item for the config invariant, and a fifth for the round trip — the section's
  standing character is "here is what did *not* change", and the round-trip result is a positive
  capability claim that D-05's lead paragraph already makes. — **Reversibility:** reversible.

- **D-07 [derived, carried from 46-CONTEXT D-05]: bullets are cut at user-visible-change granularity with requirement IDs in trailing parentheses.** Not re-asked — it is the settled
  house style since Phase 33 D-09. Applied to this milestone's 24 v1 requirements it falls out at
  roughly 8–9 bullets: two-layer output; target-as-path reversal; collision hard error; a shared
  child now reaching every master's PDF (defect A); a master that is also a toctree child (B-1); an
  included master no longer re-expanding its template mid-body (B-2); compile-time cross-reference
  degradation; the two image defects; the new output-layout documentation. The planner owns the
  final cut and the section assignment.

### SC#3 — where "green" comes from (derived; not selected for discussion, defaults recorded)

- **D-08 [derived, following 46-CONTEXT D-11]: the dispatched CI run on the post-bump commit is the authority for pytest / lint / type; the full-corpus gate and both docs builds are run locally.**
  Two measurements shape this. (a) `.github/workflows/ci.yml`'s push trigger is
  `branches: [main, develop]` only, so this milestone branch's CI runs **exclusively** via
  `workflow_dispatch` — the last full CI run on it is `31492380799` (2026-08-11, dispatched);
  every run since is Link Check. (b) The branch is **155 commits ahead** of
  `origin/gsd/v0.8.0-multi-master-composition`. The phase therefore pushes the post-bump commit
  and dispatches CI on it, which is what makes the Windows and macOS lanes visible — the lanes that
  caught a real cp1252 defect at the v0.7.0 close and a real path-separator defect at the v0.7.1
  close. Pushing a branch and dispatching a workflow are not irreversible actions; opening a PR
  (which would also trigger CI, via `pull_request: [main]`) **is** in the publish half and stays
  out. Locally, `ruff` still cannot execute on this machine
  (`todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`), which is exactly why
  lint authority sits with CI. — **Reversibility:** reversible.

- **D-09 [derived]: SC#4's invariant sweep is anchored at the `v0.7.1` tag (`48bf135`).** Measured
  this session: `v0.7.1` is an ancestor of HEAD; `origin/main` (`a97fe73`) is also an ancestor and
  is the merge-base; and excluding `.planning/`, `v0.7.1..HEAD` and `a97fe73..HEAD` produce the
  **identical** shortstat (341 files changed, +15,141 / −2,472), because the four commits between
  the tag and `origin/main` are planning/docs only. ROADMAP SC#4 says "merge-base to HEAD" and
  46-CONTEXT D-21 says "the release tag"; here the two coincide, so no choice is being made — the
  sweep is anchored at the tag, which is also "what a v0.7.1 user receives". The three assertions
  are mechanical: zero new runtime dependencies (`pyproject.toml` is **unchanged** across the
  milestone diff — measured, which makes this a one-command proof), the `@preview` count still four
  with no new lockstep site across `writer.py` / `template_engine.py` / `templates/base.typ` /
  `examples/**/*.typ`, and no new `typst_*` config value. The positive control SC#4 asks for must
  be a real one — an assertion that *would* fail if the sweep were vacuous, not a restatement.

- **D-10 [derived, following 51-CONTEXT D-10]: the goal-claim evidence is a new permanent gate test under `tests/`, reusing the existing multi-master fixture family.** Phase 51 discharged its own
  verification SC with one permanent gate test rather than a one-off transcript, and that is the
  shape to repeat: a phase artifact recording a transcript proves the claim once, whereas a gate
  test keeps proving it. `tests/fixtures/state_guard_three_master_gate/` already satisfies SC#3's
  bar (three masters, a shared child), and `pypdf` text extraction is an established pattern across
  20+ gate modules. What the new gate must add beyond the existing composition gate is the
  **PDF-level** assertion SC#3 names — each master's PDF opened via `pypdf`, with specific text and
  page assertions proving that master's full content is present — rather than the `typst.query`
  structural assertions `tests/test_state_guard_composition_gate.py` already makes. The planner
  owns whether the fixture is reused as-is or extended.

### Claude's Discretion

- The exact wording of the `## [0.8.0]` entry, the lead paragraph's phrasing, which 8–9 bullets
  D-07 resolves to, and how requirement IDs are attached.
- Which requirements land in `### Added` versus `### Changed` versus `### Fixed`. No assignment is
  fixed by decision — `### Removed` has no candidate (D-04).
- Plan decomposition and ordering, and the `uv.lock` regeneration procedure (acceptance:
  `uv sync --extra dev --locked` green).
- The mechanical method for D-09's invariant sweep, and what the positive control is.
- Whether `"0.8.0"` is added to `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py:49-63` in
  this phase — the gate asserts each listed release appears in the built page, so the addition is
  mechanical but must not land before the CHANGELOG entry exists. The 46 precedent left this to the
  planner for the same reason.
- The name and shape of D-10's new gate module and whether it extends
  `state_guard_three_master_gate` or adds a sibling fixture.
- The format and heading structure of `52-HANDOFF.md`, and where live-run evidence is recorded —
  subject to the reserved-name constraint: **do not name any evidence file
  `52-VERIFICATION.md`** (46-CONTEXT D-15; the verifier owns that name and will clobber it).
- Whether the CI dispatch is one run or two (46-CONTEXT D-23 split it into a check run and an
  authority run; here there is no separate repair to check first, so one run is the likely shape).

### Folded Todos

None. `todo.match-phase 52` returned 9 candidates, all keyword noise against a release-prep phase;
see `<deferred>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's requirements and success criteria

- `.planning/ROADMAP.md` § "Phase 52: v0.8.0 Release Prep (prep-only)" — the five success criteria
  this phase is judged against, including SC#2's explicit `:numref:` exclusion.
- `.planning/REQUIREMENTS.md` § REL-07 — the requirement verbatim, and the traceability row that
  stays `Pending` through this phase.
- `.planning/STATE.md` § "Active Milestone (v0.8.0)" — the milestone invariants, the phase table,
  and the record that milestone invariant #5 was discharged in Phase 47.
- `.planning/PROJECT.md` § "Current Milestone: v0.8.0 multi-master composition" — the milestone
  goal sentence D-05 makes the lead paragraph's axis, and the "User-visible output-shape change"
  bullet that instructs the CHANGELOG to distinguish this change from v0.7.1's own rename.

### The release-prep precedent to follow

- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-CONTEXT.md` — the
  prep/publish fence, the version-literal census, the CHANGELOG-entry decision shape (D-05..D-10),
  D-11's CI-as-authority reasoning (D-08 here), D-15's reserved-filename constraint, D-16's todo
  disposition shape, and D-27's silent-deferral precedent (D-01 here).
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-HANDOFF.md` — the handoff
  document shape SC#5 asks for, and the seven-item publish checklist to adapt.
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-RELEASE-EVIDENCE.md`,
  `46-GREEN-TREE-EVIDENCE.md`, `46-CI-EVIDENCE.md`, `46-SC4-INVARIANTS.md`, `46-BUMP-EVIDENCE.md` —
  the evidence-artifact family and its naming, and the reason none of them is called
  `46-VERIFICATION.md`.

### CHANGELOG source material handed forward by earlier phases

- `.planning/phases/51-two-layer-output-documentation/51-CONTEXT.md` — **D-07 is binding on this
  phase**: `:numref:` appears nowhere in the v0.8.0 CHANGELOG. D-08 and D-09 are the two documented
  behaviours D-02 folds into the descriptive bullets.
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md` — the
  measured composition results. Its `:numref:` section's "fix-or-document decision" paragraph is
  **superseded** by 51-CONTEXT D-07 and must not be read as a live instruction.
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-CONTEXT.md`
  — the target-as-path reversal of v0.7.1 Phase 44's D-05/D-06/D-07 and the security half that was
  retained, for the reversal bullet.
- `docs/source/changelog.rst:7-88` — the "Migrating from 0.7.x to 0.8.0" section **Phase 51 already
  wrote**, with before/after fragments for all three breaking changes. The CHANGELOG bullets must
  agree with it; the migration section itself needs no new hand edit.
- `docs/source/user_guide/output_layout.rst` — the new two-layer page; `:51` carries the standalone
  content-file prose D-02 folds in.
- `CHANGELOG.md` — the `## [0.7.1]` entry as the structural model (lead paragraph → `### Added` /
  `### Changed` / `### Fixed` / `### Removed` → `### Verified`), its `**Breaking:**` vocabulary, and
  the tail link block that must roll over.

### Version-literal and gate surfaces

- `pyproject.toml:7` — the sole version literal (measured 2026-08-15).
- `README.md:347` — `**Status**: Stable (v0.7.1) - Production ready`.
- `tests/test_readme_version_sync.py` — asserts the two agree, so both must move together.
- `tests/test_preview_version_sync.py` — the `@preview` lockstep guard over the four sync surfaces.
- `tests/test_changelog_page_gate.py:49-63` — the `RELEASE_VERSIONS` tuple, currently ending at
  `"0.7.1"`.
- `tests/test_corpus_gate.py` — the GATE-02 full-corpus gate (`@pytest.mark.slow`; skips rather
  than fails when the corpus is unavailable, so a skip is **not** evidence).
- `tests/test_state_guard_composition_gate.py` and `tests/fixtures/state_guard_three_master_gate/`
  — the existing multi-master assets D-10 builds on.
- `tests/test_output_layout_docs_gate.py` — Phase 51's D-10 gate, the precedent for "one permanent
  gate test rather than a transcript".

### Release machinery (exercised, not triggered)

- `.github/workflows/ci.yml:3-8` — the push/PR/dispatch triggers D-08 rests on.
- `.github/workflows/release.yml` — the `validate` job checks the `## [0.8.0]` heading exists and is
  non-empty before a tag is ever pushed (Phase 41 D-09); `create-release` is the job SC#5's
  checklist must explicitly say to observe.
- `scripts/extract_changelog_section.py` — run it against the new `## [0.8.0]` section as a
  **precondition**, never as acceptance.
- `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — REL-04's
  own record; already closed at the v0.7.1 publish, retained for the checklist's shape.

### Standing project constraints

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus `uv run` for every
  executor. Worktree isolation is the standing execution mode.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — the surfaces D-09's sweep counts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tests/fixtures/state_guard_three_master_gate/` — three masters with a shared child; already
  satisfies SC#3's "≥2 masters and ≥1 shared child" bar, so D-10's gate does not need a new project
  built from scratch.
- `pypdf` text extraction — an established pattern in 20+ gate modules
  (`test_document_metadata_render_gate.py`, `test_typst_lang_gate.py`,
  `test_xref_whole_document_guard_render_gate.py`, …). No new dependency and no new technique.
- `scripts/extract_changelog_section.py` — committed and pytest-covered since Phase 41; this phase
  only exercises it.
- `tests/test_readme_version_sync.py` / `tests/test_preview_version_sync.py` — the established
  "a release-surface fact is pinned by pytest" pattern; both must stay green across the bump.
- `docs/source/changelog.rst`'s "Migrating from 0.7.x to 0.8.0" section — written in Phase 51,
  so the CHANGELOG bullets have a finished, measured description to agree with rather than derive.

### Established Patterns

- **Version literals:** `pyproject.toml:7` is the sole literal; `typsphinx.__version__` derives from
  `importlib.metadata` (so the editable install must be regenerated); `README.md:347` carries the
  human-readable status line; `uv.lock` moves in lockstep.
- **CHANGELOG entry shape:** lead paragraph → `### Added` / `### Changed` / `### Fixed` →
  `### Verified` → tail link block. `[0.7.1]`, `[0.7.0]`, `[0.6.5]`, `[0.6.4]`, `[0.6.3]` all
  follow it; `[0.7.1]` added `### Removed`, which has no candidate this time (D-04).
- **Evidence culture:** commands and their output transcribed verbatim; `human_needed` recorded
  honestly; abstain rather than assert without direct evidence.
- **Test-invocation convention:** newer gate modules invoke Sphinx as `sys.executable -m sphinx`.

### Integration Points

- The post-bump commit ↔ the dispatched CI run — D-08's evidence path. Requires pushing 155+
  commits to `origin/gsd/v0.8.0-multi-master-composition`, then dispatching `ci.yml` on that
  branch, because the push trigger does not cover it.
- `CHANGELOG.md` ↔ `docs/source/changelog.rst` ↔ `tests/test_changelog_page_gate.py` — one edit,
  three surfaces. The `.. include::` propagates the release history automatically (DOC-12), so only
  the gate's version tuple is hand-maintained; the migration section is already written.
- `CHANGELOG.md` ↔ `release.yml` — the `## [0.8.0]` heading must exist and be non-empty before any
  tag is pushed, because `validate` checks it.
- `.planning/todos/pending/` ↔ `52-HANDOFF.md` — D-01 and D-03 make the todo ledger the only record
  of the four deferred defects, which raises the handoff's importance: if the handoff omits one, it
  has no second surface.

</code_context>

<specifics>
## Specific Ideas

Everything below was measured this session (2026-08-15) against the live tree, not inferred.

1. **The version literal census is unchanged from v0.7.1's shape.** `pyproject.toml:7` →
   `version = "0.7.1"`; `README.md:347` → `**Status**: Stable (v0.7.1) - Production ready`. No
   other `0.7.1` literal in either file.

2. **`## [Unreleased]` holds nothing to compress.** Its entire body is a "Planned for Future
   Releases" list (BibTeX, glossary, index, pre-commit hooks, extra template integration). Unlike
   Phase 46 — which inherited a 16-line contributed entry from `origin/main` — the `## [0.8.0]`
   entry is authored from the milestone's requirements.

3. **The tail link block ends at `[0.7.1]`**, and `[Unreleased]` currently compares
   `v0.7.1...HEAD`. Both lines move in this phase.

4. **The diff anchors coincide.** `v0.7.1` → `48bf135`, an ancestor of HEAD. `origin/main` →
   `a97fe73`, also an ancestor, and it *is* `git merge-base origin/main HEAD`. Excluding
   `.planning/`, both `v0.7.1..HEAD` and `a97fe73..HEAD` give **341 files changed, +15,141 /
   −2,472** — the four commits between them are planning/docs only (`docs: record the v0.7.1 Read
   the Docs stable confirmation`, `chore: remove REQUIREMENTS.md …`, `chore: archive v0.7.1
   milestone files`, `docs: close REL-04 and REL-06`). 301 commits in the range.

5. **Two of SC#4's three invariants are already provable in one command each.**
   `git diff v0.7.1..HEAD -- pyproject.toml` is **empty** (so no runtime dependency moved, and no
   `typst_*` registration could have moved through packaging); `git diff v0.7.1..HEAD --
   typsphinx/__init__.py | grep add_config_value` is **empty** (no config value added or removed);
   `templates/base.typ` still carries exactly **4** `@preview` lines.

6. **The four deferred defects and their measured reachability** (all `severity: minor`, all
   `resolves_phase: null`):
   - `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard` — needs one docname to
     sanitize to the same label string another docname produces via `/` → `_u2f_`, e.g. docnames
     `a/b` and `a_u2f_b` coexisting. A reference to the absent one renders as a working link to the
     decoy instead of degrading to plain text.
   - `2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide` — needs a docname
     containing a literal `#` or `>`; `make_include_edge_key` does not escape its own separators.
   - `2026-08-14-unbounded-recursion-in-derive-master-edge-keys` — needs an include chain deeper
     than Python's 1000-frame limit; Sphinx's own 154-document `doc/` corpus does not reach it. The
     failure is a raw `RecursionError`, not a named `ExtensionError`.
   - `2026-08-14-escape-branch-relocation-key-uses-basename-only-…` — needs two escaping absolute
     image URIs in different directories sharing a basename; the escape branch keys on `basename`
     while the collision branch keys on the full `rel_uri`, so they collide onto one key.

7. **CI reachability on this branch.** `ci.yml`'s `on.push.branches` is `[main, develop]` and
   `on.pull_request.branches` is `[main, develop]`; `workflow_dispatch` is the only trigger this
   branch can use without opening a PR. `gh run list --branch gsd/v0.8.0-multi-master-composition`
   shows the last full CI as `31492380799` (2026-08-11, `workflow_dispatch`, 5m30s, success); every
   later run is `Link Check`. The branch is **155 commits ahead** of its origin counterpart
   (`1959088`, "test(48): persist human verification items as UAT").

8. **SC#5's precondition already holds.** `git tag -l v0.8.0` and
   `git ls-remote --tags origin v0.8.0` are both empty.

9. **The full-corpus gate can pass vacuously.** `tests/test_corpus_gate.py` is
   `@pytest.mark.slow` and `pytest.skip`s (never fails) when the corpus is unavailable — no
   network, clone failure, unresolvable tag. SC#3's evidence must therefore record that it **ran**,
   not merely that it did not fail.

10. **Owner's framing across this discussion.** Consistency with the v0.7.1 close was chosen at
    every fork: silent internal deferral again (D-01), the same `**Breaking:**` vocabulary (D-04),
    the same three `### Verified` items (D-06), and the same todo-ledger handoff path (D-03). The
    one place a *new* framing was chosen is D-05's lead axis, where the capability claim was
    preferred over the change-notice claim.

</specifics>

<deferred>
## Deferred Ideas

- **Fixing any of the four minor defects in this phase** — declined by D-01 and by the prep-only
  fence. All four are genuinely actionable (each names its file and line, and three name where the
  RED belongs), and all four are new failure classes this milestone created. Recorded here so a
  later reader does not mistake the silence for an oversight.

- **A `### Known Limitations` CHANGELOG section and public GitHub issues for the four defects** —
  argued in full and declined by D-01. The precedent (`CHANGELOG.md:817`) and the near-empty public
  issue tracker (only #91 open) were both on the table.

- **Promoting the deferred defects to ROADMAP backlog items `999.3`+** — declined by D-03 in favour
  of the todo ledger, which is the path `/gsd-new-milestone` actually reads.

- **The `:numref:` divergence** — excluded from every published surface by 51-CONTEXT D-07 (owner
  override, extended to this phase's CHANGELOG on 2026-08-14). Its record's `resolves_phase` is
  `null`; a later milestone picks it up as a bug, not as a published limitation.

### Reviewed Todos (not folded)

`todo.match-phase 52` returned 9 candidates — the entire pending ledger — all keyword noise against
a release-prep phase. None is folded; each is deferred with its reason:

- `2026-07-22-add-sphinx-linkcheck-ci-job` — Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the links this release adds.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` — forbidden by `CLAUDE.md` and by
  the milestone's own binding constraint until the todo itself lands. Doubly deliberate.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end` — REL-04's record; **closed at the
  v0.7.1 publish** (`create-release` completed success on run `31462027486`). Worth confirming it
  belongs in `todos/completed/` rather than `pending/` — flagged for the planner, not decided here.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` — a `flake.nix`-side toolchain repair
  (Future requirement QUA-06). Does not block SC#3, which takes lint from CI (D-08).
- `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard` — D-01.
- `2026-08-14-escape-branch-relocation-key-uses-basename-only-…` — D-01.
- `2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide` — D-01.
- `2026-08-14-unbounded-recursion-in-derive-master-edge-keys` — D-01.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` — excluded
  from publication by 51-CONTEXT D-07; `resolves_phase` already moved to `null`.

</deferred>

---

*Phase: 52-v0-8-0-release-prep-prep-only*
*Context gathered: 2026-08-15*
