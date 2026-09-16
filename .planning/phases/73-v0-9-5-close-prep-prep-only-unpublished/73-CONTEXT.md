# Phase 73: v0.9.5 Close Prep (prep-only, unpublished) - Context

**Gathered:** 2026-09-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Package the v0.9.5 milestone for a merge to `main`, and do nothing else. The phase does four
things:
- It adds two CHANGELOG bullets under the existing `## [Unreleased]`.
- It proves the tree is unpublished-shaped and green, using runs executed in this phase.
- It holds REL-14's checkbox at `[ ]` behind the SHA-256 fence.
- It writes a standalone `73-HANDOFF.md` for `/gsd-complete-milestone`.

**ROADMAP SC#1..SC#4 and constraints 1–13 govern this phase.** Nothing in them is re-decided here.
The discussion settled only two things the ROADMAP left open: where the CHANGELOG bullets go, and
what happens to the five Dependabot PRs open on `main`. The owner took option A on both. Every
other decision below carries forward from v0.9.4's Phase 71 (the same close-prep shape one milestone
earlier) or from Phase 72.

**Zero irreversible action.** This phase makes no version bump and creates no tag, local or remote.
It uploads nothing to PyPI and creates no GitHub Release. It opens no PR, merges nothing, dispatches
no `update-pin.yml` and comments on no PR. It takes two outward actions, both standing prep-phase
precedent (Phases 57, 61, 63, 69, 71):
- it pushes the canonical milestone branch;
- it dispatches `ci.yml` through `workflow_dispatch`.

**Measured state at discussion time (2026-09-14, HEAD `1b8d0884`).** These figures are context
only. Constraint 8 requires each plan to re-measure fresh.
- **Version:** `pyproject.toml:7` reads `version = "0.9.2"`.
- **Branches:** local `gsd/v0.9.5-docs-link-check-and-navigation` is 11 commits ahead of its
  `origin` counterpart (`0b2595df`, Phase 72's pushed tip). All 11 are `.planning/` commits.
  `git branch -a` shows only the canonical branch and its remote-tracking ref, so no
  `gsd/v0.9.5-milestone` decoy exists.
- **`main`:** after `git fetch origin`, `origin/main` = `098a8ff6` = the milestone base, so the
  branch lacks **zero** `main` commits.
- **Milestone diff outside `.planning/`:** 5 files, +11/−5 (`CLAUDE.md`, `README.md`,
  `docs/source/contributing.rst`, `docs/source/index.rst`, `tox.ini`). Both
  `git diff --stat 098a8ff6..HEAD -- typsphinx/` and `git diff --stat 098a8ff6..HEAD -- .github/workflows/`
  are empty.
- **Open PRs:** five Dependabot PRs, all created 2026-09-14T00:15Z. Each changes **`uv.lock` only**,
  each is `MERGEABLE`, and each has 15/15 checks `SUCCESS`:
  - #146 `build` 1.5.0 → 1.6.1;
  - #147 `ruff` 0.16.6 → 0.16.7;
  - #148 `pypdf` 6.14.2 → 6.18.0;
  - #149 `twine` 6.2.0 → 7.0.0;
  - #150 `sphinx-autodoc-typehints` 3.0.1 → 3.13.6, a `docs`-extra dependency.

  Precedent: at the v0.9.3 close, #143 (the milestone PR) merged at 00:11Z and the Dependabot PRs
  #142 and #141 merged afterwards, at 00:31Z and 00:41Z.
- **CHANGELOG:**
  - `CHANGELOG.md:8` is `## [Unreleased]`.
  - `:10` is `### Changed`, which holds four bullets from v0.9.3 and v0.9.4. The last one ends at
    `:45`.
  - `:47` is `### Planned for Future Releases`.
  - `:1312` is `[0.9.2]: …/releases/tag/v0.9.2`.
  - `:1334` is `[Unreleased]: …/compare/v0.9.2...HEAD`. The file is 1334 lines.
  - The released sections use `### Added`, then `### Changed`, then `### Fixed` (then
    `### Removed`, then `### Verified`). Examples: `[0.9.0]` at `:124/:137/:175` and `[0.8.0]` at
    `:247/:264/:288`.
  - Neither `tests/test_changelog_page_gate.py` nor `scripts/extract_changelog_section.py` asserts
    which subsections `## [Unreleased]` holds, so adding `### Added` and `### Fixed` there breaks
    neither.
- **What the bullets describe:** Phase 72's evidence (`72-*-EVIDENCE.md`):
  - `BASE_MULTI_TOCTREE_COUNT = 5` → `EDIT_MULTI_TOCTREE_COUNT = 0`;
  - `BASE_WARNING_COUNT = 3` = `EDIT_WARNING_COUNT = 3`;
  - `BASE_SIDEBAR_COUNTS = 2 2 2 2 2`, reduced to one each;
  - `BASE_ROOT_DEAD_INCLUDES = 5`, removed;
  - `LINKCHECK_VERDICT = PASS`;
  - CI run `34761445288`: 12/12 `success`.

</domain>

<decisions>
## Implementation Decisions

### The CHANGELOG bullets (owner: option A)

- **D-01: Two bullets, each under a new subsection that follows the house order of the released
  sections.**
  - **`### Added`** is inserted directly after `## [Unreleased]`, before the existing
    `### Changed`. It holds one bullet: the new `tox -e linkcheck` environment (QUA-13, DOC-24).
  - **`### Fixed`** is inserted after the last `### Changed` bullet, before
    `### Planned for Future Releases`. It holds one bullet: the docs sidebar fix (DOC-18).

  The result reads `### Added` → `### Changed` → `### Fixed` → `### Planned for Future Releases`,
  the order `[0.9.0]` and `[0.8.0]` use. Blank-line spacing matches the existing `### Changed`
  block: a blank line after each heading and between bullets.

- **D-02: Both bullets follow the register of the four `### Changed` bullets.**
  - Each opens with a bold lead phrase that ends with the requirement IDs in trailing parentheses.
  - Each is prose written for a reader of the published changelog page, because
    `docs/source/changelog.rst` includes `CHANGELOG.md`.
  - Each carries one plain sentence saying it has no effect on installing or using typsphinx.
  - Each carries at most one evidence sentence.
  - Neither names `v0.9.3`, `0.9.3`, `v0.9.4`, `0.9.4`, `v0.9.5` or `0.9.5` anywhere, because no
    release carries those numbers.
  - Neither mentions the Japanese site or its catalogs (Phase 71 D-02).

- **D-03: The linkcheck bullet (`### Added`) makes three points.**
  - `tox -e linkcheck` runs Sphinx's link check over the documentation sources, including
    `#anchor` targets.
  - It needs the network and is not part of a plain `tox` run.
  - It is contributor tooling.

  It must not claim, imply or foreshadow any CI job, scheduled run or required check (REL-14;
  QUA-08 is deferred). It carries no link count, because the count moves with the docs and
  constraint 8 forbids hard-coding it.

- **D-04: The sidebar bullet (`### Fixed`) makes these points.**
  - In the HTML documentation, each User Guide and Examples page now appears once in the sidebar,
    nested under its section, instead of also being listed a second time beside it.
  - Its one evidence sentence may say either or both of: Sphinx no longer reports those pages as
    referenced in multiple toctrees; the PDF still includes each page exactly once. It does not
    enumerate the five pages' paths or cite build counts.
  - It must not claim the fix is visible on the default (`stable`) documentation, which stays on
    `v0.9.2` until the next published release (constraint 5).

- **D-05: Everything else in `CHANGELOG.md` is byte-identical.** That covers:
  - the four `### Changed` bullets, including their heading line;
  - `### Planned for Future Releases`;
  - every versioned section;
  - the tail link block.

  The diff adds lines and removes none. The `[Unreleased]` compare base stays `v0.9.2`. No
  `### Verified` subsection and no lead paragraph are added (Phase 69/71 D-04). No versioned heading
  or tail link is created, and `scripts/extract_changelog_section.py` is not run for a new section.
  `CHANGELOG.md` is the only product-tree file this phase authors.

### The open Dependabot PRs (owner: option A)

- **D-06: #146–#150 are left untouched during this phase and named in `73-HANDOFF.md`.** They are
  merged **after** the milestone PR, the order v0.9.3 used (#143, then #142 and #141). This phase
  neither merges, rebases, comments on nor closes any of them. The handoff lists each one by number,
  package and version range, and states that the order is: milestone PR first, Dependabot second.
  Dependabot rebases the remaining `uv.lock`-only PRs on its own after each merge.

- **D-07: If `main` moves anyway before execution, the standing mechanism handles it.** If any
  Dependabot PR (or anything else) lands on `main` before or during execution, nothing new is
  added. SC#3's non-committing trial merge (D-09) catches it, and a `ruff` bump's verdict on the
  merged tree is authoritative. The handoff's branch-update step (D-10) is then live rather than a
  no-op. Plans do not add a docs build of the merged tree for #150. That would go beyond SC#3, which
  names `uv lock --check` and `ruff check .` only. Under D-06's order, #150 reaches `main` after the
  milestone and runs its own 15 checks there.

### Carried forward (not re-discussed)

- **D-08: The fence is `73-CLOSEOUT-GUARD.md`, reusing the 69/71 procedure.**
  - **At phase head** it records:
    - `sha256sum .planning/REQUIREMENTS.md`;
    - `wc -l .planning/REQUIREMENTS.md`;
    - `git rev-parse HEAD` as `PHASE_BASE_SHA`;
    - `grep -n 'REL-14' .planning/REQUIREMENTS.md` verbatim.
  - **Re-verification:** the same commands re-run and MATCH at phase close, and once more after
    `phase.complete`-family tooling has run. That includes `/gsd-verify-work`'s inline transition.
  - **Primary probe:** SHA-256, because a flip leaves `wc -l` unchanged.
  - **On a flip:** it is reverted with `git checkout -- .planning/REQUIREMENTS.md` and reported,
    never committed.
  - **Plans:** every plan's `SUMMARY.md` declares `requirements-completed: []`, and no plan writes
    `.planning/REQUIREMENTS.md`.
  - **Scratch backup:** back up REQUIREMENTS, ROADMAP and STATE to scratch before `phase.complete`
    or `/gsd-verify-work` runs.

- **D-09: SC#3's trial merge is non-committing** (Phase 71 D-05). The run is:
  1. `git fetch origin`;
  2. `git merge-tree --write-tree HEAD origin/main`, transcribing the exit code and tree SHA;
  3. `git archive <tree> pyproject.toml uv.lock` into scratch, then `uv lock --check`;
  4. `ruff check .` on the merged tree, at the merged lock's `ruff` version.

  Nothing from it is committed. `main`'s protection is read with
  `gh api …/branches/main/protection/required_status_checks`, and it must equal the six contexts
  read at Phase 72's base (`REQUIRED_CONTEXTS_HEAD` in `72-BASE-EVIDENCE.md`), with `strict: true`.

- **D-10: `73-HANDOFF.md` is structured like Phase 71's, negative first.**
  - **Opening:** it publishes nothing. There is no tag, no PyPI upload, no GitHub Release and no
    version bump. The `update-pin.yml` dispatch and the Read the Docs `stable` check are marked
    **not applicable**.
  - **Recorded as facts, not steps:**
    - the daily `update-pin.yml` schedule moves ja `latest` onto the merged `main` with no action;
    - `/en/latest/` rebuilds on the `main` push;
    - `stable` stays on `v0.9.2`.
  - **Steps:**
    1. A **conditional** branch-update step: if `origin/main` has moved past `098a8ff6`, merge it
       into the canonical branch with a merge commit (never a rebase), push, and re-check.
       Otherwise the step is a recorded no-op.
    2. Open the PR from `gsd/v0.9.5-docs-link-check-and-navigation` to `main`.
    3. Wait for the six required checks, named literally, to be green on the head.
    4. Merge with a merge commit (the method used for #143 and #145).
    5. Only then, the Dependabot PRs (D-06).
  - **REL-14 is checked on these observations after the merge (SC#4):**
    - the merge commit on `origin/main`;
    - `pyproject.toml` still `0.9.2`;
    - no `v0.9.3`, `v0.9.4` or `v0.9.5` tag;
    - PyPI 404 for `0.9.5`;
    - no Release.

- **D-11: Version numbers `0.9.3`, `0.9.4` and `0.9.5` are recorded as unclaimed, not decided.**
  After this phase, `## [Unreleased]` holds three unpublished milestones' bullets: four under
  `### Changed`, plus this phase's `### Added` and `### Fixed`. The handoff states that the next
  release-prep phase promotes all of them into its versioned section. The version number belongs to
  that milestone's scoping.

- **D-12: One CI dispatch on the phase's final tip, after the push** (Phase 71 D-10).
  1. Re-run the decoy census first. If a decoy carrying commits exists, advance the canonical
     pointer to it before deleting it.
  2. Push only the canonical branch.
  3. Run `gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation` and wait for it to
     finish.
  4. Transcribe every job conclusion literally. Name both `windows-latest` and both `macos-latest`
     lanes, and read `ruff`'s verdict from `Lint and Format Check`.

  No plan triggers `release.yml`.

- **D-13: SC#1's code-invariant probe is the milestone-wide diff.**
  `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` must be empty on the close tip.
  No masked-AST harness is needed: nothing under `typsphinx/` changed in this milestone. The remote
  probes each carry a positive control against the existing `v0.9.2`:
  - tags `v0.9.3`, `v0.9.4` and `v0.9.5`, via both `git tag -l` and `git ls-remote --tags`;
  - PyPI `0.9.3`, `0.9.4` and `0.9.5`;
  - GitHub Releases for all three.

- **D-14: SC#3's docs runs follow Phase 72's rules.**
  - **Clean builds under `LC_ALL=C`:** `rm -rf` the output directory first, and grep the English
    strings only under `LC_ALL=C`.
  - **Warning baseline:** taken at this phase's own base. That base already carries DOC-18's fix,
    so the expected `multiple toctrees` count is **zero** at both base and tip. The positive
    control is Phase 72's recorded pre-fix `BASE_MULTI_TOCTREE_COUNT = 5`: it shows that the
    `LC_ALL=C` grep finds the message when it is present.
  - **linkcheck:** runs clean. Its `working` count must equal the total, and is read from
    `output.json`. Non-`working` rows follow Phase 72 D-01..D-03: a transient row is re-run (three
    runs at most); anything else stops and goes to the owner.
  - **The CHANGELOG page gate:** its zero-skip reading is taken only where the `docs` extra is
    present. In the main checkout, re-sync with `--extra dev --extra docs`.

- **D-15: The UI-gate false positive is handled with `--skip-ui` at plan time** (Phase 72 D-09).
  No UI hint line is added to the ROADMAP.

### Claude's Discretion

- The exact prose of both bullets, within D-02..D-04.
- The requirement IDs in each bullet's trailing parentheses. The default is `(QUA-13, DOC-24)` for
  the linkcheck bullet and `(DOC-18)` for the sidebar bullet. REL-14 is not cited in a bullet.
- Plan decomposition, waves and evidence-file naming, following the Phase 71 set:
  - `73-CLOSEOUT-GUARD.md`;
  - `73-CHANGELOG-EVIDENCE.md`;
  - `73-PREFLIGHT-EVIDENCE.md`;
  - `73-GREEN-TREE-EVIDENCE.md`;
  - `73-CI-EVIDENCE.md`;
  - `73-HANDOFF.md`;
  - an SC#1 invariants file.

  `73-VERIFICATION.md` is reserved for the verifier and must not be authored by a plan. Evidence is
  written as bare `KEY = value` lines wherever a verify step extracts them.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contract
- `.planning/ROADMAP.md` § "Phase 73: v0.9.5 Close Prep (prep-only, unpublished)": the goal and
  SC#1..SC#4.
- `.planning/ROADMAP.md` § "🚧 v0.9.5 — Docs Link Check and Navigation (ACTIVE)": the binding
  constraints. The ones that bind most here:
  - 1: merge-only and unpublished;
  - 2: zero `typsphinx/` lines;
  - 3: no workflow edits, and the six required contexts;
  - 5: the `stable` visibility limit;
  - 6: branch census, decoy and CI dispatch;
  - 7: clean builds and `LC_ALL=C`;
  - 8: fresh counts;
  - 10: the checksum fence;
  - 12: worktree isolation and the `docs` extra.
- `.planning/REQUIREMENTS.md`: REL-14 verbatim, the Out of Scope table, and the Traceability note
  that REL-14 maps here for coverage only.

### Precedent (v0.9.4's close prep, the same shape)
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CONTEXT.md`:
  D-01..D-12, which carry forward.
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CLOSEOUT-GUARD.md`:
  the fence procedure to reuse.
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-HANDOFF.md`:
  the handoff structure (negative first, strict-protection update step, merge commit).
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-PREFLIGHT-EVIDENCE.md`:
  the shape of the `merge-tree` + `git archive` + `uv lock --check` transcript.
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CHANGELOG-EVIDENCE.md`,
  `71-GREEN-TREE-EVIDENCE.md`, `71-CI-EVIDENCE.md` and `71-SC1-INVARIANTS.md`: the evidence shapes.
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-PLAN*.md`
  (`71-01`..`71-07`): the plan decomposition that worked last time.

### What the bullets describe (Phase 72 evidence)
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CONTEXT.md`: Phase 72's
  decisions. D-01..D-03 (the linkcheck failure policy) are reused by D-14.
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-TOCTREE-EVIDENCE.md`: the
  sidebar and `multiple toctrees` numbers behind D-04.
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-LINKCHECK-EVIDENCE.md`: the
  environment behind D-03.
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-BASE-EVIDENCE.md`:
  `REQUIRED_CONTEXTS_HEAD`, `MAIN_BASELINE_RUN_ID` and the pre-fix positive control.
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CI-EVIDENCE.md`: Phase
  72's CI run (`34761445288`), the comparison point for this phase's run.

### Files this phase edits or reads
- **`CHANGELOG.md`:**
  - `:8` `## [Unreleased]`: `### Added` is inserted after it;
  - `:10-45` `### Changed` and its four bullets: byte-identical;
  - `:47` `### Planned for Future Releases`: `### Fixed` is inserted before it;
  - `:1334` the `[Unreleased]` tail link: untouched.
- **Read only:**
  - `pyproject.toml:7`: must still read `0.9.2`.
  - `docs/source/changelog.rst`: includes `CHANGELOG.md`, so the bullets become published text.
  - `tests/test_changelog_page_gate.py`: needs `myst_parser` (the `docs` extra) and skips without
    it.
  - `.github/workflows/ci.yml`: the `workflow_dispatch` route and the 3-OS matrix. `release.yml` is
    never triggered.
- `CLAUDE.md` § "Worktree-isolated execution": the mandatory per-worktree `uv sync` + `uv run`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The 61/63/69/71 `CLOSEOUT-GUARD.md` procedure. It is the only measure that has caught the
  release-requirement flip, which fired at 8 of 9 prior release-prep closes and did not fire at 71.
- `git merge-tree --write-tree` + `git archive` + `uv lock --check`. Together they measure the
  merge result without touching the branch.

### Established Patterns
- Keep a Changelog subsection order in the released sections: `### Added` → `### Changed` →
  `### Fixed` → `### Removed` → `### Verified`.
- Bold-lead bullets with trailing requirement IDs, one plain "no effect on installing or using
  typsphinx" sentence, and at most one evidence sentence (`CHANGELOG.md:12-45`).
- Remote probes (tag, PyPI, GitHub Release) each carry a positive control against `v0.9.2`.

### Integration Points
- `docs-html` and `docs-pdf` consume `CHANGELOG.md`. A malformed MyST bullet or heading shows up as
  a new docs warning against the clean-build baseline.
- New CHANGELOG text feeds `tox -e linkcheck` through `changelog.rst`. If a bullet carries a URL,
  that URL is checked too. The default is no URL in either bullet.

</code_context>

<specifics>
## Specific Ideas

- **Draft shapes** (wording at discretion):
  - `### Added`: "**A `tox -e linkcheck` environment checks the documentation's external links and
    anchors (QUA-13, DOC-24).** … needs the network and is not part of a plain `tox` run … listed
    beside `docs-html` and `docs-pdf` in the contributor notes … This has no effect on installing
    or using typsphinx."
  - `### Fixed`: "**The HTML documentation's sidebar lists each User Guide and Examples page once
    (DOC-18).** … nested under its section … Sphinx no longer reports these pages as referenced in
    multiple toctrees, and the PDF still includes each page exactly once. This has no effect on
    installing or using typsphinx."

</specifics>

<deferred>
## Deferred Ideas

- Choosing the next published version number (`0.9.3`, `0.9.4`, `0.9.5` or other) belongs to the
  next milestone's scoping (D-11).
- A docs build of `main` + #150 (`sphinx-autodoc-typehints` 3.13.6). Under D-06 this runs as that
  PR's own checks after the milestone merge, not in this phase.

### Reviewed Todos (not folded)
- `2026-07-22-add-sphinx-linkcheck-ci-job.md`: QUA-08, a Future requirement. It needs a workflow
  file, which constraint 3 forbids. It already carries Phase 72's D-07 status note.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`: NUM-01.
  It is a `typsphinx/` change (constraint 2).
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`: MSG-06.
  It is a `typsphinx/` change (constraint 2).
- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line.md`: TRN-01. It is a
  `typsphinx/` change (constraint 2).

</deferred>

---

*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Context gathered: 2026-09-14*
