# Phase 76: The `password:`-Free `publish-pypi`, Rehearsed Against the Published v0.9.6 — and MSG-06 - Context

**Gathered:** 2026-09-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Three things, and nothing else:

1. **ATT-01** — `release.yml`'s `publish-pypi` step stops carrying a credential, so
   `pypa/gh-action-pypi-publish` takes the OIDC / Trusted Publishing path. A two-line deletion.
   Nothing is added in its place.
2. **ATT-02** — that path is *exercised against production PyPI* by exactly one
   `workflow_dispatch` run of `release.yml` with tag input `v0.9.6`, which must be turned away at the
   upload step as a **duplicate** (`400` / `File already exists`) rather than as an **unknown
   publisher** (`invalid-publisher` / `invalid-pending-publisher`). Nothing reaches PyPI from it.
3. **MSG-06** — `typsphinx/translator.py`'s two cross-directory relative-path DEBUG logs route
   `up_path`/`down_path` through `typsphinx/pathfmt.py::quote_path()`. Fourth and last module of the
   MSG-02 family.

**Not in this phase** (these land elsewhere, per ROADMAP's requirement-placement table):

- the version bump, the CHANGELOG section, the rollback procedure, the handoff → **Phase 77**
- the `v0.9.7` tag push, the real upload, the GitHub Release, ATT-03's PyPI-served-state reading,
  ATT-04's release-run reading, ATT-05's two secret deletions + PyPI revocation, DOC-25's
  `INTEGRATIONS.md` correction → **`/gsd-complete-milestone`**
- migrating `publish-testpypi`, adding `attestations:`, adding `skip-existing:`, pinning the action
  to a commit SHA, job-level `permissions:` narrowing → **explicitly out of scope** (REQUIREMENTS.md
  § Out of Scope)

</domain>

<decisions>
## Implementation Decisions

### The rehearsal dispatch — who fires it and how the wait is handled

- **D-01: The executor fires the dispatch itself.** A plan task runs
  `gh workflow run release.yml --ref <ref> -f tag=v0.9.6`. The owner does not fire it and does not
  hand a run id over.
  - The task reads `gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,event`
    **immediately before** the dispatch and records that list as the baseline, then reads it again
    after, and asserts the difference is **exactly one** new run. This is not decoration: a
    `gh workflow run` that returns HTTP 5xx has been observed in this repository to create the run
    anyway, so **no retry of `gh workflow run` is permitted until that before/after difference has
    been read**. A silent second run breaks ATT-02's exactly-one reading (ROADMAP constraint 6).
  - **Reversibility:** one-way — a dispatched run cannot be un-dispatched. The run record, the
    deployment-approval event and the audit trail are permanent, and deleting a run does not restore
    ATT-02's "exactly one dispatch" reading.

- **D-02: The same executor waits the run through and then takes the evidence — one plan.**
  No hand-back to the owner mid-plan.
  The wait is two-staged and the executor polls through both stages:
  (1) the `pypi` environment's manual approval, unbounded until the owner presses it, then
  (2) the environment's 15-minute `wait_timer`.
  Because Bash's foreground timeout ceiling is 600 s, the watch must run either as a background
  command or as a bounded polling loop — not as one foreground `gh run watch`.

- **D-03: Approval-pending reaches the owner via GitHub's own notification, not via the executor.**
  No in-repo signalling mechanism is built for it, and the executor is not expected
  to reach the owner: it is a subagent in a worktree and its mid-run output is not visible to the
  owner. The phase therefore accepts that the dispatch may sit unapproved for some time, and bounds
  that with D-04 instead of trying to shorten it.

- **D-04: The wait is bounded at 90 minutes; on exceeding it the executor HALTs, never re-dispatches.**
  The bound is elapsed time from the dispatch to the run's conclusion. On exceeding it the executor
  writes the run id, every job's current status and conclusion, and the exact point reached, into the
  phase evidence file (D-08), and returns. The same run is picked back up later; a second
  `gh workflow run` is never the recovery path for a slow approval.
  - Grounded on a measurement of this exact workflow, not an estimate: v0.9.6's production release
    run `35730551619` took **48 minutes end to end**, of which **42 m 47 s** was the gap between
    `Build Distribution` completing (13:03:54Z) and `Publish to PyPI` starting (13:46:41Z) — the
    `wait_timer` plus the owner's approval latency. 90 minutes is roughly twice that, so it absorbs
    an approval about 40 minutes slower than v0.9.6's without HALTing.

### Owner prerequisite — NOT a plan task

- **D-05: The PyPI-side Trusted Publisher is NOT yet registered as of 2026-09-27.** The owner will do
  it. No plan task may claim this step, and no agent can perform it.

**Prerequisite checkbox — must be checked before the ATT-02 dispatch task runs:**

- [x] The Trusted Publisher is registered on PyPI for the **existing** `typsphinx` project, through
      that project's own *Publishing* settings — **not** the account-level "pending publisher" flow
      most tutorials show, because `typsphinx` is already published. The four fields, all measured
      from the repository rather than recalled:
      - repository owner: `YuSabo90002`
      - repository name: `typsphinx`
      - workflow filename: `release.yml` — the **bare** filename, no `.github/workflows/` prefix
      - environment name: `pypi`

      A mismatch on any one of the four produces `invalid-publisher`, and the error is
      indistinguishable across the wrong-filename, wrong-environment and not-registered cases. The
      registration has **no dependency on any code change** — all four values exist in the repository
      unedited today — so it can be done at any time before the dispatch. It cannot be verified by
      any agent: PyPI exposes no API for reading a project's configured publishers, so the rehearsal's
      **duplicate rejection is itself the verification** that all four fields match.

      **Checked 2026-09-27 on the owner's report** ("登録完了した", relayed during `/gsd-execute-phase 76`
      wave 1). Owner-reported, not agent-verified — the ATT-02 duplicate rejection remains the verification,
      and 76-03 Task 2's checkpoint still asks for the explicit "dispatch" answer.

### Claude's Discretion

Three gray areas were offered and set aside by the owner. They are decided here so that no
downstream agent re-asks, each grounded on a measurement taken during this discussion.

- **D-06: The dispatch ref is the milestone branch, so the phase is shaped as two waves.**
  The ref is `gsd/v0.9.7-trusted-publishing-and-release`.
  Wave 1 lands the ATT-01 edit (and MSG-06 in parallel — disjoint
  files); the orchestrator merges wave 1 at cleanup-wave and **pushes the milestone branch to
  `origin`**; wave 2 then takes the pre-dispatch capture, fires the dispatch against that pushed
  milestone branch, watches, and records the evidence.
  - Why not dispatch from the executor's own worktree branch: `workflow_dispatch` runs the
    *dispatched ref's* copy of `release.yml`, so the ref must exist on `origin` and must carry the
    edit. A worktree branch is ephemeral — it is merged and deleted at cleanup-wave — which would
    leave ATT-02's evidence naming a ref that no longer exists.
  - Why this is not blocked: the `pypi` environment's `deployment_branch_policy` is **`null`**
    (measured 2026-09-27 via `gh api repos/YuSabo90002/typsphinx/environments/pypi`), so there is no
    branch restriction and a dispatch from a non-default branch does reach the `pypi` environment.
    `release.yml` already lives on `main` carrying a `workflow_dispatch` trigger, so the "a new
    workflow cannot be dispatched from an unmerged milestone branch" rule that still blocks QUA-08
    does not apply — `release.yml` is not new.
  - The evidence records both the ref **name** and its **commit SHA**, so the run stays reproducible
    after cleanup-wave.
  - **Reversibility:** costly — pushing the milestone branch to `origin` mid-phase is an outward-facing
    action, and the dispatched run permanently names the ref it ran on.

- **D-07: On an `invalid-publisher` rejection, recovery is `gh run rerun` of the SAME run.**
  This covers `invalid-publisher` and `invalid-pending-publisher` alike, and it means the executor
  HALTs rather than firing a second `gh workflow run`. It transcribes the verbatim failing lines and
  returns to the owner, who fixes the PyPI-side registration. Only then is the same run re-run.
  - This keeps ATT-02's "exactly one dispatch" literally true rather than requiring it to be re-read,
    and it is the same "cheapest recovery first" path ROADMAP constraint 14 already establishes for a
    failed production publish: `build`'s artifact is still downloadable within GitHub's 7-day
    retention window, so `publish-pypi` can re-run against it.
  - If the 7-day window has lapsed by the time the registration is fixed, that is an owner decision,
    not an executor one: a second dispatch is permitted **only** on explicit owner approval, and the
    evidence must then record both run ids and state plainly which one ATT-02 is read on.

- **D-08: All ATT-01/ATT-02 evidence goes into one file at the fixed name `76-ATT-EVIDENCE.md`.**
  Full path:
  `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-ATT-EVIDENCE.md`.
  Not `76-VERIFICATION.md`: that name is reserved by `gsd-verifier`, which overwrites it wholesale.
  Phase 77's handoff reads this file by that exact name.
  It must contain, at minimum:
  - the **pre-dispatch** PyPI capture: the Simple JSON API's full file list for `typsphinx` with its
    count and every `upload-time`, and the `provenance` value of 0.9.6's two files (expected `null`);
    plus `gh release view v0.9.6`'s asset list
  - the dispatch command verbatim, with the ref name **and** its commit SHA
  - the `gh run list` baseline and the post-dispatch reading, showing the difference is exactly one
  - the run id, every job's conclusion (`validate`, `build`, `publish-pypi`, `publish-testpypi`,
    `create-release`), and the verbatim failing lines from the `Publish to PyPI` step
  - `grep -c 'attestations input ignored'` and `grep -c 'disabling Trusted Publishing'` over the
    rehearsal run's log → both **0**, each paired with the identical grep over run `35730551619` →
    **non-zero**. A zero without its non-zero control is not a reading.
  - the **post-dispatch** PyPI capture, diffed against the pre-dispatch one
  - an explicit sentence, in the evidence's own words, that this is the **rehearsal** run and that
    ATT-04 is a reading on the **v0.9.7 release run** — so this observation must not be transcribed
    forward as ATT-04's evidence
  - the measured line numbers of the deleted lines, rather than a repetition of `:141-144`

  **D-08 AMENDED 2026-09-27 (owner decision, option 1 of 3, after research falsified the grep target).**
  `grep -c 'attestations input ignored'` reads **0** on control run `35730551619` as well (measured
  twice: research, then orchestrator — `gh run view 35730551619 --log`, 3356 lines, `LC_ALL=C`). The
  phrase exists only as the annotation's `title=`, which `--log` never prints; the log body at
  `Publish to PyPI` reads "…explicit password was also set, disabling Trusted Publishing. As a result,
  the attestations input is ignored." So the zero/non-zero pair is now read on the log body with
  **two** greps, each paired with the identical grep on the control:
  `grep -c 'disabling Trusted Publishing'` → rehearsal **0** / control **1**, and
  `grep -c 'attestations input is ignored'` → rehearsal **0** / control **1**.
  `'attestations input ignored'` is no longer an evidence grep in this phase. The same stale
  wording in ROADMAP SC #4, REQUIREMENTS.md ATT-04 and Phase 77's handoff spec is aligned in
  **Phase 77** (the phase that writes the handoff), not edited here. All other D-08 items stand.

### Folded Todos

Both were already tagged `resolves_phase: 76` when the roadmap was created (commit `964840ab`), so
they are folded rather than newly considered:

- **`.planning/todos/pending/2026-09-22-release-yml-uses-a-pypi-api-token-so-trusted-publishing-and.md`**
  — `release.yml` publishes with a PyPI API token, so Trusted Publishing is off and the action's
  default PEP 740 attestations are silently dropped. This is ATT-01 verbatim; it closes with ATT-01's
  edit plus ATT-02's rehearsal.
- **`.planning/todos/pending/2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`**
  — `translator.py`'s two relative-path DEBUG logs quote `up_path`/`down_path` with a hardcoded
  `'...'` delimiter; a fourth module, out of Phase 60's requirement scope. This is MSG-06 verbatim.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

ROADMAP.md carries **no** `Canonical refs:` line for Phase 76, so this list is assembled from
REQUIREMENTS.md, the codebase scout, and the measurements taken during this discussion.

### Requirement text and binding constraints

- `.planning/ROADMAP.md` § "🚧 v0.9.7 — Trusted Publishing and release (ACTIVE)" — the **14 binding
  constraints** and the requirement-placement table that decides what closes in Phase 76 versus
  Phase 77 versus `/gsd-complete-milestone`.
- `.planning/ROADMAP.md` § "Phase 76: The `password:`-Free `publish-pypi` …" — the goal and the five
  success criteria. **Its `:141-144` line citation for ATT-01 is wrong** — see below.
- `.planning/REQUIREMENTS.md` § Trusted Publishing / Translator messages — ATT-01, ATT-02, MSG-06.
  **ATT-01's correction here supersedes ROADMAP's citation**: the lines to delete are `:143-144`, a
  two-line deletion. **But MSG-06's `:5047` / `:5152` line numbers in this same file are stale** —
  the real sites are `:5121` and `:5226` (measured 2026-09-27). Re-measure both before editing;
  trust neither document's line numbers.
- `.planning/REQUIREMENTS.md` § Out of Scope — the five things that must **not** be added
  (`attestations:`, `skip-existing:`, a SHA pin, job-level `permissions:`, a `publish-testpypi`
  migration).

### The workflow

- `.github/workflows/release.yml` — the file being edited. Top-level `permissions:` with
  `id-token: write` at `:13-15`; `workflow_dispatch` with its `tag` input at `:7-11`; the `validate`
  job's version comparison at `:60-70`; `publish-pypi`'s `environment: pypi` at `:131-133`; the
  publish step at `:141-144`; `publish-testpypi`'s `if:` gate at `:224-230` and its credential at
  `:241-245`.

### MSG-06

- `typsphinx/translator.py` — `_compute_relative_include_path()` (DEBUG site at `:5119-5123`) and
  `_compute_relative_image_path()` (DEBUG site at `:5224-5228`). The two f-strings are **identical**:
  `f"up_path='{up_path}', down_path='{down_path}', "`.
- `typsphinx/pathfmt.py` — `quote_path()`. Its module docstring records the D-01/D-01a/D-03/D-04
  contract: `None` → the bare string `None`; an empty string → `''` (does **not** raise); the
  delimiter rule mirrors `repr()`'s minus the backslash doubling; an apostrophe-and-double-quote
  value doubles the apostrophe SQL-style with **no** backslash inserted.
- `tests/test_writer_path_quoting_gate.py` — **the closest analog for MSG-06's test.** Same observable
  (a `logger.debug()` record reachable only through `caplog` at DEBUG level), same structure: filter
  `caplog.records` to DEBUG, narrow to the one record by its message prefix, assert exactly one was
  emitted, then assert on that message. Copy this shape.
- `tests/test_builder_path_quoting_gate.py`, `tests/test_template_registry_path_quoting_gate.py` —
  the family's other two gates, for the sibling modules Phase 60 closed. Read for consistency; they
  must stay untouched (SC #5 pins `builder.py`, `writer.py` and `template_registry.py` as unchanged).

### Execution environment

- `CLAUDE.md` § "Worktree-isolated execution" — worktree isolation is the standing execution mode, so
  every executor runs `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` first and
  then everything via `uv run`. Non-negotiable, not conditional.
- `CLAUDE.md` § "NixOS development shell" — the FHS shims, and the note that a test asserting warning
  text should also be run under `LC_ALL=C` because CI runs in English.

### Read but NOT edited in this phase

- `.planning/codebase/INTEGRATIONS.md:116-117` — DOC-25's target. It currently describes
  `PYPI_API_TOKEN` as the trusted-publishing mechanism, which is exactly backwards. **It is corrected
  at `/gsd-complete-milestone`, after ATT-05 lands**, so that it describes a state that is already
  true rather than one that is intended. Do not touch it in this phase.

</canonical_refs>

<code_context>
## Existing Code Insights

All values below were measured on `gsd/v0.9.7-trusted-publishing-and-release` on 2026-09-27. They are
the phase base. Re-measure rather than trust them if the branch has moved.

### `release.yml` — the two lines, measured

```
141:      - name: Publish to PyPI                          ← KEEP
142:        uses: pypa/gh-action-pypi-publish@release/v1    ← KEEP
143:        with:                                           ← DELETE
144:          password: ${{ secrets.PYPI_API_TOKEN }}        ← DELETE
```

`git diff origin/main -- .github/workflows/release.yml` is **empty** — the branch and `main` start
byte-identical for this file.

**Grep baselines at the phase base, and their post-edit targets:**

| command | at base | after the edit |
|---|---|---|
| `grep -c 'PYPI_API_TOKEN' .github/workflows/release.yml` | **2** | **1** |
| `grep -c 'attestations' .github/workflows/release.yml` | 0 | 0 |
| `grep -c 'skip-existing' .github/workflows/release.yml` | 0 | 0 |

The base count of 2 is `:144` (`PYPI_API_TOKEN`) plus `:244` (`TEST_PYPI_API_TOKEN`, which contains
the substring). SC #1's "counts only the `TEST_PYPI_API_TOKEN` occurrences it counted at the phase
base" therefore means the post-edit count is **1**, not 0.

`publish-testpypi` must stay byte-identical at `:241-245`:
```
241:      - name: Publish to TestPyPI
242:        uses: pypa/gh-action-pypi-publish@release/v1
243:        with:
244:          password: ${{ secrets.TEST_PYPI_API_TOKEN }}
245:          repository-url: https://test.pypi.org/legacy/
```

### The `pypi` environment — measured, and the two things it changes

`gh api repos/YuSabo90002/typsphinx/environments/pypi`:

- `deployment_branch_policy`: **`null`** — no branch restriction. A dispatch from the milestone branch
  does reach this environment. This is what makes D-06 possible.
- `protection_rules`: **`required_reviewers`** = `[User YuSabo90002]`, `prevent_self_review: false`;
  and **`wait_timer`: 15** (minutes).

The `wait_timer` is **not recorded anywhere in ROADMAP.md or REQUIREMENTS.md.** Both documents mention
the approval gate; neither mentions that a further 15-minute timer follows it. That is why D-04's
bound is 90 minutes rather than something near the approval latency alone.

### `publish-testpypi` will NOT fire on this rehearsal — measured, not assumed

ROADMAP constraint 7 asks for this to be measured on the actual dispatch ref rather than assumed. All
six `contains()` operands evaluate **false**:

| operand | `alpha` | `beta` | `rc` |
|---|---|---|---|
| `github.ref` = `refs/heads/gsd/v0.9.7-trusted-publishing-and-release` | false | false | false |
| `inputs.tag` = `v0.9.6` | false | false | false |

So `publish-testpypi` concludes `skipped`, satisfying SC #3 — and `TEST_PYPI_API_TOKEN` is never
exercised by the rehearsal.

### Both `PYPI_API_TOKEN` secrets exist — ATT-05's premise confirmed

| secret | scope | last updated |
|---|---|---|
| `PYPI_API_TOKEN` | repository | 2025-10-23T14:02:37Z |
| `PYPI_API_TOKEN` | `pypi` environment | 2025-10-23T14:00:28Z |
| `TEST_PYPI_API_TOKEN` | repository | 2025-10-13T05:37:42Z |

Two distinct `PYPI_API_TOKEN` secrets, as ROADMAP constraint 11 states. **Neither is deleted in this
phase** — they are the rollback path until ATT-03 passes at `/gsd-complete-milestone`.

### The control run, `35730551619` — the timing SC #4's control comes from

`gh run view 35730551619 --json createdAt,updatedAt,jobs`:

| job | conclusion | started | completed |
|---|---|---|---|
| Validate Release | success | 12:59:22Z | 13:03:31Z |
| Build Distribution | success | 13:03:35Z | 13:03:54Z |
| Publish to PyPI | success | **13:46:41Z** | 13:46:57Z |
| Publish to TestPyPI (Optional) | **skipped** | — | — |
| Create GitHub Release | success | 13:47:00Z | 13:47:19Z |

Run window 12:59:20Z → 13:47:20Z = **48 minutes**. Build-done → publish-start = **42 m 47 s**. Note
that `publish-testpypi` concluded `skipped` here too, on tag `v0.9.6` — the same reading SC #3 expects
from the rehearsal.

### MSG-06 — the two sites, and what makes the test non-trivial

- The sites are `typsphinx/translator.py:5121` and `:5226`, **not** REQUIREMENTS.md's `:5047` /
  `:5152`. Both are the identical string `f"up_path='{up_path}', down_path='{down_path}', "`.
- **There are no other `'`-delimited path fragments in either function.** Every other DEBUG log in
  both functions interpolates unquoted (`f"Path components: current_dir={current_dir}, …"`,
  `f"Common parent depth: {common_length}, current_parts={current_parts}, …"`). So SC #5's
  zero-remaining grep is satisfiable by these two replacements alone — no wider sweep is needed, and
  none is in scope.
- **`typsphinx/translator.py` carries no `quote_path` import yet.** `builder.py:22`, `writer.py:15`
  and `template_registry.py:33` each have `from typsphinx.pathfmt import quote_path`. `pathfmt.py` is
  a deliberate leaf module with zero `typsphinx`-internal imports, so adding this import to
  `translator.py` creates no cycle.
- **`up_path` can never carry an apostrophe** — it is `"../" * up_count`, synthesized, or `""`. Only
  `down_path` (joined from docname parts) can. MSG-06 requires both to go through `quote_path()`
  regardless; but the test's literal-`'` fixture only bites on `down_path`.
- **`up_path` is `""` on the `up_count == 0` path, and `quote_path("")` returns `''`** (pathfmt D-04 —
  it deliberately does not raise, unlike `tests/_path_naming.py::path_named_in()`). So for that shape
  the emitted record is **byte-identical** before and after the fix. A RED assertion must therefore be
  driven by a `down_path` carrying a literal `'`, not by the empty-`up_path` shape.
- **The test must reach the cross-directory branch**, which needs `current_docname` and the target to
  be in *different* directory trees — `target_path.relative_to(current_dir)` must raise `ValueError`.
  A same-directory or root-directory docname returns earlier and never reaches the log.

### Integration points

- `typsphinx/pathfmt.py::quote_path()` — imported into `translator.py`; the only product change MSG-06
  makes outside the two f-strings.
- The `pypi` GitHub environment — the gate the rehearsal must pass through, twice (reviewer, then
  timer).
- PyPI's upload endpoint — reached by the rehearsal and required to reject it. Nothing is written.

</code_context>

<specifics>
## Specific Ideas

- **"Exactly one dispatch" is to be read literally, and defended mechanically.** The owner chose the
  executor-fires path knowing the exactly-one constraint, so the before/after `gh run list` reading
  in D-01 is the mechanism that makes that safe — not a note in a plan asking the executor to be
  careful. It is what stands between a 5xx response and a silent second run.
- **A slow approval is not a failure, and must not be treated as one.** D-04's 90-minute bound exists
  to make the executor return with a usable record instead of hanging, and its HALT path explicitly
  forbids the one recovery an executor would otherwise reach for: firing the dispatch again.
- **The rehearsal's clean reading must not be laundered into ATT-04's.** SC #4 and D-08 both insist on
  this in the evidence's own words. The two readings use the identical greps on two different runs,
  which is exactly the shape that gets mis-transcribed.
- **Neither ROADMAP.md nor REQUIREMENTS.md can be trusted for line numbers here.** ROADMAP's
  `:141-144` would delete the publish step itself; REQUIREMENTS.md fixes that but carries stale
  `:5047`/`:5152` for MSG-06. Both were re-measured on 2026-09-27 and both were wrong in one place.
  Measure at the phase base.

</specifics>

<deferred>
## Deferred Ideas

None raised — the discussion stayed inside the phase boundary.

### Reviewed Todos (not folded)

Both surfaced from `todo.match-phase 76` at score 0.6 and both are already recorded in
REQUIREMENTS.md § Future Requirements, so they stay deferred:

- **`.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md`** — a weekly advisory CI
  workflow calling `tox -e linkcheck` (**QUA-08**). Deferred: it would be a *new* workflow file, and
  a new workflow cannot be scheduled or dispatched from an unmerged milestone branch — the obstacle
  that does **not** apply to `release.yml` in this phase precisely because `release.yml` already
  exists on `main`.
- **`.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`**
  — **NUM-01**, settled at v0.9.6 as a `### Known Limitations` disclosure rather than a fix.

</deferred>

---

*Phase: 76-the-password-free-publish-pypi-rehearsed-against-the-published-v0-9-6-and-msg-06*
*Context gathered: 2026-09-27*
