# Phase 75 — Handoff to /gsd-complete-milestone

This document is standalone: every number it cites is written into it, not linked. A reader with
only this file can execute the whole release, in order.

## What this phase satisfied

**REL-15**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **REL-15**: v0.9.6 is published. `pyproject.toml` goes `0.9.2` → `0.9.6` as the sole version
> literal, with `uv.lock` regenerated in the same change and `uv sync --extra dev --locked` green.
> The six bullets standing under `## [Unreleased]` — carried from v0.9.3, v0.9.4 and v0.9.5 — are
> promoted into a new `## [0.9.6]` section together with this milestone's own bullets, and the link
> block at the file's end is updated in the same phase: the `[Unreleased]` compare target moves up
> to `v0.9.6` and a `[0.9.6]` releases/tag link is added. The milestone branch merges to `main`
> through a PR with CI green across the Linux, Windows and macOS lanes; tag `v0.9.6` is pushed;
> `release.yml` publishes the wheel and sdist to PyPI and creates the GitHub Release. **This
> checkbox is checked only at `/gsd-complete-milestone`, against observed evidence (merge commit on
> `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`, and
> `gh release list`), and never by phase-completion tooling** — `phase.complete` has flipped REL
> rows against an explicit decision before. Note that `release.yml`'s `create-release` job has
> end-to-end evidence from the v0.7.1 publish (run `31462027486`) and v0.8.0 (run `31861043480`)
> but has never run on a v0.9.x tag.

REL-15 stays open until step 6 of the checklist below runs. No plan in this phase touched its
checkbox, and every `75-0N-SUMMARY.md` of this phase declares `requirements-completed: []`. The
fence in `75-CLOSEOUT-GUARD.md` re-verified this at phase close and MATCHed the phase-head
baseline; the digest, `REQ_SHA256_BASE = 481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f`,
was still the live digest at close.

**REL-16 is different.** It closes inside this phase. Its `### Known Limitations` section is in
`## [0.9.6]` of `CHANGELOG.md`, and its checkbox and Traceability row may legitimately move to
`[x]` / `Complete` when phase-completion tooling runs — this is precisely why the REQUIREMENTS
fence this phase carries is line-scoped to REL-15 rather than whole-file.

## Success criteria

| SC | Verdict | Evidence |
|----|---------|----------|
| SC1 | MET | `75-BUMP-EVIDENCE.md`: the one five-file commit `84edd348b52f1f7e95073d2b3ebcbcd36417bc15` (`BUMP_COMMIT_FILES = CHANGELOG.md\|README.md\|pyproject.toml\|tests/test_changelog_page_gate.py\|uv.lock`), `uv lock --check` and a locked sync both exit 0, and the changelog page gate runs zero skips (`CHANGELOG_GATE_SKIPS = 0`). |
| SC2 | MET | `75-CHANGELOG-EVIDENCE.md`: the extractor's stdout (`scripts/extract_changelog_section.py 0.9.6`, 7104 bytes) is byte-identical to the committed `## [0.9.6]` section — both digests `f9a52e3de808bd49981658a1169e96e761fd409432c45fa2f350c5acad0f59be` (`EXTRACT_MATCHES_SECTION = yes`). |
| SC3 | MET | `75-SC5-INVARIANTS.md` § "REL-16 settlement": the anchored `### Known Limitations` heading count is 2 (the pre-existing `[0.1.0b1]` entry plus the new `## [0.9.6]` entry), and the decision record and the CHANGELOG agree (`REL16_AGREEMENT = yes`). |
| SC4 | MET | Local half `75-GREEN-TREE-EVIDENCE.md` (`SC4_LOCAL_VERDICT = MET`, amended 2026-09-20 by owner decision on the three linkcheck records — see below); CI half `75-CI-EVIDENCE.md` run id `35507024851` on `PUSHED_SHA = b63e5d453d604350b55c51a1a77918985d6dad7c`, `JOB_COUNT = 12`, `NON_SUCCESS_JOBS = 0` (`SC4_CI_VERDICT = MET`); trial-merge half `75-PREFLIGHT-EVIDENCE.md` (`TRIAL_MERGE_VERDICT = MET`). |
| SC5 | MET | `75-CLOSEOUT-GUARD.md` § "Re-verification at phase close" (`FENCE_CLOSE_VERDICT = MATCH`) and `75-SC5-INVARIANTS.md` § "Scope fence" (`SC5_VERDICT = MET`). |

**SC4's linkcheck amendment, stated plainly here so it is not mistaken for an unqualified clean
run.** `tox -e linkcheck` returned 3 broken records out of 96 on the bumped tip
(`TIP_LINKCHECK_TOTAL = 96`, `TIP_LINKCHECK_WORKING = 93`). The project owner amended SC4's
linkcheck reading on 2026-09-20 (`75-GREEN-TREE-EVIDENCE.md` § "AMENDED 2026-09-20") to
"`working` plus the classified, controlled exceptions equals `total`", rather than
`working == total` unconditionally. Two of the three records — `changelog.rst:8`
(`.../compare/v0.9.6...HEAD`) and `changelog.rst:17` (`.../releases/tag/v0.9.6`) — are **Class A:
structurally unreachable before the tag exists**, a **carried obligation, not a waiver** — see the
checklist item 2 note below, which is the step that closes Class A. The third,
`changelog.rst:474` (`https://pypi.org/project/typsphinx/#history`), is **Class B: not a broken
link** — PyPI's page returns 200 behind a bot-mitigation interstitial with no anchors, filed as a
pending todo rather than a release blocker (the same treatment IN-01 got). No product file was
edited to reach this reading, and the prep-only fence is intact.

## Checklist

Numbered steps, each with an **Owner** line and an **Ordering** line, in the order they must
execute.

### 1. Open the pull request from `gsd/v0.9.6-doctest-block-rendering-and-release` to `main` and merge it

**Owner:** `/gsd-complete-milestone`.
**Ordering:** first; everything below depends on it.

The required status checks, verbatim from `75-PREFLIGHT-EVIDENCE.md`'s `PROTECTION_CONTEXTS`
(`strict: true`): `Build Package`, `Code Coverage`, `Lint and Format Check`,
`Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Type Check`. Because
`strict` is set, if `origin/main` has moved since this phase's close, merge it into the branch
first and re-run CI before merging the pull request — do not merge against a stale base.
`75-PREFLIGHT-EVIDENCE.md`'s trial merge was clean at `MERGE_TREE = 96d8ca9e9317b25a5ca57c76f7bd75ae88e5340f`,
idempotent across two separate `git merge-tree` invocations, and the merged tree passed
`uv lock --check`, a locked sync, `ruff check .` (ruff 0.16.7) and `black --check .`, still
carrying `version = "0.9.6"`. `MAIN_MOVED` read `no` at this phase's own close — `origin/main` was
still at the milestone base `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b`. `origin/main` must be
re-read live at release time regardless, because it can move between this phase's close and
`/gsd-complete-milestone`'s own run. The observed merge method: every one of the 103 first-parent
`Merge pull request #` hits on `origin/main`, including the five most recent milestone PRs
(#132, #136, #143, #145, #151), landed as a real merge commit, not a squash or rebase — the
release PR should be expected to do the same, though the repository configuration allows all
three methods.

### 2. Push the `v0.9.6` tag on the merge commit

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after step 1.

Pushing `v0.9.6` fires `.github/workflows/release.yml`. No tag exists anywhere as of this phase's
close — local `git tag -l 'v0.9.6'` empty, remote `git ls-remote --tags origin` carries no
`v0.9.6` ref, both re-confirmed at observation 2 of 2 in `75-SC5-INVARIANTS.md`, with the
`v0.9.2` positive control present in both.

**This step is also where Class A of the linkcheck amendment above closes.** Once the tag and the
GitHub Release exist (after step 3 below), re-run `tox -e linkcheck` and confirm
`changelog.rst:8` and `changelog.rst:17` now resolve — both should turn green, since the only
missing input for either was the tag itself. If either record is still broken after the tag and
Release exist, treat it as a genuine regression and investigate before considering this phase's
linkcheck obligation discharged; do not silently re-amend the reading a second time.

### 3. Let `release.yml` run to completion: `validate`, `build`, `publish-pypi`, `create-release`

**Owner:** `/gsd-complete-milestone`, with a human approval step.
**Ordering:** after step 2.

The `pypi` GitHub Environment requires a **manual approval** step before `publish-pypi` runs —
waiting there is a gate, not a failure; every prior release in this project's history has
exercised the same gate. `create-release` has real end-to-end evidence from the v0.7.1 publish
(run `31462027486`) and the v0.8.0 publish (run `31861043480`), both `success`, but **has never
run on a v0.9.x tag** — v0.9.1 through v0.9.5 were all unpublished or merge-only. A failure in
`create-release` on this tag is handled inside the release work itself, not deferred to a later
phase, the way v0.7.0's `uv: command not found` failure was repaired on `main` and then only
exercised at the next tag push. `release.yml`'s job order is `validate` → `build` →
`publish-pypi` → `create-release` (`.github/workflows/release.yml`). The GitHub Release body
comes from `scripts/extract_changelog_section.py 0.9.6`, run inside the `create-release` job's
"Generate release notes" step; the published body must be checked byte-identical against that
extractor's own stdout — transcribed verbatim in `75-CHANGELOG-EVIDENCE.md` § "Extractor
transcript" (7104 bytes, digest `f9a52e3de808bd49981658a1169e96e761fd409432c45fa2f350c5acad0f59be`).

### 4. Dispatch `update-pin.yml` in `typsphinx-doc-translations`

**Owner:** human plus `/gsd-complete-milestone`.
**Ordering:** after step 3.

This dispatch is **manual** and does **not** happen as a side effect of the parent repository's
tag push — it is a standing per-release cost on the second repository, exactly as it was at every
prior published release (v0.6.4 through v0.9.2). It advances the submodule pin to the `v0.9.6`
merge commit and tags `typsphinx-doc-translations` with a matching `v0.9.6` tag, resyncing the
`ja` catalogs in the same run.

### 5. Confirm Read the Docs `stable` on both projects

**Owner:** human, via the unauthenticated public API or real fetches.

Both the `en` (`typsphinx`) and `ja` (`typsphinx-ja`) `stable` endpoints must report `0.9.6` after
step 4, read via Read the Docs' unauthenticated public API (`readthedocs.org`) or real fetches
against `https://typsphinx.readthedocs.io/`. Publishing is what moves `stable` — both projects'
Default Versions have been `stable` since the v0.6.4 close and have needed no re-flip at any
subsequent close, so no default-version setting change is expected or in scope here; this step is
a confirmation, not a configuration change.

### 6. Check REL-15's checkbox and its traceability row

**Owner:** `/gsd-complete-milestone`.
**Ordering:** last, and only against the **four observations** REL-15's own text names:

1. The merge commit on `origin/main`'s first-parent history.
2. `git ls-remote --tags origin` showing `v0.9.6`.
3. A PyPI 200 for `0.9.6`.
4. `gh release list` showing a `v0.9.6` Release.

**Standing warning.** Phase-completion tooling has flipped this row against an explicit decision
at 9 of the 10 prior release-prep closes (`75-CLOSEOUT-GUARD.md` § "Why this file exists"). The
flip must be the operator's own action, made here, against the four observations above — never an
automatic side effect of `phase.complete` or `/gsd-verify-work`'s inline transition.

### 7. Do not re-date the `## [0.9.6]` heading

**Owner:** nobody — this is a fact, not a step.

The `## [0.9.6] - 2026-09-20` heading carries the **prep** authoring date and may differ from the
actual tag date; precedent: `[0.9.2] - 2026-08-30` merged a day later (tagged 2026-08-31),
`[0.9.0] - 2026-08-17` tagged five days later (2026-08-22). `/gsd-complete-milestone` does not
rewrite this heading. Re-confirm the extractor still returns the intended body instead
(`uv run python scripts/extract_changelog_section.py 0.9.6`, exit 0, non-empty, the curated
section verbatim) — idempotent, so re-running it at close is safe and cheap.

## Recorded without acting

**Dependabot and open pull requests.** Quoted from `75-PREFLIGHT-EVIDENCE.md`: `OPEN_PRS = 0`,
`DEPENDABOT_OPEN_PRS = 0`, `PR_CENSUS_AT = 2026-09-20T09:03:37Z`. Both are 0 at that reading —
there is no merge-ordering question as of this phase's own execution.

**Live re-read, taken during this task's own execution:**

```
$ gh pr list --state open --json number --jq 'length'
0
```

```
HANDOFF_OPEN_PRS_LIVE = 0
HANDOFF_OPEN_PRS_AT = 2026-09-20T11:29:40Z
```

The live count agrees with `75-PREFLIGHT-EVIDENCE.md`'s reading — no drift between that census and
this task's own moment.

**The ordering rule, stated conditionally.** If any Dependabot pull request is open when the
release actually runs, order it **after** the milestone pull request — the order v0.9.3 used
(#143 first, then #142 and #141 merged afterward). If none is open, there is no ordering question
and this rule is a no-op. The Dependabot branch census drifted measurably within a single
calendar day before this phase ran (75-05's own note that the discussion-time reading and the
research-time reading disagreed), so the operative reading for `/gsd-complete-milestone` is a
fresh one taken at release time, not either of those two stale figures and not this task's own
live re-read above either — re-read again at the moment the release actually runs.

## Deferred with this phase

- **IN-01**, filed by 75-02 as a pending todo:
  `.planning/todos/pending/2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node.md`.
  `visit_literal_block` / `depart_literal_block`'s `Args:` docstring text still names only "The
  literal block node" although both signatures were widened this milestone to
  `nodes.literal_block | nodes.doctest_block`.
- **MSG-06** — still pending (`translator.py`'s two relative-path DEBUG logs use a hardcoded
  `'...'` delimiter instead of `quote_path()`).
- **QUA-08** — still pending (the weekly advisory `tox -e linkcheck` CI workflow; the obstacle
  that deferred it at v0.9.5's roadmap review is gone now that the environment it would call is on
  `main`, but it was not picked up this milestone).
- **NUM-01** — disclosed but not fixed. `## [0.9.6]`'s `### Known Limitations` section names it
  and gives a workaround; the underlying `:numref:` per-master divergence is unchanged. Its own
  Future-requirements todo stays pending after this phase.

## Before and after phase.complete-family tooling

Reproduced inline from `75-CLOSEOUT-GUARD.md` § "For the operator running phase.complete", so no
second file need be open.

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f

wc -l .planning/REQUIREMENTS.md
# compare against: 81

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-15' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   22:- [ ] **REL-15**: v0.9.6 is published. ... **This checkbox is checked only at `/gsd-complete-milestone`, against observed evidence (merge commit on `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`, and `gh release list`), and never by phase-completion tooling** — `phase.complete` has flipped REL rows against an explicit decision before. ...
#   59:| REL-15 | Phase 75 | Pending |
#   73:**REL-15 is mapped to Phase 75 for coverage only.** Its checkbox is checked at
#   76:phase artifact — which is why that phase's `REQUIREMENTS.md` fence is line-scoped to REL-15 rather
```

**REL-16's lines — expected to move.** `- [ ] **REL-16**` (line 23) and `| REL-16 | Phase 75 |
Pending |` (line 60) are **not** part of this guard. REL-16 closes inside this phase, so both may
legitimately read `[x]` / `Complete` once phase-completion tooling runs. Confusing that legitimate
flip with a REL-15 violation is exactly the mistake this line-scoping avoids.

**The third observation.** `/gsd-verify-work`'s inline transition and `/gsd-execute-phase`'s own
`phase.complete` step both count as "phase-completion tooling" for this fence — treat both as
equally likely to trigger the flip; neither is safer to assume clean than the other. The third
observation happens outside every plan's reach, run by the orchestrator or the operator, after
whichever of those two entry points actually runs. It is the observation that actually catches the
flip, because it is the first one taken after the tooling call that has fired at 9 of 10 prior
release-prep closes.

**The reversion recipe.** On any divergence in the REL-15 lines specifically:
`git checkout -- .planning/REQUIREMENTS.md`, then re-run the four probes above to confirm a MATCH.
If the divergence is confined to REL-16's two lines flipping to `[x]` / `Complete`, that is this
phase's own intended completion and is **not** reverted. The rule this project has followed at
every prior release-prep close where the flip was caught: revert first, report second, never ship
the flipped state as part of the phase's own close.

**Scratch backups**, recorded outside the repository before any `phase.complete`-family tooling
runs, so a hand-edited `STATE.md` or `ROADMAP.md` rewrite that the tooling itself corrupts has a
known-good copy to diff against, not only `.planning/REQUIREMENTS.md`:

```
BACKUP_ROADMAP = /tmp/tmp.Ea8hUnFA4z/p7501_ROADMAP.md
BACKUP_STATE = /tmp/tmp.Ea8hUnFA4z/p7501_STATE.md
```

Diff `.planning/ROADMAP.md` and `.planning/STATE.md` against these two paths as well as
re-running the REL-15 probes — `phase.complete`-family tooling has previously orphaned wrapped
lines in `ROADMAP.md` and rewritten tracking fields in `STATE.md` (including deleting
`current_phase_name`), which a checkbox-only fence would not catch.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Plan: 07*
