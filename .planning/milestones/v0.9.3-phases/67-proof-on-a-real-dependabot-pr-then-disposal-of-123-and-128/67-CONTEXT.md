# Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128 - Context

**Gathered:** 2026-09-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Close DEP-02 from a real `uv`-ecosystem dependabot PR's own check runs and step logs, then — and
only then — dispose of #123 (`ruff`) and #128 (`docutils`, grouped) on their merits, with the
grouped-update coverage gap written down (DEP-05). Nothing under `typsphinx/` (constraint 13), no
workflow edit (constraint 3), no `.github/dependabot.yml` edit.

**State at discussion time (measured 2026-09-12):**
- **SC#2 is already measured by Phase 66.** `uv` PR #138 (`ruff`) opened at `2026-09-12T10:39:49Z`
  while `pip` PR #123 (`ruff`) was open — a `uv` PR *can* open for a dependency with an open `pip`
  PR. Removing the `pip` entry from `main` closed neither #123 nor #128 (66's post-merge snapshot at
  `10:58:41Z`; still `OPEN` today, `updatedAt` unchanged). No mechanical close has occurred.
- **SC#1 evidence exists.** #138 (`dependabot/uv/ruff-0.16.6`, head `88088071…`) CI run
  `34689041575`: all 15 checks pass. Step-level, Lint / Type / Test-3.12-ubuntu each show
  `Install dependencies` (`uv sync --extra dev --locked`) `success` followed by
  `Run lint|type check|tests with tox` `success`.
- **ruff.** #138 bumps `ruff` 0.15.20 → 0.16.6 and `pyproject.toml` `>=0.15,<0.16` → `>=0.15,<0.17`,
  both files in one commit. PyPI latest `ruff` is 0.16.7. `git merge-tree --write-tree HEAD
  refs/pull/138/head` from the milestone tip is conflict-free. `ruff 0.16.6 check .` run on the
  milestone tip inside the FHS runner (`typsphinx-fhs-run uvx --from ruff==0.16.6`) →
  `All checks passed!`. `tox -e lint` is `black --check .` + `ruff check .` (`tox.ini:44-45`); `ruff
  format` is not a gate. No file outside `pyproject.toml`/`uv.lock`/`.planning` names `0.15.20`.
- **docutils.** docutils 0.23 is released, but PyPI-latest Sphinx 9.1.0 requires
  `docutils<0.23,>=0.21`. Phase 66's `uv` run failed the `docutils` update with
  `dependency_file_not_resolvable`, so no `uv` successor to #128 exists or can open until Sphinx
  relaxes that cap. #128 changes `pyproject.toml` only; merging it would reintroduce the `--locked`
  failure on `main`.
- **#128 is a grouped PR** (`dependabot/pip/sphinx-typst-stack-12b5b89b5a`, title "…in the
  sphinx-typst-stack group across 1 directory"), contradicting SC#4's and `PROJECT.md`'s premise —
  see D-06.

</domain>

<decisions>
## Implementation Decisions

### DEP-02 — the proof

- **D-01: DEP-02 is closed by reading #138's existing CI run `34689041575`; no rerun, no `@dependabot` command.** It is a real dependabot PR's own run, triggered by dependabot's push during Phase 66, so it satisfies SC#1's "the PR's own check runs and step logs" without any new external action. The executor transcribes every job's conclusion literally (all 15 checks, Windows and macOS lanes named individually), and for each Lint / Type / Test job reads the step list: `Install dependencies` `success` and the following `Run … with tox` step reaching a conclusion. SC#1 asks that jobs *run to a conclusion*, not that they pass — record literally either way. Record that this run predates Phase 67 (Phase 66 execution) and that its head is `SC1_SHA` from `66-DEPENDABOT-EVIDENCE.md`.
- **D-02: SC#2 is closed by citation, not re-measured by an action.** Cite `66-MAIN-PR-EVIDENCE.md` § D-02 pre-merge snapshot and `66-DEPENDABOT-EVIDENCE.md` § D-02 post-merge snapshot / § uv pull requests (#138 opened while #123 open → "can"), then re-snapshot #123 and #128 read-only at Phase 67 execution time before touching either. Both stayed open until D-01's proof was recorded, so SC#2's "both stay open until criterion 1" branch applies; no close in this phase is mechanical. Ordering is binding: D-01 recorded → D-03..D-05 dispositions.

### ruff — #123 and #138

- **D-03: Merge #138 into `main`; close #123 as superseded by #138.** Merits (SC#3, written into the evidence): `ruff` is a `dev`-extra tool with no runtime or user-install effect; ruff 0.16.6 raises no new violation on `main` (#138's Lint job) or on the milestone tip (the FHS measurement above); the REL-12 merge stays conflict-free (`merge-tree`). The NIX-01 interaction is stated explicitly: NIX-01 was measured and closed on the milestone branch against its own `uv.lock` (0.15.20) and stays closed; NIX-01's binding sense is "the version `uv.lock` pins", so after REL-12 the maintainer's shim will report whatever `main`'s lock then pins (0.16.x), which is consistent with NIX-01 rather than a regression of it. Order: merge #138 first, then close #123 with a terse English comment (e.g. "Superseded by #138."). Before merging, re-read #138's head SHA and `mergeStateStatus`; if dependabot has moved the head (e.g. to 0.16.7), the merge gate is the new head's own checks being green, and the milestone-tip `ruff check .` is re-measured at the new version with the FHS runner. — **Reversibility:** one-way — a merge to the default branch is public, frees a PR-limit slot so dependabot opens further PRs, and can only be countered by a revert PR; the planner puts a `checkpoint:decision` (owner go-ahead) immediately before the merge and before posting any comment.
- **D-04: The milestone branch does not absorb `main` now; REL-12 carries #138 in.** No `origin/main` → milestone merge in this phase, no local `uv sync` re-provisioning. Until REL-12 the maintainer's local shim reports 0.15.20 while `main`'s CI runs 0.16.6; that divergence is recorded, not fixed. REL-12's own CI run (constraint 7, lint authority) is where the merged tree is linted under 0.16.x.

### docutils — #128

- **D-05: Close #128 with a terse English reason comment.** Merit: PyPI-latest Sphinx 9.1.0 caps `docutils<0.23`, so widening typsphinx's range to `<0.24` admits no installable combination with any released Sphinx; the `uv` updater's own attempt failed with `dependency_file_not_resolvable`; and #128 as a `pyproject.toml`-only `pip` PR would reintroduce the `--locked` failure on `main`. Draft comment shape: "Sphinx 9.1.0 caps docutils<0.23, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap." Exact wording owner-approved before posting. Re-measure Sphinx's latest release and its `docutils` requirement on PyPI at execution time; **if Sphinx has relaxed the cap, HALT and return to the owner** — the merit premise has changed. — **Reversibility:** one-way (the comment is public; the close itself can be reopened) — `checkpoint:decision` before posting.

### SC#4 — grouped-update coverage gap

- **D-06: Correct SC#4's premise with `AMENDED 2026-09-12` blocks in `ROADMAP.md` (after Phase 67 SC#4) and `PROJECT.md` (after the "neither #123 nor #128 exercises a grouped update" bullet); `REQUIREMENTS.md` DEP-05 stays literal (its text is correct).** Correction: #128 *is* a `sphinx-typst-stack` group PR; under `uv` no group PR opened because the group's `docutils` member hit `dependency_file_not_resolvable` — itself a live instance of the "genuinely unresolvable dependency graph" SC#4 names; and the PR that carries the proof (#138) is not grouped. So the conclusion stands unchanged: this milestone's proof does not cover a grouped `uv` update, and a future grouped PR failing at resolution is an uncovered case, not a regression. The AMENDED blocks are written and committed with this CONTEXT; the phase's evidence must still state the coverage gap in writing (SC#4), citing the `docutils` failure. The verifier reports the literal and the amended reading separately.

### Claude's Discretion

- Merge method for #138 (follow recent dependabot merges on `main`, e.g. #126/#127).
- Evidence file naming and plan/wave split, provided D-01 → D-02 → dispositions ordering holds and each one-way action sits behind its owner checkpoint.
- Exact comment wording drafts for #123 and #128 (English, terse, not blaming — owner approves the final text).

### Folded Todos

- `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` (`resolves_phase: 67`) — the source defect: dependabot PRs died at `uv sync --locked`. Its "prove it on a real dependabot PR" and "decide what to do with the two open PRs" asks are exactly D-01..D-05. Closing the todo belongs to this phase's completion.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and binding constraints
- `.planning/ROADMAP.md` § "Phase 67" — goal, SC#1–SC#4 (and the D-06 `AMENDED` block under SC#4).
- `.planning/ROADMAP.md` § binding constraints 2 (incl. its `AMENDED 2026-09-12` block), 3, 4, 7, 13, 14.
- `.planning/REQUIREMENTS.md` — DEP-02, DEP-05 (literal); NIX-01 (for D-03's interaction note).
- `.planning/PROJECT.md` — v0.9.3 section incl. the D-06 `AMENDED` block.
- `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — source defect.

### Phase 66 evidence this phase cites
- `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-CONTEXT.md` — D-02 (mechanical vs merit close), deferred #128-grouped correction.
- `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-MAIN-PR-EVIDENCE.md` § D-02 pre-merge snapshot.
- `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md` § uv update job conclusion (the `docutils` `dependency_file_not_resolvable` log), § D-02 post-merge snapshot, § uv pull requests, § SC#1 selection (`SC1_PR`/`SC1_SHA`), § D-05 leg 2 CI uv on the PR head (`SC1_RUN_ID = 34689041575`), § D-06 observations.

### Files read (not edited)
- `pyproject.toml:29,40` — `docutils>=0.21,<0.23`, `ruff>=0.15,<0.16`.
- `uv.lock` — `ruff` 0.15.20, `docutils` 0.22.4, `sphinx` 9.1.0.
- `tox.ini:44-45` — lint gate is `black --check .` + `ruff check .`.
- `flake.nix` — `typsphinx-fhs-run` (the FHS runner used for the ruff 0.16.6 measurement).

### External (live, via `gh` / PyPI JSON)
- PRs #123, #128, #138 (`gh pr view`, `gh pr checks`, `gh run view 34689041575 --json jobs`).
- `https://pypi.org/pypi/sphinx/json` (`requires_dist` docutils cap), `…/docutils/json`, `…/ruff/json`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `gh` is authenticated and reaches PR state, check runs and step lists; PyPI's JSON API is reachable without auth.
- `git fetch origin refs/pull/<n>/head` + `git show` / `git merge-tree` reads a bot PR's head without checking it out (Phase 66 pattern).
- The FHS runner `typsphinx-fhs-run` (path resolvable from the `ruff` shim script) runs generic-linux ELFs such as `uvx --from ruff==X` on NixOS; plain `uvx` outside it fails on the stub-ld.

### Established Patterns
- Evidence recorded verbatim in a phase evidence markdown; no new script, no new test (Phase 64–66 convention).
- Versions, SHAs and PR states re-measured and recorded literally at execution time, not copied from this CONTEXT.
- Outward-facing text (PR comments) in English, terse, reviewed by the owner before posting.
- Premise corrections go into `AMENDED <date> (Phase N discuss, owner-approved)` blocks; REQUIREMENTS.md stays literal.

### Integration Points
- `main` is protected: 6 required checks, `strict: true` — #138 must be up to date with `main` at merge (`mergeStateStatus` was `CLEAN`).
- Merging #138 frees one of the 5 PR-limit slots; dependabot may open further `uv` PRs afterwards — record, do not act.

</code_context>

<specifics>
## Specific Ideas

- The owner asked what DEP-02 actually requires before deciding; the answer that settled it: DEP-01 (Phase 66) proved the PR's *contents*, DEP-02 proves the PR's *CI outcome*, and #138's existing run already carries that outcome — so no new run is needed.
- `PROJECT.md`'s neighbouring claim that #123/#128 "will need closing so the `uv` ecosystem opens fresh ones" is also superseded by measurement (#138 opened with #123 open). Not amended here (outside D-06's approved scope); recorded for the milestone-close PROJECT.md update.

</specifics>

<deferred>
## Deferred Ideas

- Lockfile-only `uv` PRs #139 (`tox`), #140 (`sphinx-intl`), #141 (`pre-commit`), #142 (`mypy`) — outside DEP-05's text; not merged, closed or commented on in this phase.
- A future docutils 0.23 adoption once Sphinx relaxes its cap — its own work, triggered by dependabot's re-proposal.
- `versioning-strategy` tuning if lockfile-only PR volume crowds the limit of 5 (carried from Phase 66).

### Reviewed Todos (not folded)
- `2026-07-22-add-sphinx-linkcheck-ci-job.md`, `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`,
  `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`,
  `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md`,
  `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` —
  keyword-score matches only; unrelated to dependabot PR disposal.

</deferred>

---

*Phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128*
*Context gathered: 2026-09-12*
