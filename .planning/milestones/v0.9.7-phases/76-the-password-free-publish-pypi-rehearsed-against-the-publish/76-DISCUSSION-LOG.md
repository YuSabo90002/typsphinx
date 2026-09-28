# Phase 76: The `password:`-Free `publish-pypi`, Rehearsed Against the Published v0.9.6 — and MSG-06 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `76-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-09-27
**Phase:** 76-the-password-free-publish-pypi-rehearsed-against-the-published-v0-9-6-and-msg-06
**Areas discussed:** Dispatch actor and wait handling (1 of 4 offered)

---

## Gray-area selection

Four phase-specific gray areas were offered; the parts ROADMAP.md had already settled (which two
lines come out, that nothing is added in their place, that evidence comes from PyPI's served state)
were excluded from the offer.

| Option | Description | Selected |
|--------|-------------|----------|
| dispatch する ref と push 経路 | Worktree isolation is the standing mode, so the `release.yml` edit lands on a worktree sub-branch; `gh workflow run --ref` only accepts a ref that exists on `origin`. Which branch gets pushed, and which ref is dispatched. Bears on wave ordering and on the scope of the outward-facing `origin` push. | |
| dispatch の実行主体と待ち方 | The exactly-one-dispatch constraint (with the known 5xx-still-creates-a-run behavior) plus the two-stage wait: approval gate and the 15-minute `wait_timer`. Does the executor fire `gh workflow run`, or does the owner fire it and the executor only read? | ✓ |
| invalid-publisher が返ったときの挙動 | A registration mismatch can only be fixed by the owner on PyPI, after which a second dispatch is needed. How ATT-02's "exactly one dispatch" is then read; whether the phase HALTs or re-dispatches automatically. | |
| 事前スナップショットと control の保存形式 | SC #3 compares against a capture taken before the dispatch; SC #4 needs a non-zero control read on v0.9.6's run `35730551619`. What is recorded, in which file, in what form — Phase 77's handoff and `/gsd-complete-milestone` both inherit it. | |

**User's choice:** dispatch の実行主体と待ち方
**Notes:** The three unselected areas were left to Claude's discretion and are decided with
measured grounding in `76-CONTEXT.md` § Claude's Discretion (D-06, D-07, D-08), so no downstream
agent re-asks them.

---

## Dispatch actor and wait handling

### Q1 — Who actually fires `gh workflow run release.yml --ref <ref> -f tag=v0.9.6`?

Measured premises stated with the question: the `pypi` environment's branch restriction is `null`, so
a dispatch from the milestone branch reaches it; the reviewer is `YuSabo90002`; `prevent_self_review`
is `false`.

| Option | Description | Selected |
|--------|-------------|----------|
| executor が撃つ | A plan task runs `gh workflow run`. It reads `gh run list` immediately before and after and asserts the difference is exactly one — retrying `gh workflow run` is forbidden until that reading is taken, because an HTTP 5xx has been observed to create the run anyway. | ✓ |
| オーナーが撃ち run id を渡す | The owner dispatches by hand; the executor only reads the given run id and transcribes SC #2–#4's evidence. Removes the double-dispatch risk but puts a human turn inside the phase. | |
| executor がコマンドを置き、オーナーが実行 | The executor writes the dispatch command plus its pre/post guards to a file and HALTs; the owner runs it with `!` so the output enters the session, then the executor resumes. Same shape as Phase 77's handoff. | |

**User's choice:** executor が撃つ → **D-01**
**Notes:** Chosen with the exactly-one constraint in view, which is why the before/after `gh run list`
reading is recorded as the mechanism rather than as advice.

### Q2 — How is the wait after the dispatch structured?

Stated with the question: the wait is two-staged — the `pypi` environment's manual approval (unbounded
until the owner presses it), then a 15-minute `wait_timer`. Bash's foreground timeout ceiling is 600 s,
so waiting it through requires `run_in_background` or a polling loop.

| Option | Description | Selected |
|--------|-------------|----------|
| executor が通しで待つ | The executor dispatches, watches approval-wait → `wait_timer` → completion by background polling, and proceeds straight into evidence capture. Closes in one plan, but blocks for a long time if approval is slow. | ✓ |
| 一旦戻り SendMessage で再開 | The executor returns after recording the run id; once the owner has approved and the run has finished, the same executor is resumed via SendMessage — never re-dispatched. Matches behavior already observed in this repository. | |
| dispatch と証拠採取を別プランに分ける | Split at a plan boundary: one plan for pre-dispatch capture + dispatch + run-id record, another for reading the finished run. The owner's approval falls naturally between waves. | |

**User's choice:** executor が通しで待つ → **D-02**

### Q3 — How does the owner learn approval is pending, and is the wait bounded?

Stated with the question: the executor is a subagent in a worktree, so its mid-run output is not
visible to the owner.

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub の通知に任せ、上限あり | GitHub sends a pending-deployment-review notification; that is the approval trigger. The executor waits with a bound and, on exceeding it, records the run id and current state and HALTs. The bound goes in CONTEXT.md. | ✓ |
| dispatch をオーケストレータ側に残す | The orchestrator fires `gh workflow run`, so it can tell the owner "approve now" the moment it fires; the executor only watches and captures. | |
| 上限なしで待たせる | The executor polls until approval arrives. Simple, but if the owner misses the notification the phase looks silently stalled. | |

**User's choice:** GitHub の通知に任せ、上限あり → **D-03**

### Q4 — What is the bound?

Measured and stated with the question: on v0.9.6's production run `35730551619`, `Build Distribution`
completed at 13:03:54Z and `Publish to PyPI` started at 13:46:41Z — a **42 m 47 s** gap (the
`wait_timer` plus the owner's approval latency). The whole run took 48 minutes. The bound applies to
elapsed time from the dispatch to the run's conclusion.

| Option | Description | Selected |
|--------|-------------|----------|
| 90 分 | About twice the measured 48 minutes; absorbs an approval ~40 minutes slower than v0.9.6's. On exceeding it the executor records the run id and each job's state and HALTs — no re-dispatch, the same run is re-read later. | ✓ |
| 120 分 | ~2.5× the measurement; covers being away for over an hour. Lower chance of a HALT, slower to surface a genuine stall. | |
| 60 分 | 12 minutes of headroom over the measurement. Assumes prompt approval; an approval as slow as v0.9.6's would leave almost none, so it becomes a HALT-and-resume-by-hand shape. | |

**User's choice:** 90 分 → **D-04**

### Q5 — Is the PyPI-side Trusted Publisher already registered?

Asked because the answer changes plan ordering: an unregistered publisher makes the rehearsal come
back `invalid-publisher`. The four fields were stated as measured from the repository — owner
`YuSabo90002`, repo `typsphinx`, the bare workflow filename `release.yml`, environment `pypi` — along
with the note that registration goes through the existing project's Publishing settings, not the
account-level pending-publisher flow.

| Option | Description | Selected |
|--------|-------------|----------|
| まだ未登録、これからやる | Recorded in CONTEXT.md as an unchecked prerequisite, with "this checkbox is filled" written as a precondition on the dispatch task. MSG-06 does not depend on it and can run in a separate wave first. | ✓ |
| もう登録済み | Recorded as done. The executor still cannot verify it (PyPI exposes no API for reading a project's publishers), so the rehearsal's duplicate rejection remains the verification. | |
| 不確か、後で確かめる | Recorded as unverified, with an owner confirmation step as a precondition on the dispatch. Same plan shape as "not yet registered". | |

**User's choice:** まだ未登録、これからやる → **D-05**
**Notes:** Recorded as a literal `- [ ]` checkbox in CONTEXT.md, never as a plan task — ROADMAP
constraint 1 forbids any plan task claiming it.

### Wrap-up

| Option | Description | Selected |
|--------|-------------|----------|
| CONTEXT.md を書いてよい | Record the five decisions plus Claude's discretion on the three unselected areas, commit with DISCUSSION-LOG.md, and move to `/gsd-plan-phase 76`. | ✓ |
| この領域をもう少し詰める | Four more questions on dispatch actor and waiting — polling interval, what a HALT records, warning as the bound approaches. | |
| 未選択の 3 領域も詰める | The dispatch ref and push route, `invalid-publisher` behavior, and the evidence storage format. | |

**User's choice:** CONTEXT.md を書いてよい

---

## Claude's Discretion

The three gray areas offered and not selected. Each is decided in `76-CONTEXT.md` with the
measurement it rests on:

- **D-06 — dispatch ref and push route.** The dispatch runs against the milestone branch
  `gsd/v0.9.7-trusted-publishing-and-release`, which makes the phase two waves: wave 1 lands the
  ATT-01 edit and MSG-06 in parallel, the orchestrator merges and pushes the milestone branch, wave 2
  captures, dispatches, watches and records. Grounded on `deployment_branch_policy: null` (so a
  non-default branch does reach the `pypi` environment) and on the fact that a worktree branch is
  deleted at cleanup-wave, which would leave ATT-02's evidence naming a ref that no longer exists.
- **D-07 — `invalid-publisher` behavior.** HALT and transcribe; recovery is `gh run rerun` of the same
  run after the owner fixes the registration, never a second `gh workflow run`. This keeps ATT-02's
  "exactly one dispatch" literally true and reuses ROADMAP constraint 14's cheapest-recovery path
  (`build`'s artifact is still downloadable inside GitHub's 7-day retention window). A second dispatch
  needs explicit owner approval, and the evidence must then name both run ids.
- **D-08 — evidence storage.** One file, `76-ATT-EVIDENCE.md`, in the phase directory — deliberately
  not `76-VERIFICATION.md`, which `gsd-verifier` overwrites wholesale. Phase 77's handoff reads it by
  that exact name. Its required contents are enumerated in CONTEXT.md.

## Deferred Ideas

None raised — the discussion stayed inside the phase boundary.

Two todos surfaced from `todo.match-phase 76` at score 0.6 were reviewed and left deferred, both
already recorded in `.planning/REQUIREMENTS.md` § Future Requirements: the weekly `tox -e linkcheck`
CI job (QUA-08) and the `:numref:` divergence (NUM-01, settled at v0.9.6 as a disclosure). The two
score-0.9 todos were already tagged `resolves_phase: 76` at roadmap creation and are folded, not
deferred.
