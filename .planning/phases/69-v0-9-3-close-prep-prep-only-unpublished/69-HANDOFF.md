# Phase 69: v0.9.3 Close Prep — Handoff for /gsd-complete-milestone

**This milestone publishes nothing.** No tag is created, locally or on the remote; nothing is uploaded to PyPI; no GitHub Release is created; and `pyproject.toml` stays at `0.9.2` — no version bump lands with this close.

The `typsphinx-doc-translations` `update-pin.yml` dispatch and the Read the Docs `stable` verification are both **not applicable** to this close: neither project has anything new to track when no tag and no GitHub Release exist for this repository. Read the Docs `latest` rebuilds from `main` on its own once the PR below merges, and needs no action from this handoff.

The one irreversible action this close performs is **REL-12**: a pull request from `gsd/v0.9.3-toolchain-and-dependency-update-repair` to `main`, opened and merged at `/gsd-complete-milestone`. This inverts the v0.9.1 close (`61-HANDOFF.md`), which opened no pull request at all — this milestone's PR is the one publish-adjacent step that is genuine and irreversible, and everything below names it precisely rather than folding it into a habitual publish checklist.

Every other v1 requirement of this milestone (NIX-01..NIX-08, TOX-01..TOX-04, DEP-01..DEP-05, DOC-19..DOC-21) already closed in Phases 64 through 68; REL-12 is the sole requirement this phase carries, and it is held open by design until the PR below actually merges — never flipped inside a plan.

CI stays exactly as it was before this milestone: no `nix` job, no pinned `setup-uv` version, no bumped action tag. The only workflow-adjacent file this milestone edits is `.github/dependabot.yml`, which is not itself a workflow.

Everything below this line is either a step this handoff hands to `/gsd-complete-milestone` to run, or a record of what this phase already measured and left untouched — no prose past this point should be read as an instruction already carried out inside Phase 69 itself.

## What /gsd-complete-milestone does, in order

0. **Fence first.** Back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` to a scratch directory outside the repository (e.g. `/tmp/scratch-69-closeout/`). Then run the § 4 probes below, and start only on a MATCH.

1. **Re-run the trial merge.**
   - `git fetch origin`, then `git merge-tree --write-tree HEAD origin/main; echo "exit:$?"`, which requires `exit:0`.
   - Cite `69-PREFLIGHT-EVIDENCE.md`'s `MERGE_TREE`, `LOCK_CHECK_EXIT` and `MERGED_RUFF_LOCK_VERSION` as the phase-time result (`MERGE_RC = 0`, tree `32f0573c8dccda8101a8df34a9c968ba2952108b`, lock check exit 0, merged ruff `0.16.6`). That tree SHA changes with every commit on either ref, so it is re-measured here, not copied.
   - If `origin/main` has moved past the `ORIGIN_MAIN_SHA` recorded in `69-PREFLIGHT-EVIDENCE.md` (`cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a`), re-run the scratch `uv lock --check` exactly as `69-PREFLIGHT-EVIDENCE.md` § "Merged lock" did: `git archive <tree> pyproject.toml uv.lock` into a `mktemp -d` scratch directory, then `uv --directory <scratch> lock --check`.

2. **Merge `origin/main` into the branch.** In the main checkout, on `gsd/v0.9.3-toolchain-and-dependency-update-repair`, run `git merge --no-ff origin/main -m "Merge origin/main into gsd/v0.9.3-toolchain-and-dependency-update-repair"`. Never rebase the milestone's own commits. The reason: `main`'s branch protection has `strict: true` (`69-PREFLIGHT-EVIDENCE.md` § "main protection"), so the pull request cannot merge until its head branch is up to date with `main`. D-06 deferred this merge to here, on purpose — no `origin/main` merge happened inside any plan of this phase.

3. **Check the lock and re-sync.**
   - `uv lock --check`, then `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`. The docs extra is named explicitly because a bare `--extra dev` exact sync drops it from the main checkout (`CLAUDE.md`'s own documented hazard, restated in `69-CONTEXT.md` § "Specific Ideas").
   - `ruff --version` now reports the merged lock's version, `0.16.x` (`MERGED_RUFF_LOCK_VERSION = 0.16.6` in `69-PREFLIGHT-EVIDENCE.md`). That is consistent with NIX-01 per `67-CONTEXT.md` D-03: NIX-01's binding sense is "the version `uv.lock` pins", and after REL-12 that pin is `main`'s.
   - `69-PREFLIGHT-EVIDENCE.md` § "Merged-tree lint" recorded no `## FINDING: merged-tree lint` — both `ruff check .` and `black --check .` passed clean on the merged tree at merge-tree time. If a fresh run here finds a violation the pre-flight did not (because `origin/main` moved), name it as the owner's decision before step 5, exactly as the pre-flight instructed.

4. **Push.** `git push --no-follow-tags origin gsd/v0.9.3-toolchain-and-dependency-update-repair`, a fast-forward from `PUSHED_SHA` (`becd70c31bfed573dc10cdc20dcf7a30d57edd57`, `69-CI-EVIDENCE.md`). It also carries this phase's later `.planning/` commits (69-03 through this plan's own).

5. **Open the pull request.** `gh pr create --base main --head gsd/v0.9.3-toolchain-and-dependency-update-repair --title <English title> --body-file <file>`. Title and body are English and terse. The body goes through a file, never through `$(…)` command substitution (this project's sandbox has refused `gh --comment`-style command substitution before).

6. **Wait for the required checks.** Wait for all six to be green on the updated head, named literally: `Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Lint and Format Check`, `Type Check`, `Code Coverage` and `Build Package` (`69-PREFLIGHT-EVIDENCE.md` § "main protection", `PROTECTION_CONTEXTS_COUNT = 6`). The `pull_request` trigger runs the whole twelve-job `ci.yml`, which should be green throughout — the six named above are only the ones branch protection requires.

7. **Merge.** `gh pr merge <number> --merge`: a merge commit, never squash or rebase. Cite `69-PREFLIGHT-EVIDENCE.md` § "Merge-method precedent" — #135 and #136 (`MERGE_PRECEDENT_HITS = 2`) are both `Merge pull request` commits on `main`'s first-parent history, and the same two dependency PRs (#137, #138) merged the same way in between.

8. **Observe what REL-12 requires, then close it.**
   - The merge commit is on `origin/main`.
   - `git show origin/main:pyproject.toml | sed -n 7p` reads `version = "0.9.2"`.
   - `git ls-remote --tags origin` shows `v0.9.2` and no `v0.9.3`.
   - PyPI returns `404` for `0.9.3` and `200` for `0.9.2`.
   - `gh release list` shows no `v0.9.3`.

   Only on those five observations is REL-12's checkbox flipped — at `/gsd-complete-milestone`, never inside a plan of this phase.

9. **Not applicable.** No tag; no `release.yml` run; no PyPI upload; no GitHub Release; no `update-pin.yml` dispatch on `typsphinx-doc-translations`; no Read the Docs `stable` check. Read the Docs `latest` rebuilds from `main` on its own and will then show the `## [Unreleased]` bullets — that needs no action from this close.

## What this phase satisfied

**REL-12**, quoted verbatim from `.planning/REQUIREMENTS.md:75`:

> - [ ] **REL-12**: the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no
>       GitHub Release, and `pyproject.toml` still at `0.9.2`

**REL-12 stays open until step 8 above runs.** No plan in this phase — including this one — touched its checkbox; every SUMMARY of this phase declares `requirements-completed: []`.

Reporting ROADMAP SC#1 through SC#4, each citing its own evidence file and section rather than re-deriving the verdict:

- **SC#1** (the tree is proven unpublished-shaped, twice, at separated timestamps) — **MET**. `69-SC1-INVARIANTS.md` § "Observation 1 of 2" (`OBS1_AT = 2026-09-12T22:35:11Z`) and § "Observation 2 of 2" (`OBS2_AT = 2026-09-12T23:01:58Z`, 26m47s later, after wave 2's push and CI dispatch), both with the same positive-controlled tag/PyPI/GitHub-Release/release-workflow/PR probes and identical results. § "The phase-scoped typsphinx/ diff" — empty against `PHASE_BASE_SHA`, with the widened diff proving the anchor real (exactly `CHANGELOG.md`, +25/−0).
- **SC#2** (the milestone's CHANGELOG bullets land under `## [Unreleased]`, no version literal moves) — **MET**. `69-CHANGELOG-EVIDENCE.md` § "Fence assertions" (headings/link-refs counts unchanged, `### Planned for Future Releases` byte-identical, `V093_AFTER = 0`) and § "Pure-addition proof" (zero removed lines across both tasks' combined diff).
- **SC#3** (the tree is proven green on live runs) — **MET**. Local half: `69-GREEN-TREE-EVIDENCE.md` (`SC3_LOCAL_VERDICT = MET` — full pytest suite 1547 passed/1 skipped twice, once under `LC_ALL=C`, `black`/`mypy`/`ruff` all exit 0, changelog page gate 6/6, docs clean builds 3/5 warnings matching baseline). CI half: `69-CI-EVIDENCE.md` (`SC3_CI_VERDICT = MET` — run `34723677990`, `JOB_COUNT = 12`, `NON_SUCCESS_JOBS = 0`, both `windows-latest` and both `macos-latest` lanes `success`). Set side by side: local `ruff` `0.15.20` (`RUFF_LOCAL_VERSION`) equals CI's `CI_RUFF_VERSION` (`0.15.20`), both equal to `LOCK_RUFF_VERSION` at `PUSHED_SHA`; local docs `DOCS_HTML_WARN_FINAL = 3` / `DOCS_PDF_WARN_FINAL = 5` equal the `69-CHANGELOG-EVIDENCE.md` `_BASE` counts (3 / 5) exactly.
- **SC#4** (the no-irreversible-action fence is proven held at phase close) — **MET**. `69-CLOSEOUT-GUARD.md` § "Re-verification at phase close" (`REQ_VERDICT_CLOSE = MATCH` — digest, line count, empty diff, empty git-log-over-file, and the four REL-12 grep lines all match the phase-head Baseline), and this document's own § "Fence observation" below.

**The D-13 statement.** The single CI dispatch ran on `PUSHED_SHA` (`becd70c31bfed573dc10cdc20dcf7a30d57edd57`), the tip carrying every product-tree change of the phase (the CHANGELOG edit authored by 69-01), and every later commit of the phase is `.planning/`-only (`69-SC1-INVARIANTS.md` § "Commits after the CI dispatch": `POST_DISPATCH_PRODUCT_FILES = 0`, no `release.yml` run at `PUSHED_SHA`, exactly one `ci.yml` dispatch at it).

## Recorded without acting

**D-10.** The open dependabot PRs, read-only, at `PR_CENSUS_AT = 2026-09-12T22:50:42Z` (`69-PREFLIGHT-EVIDENCE.md` § "Dependabot PRs"):

| PR | State | Base | Head | Title |
|----|-------|------|------|-------|
| #139 | OPEN | main | dependabot/uv/tox-4.61.4 | chore(deps): bump tox from 4.56.1 to 4.61.4 |
| #140 | OPEN | main | dependabot/uv/sphinx-intl-2.4.0 | chore(deps): bump sphinx-intl from 2.3.2 to 2.4.0 |
| #141 | OPEN | main | dependabot/uv/pre-commit-4.6.2 | chore(deps): bump pre-commit from 4.6.0 to 4.6.2 |
| #142 | OPEN | main | dependabot/uv/mypy-2.3.1 | chore(deps): bump mypy from 2.1.0 to 2.3.1 |

All four target `main`. This phase took no merge, close, comment or rebase-request action on any of them. Their disposition is ordinary dependency maintenance after REL-12: once the PR in step 7 above changes `main`'s `uv.lock`, dependabot rebases these PRs on its own schedule — no action is owed from this handoff.

**D-11.** The `0.9.3` version number is **unclaimed**, not decided. No `v0.9.3` tag exists anywhere and none is created by this close. Whether the next published release is `0.9.3` or skips the number belongs to the next milestone's own scoping, not to this handoff. The next release-prep phase promotes this phase's `## [Unreleased]` bullets (the TOX/DEP/NIX entries authored by 69-01) into its own versioned section, exactly as Phase 63 promoted Phase 61's bullets into `## [0.9.2]`.

## Before and after phase.complete-family tooling

Reproduced from `69-CLOSEOUT-GUARD.md` § "For the operator running phase.complete", so an operator following this handoff reaches the procedure without opening that file separately.

This section applies after this phase's plans have finished, at **whichever of the two entry points runs**: `/gsd-execute-phase`'s `phase.complete` step, or `/gsd-verify-work`'s inline transition (`transition.md`'s `update_roadmap_and_state`, which calls the same `phase.complete` verb unconditionally once UAT closes clean — the exact path that produced Phase 63's "Fourth observation"). Both entry points must be treated as equally likely to trigger the flip; neither is safer to assume clean than the other.

**Before either runs:** back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` to a scratch directory outside the repository (e.g. `/tmp/scratch-69-closeout/`), so a hand-edited STATE.md or ROADMAP.md rewrite that the tooling itself corrupts (Phase 63's "Fourth observation" found STATE.md's rewrite dropping `current_phase_name` and degrading descriptive fields) has a known-good copy to diff against, not only `.planning/REQUIREMENTS.md`.

**After it runs**, re-run these probes, with the baseline digest and grep lines written out inline here so the reader needs no other file open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-12' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   75:- [ ] **REL-12**: the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no
#   147:| REL-12 | Phase 69 | Pending |
#   164:| 69 — v0.9.3 Close Prep (prep-only, unpublished) | REL-12 | 1 |
#   166:**REL-12 is mapped to Phase 69 for coverage purposes only.** Like every REL requirement in this
```

**On any divergence:** run `git checkout -- .planning/REQUIREMENTS.md`, re-run the probes above to show a MATCH, and then diff `.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch backup — reverting either if it, too, carries an unwarranted change from the same tooling run.

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts until every probe above shows MATCH. This is the explicit rule this project has followed at every prior release-prep close where the flip was caught: revert first, report second, never ship the flipped state as part of the phase's own close. The flip has landed at **seven consecutive** prior release-prep closes (Phases 41, 46, 52, 57 flipped and were caught; 61 and 68 held with no requirement to flip; 63 flipped and was reverted **twice** — once through `/gsd-execute-phase`'s `phase.complete` step and once again through `/gsd-verify-work`'s inline transition, the same underlying verb reached through two different entry points, per `63-CLOSEOUT-GUARD.md`).

## Fence observation

Recorded live, at this task's own time, inside plan 69-06's own worktree, after Tasks 1 and 2 of this same plan:

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ sha256sum .planning/REQUIREMENTS.md
02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a  .planning/REQUIREMENTS.md

$ git tag -l 'v0.9.3'
(no output)

$ git status --porcelain typsphinx/ tests/ CHANGELOG.md pyproject.toml uv.lock .planning/REQUIREMENTS.md
(no output)
```

Empty diff, digest equal to `REQ_SHA256_BASE` (`02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a`), no local `v0.9.3` tag, and every named product/tracking path clean. The fence holds at this plan's own close, matching `69-CLOSEOUT-GUARD.md`'s `REQ_VERDICT_CLOSE = MATCH` and `69-SC1-INVARIANTS.md`'s two observations.

## What this phase deliberately did not do

- No tag, local or remote.
- No `release.yml` run — only `ci.yml` was dispatched, exactly once, in 69-04 (D-13).
- Nothing uploaded to PyPI.
- No GitHub Release.
- No pull request opened, merged or commented on.
- No `origin/main` merged into the milestone branch (D-06) — that merge is deferred to step 2 above, at `/gsd-complete-milestone`.
- No `update-pin.yml` dispatch on `typsphinx-doc-translations`.
- No merge, close, rebase request or comment on #139, #140, #141 or #142 (D-10).
- No `.planning/REQUIREMENTS.md` checkbox or Traceability-row change.
- One push and one `ci.yml` dispatch only, in 69-04 (D-13).

This handoff contains no command that tags, creates a release, or dispatches the translations-repository pin workflow.

---
*Phase: 69-v0-9-3-close-prep-prep-only-unpublished*
*Plan: 06*
