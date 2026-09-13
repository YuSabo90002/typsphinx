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
- 🚧 **v0.9.5 — Docs Link Check and Navigation** — Phases 72–73 (active, started 2026-09-13)

**Active milestone: v0.9.5 — Docs Link Check and Navigation.** Two phases (72–73). It makes
Sphinx's own `linkcheck` a **one-command** check over `docs/source/`, through a new
`tox -e linkcheck` environment that is listed wherever the tox environments are listed. It also
removes the duplicated section children from the root toctree, so the HTML sidebar matches the
document hierarchy. **No builder output changes:** zero lines under `typsphinx/` change in this
milestone. QUA-08, the weekly advisory CI workflow that would run the new environment, was scoped in
and then **deferred to Future** by the owner at roadmap review (2026-09-13; constraint 4).

**This milestone is not published** (owner decision 2026-09-13, the same shape as v0.9.3 and
v0.9.4). There is no tag, no PyPI upload and no GitHub Release. `pyproject.toml` stays at
**`0.9.2`**, and the CHANGELOG bullet(s) go under the existing `## [Unreleased]`. The milestone
branch **is** merged to `main` through a PR. That merge is **REL-14**, and it closes at
`/gsd-complete-milestone`, on the observed merge.

Phase numbering is **continuous across milestones**: v0.9.4 ran Phases 70–71, so v0.9.5 starts at
**Phase 72**.

## Phases

**Phase Numbering:**

- Integer phases (72, 73): Planned milestone work
- Decimal phases (72.1, 72.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.4 ran Phases 70–71, so this milestone starts at **Phase 72**.

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

## 🚧 v0.9.5 — Docs Link Check and Navigation (ACTIVE)

**Milestone Goal:** close one long-deferred defect in this project's own documentation, and land
the local half of another, without changing anything the builders emit.
- **DOC-18:** the root toctree duplicates section children in the HTML sidebar, open since
  2026-08-16. This milestone closes it.
- **The 2026-07-22 linkcheck todo:** this milestone lands its local half, a `tox -e linkcheck`
  environment. The scheduled CI job the todo is actually about (QUA-08) stays deferred.

This serves the core value's publishing-surface clause: "a URL the project publishes must actually
resolve" becomes something one command checks, anchors included. Running that command
automatically on a schedule is future work (constraint 4).

**Binding constraints this roadmap is built on** (settled decisions and measured facts):

1. **Merge-only, unpublished** (owner decision 2026-09-13, the same shape as v0.9.3 and v0.9.4).
   There is no tag (local or remote), no PyPI upload and no GitHub Release. `pyproject.toml` stays
   `0.9.2`. The CHANGELOG bullet(s) go under the existing `## [Unreleased]` beside the four already
   there, and no versioned heading or tail link is created. Which version number the next published
   release uses stays undecided (`0.9.3` and `0.9.4` are both unclaimed). The milestone branch
   **is** merged to `main` through a PR. That merge is **REL-14**, and it executes at
   `/gsd-complete-milestone`. REL-14's checkbox is checked only there, on the observed merge, never
   by phase-completion tooling (constraint 10).

2. **Zero lines change under `typsphinx/`** (binding). The milestone changes no builder output, and
   `git diff --stat 098a8ff6..HEAD -- typsphinx/` is empty at every phase close. This is also why the
   3 counted docs warnings stay (constraint 9): fixing them means editing
   `TypstTranslator.visit_toctree`'s docstring.

   Standing invariants carried forward:
   - zero new runtime dependencies;
   - no new `typst_*` config value;
   - the `@preview` package count stays at **four** with no version change, and
     `tests/test_preview_version_sync.py` stays green;
   - SEED-003 stays dormant;
   - NUM-01, TRN-01, MSG-06, WR-02 and WR-03 are not absorbed;
   - `flake.nix` is not touched;
   - every phase closes green on the full pytest suite.

   No `pyproject.toml` edit is expected: `linkcheck` is a builder built into Sphinx, and the `docs`
   extra already installs Sphinx. If an edit turns out to be needed, it is brought to the owner, not
   made.

3. **`tox -e linkcheck` stays local, and no CI changes.** The environment is **not** added to
   `env_list`, because it needs the network. **No workflow file is added or edited in this
   milestone**. None of `ci.yml`, `docs.yml`, `drift.yml`, `links.yml` or `release.yml` appears in
   the milestone diff, and no new file appears under `.github/workflows/`.

   `main`'s required status checks were measured on 2026-09-13 with
   `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks`: `strict:
   true`, with six contexts. They are `Test Python 3.12 on ubuntu-latest`,
   `Test Python 3.13 on ubuntu-latest`, `Lint and Format Check`, `Type Check`, `Code Coverage` and
   `Build Package`. That set must read identically at the close.

   `links.yml`'s repo-wide lychee check stays as it is, and it remains the per-push/PR raw-URL
   check. What `tox -e linkcheck` adds is `#anchor` existence and URLs reached through autodoc
   docstrings.

4. **QUA-08 is deferred to Future** (owner decision 2026-09-13, at roadmap review). QUA-08 is the
   weekly advisory CI workflow that would run `tox -e linkcheck`. It was scoped into this milestone
   at requirements time and removed when GitHub's own documentation, checked 2026-09-13, showed
   that its proof could not be observed on an unmerged milestone branch:

   - `docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows`,
     `workflow_dispatch`: "This event will only trigger a workflow run if the workflow file exists
     on the default branch." And: "Once a workflow has run at least once, you can dispatch it
     against any branch or tag via the GitHub API or GitHub CLI."
   - Same page, `schedule`: "Scheduled workflows will only run on the default branch."
   - `docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow`: "To trigger
     the `workflow_dispatch` event, your workflow must be in the default branch."

   **A future pickup should plan a side PR to `main` from the start.** v0.9.3 did exactly that for
   `.github/dependabot.yml`: PR #137, merged as `293f0c26`, with byte-identical content on the
   milestone branch so the milestone's own merge stayed conflict-free. The Future entry, with this
   reason, is in `REQUIREMENTS.md`. Nothing in this milestone depends on QUA-08.

5. **Accepted visibility limit** (owner decision 2026-09-13). `https://typsphinx.readthedocs.io/`
   302-redirects to `/en/stable/`, which is built from tag `v0.9.2` (`45962faa`). Without a release,
   the DOC-18 sidebar fix appears in two places:
   - `/en/latest/`, which is rebuilt on every `main` push;
   - ja `latest`, via the translations repo's daily pin update.

   It does not appear on the default `stable` pages until the next published release. Switching
   Read the Docs' default version to `latest` is out of scope, and no phase's success depends on
   `stable` changing.

6. **Branch census and the first push (measured 2026-09-13).**
   - **The branch:** canonical `gsd/v0.9.5-docs-link-check-and-navigation` was created by hand from
     `main` at `098a8ff6`, to pre-empt the commit helper's `gsd/vX.Y-milestone` decoy. It sits at
     `5b8c50f8`, which is `main` + 2 commits touching only `.planning/PROJECT.md`,
     `.planning/REQUIREMENTS.md` and `.planning/STATE.md`, so its tree outside `.planning/` equals
     `main`'s tip.
   - **Local only:** `git ls-remote origin` returns `refs/heads/main` at `098a8ff6` (positive
     control) and nothing for `gsd/v0.9.5*`.
   - **Decoy:** no `gsd/v0.9.5-milestone` decoy exists yet. The helper has re-created one in every
     milestone since v0.9.1, so expect one after the next `gsd-tools` commit.
   - **First push (milestone invariant #5):** the branch reaches `origin` in the **first** phase
     (Phase 72), with the census re-measured just before the push. If a decoy carrying commits has
     appeared, the canonical ref is fast-forwarded to it, HEAD is re-pointed with
     `git symbolic-ref`, and only **then** is the decoy deleted. Deleting it first would orphan
     commits.
   - **CI on the branch:** `ci.yml`'s `push`/`pull_request` triggers are scoped to `main`/`develop`,
     so a push alone runs no CI. Runs on the branch are dispatched with
     `gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation`, and only such a run
     reaches the `windows-latest` and `macos-latest` lanes. `ci.yml` already exists on `main`, so
     this dispatch is unaffected by constraint 4. `main`'s push-triggered CI run on `098a8ff6` is
     the baseline; its run ID and conclusion are read at Phase 72's base, not assumed here.
   - **Dependabot refs:** the local fetch also carries four `origin/dependabot/uv/*` refs
     (`mypy-2.3.1`, `pre-commit-4.6.2`, `sphinx-intl-2.4.0`, `tox-4.61.4`). Whether their PRs are
     open was **not** measured here. Anything that lands on `main` mid-milestone is caught by Phase
     73's trial merge.

7. **Docs measurements need clean builds and the C locale.** Every docs build whose output is
   compared or counted starts from `rm -rf` of its output directory (`docs/_build/html`,
   `docs/_build/linkcheck`, and the typst output). An incremental rebuild under-reports warnings,
   and that is how this project once manufactured a false "baseline match".

   Sphinx's console text is **localised** on the maintainer's machine, because the FHS sandbox
   passes the host `LANG` through (`CLAUDE.md` § Locale). Under that locale, a grep for the English
   strings `document is referenced in multiple toctrees` or `build succeeded, N warnings.` would
   find **zero** and look like a pass. Every such grep therefore runs under `LC_ALL=C`, with a
   positive control: the same command on the pre-fix base must find the messages (5 on 2026-09-13)
   before any post-fix zero counts. Link counts are read from `_build/linkcheck/output.json`, whose
   `status` field is not localised, not from console text.

8. **Counts are measured fresh, never hard-coded.** These figures are 2026-09-13 context, not pass
   thresholds: 95 links `working`, 5 `multiple toctrees` messages, `build succeeded, 3 warnings.`
   and six required contexts. Each phase re-measures at its own base. Only three quantities are
   fixed by the requirements and constraints themselves:
   - **zero** `multiple toctrees` messages after DOC-18;
   - a warning count **unchanged** from the same phase's own pre-fix clean build;
   - required status checks **identical** to the set read at the base.

   The linkcheck `working` count is never compared with 95. What is checked is that it equals the
   total number of checked links.

9. **No warnings gate.** Neither `-W` nor a warning-count gate is added. `-W` could not catch the
   `multiple toctrees` class anyway, because those messages are not counted as warnings. The 3
   counted warnings, rST errors in `TypstTranslator.visit_toctree`'s docstring, stay: fixing them
   edits `typsphinx/` (constraint 2), and both that fix and the gate are Future requirements.

   Also out of scope, per `REQUIREMENTS.md`:
   - any CI job that runs linkcheck (QUA-08 is deferred; per-push/PR or required runs were declined
     outright);
   - link-checking `README.md`, `pyproject.toml` or the repository root (lychee already does);
   - link-checking the ja site;
   - fixing the HTML-vs-Typst parent divergence for `examples/basic` beyond re-measuring it after
     the dedup.

10. **The release-requirement flip is fenced again.** `phase.complete`-family tooling has
    auto-flipped the release requirement to `[x]` against an explicit CONTEXT decision at **8 of the
    9** prior release-prep closes. It did not fire at v0.9.4's Phase 71, and one non-firing is not
    treated as a fix.

    Phase 73 reuses the procedure that caught it: a SHA-256 + `wc -l` + `PHASE_BASE_SHA` fence on
    `.planning/REQUIREMENTS.md`, guarding **REL-14** only. It is re-verified at phase close **and
    once more after `phase.complete` has run**. A whole-file fence works only in a phase where no
    other checkbox is meant to move, so every work requirement sits in Phase 72.

11. **DOC-24's discovery is by grep, and was measured at roadmap time.** On 2026-09-13,
    `git grep -n 'tox -e docs-pdf'` outside `.planning/` returned five hits:
    - the three listing surfaces `REQUIREMENTS.md` names: `CLAUDE.md:33`, `README.md:262` and
      `docs/source/contributing.rst:124`;
    - `.github/workflows/docs.yml:36`, a CI step that *runs* `docs-pdf` rather than listing
      environments (and a workflow file, which constraint 3 keeps out of the diff anyway);
    - `CHANGELOG.md:921`, a bullet inside a released section, which is history.

    The roadmapper reads the last two as not listing surfaces. The phase re-runs the grep at
    execution and records a disposition for every hit, confirming or correcting that reading.
    `CLAUDE.md`'s `tox  # env_list: py312, py313, lint, type, cov, docs` comment stays true, because
    linkcheck is not in `env_list`. The `CLAUDE.md` edit touches neither sync-hazard line (the
    `@preview` versions or the `tox-uv` pin).

12. **Worktree isolation is the standing execution mode** (`CLAUDE.md` § Worktree-isolated
    execution). Every executor provisions with
    `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and runs everything via
    `uv run`. On the maintainer's NixOS machine the recipe runs through the FHS shims inherited
    from the direnv-loaded session.
    - The `dev` extra lacks the `docs` extra (`myst-parser`, `furo`, …), so the CHANGELOG page gate
      skips in a bare worktree venv. A zero-skip reading is taken only where the `docs` extra is
      present.
    - The `docs-html`, `docs-pdf` and `linkcheck` tox environments install `extras = docs` on
      their own through `uv-venv-lock-runner`.
    - In the main checkout, `uv sync --extra dev` alone drops the `docs` extra, so re-sync with
      `--extra dev --extra docs`.

13. **No phase carries a `**UI hint**` line** (orchestrator instruction for this roadmap). This is
    not a frontend UI milestone. The measured consequence: `.claude/gsd-core/bin/lib/ui-safety-gate.cjs:82-109`
    treats an explicit `**UI hint**: no` as the author's override and otherwise sniffs tokens.
    Phase 72's text cannot avoid `sidebar`, `navigation`, `HTML` and `page`, so `ui.plan-gate` is
    expected to false-positive on it. The standing workaround in this project is `--skip-ui` at
    plan time. v0.9.4's alternative was an explicit `**UI hint**: no` line on each phase; whether to
    add one here is the owner's call.

**Two phases: one work phase, then close prep.** With QUA-08 deferred, the three work requirements
are small, file-disjoint and verifiable entirely inside the repository, with nothing waiting on
GitHub-side observation. So no reason to split them survives, and one work phase followed by close
prep matches v0.9.4's shape. Phase 73 is this project's standing prep-only final phase. It takes
zero irreversible action, the merge executes at `/gsd-complete-milestone`, and REL-14 is mapped to it
for coverage only.

- [ ] **Phase 72: `tox -e linkcheck` and Root Toctree Deduplication** - A maintainer runs Sphinx's own link check over `docs/source/` with `tox -e linkcheck`, and every surface listing the tox environments names it. The root `index.rst` toctrees list only the section indexes, so the HTML sidebar shows each User Guide and Examples page once while the Typst output still includes each page exactly once. The milestone branch reaches `origin` with a green 3-OS CI run.
- [ ] **Phase 73: v0.9.5 Close Prep (prep-only, unpublished)** - CHANGELOG bullet(s) land under `## [Unreleased]` with `pyproject.toml` still at `0.9.2`. The tree is proven green on runs executed in this phase, and the PR to `main` is prepared behind a REL-14 checksum fence with zero irreversible action taken.

## Phase Details

### Phase 72: `tox -e linkcheck` and Root Toctree Deduplication

**Goal**: Two changes to this project's own documentation.
- **For maintainers:** Sphinx's own link check over `docs/source/` runs with one command,
  `tox -e linkcheck`. It checks every external link and `#anchor`, including URLs that reach the
  docs through autodoc docstrings, and it passes on today's tree. Every place that lists the
  project's tox environments names the new one, so a contributor finds it where they already find
  `docs-html` and `docs-pdf`.
- **For readers of the HTML documentation:** each User Guide and Examples page appears exactly once
  in the sidebar, nested under its section. That means Configuration, Builders, Templates and
  Output Layout under User Guide, and Basic and Advanced under Examples. Today five of those pages
  are also listed a second time beside their section. After the fix, Sphinx no longer reports them
  as referenced in multiple toctrees.

The PDF never had the defect, because the include-edge state guard already deduplicates it. It
still includes each page exactly once, and the root `index.typ` loses the dead state-guarded
`include()` lines the duplicates produced. The toctree fix follows the owner's decision of
2026-09-13: the conventional hierarchy, not flat visibility. No `:maxdepth:` or furo sidebar setting
stands in for the deleted entries.

**Ordering inside the phase (binding):**
- **QUA-13 before DOC-24:** QUA-13's environment lands before any surface names it, because a
  surface naming an environment that does not yet exist would be false for part of the milestone.
- **DOC-18 is independent:** it shares no file or mechanism with QUA-13 or DOC-24, so it may run
  alongside QUA-13.
- **Base builds first:** the pre-fix clean HTML and `-b typst` builds are taken at `PHASE_BASE_SHA`,
  before either docs edit lands. The after-builds on the tip carry both DOC-18's `index.rst` edit
  and DOC-24's `contributing.rst` edit, so one base/after pair covers both.
- **Evidence last:** the evidence, the first push and the CI dispatch come after every edit, in a
  later wave than the work they audit.

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: QUA-13, DOC-24, DOC-18
**Success Criteria** (what must be TRUE):

  1. **`tox -e linkcheck` exists, is shaped like `docs-html`, and passes on a clean run measured at
     execution time.** `tox.ini`'s diff adds lines and removes none. It adds one
     `[testenv:linkcheck]` section with `runner = uv-venv-lock-runner`, `extras = docs` and
     `changedir = docs`, which runs `sphinx-build -b linkcheck source _build/linkcheck`. `env_list`
     still reads `py312, py313, lint, type, cov, docs`, and the `requires` pin line and its comment
     are untouched. Run with `docs/_build/linkcheck` removed first, the environment exits 0 and
     every entry in `_build/linkcheck/output.json` has status `working`. The total and the `working`
     count are recorded at execution time and are equal.

     Any `linkcheck_*` key in `docs/source/conf.py` (ignore patterns, timeouts, retries, rate
     limits) carries a comment naming the measured failure that required it: the URL, the status
     and the run that showed it. If no failure was measured, `conf.py` gains no `linkcheck_*` key
     (QUA-13; constraints 3, 7, 8).

  2. **Every surface that lists the tox environments names `tox -e linkcheck`, found by grep rather
     than taken from a list.** The repo-wide `git grep -n 'tox -e docs-pdf'` is re-run at execution
     time and recorded in full. Every hit that lists the project's tox environments gains
     `tox -e linkcheck` beside `docs-html`/`docs-pdf` in the same block. It uses the form the
     neighbouring lines use: `tox -e …` in `CLAUDE.md`, `uv run tox -e …` in `README.md` and in
     `docs/source/contributing.rst`. Every hit left unedited is recorded with its reason. The
     roadmap-time grep found five hits, three of them listing surfaces (DOC-24; constraint 11).

  3. **The root toctrees list only the section indexes, and a clean HTML build proves it: zero
     `multiple toctrees` messages, with the warning count unchanged, against a positive control.**

     *The edit.* In `docs/source/index.rst`, the "User Guide" toctree lists exactly
     `user_guide/index` and the "Examples" toctree lists exactly `examples/index`. The file's diff
     removes exactly five entry lines and adds none: `user_guide/configuration`,
     `user_guide/builders`, `user_guide/templates`, `examples/basic` and `examples/advanced`
     (`index.rst:43-45` and `:52-53` on 2026-09-13). These stay as they are:
     - every `:maxdepth:` and `:caption:`;
     - the Getting Started, API Reference and Development toctrees;
     - `docs/source/user_guide/index.rst:6-12` and `docs/source/examples/index.rst:6-10`, the
       toctrees that own those pages, which are absent from the diff.

     No theme or sidebar configuration is added.

     *The proof.* At `PHASE_BASE_SHA`, a clean HTML build runs under `LC_ALL=C` and is filtered for
     `document is referenced in multiple toctrees`. Its non-zero count is recorded (5 on
     2026-09-13), with its `build succeeded, N warnings.` line (3 on 2026-09-13). On the phase tip,
     the same command and filter on a clean build return **0**, and `N` equals the base's `N`. Both
     builds run in the same environment, with its interpreter recorded (DOC-18; constraints 7, 8).

  4. **Each page appears once, in the sidebar and in the Typst output, through its section index.**
     - **In the HTML:** in the clean build's `index.html`, the sidebar navigation holds exactly one
       link to each of the five pages, each nested inside its section index's list item. The count
       is taken from the markup, not from prose. As a control, `user_guide/output_layout` (never
       listed at the root) still appears exactly once. The owner looks at the rendered sidebar at
       UAT, which is the human check the 2026-08-16 todo names.
     - **In the Typst output:** a clean `-b typst` build is compared with the same build at the
       phase base. The root `index.typ` has no `include()` line for any of the five pages; the base
       had state-guarded ones that never fired. Each page's `include()` sits in
       `user_guide/index.typ` or `examples/index.typ`. The master wrapper's
       `typsphinx:include-edges` state lists exactly one edge per page, from its section index.
     - **The `examples/basic` parent divergence:** it is re-measured, not fixed. The parent Sphinx
       HTML selects and the parent the Typst edge map records are both transcribed. If they still
       differ, a todo is filed and nothing more is done here (`REQUIREMENTS.md` Out of Scope).

     (DOC-18.)

  5. **The tree is green locally and on CI, the milestone branch is on `origin`, and nothing outside
     scope moved.**
     - **Local gates:** in the provisioned worktree venv, `ruff check .`, `black --check .`,
       `mypy typsphinx/` and the full pytest suite pass on the phase tip.
     - **Scope:** `git diff --stat <PHASE_BASE_SHA>..HEAD -- typsphinx/ .github/workflows/` is
       empty.
     - **Required checks:** `main`'s required status checks, read with
       `gh api …/required_status_checks` at phase head and at phase close, give the same six
       contexts both times, with `strict` unchanged.
     - **First push:** the branch census is re-measured and any decoy is corrected per constraint 6.
       Then `gsd/v0.9.5-docs-link-check-and-navigation` is pushed with tracking.
     - **CI:** a CI run dispatched on the phase tip with
       `gh workflow run CI --ref gsd/v0.9.5-docs-link-check-and-navigation` has **completed**. Every
       job's conclusion is transcribed, and both `windows-latest` and both `macos-latest` lanes are
       named individually and green. The `Lint and Format Check` job runs lint through tox, so this
       run also exercises the edited `tox.ini` on the runner.

     (Milestone invariant #5; constraints 2, 3, 6.)

**Plans**: 3/6 plans executed (4 waves)

Plans:
**Wave 1**

- [x] 72-01-PLAN.md — base: PHASE_BASE_SHA, clean base HTML and Typst builds with positive control, phase-head reads; then the DOC-18 edit and todo move (wave 1)
- [x] 72-02-PLAN.md — QUA-13: add [testenv:linkcheck] and pass it on a clean run under D-01..D-03 (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 72-03-PLAN.md — DOC-24: name tox -e linkcheck on every listing surface found by grep, plus the D-07 todo note (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 72-04-PLAN.md — DOC-18 proof: same-environment base/tip pair for SC#3, sidebar and Typst for SC#4, parent divergence re-measured (wave 3)
- [ ] 72-05-PLAN.md — tip gates: real tox linkcheck and docs-html runs, local gate quartet, scope fence (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 72-06-PLAN.md — branch census, first push with tracking, one CI dispatch, job transcript, required checks at close (wave 4)

### Phase 73: v0.9.5 Close Prep (prep-only, unpublished)

**Goal**: the milestone is packaged for a merge to `main` and nothing else happens: no version
bump, no tag, no PyPI upload and no GitHub Release. The CHANGELOG bullet(s) go under
`## [Unreleased]` and stay there, the shape v0.9.3 and v0.9.4 used, decided up front.

The one irreversible action this milestone takes, opening and merging the PR to `main`, is
**REL-14**. Per this project's convention it executes at `/gsd-complete-milestone`, not inside this
phase. REL-14 is cited here for coverage only. Its checkbox stays `[ ]` through every plan, and
constraint 10's checksum fence is what keeps it there.

**Depends on**: Phase 72
**Requirements**: REL-14
**Success Criteria** (what must be TRUE):

  1. **The tree is proven unpublished-shaped, with every remote probe positively controlled.**
     `pyproject.toml` still reads `0.9.2`, and no milestone commit changes it. For each of `v0.9.3`,
     `v0.9.4` and `v0.9.5`, both `git tag -l` and a remote tag probe return **empty**. Each remote
     probe carries a positive control (`v0.9.2` present), so an empty result can be told apart from
     a broken probe. PyPI has none of `0.9.3`, `0.9.4` or `0.9.5`, and no GitHub Release exists for
     any of them. Across the whole milestone,
     `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` is empty (constraints 1, 2,
     3).

  2. **The CHANGELOG carries this milestone's changes under `## [Unreleased]` and creates no release
     section.** The new bullet(s) are a pure addition under the existing `## [Unreleased]`, and the
     four bullets already there stay byte-identical. The new bullet(s) follow the register of those
     four. They name the docs sidebar fix and the new `tox -e linkcheck` environment (REL-14 as reworded
     at roadmap revision, 2026-09-13). No bullet claims a CI job that does not exist. `grep` finds no
     `## [0.9.3]`, `## [0.9.4]` or `## [0.9.5]` heading and no matching tail link. The `[Unreleased]`
     compare base stays `v0.9.2`, and `scripts/extract_changelog_section.py` is not run for any new
     section. The CHANGELOG page gate runs with **zero skipped** in an environment carrying the
     `docs` extra (REL-14; constraint 12).

  3. **The tree is proven green by runs executed in this phase, including against `main` as it
     stands at close.** The proof comes from this phase's own runs, not from a prior phase's word:
     - The full pytest suite passes twice, once under `LC_ALL=C`, since CI runs in English.
     - `black --check .`, `mypy typsphinx/`, `ruff check .` and the `@preview` version-sync family
       pass.
     - `tox -e docs-html` and `tox -e docs-pdf` each pass on a clean build under `LC_ALL=C`. The
       `build succeeded, N warnings.` count matches a clean baseline taken at this phase's base,
       with **zero** `multiple toctrees` messages.
     - `tox -e linkcheck` passes on a clean run, with its `working` count equal to the total and
       recorded fresh.
     - One fresh CI run is dispatched on this phase's tip. Every job's conclusion is transcribed,
       with both `windows-latest` and both `macos-latest` lanes named.
     - A **non-committing** trial merge of `origin/main` into the branch passes `uv lock --check`
       and `ruff check .` on the merged tree.
     - `main`'s protection and merge method are read, not assumed. The required contexts equal the
       six read at Phase 72's base.

     (Constraints 3, 6, 7.)

  4. **The REL-14 checkbox is proven held by a recorded SHA-256, and the handoff is standalone.**
     - **The guard:** at phase head, a `73-CLOSEOUT-GUARD.md` records
       `sha256sum .planning/REQUIREMENTS.md`, `wc -l`, the `PHASE_BASE_SHA` and the verbatim guarded
       lines (`grep -n 'REL-14'`). The same commands re-run and MATCH at phase close, **and once more
       after `phase.complete`-family tooling has run**.
     - **The checkbox:** every plan's `SUMMARY.md` declares `requirements-completed: []` for REL-14,
       and the box is read directly out of `.planning/REQUIREMENTS.md` as `[ ]` at close, never
       inferred.
     - **The handoff:** a `73-HANDOFF.md` enumerates every step `/gsd-complete-milestone` must
       execute: the PR from the canonical milestone branch to `main`, the checks that must be green
       before merge, and the merge itself. It states that no tag is pushed, no PyPI upload is made
       and no GitHub Release is created. It marks two steps **not applicable**: the translations
       repo's `update-pin.yml` dispatch, and the Read the Docs `stable` check, since `stable` stays
       on `v0.9.2` (constraint 5).
     - **The observations REL-14 is checked on after the merge:** the merge commit on `origin/main`,
       `pyproject.toml` still at `0.9.2`, no new tag, PyPI 404 and no Release.

     (REL-14; constraint 10.)

**Plans**: TBD

## Progress

**Execution Order:** 72 → 73. The arrow is a real dependency: close prep documents and fences what
Phase 72 landed, and its trial merge and CI run are only meaningful on the finished tree. Inside
Phase 72, two orderings are also real dependencies: QUA-13 → DOC-24, and base builds before either
docs edit.

Phases 1–71 shipped or completed across v0.4.4 → v0.9.4; their per-phase plan counts, statuses and
completion dates are preserved in each milestone's archived roadmap under `milestones/`. The table
below tracks the active milestone only.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 72. `tox -e linkcheck` and Root Toctree Deduplication | v0.9.5 | 3/6 | In Progress | - |
| 73. v0.9.5 Close Prep (prep-only, unpublished) | v0.9.5 | 0/TBD | Not started | - |

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.4's live in
[milestones/v0.9.4-ROADMAP.md](milestones/v0.9.4-ROADMAP.md): the two-phase structure below the
`standard` granularity range, DOC-22 and DOC-23 mapped to Phase 70, the todo move landing with the
ignore flip rather than with the `CLAUDE.md` rewrite, and the REL-13 AMENDED block withdrawing the
ja-catalog clause.

- **2026-09-13** — v0.9.5 roadmap created, then revised the same day at owner review. **Phases
  72–73**, 4/4 v1 requirements mapped, zero orphans, zero duplicates, numbering continued from
  v0.9.4's Phase 71. No research was run (owner decision). Six decisions are built into the
  structure and should not be re-derived during planning:

  - **QUA-08 was removed at review and deferred to Future.** The first draft had three phases
    (72–74). QUA-08 sat in Phase 72 with an open question: how its "`workflow_dispatch` run on the
    milestone branch" proof could happen, given GitHub runs `workflow_dispatch` and `schedule` only
    for a workflow file on the default branch. The owner removed QUA-08 rather than choose a route
    (constraint 4).

  - **One work phase, then close prep.** The first draft split DOC-18 into its own phase so it
    would not wait on QUA-08's route decision. With QUA-08 gone, that reason no longer holds.
    Two phases at `granularity: standard` sit below its nominal 4–6 range, for the reason v0.9.4
    recorded: splitting would manufacture single-requirement phases.

  - **DOC-24 sits with QUA-13 in Phase 72**, ordered after it by wave. It names an environment
    QUA-13 creates, and a surface naming an environment that does not yet exist would be false for
    part of the milestone.

  - **REL-14 maps to Phase 73 for coverage only.** It closes at `/gsd-complete-milestone` on the
    observed merge. Its CHANGELOG clause was reworded at roadmap revision (2026-09-13) to name the
    new `tox -e linkcheck` environment instead of the deferred CI job.

  - **The 3-OS CI run and milestone invariant #5 carry no REQ-ID**, matching v0.9.1–v0.9.4. They are
    held by Phase 72 SC#5 (the first push) and Phase 73 SC#3 (the close tip), each dispatched fresh
    on its own phase's tip.

  - **No `**UI hint**` line on any phase**, per orchestrator instruction. The expected
    `ui.plan-gate` false positive on Phase 72 is recorded in constraint 13.

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

**Todos addressed by v0.9.5** (2026-09-13):

- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar` → **Phase 72** (DOC-18). It
  recorded 4 `multiple toctrees` messages; 5 were measured on 2026-09-13, because
  `examples/advanced` now also appears. The owner settled its open question, hierarchy or flat
  visibility, on 2026-09-13: hierarchy. It moves to `todos/completed/` when DOC-18 is checked.

- `2026-07-22-add-sphinx-linkcheck-ci-job` — **partially addressed; it stays in `pending/`.** Phase
  72 lands the `tox -e linkcheck` environment (QUA-13) and lists it (DOC-24). The CI job the todo is
  actually about (QUA-08, superseding LNK-01) is deferred to Future (constraint 4), so the todo stays
  open for that half. Two notes for whoever picks it up:
  - Its "Solution" section proposed `linkcheck_ignore` for external domains up front. QUA-13 forbids
    speculative settings, so only a measured failure earns one.
  - It named `ci.yml` / `docs.yml` as candidate hosts. Both trigger on push and PR, which QUA-08's
    shape excludes.

  A future pickup should plan a side PR to `main` from the start (constraint 4).

**Still open and deferred** (3 of the 5 pending todos, besides the partially addressed linkcheck
todo above):

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — still excluded from every published surface by owner override D-07.

- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line` (TRN-01, `severity: major`) —
  `doctest_block` has no translator handler, so `>>>` examples lose every line break. Captured
  2026-09-13 during the Issue #91 re-measurement; acknowledged at the v0.9.4 close. A behaviour
  change under `typsphinx/`, so out of this milestone's scope by construction (constraint 2).

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — `translator.py`'s two relative-path DEBUG logs carry the same
  hardcoded-`'...'` delimiter shape Phase 60 closed in three other modules; the one-line fix is
  `quote_path()`, which now exists. Also a `typsphinx/` edit, so excluded by constraint 2.

**Dormant seeds:**
- **`SEED-001-readme-quickstart-typst-documents-pdf`** — substantially discharged by v0.7.1's
  CONF-08 + DOC-11 and v0.8.0's DOC-14.
- **`SEED-003-tox-dependency-groups-per-env`** (Future QUA-07) — splitting the `dev` extra into PEP
  735 `[dependency-groups]`. A phase touching `pyproject.toml` or `tox.ini` must not absorb it
  opportunistically, and Phase 72 edits `tox.ini`.
- **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`** — `typst-py` upstream maintenance
  is slowing, and typsphinx may eventually need to carry an equivalent compile path. It is still the
  single largest structural risk on the horizon, and it has never been scoped into any milestone
  across eight consecutive scopings.
- **`SEED-005-gsd-workstreams-for-parallel-roadmap-tracks`** — adopt GSD workstreams so independent
  roadmap tracks run in parallel; dormant since v0.9.3.

**Known limitations still shipped with no published surface** after v0.9.2, carried unchanged
through v0.9.3 and v0.9.4 and into v0.9.5, none of which changes product behaviour: WR-02's `confdir`
gap, the tripled "Custom template not found" warning, and NUM-01's `numref` per-master divergence.
The `### Known Limitations` decision stays open for the next *published* release; v0.9.5 publishes
nothing, so it does not force it.

**Standing risk carried from v0.9.3:** `flake.nix` is load-bearing while keeping **zero CI
coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only when the
maintainer next enters the shell, and the darwin branch of the per-system guard cannot be exercised
from a Linux machine at all. Accepted deliberately (owner decision 2026-09-02); documented on the
surface itself by v0.9.3's DOC-21. This milestone adds no workflow and does not touch `flake.nix`.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31), v0.9.3 (2026-09-13 — merged, not published), v0.9.4 (2026-09-13 — merged, not published). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. Active milestone: v0.9.5 (Phases 72–73), roadmap created and revised 2026-09-13 (QUA-08 deferred to Future at owner review).*
