# Phase 73: v0.9.5 Close Prep (prep-only, unpublished) - Research

**Researched:** 2026-09-14
**Domain:** Milestone close-prep procedure (git/gh evidence gathering, CHANGELOG editing, no runtime code) — the fourth consecutive milestone to use this exact phase shape (v0.8.0 Phase 52, v0.9.0 Phase 57, v0.9.1 Phase 61, v0.9.2 Phase 63, v0.9.3 Phase 69, v0.9.4 Phase 71, now v0.9.5 Phase 73)
**Confidence:** HIGH — this phase has direct, complete precedent (Phase 71, one milestone earlier) executed under an almost-identical CONTEXT, plus a second precedent (Phase 69) for the "no `typsphinx/` change" fence shape this phase also needs. Every command below was either read from a committed evidence file this session or re-run live against the current tree.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01: Two bullets, each under a new subsection that follows the house order of the released sections.**
- **`### Added`** is inserted directly after `## [Unreleased]`, before the existing `### Changed`. It holds one bullet: the new `tox -e linkcheck` environment (QUA-13, DOC-24).
- **`### Fixed`** is inserted after the last `### Changed` bullet, before `### Planned for Future Releases`. It holds one bullet: the docs sidebar fix (DOC-18).

The result reads `### Added` -> `### Changed` -> `### Fixed` -> `### Planned for Future Releases`, the order `[0.9.0]` and `[0.8.0]` use. Blank-line spacing matches the existing `### Changed` block: a blank line after each heading and between bullets.

**D-02: Both bullets follow the register of the four `### Changed` bullets.**
- Each opens with a bold lead phrase that ends with the requirement IDs in trailing parentheses.
- Each is prose written for a reader of the published changelog page, because `docs/source/changelog.rst` includes `CHANGELOG.md`.
- Each carries one plain sentence saying it has no effect on installing or using typsphinx.
- Each carries at most one evidence sentence.
- Neither names `v0.9.3`, `0.9.3`, `v0.9.4`, `0.9.4`, `v0.9.5` or `0.9.5` anywhere, because no release carries those numbers.
- Neither mentions the Japanese site or its catalogs (Phase 71 D-02).

**D-03: The linkcheck bullet (`### Added`) makes three points.** `tox -e linkcheck` runs Sphinx's link check over the documentation sources, including `#anchor` targets; it needs the network and is not part of a plain `tox` run; it is contributor tooling. It must not claim, imply or foreshadow any CI job, scheduled run or required check (REL-14; QUA-08 is deferred). It carries no link count, because the count moves with the docs and constraint 8 forbids hard-coding it.

**D-04: The sidebar bullet (`### Fixed`) makes these points.** In the HTML documentation, each User Guide and Examples page now appears once in the sidebar, nested under its section, instead of also being listed a second time beside it. Its one evidence sentence may say either or both of: Sphinx no longer reports those pages as referenced in multiple toctrees; the PDF still includes each page exactly once. It does not enumerate the five pages' paths or cite build counts. It must not claim the fix is visible on the default (`stable`) documentation, which stays on `v0.9.2` until the next published release (constraint 5).

**D-05: Everything else in `CHANGELOG.md` is byte-identical.** That covers the four `### Changed` bullets (including their heading line), `### Planned for Future Releases`, every versioned section, and the tail link block. The diff adds lines and removes none. The `[Unreleased]` compare base stays `v0.9.2`. No `### Verified` subsection and no lead paragraph are added (Phase 69/71 D-04). No versioned heading or tail link is created, and `scripts/extract_changelog_section.py` is not run for a new section. `CHANGELOG.md` is the only product-tree file this phase authors.

**D-06: #146-#150 are left untouched during this phase and named in `73-HANDOFF.md`.** They are merged **after** the milestone PR, the order v0.9.3 used (#143, then #142 and #141). This phase neither merges, rebases, comments on nor closes any of them. The handoff lists each one by number, package and version range, and states that the order is: milestone PR first, Dependabot second.

**D-07: If `main` moves anyway before execution, the standing mechanism handles it.** SC#3's non-committing trial merge (D-09) catches it, and a `ruff` bump's verdict on the merged tree is authoritative. The handoff's branch-update step (D-10) is then live rather than a no-op. Plans do not add a docs build of the merged tree for #150 — that would go beyond SC#3, which names `uv lock --check` and `ruff check .` only.

**D-08: The fence is `73-CLOSEOUT-GUARD.md`, reusing the 69/71 procedure.** Records `sha256sum`/`wc -l`/`PHASE_BASE_SHA`/`grep -n 'REL-14'` at phase head; re-verified at close, and once more after `phase.complete`-family tooling. Primary probe: SHA-256 (a flip leaves `wc -l` unchanged). On a flip: reverted with `git checkout --`, never committed. Every plan's `SUMMARY.md` declares `requirements-completed: []`; no plan writes `.planning/REQUIREMENTS.md`. Back up REQUIREMENTS, ROADMAP and STATE to scratch before `phase.complete`/`/gsd-verify-work` runs.

**D-09: SC#3's trial merge is non-committing** (Phase 71 D-05): `git fetch origin`; `git merge-tree --write-tree HEAD origin/main`; `git archive <tree> pyproject.toml uv.lock` into scratch, then `uv lock --check`; `ruff check .` on the merged tree. Nothing is committed. `main`'s protection is read and must equal the six contexts read at Phase 72's base, with `strict: true`.

**D-10: `73-HANDOFF.md` is structured like Phase 71's, negative first.** Publishes nothing; `update-pin.yml` and RTD `stable` are **not applicable**. A conditional branch-update step (merge commit only, never rebase, only if `origin/main` moved); open the PR; wait for the six required checks named literally; merge with a merge commit; then the Dependabot PRs. REL-14 is checked on five post-merge observations only.

**D-11: Version numbers `0.9.3`, `0.9.4` and `0.9.5` are recorded as unclaimed, not decided.** The next release-prep phase promotes all bullets under `## [Unreleased]` into its versioned section.

**D-12: One CI dispatch on the phase's final tip, after the push** (Phase 71 D-10): re-run the decoy census first; push only the canonical branch; `gh workflow run CI --ref ...`; wait for completion; transcribe every job conclusion literally, naming both `windows-latest` and both `macos-latest` lanes, and reading `ruff`'s verdict from `Lint and Format Check`. No plan triggers `release.yml`.

**D-13: SC#1's code-invariant probe is the milestone-wide diff.** `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` must be empty on the close tip. No masked-AST harness is needed. Remote probes each carry a positive control against `v0.9.2`: tags (both `git tag -l` and `git ls-remote --tags`), PyPI, GitHub Releases for all three unpublished version numbers.

**D-14: SC#3's docs runs follow Phase 72's rules.** Clean builds under `LC_ALL=C` (`rm -rf` first); warning baseline taken at this phase's own base, expected **zero** `multiple toctrees` at both base and tip, positive-controlled by Phase 72's `BASE_MULTI_TOCTREE_COUNT = 5`; linkcheck runs clean, `working` count equals total, non-`working` rows follow Phase 72 D-01..D-03 (transient re-run, max three runs; anything else stops and goes to the owner); the CHANGELOG page gate's zero-skip reading is taken only where the `docs` extra is present (main checkout re-syncs with `--extra dev --extra docs`).

**D-15: The UI-gate false positive is handled with `--skip-ui` at plan time** (Phase 72 D-09). No UI hint line is added to the ROADMAP.

### Claude's Discretion

- The exact prose of both bullets, within D-02..D-04.
- The requirement IDs in each bullet's trailing parentheses. The default is `(QUA-13, DOC-24)` for the linkcheck bullet and `(DOC-18)` for the sidebar bullet. REL-14 is not cited in a bullet.
- Plan decomposition, waves and evidence-file naming, following the Phase 71 set: `73-CLOSEOUT-GUARD.md`; `73-CHANGELOG-EVIDENCE.md`; `73-PREFLIGHT-EVIDENCE.md`; `73-GREEN-TREE-EVIDENCE.md`; `73-CI-EVIDENCE.md`; `73-HANDOFF.md`; an SC#1 invariants file. `73-VERIFICATION.md` is reserved for the verifier and must not be authored by a plan. Evidence is written as bare `KEY = value` lines wherever a verify step extracts them.

### Deferred Ideas (OUT OF SCOPE)

- Choosing the next published version number (`0.9.3`, `0.9.4`, `0.9.5` or other) belongs to the next milestone's scoping (D-11).
- A docs build of `main` + #150 (`sphinx-autodoc-typehints` 3.13.6). Under D-06 this runs as that PR's own checks after the milestone merge, not in this phase.
- Reviewed-but-not-folded todos: the QUA-08 scheduled CI workflow (needs a workflow file, forbidden by constraint 3); NUM-01, MSG-06, TRN-01 (all `typsphinx/` changes, forbidden by constraint 2).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-14 | Close prep only, unpublished. CHANGELOG bullet(s) go under the existing `## [Unreleased]`, in the register of the four bullets already there, naming the docs sidebar fix and the new `tox -e linkcheck` environment. `pyproject.toml` stays `0.9.2`. No tag, no PyPI upload, no GitHub Release. The milestone branch is merged to `main` through a PR, as REL-12/REL-13 were. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, never by phase-completion tooling. | Patterns 1-3 (CHANGELOG pure-addition proof, trial merge, SHA-256 closeout guard) give the mechanical proof for every sub-clause except the merge itself; `73-HANDOFF.md`'s recommended content (Recommended Plan Decomposition, plan 73-07) is the artifact that hands the actual merge to `/gsd-complete-milestone`; the Validation Architecture table maps REL-14's non-code-testable nature to the SC#1..SC#4 observable contract this phase's plans actually discharge. |

</phase_requirements>

## Summary

Phase 73 packages v0.9.5 for a merge to `main` and takes no irreversible action. It does four things: add two new CHANGELOG subsections (`### Added`, `### Fixed`) under `## [Unreleased]`, prove the tree is unpublished-shaped and green using runs executed in this phase, hold REL-14's checkbox at `[ ]` behind a SHA-256 fence, and write a standalone `73-HANDOFF.md`. This is not new territory: Phase 71 (v0.9.4's close prep, one milestone earlier) did the identical four things under the identical binding constraints, with the identical checksum-fence hazard, and its seven plans, evidence files and closing handoff are a working, reusable procedure — not a pattern to rediscover.

Four things differ from Phase 71 and need explicit handling in the plan: (1) two new CHANGELOG subsections instead of one bullet appended to an existing subsection — mechanically a two-hunk pure-addition instead of Phase 71's one-hunk addition, but the same test surface (`test_changelog_page_gate.py`, `extract_changelog_section.py`) is provably indifferent to subsection names, confirmed by reading both files this session; (2) `tox -e linkcheck` is now a real environment (added in Phase 72) and its SC#3 run must happen fresh in this phase, following Phase 72's own D-01..D-03 failure-classification policy; (3) the docs-warning baseline must show **zero** `multiple toctrees` messages at both base and tip (Phase 72 fixed the defect; Phase 72's own pre-fix count of 5 is the positive control that the `LC_ALL=C` grep actually works); (4) five open, all-green Dependabot PRs sit on `main` untouched, to be listed in the handoff and merged after the milestone PR, per owner decision (D-06). A fifth axis — the SC#1 tree-invariant proof — is actually *simpler* than Phase 71's: because `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` is empty for this whole milestone (Phase 72 changed only `tox.ini`, three doc-listing files, and `docs/source/index.rst`), Phase 73 needs Phase 69's lightweight "scoped diff + widened-diff positive control" shape, not Phase 71's masked-AST re-run (Phase 71 had to prove *behavioral* identity because Phase 70 rewrote type annotations; Phase 73 has nothing under `typsphinx/` to re-prove).

**Primary recommendation:** Reuse Phase 71's 7-plan / 4-wave decomposition verbatim in shape (CHANGELOG+base-docs plan / closeout-guard-baseline plan in wave 1; local-green-tree plan / CI-dispatch plan / trial-merge-preflight plan in wave 2; SC1-invariants plan in wave 3; closeout-guard-reverify + HANDOFF plan in wave 4), folding in the four deltas above at the exact points Phase 71 and Phase 72 already demonstrate them (linkcheck goes into the same plan as the full pytest suite and docs builds; the two-subsection CHANGELOG edit and its zero-`multiple-toctrees` base build go into wave 1's CHANGELOG plan; the Dependabot census goes into the trial-merge plan, exactly where Phase 71 put its own empty census).

## Architectural Responsibility Map

This phase touches no application architecture — it is a release-process phase operating on repository metadata and CI/VCS state. The "tiers" below are process tiers, not runtime tiers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CHANGELOG content authoring | Repository metadata (git-tracked prose) | Docs build (MyST render via `changelog.rst`) | `CHANGELOG.md` is the single source; `docs/source/changelog.rst` only `:parser: myst_parser.sphinx_`-includes it, so authoring happens once and both HTML/PDF consume it identically |
| Unpublished-shape proof (tags/PyPI/Releases) | GitHub/PyPI remote state (read-only probes) | Local git (tag/branch state) | These are external services this phase only reads; no phase action writes to them |
| Green-tree proof (pytest/lint/type/docs/linkcheck) | Local worktree execution | CI (`ci.yml` via `workflow_dispatch`) | Local runs give fast, foreground feedback; CI is the authoritative lint/matrix verdict per ROADMAP constraint 8 |
| Trial-merge proof against `origin/main` | Local git object store (`merge-tree --write-tree`, non-committing) | `uv`/`ruff` toolchain on the merged tree | Nothing is pushed or committed; the merge result is materialized into scratch only |
| REL-14 checkbox fence | `.planning/REQUIREMENTS.md` (read-only guard) | `phase.complete`/`/gsd-verify-work` tooling (the thing being fenced against) | The checkbox is state this phase must NOT change; the guard exists because the tooling has flipped it unbidden 8 of 9 prior times |
| Handoff instructions for the actual merge | `73-HANDOFF.md` (standalone doc) | `/gsd-complete-milestone` (the consumer) | The one irreversible action (REL-14, the PR+merge) is deliberately deferred out of this phase entirely |

## Standard Stack

No new library, runtime dependency, or Python package is introduced by this phase (ROADMAP constraint 2: zero lines under `typsphinx/`; D-05: "`CHANGELOG.md` is the only product-tree file this phase authors"). The "stack" here is the existing toolchain this project already pins.

### Core (already pinned; verify versions fresh at execution, per constraint 8)
| Tool | Verified-this-session version | Purpose | Why standard here |
|------|------|---------|--------------|
| `uv` | 0.12.13 (Phase 72's worktrees, `[VERIFIED: 72-BASE-EVIDENCE.md]`) | Provisions per-worktree `.venv`, runs `uv lock --check` on the merged tree | CLAUDE.md's mandatory worktree provisioning route |
| `git` | host-installed | `merge-tree --write-tree`, tag/branch/diff probes | Every SC#1/SC#3 proof is a git primitive, not a custom script |
| `gh` CLI | host-installed | PR/release/workflow/branch-protection reads and the one `workflow_dispatch` | All GitHub-side observation in this phase is read-only or a single dispatch |
| `ruff` | 0.16.6 pinned in `uv.lock` (`[VERIFIED: uv.lock via grep this session showed ruff==0.16.6 unchanged from Phase 72]`) | Lint verdict, both locally and on the merged-tree trial | CI holds lint authority (constraint 8); local run is additive |
| `black`, `mypy`, `pytest`, `tox` | pinned in `uv.lock`/`pyproject.toml` | Format/type/test/env-runner gates | Unchanged this phase — no `pyproject.toml` edit expected |

### Package Legitimacy Audit

**Not applicable.** This phase installs no new package in any ecosystem. `73-CONTEXT.md` D-05 states `CHANGELOG.md` is the only product-tree file this phase authors, and ROADMAP constraint 2 forbids any `typsphinx/` change. The five open Dependabot PRs (#146–#150) touch `uv.lock` only and are explicitly left untouched by this phase (D-06) — their own legitimacy was already established by Dependabot itself opening them against the existing `uv.lock`-pinned versions; this phase takes no action on them beyond recording their existence in the handoff.

## Architecture Patterns

### System Architecture Diagram

```
                         ┌─────────────────────────────┐
                         │  Wave 1 (parallel, no deps)  │
                         └─────────────────────────────┘
  CHANGELOG plan (73-01)                         CLOSEOUT-GUARD-baseline plan (73-02)
  ┌──────────────────────────────┐               ┌───────────────────────────────────┐
  │ pre-edit clean docs baseline │               │ sha256sum + wc -l + grep REL-14     │
  │  (0 multiple-toctrees,       │               │  at phase head -> 73-CLOSEOUT-GUARD │
  │   N warnings, positive       │               │ SC#1 observation 1 of 2 (tags/PyPI/ │
  │   control = Phase 72's 5)    │               │  Release/version-line probes)       │
  │        ↓                     │               └───────────────────────────────────┘
  │ insert ### Added, ### Fixed  │
  │ (two-hunk pure addition)     │
  │        ↓                     │
  │ post-edit clean docs rebuild │
  │  (same 0 / same N: MATCH)    │
  └──────────────────────────────┘
              │                                              │
              ▼                                              ▼
     ┌───────────────────────────────────────────────────────────────┐
     │                    Wave 2 (parallel, depends on wave 1)       │
     └───────────────────────────────────────────────────────────────┘
  GREEN-TREE plan (73-03)         CI plan (73-04)          PREFLIGHT plan (73-05)
  ┌───────────────────────┐   ┌───────────────────────┐  ┌───────────────────────────┐
  │ full pytest x2         │   │ decoy census           │  │ git fetch + merge-tree     │
  │ (default + LC_ALL=C)   │   │ push canonical branch  │  │  --write-tree (non-commit) │
  │ black/mypy/ruff local  │   │ gh workflow run CI     │  │ uv lock --check on merged  │
  │ version-sync family    │   │ observe to completion  │  │ ruff check . on merged     │
  │ changelog-page gate    │   │ transcribe every job   │  │ main protection read       │
  │  (0 skipped, docs      │   │  incl. both windows +  │  │ merge-method precedent     │
  │   extra present)       │   │  both macos lanes      │  │ Dependabot #146-150 census │
  │ docs-html/docs-pdf     │   └───────────────────────┘  │  (recorded, untouched)     │
  │  clean rebuild on      │                              └───────────────────────────┘
  │  final tree            │
  │ tox -e linkcheck       │
  │  (D-01..D-03 policy)   │
  └───────────────────────┘
              │                          │                            │
              └──────────────┬───────────┴────────────┬───────────────┘
                              ▼                                        ▼
                 ┌─────────────────────────────────────────────────────────┐
                 │           Wave 3 (depends on all of wave 1+2)           │
                 └─────────────────────────────────────────────────────────┘
                      SC1-INVARIANTS plan (73-06)
                 ┌───────────────────────────────────────────┐
                 │ Observation 2 of 2 (tags/PyPI/Release/     │
                 │  version-line probes, repeated)            │
                 │ typsphinx/ + .github/workflows/ scoped     │
                 │  diff (empty) + widened-diff positive ctrl │
                 │  (Phase 69 shape — NOT masked-AST)         │
                 │ commits-after-CI-dispatch product-file     │
                 │  count = 0                                 │
                 └───────────────────────────────────────────┘
                              │
                              ▼
                 ┌─────────────────────────────────────────────────────────┐
                 │           Wave 4 (depends on everything above)          │
                 └─────────────────────────────────────────────────────────┘
                    CLOSEOUT-GUARD-reverify + HANDOFF plan (73-07)
                 ┌───────────────────────────────────────────┐
                 │ re-run guard probes at phase close (MATCH) │
                 │ write 73-HANDOFF.md (negative-first,       │
                 │  conditional branch-update, 6-check wait,  │
                 │  merge-commit, REL-14 5-observation close) │
                 │ fence observation over typsphinx/tests/    │
                 └───────────────────────────────────────────┘
                              │
                              ▼
                 [Orchestrator: phase.complete / /gsd-verify-work]
                              │
                              ▼
                 OBSERVATION 3 (outside any plan): re-run guard probes
                 after phase.complete-family tooling; revert-and-report
                 if REQUIREMENTS.md flipped; NEVER commit a flip.
```

### Recommended Project Structure (evidence files, following Phase 71's naming — Claude's Discretion in 73-CONTEXT.md)
```
.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/
├── 73-01-PLAN.md / 73-01-SUMMARY.md   # CHANGELOG bullets + docs pure-addition proof
├── 73-02-PLAN.md / 73-02-SUMMARY.md   # CLOSEOUT-GUARD baseline + SC1 observation 1 + COVERAGE.md
├── 73-03-PLAN.md / 73-03-SUMMARY.md   # local green-tree: pytest x2, lint trio, version-sync,
│                                        #  changelog gate, docs-html/pdf, tox -e linkcheck
├── 73-04-PLAN.md / 73-04-SUMMARY.md   # decoy census, push, CI dispatch + full job transcript
├── 73-05-PLAN.md / 73-05-SUMMARY.md   # trial merge, merged-tree lint, main protection,
│                                        #  merge-method precedent, Dependabot census
├── 73-06-PLAN.md / 73-06-SUMMARY.md   # SC1-INVARIANTS: observation 2, typsphinx/.github fence
├── 73-07-PLAN.md / 73-07-SUMMARY.md   # guard re-verification at close + 73-HANDOFF.md
├── 73-CHANGELOG-EVIDENCE.md
├── 73-CLOSEOUT-GUARD.md
├── 73-GREEN-TREE-EVIDENCE.md
├── 73-CI-EVIDENCE.md
├── 73-PREFLIGHT-EVIDENCE.md
├── 73-SC1-INVARIANTS.md
├── 73-HANDOFF.md
├── COVERAGE.md
└── 73-VERIFICATION.md                 # verifier-authored; no plan may write this file
```

### Pattern 1: Pure-addition CHANGELOG edit, proven mechanically (not by inspection)
**What:** Insert new content under `## [Unreleased]` while proving every other byte of `CHANGELOG.md` is unchanged.
**When to use:** Any release-prep phase adding CHANGELOG content to an unpublished milestone.
**Phase 73's shape differs from Phase 71's in hunk count, not in method.** Phase 71 inserted one bullet into the existing `### Changed` list — a single hunk, 10 added lines, 0 removed. Phase 73 (per D-01) inserts **two new subsections** at two different points (`### Added` right after `## [Unreleased]`, before `### Changed`; `### Fixed` right after the last `### Changed` bullet, before `### Planned for Future Releases`) — this will be **two hunks** in `git diff -U0`, not one. The proof pattern from Phase 71 generalizes directly:
```bash
# Source: 71-CHANGELOG-EVIDENCE.md "Pure-addition proof" + "Fence assertions", adapted for two hunks
git diff --numstat "$BASE_73_01" -- CHANGELOG.md   # expect: N added, 0 removed
git diff -U0 "$BASE_73_01" -- CHANGELOG.md | grep -c '^@@'   # expect: 2 (two insertion points)
grep -cE '^## \[' CHANGELOG.md                      # unchanged before/after (23)
grep -cE '^\[[^]]+\]: https' CHANGELOG.md            # unchanged before/after (23)
awk '/^### Planned for Future Releases$/{f=1} /^## \[0\.9\.2\]/{exit} f' CHANGELOG.md | sha256sum  # unchanged
tail -n 1 CHANGELOG.md                               # still "[Unreleased]: .../compare/v0.9.2...HEAD"
grep -cF 'compare/v0.9.2...HEAD' CHANGELOG.md         # 1
grep -cE '0\.9\.[345]' CHANGELOG.md                   # 0 — no version literal anywhere
```
**New assertion Phase 73 needs that Phase 71 didn't:** confirm the four existing `### Changed` bullets are byte-identical (Phase 71 didn't need this because it inserted *into* that same subsection — Phase 73 must prove the block it does NOT touch is untouched even though two *new* sibling subsections are added around it):
```bash
awk '/^### Changed$/{f=1} /^### Fixed$/{exit} f' CHANGELOG.md | sha256sum
# compare against the pre-edit sha256 of the same awk range
```

### Pattern 2: Non-committing trial merge against `origin/main`
**What:** Prove a future real merge of `origin/main` would be conflict-free and pass `uv lock --check` + `ruff check .`, without touching the branch.
**When to use:** SC#3's trial-merge requirement, every release-prep phase since Phase 71 (D-09/D-05 lineage).
**Example (from `71-PREFLIGHT-EVIDENCE.md`, re-verified live this session — `origin/main` is still exactly the milestone base `098a8ff6`, so this is expected to reproduce a no-op today):**
```bash
git fetch origin
git merge-tree --write-tree HEAD origin/main; echo "exit:$?"   # exit 0 + a tree SHA = conflict-free
git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"  # exit 0 = main hasn't moved past base
mkdir -p "$SCRATCH/lock_scratch"
git archive --format=tar -o "$SCRATCH/lock.tar" "$MERGE_TREE" pyproject.toml uv.lock
tar -xf "$SCRATCH/lock.tar" -C "$SCRATCH/lock_scratch"
uv --directory "$SCRATCH/lock_scratch" lock --check; echo "exit:$?"
# separately, full-tree archive + hash-verified sync + ruff/black:
git archive --format=tar -o "$SCRATCH/lint.tar" "$MERGE_TREE"
tar -xf "$SCRATCH/lint.tar" -C "$SCRATCH/lint_scratch"
uv --directory "$SCRATCH/lint_scratch" sync --locked --extra dev --no-install-project
uv --directory "$SCRATCH/lint_scratch" run --no-sync ruff check .; echo "exit:$?"
```
**Today's live state (measured this session, 2026-09-14):** `origin/main` = `098a8ff64cf008822eef9dc69f75102ded3f7bc1`, exactly the milestone base. `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` is empty. Five Dependabot PRs are open and MERGEABLE but not yet on `main`. The trial merge Phase 73 runs at execution time will very likely again be a same-tree no-op (`TRIAL_IS_NOOP = yes` in Phase 71's terms), **unless** a Dependabot PR merges to `main` between now and execution — which the plan cannot assume either way and must re-measure fresh (constraint 8; D-07).

### Pattern 3: SHA-256 closeout-guard fence with three re-verification points
**What:** Guard a single requirement's checkbox against `phase.complete`-family tooling's historical habit of flipping it.
**When to use:** Every release-prep final phase in this project (constraint 10; 8 of 9 prior closes flipped the checkbox before this guard existed/matured; it held for the first time at Phase 61, and held again at Phase 71).
**Example, condensed from `71-CLOSEOUT-GUARD.md`:**
```bash
# At phase head (73-02):
sha256sum .planning/REQUIREMENTS.md   # -> REQ_SHA256_BASE
wc -l .planning/REQUIREMENTS.md       # -> REQ_LINES_BASE
git rev-parse HEAD                    # -> PHASE_BASE_SHA
grep -n 'REL-14' .planning/REQUIREMENTS.md   # verbatim, classify state-bearing vs informational lines

# At phase close (73-07), before phase.complete:
# re-run all four commands above; expect byte-identical MATCH against the baseline

# Backup before phase.complete/gsd-verify-work run (outside the repo):
cp .planning/{REQUIREMENTS,ROADMAP,STATE}.md /tmp/scratch-73-closeout/

# After phase.complete/gsd-verify-work run (the orchestrator's own observation, outside any plan):
# re-run all four commands again; if REQ_SHA256 no longer matches:
git checkout -- .planning/REQUIREMENTS.md   # revert, never commit the flip
# then re-run and confirm MATCH; diff ROADMAP.md/STATE.md against the scratch backup too
```
**Why SHA-256 and not just `wc -l`:** a `- [ ]` -> `- [x]` flip is line-count-neutral; only a byte-level digest catches it. Phase 63 also showed the flip can move **three** requirement IDs in one edit — the whole-file digest catches any writer of `.planning/REQUIREMENTS.md`, not just a scoped grep on `REL-14`.

### Pattern 4: `tox -e linkcheck` failure classification (D-01..D-03, new to this phase's SC#3)
**What:** Run `tox -e linkcheck` fresh on the final tree and classify any non-`working` row before declaring PASS.
**When to use:** Any phase from Phase 72 onward that needs a clean linkcheck verdict.
**Example, from `72-LINKCHECK-EVIDENCE.md` / `72-GATES-EVIDENCE.md`, directly reusable:**
```bash
rm -rf docs/_build/linkcheck
uv run tox -e linkcheck > "$SCRATCH/lc_run1.log" 2>&1; echo "exit:$?"
python3 -c "
import json
rows = [json.loads(l) for l in open('docs/_build/linkcheck/output.json') if l.strip()]
total = len(rows)
working = sum(1 for r in rows if r.get('status') == 'working')
print(f'total={total} working={working}')
for r in rows:
    if r.get('status') != 'working':
        print(r)
"
```
D-01 (72-CONTEXT.md): a non-`working` row that looks transient (network hiccup) is re-run from a clean output directory, **at most three runs total**. D-02: a `conf.py` `linkcheck_*` key (timeout/retries) is added only if the *same URL* fails transiently across two or more runs, with a comment naming the measured failure. D-03: anything not transient (a genuinely dead link/anchor) **stops the phase and goes to the owner** — it is not silently ignored. Phase 72's own run needed none of this (95/95 working on the first try); Phase 73 must re-measure fresh, since D-03 (73-CONTEXT) explicitly forbids hard-coding a link count into the CHANGELOG bullet.

### Anti-Patterns to Avoid
- **Hard-coding any count from this research or from Phase 72's evidence into a CHANGELOG bullet, a plan's verify step, or a checkpoint condition.** Constraint 8 is explicit: link-`working` counts, `multiple toctrees` counts, warning counts, and required-context sets are all "measured fresh, never hard-coded." This RESEARCH.md's numbers (95 links, 5 pre-fix `multiple toctrees` messages, 3 docs warnings, 6 required contexts, `098a8ff6` as milestone base) are **context for planning**, not values a plan may assert without re-measuring.
- **Running `scripts/extract_changelog_section.py` for this phase's edit.** It extracts a `## [X.Y.Z]` heading's body; no such heading exists or should exist here (D-05). Both Phase 69 and Phase 71's evidence explicitly record this script was *not* run.
- **Anchoring a `sed`/grep at pytest's collection summary line's start-of-line.** `pytest --collect-only -q`'s last line is padded with `=` decoration; use `grep -oE '[0-9]+ (passed|tests? collected)'` instead (documented project hazard, see memory: `plan-verify-oracle-format-traps`).
- **Treating a `gh workflow run` HTTP 5xx as "no run created."** Phase 71's own CI dispatch hit exactly this: a "failed" call had actually created a run server-side, and a naive retry created a second (`DISPATCH_COUNT` note in `71-HANDOFF.md`). Before retrying, run `gh run list --workflow=ci.yml --branch <branch> --event workflow_dispatch` and look for a row at the just-pushed SHA.
- **Running the full pytest suite, `tox -e docs-*`, or `tox -e linkcheck` from the research/planning session.** Per this run's own ground rules and constraint 8, these gates must be executed **fresh, by the phase's own plans, inside their own worktrees** — a research-time run proves nothing binding and this session deliberately did not attempt one.
- **Assuming a fresh worktree's `uv sync --extra dev` alone gives a zero-skip changelog-gate reading.** It omits the `docs` extra (`myst-parser`); `--extra dev --extra docs` is required (constraint 12, D-14).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting whether a merge would conflict, without merging | A custom three-way-diff script | `git merge-tree --write-tree <head> <origin/main>` | Git's own plumbing command; exit code + tree SHA are the complete, reproducible answer (`71-PREFLIGHT-EVIDENCE.md` demonstrates idempotency: running it twice on the same inputs prints the same tree SHA) |
| Checking whether `.planning/REQUIREMENTS.md` changed | A line-by-line diff heuristic or a scoped grep count | Whole-file `sha256sum` | A checkbox flip (`- [ ]` -> `- [x]`) is line-count-neutral and can move multiple requirement IDs in one edit (Phase 63 precedent); only a byte-level digest is unambiguous |
| Verifying a merged tree's dependency lock is still consistent | Manually diffing `uv.lock` | `uv lock --check` against a `git archive`-materialized scratch copy of the merged tree | This is exactly what CI's own `uv sync --locked` step would do; running it locally on the trial-merge tree is the same check, earlier |
| Extracting a GitHub Release body from CHANGELOG.md | A new ad hoc parser | `scripts/extract_changelog_section.py` (already exists, tested) — **not invoked this phase**, since no versioned section exists yet | D-05/D-08: this phase creates no `## [X.Y.Z]` heading for it to extract; the mechanism is reused unmodified at the *next* release-prep phase |
| Judging whether a linkcheck failure is worth stopping for | An automated "just retry N times and ignore" policy | The three-tier D-01/D-02/D-03 policy from Phase 72's CONTEXT (transient -> re-run; recurring-on-the-same-URL -> timing key with a comment; anything else -> stop, ask the owner) | A silent retry-and-ignore policy would let a genuinely broken link or anchor pass; this policy is already decided and reusable verbatim |

**Key insight:** every mechanism this phase needs already exists, tested, in this repository's own history from one or two milestones ago. The work here is *reuse with fresh measurement*, not invention — the single largest risk is a plan silently copying a Phase 71/72 number instead of re-running the command that produced it.

## Common Pitfalls

### Pitfall 1: Worktree `uv sync --extra dev` omits the `docs` extra, producing a false-skip on the changelog gate
**What goes wrong:** `tests/test_changelog_page_gate.py`'s `TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf` classes both skip silently when `myst_parser` is not importable — a bare `uv sync --extra dev` worktree provision gives a "6 passed" *looking* result that is actually 4 skipped, 2 run (the delegation-only class always runs).
**Why it happens:** the standing per-worktree provisioning line in CLAUDE.md is `uv sync --extra dev`; the `docs` extra is separate.
**How to avoid:** provision with `--extra dev --extra docs --python 3.13.13` (Phase 71/72's own worktrees both did this for every plan touching docs/changelog gates). In the main checkout (used only for the operator-level HANDOFF steps at `/gsd-complete-milestone`, not inside any plan), a bare `--extra dev` exact-sync **drops** the docs extra if it was previously present — re-sync with both extras named (memory: `main-checkout-uv-sync-drops-docs-extra`).
**Warning signs:** `CHANGELOG_GATE_SKIPPED` > 0 in the evidence transcript, or a pytest run showing fewer than 6 collected items for `test_changelog_page_gate.py`.

### Pitfall 2: Interpreter drift between a fresh worktree and the main checkout
**What goes wrong:** a fresh worktree's `uv sync` resolves onto uv-managed CPython (3.14 observed in memory notes), while the main checkout runs on nix-provided CPython 3.13.13 — pytest counts compared across the two are not directly comparable, and Pillow/`libz.so.1` issues have been observed under some FHS-sandboxed 3.14 environments.
**Why it happens:** the worktree's `.venv` is provisioned independently and `uv` picks whatever interpreter its own resolution logic prefers unless `--python 3.13.13` is pinned explicitly.
**How to avoid:** every provisioning command in this phase's plans should pin `--python 3.13.13` explicitly (as every Phase 71/72 plan already did — confirmed live in `71-GREEN-TREE-EVIDENCE.md`, `72-BASE-EVIDENCE.md`, `72-LINKCHECK-EVIDENCE.md`, `72-GATES-EVIDENCE.md`), and record both `.venv/pyvenv.cfg`'s `home`/`version_info` alongside every pytest count.
**Warning signs:** a pytest total that differs from the last-measured `1547 passed, 1 skipped` / `1548 tests collected` without an accompanying product-tree diff explaining why.

### Pitfall 3: Localized console text hides English-string grep hits
**What goes wrong:** the maintainer's host locale is `ja_JP.UTF-8`; a plain `grep 'document is referenced in multiple toctrees'` or `grep 'build succeeded'` against a Sphinx log produced without `LC_ALL=C` finds **zero** matches and can be misread as "the defect is fixed" or "the build succeeded" when actually the message is present but printed in Japanese.
**Why it happens:** the FHS sandbox passes the host `LANG` through unchanged (CLAUDE.md § Locale).
**How to avoid:** every docs build whose warning/message count is compared runs under `LANG=C LC_ALL=C`, and every grep against its output also runs under `LC_ALL=C`. Always pair a zero-count claim with a positive control: Phase 72's `BASE_MULTI_TOCTREE_COUNT = 5` (pre-fix) proves the same `LC_ALL=C` grep finds the message when it is genuinely present.
**Warning signs:** a docs-build evidence section with no `LC_ALL=C` prefix on its grep commands, or a "0 matches" claim with no accompanying pre-fix positive-control count nearby.

### Pitfall 4: Incremental docs rebuilds under-report warnings
**What goes wrong:** re-running `tox -e docs-html`/`docs-pdf` without first clearing `docs/_build/` can produce a lower warning count than a genuinely clean build, manufacturing a false "unchanged from baseline" match.
**Why it happens:** Sphinx's incremental build skips re-processing unchanged source files, so warnings from those files are not re-emitted.
**How to avoid:** `rm -rf docs/_build` (or the specific `docs/_build/html` / `docs/_build/linkcheck` subdirectory) immediately before every counted build — every Phase 71/72 evidence file does this and states the reason explicitly.
**Warning signs:** a warning count that doesn't match a freshly-clean-built baseline taken minutes earlier in the same plan.

### Pitfall 5: `gh workflow run` returning HTTP 5xx while still creating a run
**What goes wrong:** Phase 71 hit this directly — a "failed" `gh workflow run CI --ref ...` call returned an error, but the run had actually been created server-side; a retry created a *second* run, leaving two `workflow_dispatch` runs on the same pushed SHA (one `success`, one `cancelled`).
**Why it happens:** GitHub's Actions dispatch API is occasionally flaky on the response leg even when the mutation succeeds.
**How to avoid:** before any retry, run `gh run list --workflow=ci.yml --branch <branch> --event workflow_dispatch --limit 5 --json databaseId,headSha,status,createdAt` and check for a row at the just-pushed SHA. D-12 (73-CONTEXT) expects "exactly one dispatch" — Phase 71's owner-approved reading, if this recurs, is "exactly one *success* run at the pushed SHA," with any duplicate documented rather than deleted from Actions history.
**Warning signs:** the dispatch command's own exit code is non-zero, or its stdout does not print a run URL immediately.

### Pitfall 6: Same-wave evidence dependency across parallel worktrees
**What goes wrong:** worktrees cannot see a sibling worktree's uncommitted evidence files. A plan that needs to compare its own measurement against another wave-mate plan's evidence (e.g., "does my docs-warning count equal the pre-edit baseline recorded in the CHANGELOG plan?") will find that file absent if both plans are in the same wave.
**Why it happens:** parallel wave execution forks each plan into its own isolated worktree at the wave's start.
**How to avoid:** sequence dependency-bearing measurements into a *later* wave, exactly as Phase 71 did — the local green-tree plan (71-03/73-03) reads 71-01's/73-01's already-committed `DOCS_HTML_WARN_BASE`/`DOCS_PDF_WARN_BASE` only because 73-01 sits in wave 1 and merges before wave 2 starts.
**Warning signs:** a plan's task referencing "compare against <other-plan>'s evidence file" where both plans are declared in the same `wave:` value in frontmatter.

### Pitfall 7: `phase.complete` / `/gsd-verify-work` mangling STATE.md/ROADMAP.md incidentally, not just REQUIREMENTS.md
**What goes wrong:** Phase 71's own third observation recorded that `phase.complete` deleted `STATE.md`'s `current_phase_name` field and wrote `Plan: Not started` — a side effect distinct from (and in addition to) the REL-13/REL-14 checkbox-flip hazard.
**Why it happens:** the same tooling call rewrites multiple tracking files; not every rewrite is wrong, but some need hand-correction (e.g., ROADMAP.md's Status-cell padding).
**How to avoid:** back up all three files (`REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`) to scratch *before* either `phase.complete` or `/gsd-verify-work` runs (not just REQUIREMENTS.md), and diff all three after, per `71-CLOSEOUT-GUARD.md`'s and `71-HANDOFF.md`'s explicit instruction.
**Warning signs:** STATE.md's `Current Position` or `current_phase_name` looking stale/blank right after a completion step.

## Code Examples

### Decoy-branch census and safe push (D-12, from `72-CI-EVIDENCE.md`, reusable verbatim)
```bash
# Source: 72-CI-EVIDENCE.md "Decoy census (constraint 6)"
git branch --list 'gsd/v0.9.5*' -v
git ls-remote --heads origin 'gsd/v0.9.5*'
# If a decoy carrying commits exists: fast-forward canonical ref to it FIRST,
# re-point HEAD with git symbolic-ref, THEN delete the decoy. Never delete first.
git push --no-follow-tags -u origin gsd/v0.9.5-docs-link-check-and-navigation
gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation
```

### Observing a dispatched CI run to completion, in the foreground (from `72-CI-EVIDENCE.md`)
```bash
# Source: 72-CI-EVIDENCE.md "Run" — Bash tool timeout 590s < 600000ms cap, no run_in_background
timeout 590 gh run watch <RUN_ID> --interval 30
gh run view <RUN_ID> --json status,conclusion,workflowName,headSha,url,createdAt,updatedAt
gh run view <RUN_ID> --json jobs --jq '.jobs[] | [.name, .conclusion] | @tsv'
```
Required transcription per D-12: name both `Test Python 3.12 on windows-latest`/`Test Python 3.13 on windows-latest` and both `Test Python 3.12 on macos-latest`/`Test Python 3.13 on macos-latest` lanes explicitly, and read `ruff`'s verdict from the `Lint and Format Check` job's own log (not just its conclusion), as `72-CI-EVIDENCE.md` § "Lint through tox" does.

### Reading `main`'s branch protection, with the exact `jq` shape this project's evidence files use
```bash
# Source: 72-BASE-EVIDENCE.md / 71-PREFLIGHT-EVIDENCE.md
gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict
gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '[.contexts[]] | sort | join("|")'
gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '.contexts | length'
```
Live-measured this session (2026-09-14): `strict: true`; six contexts — `Build Package`, `Code Coverage`, `Lint and Format Check`, `Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Type Check` — matching Phase 72's own `REQUIRED_CONTEXTS_HEAD` exactly. D-09 (73-CONTEXT) requires this to still equal that same six-context set at Phase 73's own close.

### Dependabot PR census, recorded but not acted on (D-06/D-12 shape, from `71-HANDOFF.md`)
```bash
# Source: 71-HANDOFF.md "Recorded without acting" — adapt for 73's non-empty case
gh pr list --state open --json number,title,author,headRefName,baseRefName,updatedAt
```
Live-measured this session: five open PRs, all Dependabot, all `uv.lock`-only — `#146` (`build` 1.5.0->1.6.1), `#147` (`ruff` 0.16.6->0.16.7), `#148` (`pypdf` 6.14.2->6.18.0), `#149` (`twine` 6.2.0->7.0.0), `#150` (`sphinx-autodoc-typehints` 3.0.1->3.13.6, a `docs`-extra dependency). Unlike Phase 71's empty census, Phase 73's plan must record all five by number/package/version-range in `73-PREFLIGHT-EVIDENCE.md` and name them again in `73-HANDOFF.md` (D-06) — the census pattern (a `gh pr list` call plus a "no action taken" statement) is identical; only the row count differs.

## State of the Art

| Old Approach (Phase 71 / v0.9.4 close) | New Approach (Phase 73 / v0.9.5 close) | When Changed | Impact |
|--------------|------------------|--------------|--------|
| One CHANGELOG bullet appended to the existing `### Changed` list | Two NEW subsections (`### Added`, `### Fixed`) inserted at two different points around the existing `### Changed` block | This phase (D-01, owner decision 2026-09-14) | Diff is now 2 hunks, not 1; a new "is `### Changed` itself untouched" assertion is needed since it now has new siblings rather than a new tail |
| No `tox -e linkcheck` existed | `tox -e linkcheck` exists (landed Phase 72) and its SC#3 run is new to this phase | Phase 72 (2026-09-13) | SC#3's green-tree proof gains one more command, with its own D-01..D-03 failure policy already decided |
| Docs-warning baseline included 5 `multiple toctrees` messages (the still-open defect at Phase 71's time) | Docs-warning baseline must show **zero** `multiple toctrees` at both base and tip (DOC-18 fixed in Phase 72) | Phase 72 (2026-09-13) | The positive control for "the `LC_ALL=C` grep actually detects the message" must now come from Phase 72's own recorded pre-fix count (5), not from this phase's own base build |
| SC#1's product-tree invariant needed a masked-AST re-run (Phase 70 rewrote type annotations under `typsphinx/`) | SC#1's product-tree invariant needs only a scoped-diff + widened-diff positive control (Phase 69's shape) — `typsphinx/` and `.github/workflows/` are both empty since the milestone base | This phase (constraint 2; D-13) | Simpler, faster proof — no fixture-corpus manifest re-hash needed |
| Zero open PRs at close-prep time | Five open, all-green Dependabot PRs at close-prep time, explicitly deferred to post-merge (D-06) | Measured 2026-09-14 | The handoff must name and order them (milestone PR first, per v0.9.3 precedent of #143 then #142/#141) |

**Deprecated/outdated:** nothing in the toolchain itself is deprecated this phase; the "old approach" column above describes the immediately-prior milestone's close-prep artifacts, not a superseded technology.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The next `gh workflow run CI` dispatch on this phase's tip will behave the same way Phase 72's did (single clean dispatch, no HTTP 5xx) | Pitfall 5 / Code Examples | Low — the dispatch procedure already includes the re-check-before-retry mitigation regardless of outcome |
| A2 | The trial merge against `origin/main` will again be a no-op (`origin/main` unchanged from milestone base) at the time Phase 73's plans actually execute | Pattern 2 | Medium — if a Dependabot PR merges to `main` between this research and execution, the plan must run the *conditional* branch-update path instead of recording a no-op; D-07 already anticipates this and names the mitigation (SC#3's trial merge catches it) |
| A3 | `tox -e linkcheck` will again pass clean (no non-`working` rows) on Phase 73's tip, since the only CHANGELOG-driven docs change is prose with no new URLs (D-03: neither bullet is drafted with a URL) | Pattern 4 | Low-Medium — if a non-`working` row does appear, D-01..D-03's policy already governs the response (re-run up to 3x, then owner escalation for anything non-transient) |

**None of these assumptions block planning** — each is already covered by an existing decision (D-07 for A2, D-01..D-03 for A3) or is low-risk with a known fallback (A1). No open item here requires a new owner confirmation before Phase 73 can be planned.

## Open Questions

1. **Will the pushed CI job set still exactly match Phase 71's/Phase 72's 12-job set (no new job, no removed job) at the moment Phase 73 dispatches?**
   - What we know: `ci.yml` has not been touched since Phase 71 (`JOB_NAMES_MATCH_PHASE71 = yes` recorded in `72-CI-EVIDENCE.md`), and constraint 3 forbids any workflow-file edit this milestone.
   - What's unclear: whether an upstream GitHub Actions runner-image change (independent of this repo) could alter job behavior between now and execution — historically not observed in this project's release-prep phases.
   - Recommendation: 73-04's plan should still transcribe the full job list and compare its sorted name-set against Phase 72's `34761445288` run, exactly as Phase 72 compared against Phase 71's — don't assume it, measure it.

2. **Will any of the five open Dependabot PRs merge to `main` before this phase's execution finishes?**
   - What we know: today (2026-09-14) `origin/main` still equals the milestone base exactly; all five PRs are `MERGEABLE` with 15/15 checks green but nothing auto-merges them.
   - What's unclear: the exact timing of Phase 73's own execution relative to any manual or automated merge action outside this project's control.
   - Recommendation: D-07 already covers this — the trial merge (73-05) is the authoritative, re-run-at-execution-time catch. No plan should special-case "assume nothing merged."

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `git` (host + worktree) | Every SC#1/SC#3 probe | Yes | host-installed | — |
| `gh` CLI, authenticated | PR/branch-protection/CI reads, one `workflow_dispatch` | Yes (used live this session) | host-installed | — |
| `uv` 0.12.13 | Per-worktree provisioning, `uv lock --check` on merged tree | Yes (verified in Phase 72's worktrees) | 0.12.13 | On NixOS, reached via the `typsphinx-fhs-run` shim per CLAUDE.md § NixOS development shell |
| Network access (linkcheck, PyPI probe, gh API) | `tox -e linkcheck`, `curl`/API probes to PyPI, `gh api` calls | Assumed yes (Phase 72's linkcheck run succeeded; not independently re-verified this session) | — | None needed — if network is unavailable, `tox -e linkcheck` itself would fail loudly, which is D-03's "stop and go to owner" case |
| `myst_parser`, `furo`, `sphinx-autodoc-typehints` (the `docs` extra) | Changelog-page gate zero-skip reading, docs-html/pdf builds | Yes, when synced with `--extra docs` | pinned in `uv.lock` (myst-parser 5.1.0 confirmed in Phase 71's worktree) | Pitfall 1 above — must not rely on a bare `--extra dev` sync |

**Missing dependencies with no fallback:** none identified.

**Missing dependencies with fallback:** none identified — every dependency this phase needs is either already present in the pinned `uv.lock` or reachable through the existing NixOS FHS shim mechanism.

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json` (confirmed by reading the file this session), so this section is required.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (via `tox`'s `uv-venv-lock-runner`), plus `ruff`/`black`/`mypy` as static gates and Sphinx's own `linkcheck`/`html`/`typstpdf` builders as build-time gates |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.ruff]`, `[tool.black]`, `[tool.mypy]`); `tox.ini` (env definitions, including the new `[testenv:linkcheck]`) |
| Quick run command | `uv run pytest tests/test_changelog_page_gate.py -v -rs -p no:cacheprovider` (~4s; the fastest gate that actually exercises this phase's own edit) |
| Full suite command | `uv run pytest -q -rs -p no:cacheprovider` (~128s; expect `1547 passed, 1 skipped` per the last two phases' identical counts, to be re-measured fresh) |

### Phase Requirements -> Validation Map

This phase's only mapped requirement is REL-14, which is **explicitly not code-tested** — it closes on observed git/GitHub state at `/gsd-complete-milestone`, never inside this phase (REQUIREMENTS.md verbatim: "This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, and never by phase-completion tooling"). The table below maps ROADMAP SC#1..SC#4 (the actual observable contract this phase's plans discharge) and every CONTEXT.md decision (D-NN) that produces an observable outcome, to the concrete command and the evidence file that records it — this is the "requirements" surface a Nyquist-validation reading needs for a prep-only phase.

| SC / D-ID | Observable Behavior | Verification Type | Concrete Command | Evidence File / Section | File Exists? |
|-----------|---------------------|--------------------|-------------------|--------------------------|--------------|
| SC#1 (unpublished-shaped) | `pyproject.toml` still `0.9.2`; no `v0.9.3`/`v0.9.4`/`v0.9.5` tag (local + remote, positive-controlled on `v0.9.2`); no PyPI upload; no GitHub Release; milestone-wide product diff empty | build/state | `sed -n 7p pyproject.toml`; `git tag -l 'v0.9.[345]'`; `git ls-remote --tags origin`; `curl -sf https://pypi.org/pypi/typsphinx/0.9.X/json` (expect 404, with `0.9.2` as the 200 positive control); `gh release list`; `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` | `73-SC1-INVARIANTS.md` (two full observations, separated in time), `73-CLOSEOUT-GUARD.md` | ❌ Wave 1/3 |
| SC#2 (CHANGELOG under `## [Unreleased]` only) | Two new subsections, pure addition, zero deletions elsewhere; `[Unreleased]` compare base stays `v0.9.2`; no versioned heading created; changelog-page gate zero-skipped | unit + build | `git diff --numstat`; `awk`/`sha256sum` fence assertions (see Pattern 1); `uv run pytest tests/test_changelog_page_gate.py -v -rs` | `73-CHANGELOG-EVIDENCE.md` | ❌ Wave 1 |
| SC#3 (tree proven green, this phase's own runs) | Full pytest x2 (default + `LC_ALL=C`); `black`/`mypy`/`ruff` clean; docs-html/docs-pdf clean rebuild with zero `multiple toctrees` and unchanged warning count; `tox -e linkcheck` clean; one dispatched CI run, all 12 jobs green including both windows/macos lanes; non-committing trial merge passes `uv lock --check` + `ruff check .`; `main` protection read matches Phase 72's six contexts | unit + integration + build + remote | see Code Examples above | `73-GREEN-TREE-EVIDENCE.md`, `73-CI-EVIDENCE.md`, `73-PREFLIGHT-EVIDENCE.md` | ❌ Wave 2 |
| SC#4 (REL-14 held + standalone handoff) | SHA-256/`wc -l`/`grep` fence MATCH at head, close, AND after `phase.complete`-family tooling; `SUMMARY.md` declares `requirements-completed: []`; handoff enumerates every `/gsd-complete-milestone` step | state | see Pattern 3 above | `73-CLOSEOUT-GUARD.md`, `73-HANDOFF.md` | ❌ Wave 1 baseline / Wave 4 close+observation |
| D-06/D-07 (Dependabot PRs recorded, untouched) | Five PRs named by number/package/version in the handoff; no merge/comment/rebase action taken this phase | state | `gh pr list --state open --json number,title,author,headRefName,baseRefName,updatedAt` | `73-PREFLIGHT-EVIDENCE.md`, `73-HANDOFF.md` | ❌ Wave 2 |
| D-13 (SC#1's typsphinx/ + workflows fence, Phase-69 shape) | Scoped diff empty, widened diff non-empty (positive control the anchor is real) | state | `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/`; `git diff --name-only 098a8ff6..HEAD -- . ':(exclude).planning'` | `73-SC1-INVARIANTS.md` § "The typsphinx/.github fence" | ❌ Wave 3 |

### Sampling Rate
- **Per task commit:** the fast changelog-gate run (`pytest tests/test_changelog_page_gate.py`) after the CHANGELOG edit; scoped git-diff fences after every git/gh mutation
- **Per wave merge:** the full local green-tree suite (73-03) once per wave-2 merge; the CI dispatch (73-04) once, at the phase's single intended push
- **Phase gate:** all of SC#1..SC#4 MET, transcribed in `73-VERIFICATION.md` (verifier-authored) before `/gsd-verify-work`

### Wave 0 Gaps
None — every test file and fixture this phase needs (`tests/test_changelog_page_gate.py`, `tests/test_preview_version_sync.py`, `tests/test_readme_version_sync.py`, `tests/test_extension.py::test_version_matches_pyproject_toml`, and the full suite) already exists and passed at Phase 72's close. This phase adds no code and needs no new test infrastructure.

## Security Domain

`workflow.security_enforcement` is `true` (confirmed by reading `.planning/config.json` this session), so this section is required even though the phase makes no runtime/application change.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This phase touches no authentication surface; `gh`/git operations use the operator's own already-authenticated credentials, unmodified by this phase |
| V3 Session Management | No | N/A — no session-bearing component exists in this phase's scope |
| V4 Access Control | No | N/A — branch-protection *reading* is the only access-control-adjacent action, and it is read-only |
| V5 Input Validation | Marginal | The only "input" this phase authors is CHANGELOG prose (human-written, not parsed as code); `scripts/extract_changelog_section.py`'s own security note (already in the file, confirmed by reading it this session) states its `version` argument is used only for string-equality comparison, never interpolated into a shell command or used as a filesystem path — and this phase does not invoke that script at all (D-05) |
| V6 Cryptography | Marginal | `sha256sum` is used purely as a change-detection fence (Pattern 3), not for any security boundary — no secret, credential, or cryptographic guarantee depends on it |

### Known Threat Patterns for this phase's stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A checkbox-flip in `.planning/REQUIREMENTS.md` being silently committed by automation, misrepresenting the milestone's actual publish state | Tampering / Repudiation | The SHA-256 closeout-guard fence (Pattern 3), re-verified at three separated points, revert-and-report on any divergence, never committed |
| A `gh pr create`/`gh release` command constructed via string interpolation from untrusted content (e.g., a PR body built with `$(...)` command substitution) | Injection | CLAUDE.md and this project's own memory record ("sandbox-refuses-command-substitution-in-gh-comment") already establish the standing practice: PR/release bodies go through `--body-file <path>`, never through command substitution — `71-HANDOFF.md` step 4 follows this exactly and Phase 73's own handoff-authoring plan should too |
| A stale or forged positive-control value making an "empty diff" or "zero count" claim unfalsifiable | Repudiation | Every empty-diff or zero-count claim in this phase's evidence is paired with a positive control from a real, cited prior measurement (e.g., Phase 72's pre-fix `BASE_MULTI_TOCTREE_COUNT = 5`; `v0.9.2`'s 200 response as PyPI's positive control against `0.9.5`'s expected 404) |

This phase introduces no new attack surface (no new dependency, no new endpoint, no new user input parser); the security-relevant work is entirely about *not misrepresenting project state* (the checkbox fence, the positive-controlled probes), which V5/V6's marginal applicability above already covers.

## Recommended Plan Decomposition

Reusing Phase 71's 7-plan / 4-wave shape (Claude's Discretion in `73-CONTEXT.md` names exactly this evidence-file set), adapted for the four deltas described in the Summary:

| Plan | Wave | `depends_on` | Scope | Evidence file(s) |
|------|------|--------------|-------|-------------------|
| 73-01 | 1 | `[]` | Pre-edit clean docs baseline (positive control: 0 `multiple toctrees`, matching Phase 72's post-fix state, contrasted against Phase 72's own pre-fix `5`); insert `### Added` + `### Fixed` (D-01..D-05); post-edit clean docs rebuild proving identical counts; two-hunk pure-addition proof; byte-identity proof of the untouched `### Changed` block | `73-CHANGELOG-EVIDENCE.md` |
| 73-02 | 1 | `[]` | `73-CLOSEOUT-GUARD.md` baseline (SHA-256/`wc -l`/grep on REL-14 at phase head); SC#1 observation 1 of 2 (version-line, local+remote tag, PyPI, GitHub-Release, release-workflow, PR probes, each positive-controlled); `COVERAGE.md` | `73-CLOSEOUT-GUARD.md` (baseline section), `COVERAGE.md` |
| 73-03 | 2 | `["73-01", "73-02"]` | Full pytest x2 (default + `LC_ALL=C`); `black`/`mypy`/`ruff` local; version-sync family; changelog-page gate (0 skipped, docs extra present); docs-html/docs-pdf clean rebuild on the final (post-CHANGELOG-edit) tree, asserting 0 `multiple toctrees` + unchanged warning count; `tox -e linkcheck` fresh run with D-01..D-03 classification | `73-GREEN-TREE-EVIDENCE.md` |
| 73-04 | 2 | `["73-01", "73-02"]` | Decoy census; push canonical branch; `gh workflow run CI`; observe to completion in the foreground; transcribe all 12 jobs by name/conclusion, both windows lanes, both macos lanes; lint verdict read from the job's own log | `73-CI-EVIDENCE.md` |
| 73-05 | 2 | `["73-01", "73-02"]` | Non-committing trial merge (`git merge-tree --write-tree`, idempotency re-check); merged-tree `uv lock --check` + `ruff check .`; `main` protection read (six contexts, `strict: true`); merge-method precedent (#135/#136/#143/#(more recent) all merge-commits); Dependabot #146-150 census (recorded, untouched, per D-06) | `73-PREFLIGHT-EVIDENCE.md` |
| 73-06 | 3 | `["73-01", "73-02", "73-03", "73-04", "73-05"]` | SC#1 observation 2 of 2 (repeat every probe from 73-02, separated in time, spanning wave 2's CI dispatch + trial merge); the `typsphinx/`+`.github/workflows/` scoped-diff fence with the widened-diff positive control (Phase 69 shape, **not** masked-AST — D-13 explicitly says no masked-AST harness is needed); commits-after-CI-dispatch product-file count = 0 | `73-SC1-INVARIANTS.md` |
| 73-07 | 4 | `["73-01".."73-06"]` | Re-run the closeout-guard probes at phase close (MATCH against 73-02's baseline); write `73-HANDOFF.md` (negative-first opening; conditional branch-update step keyed on whether `origin/main` has moved; six-check wait; merge-commit method; REL-14's five-observation close checklist; Dependabot merge-order note; translations-repo/`stable`-check "not applicable" notes); fence observation over `typsphinx/`/`tests/`/`CHANGELOG.md`/`pyproject.toml`/`uv.lock`/`.planning/REQUIREMENTS.md` | `73-HANDOFF.md` (also reproduces the closeout-guard's operator-facing re-verification section in full) |

**What must change from a literal copy of Phase 71's plans (do not copy verify commands verbatim without adapting):**
1. **73-01's diff assertions must expect 2 hunks, not 1** (`git diff -U0 ... | grep -c '^@@'` -> 2), and must add a byte-identity check over the `### Changed` block specifically (new — Phase 71 never needed to prove a *sibling* subsection was untouched, because it edited inside the only subsection that existed).
2. **73-01/73-03's docs-build assertions must check `multiple toctrees` count = 0** at both pre-edit and post-edit builds (new — this defect didn't exist as a "must stay fixed" invariant at Phase 71's time; Phase 72's `BASE_MULTI_TOCTREE_COUNT = 5` is the positive control proving the grep methodology works, not a value Phase 73 should reproduce).
3. **73-03 must add the `tox -e linkcheck` run and its D-01..D-03 classification** — entirely absent from Phase 71's plan set, since `linkcheck` didn't exist yet.
4. **73-05's Dependabot census must enumerate and describe five real PRs** (not record an empty list like Phase 71's did) — the handoff text in 73-07 must name all five by number/package/range and state the merge order (milestone PR first, Dependabot after, per v0.9.3's #143->#142->#141 precedent already cited in `73-CONTEXT.md`).
5. **73-06's SC#1 typsphinx/ fence must use Phase 69's scoped-diff+widened-diff shape, not Phase 71's masked-AST harness** — do not copy `71-SC1-INVARIANTS.md`'s "Masked-AST re-run on the close tip" section into the plan; it is the wrong tool here since D-13 already establishes there is nothing under `typsphinx/` to re-prove behaviorally. Also widen the scoped-diff path list to `typsphinx/ .github/workflows/` (two paths), matching constraint 2/3 and D-13's exact wording, versus Phase 69's `typsphinx/`-only scope.
6. **Every count copied from this RESEARCH.md or from any `72-*-EVIDENCE.md`/`71-*-EVIDENCE.md` file must be re-measured fresh inside the executing plan's own worktree** (constraint 8) — this file's numbers exist to tell the planner what commands to run and what shape of result to expect, not values to assert without measuring.

## Sources

### Primary (HIGH confidence — read directly, this session, from committed repository files)
- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CONTEXT.md` — full D-01..D-15 decision set
- `.planning/REQUIREMENTS.md` — REL-14 verbatim, Traceability, Out of Scope
- `.planning/ROADMAP.md` § "🚧 v0.9.5 — Docs Link Check and Navigation (ACTIVE)" — constraints 1-13
- `.planning/STATE.md` — milestone history, v0.9.3/v0.9.4 close narratives
- `.planning/milestones/v0.9.4-phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CLOSEOUT-GUARD.md`, `71-HANDOFF.md`, `71-PREFLIGHT-EVIDENCE.md`, `71-CHANGELOG-EVIDENCE.md`, `71-GREEN-TREE-EVIDENCE.md`, `71-REVIEW.md`, `71-SC1-INVARIANTS.md` (headers) — full content read this session
- `.planning/milestones/v0.9.3-phases/69-v0-9-3-close-prep-prep-only-unpublished/69-SC1-INVARIANTS.md` — "typsphinx/ fence" section read this session
- `.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-BASE-EVIDENCE.md`, `72-LINKCHECK-EVIDENCE.md`, `72-CI-EVIDENCE.md`, `72-GATES-EVIDENCE.md`, `72-CONTEXT.md` (D-01..D-03 grep) — full content read this session
- `tests/test_changelog_page_gate.py`, `scripts/extract_changelog_section.py`, `docs/source/changelog.rst` — read this session, confirming neither test module nor script is sensitive to `## [Unreleased]` subsection names
- `CHANGELOG.md`, `pyproject.toml`, `.planning/config.json` — read/grepped this session, confirming current line numbers (`## [Unreleased]` at line 8, `### Changed` at 10-45, `### Planned...` at 47, `[Unreleased]` tail link at 1334), version `0.9.2`, `nyquist_validation: true`, `security_enforcement: true`

### Secondary (MEDIUM confidence — live git/gh probes run this session, current as of 2026-09-14)
- `git fetch origin` / `git rev-parse origin/main` -> `098a8ff64cf008822eef9dc69f75102ded3f7bc1` (unchanged from milestone base)
- `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` -> empty
- `git tag -l 'v0.9.*'` -> only `v0.9.0`, `v0.9.2`
- `gh pr list --state open` -> #146-#150, all Dependabot, `uv.lock`-only
- `gh api .../branches/main/protection/required_status_checks` -> `strict: true`, the same six contexts Phase 72 recorded

### Tertiary
None — no WebSearch was needed; this phase's entire domain is internal repository/process precedent, not external library research.

## Metadata

**Confidence breakdown:**
- Standard stack / tooling: HIGH — every tool version was either read from a committed evidence file this session or is unchanged (`git`, `gh`, `uv`, `ruff` pins confirmed live)
- Architecture / plan decomposition: HIGH — direct precedent (Phase 71) executed the identical phase shape one milestone ago; the four deltas are each independently confirmed against Phase 72's own evidence
- Pitfalls: HIGH — every pitfall listed was either directly observed in this project's own history (cited by evidence file) or is a documented standing hazard in project memory
- Validation architecture: HIGH — the requirement (REL-14) is explicitly not code-testable by design; the SC#1..SC#4 / D-NN mapping substitutes the actual observable contract, each row backed by a command already proven to work in Phase 71/72's own evidence

**Research date:** 2026-09-14
**Valid until:** this phase's own execution (days, not weeks) — every count in this file is explicitly "context only" per constraint 8 and must be re-measured fresh; the *procedures* (Patterns 1-4, the plan decomposition) remain valid for the life of this milestone shape (i.e., until the next release-prep phase changes the CHANGELOG-insertion or fence mechanism)
