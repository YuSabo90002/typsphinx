# Architecture Research: Trusted Publishing integration into `release.yml`

**Domain:** GitHub Actions release pipeline / PyPI publishing (CI-CD, not application architecture)
**Researched:** 2026-09-23
**Confidence:** HIGH (repo state and GitHub-side config measured directly via `gh` CLI and file reads; PyPI OIDC failure-mode claims corroborated by official PyPI docs and multiple `pypa/gh-action-pypi-publish` issue reports)

This is not a system-design document — `release.yml` is a fixed five-job pipeline that already exists
and is not being redesigned. This file answers one thing: **the correct sequencing of a one-line code
change against an out-of-band, manual PyPI-side action, given that the workflow has no dry-run path
and no `if:` gate protecting production PyPI.**

## Standard Architecture

### System Overview — the pipeline as it exists today (measured at `.github/workflows/release.yml`)

```
push tag v*  ─┐
              ├─► validate ──► build ──► publish-pypi ──► create-release
workflow_     ┘   (:19-90)    (:93-124)  (:127-144)       (:147-217)
dispatch                                  environment:        needs:
(tag input)                               pypi (manual         [build,
                                           approval by          publish-pypi]
                                           YuSabo90002,          — SKIPPED if
                                           measured via          publish-pypi
                                           gh api)               fails or is
                                                                  skipped
                                    └──► publish-testpypi (:220-245)
                                         gated: alpha/beta/rc tags only
                                         environment: testpypi
                                         UNCHANGED this milestone —
                                         stays on TEST_PYPI_API_TOKEN
```

`publish-pypi` carries **no `if:` condition** — every job upstream of it (`validate`, `build`) runs
unconditionally for any `v*` tag, so an rc tag reaches production PyPI exactly like a final tag does.
This is the single fact that shapes every ordering decision below.

### Component Responsibilities (jobs, as they exist — none added, none removed)

| Job | Responsibility | Change this milestone |
|-----|-----------------|------------------------|
| `validate` (:19-90) | Version match, CHANGELOG section present, tests/lint/mypy | none |
| `build` (:93-124) | `uv build`, `twine check`, uploads `dist-packages` artifact (7-day retention) | none |
| `publish-pypi` (:127-144) | Publish to production PyPI, gated by `environment: pypi` (manual approval, reviewer `YuSabo90002` — measured via `gh api repos/{owner}/{repo}/environments/pypi`) | **`password: ${{ secrets.PYPI_API_TOKEN }}` deleted (line 144)**; nothing added |
| `create-release` (:147-217) | GitHub Release body from `scripts/extract_changelog_section.py`; `needs: [build, publish-pypi]`, no `if:` override | none — but its *skip* behavior is load-bearing (see Blast Radius) |
| `publish-testpypi` (:220-245) | TestPyPI publish for alpha/beta/rc tags | **untouched** — `password: ${{ secrets.TEST_PYPI_API_TOKEN }}` (line 244) stays |

## Integration Points

### External service: PyPI Trusted Publisher registration

| Prerequisite | State measured 2026-09-23 |
|---|---|
| `id-token: write` | present, top-level, `:15` |
| `environment: pypi` on `publish-pypi` | present, `:131-133` |
| `pypi` environment protection | `required_reviewers: [YuSabo90002]` + `wait_timer` (measured via `gh api`) |
| `password:` in `publish-pypi` | present at `:144` — **the only line this milestone deletes** |
| Trusted Publisher registered on PyPI | **not done** (todo's own measurement, unchanged) |

The registration itself happens on pypi.org, under the **existing `typsphinx` project's** own
"Publishing" settings (not the account-level "pending publisher" page — that page is only for
project names that don't exist on PyPI yet, and `typsphinx` has shipped releases since v0.1.0b1, so
**"pending publisher" does not apply here**). The form asks for four strings: repository owner
(`YuSabo90002`), repository name (`typsphinx`), workflow filename (`release.yml`), and environment
name (`pypi`) — all four already exist today, unedited. **Registration has zero dependency on any
code change in this milestone**; it can be done on day one, in parallel with everything else.

### Internal boundary: `password:` vs OIDC inside `pypa/gh-action-pypi-publish`

Per the action's own behavior (confirmed by the run-`35730551619` annotation already captured in the
todo): if `password:` is supplied, the action takes the API-token path **regardless of whether a
Trusted Publisher is also registered** — OIDC is never attempted, and the default `attestations: true`
silently becomes a no-op. This means registering the Trusted Publisher *before* removing `password:`
is safe and inert (todo's step 1, correctly ordered) — the token path keeps winning until the line is
deleted. There is no intermediate state where both are "live" and one could shadow the other in an
unexpected way.

---

## Q1 — Ordering constraint

**Required order: PyPI-side registration → (b) merge to `main` → (c) push the real tag, with
registration free-floating before (b) or even before the milestone starts.**

Concretely:

1. **PyPI-side registration (owner, out-of-band) — do this FIRST, independent of code state.**
   Because the four fields PyPI needs (`YuSabo90002` / `typsphinx` / `release.yml` / `pypi`) already
   exist unedited in the repo today, this step has no dependency on (a) or (b) at all. Doing it first
   removes it from the critical path entirely and eliminates the one real risk described below.
2. **(a) Edit `release.yml`** — delete `password:` at line 144 only; `publish-testpypi` (:244) is
   explicitly untouched. This can be merged to `main` at any time *relative to step 1*, but **must
   not land on `main` before step 1 completes** — see "what breaks" below.
3. **(b) Merge to `main`** via the milestone's PR.
4. **(c) Push the tag** (`v0.9.7`) — this is the only event that actually exercises OIDC against
   production PyPI for real.

**What breaks if the order is inverted (code merged before PyPI registration, and a `v*` tag lands
in that window):** `publish-pypi` has no `if:` gate, so *any* tag push — not just the intended
`v0.9.7` — reaches it. With `password:` gone and no Trusted Publisher registered, the OIDC exchange
fails with PyPI's `invalid-publisher: valid token, but no corresponding publisher` error (confirmed
pattern across multiple `pypa/gh-action-pypi-publish` issues — #138, #173, #217; PyPI's own
troubleshooting docs describe the same mechanism). **This is a safe failure, not data corruption:**
no file is uploaded (the exchange fails before `twine upload` runs), so nothing is left half-published
on PyPI. The consequences are operational, not destructive:
   - `publish-pypi` shows failed/red.
   - `create-release` is **skipped**, not failed (its `needs: [build, publish-pypi]` has no
     `if: always()` override, measured at `:147-150` — GitHub Actions' default is "run only if all
     `needs` succeeded"), so no GitHub Release is created.
   - The build artifact (`dist-packages`) still exists, with 7-day retention (`:120-124`).
   - The tag itself is **not consumed or rolled back** — git tags are not touched by workflow
     failure; the pushed tag ref stays exactly where it was pushed.

**Is it recoverable?** Yes, cheaply, *if caught within the 7-day artifact retention window*: register
the Trusted Publisher, then use GitHub Actions' "Re-run failed jobs" on the same run — this reuses
the already-uploaded `dist-packages` artifact and retries only `publish-pypi` (and then
`create-release`, since its `needs` would now be satisfied). No new tag, no version bump, no second
`validate`/`build` pass needed. This is cheaper than the owner's documented fallback (restore
`password:`, re-tag 0.9.8) and should be tried first if the failure is specifically
`invalid-publisher` (a registration problem, not a code problem). The owner's re-tag-as-0.9.8 plan is
the right call only if the *first* 0.9.7 tag failure happens outside that recovery window, or if OIDC
still fails after registration is fixed and confirmed correct.

**Net:** doing PyPI registration first makes the "wrong order" scenario unreachable rather than merely
recoverable. This is the cheapest possible risk mitigation, so it belongs as literally the first
action of the milestone, not gated behind any phase.

---

## Q2 — What can be proven before the production tag

None of the following gives a *cost-free, zero-blast-radius* rehearsal of the real thing — this
matches the todo's own conclusion ("proof only exists at a real tag push") and the owner's
already-recorded decision to prove directly on the production 0.9.7 tag rather than a pre-flight rc.
Evaluated concretely against this workflow's actual mechanics:

| Option | Exercises REAL OIDC for the REAL `typsphinx` project? | Real cost |
|---|---|---|
| **`workflow_dispatch` with the existing `tag` input** | **Yes, if let run to completion** — not a simulation. `validate`'s "Extract version from tag" step (`:45-58`) parses the *input string*, not a real git ref; if `pyproject.toml` on the dispatched branch already reads e.g. `0.9.7`, `validate` passes, `build` produces real dist files, and (after the manual `pypi` environment approval) `publish-pypi` performs a genuine OIDC exchange and a genuine upload attempt to the real project. There is no `if:` distinguishing a dispatch run from a tag-push run in `publish-pypi`. **This is the same production action, just a different trigger — it is not a dry run.** |
| **"Pending publisher" registration** | N/A — doesn't apply. Pending publishers are only for PyPI project names that don't exist yet; `typsphinx` has shipped since v0.1.0b1 (tags `v0.1.0b1`…`v0.9.6` confirmed present via `git tag -l`). |
| **Publish to TestPyPI first** | No. `publish-testpypi` is deliberately staying on `TEST_PYPI_API_TOKEN` this milestone (out of scope, per `PROJECT.md`), so it doesn't touch OIDC at all right now. Even if it were flipped too, TestPyPI Trusted Publisher registration is a *separate* registration on a *separate* site from production PyPI — success there proves nothing about the production registration. |
| **A documented dry-run/no-op mode of `pypa/gh-action-pypi-publish`** | No such flag exists. The closest lever is `skip-existing: true`, which still performs the full OIDC mint-token exchange and only changes how an *already-uploaded* file is handled afterward (treated as success instead of a 409 error). This is not a dry run of the action, but it does enable the next row. |
| **Dispatch against an already-published version (e.g. `v0.9.6`) with `password:` already removed** | **Yes — and safely.** This is the one genuinely useful pre-flight this pipeline supports without any throwaway infrastructure: dispatching with `tag: v0.9.6` against a `main` where `pyproject.toml` still/again reads `0.9.6` makes `validate` pass (version match) and `build` reproduce the same dist files. At `publish-pypi`, the OIDC exchange runs for real against the real `typsphinx` project; PyPI then rejects the upload because that file already exists. **A rejection at the upload step (not an `invalid-publisher` error) is itself proof the Trusted Publisher registration is correct** — the failure signature distinguishes "registration is wrong" from "registration is right, upload correctly refused a duplicate." Nothing on PyPI is overwritten (PyPI rejects re-uploads of an existing file by design). This requires deliberately triggering a dispatch run and accepting an expected red `publish-pypi` step as the "pass" signal — a genuine but easily-misread affordance, and worth calling out explicitly to whoever runs it so a red step isn't mistaken for the milestone failing. |
| **A throwaway/disposable PyPI package name** | Proves the *generic* GitHub↔PyPI OIDC mechanism works under correct `id-token`/environment config, but requires its own repo-name+workflow-filename+environment registration on PyPI (a different config entry than production `typsphinx`), so it does **not** validate that the *actual* production registration was entered correctly — and it leaves a second PyPI project to clean up. Disproportionate to what it proves, given this repo's `release.yml` is hardcoded to `url: https://pypi.org/p/typsphinx` (`:133`) and can't be pointed at a throwaway name without its own workflow edit. |

**Recommendation for the roadmapper:** the dispatch-against-an-already-published-version trick is the
only real, low-risk pre-production verification available in this pipeline, and it can be scheduled as
an optional verification step *after* `password:` is removed and merged to `main`, but *before* the
real `v0.9.7` tag is pushed — it uses the manual `pypi` environment approval gate as a natural stop
point (the approver can simply decline if anything looks wrong before the real network call happens).
Given the owner's already-recorded decision to prove on the production tag directly, this is worth
presenting as an option, not a requirement.

---

## Q3 — Blast radius

**Jobs that can fail as a direct consequence of this change:** only `publish-pypi` (:127-144) itself.
`validate` and `build` don't reference PyPI credentials or Trusted Publishing at all, so this change
cannot make them fail differently than before.

**Downstream effect, measured against the actual `needs:` graph:**

- `create-release` (`:149`, `needs: [build, publish-pypi]`) has no `if:` override, so GitHub Actions'
  default applies: **it does not run at all** (status: skipped, not failed) if `publish-pypi` fails.
  No GitHub Release is created, but nothing partial is created either — `softprops/action-gh-release`
  never executes.
- `publish-testpypi` (`:220-245`) is independent (`needs: [build]` only) and unaffected either way —
  it doesn't share a `needs` edge with `publish-pypi`, so its outcome (or non-run, for a non-prerelease
  tag) is unchanged by this milestone.

**Is the tag consumed?** No. A git tag is a static ref; pushing it and having the triggered workflow
fail does not delete or move the tag. `v0.9.7` would remain exactly where it was pushed regardless of
`publish-pypi`'s outcome.

**Can the same tag be re-run?** Yes, two ways, in order of cost:
1. **Re-run failed jobs on the same workflow run** (GitHub Actions UI/`gh run rerun --failed`), reusing
   the existing `dist-packages` artifact (7-day retention) — cheapest, no new tag, no version bump,
   works as long as the underlying cause (e.g. missing TP registration) is fixed within that window.
2. **Push a brand-new tag** (the owner's documented `0.9.8` fallback) — required if the retention
   window has lapsed, or if the failure turns out not to be a simple registration gap.

Re-running the identical tag by deleting and re-pushing `v0.9.7` (rather than re-running the existing
run, or moving to `0.9.8`) is **not** a path documented anywhere in `PROJECT.md`/`STATE.md`/`ROADMAP.md`
for this milestone, and this project has no established precedent for deleting-and-re-pushing a tag —
worth flagging to the roadmapper as a gap rather than assuming it's acceptable practice here.

---

## Q4 — Rollback (the owner's chosen procedure, made concrete)

Owner's stated rollback (`PROJECT.md` "Key context"): *"restore `password:` and re-tag as 0.9.8,
leaving 0.9.7 unclaimed on PyPI the way 0.9.1 and 0.9.3–0.9.5 already are."* Two things measured here
sharpen that sentence into an actual procedure:

**Measured precedent — but it doesn't fully match this scenario.** `git tag -l "v0.9.*"` returns only
`v0.9.0`, `v0.9.2`, `v0.9.6` — **no `v0.9.1`, `v0.9.3`, `v0.9.4`, or `v0.9.5` tag has ever been pushed**,
and `git log -S` over `CHANGELOG.md` confirms **no `## [0.9.1]`/`## [0.9.3]`/`## [0.9.4]`/`## [0.9.5]`
heading has ever existed** in this repo's history either. The established "unclaimed version" pattern
is *"the version number was bumped in planning and then superseded before ever being tagged"* — not
*"a real tag was pushed, CI ran, and the publish step failed."* **v0.9.7 failing after a real tag push
would be the first time this repo has an actually-pushed tag with no corresponding PyPI release or
GitHub Release**, which is a materially different, and currently undocumented, situation. Flag this
explicitly to the roadmapper: the rollback plan needs an explicit decision on **whether the pushed
`v0.9.7` git tag is deleted or left dangling** — `PROJECT.md` covers the PyPI-side unclaimedness but
not the git-tag-side, and there's no prior instance in this repo to copy from.

**File-level checklist for the rollback (mirrors the version-bump these same files receive going
0.9.6→0.9.7, just re-targeted to 0.9.8):**

- [ ] `pyproject.toml:7` — `version = "0.9.7"` → `version = "0.9.8"`.
- [ ] `uv.lock:1528` — the `typsphinx` self-entry (`source = { editable = "." }`) must be
      regenerated (`uv lock` / `uv sync`), not hand-edited, to stay consistent with `pyproject.toml`.
- [ ] `README.md:348` — `**Status**: Stable (v0.9.7) - Production ready` → `(v0.9.8)`.
- [ ] `CHANGELOG.md` — **rename** the `## [0.9.7] - <date>` heading (added during this milestone's
      release-prep) to `## [0.9.8] - <new date>`, rather than leaving `## [0.9.7]` in place and adding
      a second heading below it. This is what the "no trace ever existed for 0.9.1/0.9.3–0.9.5" precedent
      implies: an unclaimed version number should leave **zero** heading in `CHANGELOG.md`, and its
      content is simply reassigned to whatever version actually ships.
- [ ] `CHANGELOG.md` link block (bottom) — same rename: `[0.9.7]: …/tag/v0.9.7` → `[0.9.8]: …/tag/v0.9.8`,
      and `[Unreleased]: …/compare/v0.9.7...HEAD` → `…/compare/v0.9.8...HEAD`. No `[0.9.7]:` entry
      should remain, matching the fact that no `[0.9.1]:`/`[0.9.3]:`/`[0.9.4]:`/`[0.9.5]:` entries exist
      today either.
- [ ] `release.yml` — restore `password: ${{ secrets.PYPI_API_TOKEN }}` at (what was) line 144, i.e.
      revert the ATT-01 edit. **Only do this if `PYPI_API_TOKEN` has not yet been deleted from
      secrets** — see Q5; if the secret was already retired, this revert needs a *new* token minted
      and stored before it's usable again.
- [ ] Push a fresh `v0.9.8` tag from the commit containing all of the above.

**Left behind, either way:**
- An unclaimed `0.9.7` on PyPI (matches the stated intent — PyPI never allows re-uploading a deleted/
  failed version number under the same version string anyway, so this is enforced by PyPI itself, not
  just a convention).
- The original failed `release.yml` run for `v0.9.7`, visible in Actions history (harmless, informational).
- **Open decision, not yet answered anywhere in `.planning/`:** delete the `v0.9.7` git tag
  (`git push origin :refs/tags/v0.9.7` after `git tag -d v0.9.7`) or leave it pointing at the merge
  commit permanently. Recommend surfacing this as an explicit roadmap/CONTEXT question rather than
  assuming an answer, since — per the precedent check above — this repo has never had to make this
  call before.

---

## Q5 — Secret retirement

**Grep across the whole repo (excluding `.git/`) for `PYPI_API_TOKEN` / `TEST_PYPI_API_TOKEN`:**

| Location | What it is |
|---|---|
| `.github/workflows/release.yml:144` | live reference — `publish-pypi`'s `password:` (**being deleted this milestone**) |
| `.github/workflows/release.yml:244` | live reference — `publish-testpypi`'s `password:` (**staying, out of scope**) |
| `.planning/codebase/INTEGRATIONS.md:116-117` | a codebase-mapping doc describing both secrets — **currently stale/backwards**: it calls `PYPI_API_TOKEN` "PyPI trusted publishing... alternative to deprecated password," which is the opposite of the current architecture (today it *is* the password; Trusted Publishing is the thing replacing it). Worth a follow-up doc fix once ATT-01 lands, though out of this research's scope. |
| `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/MILESTONES.md` | planning narrative only, no live references |
| `.planning/milestones/v0.6.4-phases/...` (three files) | historical security/asset notes from Phase 31/32, listing the secret *names* only (never values) as already-public in workflow files — inert history |
| `.planning/todos/pending/2026-09-22-...md` | the todo this milestone implements |

**No script, no `conf.py`, no test fixture, and no other workflow file references either secret.**
`release.yml` is the only live consumer of `PYPI_API_TOKEN`, and only at the one line being deleted.

**Environment-scoped vs repository-scoped — measured directly via `gh secret list`, and this is the
sharpest finding of this research:**

```
$ gh secret list                    $ gh secret list --env pypi     $ gh secret list --env testpypi
PYPI_API_TOKEN       2025-10-23...  PYPI_API_TOKEN   2025-10-23...   (empty)
TEST_PYPI_API_TOKEN  2025-10-13...
```

**There are two distinct `PYPI_API_TOKEN` secret objects** — a repository-scoped one and an
environment-scoped one under the `pypi` environment, created two minutes apart
(`14:02:37Z` repo vs `14:00:28Z` env). GitHub resolves `secrets.PYPI_API_TOKEN` inside a job that
declares `environment: pypi` by preferring the environment-scoped copy when both exist. **`TEST_PYPI_API_TOKEN`
exists only at the repository scope** — `gh secret list --env testpypi` returns nothing — consistent
with `publish-testpypi` staying untouched and never having had an environment-scoped copy to begin
with.

**Safe sequence:**
1. Remove `password:` from `release.yml:144` and get a successful token-free `publish-pypi` run (the
   milestone's own proof step).
2. **Delete both `PYPI_API_TOKEN` copies**, not just one:
   - `gh secret delete PYPI_API_TOKEN` (repository scope)
   - `gh secret delete PYPI_API_TOKEN --env pypi` (environment scope)

   Deleting only the repository-scoped copy would make `gh secret list` (no `--env` flag) *look*
   clean while the environment-scoped copy silently remains — misleading, since that's the copy the
   job would actually resolve if `password:` were ever restored (e.g. under the Q4 rollback path,
   before rollback re-adds the `password:` line and needs a live token again).
3. Leave `TEST_PYPI_API_TOKEN` untouched — it has no environment-scoped shadow copy to worry about,
   and `publish-testpypi` is explicitly out of scope this milestone.

**Rollback interaction (Q4):** if the Q4 rollback path is ever taken *after* step 2 above has already
run, restoring `password: ${{ secrets.PYPI_API_TOKEN }}` in the workflow file resolves to a secret
that no longer exists — the step would fail with an empty/missing password rather than silently
succeed with a stale value. A real rollback taken post-retirement needs a **freshly minted** PyPI API
token stored again (at whichever scope — repository is sufficient, since no environment-level need is
being reintroduced) before the reverted workflow can run.

---

## Q6 — Suggested build order

Given: (1) PyPI-side registration is a zero-dependency, out-of-band action that can happen on day one;
(2) MSG-06 is a one-line `translator.py` fix with no relationship to any of the release-pipeline work
(confirmed: `translator.py:5047`/`:5152`, `release.yml`, and `pyproject.toml`/`CHANGELOG.md` are
disjoint file sets); (3) the version bump and CHANGELOG promotion must exist on `main` before the tag
that proves everything is pushed; (4) secret retirement must strictly follow a successful token-free
publish.

1. **Phase A — MSG-06 (independent, do anytime, first for cheap early green CI).** One-line
   `quote_path()` fix in `typsphinx/translator.py` at both call sites. No dependency on anything else
   in this milestone; can land, merge, and even ship inside the same tag as everything else with zero
   ordering risk.

2. **Phase B — ATT-01 code change.** Delete `password:` from `release.yml:144` only (not `:244`).
   Owner should complete the PyPI-side Trusted Publisher registration (out-of-band, on pypi.org)
   before or during this phase — it has no code dependency, so it is not itself a "phase" with a
   plan/execute shape, just a prerequisite fact that must be true before Phase D's tag push. Consider
   an explicit CONTEXT checkbox/acknowledgment for this manual step rather than a plan task, since no
   agent can perform it.

3. **Phase C — version bump + release-prep.** Bump `pyproject.toml`, regenerate `uv.lock`, update
   `README.md`'s status line, promote `## [Unreleased]` into `## [0.9.7]` in `CHANGELOG.md` with its
   link-block entries. This is the standard release-prep shape this project already follows every
   milestone (see the v0.9.6 close for the precedent) — no new pattern needed, just sequenced after
   Phase B so the workflow fix rides the same tag as the version it's meant to prove.

4. **Phase D — tag push and proof.** Merge to `main`, push `v0.9.7`, watch `publish-pypi` run under
   the `pypi` environment's manual approval gate (reviewer `YuSabo90002`), confirm no "disabling
   Trusted Publishing" annotation and a PEP 740 attestation on the PyPI project page. This is the
   phase that actually needs the rollback procedure (Q4) on standby, not before it.

5. **Phase E — secret retirement.** Only after Phase D's proof succeeds: delete both `PYPI_API_TOKEN`
   copies (repository-scoped and `pypi`-environment-scoped — see Q5). This should be its own small,
   clearly-gated phase (or a final task inside Phase D) so it can never run before the proof exists.

**Ordering rationale:** A and B have no dependency on each other and could be parallel workstreams;
B must precede C only in the sense that both need to be on `main` before D's tag, not relative to each
other. D strictly depends on B+C being merged and on the out-of-band PyPI registration being complete.
E strictly depends on D's success. This is a straight line with one fan-in (B+C → D) and one
independent branch (A), not a graph requiring parallel-wave planning.

## Sources

- `.github/workflows/release.yml` (read in full, this repo, measured 2026-09-23) — HIGH
- `.planning/todos/pending/2026-09-22-release-yml-uses-a-pypi-api-token-so-trusted-publishing-and.md` — HIGH (curated, this repo)
- `.planning/PROJECT.md` "Current Milestone: v0.9.7" section — HIGH (curated, this repo)
- `gh api repos/{owner}/{repo}/environments/pypi` (live measurement, 2026-09-23) — HIGH
- `gh secret list` / `gh secret list --env pypi` / `gh secret list --env testpypi` (live measurement, 2026-09-23) — HIGH
- `git tag -l "v0.9.*"` and `git log -S "## [0.9.X]" -- CHANGELOG.md` (live measurement, 2026-09-23) — HIGH
- [PyPI Trusted Publishers docs](https://docs.pypi.org/trusted-publishers/) and [Creating a PyPI Project with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) — HIGH (official docs)
- `pypa/gh-action-pypi-publish` issues #138, #173, #217, discussion #349 (`invalid-publisher` failure mode) — MEDIUM (community reports, but consistent across four independent threads)

---
*Architecture research for: typsphinx v0.9.7 Trusted Publishing integration*
*Researched: 2026-09-23*
