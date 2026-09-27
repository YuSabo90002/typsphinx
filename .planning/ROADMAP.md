# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- ✅ **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (shipped 2026-07-29) → [archive](milestones/v0.6.5-ROADMAP.md)
- ✅ **v0.7.0 — API rendering design overhaul** — Phases 36–42 (+40.1) (shipped 2026-08-04) → [archive](milestones/v0.7.0-ROADMAP.md)
- ✅ **v0.7.1 — bug-fix round** — Phases 43–46 (+44.1, 44.2, 45.1, 45.2) (shipped 2026-08-11) → [archive](milestones/v0.7.1-ROADMAP.md)
- ✅ **v0.8.0 — multi-master composition** — Phases 47–52 (shipped 2026-08-15) → [archive](milestones/v0.8.0-ROADMAP.md)
- ✅ **v0.9.0 — per-document templates** — Phases 53–57 (+54.1) (shipped 2026-08-22) → [archive](milestones/v0.9.0-ROADMAP.md)
- ✅ **v0.9.1 — Windows path correctness** — Phases 58–61 (completed 2026-08-30, **never published**) → [archive](milestones/v0.9.1-ROADMAP.md)
- ✅ **v0.9.2 — Inline image blocker fix and release** — Phases 62–63 (shipped 2026-08-31) → [archive](milestones/v0.9.2-ROADMAP.md)
- ✅ **v0.9.3 — Toolchain and dependency-update repair** — Phases 64–69 (completed 2026-09-13, merged to `main`, **not published**) → [archive](milestones/v0.9.3-ROADMAP.md)
- ✅ **v0.9.4 — Typing Modernization** — Phases 70–71 (completed 2026-09-13, merged to `main`, **not published**) → [archive](milestones/v0.9.4-ROADMAP.md)
- ✅ **v0.9.5 — Docs Link Check and Navigation** — Phases 72–73 (completed 2026-09-16, merged to `main`, **not published**) → [archive](milestones/v0.9.5-ROADMAP.md)
- ✅ **v0.9.6 — Doctest block rendering and release** — Phases 74–75 (**shipped 2026-09-22, PUBLISHED**) → [archive](milestones/v0.9.6-ROADMAP.md)
- 🚧 **v0.9.7 Trusted Publishing and release** — Phases 76–77 (active, started 2026-09-23)

**Active milestone: v0.9.7 — Trusted Publishing and release.** Two phases (76–77). It moves
`release.yml`'s production publish off a long-lived PyPI API token and onto Trusted Publishing, so
the uploaded wheel and sdist carry PEP 740 provenance attestations — and it proves that on **PyPI's
own served state** at the real `v0.9.7` tag, not on the workflow file looking correct. Before
anything irreversible happens the OIDC exchange is rehearsed against the already-published `v0.9.6`,
where PyPI turns the upload away as a duplicate. The milestone also closes MSG-06, the fourth and
last module of the MSG-02 hardcoded-delimiter family, and publishes 0.9.7.

Phase numbering is **continuous across milestones**: v0.9.6 ran Phases 74–75, so v0.9.7 starts at
**Phase 76**.

## Phases

**Phase Numbering:**

- Integer phases (76, 77): Planned milestone work
- Decimal phases (76.1, 76.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1).

<details>
<summary>✅ v0.9.6 Doctest block rendering and release (Phases 74–75) — SHIPPED 2026-09-22, PUBLISHED</summary>

- [x] Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors (7/7 plans) — completed 2026-09-20
- [x] Phase 75: v0.9.6 Release Prep (prep-only) (7/7 plans) — completed 2026-09-22

5/5 v1 requirements complete. REL-15 was checked at the close, by hand, against the four
observations its own text names: the merge commit `6fcc5adb` on `origin/main`'s first-parent
history (PR #156, 15/15 checks green), `refs/tags/v0.9.6`, a PyPI 200 for `0.9.6` against a 404 for
`0.9.5` as negative control, and the Release in `gh release list`. `release.yml` run `35730551619`
succeeded on every job, `create-release` included — it had never run on a v0.9.x tag before.
`override_closeout` (both phases' verifications read fingerprint-stale from later `.planning/`
tracking commits while both VERIFICATION.md files themselves read `passed`; the same-day audit
stood in — the fourth consecutive close with that exact reading). The pre-close artifact audit
found 2 open todos and **both were fixed rather than acknowledged**, as quick tasks `260922-tbe`
and `260922-tkt`, because the prep-only fence that had deferred them lapsed once `origin/main`
moved and a CI re-dispatch became mandatory anyway. Full phase detail, the binding constraints,
success criteria and decisions: [milestones/v0.9.6-ROADMAP.md](milestones/v0.9.6-ROADMAP.md).
Audit: [milestones/v0.9.6-MILESTONE-AUDIT.md](milestones/v0.9.6-MILESTONE-AUDIT.md).
Quick tasks: `milestones/v0.9.6-quick/`.

</details>

<details>
<summary>✅ v0.9.5 Docs Link Check and Navigation (Phases 72–73) — COMPLETED 2026-09-16, MERGED, NOT PUBLISHED</summary>

- [x] Phase 72: `tox -e linkcheck` and Root Toctree Deduplication (6/6 plans) — completed 2026-09-14
- [x] Phase 73: v0.9.5 Close Prep (prep-only, unpublished) (7/7 plans) — completed 2026-09-16

4/4 v1 requirements complete; REL-14 checked at the close on the observed merge of PR #151
(`43fd7c13`). QUA-08, the weekly advisory linkcheck CI workflow, was scoped in at roadmap creation
and deferred to Future the same day, so it maps to no phase. `override_closeout` (both phases'
verifications read fingerprint-stale from later `.planning/` tracking commits while both
VERIFICATION.md files themselves read `passed`; the same-day audit stood in). Full phase detail, the
binding constraints, success criteria and decisions:
[milestones/v0.9.5-ROADMAP.md](milestones/v0.9.5-ROADMAP.md).
Audit: [milestones/v0.9.5-MILESTONE-AUDIT.md](milestones/v0.9.5-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v0.9.4 Typing Modernization (Phases 70–71) — COMPLETED 2026-09-13, MERGED, NOT PUBLISHED</summary>

- [x] Phase 70: Typing Modernization and Its Behaviour-Identity Evidence (13/13 plans) — completed 2026-09-13
- [x] Phase 71: v0.9.4 Close Prep (prep-only, unpublished) (7/7 plans) — completed 2026-09-13

6/6 v1 requirements complete; REL-13 checked at the close on the observed merge of PR #145
(`383a07e9`). `override_closeout` (Phase 70's verification fingerprint-stale after REL-13's AMENDED
block landed in `REQUIREMENTS.md`; the same-day audit stood in). Full phase detail, the 13 binding
constraints, success criteria and decisions: [milestones/v0.9.4-ROADMAP.md](milestones/v0.9.4-ROADMAP.md).
Audit: [milestones/v0.9.4-MILESTONE-AUDIT.md](milestones/v0.9.4-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v0.9.3 Toolchain and dependency-update repair (Phases 64–69) — COMPLETED 2026-09-13, MERGED, NOT PUBLISHED</summary>

- [x] Phase 64: FHS Wrapper and Command Shims in `flake.nix` (6/6 plans) — completed 2026-09-12
- [x] Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves (2/2 plans) — completed 2026-09-12
- [x] Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem (4/4 plans) — completed 2026-09-12
- [x] Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128 (5/5 plans) — completed 2026-09-12
- [x] Phase 68: Documentation Follow-Through — `CLAUDE.md`, `tox.ini`, `flake.nix` (4/4 plans) — completed 2026-09-13
- [x] Phase 69: v0.9.3 Close Prep (prep-only, unpublished) (6/6 plans) — completed 2026-09-13

21/21 v1 requirements complete; REL-12 checked at the close on the observed merge of PR #143.
`override_closeout` (all six verifications fingerprint-stale after later legitimate edits; the
same-day audit stood in). Full phase detail, the 15 binding constraints, success criteria and
decisions: [milestones/v0.9.3-ROADMAP.md](milestones/v0.9.3-ROADMAP.md). Audit:
[milestones/v0.9.3-MILESTONE-AUDIT.md](milestones/v0.9.3-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v0.9.2 Inline image blocker fix and release (Phases 62–63) — SHIPPED 2026-08-31</summary>

- [x] Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate (4/4 plans) — completed 2026-08-30
- [x] Phase 63: v0.9.2 Release Prep (prep-only) (6/6 plans) — completed 2026-08-30

7/7 v1 requirements complete; `verified_closeout`. Full phase detail, the 14 binding constraints,
success criteria and decisions: [milestones/v0.9.2-ROADMAP.md](milestones/v0.9.2-ROADMAP.md)

</details>

<details>
<summary>✅ v0.9.1 Windows path correctness (Phases 58–61) — COMPLETED 2026-08-30, NOT PUBLISHED</summary>

- [x] Phase 58: `repr()`-Format Decoupling (test-side only) (3/3 plans) — completed 2026-08-28
- [x] Phase 59: Path-Shape Predicate and Image-URI Correctness (5/5 plans) — completed 2026-08-29
- [x] Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere (5/5 plans) — completed 2026-08-29
- [x] Phase 61: v0.9.1 Release Prep (prep-only) (4/4 plans) — completed 2026-08-30

10/11 v1 requirements complete. REL-09 (publish to PyPI) deliberately unmet — the release was
cancelled, not missed. It carried forward into v0.9.2 and closed there. Full phase detail:
[milestones/v0.9.1-ROADMAP.md](milestones/v0.9.1-ROADMAP.md)

</details>

<details>
<summary>✅ v0.4.4 – v0.9.0 (Phases 1–57) — SHIPPED 2026-07-05 → 2026-08-22</summary>

Each milestone's phase detail lives in its own archive, linked from the **Milestones** list above.

</details>

## 🚧 v0.9.7 — Trusted Publishing and release (ACTIVE)

**Milestone Goal:** the wheel and sdist a user downloads from PyPI can *prove* which workflow built
them. `release.yml`'s `publish-pypi` step stops reading a long-lived API token and mints its own
OIDC token instead, which turns `pypa/gh-action-pypi-publish`'s default PEP 740 attestations back
on — and the switch is proven on PyPI's own served state for the real 0.9.7 upload, never on the
workflow file and never on a green run.

- **ATT-01 / ATT-02:** `publish-pypi` currently passes `password: ${{ secrets.PYPI_API_TOKEN }}`,
  which puts the action on the API-token path and disables Trusted Publishing, and with it the
  action's own `attestations: true` default. `id-token: write` (`:13-15`) and `environment: pypi`
  are already declared, so removing the credential is the whole code change. The rehearsal — one
  `workflow_dispatch` against the already-published `v0.9.6` — is what converts "the file looks
  right" into "the OIDC exchange actually works", because PyPI rejects a duplicate filename
  *after* the token exchange and rejects a bad registration *before* it, and the two failures read
  differently in the log.
- **ATT-03 / ATT-04:** the acceptance oracle. ATT-03 is PyPI's Simple JSON API carrying a non-null
  `provenance` for both 0.9.7 files and the Integrity API returning 200 with a `publisher` naming
  this repository, `release.yml` and `pypi`. ATT-04 is the absence of the action's
  `attestations input ignored` / `disabling Trusted Publishing` annotation — a necessary but **not
  sufficient** signal, since the action emits it locally from the presence of `password:` before any
  network call.
- **ATT-05 / ATT-06:** the token is the rollback path until ATT-03 passes, so it is retired strictly
  afterwards — from **two** distinct GitHub secrets plus a separate revocation on PyPI. And because
  a failed publish here cannot be retried under the same version, the rollback procedure is written
  down *before* the tag exists rather than improvised after it.
- **MSG-06:** `translator.py`'s two cross-directory relative-path DEBUG logs still delimit
  `up_path`/`down_path` with a hardcoded `'...'`, so a path containing a literal single quote closes
  the quote early. `quote_path()` has existed since Phase 60, which closed the same shape in
  `builder.py`, `writer.py` and `template_registry.py`. This is the family's fourth and last module.
- **REL-17 / DOC-25:** publish 0.9.7, describing attestations honestly as audit provenance rather
  than an install-time gate; and correct the one line of `.planning/codebase/INTEGRATIONS.md` that
  currently describes `PYPI_API_TOKEN` as the trusted-publishing mechanism — exactly backwards.

This serves the core value's publishing clause, the one v0.6.4 and v0.9.2 extended it with: an
artifact the project uploads must be what it claims to be. v0.9.6's upload *succeeded* and carried
`"provenance": null`, which is precisely the gap.

**Binding constraints this roadmap is built on** (settled decisions and measured facts):

1. **The PyPI-side Trusted Publisher registration is a manual, off-repo action by the project
   owner.** No agent can perform it. It is a **Phase 76 prerequisite and a CONTEXT checkbox, never a
   plan task.** The four fields it needs are copied from the file and the repository URL rather than
   from memory: repository owner, repository name, the **bare** workflow filename `release.yml`, and
   the environment name `pypi`. All four exist in the repository unedited today, so it has no
   dependency on any code change and should be done first. It must be registered through the
   **existing project's** Publishing settings, not the account-level "pending publisher" flow most
   tutorials show, because `typsphinx` is already published.

2. **Proof is taken on the production `v0.9.7` tag** (owner decision 2026-09-23). `publish-pypi`
   carries no `if:` gate, so **every** `v*` tag reaches production PyPI — an rc tag included, which
   would leave a prerelease on PyPI permanently. There is no dry-run path.

3. **ATT-02's rehearsal must run on a ref whose `pyproject.toml` still reads `0.9.6`.** The
   `validate` job compares `pyproject.toml`'s version against the dispatch's `tag` input and exits 1
   on mismatch; `build` and `publish-pypi` then never run, and the OIDC exchange is never reached.
   This is the dependency that orders Phase 76 before Phase 77 and forbids the version bump from
   landing early. **Measure it on the actual ref rather than trusting this sentence.**

4. **`workflow_dispatch` runs the *dispatched ref's* copy of `release.yml`.** The file already lives
   on `main` carrying a `workflow_dispatch` trigger, so `gh workflow run release.yml --ref
   <milestone-branch> -f tag=v0.9.6` executes the branch's edited copy. The "a new workflow cannot
   be scheduled or dispatched from an unmerged milestone branch" rule that still blocks QUA-08 does
   **not** apply here — `release.yml` is not new. `git diff origin/main -- .github/workflows/release.yml`
   was empty at roadmap creation, so the branch and `main` start identical.

5. **The rehearsal needs the `pypi` environment's manual approval to reach the upload step.** That
   is an expected gate, not a failure — v0.9.6's run `35730551619` waited on it too. An executor
   that returns at "waiting for approval" has not finished; the same run is resumed once the owner
   approves, not re-dispatched.

6. **Exactly one dispatch.** If `gh workflow run` returns an HTTP 5xx, `gh run list` is read before
   any retry — a 5xx here has been observed to create the run anyway, and a silent second run breaks
   ATT-02's exactly-one reading.

7. **`publish-testpypi` is out of scope and stays on `TEST_PYPI_API_TOKEN`**, repository-scoped and
   environment-scoped alike. Its `if:` matches `contains(github.ref, 'alpha'|'beta'|'rc')` as well
   as the tag input, so whether it fires on the rehearsal is a **measurement on the actual dispatch
   ref**, not an assumption — a branch name containing any of those three substrings would drag it in.

8. **ATT-01's `:141-144` citation spans four lines but the credential is two.** Measured 2026-09-23
   on `origin/main` (byte-identical to the branch): `:141` is `- name: Publish to PyPI`, `:142` is
   `uses: pypa/gh-action-pypi-publish@release/v1`, `:143` is `with:`, `:144` is
   `password: ${{ secrets.PYPI_API_TOKEN }}`. Deleting `:141-144` literally would delete the publish
   step itself and publish nothing. The controlling clause is ATT-01's first sentence — the step
   **publishes** with no `password:` key — so `:143-144` come out and `:141-142` stay. Re-measure the
   line numbers at the phase base before editing; do not trust the citation, in this roadmap or in
   REQUIREMENTS.md.

9. **Nothing is added to replace the deleted key.** No `attestations:` — it is already the action's
   default once Trusted Publishing is active, and writing it restates the exact misreading ATT-01's
   record exists to correct. No `skip-existing:` — it would turn ATT-02's duplicate rejection, the
   signal that proves the registration is correct, into a silent pass, and would mask a real failed
   upload at the production tag. No commit-SHA pin (`@release/v1` is the PyPA-recommended ref and a
   separate supply-chain decision) and no job-level `permissions:` narrowing.

10. **Neither the workflow file nor a green run is evidence.** This project lost a whole milestone
    to that exact shape once (REL-04, v0.7.0) and ATT-01 is the second instance: v0.9.6's upload
    succeeded *and* served `"provenance": null`. Every acceptance reading in this milestone comes
    from PyPI's own served state or from a run log. The legacy `/pypi/<project>/<version>/json`
    endpoint never carries the provenance field and does not count.

11. **ATT-05 is strictly gated behind ATT-03 passing, and there are two `PYPI_API_TOKEN` secrets** —
    one repository-scoped and one scoped to the `pypi` environment, which are distinct secrets. Both
    are deleted, and the token is separately revoked on PyPI's own token-management page. Until
    ATT-03 passes, that token is the rollback path.

12. **Every irreversible action executes at `/gsd-complete-milestone`, not inside a phase:** the PR
    merge to `main`, the `v0.9.7` tag push, the PyPI upload, the GitHub Release, both secret
    deletions and the PyPI-side revocation. ATT-03, ATT-04, ATT-05, DOC-25 and REL-17's publish
    clauses are checked **there**, against observed evidence, and **never by phase-completion
    tooling** — which has flipped a deferred release checkbox before (v0.9.2 precedent).

13. **MSG-06 must not land in the release-prep phase.** Phase 77 is prep-only: no change under
    `typsphinx/`. MSG-06 was deferred under exactly that fence at v0.9.6's Phase 75, and was still
    not picked up when its two siblings closed at the v0.9.6 close. It closes in Phase 76 instead,
    with its own recorded-RED evidence — a test observed failing on the pre-fix tree — per this
    repository's standing bar.

14. **Cheapest recovery first.** A failed publish does not create a partial release: `create-release`
    has `needs: [build, publish-pypi]` with no `if:` override, so it is *skipped* rather than failed
    and the tag is not consumed. Re-running the same failed run within the 7-day artifact retention
    window, once the registration is fixed, is cheaper than ATT-06's re-tag path and is tried first.

**Two phases: one work phase, then release prep — and where the post-tag requirements land.**

The research summary proposed five phases (MSG-06 / workflow edit / release-prep / tag + proof /
secret retirement). Four of those five are not phase-shaped here. The total build work in this
milestone is a **two-line deletion** in `release.yml` (constraint 8), a **two-call-site** change in
`translator.py`, one `workflow_dispatch`, one standard release-prep, and one `.planning/` line
correction. Splitting the workflow edit from its rehearsal would produce two phases of one
requirement each that cannot be verified apart — the edit's only meaningful evidence *is* the
rehearsal — which is the over-fragmentation shape this project has twice recorded. MSG-06 is folded
into Phase 76 rather than given its own phase for the same reason, and because the release-prep
phase's prep-only fence forbids it there (constraint 13). And the research's Phase D and Phase E are
not phases at all under this project's process: they are the **publish half**.

That split is the established shape here — v0.9.2's Phase 63, v0.9.4's Phase 71, v0.9.5's Phase 73
and v0.9.6's Phase 75 each ran a *prep half* as a phase and handed the *publish half* to
`/gsd-complete-milestone` through a standalone `NN-HANDOFF.md`. This milestone has an unusually
heavy publish half — five requirements rather than one — so Phase 77's own criteria carry the weight
that a phase normally would: each post-tag requirement must arrive at the close as a **pre-written
command with its expected output and its control already recorded**, in an order the handoff
enforces, not as an instruction to go and check something.

Where each requirement lands:

| Requirement | Phase | Half | Closed by |
|-------------|-------|------|-----------|
| ATT-01 | 76 | pre-tag | Phase 76 — the edited file plus the rehearsal that exercises it |
| ATT-02 | 76 | pre-tag | Phase 76 — the rehearsal run's own log and PyPI's unchanged state |
| MSG-06 | 76 | pre-tag | Phase 76 — recorded-RED test on the pre-fix tree, then green |
| ATT-06 | 77 | pre-tag | Phase 77 — the rollback procedure, written before any tag exists |
| REL-17 | 77 | **split** | Prep (bump, CHANGELOG, green tree) closes in Phase 77; the tag, the upload and the GitHub Release are checked at `/gsd-complete-milestone` |
| ATT-04 | 77 | publish | `/gsd-complete-milestone`, on the v0.9.7 release run's log |
| ATT-03 | 77 | publish | `/gsd-complete-milestone`, on PyPI's Simple JSON and Integrity APIs |
| ATT-05 | 77 | publish | `/gsd-complete-milestone`, strictly after ATT-03 passes |
| DOC-25 | 77 | publish | `/gsd-complete-milestone`, written **after** ATT-05 so it describes a state that is already true rather than one that is intended |

DOC-25 is deliberately **not** written during release prep. Its own text requires it to describe
"what the repository actually does after ATT-01 and ATT-05 land", and ATT-05 lands after the
publish; writing it earlier would put a forward-looking claim into a codebase map, which is the same
class of error the line already contains.

- [x] **Phase 76: The `password:`-Free `publish-pypi`, Rehearsed Against the Published v0.9.6 — and MSG-06** - `release.yml`'s production publish step carries no credential and mints its own OIDC token, proven by one `workflow_dispatch` against the already-published `v0.9.6` that reaches PyPI's upload endpoint and is turned away as a duplicate rather than as an unknown publisher — with nothing reaching PyPI. In the same phase, `translator.py`'s last two hardcoded-delimiter DEBUG logs route through `quote_path()`. (completed 2026-09-27)
- [ ] **Phase 77: v0.9.7 Release Prep (prep-only) and the Trusted-Publishing Proof Handoff** - `pyproject.toml` reads `0.9.7` with `uv.lock` and `README.md` regenerated in the same commit, one curated `## [0.9.7]` CHANGELOG section with its tail link block moved and attestations described as audit provenance rather than an install-time gate, a rollback procedure recorded before any tag exists, and a standalone handoff that turns each of the five post-tag requirements into a pre-written command with its expected output and its control — with zero irreversible action taken and those five checkboxes held by a line-scoped fence.

## Phase Details

### Phase 76: The `password:`-Free `publish-pypi`, Rehearsed Against the Published v0.9.6 — and MSG-06

**Goal**: `release.yml`'s production publish step stops reading a long-lived secret and mints its
own OIDC token — and that path is **proven to work against real PyPI before anything irreversible
happens**, by a dispatch that reaches the upload endpoint and is turned away as a duplicate rather
than as an unknown publisher. A duplicate rejection proves the PyPI-side registration matches on all
four fields; an `invalid-publisher` error names a mismatch that is indistinguishable across the
wrong-filename, wrong-environment and not-registered cases, and must be resolved before tagging. In
the same phase, `translator.py`'s two cross-directory relative-path DEBUG logs move to
`quote_path()`, closing the fourth and last module of the MSG-02 family.

**Depends on**: Nothing (first phase of the milestone) — but **gated on an owner prerequisite**: the
Trusted Publisher must be registered on PyPI, through the existing project's Publishing settings,
before the rehearsal is dispatched (constraint 1). No plan task may claim that step.

**Requirements**: ATT-01, ATT-02, MSG-06
**Success Criteria** (what must be TRUE):

  1. **`publish-pypi` still publishes and carries no credential, and nothing was added in its
     place.** The `Publish to PyPI` step remains, still on `pypa/gh-action-pypi-publish@release/v1`,
     with its `with:` block and `password:` line removed and **no** replacement key:
     `grep -c 'PYPI_API_TOKEN' .github/workflows/release.yml` counts only the `TEST_PYPI_API_TOKEN`
     occurrences it counted at the phase base, `grep -c 'attestations'` → 0, `grep -c 'skip-existing'`
     → 0. `publish-testpypi`'s `password:` and `repository-url:` lines are byte-identical to their
     phase-base state, `@release/v1` is unchanged, the top-level `permissions:` block is unchanged,
     and the file still parses as YAML. The phase evidence records the **measured** line numbers of
     the deleted lines rather than repeating `:141-144` (constraint 8). (ATT-01)

  2. **The OIDC exchange is exercised against production PyPI and turned away as a duplicate, not as
     an unknown publisher.** Exactly one `workflow_dispatch` run of `release.yml` is dispatched with
     input tag `v0.9.6`, on a ref whose `release.yml` carries no `password:` and whose
     `pyproject.toml` still reads `0.9.6` (constraint 3, measured on the ref). The run reaches the
     `Publish to PyPI` step — so `validate` and `build` both concluded `success` and the `pypi`
     environment was approved — and that step fails with a `400`/`File already exists` rejection.
     The log carries **zero** occurrences of `invalid-publisher` and zero of
     `invalid-pending-publisher`. The run id, every job's conclusion, and the verbatim failing lines
     are transcribed into the phase evidence. (ATT-02)

  3. **Nothing reached PyPI, and no release artifact was created, from the rehearsal.** Against a
     capture taken **before** the dispatch: the Simple JSON API's file list for `typsphinx` is
     unchanged in count and in every `upload-time`, and 0.9.6's two files still read
     `"provenance": null`; `gh release view v0.9.6` still shows its original assets; the run's
     `create-release` job concluded `skipped` (its `needs: publish-pypi` was not satisfied) and
     `publish-testpypi` concluded `skipped`, with the `if:` evaluation checked against the actual
     dispatch ref and tag input rather than assumed (constraint 7). (ATT-02)

  4. **The disabling annotation is already absent at the rehearsal, read against a non-zero
     control.** `gh run view <rehearsal-run-id> --log | grep -c 'attestations input ignored'` → 0,
     and the same for `disabling Trusted Publishing`, with the identical greps run against v0.9.6's
     release run `35730551619` returning non-zero. The evidence states in its own words that this is
     the **rehearsal** run and that ATT-04 is a reading on the v0.9.7 release run, so this
     observation must not be transcribed forward as ATT-04's evidence.

  5. **A path containing a literal single quote no longer closes the quote early in either
     relative-path DEBUG log.** `_compute_relative_include_path()` and
     `_compute_relative_image_path()` both emit `up_path`/`down_path` through
     `typsphinx/pathfmt.py::quote_path()`; a `grep` over `typsphinx/translator.py` finds zero
     remaining hardcoded `'`-delimited path fragments in either function; and a test drives each of
     the two call sites with a path carrying a literal `'` and asserts the emitted DEBUG record,
     **recorded RED against the pre-fix tree first**. `builder.py`, `writer.py` and
     `template_registry.py` — the family's other three modules, closed in Phase 60 — are unchanged.
     (MSG-06)

**Plans**: 3/3 plans complete (2 waves)

Plans:

**Wave 1**

- [x] 76-01-PLAN.md — ATT-01: the measured two-line deletion of `publish-pypi`'s credential, SC #1 readout and byte-identity invariants, opening `76-ATT-EVIDENCE.md` (D-08)
- [x] 76-02-PLAN.md — MSG-06: new `tests/test_translator_path_quoting_gate.py` recorded RED on the unedited tree, both cross-directory debug logs routed through `quote_path()`, fence and full-suite green (`76-MSG06-EVIDENCE.md`)

**Wave 2** *(after the orchestrator merges wave 1 and pushes the milestone branch, D-06)*

- [x] 76-03-PLAN.md — ATT-02: pre-dispatch gate on the pushed SHA (CI green, validate-only checks, PyPI/Release baselines, control greps), blocking-human owner checkpoint for the one-way dispatch (D-05), exactly one `workflow_dispatch` rehearsal watched to conclusion, SC #2–#4 evidence into `76-ATT-EVIDENCE.md`

### Phase 77: v0.9.7 Release Prep (prep-only) and the Trusted-Publishing Proof Handoff

**Goal**: the 0.9.7 tree is bumped, its CHANGELOG curated into a single `## [0.9.7]` section with
the tail link block moved to match, the release note stating attestations as audit provenance rather
than an install-time gate, a rollback procedure recorded **before any `v0.9.7` tag exists anywhere**,
and a standalone handoff that turns each of the five post-tag requirements into a pre-written
command with its expected output and its control — with **zero irreversible action inside the
phase**. No tag, local or remote; no PyPI upload; no GitHub Release; no secret deleted; no PR merged.

v0.9.7 is a **patch-level release with no breaking change**: no new configuration surface, no new
runtime or dev dependency, no `@preview` change. Its user-visible content is one DEBUG-message
correctness fix and a publishing-mechanics change that adds provenance to the artifacts — which the
release note must describe as *audit* provenance, because neither `pip` nor `uv` verifies
attestations at install time today and a reader must not conclude otherwise.

**Depends on**: Phase 76 — and the dependency is mechanical, not conventional: the version bump
cannot land before ATT-02's rehearsal, because `validate` compares `pyproject.toml` against the
dispatch's tag input and a bumped tree makes the rehearsal fail before the OIDC exchange
(constraint 3).

**Requirements**: ATT-03, ATT-04, ATT-05, ATT-06, REL-17, DOC-25
*(ATT-06 closes in this phase. REL-17's prep half closes here and its publish half at the close.
ATT-03, ATT-04, ATT-05 and DOC-25 are mapped here for **coverage only** and are observed at
`/gsd-complete-milestone` — see the half table above and constraint 12.)*

**Success Criteria** (what must be TRUE):

  1. **The version moves to 0.9.7 in one commit touching every file that carries it.**
     `git show --name-only` on the bump commit lists `pyproject.toml`, `uv.lock`, `README.md` and
     `CHANGELOG.md` together — a commit touching only `pyproject.toml` is the exact shape that once
     killed every dependabot PR. `pyproject.toml:7` is the **sole hand-edited version literal**
     (`0.9.6` → `0.9.7`); `uv.lock`'s `typsphinx` stanza reads `0.9.7` because `uv lock` regenerated
     it, not because it was edited; `README.md`'s Status line reads `v0.9.7`;
     `uv sync --extra dev --locked` exits 0 against the bumped tree;
     `tests/test_readme_version_sync.py` is green; and `RELEASE_VERSIONS` in
     `tests/test_changelog_page_gate.py` gains `"0.9.7"`, with the changelog page gate running at
     **zero skipped** in an environment carrying the `docs` extra. (REL-17, prep half)

  2. **The CHANGELOG carries one curated `## [0.9.7]` section, the tail link block moves with it,
     and the attestation wording cannot be misread as an install-time guarantee.**
     - The bullets standing under `## [Unreleased]` are counted at the phase base, not assumed, and
       promoted into a new `## [0.9.7]` section together with this milestone's own, under a fresh,
       empty `## [Unreleased]` heading placed **above** it.
     - `[Unreleased]`'s compare base moves from `v0.9.6` to `v0.9.7` and a
       `[0.9.7]: …/releases/tag/v0.9.7` link is added, in this same phase.
     - The section says in words that attestations are **audit provenance, not an install-time
       gate** — neither `pip` nor `uv` verifies them today.
     - `scripts/extract_changelog_section.py 0.9.7` is **executed** and its stdout transcribed into
       the phase evidence: non-empty, reproducing the `## [0.9.7]` section byte-for-byte, with no
       `Planned for Future Releases` leakage. (REL-17, prep half)

  3. **The bumped tree is proven green by runs executed in this phase, not on Phase 76's word.**
     The full pytest suite passes twice, once under `LC_ALL=C` since CI runs in English;
     `black --check .`, `ruff check .`, `mypy typsphinx/` and the `@preview` version-sync family
     pass. `tox -e docs-html` and `tox -e docs-pdf` each pass on a **clean** build
     (`rm -rf docs/_build` first — an incremental rebuild under-reports warnings and manufactures a
     false baseline match) against a warning baseline taken at this phase's own base, and
     `tox -e linkcheck` passes with its `working` count recorded fresh. **One** fresh CI run is
     dispatched on the **bumped** tip and has completed, with every job's conclusion transcribed,
     both `windows-latest` and both `macos-latest` lanes named, and `ruff`'s verdict read from the
     `Lint and Format Check` job. A **non-committing** trial merge of `origin/main` into the branch
     passes `uv lock --check` and `ruff check .` on the merged tree, and `main`'s protection, merge
     method and required contexts are read rather than assumed.

  4. **The publish half exists on paper before it exists in fact: a rollback procedure and a
     standalone handoff, both written while no `v0.9.7` tag exists anywhere.**
     - **Rollback (ATT-06, closes here).** A phase artifact names all three parts: restoring
       `password:` to `publish-pypi`; bumping to **0.9.8** rather than retrying 0.9.7, because PyPI
       permanently refuses a re-uploaded filename regardless of git-tag state; and **deleting the
       failed `v0.9.7` tag both locally and on `origin`** (owner decision 2026-09-23 — `git tag -l`
       shows 0.9.1 and 0.9.3–0.9.5 were never tagged at all, so a pushed tag with no release would
       be a first here). It also records the **cheaper path to try first**: a failed publish leaves
       `create-release` *skipped* and the tag unconsumed, so the same run can be re-run within the
       7-day artifact retention window once the registration is fixed (constraint 14).
     - **Handoff.** A standalone `77-HANDOFF.md` enumerates, in an order it states as load-bearing:
       the merge to `main`; the `v0.9.7` tag push; the `pypi` environment's manual approval (an
       expected gate, not a failure); then **ATT-04** as
       `gh run view <id> --log | grep -c 'attestations input ignored'` → `0` with run `35730551619`
       named as the non-zero control and the signal labelled necessary-but-not-sufficient;
       **ATT-03(a)** as the Simple **JSON** API
       (`curl -s https://pypi.org/simple/typsphinx/ -H 'Accept: application/vnd.pypi.simple.v1+json'`)
       returning non-null `provenance` for **both** the 0.9.7 wheel and the 0.9.7 sdist, against
       0.9.6's measured `"provenance": null` control, with the legacy
       `/pypi/<project>/<version>/json` endpoint named as **not** counting; **ATT-03(b)** as
       `https://pypi.org/integrity/typsphinx/0.9.7/<filename>/provenance` returning **200** with
       `publisher` naming `repository` `YuSabo90002/typsphinx`, `workflow` `release.yml` and
       `environment` `pypi`, against a 404 control for 0.9.6's wheel; **ATT-05** — only after ATT-03
       passes — as `gh secret delete PYPI_API_TOKEN` at repository scope **and**
       `gh secret delete PYPI_API_TOKEN --env pypi`, both scopes listed before and after, plus the
       separate revocation on PyPI's token-management page, with `TEST_PYPI_API_TOKEN` re-listed at
       both scopes to prove it survived; **DOC-25** as the
       `.planning/codebase/INTEGRATIONS.md:116-117` rewrite, performed **after** ATT-05 so it
       describes a state that is already true; then the `typsphinx-doc-translations`
       `update-pin.yml` dispatch (a **manual** dispatch — it does not happen as a side effect of the
       parent repo's tag push) and the Read the Docs `en` and `ja` `stable` re-measurement, fetched
       cache-busted. The document is readable without this roadmap or any phase file.

  5. **Zero irreversible action, probed twice, and the five post-tag checkboxes held by a recorded
     line-scoped fence.** `git tag -l 'v0.9.7'` and a remote tag probe both come back empty, each
     with a positive control, at two observations separated by intervening waves rather than by
     wall-clock luck; no 0.9.7 file exists on PyPI; no GitHub Release for `v0.9.7` exists;
     `gh secret list` still shows `PYPI_API_TOKEN` at **both** scopes; and `git diff` over the phase
     shows no change under `typsphinx/` (constraint 13). A `77-CLOSEOUT-GUARD.md` records
     `sha256sum .planning/REQUIREMENTS.md`, `wc -l`, the `PHASE_BASE_SHA` and the verbatim guarded
     lines for **ATT-03, ATT-04, ATT-05, REL-17 and DOC-25**; the same commands re-run MATCH at
     phase close **and once more after `phase.complete`-family tooling has run** — the observation
     that actually catches the automatic flip, because it runs outside any plan's reach. Every
     plan's `SUMMARY.md` frontmatter declares those five in `requirements-completed: []`, and each
     checkbox is read directly out of `.planning/REQUIREMENTS.md` at close, never inferred from
     frontmatter. ATT-06 is the one requirement this phase **does** close, which is why the fence is
     line-scoped rather than whole-file (v0.9.6 Phase 75 precedent).

**Plans**: TBD

**Cross-cutting constraints** *(truths any plan in this phase must carry)*: the prep-only fence
(nothing under `typsphinx/`, `docs/source/` content aside from version strings, or
`.github/workflows/`); no irreversible action of any kind; and the five coverage-only requirements
are never checked here, by hand or by tooling.

## Progress

Phases 1–75 shipped or completed across v0.4.4 → v0.9.6; their per-phase plan counts, statuses and
completion dates are preserved in each milestone's archived roadmap under `milestones/`. The table
below tracks the active milestone only.

**Execution Order:** 76 → 77. The arrow is a mechanical dependency, not a convention: ATT-02's
rehearsal needs `pyproject.toml` to still read `0.9.6`, so the bump cannot land first (constraint 3).
Inside Phase 76 two further orderings are real — the pre-dispatch capture of PyPI's served state
before the dispatch, and MSG-06's RED before its GREEN. The publish half runs after Phase 77, at
`/gsd-complete-milestone`, in the order `77-HANDOFF.md` fixes: tag → ATT-04 → ATT-03 → ATT-05 →
DOC-25.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 76. The `password:`-Free `publish-pypi`, Rehearsed Against the Published v0.9.6 — and MSG-06 | v0.9.7 | 3/3 | Complete | 2026-09-27 |
| 77. v0.9.7 Release Prep (prep-only) and the Trusted-Publishing Proof Handoff | v0.9.7 | 0/TBD | Not started | - |

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.6's live in
[milestones/v0.9.6-ROADMAP.md](milestones/v0.9.6-ROADMAP.md): the one-work-phase-plus-close-prep
shape, the acceptance gate being this project's own documentation build rather than a scratch
fixture, and REL-15 mapped to Phase 75 for coverage only while REL-16 closed inside it — which is
why that phase's `REQUIREMENTS.md` fence was line-scoped for the first time.

- **2026-09-23** — v0.9.7 roadmap created: **Phases 76–77**, 9/9 v1 requirements mapped, zero
  orphans, zero duplicates, continuing numbering from v0.9.6's Phase 75. Two phases at
  `granularity: standard` (nominally 4–6), below the range and **below the research summary's own
  five-phase suggestion**, for reasons recorded in the active-milestone section. Baked in:
  **(a)** ATT-01 and ATT-02 share Phase 76 because the edit's only meaningful evidence *is* the
  rehearsal — splitting them manufactures two single-requirement phases neither of which can be
  verified alone, the over-fragmentation shape this project has twice recorded. **(b)** MSG-06 joins
  Phase 76 rather than taking its own phase or riding along in release prep, because the prep-only
  fence forbids `typsphinx/` changes there and has already deferred MSG-06 once for exactly that
  reason (v0.9.6 Phase 75). **(c)** The **mechanical** 76 → 77 ordering: `validate` compares
  `pyproject.toml` against the dispatch tag input, so a bumped tree makes ATT-02's rehearsal fail
  before the OIDC exchange is ever reached. This is the constraint most likely to be discovered the
  expensive way, and it is why "rehearse, then bump" is not a stylistic preference. **(d)** The
  research's Phase D and Phase E are not phases: they are the **publish half**, and this project
  hands that half to `/gsd-complete-milestone` through a standalone handoff (v0.9.2 Phase 63,
  v0.9.4 Phase 71, v0.9.5 Phase 73, v0.9.6 Phase 75). With five requirements in that half rather
  than one, Phase 77's SC#4 carries the weight a phase normally would — every post-tag reading must
  arrive at the close as a pre-written command with its expected output *and its control*.
  **(e)** DOC-25 is deliberately deferred to after ATT-05 rather than written during prep, because
  its own text requires it to describe a state that has already landed; writing it earlier would put
  a forward-looking claim into a codebase map, the same class of error the line already contains.
  **(f)** ATT-01's `:141-144` citation was **measured and found to overstate the edit** — the
  credential is two lines (`:143-144`), and deleting the cited span literally would delete the
  publish step. Recorded as constraint 8 rather than silently corrected.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog has been empty since
2026-08-04. Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst
error) was promoted into v0.6.5 as Phase 34 / requirement MATH-01 and shipped 2026-07-29. Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** and shipped in v0.7.0. Numbering does not reuse
retired numbers, so the next item filed here is **999.3**.

**Closed at the v0.9.6 close (2026-09-22):**

- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line` (TRN-01) — closed by Phase 74.
- `2026-09-20-literal-block-docstring-args-still-name-only-the-literal-block-node` (IN-01) — closed
  by quick task `260922-tbe`, not deferred a second time.
- `2026-09-20-pypi-history-anchor-unverifiable-under-bot-mitigation-breaks-sphinx-linkcheck` — closed
  by quick task `260922-tkt`. Its own proposed fix would have been a silent no-op: Sphinx's
  `_check_uri` strips the fragment **before** matching `linkcheck_anchors_ignore_for_url`, so a
  pattern carrying `#history` never matches, and a bare `pypi\.org` entry would prefix-match every
  PyPI project page. The landed pattern is end-anchored at the bare project URL.

**Still open after v0.9.6, not scoped:**

- `2026-07-22-add-sphinx-linkcheck-ci-job` — **half closed; it stays in `pending/`.** Phase 72 (v0.9.5)
  landed the `tox -e linkcheck` environment (QUA-13) and listed it on all three surfaces (DOC-24).
  The CI job the todo is actually about (QUA-08, superseding LNK-01) is Future. **Its stated obstacle
  is now gone and has been for two consecutive milestones** — a new workflow file cannot be scheduled
  or `workflow_dispatch`-ed from an unmerged milestone branch, but the environment it would call has
  been on `main` since v0.9.5, so a side PR to `main` is the route whenever it is picked up. Note
  that `links.yml`'s lychee job is **not** this: it scans the repository over HTTP and cannot see
  `#anchor` existence or URLs reached through autodoc docstrings, which is exactly what
  `-b linkcheck` adds. The todo's "Solution" section proposed `linkcheck_ignore` up front; the one
  `linkcheck_*` key this project now has was earned by a measured failure (the PyPI interstitial),
  and nothing else has been.

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — **now disclosed but still unfixed.** REL-16 settled the question at v0.9.6:
  `## [0.9.6]`'s `### Known Limitations` names it with its precondition (multi-master only), both
  symptoms (diverging number; fallback to raw label text) and a workaround. D-07's five-milestone
  exclusion from every published surface is therefore over; the underlying divergence is unchanged.

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — **now scoped into v0.9.7 as Phase 76.** `translator.py`'s two relative-path
  DEBUG logs carry the same hardcoded-`'...'` delimiter shape Phase 60 closed in three other
  modules; the fix is `quote_path()`, which exists. It was deferred once more under Phase 75's
  prep-only fence and **not** picked up when its two siblings were closed at the v0.9.6 close —
  which is why the v0.9.7 roadmap places it in the work phase, not the release-prep phase.

- `2026-09-22-release-yml-uses-a-pypi-api-token-so-trusted-publishing-and` (**ATT-01**,
  `severity: minor`) — **now scoped into v0.9.7 as Phase 76**, with one correction to the todo's own
  text: the fix removes `password:` from `publish-pypi` **only**. `publish-testpypi` keeps
  `TEST_PYPI_API_TOKEN` (owner decision 2026-09-23 — registering a second publisher would leave an
  unexercised path, the shape this milestone exists to avoid).
  `release.yml` publishes with `password: ${{ secrets.PYPI_API_TOKEN }}`, which puts
  `pypa/gh-action-pypi-publish` on the API-token path and turns Trusted Publishing off, and with it the
  action's own default `attestations: true` — so the uploaded artifacts carry no PEP 740 provenance.
  **The workflow file contains no `attestations` line at all**; run `35730551619`'s annotation reports
  the action's effective default, so anyone searching for an `attestations:` key will find nothing. The
  fix is removing `password:` from **both** publish steps (`publish-pypi` and `publish-testpypi`) after
  registering a Trusted Publisher on PyPI — `id-token: write` and the `pypi` environment are already
  declared. It can only be proven on a real tag push, so it belongs in a milestone that publishes; the
  upload itself succeeded, so this is a supply-chain-provenance gap, not a release blocker.

**Dormant seeds:**
- **`SEED-001-readme-quickstart-typst-documents-pdf`** — substantially discharged by v0.7.1's
  CONF-08 + DOC-11 and v0.8.0's DOC-14.
- **`SEED-003-tox-dependency-groups-per-env`** (Future QUA-07) — splitting the `dev` extra into PEP
  735 `[dependency-groups]`. A phase touching `pyproject.toml` or `tox.ini` must not absorb it
  opportunistically.
- **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`** — `typst-py` upstream maintenance
  is slowing, and typsphinx may eventually need to carry an equivalent compile path. It is still the
  single largest structural risk on the horizon, and it has never been scoped into any milestone
  across eleven consecutive scopings.
- **`SEED-005-gsd-workstreams-for-parallel-roadmap-tracks`** — adopt GSD workstreams so independent
  roadmap tracks run in parallel; dormant since v0.9.3.

**Known limitations still shipped, now with one published surface.** After v0.9.6, WR-02's `confdir`
gap and the tripled "Custom template not found" warning remain silent on every public surface;
NUM-01 no longer does. Phase 75's `VALIDATION.md` is at `status: draft` — the third consecutive
release-prep phase to skip `/gsd-validate-phase`, which is worth deciding about deliberately rather
than re-discovering at a fourth close.

**Standing risk carried from v0.9.3:** `flake.nix` is load-bearing while keeping **zero CI
coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only when the
maintainer next enters the shell, and the darwin branch of the per-system guard cannot be exercised
from a Linux machine at all. Accepted deliberately (owner decision 2026-09-02); documented on the
surface itself by v0.9.3's DOC-21.

**Risk discharged at v0.9.6:** `release.yml`'s `create-release` job, which had never run on a v0.9.x
tag, ran on `v0.9.6` and succeeded (run `35730551619`).

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31), v0.9.3 (2026-09-13 — merged, not published), v0.9.4 (2026-09-13 — merged, not published), v0.9.5 (2026-09-16 — merged, not published), v0.9.6 (2026-09-22 — **shipped and published**). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. Active milestone: **v0.9.7 Trusted Publishing and release** (Phases 76–77), roadmapped 2026-09-23.*
