# Phase 71: v0.9.4 Close Prep — Handoff for /gsd-complete-milestone

**This milestone publishes nothing.** No tag is created, locally or on the remote; nothing is uploaded to PyPI; no GitHub Release is created; and `pyproject.toml` stays at `0.9.2` — no version bump lands with this close.

The `typsphinx-doc-translations` `update-pin.yml` dispatch and the Read the Docs `stable` check are both **not applicable** to this close: neither project has anything new to track when no tag and no GitHub Release exist for this repository. Recorded as a fact, not a step: the daily `update-pin.yml` schedule moves the Japanese `latest` site onto the merged `main` within about a day, with no action from anyone. The Japanese `stable` site is unchanged, because it follows the translations repository's own tags, not `main`.

The one irreversible action this close performs is **REL-13**: a pull request from `gsd/v0.9.4-typing-modernization` to `main`, opened and merged at `/gsd-complete-milestone`, as v0.9.3's REL-12 was with PR #143.

Every other v1 requirement of this milestone (QUA-09, QUA-11, QUA-12, DOC-22, DOC-23) already closed in Phase 70; REL-13 is the sole requirement this phase carries, and it is held open by design until the PR below actually merges — never flipped inside a plan.

CI stays exactly as it was before this milestone: no workflow file is edited anywhere in this phase or by this handoff's own steps.

Everything below this line is either a step this handoff hands to `/gsd-complete-milestone` to run, or a record of what this phase already measured and left untouched — no prose past this point should be read as an instruction already carried out inside Phase 71 itself.

## What /gsd-complete-milestone does, in order

0. **Fence first.** Back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` to a scratch directory outside the repository (e.g. `/tmp/scratch-71-closeout/`). Then run the § 4 probes below, and start only on a MATCH.

1. **Re-run the trial merge.**
   - `git fetch origin`, then `git merge-tree --write-tree HEAD origin/main; echo "exit:$?"`, which requires `exit:0`.
   - Cite `71-PREFLIGHT-EVIDENCE.md`'s `MERGE_TREE` (`0fc0c03a5fc3cb730542fde7a1c11f01b90205fe`), `MAIN_MOVED` (`no`), `LOCK_CHECK_EXIT` (`0`), `MERGED_RUFF_LOCK_VERSION` (`0.16.6`) and `TRIAL_MERGE_VERDICT` (`MET`) as the phase-time result. That tree SHA changes with every commit on either ref, so `merge-tree` is re-run here, not copied.
   - Then `git merge-base --is-ancestor origin/main HEAD; echo "exit:$?"`. `exit:0` means `main` has not moved past the merge-base — today's `MAIN_MOVED = no`. `exit:1` means it moved: re-run the scratch `uv lock --check` and the merged-tree `ruff check .` and `black --check .` exactly as `71-PREFLIGHT-EVIDENCE.md` § "Merged lock" and § "Merged-tree lint" did. Under constraint 4, a moved `main`'s `ruff` count is authoritative, and a finding is the owner's decision before step 4.

2. **Conditional branch update (D-06).** Only if step 1 printed `exit:1`: in the main checkout, on `gsd/v0.9.4-typing-modernization`, run `git merge --no-ff origin/main -m "Merge origin/main into gsd/v0.9.4-typing-modernization"`. Never rebase the milestone's commits. Then run `uv lock --check`, then `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`; the docs extra is named because a bare `--extra dev` exact sync drops it from the main checkout. Re-check that `git merge-base --is-ancestor origin/main HEAD` now exits 0. **Otherwise, record this step as a no-op with step 1's `exit:0` output** — that is today's expected outcome, since `origin/main` (`d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d`) equals `MILESTONE_BASE` exactly and there is nothing to absorb. The reason this step exists at all: `main`'s protection is `strict: true` (`71-PREFLIGHT-EVIDENCE.md` § "main protection (D-06)"), so the pull request cannot merge until the branch is up to date.

3. **Push.** `git push --no-follow-tags origin gsd/v0.9.4-typing-modernization`, a fast-forward from `71-CI-EVIDENCE.md`'s `PUSHED_SHA` (`7a42bf996b1aaca24a8b17346be78459e6d41e2b`). It carries this phase's later `.planning/` commits, and the merge commit if step 2 ran.

4. **Open the pull request.** `gh pr create --base main --head gsd/v0.9.4-typing-modernization --title <English title> --body-file <file>`. Title and body are English and terse. The body goes through a file, never through a command substitution.

5. **Wait for the required checks.** Wait for all six to be green on the pull request head, named literally: `Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Lint and Format Check`, `Type Check`, `Code Coverage` and `Build Package`. The `pull_request` trigger runs the whole twelve-job `ci.yml`; the six named above are only the ones branch protection requires.

6. **Merge.** `gh pr merge <number> --merge`: a merge commit, never squash or rebase. Cite `71-PREFLIGHT-EVIDENCE.md` § "Merge-method precedent (D-06)": `#135`, `#136` and `#143` (`MERGE_PRECEDENT_HITS = 3`) are all `Merge pull request` commits on `main`'s first-parent history, with every dependabot/docs PR reaching `main` in between merged the same way — never a squash or a rebase.

7. **Observe what REL-13 requires, then close it** (SC#4, D-07).
   - The merge commit is on `origin/main`: `git log --first-parent -1 --format='%h %s' origin/main`.
   - `git show origin/main:pyproject.toml | sed -n 7p` reads `version = "0.9.2"`.
   - `git ls-remote --tags origin` shows `refs/tags/v0.9.2` and no `v0.9.4` tag.
   - PyPI returns `404` for `0.9.4` and `200` for `0.9.2`, the positive control.
   - `gh release list` shows no `v0.9.4` Release.

   Only on those five observations is REL-13's box checked, at `/gsd-complete-milestone`, never inside a plan.

8. **Not applicable.** No tag; no `release.yml` run; no PyPI upload; no GitHub Release; no `update-pin.yml` dispatch on `typsphinx-doc-translations`; no Read the Docs `stable` check. Read the Docs `latest` rebuilds from `main` and then shows the four `## [Unreleased]` bullets, which needs no action.

## What this phase satisfied

**REL-13**, quoted verbatim from `.planning/REQUIREMENTS.md:24`:

> - [ ] **REL-13**: Close prep only, unpublished: one CHANGELOG bullet under the existing `## [Unreleased]`, in the register of the three bullets already there, naming the API-reference type-text change and noting that the ja translation catalogs pick it up at the next published release; `pyproject.toml` stays `0.9.2`; no tag, no PyPI upload, no GitHub Release. The milestone branch is merged to `main` through a PR, as v0.9.3's REL-12 was. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge — never by phase-completion tooling.

**Its AMENDED block (D-02, `.planning/REQUIREMENTS.md:26-34`) governs this bullet's actual content**: the sentence quoted above still literally names "the ja translation catalogs pick it up at the next published release", but the owner withdrew that clause before any bullet was written — measurement showed the `ja` `latest` site follows `main`'s daily `update-pin.yml` schedule, not a release, and the `ja` API reference is untranslated (0/668 msgids). The CHANGELOG bullet `71-01` authored (`CHANGELOG.md`) carries no Japanese-site wording at all; `71-CHANGELOG-EVIDENCE.md` § "Bullet content assertions" measures `JAPANESE_SITE_WORDS = 0`. **REL-13 stays open until step 7 above runs.** No plan in this phase — including this one — touched its checkbox; every SUMMARY of this phase declares `requirements-completed: []`.

Reporting ROADMAP SC#1 through SC#4, each citing its own evidence file and section rather than re-deriving the verdict:

- **SC#1** (the tree is proven unpublished-shaped, twice, at separated timestamps, with no code change slipped in) — **MET**. `71-SC1-INVARIANTS.md` § "Observation 1 of 2" (`OBS1_AT = 2026-09-13T08:31:24Z`) and § "Observation 2 of 2" (`OBS2_AT = 2026-09-13T09:11:36Z`, 40m12s later, spanning wave 2's local green-tree proof, the phase's only push and CI dispatch, and the trial-merge pre-flight), both with the same positive-controlled version/tag/PyPI/GitHub-Release/release-workflow/PR probes and identical results. § "The phase-scoped product diff" — empty over `typsphinx/` and `tests/` from `PHASE_BASE_SHA`, with the widened `--numstat` diff proving the anchor real (exactly `CHANGELOG.md`, +10/−0). § "Code freeze on the close tip (D-11 part 1)" and § "Masked-AST re-run on the close tip (D-11 part 2)": all ten of Phase 70's converted files' masked hashes equal their `PHASE_BASE_SHA` (Phase 70's `697a1132…`) counterparts, non-vacuously (two mutation controls both DIFFER), cross-checked against Phase 70's own leg (a) table (`PHASE70_TABLE_MATCH = 10`). `D11_VERDICT = MET`.
- **SC#2** (the milestone's CHANGELOG bullet lands under `## [Unreleased]`, no version literal moves) — **MET**. `71-CHANGELOG-EVIDENCE.md` § "Fence assertions" (headings/link-refs counts unchanged at 23, `### Planned for Future Releases` byte-identical `PLANNED_SHA`, `VERSION_LITERALS_AFTER = 0`) and § "Pure-addition proof" (`ADDED_LINES = 10`, `REMOVED_LINES = 0`, `DIFF_HUNKS = 1`) and § "Bullet content assertions" (`BULLET_ID_SPAN = present`, `TYPE_EXAMPLE = present`, `JAPANESE_SITE_WORDS = 0`). `71-GREEN-TREE-EVIDENCE.md` § "Changelog page gate": `CHANGELOG_GATE_SUMMARY = 6 passed`, `CHANGELOG_GATE_SKIPPED = 0` — every build class (delegation, HTML content coverage, PDF include-compile) actually executed, in an environment carrying the `docs` extra.
- **SC#3** (the tree is proven green on runs executed in this phase, including a non-committing trial merge against `main` at close) — **MET**. Set side by side:

  | Measurement | Local (`71-GREEN-TREE-EVIDENCE.md`) | CI (`71-CI-EVIDENCE.md`) | Trial merge (`71-PREFLIGHT-EVIDENCE.md`) |
  |---|---|---|---|
  | Full suite | `FULL_SUMMARY = 1547 passed, 1 skipped` | — | — |
  | Full suite, `LC_ALL=C` | `LCALLC_SUMMARY = 1547 passed, 1 skipped` | — | — |
  | `ruff` version | `RUFF_LOCAL_VERSION = 0.16.6` | `CI_RUFF_VERSION = 0.16.6` | `MERGED_RUFF_LOCK_VERSION = 0.16.6` |
  | Lint/format exit | `RUFF_LOCAL_EXIT = 0`, `BLACK_EXIT = 0`, `MYPY_EXIT = 0` | ruff's verdict quoted from `Lint and Format Check`: `All checks passed!` | `MERGED_RUFF_EXIT = 0`, `MERGED_BLACK_EXIT = 0` |
  | Docs clean-build counts | `DOCS_HTML_WARN_FINAL = 3` = `DOCS_HTML_WARN_BASE`; `DOCS_PDF_WARN_FINAL = 5` = `DOCS_PDF_WARN_BASE` (`71-CHANGELOG-EVIDENCE.md`) | — | — |
  | Run identity / verdict | — | `RUN_ID = 34748483361`, `JOB_COUNT = 12`, `NON_SUCCESS_JOBS = 0`, both `windows-latest` and both `macos-latest` lanes `success`, `JOB_NAMES_MATCH_PHASE70 = yes` | `MERGE_RC = 0`, `LOCK_CHECK_EXIT = 0` |
  | Verdict | `SC3_LOCAL_VERDICT = MET` | `SC3_CI_VERDICT = MET` | `TRIAL_MERGE_VERDICT = MET` |

  **The `DISPATCH_COUNT` note (owner-approved AMENDED reading — see below), qualifying "exactly one dispatch".** During 71-04 the CI dispatch API (`gh workflow run CI --ref …`) returned HTTP 500/502 on repeated calls; one of those "failed" calls actually created a run server-side, and a retry created a second. Two `workflow_dispatch` CI runs carry `PUSHED_SHA` (`7a42bf996b1aaca24a8b17346be78459e6d41e2b`): `34748483361` (`success`, `RUN_ID`, 12/12 jobs) and `34748491771` (`cancelled`, no failed job). The owner chose to keep the Actions history (no `gh run delete`) and read "exactly one dispatch" as **"exactly one success run at `PUSHED_SHA`, and it is `RUN_ID`; the only other is the cancelled `34748491771`"** — see `71-CI-EVIDENCE.md` § "AMENDED 2026-09-13 — dispatch count" and `71-SC1-INVARIANTS.md` § "Commits after the CI dispatch" for the full transcript and re-measurement. This does not weaken SC#3's CI verdict: `SC3_CI_VERDICT = MET` is on `RUN_ID`'s own merits (12/12 jobs `success`), independent of the dispatch-count bookkeeping.

- **SC#4** (the REL-13 checkbox is proven held by a recorded SHA-256, and the handoff is standalone) — **MET**. `71-CLOSEOUT-GUARD.md` § "Re-verification at phase close" (`REQ_VERDICT_CLOSE = MATCH`), and this file.

**The D-10 statement.** The single intended dispatch ran on `PUSHED_SHA` (`7a42bf996b1aaca24a8b17346be78459e6d41e2b`), the tip carrying every product-tree change of the phase (the `CHANGELOG.md` edit from 71-01 and the fences from 71-02), and every later commit of the phase is `.planning/`-only (`71-SC1-INVARIANTS.md` § "Commits after the CI dispatch": `POST_DISPATCH_PRODUCT_FILES = 0`, no `release.yml` run at `PUSHED_SHA`). Also qualified by the same AMENDED reading above — the "single dispatch" is the one `success` run at that tip, `RUN_ID`; the cancelled `34748491771` never reached a terminal green-or-red conclusion before the discovery of the anomaly and reported no failed job.

## Recorded without acting

**D-12.** The open-PR census from `71-PREFLIGHT-EVIDENCE.md` § "Open pull requests (D-12)":

```
PR_CENSUS_AT = 2026-09-13T08:48:59Z
OPEN_PRS = 0
DEPENDABOT_OPEN_PRS = 0
```

**Live re-read, taken during this plan's own execution:**

```
$ date -u +%FT%TZ
2026-09-13T09:30:06Z

$ gh pr list --state open --json number,title,author,headRefName,baseRefName
[]
```

No pull request is open at either census time; there is no dependabot PR to name. This phase took no merge, close, comment or rebase-request action on any pull request. A dependabot `ruff` bump merged to `main` after this point is caught by step 1's re-run `merge-tree` and trial-merge lint (constraint 4), not by this census.

**D-08.** The `0.9.3` and `0.9.4` version numbers are both recorded as **unclaimed, not decided**. After this phase, `## [Unreleased]` holds four bullets from two unpublished milestones: three from v0.9.3 (`tox-uv`, Dependabot `uv`, `flake.nix`) and this phase's own (`71-01`'s typing-modernization bullet). The next release-prep phase promotes all four bullets into its own versioned section — the same mechanism by which **Phase 63** promoted Phase 61's bullets into `## [0.9.2]`. Whether the next published release is `0.9.3`, `0.9.4` or another number belongs to that milestone's own scoping, not to this handoff.

## Before and after phase.complete-family tooling

Reproduced from `71-CLOSEOUT-GUARD.md` § "For the operator running phase.complete", so an operator following this handoff reaches the procedure without opening that file separately.

This section applies after this phase's plans have finished, at **whichever of the two entry points runs**: `phase.complete` reached from `/gsd-execute-phase`, or `/gsd-verify-work`'s inline transition — the same underlying verb, reached through two different entry points. Both entry points must be treated as equally likely to trigger the flip; neither is safer to assume clean than the other.

**Before either runs:** back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` to a scratch directory outside the repository (e.g. `/tmp/scratch-71-closeout/`), so a hand-edited STATE.md or ROADMAP.md rewrite that the tooling itself corrupts has a known-good copy to diff against, not only `.planning/REQUIREMENTS.md`.

**After it runs**, re-run these probes, with the baseline digest and grep lines written out inline here so the reader needs no other file open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636

wc -l .planning/REQUIREMENTS.md
# compare against: 80

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-13' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   24:- [ ] **REL-13**: Close prep only, unpublished: one CHANGELOG bullet under the existing `## [Unreleased]`, in the register of the three bullets already there, naming the API-reference type-text change and noting that the ja translation catalogs pick it up at the next published release; `pyproject.toml` stays `0.9.2`; no tag, no PyPI upload, no GitHub Release. The milestone branch is merged to `main` through a PR, as v0.9.3's REL-12 was. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge — never by phase-completion tooling.
#   33:  wrong for the same reason. Every other part of REL-13 stands, including when this checkbox is
#   71:| REL-13 | Phase 71 | Pending — coverage only; checked at `/gsd-complete-milestone` on the observed merge, never by phase-completion tooling |
#   75:- Mapped to phases: 6 (Phase 70: 5 — QUA-09, QUA-11, QUA-12, DOC-22, DOC-23; Phase 71: 1 — REL-13)
```

**The reversion:** `git checkout -- .planning/REQUIREMENTS.md`, then re-run the probes above to show a MATCH, and then diff `.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch backup — reverting either if it, too, carries an unwarranted change from the same tooling run.

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts until every probe above shows MATCH. This is the explicit rule this project has followed at every prior release-prep close where the flip was caught: revert first, report second, never ship the flipped state as part of the phase's own close.

**The history.** The flip has landed at **eight consecutive** prior release-prep closes (`ROADMAP.md` binding constraint 10). The most recent was **REL-12 at the Phase 69 close** (v0.9.3): caught by the third observation after `phase.complete` and reverted before any commit (`69-CLOSEOUT-GUARD.md` § "Third observation (after phase.complete, orchestrator)"; `69-HANDOFF.md` § "Before and after phase.complete-family tooling"). It has landed through both entry points in the same close before (Phase 63, through both `phase.complete` and `/gsd-verify-work`'s inline transition in the same close).

## Fence observation

Recorded live, at this task's own time, inside plan 71-07's own worktree:

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ sha256sum .planning/REQUIREMENTS.md
4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636  .planning/REQUIREMENTS.md

$ git tag -l 'v0.9.3'
(no output)

$ git tag -l 'v0.9.4'
(no output)

$ git status --porcelain typsphinx/ tests/ CHANGELOG.md pyproject.toml uv.lock .planning/REQUIREMENTS.md
(no output)

$ git log --format=%H -1 -- typsphinx/ tests/
e721ff899a981eafdad696ef1a9c93aaab41ece5

$ git diff --quiet 9c66a8505e36af774af9d6c4260206a697a7b0d4 HEAD -- typsphinx/ tests/; echo "exit:$?"
exit:0
```

Empty diff, digest equal to `REQ_SHA256_BASE` (`4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636`), no local `v0.9.3` or `v0.9.4` tag, every named product/tracking path clean, the last commit touching `typsphinx/`/`tests/` still equal to `CODE_FREEZE_ANCHOR` (`e721ff899a981eafdad696ef1a9c93aaab41ece5`), and `git diff --quiet` against `BASE_71_06` (`9c66a8505e36af774af9d6c4260206a697a7b0d4`, read from `71-SC1-INVARIANTS.md`) over `typsphinx/`/`tests/` exits `0`. The ten files 71-06 hashed under Phase 70's masked-AST harness are unchanged on this tip (D-11), and the fence holds, matching `71-CLOSEOUT-GUARD.md`'s `REQ_VERDICT_CLOSE = MATCH` and `71-SC1-INVARIANTS.md`'s two observations.

## What this phase deliberately did not do

- No tag, local or remote.
- No `release.yml` run — only `ci.yml` was dispatched, on the phase's single intended tip, in 71-04 (D-10).
- Nothing uploaded to PyPI.
- No GitHub Release.
- No version bump.
- No pull request opened, merged or commented on.
- No `origin/main` merged into the branch (D-05) — that merge, if `main` has moved by then, is deferred to step 2 above, at `/gsd-complete-milestone`.
- No `update-pin.yml` dispatch on `typsphinx-doc-translations`.
- No action on any open pull request (D-12).
- No `.planning/REQUIREMENTS.md` edit of any kind — no checkbox flip, no Traceability-row change, no other edit (D-02, D-09).
- No change under `typsphinx/`, `tests/`, `.github/`, `pyproject.toml` or `uv.lock`.
- One push and one `ci.yml` dispatch only, in 71-04 (D-10).

This handoff contains no command that tags, creates a release, or dispatches the translations-repository pin workflow.

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Plan: 07*
