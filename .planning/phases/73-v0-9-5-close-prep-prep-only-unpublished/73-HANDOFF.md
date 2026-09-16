# Phase 73: v0.9.5 Close Prep — Handoff for /gsd-complete-milestone

**This milestone publishes nothing.** No tag is created, locally or on the remote; nothing is uploaded to PyPI; no GitHub Release is created; and `pyproject.toml` stays at `0.9.2` — no version bump lands with this close.

The `typsphinx-doc-translations` `update-pin.yml` dispatch and the Read the Docs `stable` check are both **not applicable** to this close: neither project has anything new to track when no tag and no GitHub Release exist for this repository. Recorded as facts, not steps: the daily `update-pin.yml` schedule moves the Japanese `latest` site onto the merged `main` with no action from anyone; `/en/latest/` rebuilds on the `main` push; and `stable` stays on `v0.9.2` until the next published release.

The one irreversible action this close performs is **REL-14**: a pull request from `gsd/v0.9.5-docs-link-check-and-navigation` to `main`, opened and merged at `/gsd-complete-milestone`, as REL-12 and REL-13 were with PR #143 and PR #145.

Every other v1 requirement of this milestone (QUA-13, DOC-24, DOC-18) already closed in Phase 72; REL-14 is the sole requirement this phase carries, and it is held open by design until the pull request below actually merges — never flipped inside a plan.

CI stays exactly as it was before this milestone: no workflow file is edited anywhere in this phase or by this handoff's own steps.

Everything below this line is either a step this handoff hands to `/gsd-complete-milestone` to run, or a record of what this phase already measured and left untouched — no prose past this point should be read as an instruction already carried out inside Phase 73 itself.

## What /gsd-complete-milestone does, in order

0. **Fence first.** Back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` to a scratch directory outside the repository (e.g. `/tmp/scratch-73-closeout/`). Then run the § "Before and after phase.complete-family tooling" probes below, and start only on a MATCH.

1. **Re-run the trial merge.**
   - `git fetch origin`, then `git merge-tree --write-tree HEAD origin/main; echo "exit:$?"`, which requires `exit:0`.
   - Cite `73-PREFLIGHT-EVIDENCE.md`'s `MERGE_TREE` (`228dc64ea867e2f993b97229faf6607774ed39c6`), `MAIN_MOVED` (`yes`), `LOCK_CHECK_EXIT` (`0`), `MERGED_RUFF_LOCK_VERSION` (`0.16.7`) and `TRIAL_MERGE_VERDICT` (`MET`) as the phase-time result. That tree SHA changes with every commit on either ref, so `git merge-tree` is re-run here, not copied.
   - Then `git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"`. `exit:0` means `main` has not moved past the milestone base `098a8ff6`. `exit:1` means it moved: re-run the scratch `uv lock --check` and the merged-tree `ruff check .` exactly as `73-PREFLIGHT-EVIDENCE.md` § "Merged lock" and § "Merged-tree lint" did. That `ruff` verdict is authoritative, and a finding is the owner's decision before step 4. No docs build of the merged tree is added (D-07).
   - **This is not a hypothetical branch.** `main` had already moved past `098a8ff6` by absorbing all five Dependabot pull requests before this phase's own execution began (§ "Recorded without acting" below re-measures this live). Barring a fresh force-push or revert on `main` between now and `/gsd-complete-milestone`, this step will print `exit:1` and the conditional branch update in step 2 will run, not be a recorded no-op.

2. **Conditional branch update (D-10).** Only if step 1 printed `exit:1`: in the main checkout, on `gsd/v0.9.5-docs-link-check-and-navigation`, run `git merge --no-ff origin/main -m "Merge origin/main into gsd/v0.9.5-docs-link-check-and-navigation"`. Never rebase the milestone's commits. Then run `uv lock --check`, then `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` (the docs extra is named because a bare `--extra dev` exact sync drops it from the main checkout), and re-check that `git merge-base --is-ancestor origin/main HEAD` now exits 0. Otherwise, record this step as a no-op with step 1's `exit:0` output. The reason: `main`'s protection is `strict: true` (`73-PREFLIGHT-EVIDENCE.md` § "main protection (D-09)"), so the pull request cannot merge until the branch is up to date.

3. **Push.** `git push --no-follow-tags origin gsd/v0.9.5-docs-link-check-and-navigation`, a fast-forward from `73-CI-EVIDENCE.md`'s `PUSHED_SHA` (`a54a2d8a3b06b388c7ee004e5cfbe3405431421d`). It carries this phase's later `.planning/` commits, and the merge commit if step 2 ran.

4. **Open the pull request.** `gh pr create --base main --head gsd/v0.9.5-docs-link-check-and-navigation --title <English title> --body-file <file>`. Title and body are English and terse. The body goes through a file passed with `--body-file`, never through a command substitution.

5. **Wait for the required checks.** Wait for all six to be green on the pull request head, named literally: `Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Lint and Format Check`, `Type Check`, `Code Coverage` and `Build Package`. The `pull_request` trigger runs the whole `ci.yml`; the six named above are only the ones branch protection requires.

6. **Merge.** `gh pr merge <number> --merge`: a merge commit, never squash or rebase. Cite `73-PREFLIGHT-EVIDENCE.md` § "Merge-method precedent (D-10)": `#143` and `#145` (`MERGE_PRECEDENT_HITS = 2`) are both `Merge pull request` commits on `main`'s first-parent history.

7. **Observe what REL-14 requires, then close it** (SC#4, D-10). Immediately after the merge, before any Dependabot merge:
   - The merge commit is on `origin/main`: `git fetch origin`, then `git log --first-parent -1 --format='%h %s' origin/main`.
   - `git show origin/main:pyproject.toml`, line 7, reads `version = "0.9.2"`.
   - `git ls-remote --tags origin` shows `refs/tags/v0.9.2` (positive control) and no `v0.9.3`, `v0.9.4` or `v0.9.5` tag.
   - PyPI returns `404` for `0.9.5`, and for `0.9.3` and `0.9.4`, and `200` for `0.9.2`, the positive control.
   - `gh release list` shows `v0.9.2` as Latest and no `v0.9.3`, `v0.9.4` or `v0.9.5` Release.

   Only on those five observations is REL-14's box checked, at `/gsd-complete-milestone`, never inside a plan.

8. **Only then, the Dependabot pull requests (D-06) — already merged, nothing left to order.** #146 (`build`, `1.5.0 -> 1.6.1`), #147 (`ruff`, `0.16.6 -> 0.16.7`), #148 (`pypdf`, `6.14.2 -> 6.18.1`), #149 (`twine`, `6.2.0 -> 7.0.0`) and #150 (`sphinx-autodoc-typehints`, `3.0.1 -> 3.13.6`, a `docs`-extra dependency) all merged into `main` on `2026-09-14` — before this phase's own execution began on `2026-09-16` — measured live in § "Recorded without acting" below with `gh pr list --state all`, independently of the phase's own `73-PREFLIGHT-EVIDENCE.md` census. The order this project has followed at every prior close still held here: the literal phrase is **"milestone pull request first, Dependabot second"** — #145 (the v0.9.4 milestone pull request) merged first, and #146–#150 rebased themselves onto `main` and merged afterward, exactly as v0.9.3's #143 was followed by #142 and #141. There is no post-milestone Dependabot queue for `/gsd-complete-milestone` to order: by the time this handoff's step 8 is reached, all five will already be part of `main`'s history, absorbed by step 1's re-run trial merge and, if `main` moved, step 2's branch update — not by any action against a pull request. The one live consequence for the operator is that `main` has moved (D-07's case), which is exactly why step 2's conditional branch update above is not a theoretical possibility but the expected path.

9. **Not applicable.** No tag; no `release.yml` run; no PyPI upload; no GitHub Release; no `update-pin.yml` dispatch on `typsphinx-doc-translations`; no Read the Docs `stable` check. Read the Docs `latest` rebuilds from `main` and then shows the six `## [Unreleased]` bullets, which needs no action.

## What this phase satisfied

**REL-14**, quoted verbatim from `.planning/REQUIREMENTS.md:22`:

> - [ ] **REL-14**: Close prep only, unpublished. CHANGELOG bullet(s) go under the existing `## [Unreleased]`, in the register of the four bullets already there, and name the docs sidebar fix and the new `tox -e linkcheck` environment (owner decision 2026-09-13; revised the same day when QUA-08, the CI job, was deferred — no bullet may claim a CI job that does not exist). `pyproject.toml` stays `0.9.2`. There is no tag, no PyPI upload and no GitHub Release. The milestone branch is merged to `main` through a PR, as REL-12 and REL-13 were. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, and never by phase-completion tooling.

**REL-14 stays open until step 7 above runs.** No plan in this phase — including this one — touched its checkbox; every SUMMARY of this phase declares `requirements-completed: []`.

Reporting ROADMAP SC#1 through SC#4, each citing its own evidence file and section rather than re-deriving the verdict:

- **SC#1** (the tree is proven unpublished-shaped, twice, at separated timestamps, with no code change slipped in) — **MET**. `73-SC1-INVARIANTS.md` § "Observation 1 of 2" (`OBS1_AT = 2026-09-16T09:57:35Z`) and § "Observation 2 of 2" (`OBS2_AT = 2026-09-16T10:30:21Z`, 32m46s later, spanning the local green-tree proof, the phase's only push and CI dispatch, and the D-09 trial-merge pre-flight), both with the same positive-controlled version/tag/PyPI/GitHub-Release/release-workflow/PR probes and identical results. § "Milestone fences (D-13)" and § "Milestone fences on the close tip (D-13)": `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` is empty at both observations (`MILESTONE_CODE_WORKFLOW_DIFF = empty`, `CLOSE_MILESTONE_CODE_WORKFLOW_DIFF = empty`), each with a pathspec control (16 tracked files) and a widened-diff control (Phase 72's five product files, plus this phase's own `CHANGELOG.md` at the close tip). § "The phase-scoped product diff": exactly `CHANGELOG.md`, +15/−0, from `PHASE_BASE_SHA`, with no other product-tree file touched. § "Commits after the CI dispatch": `POST_DISPATCH_PRODUCT_FILES = 0` — every one of the eighteen commits after `PUSHED_SHA` touches only `.planning/`. `SC1_VERDICT = MET`.
- **SC#2** (the milestone's CHANGELOG bullets land under `## [Unreleased]`, no version literal moves) — **MET**. `73-CHANGELOG-EVIDENCE.md` § "Pure-addition proof" (`ADDED_LINES = 15`, `REMOVED_LINES = 0`, `DIFF_HUNKS = 2`), § "Fence assertions" (`HEADINGS_AFTER = HEADINGS_BEFORE = 23`, `CHANGED_SHA_AFTER = CHANGED_SHA_BEFORE`, `PLANNED_SHA_AFTER = PLANNED_SHA_BEFORE`, `VERSION_LITERALS_AFTER = 0`) and § "Bullet content assertions" (`ADDED_ID_SPAN = present`, `FIXED_ID_SPAN = present`, `JAPANESE_SITE_WORDS = 0`, `BULLET_URLS = 0`). `73-GREEN-TREE-EVIDENCE.md` § "Changelog page gate" (zero skipped): `CHANGELOG_GATE_SUMMARY = 6 passed`, `CHANGELOG_GATE_SKIPPED = 0` — every build-dependent test class ran, in an environment carrying the `docs` extra.
- **SC#3** (the tree is proven green by runs executed in this phase, including against `main` as it stands at close) — **MET**. Set side by side:

  | Measurement | Local (`73-GREEN-TREE-EVIDENCE.md`) | CI (`73-CI-EVIDENCE.md`) | Trial merge (`73-PREFLIGHT-EVIDENCE.md`) |
  |---|---|---|---|
  | Full suite | `FULL_SUMMARY = 1547 passed, 1 skipped` | — | — |
  | Full suite, `LC_ALL=C` | `LCALLC_SUMMARY = 1547 passed, 1 skipped` | — | — |
  | `ruff` version | `RUFF_LOCAL_VERSION = 0.16.6` | `CI_RUFF_VERSION = 0.16.6` | `MERGED_RUFF_LOCK_VERSION = 0.16.7` |
  | Lint/format exit | `RUFF_LOCAL_EXIT = 0`, `BLACK_EXIT = 0`, `MYPY_EXIT = 0` | ruff's verdict quoted from `Lint and Format Check`: `All checks passed!` | `MERGED_RUFF_EXIT = 0`, `MERGED_BLACK_EXIT = 0` |
  | Docs clean-build counts | `DOCS_HTML_WARN_FINAL = 3` = `DOCS_HTML_WARN_BASE`; `DOCS_PDF_WARN_FINAL = 5` = `DOCS_PDF_WARN_BASE`, both `MULTI_TOCTREE_*_FINAL = 0` | — | — |
  | `tox -e linkcheck` | `LINKCHECK_TOTAL = 95`, `LINKCHECK_WORKING = 95`, `LINKCHECK_VERDICT = PASS` | — | — |
  | Run identity / verdict | — | `RUN_ID = 35083828156`, `JOB_COUNT = 12`, `NON_SUCCESS_JOBS = 0`, both `windows-latest` and both `macos-latest` lanes `success`, `JOB_NAMES_MATCH_PHASE72 = yes` | `MERGE_RC = 0`, `LOCK_CHECK_EXIT = 0` |
  | Required contexts | — | `REQUIRED_CHECKS_UNCHANGED = yes` (`Build Package\|Code Coverage\|Lint and Format Check\|Test Python 3.12 on ubuntu-latest\|Test Python 3.13 on ubuntu-latest\|Type Check`, `strict: true`) | `PROTECTION_STRICT = true`, `PROTECTION_CONTEXTS_COUNT = 6` |
  | Verdict | `SC3_LOCAL_VERDICT = MET` | `SC3_CI_VERDICT = MET` | `TRIAL_MERGE_VERDICT = MET` |

- **SC#4** (the REL-14 checkbox is proven held by a recorded SHA-256, and the handoff is standalone) — **MET**. `73-CLOSEOUT-GUARD.md` § "Re-verification at phase close" (`REQ_VERDICT_CLOSE = MATCH`), and this file.

**The D-12 statement.** The single dispatch (`RUN_ID = 35083828156`) ran on `PUSHED_SHA` (`a54a2d8a3b06b388c7ee004e5cfbe3405431421d`), the tip carrying every product-tree change of the phase — `73-CI-EVIDENCE.md` § "Tip identity and fence" already showed the pushed tree byte-identical to that worktree's HEAD, which carried the phase's own `CHANGELOG.md` edit (wave 1) and nothing else since. Every commit landing after `PUSHED_SHA` — eighteen commits (`73-SC1-INVARIANTS.md` § "Commits after the CI dispatch") — touches only `.planning/`, which no CI job reads. No `release.yml` run has ever fired at `PUSHED_SHA` either.

## Recorded without acting

- **D-06:** the phase-time census from `73-PREFLIGHT-EVIDENCE.md` § "Dependabot and open pull requests (D-06)": `PR_CENSUS_AT = 2026-09-16T10:17:02Z`, `OPEN_PRS = 0`, `DEPENDABOT_OPEN_PRS = 0` — all five of #146–#150 had already merged before that census, and the census recorded each one's package, version range, state and files:

  | Pull request | Package | Range | State | Files | Actor touches (census) |
  |---|---|---|---|---|---|
  | #146 | build | 1.5.0 -> 1.6.1 | MERGED | uv.lock | 0 |
  | #147 | ruff | 0.16.6 -> 0.16.7 | MERGED | uv.lock | 0 |
  | #148 | pypdf | 6.14.2 -> 6.18.1 | MERGED | uv.lock | 0 |
  | #149 | twine | 6.2.0 -> 7.0.0 | MERGED | uv.lock | 0 |
  | #150 | sphinx-autodoc-typehints | 3.0.1 -> 3.13.6 | MERGED | uv.lock | 0 |

  **Live re-read, taken during this task's own execution, independently of the census above:**

  ```
  $ date -u +%FT%TZ
  2026-09-16T10:47:11Z

  $ gh pr list --state all --limit 10 --json number,title,state,mergedAt,baseRefName,headRefName
  [{"number":150,"state":"MERGED","mergedAt":"2026-09-14T15:13:52Z", ...},
   {"number":149,"state":"MERGED","mergedAt":"2026-09-14T15:18:45Z", ...},
   {"number":148,"state":"MERGED","mergedAt":"2026-09-14T15:52:00Z", ...},
   {"number":147,"state":"MERGED","mergedAt":"2026-09-14T15:40:35Z", ...},
   {"number":146,"state":"MERGED","mergedAt":"2026-09-14T16:03:53Z", ...},
   {"number":145,"state":"MERGED","mergedAt":"2026-09-13T10:09:32Z", ...}, ...]
  ```

  All five merged on `2026-09-14`, before this phase's own execution began on `2026-09-16` — this project's phase-planning premise that #146–#150 were "open, to be named and ordered after the milestone pull request" was overtaken by events between planning (2026-09-14) and execution; the live measurement above, not the plan's own prose, is authoritative. For each of #146–#150, the live count of comments and reviews by the gh account (`GH_ACTOR = YuSabo90002`) equals the census (`0` for all five, re-measured with `gh pr view <n> --json comments,reviews`). No new pull request from any actor appeared against `main` beyond the twelve already on record. This phase took no merge, close, comment, review, label or rebase-request action on any pull request — #146–#150 merged themselves, through Dependabot's own automation, entirely outside this phase's or this milestone's control.

- **D-07:** a Dependabot merge landing on `main` before the close — which is exactly what happened here — is caught by step 1's re-run `merge-tree` and the merged-tree `ruff check .`/`uv lock --check` above; no docs build of `main` plus #150 is added by this phase or this handoff.

- **D-11:** the `0.9.3`, `0.9.4` and `0.9.5` version numbers are all recorded as **unclaimed, not decided**. After this phase, `## [Unreleased]` holds six bullets from three unpublished milestones: four under `### Changed` (three from v0.9.3 — `tox-uv`, Dependabot `uv`, `flake.nix` — and one from v0.9.4 — typing modernization), plus this phase's own `### Added` (the `tox -e linkcheck` bullet) and `### Fixed` (the sidebar-dedup bullet). The next release-prep phase promotes all six bullets into its own versioned section — the same mechanism by which Phase 63 promoted Phase 61's bullets into `## [0.9.2]`. Whether the next published release is `0.9.3`, `0.9.4`, `0.9.5` or another number belongs to that milestone's own scoping, not to this handoff.

## Before and after phase.complete-family tooling

Reproduced from `73-CLOSEOUT-GUARD.md` § "For the operator running phase.complete", so an operator following this handoff reaches the procedure without opening that file separately.

This section applies after this phase's plans have finished, at **whichever of the two entry points runs**: `phase.complete` reached from `/gsd-execute-phase`, or `/gsd-verify-work`'s inline transition — the same underlying verb, reached through two different entry points. Both entry points must be treated as equally likely to trigger the flip; neither is safer to assume clean than the other.

**Before either runs:** back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` to a scratch directory outside the repository (e.g. `/tmp/scratch-73-closeout/`), so a hand-edited STATE.md or ROADMAP.md rewrite that the tooling itself corrupts has a known-good copy to diff against, not only `.planning/REQUIREMENTS.md`.

**After it runs**, re-run these probes, with the baseline digest and grep lines written out inline here so the reader needs no other file open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad

wc -l .planning/REQUIREMENTS.md
# compare against: 70

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-14' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   22:- [ ] **REL-14**: Close prep only, unpublished. CHANGELOG bullet(s) go under the existing `## [Unreleased]`, in the register of the four bullets already there, and name the docs sidebar fix and the new `tox -e linkcheck` environment (owner decision 2026-09-13; revised the same day when QUA-08, the CI job, was deferred — no bullet may claim a CI job that does not exist). `pyproject.toml` stays `0.9.2`. There is no tag, no PyPI upload and no GitHub Release. The milestone branch is merged to `main` through a PR, as REL-12 and REL-13 were. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, and never by phase-completion tooling.
#   57:| REL-14 | Phase 73 | Pending |
#   62:- Mapped to phases: 4 (Phase 72: QUA-13, DOC-24, DOC-18 · Phase 73: REL-14)
#   65:- REL-14 is mapped to Phase 73 for coverage only; its checkbox is checked at
```

**The reversion:** `git checkout -- .planning/REQUIREMENTS.md`, then re-run the probes above to show a MATCH, and then diff `.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch backup — reverting either if it, too, carries an unwarranted change from the same tooling run.

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts until every probe above shows MATCH. This is the explicit rule this project has followed at every prior release-prep close where the flip was caught: revert first, report second, never ship the flipped state as part of the phase's own close.

**The history.** The flip has landed at **8 of the 9** prior release-prep closes (`ROADMAP.md` binding constraint 10; `73-CLOSEOUT-GUARD.md` §§ "Why this file exists"). It did **not** fire at Phase 71 (v0.9.4's close, REL-13) — one non-firing close is not treated as a fix; the mechanism that produced 8 flips before it is unchanged. It has landed through both entry points, `phase.complete` from `/gsd-execute-phase` and `/gsd-verify-work`'s inline transition, in the same close before (Phase 63).

## Fence observation

Recorded live, at this task's own time, inside plan 73-07's own worktree:

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ sha256sum .planning/REQUIREMENTS.md
7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad  .planning/REQUIREMENTS.md

$ git tag -l 'v0.9.3'
(no output)

$ git tag -l 'v0.9.4'
(no output)

$ git tag -l 'v0.9.5'
(no output)

$ git status --porcelain typsphinx/ tests/ CHANGELOG.md pyproject.toml uv.lock .planning/REQUIREMENTS.md
(no output)

$ git diff --name-only a54a2d8a3b06b388c7ee004e5cfbe3405431421d HEAD -- . ':(exclude).planning'
(no output)
```

Empty diff, digest equal to `REQ_SHA256_BASE` (`7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad`), no local `v0.9.3`, `v0.9.4` or `v0.9.5` tag, every named product/tracking path clean, and the product tree unchanged since `PUSHED_SHA` — the tip CI actually tested (`73-CI-EVIDENCE.md`'s `RUN_ID = 35083828156`) is the product tree of this plan's own tip.

```
$ awk '/^### Phase 73:/{f=1} f && /^## Progress/{exit} f' .planning/ROADMAP.md | grep -c 'UI hint'
0
```

The Phase 73 section of `.planning/ROADMAP.md` carries no UI-hint line — the `ui.plan-gate` false positive on this phase's docs/navigation wording was handled at plan time with `--skip-ui` (D-15), not with an explicit `**UI hint**: no` marker.

This matches `73-CLOSEOUT-GUARD.md`'s `REQ_VERDICT_CLOSE = MATCH` and `73-SC1-INVARIANTS.md`'s two observations.

## What this phase deliberately did not do

- No tag, local or remote.
- No `release.yml` run — only `ci.yml` was dispatched, on the phase's single intended tip, in 73-04 (D-12).
- Nothing uploaded to PyPI.
- No GitHub Release.
- No version bump.
- No pull request opened, merged or commented on.
- No `origin/main` merged into the branch — that merge, since `main` has moved, is deferred to step 2 above, at `/gsd-complete-milestone`.
- No `update-pin.yml` dispatch on `typsphinx-doc-translations`.
- No action on any of #146–#150 or any other Dependabot pull request (D-06) — all five merged on their own, through Dependabot's automation, entirely outside this phase's control.
- No `.planning/REQUIREMENTS.md` edit of any kind — no checkbox flip, no Traceability-row change, no other edit (D-08).
- No product-tree change beyond `CHANGELOG.md`, and no `docs/source/conf.py` linkcheck key.
- No UI-hint line added to the ROADMAP (D-15).
- One push and one `ci.yml` dispatch only, in 73-04 (D-12).

This handoff contains no command that tags, creates a release, or dispatches the translations-repository pin workflow.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 07*
