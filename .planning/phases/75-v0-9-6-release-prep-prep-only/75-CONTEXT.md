# Phase 75: v0.9.6 Release Prep (prep-only) - Context

**Gathered:** 2026-09-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Package v0.9.6 for publication and hand it off, with **zero irreversible action inside the phase**.
The phase does six things:

- it moves the version to `0.9.6` in one commit touching `pyproject.toml`, `uv.lock`, `README.md`
  and `CHANGELOG.md` together;
- it curates one `## [0.9.6]` section holding the six carried `## [Unreleased]` bullets plus this
  milestone's own, under a fresh `## [Unreleased]`, and moves the tail link block in the same phase;
- it settles the `### Known Limitations` question on the record (REL-16, the one release
  requirement that closes here);
- it proves the bumped tree green by runs executed in this phase, not on Phase 74's word;
- it holds REL-15's checkbox at `[ ]` behind a recorded SHA-256 fence, re-verified once more after
  `phase.complete`-family tooling runs;
- it writes a standalone `75-HANDOFF.md` enumerating every step `/gsd-complete-milestone` must
  execute.

No tag (local or remote), no PyPI upload, no GitHub Release, no PR opened or merged, no
`update-pin.yml` dispatch. The merge, the tag push and the publish all execute at
`/gsd-complete-milestone` (ROADMAP constraint 1).

**ROADMAP § Phase 75 SC 1–5 and binding constraints 1–13 govern this phase and are not re-decided
here.** The discussion settled the CHANGELOG's shape and content, the two Phase 74 leftovers, the
push/CI-dispatch operating rule, and REL-16. Requirements: REL-15 (coverage only), REL-16 (closes
here).

**Measured state at discussion time (2026-09-20, HEAD `8325f7cd`).** Context only — constraint 4
requires each plan to re-measure fresh at its own base.

- **Version:** `pyproject.toml:7` = `version = "0.9.2"`; `README.md:348` = `**Status**: Stable
  (v0.9.2) - Production ready`.
- **CHANGELOG:** `## [Unreleased]` at `:8`, holding `### Added` (`:10`, one bullet — the
  `tox -e linkcheck` environment), `### Changed` (`:18`, four bullets — `tox-uv` return, Dependabot
  `uv` ecosystem, `flake.nix` dev shell, builtin generics) and `### Fixed` (`:55`, one bullet — the
  HTML sidebar). **Six bullets**, matching the requirement's count.
  `### Planned for Future Releases` sits at `:62`, **inside** the `## [Unreleased]` section. The
  next `## [` heading is `## [0.9.2] - 2026-08-30` at `:69`. The file is 1349 lines; the tail block
  ends with `[Unreleased]: …/compare/v0.9.2...HEAD`.
- **Branches:** the canonical `gsd/v0.9.6-doctest-block-rendering-and-release` is checked out. **No
  `gsd/v0.9.6-milestone` decoy exists yet** — the commit helper has created one in every milestone
  since v0.9.1, so expect one. `origin`'s counterpart is at `e54d47d0` and the local branch is
  **12 commits ahead** of it.
- **`main`:** `origin/main` = `6cc44f22` = the milestone base. The branch lacks **zero** `main`
  commits, so SC4's trial merge is expected to be a recorded no-op.
- **Open PRs: zero.** Nine stale `dependabot/uv/*` remote branches exist with no open PR behind
  them. Unlike Phase 73 (five open Dependabot PRs, D-06), there is no merge-ordering question this
  time. Plans re-measure; if PRs have opened by execution, the handoff orders them after the
  milestone PR, the order v0.9.3 used.
- **Publish probes:** `git ls-remote --tags origin` carries `v0.9.0` and `v0.9.2` but no `v0.9.6`.
- **Milestone diff outside `.planning/`:** 9 files, +865/−3. Under `typsphinx/` exactly
  `pathfmt.py` and `translator.py`.
- **Dependency diff `v0.9.2..HEAD`:** runtime `dependencies` **unchanged**; the `dev` extra **did
  change** (`tox-uv-bare>=1.35,<2` → `tox-uv>=1.35,<2`; `ruff>=0.15,<0.16` → `ruff>=0.15,<0.17`),
  and two `ruff` ignores (`UP035`, `UP006`) were removed. This is why D-04 forbids the blanket
  "zero new runtime or dev dependencies" sentence `[0.9.2]` used.

</domain>

<decisions>
## Implementation Decisions

### The `## [0.9.6]` section's shape

- **D-01: The Phase 74 doctest bullet goes at the head of `### Fixed`; the six carried bullets are
  byte-identical.** They are promoted in their current assignment — `### Added` (linkcheck) →
  `### Changed` (four contributor-tooling bullets) → `### Fixed` — which is the house order
  `[0.9.2]`, `[0.9.0]` and `[0.8.0]` use. The carried bullets are not compressed, re-worded or
  re-ordered: REL-15 says they are *promoted*, and 69/71/73's D-05 each recorded the same
  byte-identical rule. Within `### Fixed` the order is: doctest (new) → QUA-14 (new, D-09) →
  the carried sidebar bullet.

- **D-02: `## [0.9.6]` carries a lead paragraph, framed on the doctest rendering fix as the
  release's subject.** The contributor tooling is acknowledged in one sentence as a side note, not
  as the release's theme. Every prior released section (`[0.9.2]:69`, `[0.9.0]:126`, `[0.8.0]:252`,
  `[0.7.1]:325`, `[0.7.0]:405`, `[0.6.5]:462`) carries such a paragraph; omitting one would be the
  first exception.

- **D-03: The lead paragraph recommends the upgrade explicitly**, in the register `[0.9.2]` used
  ("0.9.0 users should upgrade to this release"). The reader's previous release is **0.9.2**, not
  0.9.5 — `0.9.3`, `0.9.4` and `0.9.5` are permanently unclaimed on PyPI — so the recommendation and
  any "since" framing are written against 0.9.2, and the diff a user receives spans three
  milestones. The justification for the recommendation is that the pre-fix failure was not only
  cosmetic: a `doctest_block` followed by further content in the same container aborted the
  `typst.compile()` with `expected semicolon or line break`.

- **D-04: `## [0.9.6]` carries a `### Verified` section, and its invariance claims are stated
  precisely.** Every prior released section has one. The blanket sentence `[0.9.2]` used — "Zero
  new runtime or dev dependencies across this milestone's diff" — is **false for v0.9.6** and must
  not be copied: the measured `v0.9.2..HEAD` diff leaves runtime `dependencies` untouched but does
  change the `dev` extra (`tox-uv-bare` → `tox-uv`, `ruff` cap `<0.16` → `<0.17`). The correct
  shape is "zero new runtime dependencies; the `dev` extra changed only by the `tox-uv` return".
  The other `### Verified` items are the four `@preview` packages unchanged across the three sync
  surfaces, the GATE-01 real-compile coverage, and the clean-build warning ledger.

- **D-05: The `## [0.9.6] - YYYY-MM-DD` date is the prep authoring date, fixed, and not corrected
  if the tag lands later.** Precedent measured: `[0.9.2] - 2026-08-30` was written on 2026-08-30 in
  bump commit `10d9d95d` and merged 2026-08-31 (one day out); `[0.9.0] - 2026-08-17` was written on
  2026-08-17 in `e74733d8` and tagged 2026-08-22 (five days out). `75-HANDOFF.md` records this as a
  **fact, not a step**: the heading date is the prep date and may differ from the tag date, and
  `/gsd-complete-milestone` does not rewrite it.

### The Phase 74 CHANGELOG bullets

- **D-06: The doctest bullet claims both the rendering fix and the compile failure.** The lead
  claim is that a `>>>` example now renders as a Typst code block with its line structure intact;
  the second sentence records that in the shape where further content follows the block in the same
  container, the PDF compile itself failed. Measured basis: pre-fix the translator emitted
  `unknown node type: <doctest_block …>` and let the node's `Text` children flow as running prose
  (two such lines in this project's own `api/index` build); the GATE-01 context (a) fixture
  reproduced the `expected semicolon or line break` compile abort on the pre-handler tree.

- **D-07: The bullet discloses the `python`-fence trade-off in one sentence** — the whole block is
  highlighted as Python, so output lines are coloured as Python source rather than as console
  output. Measured basis (74-CONTEXT D-01): `codly-languages:0.1.10` has a `python` entry and no
  `pycon` entry, so `pycon` yields neither highlighting nor a language label; under `python` the
  measured output line `'index.typ'` comes out green as a string literal. The `honour an existing
  non-empty language` path (74 D-02) is **not** mentioned — standard Sphinx never sets `language`
  on a `doctest_block`, so no ordinary build reaches it.

- **D-08: The bullet's single evidence sentence is the reflection into the published
  documentation** — typsphinx's own API reference is the worked example, and it reaches the
  published docs with this release. This **inverts** 73 D-04's standing prohibition ("must not
  claim the fix is visible on the default (`stable`) documentation"), and the inversion is
  deliberate: that rule existed because v0.9.5 published nothing, whereas publishing v0.9.6 moves
  Read the Docs' `/en/stable/` off `v0.9.2` on its own (ROADMAP constraint 13). The sentence does
  not name warning counts or build numbers (constraint 4).

- **D-09: QUA-14 gets its own bullet, second in `### Fixed`.** It is not folded into the doctest
  bullet and not omitted. It says that typsphinx's own docstrings no longer raise docutils
  `Unexpected indentation` / `Block quote ends without a blank line` errors when the package is
  autodoc'd. Measured basis: the base `6cc44f22` clean `LC_ALL=C` `-b typst` build reported 3
  attributed and 10 raw such messages; the tip reports zero, and the total warning ledger went
  `5 warnings` → `build succeeded.` with none. The two sites fixed were `translator.py`'s
  `visit_toctree` docstring and `pathfmt.py`'s `quote_path` docstring.

### REL-16 — the `### Known Limitations` question

- **AMENDED 2026-09-20 (owner-approved, measured during this discussion): two of the three
  candidate defects REL-16 names are already closed.** `REQUIREMENTS.md:23`, ROADMAP SC3 and
  `PROJECT.md:88-90` all name the candidate set as "NUM-01's per-master `numref` divergence, the
  converted-image rehome collision, the `typst_documents` duplicate-target cluster". Measured:
  - `2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md` is in
    `.planning/todos/completed/`. `MILESTONES.md:746` records "The two PR #131 follow-on image
    defects closed (IMG-01, IMG-02)", and `builder.py:40` carries the
    `RESERVED_IMAGE_NAMESPACE = "_typst_converted"` that fixed it (v0.8.0).
  - All three `typst_documents`-modelling todos —
    `2026-08-04-duplicate-typst-documents-target-silently-drops-a-master.md`,
    `2026-08-05-a-master-that-is-also-a-toctree-child-is-unrepresentable.md` and
    `2026-08-05-shared-document-silently-dropped-from-all-but-first-master.md` — are in
    `.planning/todos/completed/`. `builder.py:1068 _validate_output_path_collisions()` is the
    pre-write validator that closed the duplicate-target half (v0.8.0 Phase 47).
  - `.planning/todos/pending/` holds exactly three records: QUA-08 (linkcheck CI, deferred to
    Future), **NUM-01**, and MSG-06 (hardcoded delimiter in `translator.py`'s DEBUG logs).

  The requirement text in `REQUIREMENTS.md` and `ROADMAP.md` stays **literal and unedited**; this
  reframing lives here, the same treatment Phase 74 gave its two falsified TRN-02 claims. What
  changes is the candidate set, not REL-16's demand for an explicit answer.

- **D-10: `## [0.9.6]` carries a `### Known Limitations` section, holding NUM-01 and nothing
  else.** Writing the two closed defects would publish already-fixed issues as current
  limitations — the mirror image of the over-broad true-sounding claim this project recorded
  against itself at the v0.9.0 close (`MILESTONES.md:626-630`). WR-02 / WR-03, which are genuinely
  open in `REQUIREMENTS.md` § Future, are **not** added: REL-16 does not name them, and adding them
  would widen a disclosure requirement beyond its text.

- **D-11: The NUM-01 entry states the precondition, both symptoms, and a workaround.** Its shape
  follows the existing `### Known Limitations` precedent at `CHANGELOG.md:1205` (bold lead,
  sub-bullets, a `Workaround:` line):
  - **Precondition:** it occurs only in a `typst_documents` configuration declaring more than one
    master. A single-master project is unaffected, and the entry says so.
  - **Symptom (a):** a figure reachable from two masters gets one baked-in Sphinx number in the
    `:numref:` reference text, while Typst counts captions independently per compiled wrapper — so
    the same reference reads correctly in one master's PDF and points at the wrong number in the
    other's. Nothing reports the divergence.
  - **Symptom (b):** a figure reachable only from a non-root master never enters the `root_doc`
    figure-number scan, so the reference falls back to the raw label text. Sphinx emits **one**
    warning naming the label, so a build-log reader gets a diagnostic even though the PDF reader
    gets none.
  - **Workaround:** the honest one — a single-master configuration, or `:ref:` in place of
    `:numref:` for the affected figures. Both give up something; the entry does not oversell them.
  - The entry does **not** promise a fix or a version. NUM-01 is disclosure-only this milestone
    (`REQUIREMENTS.md` § Out of Scope).

- **D-12: The `grep` over `CHANGELOG.md` for `Known Limitations` and this decision record must
  agree, and the phase evidence names which branch was taken (SC3).** After this phase the file
  carries **two** `### Known Limitations` headings: the pre-existing one in `[0.1.0b1]` at `:1205`
  and the new one in `[0.9.6]`. Any grep-based check is written to expect two, not one.

### Phase 74's leftovers

- **D-13: The five untracked `probe_*.typ` files at the repo root are deleted in this phase.**
  `probe_bogusxyz.typ`, `probe_none.typ`, `probe_pycon.typ`, `probe_python.typ`, `probe_text.typ`,
  left from Phase 74's D-01 language-tag compile probing (milestone audit tech_debt #2). They are
  untracked, so the deletion produces no commit and does not touch SC5's `git diff` reading; the
  point is a clean `git status` at the milestone close. `.gitignore` is **not** edited — that would
  be a product-tree commit outside the file set REL-15 names.

- **D-14: IN-01 is not fixed here; it is filed as a pending todo.** `74-REVIEW.md`'s unresolved
  Info finding — `visit_literal_block` / `depart_literal_block` still document
  `node: The literal block node` although both signatures widened to
  `nodes.literal_block | nodes.doctest_block` — stays untouched, and a new record goes in
  `.planning/todos/pending/`. Precedent: v0.7.1's D-03 declined the `typst_authors` shim purely to
  hold the prep-only fence, and D-27 cited that consistency to decline a `builder.py` fix in the
  same phase. Touching `typsphinx/` here would also force SC4's entire green proof (full pytest
  twice, clean `docs-html` / `docs-pdf`, the single CI run) to be re-taken on the changed tip.

### Push and CI dispatch

- **D-15: The branch is pushed whenever it is convenient; exactly one CI run is dispatched, on the
  bumped tip.** Owner rule, 2026-09-20: the PR remains per-milestone (opened at
  `/gsd-complete-milestone`), and pushing in between is free. Measured basis: `ci.yml`'s triggers
  are scoped to `main`/`develop`, so a push to the milestone branch runs no CI (ROADMAP constraint
  10) — push cost is zero and push timing carries no evidence weight. The single
  `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release` happens **after** the
  bump and CHANGELOG work is pushed, so it covers the whole tree including
  `tests/test_docstring_rest_census_guard.py`, which the last CI run (`35476044079`, on
  `e54d47d0`) does not (milestone audit tech_debt #1). If a dispatch returns HTTP 5xx,
  `gh run list` is checked before any retry — a silent second run breaks the exactly-one reading.

### Claude's Discretion

The owner did not discuss the following; they are governed by ROADMAP SC 1–5 or carried unchanged
from Phases 69 / 71 / 73, and the planner applies them without re-asking:

- **The fence.** `75-CLOSEOUT-GUARD.md` recording `sha256sum` and `wc -l` of
  `.planning/REQUIREMENTS.md`, `PHASE_BASE_SHA`, and the verbatim `grep -n 'REL-15'` lines at phase
  head; re-run and MATCH at phase close **and once more after `phase.complete`-family tooling has
  run**, including `/gsd-verify-work`'s inline transition. SHA-256 is the primary probe (a checkbox
  flip leaves `wc -l` unchanged). REL-16's line is recorded separately as expected-to-move. On a
  flip: `git checkout -- .planning/REQUIREMENTS.md`, reported, never committed. Every plan's
  `SUMMARY.md` declares `requirements-completed: []` for REL-15. Back up REQUIREMENTS, ROADMAP and
  STATE to scratch before `phase.complete` or `/gsd-verify-work` runs.
- **The trial merge is non-committing** (71 D-05 / 73 D-09): `git fetch origin`;
  `git merge-tree --write-tree HEAD origin/main` with exit code and tree SHA transcribed;
  `git archive <tree> pyproject.toml uv.lock` into scratch then `uv lock --check`; `ruff check .`
  on the merged tree. `main`'s protection, merge method and required contexts are read with
  `gh api`, not assumed. Expected to be a no-op — `origin/main` is still the milestone base.
- **The bump mechanics.** `pyproject.toml:7` is the sole hand-edited version literal; `uv.lock` is
  regenerated by `uv lock`, never edited; `README.md`'s Status line goes to `v0.9.6`;
  `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` gains `"0.9.6"`; all of it lands in one
  commit whose `git show --name-only` lists the four files together.
- **The fresh `## [Unreleased]`.** Placed above `## [0.9.6]` and retaining only
  `### Planned for Future Releases`, which is **not** promoted. Measured precedent: at tag `v0.9.2`
  the `## [Unreleased]` section held exactly that scratch block and nothing else.
- **The tail link block.** `[Unreleased]`'s compare base `v0.9.2` → `v0.9.6`, plus a new
  `[0.9.6]: …/releases/tag/v0.9.6` line above `[0.9.2]`. No `## [0.9.3]`, `## [0.9.4]` or
  `## [0.9.5]` heading or tail link is created.
- **`scripts/extract_changelog_section.py 0.9.6` is executed** and its stdout transcribed into the
  phase evidence, verified non-empty, byte-faithful to the `## [0.9.6]` section, and free of the
  `Planned for Future Releases` scratch block.
- **Requirement IDs** are attached in the trailing-parenthesis style the existing bullets use
  (`(TRN-01, TRN-02)`, `(QUA-14)`), and the two new bullets do **not** carry the "This has no effect
  on installing or using typsphinx" sentence — they are the release's user-visible content.
- **The handoff.** `75-HANDOFF.md` enumerates the PR to `main` and its required checks, the
  `v0.9.6` tag push, the expected manual approval of the `pypi` GitHub Environment (a gate, not a
  failure), the GitHub Release body being byte-identical to the extract script's stdout, the
  **manual** `typsphinx-doc-translations` `update-pin.yml` dispatch, the Read the Docs `en` and
  `ja` `stable` endpoints reporting `0.9.6`, and the four observations REL-15 is checked on. It
  records that `release.yml`'s `create-release` job has never run on a v0.9.x tag and that a failure
  there is handled inside the release work rather than deferred. It also carries D-05's date fact,
  D-14's filed todo, and the Dependabot ordering rule if any PR has opened by then.
- **The decoy branch.** If a `gsd/v0.9.6-milestone` appears carrying commits, the canonical ref is
  fast-forwarded to it and HEAD re-pointed with `git symbolic-ref` **before** the decoy is deleted.
- **The probes.** `git tag -l 'v0.9.6'` and a remote tag probe, empty at two observations separated
  by intervening waves, each remote probe carrying a `v0.9.2` positive control; PyPI 404 for
  `0.9.6` with a 200 for `0.9.2`; no `v0.9.6` GitHub Release.

### Folded Todos

- **`2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`
  (NUM-01)** — folded for **disclosure only**. D-10/D-11 put it in `## [0.9.6]`'s
  `### Known Limitations`; the defect itself is not fixed and the todo stays in
  `.planning/todos/pending/` after this phase. It is the source of the two measured symptoms D-11
  describes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope, constraints, acceptance
- `.planning/ROADMAP.md` § "Phase 75: v0.9.6 Release Prep (prep-only)" — goal, SC 1–5, the
  cross-cutting constraints (REL-15 cited as coverage only in **every** plan's frontmatter; REL-16
  is different and must not be copy-pasted from prior prep phases; the tail link block is this
  phase's work)
- `.planning/ROADMAP.md` § "v0.9.6 — Doctest block rendering and release" — binding constraints
  1–13, especially 1 (zero irreversible action; REL-15 checked only at `/gsd-complete-milestone`),
  2 (version `0.9.6`, six carried bullets, link block moves in the same phase), 4 (counts measured
  fresh), 5 (clean builds under `LC_ALL=C` with positive controls), 9 (the REQUIREMENTS fence,
  line-scoped to REL-15), 10 (branch census, decoy handling, CI dispatch), 11 (worktree
  provisioning; the `docs` extra and the changelog page gate), 12 (`**UI hint**: no`), 13
  (publishing moves `stable`; `update-pin.yml` is manual; `create-release` untested on v0.9.x)
- `.planning/REQUIREMENTS.md` — REL-15 (`:22`), REL-16 (`:23`), § Future (NUM-01, WR-02/WR-03,
  QUA-08, the docs warnings gate), § Out of Scope (the three carried defects are disclosed, not
  fixed), § Traceability (`:59-76`)
- `.planning/v0.9.6-MILESTONE-AUDIT.md` — the four tech-debt items handed to this phase (post-CI
  source drift; the `probe_*.typ` leftovers; IN-01; Phase 74 wrote no CHANGELOG bullet)
- `CLAUDE.md` § "Worktree-isolated execution", § "NixOS development shell" (Locale; Interpreters
  may differ)

### Prior prep-only phases (the shape this phase reuses)
- `.planning/milestones/v0.9.5-phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CONTEXT.md` —
  D-05 (existing CHANGELOG content byte-identical), D-08 (the closeout guard), D-09 (non-committing
  trial merge), D-10 (handoff structure). **D-04's "must not claim the fix is visible on `stable`"
  is deliberately inverted here by D-08** — that rule existed because v0.9.5 published nothing
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CONTEXT.md` —
  the guard and handoff procedure this phase's fence reuses
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-CONTEXT.md` — D-03 (the
  prep-only fence declining an in-scope-looking fix, the precedent behind D-14), D-27 (declining a
  `### Known Limitations` section in full, the counter-branch SC3 allows)
- `.planning/MILESTONES.md:618-638` § "Known limitations shipped" (v0.9.0) — the register D-11
  follows, and `:626-630`'s self-criticism about an over-broad true-sounding claim, which is the
  reasoning behind D-10's exclusion of the two closed defects
- `.planning/MILESTONES.md:746-750` — "The two PR #131 follow-on image defects closed (IMG-01,
  IMG-02)", the measurement behind the AMENDED block

### Phase 74's output (what the new bullets describe)
- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-CONTEXT.md`
  — D-01 (why `python` and not `pycon`; the measured colour census behind D-07), D-02 (the honour
  path D-07 omits), D-07 (the QUA-14 census, both sites)
- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/` —
  `74-VERIFICATION.md`, the plan `SUMMARY.md` files and `74-REVIEW.md` (IN-01, D-14)
- `typsphinx/translator.py` — `visit_doctest_block` / `depart_doctest_block` (`:2628-2665`), the
  widened `visit_literal_block` / `depart_literal_block` signatures, `visit_toctree`'s docstring
- `typsphinx/pathfmt.py` — `quote_path`'s docstring (the second QUA-14 site)
- `tests/test_doctest_block_render_gate.py`, `tests/test_docstring_rest_census_guard.py` — the
  GATE-01 gate and the Nyquist census guard; the latter is the file CI has not yet run

### Release machinery
- `CHANGELOG.md` — `## [Unreleased]` (`:8`), `### Planned for Future Releases` (`:62`),
  `## [0.9.2]` (`:69`, the lead-paragraph and `### Verified` model), the existing
  `### Known Limitations` in `[0.1.0b1]` (`:1205`, the register D-11 follows), the tail link block
- `scripts/extract_changelog_section.py` — the positional extraction algorithm and its module
  docstring's warning about the two `## [Unreleased]` headings; SC2 requires running it
- `tests/test_changelog_page_gate.py` — `RELEASE_VERSIONS` (`:50`) gains `"0.9.6"`; a zero-skip
  reading needs the `docs` extra present
- `tests/test_readme_version_sync.py`, `README.md:348` — the Status line SC1 checks
- `.github/workflows/release.yml` — the `validate` / `build` / `publish-pypi` / `create-release`
  job order and the `pypi` environment gate the handoff describes
- `.github/workflows/ci.yml` — triggers scoped to `main`/`develop` (the basis for D-15)

### NUM-01's measurement (behind D-11)
- `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`
  — both symptoms, the corrected "one warning, not silent" finding, and the owner decision that
  moved the fix out of scope
- `tests/fixtures/state_guard_numref_two_case_gate/`, `tests/test_state_guard_numref_gate.py` — the
  live fixture the measurement came from

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/extract_changelog_section.py` — the one committed, pytest-covered extractor;
  `release.yml` calls it from both `validate` and `create-release`. SC2 requires executing it and
  transcribing its stdout, not reimplementing the extraction.
- `tests/test_changelog_page_gate.py` / `tests/test_readme_version_sync.py` /
  `tests/test_preview_version_sync.py` — the three gates that make the bump self-checking. The
  first needs the `docs` extra to avoid skips.
- `typsphinx/builder.py:1068 _validate_output_path_collisions()` and `:40
  RESERVED_IMAGE_NAMESPACE` — read-only here, as the evidence that two of REL-16's named defects
  are closed.

### Established Patterns
- Version bump + curated CHANGELOG section in the final phase, publish at
  `/gsd-complete-milestone` — standing since v0.5.0 Phase 10.
- Released sections carry a lead paragraph, then `### Added` → `### Changed` → `### Fixed` →
  `### Removed` → `### Verified`, and a dated heading.
- Each bullet: a bold lead phrase ending in trailing-parenthesis requirement IDs, prose written for
  a reader of the published changelog page (`docs/source/changelog.rst` includes `CHANGELOG.md`),
  at most one evidence sentence.
- Every docs measurement starts from `rm -rf` of the output directory and runs under `LC_ALL=C`
  with a positive control on the pre-fix base.

### Integration Points
- `docs/source/changelog.rst` includes `CHANGELOG.md`, so every bullet is published documentation
  and the changelog page gate renders it.
- `release.yml` reads the `## [0.9.6]` section at tag time through the extract script; whatever is
  in the tagged tree becomes the GitHub Release body (the basis for D-05's "not corrected later").
- The `dev` extra lacks the `docs` extra, so in a bare worktree venv the changelog page gate skips.
  A zero-skip reading is taken only where `docs` is present; in the main checkout re-sync with
  `--extra dev --extra docs`.

</code_context>

<specifics>
## Specific Ideas

- The AMENDED block under REL-16 is the load-bearing correction of this discussion. A planner that
  reads only `REQUIREMENTS.md:23` or ROADMAP SC3 will produce a three-item
  `### Known Limitations` section naming two defects fixed in v0.8.0. D-10 is the binding
  instruction; the requirement text is literal and stays that way.
- D-08 deliberately reverses a standing prohibition from the immediately preceding prep phase
  (73 D-04). A reviewer comparing the two phases should read the reason, not flag the difference.
- After this phase `CHANGELOG.md` holds two `### Known Limitations` headings (D-12). Any
  grep-shaped acceptance check must expect two.
- The Dependabot situation differs from Phase 73's: zero open PRs today, nine stale
  `dependabot/uv/*` remote branches. Plans re-measure rather than inherit either state.

</specifics>

<deferred>
## Deferred Ideas

- **Fixing NUM-01.** Only its disclosure is in scope (`REQUIREMENTS.md` § Out of Scope). The todo
  stays pending after this phase.
- **Disclosing WR-02 / WR-03 in the CHANGELOG.** Genuinely open, but not named by REL-16 (D-10).
  `MILESTONES.md:618` records that v0.9.0 was the third consecutive release to decline a
  `### Known Limitations` carve-out for WR-02; a future release may revisit it as its own
  requirement.
- **Fixing IN-01** (`visit_literal_block` / `depart_literal_block` `Args:` text). D-14 files it as
  a pending todo for a future milestone.
- **Adding `probe_*.typ` to `.gitignore`.** Rejected as a product-tree commit outside REL-15's file
  set (D-13). Deletion alone is sufficient.

### Reviewed Todos (not folded)
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` (QUA-08) — deferred to Future at v0.9.5. It needs a
  side PR to `main`, because a new workflow file cannot be scheduled or dispatched from an unmerged
  milestone branch. Not this phase.
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`
  (MSG-06) — touches `typsphinx/translator.py`, which the prep-only fence puts out of reach here,
  the same reasoning as D-14. Stays pending.

</deferred>

---

*Phase: 75-v0-9-6-release-prep-prep-only*
*Context gathered: 2026-09-20*
