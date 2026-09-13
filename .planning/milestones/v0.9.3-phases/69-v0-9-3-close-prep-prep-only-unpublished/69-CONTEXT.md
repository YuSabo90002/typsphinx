# Phase 69: v0.9.3 Close Prep (prep-only, unpublished) - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Package the v0.9.3 toolchain milestone for a merge to `main` and nothing else: author this
milestone's CHANGELOG bullets under the existing `## [Unreleased]` heading, prove the tree
unpublished-shaped and green on runs executed in this phase, hold REL-12's checkbox at `[ ]` behind
the SHA-256 fence, and write a standalone `69-HANDOFF.md` for `/gsd-complete-milestone`.

**ROADMAP SC#1..SC#4 govern this phase unchanged.** Unlike Phase 61 (61-CONTEXT D-11), nothing here
drops or rewords a success criterion; the decisions below only settle what the criteria leave open.

**Zero irreversible action.** No version bump, no tag (local or remote), no PyPI upload, no GitHub
Release, no PR opened, no merge, no `update-pin.yml` dispatch, no comment on any PR. Pushing the
canonical milestone branch and dispatching `ci.yml` via `workflow_dispatch` are the only outward
actions, and both are the standing prep-phase precedent (Phases 57, 61, 63).

**Measured state at discussion time (2026-09-13, HEAD `c4b2fd7c`):**
- `pyproject.toml:7` reads `version = "0.9.2"`; the milestone's only `pyproject.toml` change is the
  `tox-uv` line.
- `git diff --stat $(git merge-base origin/main HEAD) HEAD -- typsphinx/` is empty.
- `git tag -l 'v0.9*'` returns `v0.9.0` and `v0.9.2` only (a ready positive control).
- `CHANGELOG.md:8` `## [Unreleased]` holds only `### Planned for Future Releases` (zero real change
  bullets); the tail link at `CHANGELOG.md:1297` is `[Unreleased]: …/compare/v0.9.2...HEAD`.
- `origin/gsd/v0.9.3-toolchain-and-dependency-update-repair` is at `d9c75553`, **114 commits behind**
  local HEAD.
- `origin/main` carries 4 commits the milestone branch lacks: `7cc85d28` / `293f0c26` (#137,
  dependabot `pip` → `uv`) and `88088071` / `cf3305ce` (#138, `ruff` 0.15.20 → 0.16.6).
- `main` branch protection: `strict: true` with 6 required checks — `Test Python 3.12 on
  ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Lint and Format Check`, `Type Check`,
  `Code Coverage`, `Build Package`. The PR cannot merge until the branch is up to date with `main`.
- Trial merge: `git merge-tree --write-tree HEAD origin/main` → tree `7c9e3002…`, rc 0 (no
  conflict); `uv lock --check` on that tree's `pyproject.toml` + `uv.lock` → `Resolved 91 packages`,
  rc 0; the merged lock pins `ruff` 0.16.6 and the merged `pyproject.toml` carries `tox-uv>=1.35,<2`
  and `ruff>=0.15,<0.17`.
- Open PRs: dependabot `uv` lockfile-only #139 (`tox`), #140 (`sphinx-intl`), #141 (`pre-commit`),
  #142 (`mypy`).

</domain>

<decisions>
## Implementation Decisions

The owner accepted every recommendation presented ("おすすめ"). Each decision is grounded in the
measurements above; re-measure at execution time rather than copying values from this file.

### The `## [Unreleased]` CHANGELOG bullets

- **D-01: The milestone is described in three bullets under a `### Changed` subsection of the existing `## [Unreleased]`.** One bullet per track, bold lead phrase, requirement IDs in trailing parentheses (house style since Phase 33): (1) the `dev` extra and `tox.ini` return to `tox-uv` from `tox-uv-bare` (TOX-01..TOX-04); (2) Dependabot's Python updates switch from the `pip` to the `uv` ecosystem, so each dependency PR updates `pyproject.toml` and `uv.lock` in the same commit and passes `uv sync --locked` (DEP-01..DEP-05); (3) a NixOS development shell in which `flake.nix` runs the project's own `.venv` tools inside an FHS sandbox, with the contributor notes updated to match (NIX-01..NIX-08, DOC-19..DOC-21). Precedent measured: `0.4.4` (`### Changed` → "CI/Release Durability") and `0.5.0` (`### Added` → "CI Durability Guardrails", Dependabot group) both recorded tooling-only work as bold-lead bullets; `### Changed` fits because every item modifies existing tooling.

- **D-02: Each bullet states plainly that it has no effect on installing or using typsphinx.** `docs/source/changelog.rst` includes `CHANGELOG.md` wholesale, so the bullets are published on Read the Docs `latest` once REL-12 merges. Write them as prose a user reads, not internal shorthand, and do not name `v0.9.3` or `0.9.3` anywhere in the prose (no release carries that number).

- **D-03: The new `### Changed` block sits above `### Planned for Future Releases`, which stays byte-identical.** Same placement Phase 61 used (61-CONTEXT D-03; 63-CONTEXT D-20 found the bullets at `:10-36` and the Planned block after them). The tail link-reference block is untouched: no `[0.9.3]` line, `[Unreleased]` compare base stays `v0.9.2` (SC#2).

- **D-04: No `### Verified` subsection and no lead paragraph under `## [Unreleased]`.** The next release-prep phase authors `### Verified` against its own whole diff when it promotes these bullets into a versioned section, exactly as Phase 63 did with Phase 61's bullets (61-CONTEXT Claude's Discretion, 63-CONTEXT D-04 and D-06).

- **D-05: The `ruff` 0.15.20 → 0.16.6 bump (#138) gets no bullet of its own.** It is a routine `dev`-extra version bump already on `main`; the DEP bullet describes the mechanism that produced it. The DEP bullet may cite it as the first dependency PR to pass under the new ecosystem if that reads naturally (Claude's discretion), but it is not a separate entry.

### Bringing `main` in, and the PR at close

- **D-06: The milestone branch does not absorb `main` in this phase; Phase 67 D-04 carries forward unchanged.** No `origin/main` → milestone merge commit and no local re-provisioning against `main`'s lock inside Phase 69. SC#3's green is proven on this phase's own tip; the merged tree is linted under `ruff` 0.16.x by the PR's own required checks at `/gsd-complete-milestone`.

- **D-07: Phase 69 records a non-committing trial-merge pre-flight as evidence.** Re-run at execution time and transcribe verbatim — `git fetch origin`, `git merge-tree --write-tree HEAD origin/main` (exit code and tree SHA), and `uv lock --check` against that tree's `pyproject.toml` + `uv.lock` extracted to scratch (for example via `git archive <tree> pyproject.toml uv.lock`). Optionally also `ruff check .` at the merged lock's `ruff` version over the merged tree inside the FHS runner (Phase 67's `typsphinx-fhs-run uvx --from ruff==X` pattern). Nothing from this pre-flight is committed to the branch; it exists so the handoff's update step is known conflict-free with a valid lock before the operator reaches it.

- **D-08: `69-HANDOFF.md` includes the branch-update step, required by `main`'s strict protection.** In order: merge `origin/main` into the canonical milestone branch with a merge commit (never a rebase of the milestone's commits), push, open the PR from `gsd/v0.9.3-toolchain-and-dependency-update-repair` to `main`, wait for all six required checks (named literally as listed in the domain section) to be green on the updated head, then merge with a merge commit — the method every prior milestone PR used (#135, #136 measured as "Merge pull request" commits on `main`'s first-parent history). The handoff states the reason the update is mandatory (`strict: true`), and that the post-update `ruff` is the merged lock's version (0.16.x), consistent with NIX-01 per Phase 67 D-03.

- **D-09: `69-HANDOFF.md` opens by stating the negative.** Its first lines say this milestone publishes nothing — no tag, no PyPI upload, no GitHub Release, no version bump — and that the `typsphinx-doc-translations` `update-pin.yml` dispatch and the Read the Docs `stable` verification are not applicable. This is the Phase 61 shape (61-CONTEXT D-12, specifics item 3), the anomaly case where the standing publish checklist must not be followed out of habit.

### Items the handoff records without acting

- **D-10: The open dependabot PRs #139..#142 are named in `69-HANDOFF.md` and left untouched.** No merge, close, rebase request or comment in this phase or as part of REL-12. They were deferred by Phase 67 as outside DEP-05's text; the handoff notes only that they target `main` and dependabot will rebase them once REL-12 changes `uv.lock`.

- **D-11: The `0.9.3` version number is recorded as unclaimed, not decided.** No `v0.9.3` tag exists and none is created, so whether the next published release is `0.9.3` or skips it belongs to the next milestone's scoping. `69-HANDOFF.md` states this and that the next release-prep phase promotes D-01's bullets into its versioned section (the Phase 61 → 63 mechanism).

### Mechanics that bind every plan

- **D-12: The fence is `69-CLOSEOUT-GUARD.md`, reusing the `61-CLOSEOUT-GUARD.md` / `63-CLOSEOUT-GUARD.md` procedure.** `sha256sum`, `wc -l`, `git rev-parse HEAD` as `PHASE_BASE_SHA`, and `grep -n 'REL-12' .planning/REQUIREMENTS.md` recorded at phase head; re-run and MATCH at phase close; and once more after `phase.complete`-family tooling runs (including `/gsd-verify-work`'s inline transition). A flip is reverted with `git checkout -- .planning/REQUIREMENTS.md` and reported, never committed. Every plan's `SUMMARY.md` declares `requirements-completed: []`. SHA-256 is the primary probe (a flip leaves `wc -l` unchanged).

- **D-13: One CI dispatch on the phase's final tip, after the branch is pushed.** `git push origin gsd/v0.9.3-toolchain-and-dependency-update-repair` first (origin is 114 commits behind), then `gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair`, waited to completion, every job conclusion transcribed literally with both `windows-latest` lanes and `macos-latest` named, and `ruff`'s verdict read from the `Lint and Format Check` job (step `Run lint with tox`). No plan triggers `release.yml`. A second dispatch is justified only if a later plan lands a code-affecting change.

- **D-14: Before any push, re-check the decoy branch.** Constraint 9's `gsd/v0.9.3-milestone` decoy is absent today (`git branch -vv` shows only the canonical `0.9.3` branch), but the commit helper re-creates it per milestone. If it reappears, advance the canonical pointer before deleting the decoy, and push only the canonical branch.

### Claude's Discretion

- Exact prose of the three bullets, within D-01..D-05.
- Plan decomposition, waves, and evidence-file naming following the Phase 61/63 set (`69-CLOSEOUT-GUARD.md`, `69-CHANGELOG-EVIDENCE.md`, `69-GREEN-TREE-EVIDENCE.md`, `69-CI-EVIDENCE.md`, `69-HANDOFF.md`, plus a pre-flight evidence file for D-07). `69-VERIFICATION.md` is reserved for the verifier and must not be plan-authored.
- Whether the D-07 pre-flight includes the optional `ruff` run on the merged tree.
- Docs warning baselines for SC#3, provided both are taken from a clean build (`rm -rf docs/_build` first).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase contract
- `.planning/ROADMAP.md` § "Phase 69: v0.9.3 Close Prep (prep-only, unpublished)" — goal and SC#1..SC#4, read in full.
- `.planning/ROADMAP.md` § milestone constraints 7 (CI lint authority, `Lint and Format Check`), 9 (decoy branch pair), 10 (branch on origin), 11 (worktree isolation), 13 (standing invariants, no `typsphinx/` change), 14 (REL-12 checksum fence).
- `.planning/REQUIREMENTS.md` — REL-12 verbatim; § Traceability note that REL-12 is mapped here for coverage only.

### Precedent phases
- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-CONTEXT.md` — the unpublished-close shape (D-03 bullets under `## [Unreleased]`, D-04 tail block untouched, D-12 negative-first handoff).
- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-CLOSEOUT-GUARD.md` and `61-HANDOFF.md` — fence procedure and handoff structure to reuse.
- `.planning/milestones/v0.9.2-phases/63-v0-9-2-release-prep-prep-only/63-CONTEXT.md` — D-16 (three-observation fence), D-18 + Amendment 1 (single dispatch, `Lint and Format Check`), D-19 (evidence naming, `63-VERIFICATION.md` ban), D-21 (clean docs build).
- `.planning/milestones/v0.9.2-phases/63-v0-9-2-release-prep-prep-only/63-CLOSEOUT-GUARD.md` — most recent fence file, including the seventh flip and its reversion.
- `.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-CONTEXT.md` — D-03 (NIX-01 interaction after REL-12), D-04 (no `main` absorption until REL-12), deferred #139..#142.
- `.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-02-SUMMARY.md` — the #138 merge into `main` and the recorded 0.15.20 / 0.16.6 divergence.

### What the bullets describe
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/` — NIX-01..NIX-08 evidence and `64-VERIFICATION.md`.
- `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/` — TOX-01..TOX-04, `65-REVERT-EVIDENCE.md`.
- `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/` — DEP-01, DEP-03, DEP-04.
- `.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/` — DEP-02, DEP-05, `67-PROOF-EVIDENCE.md`, `67-CLOSURE-EVIDENCE.md`.
- `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/` — DOC-19..DOC-21.

### Files this phase edits or reads
- `CHANGELOG.md:8` (`## [Unreleased]`), the `### Planned for Future Releases` block below it (untouched), and `:1297` (`[Unreleased]` tail link, untouched).
- `pyproject.toml:7` — must still read `0.9.2` (read only).
- `docs/source/changelog.rst:1-2` — includes `CHANGELOG.md` via `myst_parser.sphinx_`, making the bullets published text.
- `.github/workflows/ci.yml` — `workflow_dispatch` route, 3-OS matrix, `Lint and Format Check` job; `.github/workflows/release.yml` is never triggered.
- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree `uv sync` + `uv run`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The 61/63 `CLOSEOUT-GUARD.md` procedure — the only measure that has caught the release-requirement flip; reused with REL-12 and fresh baselines.
- `git merge-tree --write-tree` + `git archive` into scratch + `uv lock --check` — measures the REL-12 merge result without touching the branch (D-07; measured working 2026-09-13).
- `typsphinx-fhs-run` (path resolvable from any shim script) — runs `uvx --from ruff==X` on NixOS for D-07's optional merged-tree lint.

### Established Patterns
- CHANGELOG vocabulary measured file-wide: `### Fixed` 20, `### Added` 14, `### Changed` 11, `### Verified` 10, `### Removed` 5; tooling-only work has historically been bold-lead bullets under `### Changed` / `### Added`.
- Evidence transcribed verbatim in `{padded_phase}-{TOPIC}-EVIDENCE.md`; `KEY = value` bare lines with no trailing prose when a verify step `sed`-extracts them.
- Remote probes (tag, PyPI, GitHub Release) each carry a positive control against an existing release (`v0.9.2`).

### Integration Points
- `CHANGELOG.md` is the only product-tree file whose content this phase authors; everything else lands under `.planning/phases/69-*/`.
- `docs-html` and `docs-pdf` consume `CHANGELOG.md`, so a malformed MyST bullet shows as a new docs warning against the clean-build baseline.
- `tests/test_changelog_page_gate.py`'s build classes need `myst_parser` (the `docs` extra) and skip in a `--extra dev` worktree venv; `RELEASE_VERSIONS` is not extended (no release section), but a green worktree `pytest` alone does not prove the changelog page renders — the docs tox environments or CI do.

</code_context>

<specifics>
## Specific Ideas

- Draft bullet shape for D-01 (wording at discretion): "**Contributor tooling returns to `tox-uv` (TOX-01, TOX-02, TOX-03, TOX-04)** — … No effect on installing or using typsphinx."
- `phase.complete` has flipped the release requirement at seven consecutive release-prep closes, and `/gsd-verify-work` reaches it too via its inline transition; back up REQUIREMENTS / ROADMAP / STATE to scratch before either runs.
- The main-checkout `uv sync --extra dev` drops the `docs` extra; restore with `--extra dev --extra docs` before running the docs tox environments from the main checkout.

</specifics>

<deferred>
## Deferred Ideas

- Disposition of dependabot PRs #139..#142 — after REL-12, as ordinary dependency maintenance (D-10).
- Choosing whether the next published release is `0.9.3` — next milestone's scoping (D-11).
- `PROJECT.md`'s superseded claim that #123/#128 "will need closing so the `uv` ecosystem opens fresh ones" (67-CONTEXT specifics) — for the milestone-close `PROJECT.md` update, not this phase.

### Reviewed Todos (not folded)
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — docs structure; unrelated to close prep.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — new CI workflow; constraint 3.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — `typsphinx/` source change; constraint 13 and `CLAUDE.md`.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` — translator defect; constraint 13.
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` — `typsphinx/` change; constraint 13.

</deferred>

---

*Phase: 69-v0-9-3-close-prep-prep-only-unpublished*
*Context gathered: 2026-09-13*
