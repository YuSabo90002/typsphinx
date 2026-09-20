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
- 🚧 **v0.9.6 — Doctest block rendering and release** — Phases 74–75 (active, started 2026-09-16)

**Active milestone: v0.9.6 — Doctest block rendering and release.** Two phases (74–75). It gives
`doctest_block` — the node docutils builds from any `>>>`-led block, with no markup opt-out
available to the author — the translator handler it has never had, so a Google/NumPy-style
`Examples:` docstring renders as a code block instead of collapsing onto one line of plain text. It
clears the docutils reST errors this project's own docstrings raise in the same build. Then it
**publishes**, after three consecutive merge-only milestones: `pyproject.toml` goes `0.9.2` →
`0.9.6`, the six bullets carried under `## [Unreleased]` from v0.9.3, v0.9.4 and v0.9.5 are promoted
into `## [0.9.6]` with this milestone's own, and tag → PyPI → GitHub Release follow at
`/gsd-complete-milestone`.

Phase numbering is **continuous across milestones**: v0.9.5 ran Phases 72–73, so v0.9.6 starts at
**Phase 74**.

## Phases

**Phase Numbering:**

- Integer phases (74, 75): Planned milestone work
- Decimal phases (74.1, 74.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.9.5 ran Phases 72–73, so this milestone starts at **Phase 74**.

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

## 🚧 v0.9.6 — Doctest block rendering and release (ACTIVE)

**Milestone Goal:** make a `>>>` example render as a code block instead of collapsing onto one line,
clear the reST errors this project's own docstrings raise in the same build, and then publish — the
first published release since v0.9.2, carrying three merge-only milestones' worth of change with it.

- **TRN-01 / TRN-02:** `doctest_block` has no `TypstTranslator` handler, so the node falls through
  `unknown_visit()` (`translator.py:5819`) while its `Text` children are still visited as ordinary
  inline text — every line break is lost. It is a **parser-level** construct
  (`docutils/parsers/rst/states.py:1251` matches `r'>>>( +|$)'`, `:1698` builds the node), so a
  docstring author cannot opt out of it. This milestone renders it exactly as a code block, the shape
  all three of Sphinx's own writers use.
- **QUA-14:** the same clean `-b typst` build reports docutils `Unexpected indentation` and
  `Block quote ends without a blank line` messages originating in typsphinx's own docstrings.
  `milestones/v0.9.5-REQUIREMENTS.md`'s Future section names exactly these as the prerequisite a
  docs warnings gate would first need fixed.
- **REL-15 / REL-16:** publish v0.9.6, and settle the `### Known Limitations` question on the record
  — the question v0.9.5 could leave open only because it published nothing.

This serves the core value directly on its first clause: a node family that renders *wrong* rather
than merely unsupported is the sharpest case of output that is not faithful to its source. It also
serves the publishing clause — three milestones of fixes currently reach no installed user at all,
and `/en/stable/` has stood on tag `v0.9.2` since 2026-08-31.

**Binding constraints this roadmap is built on** (settled decisions and measured facts):

1. **This milestone publishes** (owner decision 2026-09-16), unlike v0.9.3, v0.9.4 and v0.9.5. But
   every irreversible action still executes at `/gsd-complete-milestone`, not inside Phase 75: the
   PR merge to `main`, the `v0.9.6` tag push, `release.yml`'s PyPI upload and the GitHub Release.
   **REL-15's checkbox is checked only there**, against observed evidence — the merge commit on
   `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`, and
   `gh release list` — **and never by phase-completion tooling** (constraint 9).

2. **The version is `0.9.6`** (owner decision 2026-09-16), keeping the milestone number and the
   released version aligned, the rule every milestone here has followed. `0.9.3`, `0.9.4` and
   `0.9.5` stay permanently unclaimed on PyPI exactly as `0.9.1` already is; the tag series reads
   `v0.9.0` → `v0.9.2` → `v0.9.6`. The `## [Unreleased]` section holds **six** bullets today (one
   Added, four Changed, one Fixed; measured 2026-09-16), five of them explicitly "This has no effect
   on installing or using typsphinx". They are promoted into `## [0.9.6]` together with this
   milestone's own bullets, and the **link block at the file's end moves in the same phase**:
   `[Unreleased]`'s compare base `v0.9.2` → `v0.9.6`, plus a new `[0.9.6]` releases/tag link.

3. **Every node-handler change ships its own recorded-RED GATE-01 acceptance fixture that goes
   through a real `typst.compile()`.** This is a standing bar in this repo since v0.6.0 Phase 11,
   where `tests/test_pdf_render_gate.py` established the `sphinx-build` → `typst.compile()` →
   `pypdf` pattern. A string assertion on the emitted `.typ` alone does not satisfy it, and neither
   does a fixture that was never observed failing on the pre-handler tree. TRN-01 and TRN-02 both
   require it, and TRN-02 requires **one fixture per context**.

4. **Counts are measured fresh, never transcribed.** These figures are 2026-09-16 context measured
   on `main` at `6cc44f22`, not pass thresholds: `build succeeded, 5 warnings.`, of which **2** are
   `unknown node type: <doctest_block ...>` in `api/index` and **3** are the docutils messages
   QUA-14 names (`TypstTranslator.visit_toctree` docstring `:5` and `:21` ERROR, `:6` WARNING); and
   the single `text("...")` run at `api/index.typ:811`. Each phase re-measures at its own base. Only
   three quantities are fixed by the requirements themselves:
   - **zero** `unknown node type: <doctest_block` lines after TRN-01;
   - **zero** `Unexpected indentation` / `Block quote ends without a blank line` messages
     originating in typsphinx's own docstrings after QUA-14;
   - a total `build succeeded, N warnings.` count that has **not risen** against the same phase's
     own pre-fix clean build.

5. **Docs measurements need clean builds and the C locale.** Every docs build whose output is
   compared or counted starts from `rm -rf` of its output directory. An incremental rebuild
   under-reports warnings, and that is how this project once manufactured a false "baseline match".
   Sphinx's console text is **localised** on the maintainer's machine, because the FHS sandbox
   passes the host `LANG` through (`CLAUDE.md` § Locale), so a grep for `unknown node type`,
   `Unexpected indentation` or `build succeeded, N warnings.` would find **zero** and look like a
   pass. Every such grep runs under `LC_ALL=C`, with a positive control: the same command on the
   pre-fix base must find the messages before any post-fix zero is believed.

6. **QUA-14's discovery is a fresh full-build measurement, not a lookup of the docstrings the
   requirement names.** A success criterion that checked only `TypstTranslator.visit_toctree` would
   be wrong. The census comes from the base clean build's own output, filtered for the two message
   classes, with every hit's originating file and line transcribed; **any** docstring anywhere under
   `typsphinx/` raising the same class is in scope. This project has been burned before by scoping
   a "clear all X" requirement to the files the requirement's text happened to name.

7. **Scope fence and standing invariants.** The changes under `typsphinx/` are the `doctest_block`
   handler and docstring text — nothing else. Not absorbed, by name: NUM-01, MSG-06, WR-02, WR-03,
   and any sweep of other nodes still reaching `unknown_visit()` (owner decision 2026-09-16 —
   `doctest_block` is the only node falling through on this project's own docs, and a broader
   candidate set would first need re-measuring against a large corpus, as v0.6.0 Phase 15 did).
   Carried forward unchanged: zero new runtime dependencies; no new `typst_*` config value; the
   `@preview` package count stays at **four** with no version change and
   `tests/test_preview_version_sync.py` stays green; SEED-003 stays dormant; `flake.nix` is not
   touched; no workflow file is added or edited; every phase closes green on the full pytest suite.

8. **Two adjacent mechanisms are already measured working and stay out of scope.**
   `sphinx.ext.doctest`'s `.. doctest::` / `.. testcode::` / `.. testoutput::` directives build
   `literal_block` subclasses and already go through `visit_literal_block`; only the unmarked-up
   `>>>` form is broken. And `TrimDoctestFlagsTransform`
   (`sphinx/transforms/post_transforms/code.py:100`) already strips `# doctest: +FLAG` from
   `doctest_block` nodes before any writer sees them, so no `trim_doctest_flags` equivalent is
   needed in the translator. The language tag, by contrast, **cannot** be inherited:
   `HighlightLanguageTransform` assigns `node['language']` only to `literal_block`, so
   `translator.py:2570`'s `node.get("language", "")` would read empty and emit an unhighlighted
   fence. The handler supplies it. Both ` ```pycon ` and ` ```python ` were confirmed to compile
   under a real `typst.compile()`, so the choice is a highlighting-quality one, not a validity one.

9. **The release-requirement flip is fenced, and the fence is line-scoped this time.**
   `phase.complete`-family tooling has auto-flipped the release requirement to `[x]` against an
   explicit CONTEXT decision at **9 of the 10** prior release-prep closes; the one non-firing
   (v0.9.4's Phase 71) is an outlier, not a fix. Phase 75 reuses the procedure that caught it — a
   SHA-256 + `wc -l` + `PHASE_BASE_SHA` fence on `.planning/REQUIREMENTS.md`, re-verified at phase
   close **and once more after `phase.complete` has run**. Unlike v0.9.5's Phase 73, this phase
   carries **two** requirements and REL-16 legitimately closes inside it, so the fence guards the
   verbatim **REL-15** lines (`grep -n 'REL-15'`) rather than the whole file, with REL-16's line
   recorded separately as expected-to-move. Every work requirement sits in Phase 74 so nothing else
   moves.

10. **Branch census (measured 2026-09-16).** The canonical milestone branch
    `gsd/v0.9.6-doctest-block-rendering-and-release` exists and is checked out, at `94497c0a` =
    `main` (`6cc44f22`) + 2 commits touching only `.planning/`, so its tree outside `.planning/`
    equals `main`'s tip and **`6cc44f22` is the milestone base** for every scope fence. No
    `gsd/v0.9.6-milestone` decoy exists yet; the commit helper has re-created one in every milestone
    since v0.9.1, so expect one. If a decoy carrying commits appears, the canonical ref is
    fast-forwarded to it and HEAD re-pointed with `git symbolic-ref` **before** the decoy is
    deleted — deleting it first orphans commits. The branch reaches `origin` in the **first** phase
    (74), with the census re-measured just before the push. `ci.yml`'s triggers are scoped to
    `main`/`develop`, so a push alone runs no CI; runs on the branch are dispatched with
    `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release`, and only such a run
    reaches the `windows-latest` and `macos-latest` lanes. `main`'s required status checks were six
    contexts when last read (2026-09-13); each phase reads them rather than assuming them.

11. **Worktree isolation is the standing execution mode** (`CLAUDE.md` § Worktree-isolated
    execution; `use_worktrees: true`, `worktree.baseRef: "head"`). Every executor provisions with
    `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and runs everything via
    `uv run`; on the maintainer's NixOS machine that runs through the FHS shims inherited from the
    direnv-loaded session. Two consequences this milestone will hit:
    - the `dev` extra lacks the `docs` extra (`myst-parser`, `furo`, …), so the CHANGELOG page gate
      **skips** in a bare worktree venv. A zero-skip reading is taken only where the `docs` extra is
      present. In the main checkout, `uv sync --extra dev` alone drops the `docs` extra, so re-sync
      with `--extra dev --extra docs`.
    - a fresh worktree `.venv` may be built on a different interpreter than the main checkout's, so
      pytest counts are compared only after both `pyvenv.cfg` `version_info` values are read.

12. **No phase carries a `**UI hint**: yes` line; both carry an explicit `**UI hint**: no`.** This is
    not a frontend UI milestone — "rendering", "page" and "layout" here mean Typst/PDF output.
    `ui-safety-gate` treats an explicit `**UI hint**: no` as the author's override and otherwise
    sniffs tokens, and this project has a standing record of `ui.plan-gate` false-positiving on
    PDF/HTML/rendering phases. The `--skip-ui` flag at plan time remains the fallback if it fires
    anyway.

13. **Publishing is what moves the published docs.** `https://typsphinx.readthedocs.io/` redirects
    to `/en/stable/`, built from tag `v0.9.2`; publishing v0.9.6 moves `stable` forward on its own,
    which is the point. Switching Read the Docs' default version is therefore **unnecessary and out
    of scope**. The `typsphinx-doc-translations` `update-pin.yml` dispatch is a **manual** step in
    the release handoff — it does not happen as a side effect of the parent repo's tag push. And
    `release.yml`'s `create-release` job has real end-to-end evidence from the v0.7.1 publish (run
    `31462027486`) and v0.8.0 (run `31861043480`) but **has never run on a v0.9.x tag**; per
    PROJECT.md's standing constraint, a failure at the real tag push is handled inside the release
    work rather than deferred.

**Two phases: one work phase, then release prep.** The three work requirements are one handler, its
two-context gate, and a docstring cleanup measured by the *same* clean `-b typst` build — the
`build succeeded, N warnings.` ledger that TRN-01 must drive to zero on one class is the ledger
QUA-14 must not raise on the other. Splitting them would split one base/tip measurement pair across
two phases and manufacture a single-requirement phase, which is the shape this project has twice
recorded as over-fragmentation. Phase 75 is this project's standing prep-only final phase, the same
structure v0.9.3 (69), v0.9.4 (71) and v0.9.5 (73) used — with the difference that this one bumps a
version and promotes a CHANGELOG section, because this milestone publishes.

- [x] **Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors** - A `>>>` example renders in Typst output as a code block with its line structure intact and a language tag the handler supplies itself, in both positions autodoc/napoleon place one, each proven by a recorded-RED fixture through a real `typst.compile()`. The same clean `-b typst` build of `docs/source` reports zero `doctest_block` unknown-node warnings and zero docutils indentation/block-quote messages from typsphinx's own docstrings, with the total warning count not risen. (completed 2026-09-20)
- [ ] **Phase 75: v0.9.6 Release Prep (prep-only)** - `pyproject.toml` reads `0.9.6` with `uv.lock` regenerated in the same commit, the six carried `## [Unreleased]` bullets are promoted into a curated `## [0.9.6]` section with the tail link block moved to match, the `### Known Limitations` question is settled on the record either way, and the bumped tree is proven green — with zero irreversible action taken and REL-15 held by a checksum fence.

## Phase Details

### Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors

**Goal**: A `>>>` example renders in Typst output as a **code block** — the same construct
`literal_block` produces, codly-styled, with a language tag the handler supplies itself — in both
positions autodoc/napoleon actually place one. And the same clean `-b typst` build of `docs/source`
stops reporting the docutils reST errors that typsphinx's own docstrings raise.

What a reader observes today, in output this project itself ships: `api/index.typ:811` carries a
six-line, three-prompt `compute_content_include_path` example as a single `text("...")` run — the
prompts, the continuation and the output all run together on one line. After this phase the lines
survive, the block reads as code, and the build stops warning that it did not know what the node
was.

**Ordering inside the phase (binding):**

- **Base build first.** The pre-fix clean `-b typst` build is taken at `PHASE_BASE_SHA` under
  `LC_ALL=C`, with its per-class counts and the verbatim `api/index.typ` region recorded, before any
  edit lands. One base/tip pair covers both TRN-01 and QUA-14, which is why they share a phase.
- **RED before GREEN.** Both GATE-01 fixtures are recorded failing against the **pre-handler**
  translator before the handler lands. A fixture first observed on the fixed tree does not satisfy
  constraint 3.
- **QUA-14's census before its fix.** The message census is produced from the base build's own
  output over the whole tree (constraint 6), and the fix list is derived from that census, not from
  the two docstrings the requirement names.
- **Same file, sequenced not parallel.** The handler and the docstring fix both edit
  `typsphinx/translator.py`. They are ordered by wave rather than dispatched as concurrent worktree
  plans; disjoint `files_modified` is not what makes plans safe to co-run here, because these are
  not disjoint.
- **Evidence last.** Tip measurements, the first push and the CI dispatch run in a later wave than
  the work they audit — never co-located with it.

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: TRN-01, TRN-02, QUA-14
**Success Criteria** (what must be TRUE):

  1. **A `>>>` block renders as a code block in this project's own documentation output, proven
     against a base measured in this phase.**

     *The base.* At `PHASE_BASE_SHA`, a clean `sphinx-build -b typst docs/source <tmp>` (output
     directory removed first) runs under `LC_ALL=C` and records three things: the
     `build succeeded, N warnings.` line, the count of `unknown node type: <doctest_block` lines,
     and the verbatim `api/index.typ` region carrying the `compute_content_include_path` example.
     On 2026-09-16 those read 5, 2 and the single `text("...")` run at `:811` — context, re-measured
     here, never transcribed (constraints 4, 5).

     *The proof.* On the phase tip, the same command on a clean build reports **zero**
     `unknown node type: <doctest_block` lines, with the recorded base output standing as the
     positive control that the filter can find such a line when one exists. In the tip's
     `api/index.typ`, the example sits inside the same code-block construct `literal_block` emits —
     a codly-styled fence — with its three `>>>` prompts, their continuation and their outputs on
     **separate lines**, not as one `text("...")` run.

     *The tag.* The emitted fence names a **non-empty** language, supplied by the handler itself
     rather than read from `node['language']`, which `HighlightLanguageTransform` never sets on a
     `doctest_block`. The tag chosen (` ```pycon ` or ` ```python `) and the reason are recorded in
     the phase's decision record; both compile, so this is a highlighting-quality decision
     (TRN-01; constraint 8).

  2. **Both contexts autodoc actually produces are covered by GATE-01 fixtures, each recorded RED
     first and green through a real `typst.compile()`.**

     Two fixtures, one per context: **(a)** a doctest block in plain paragraph position; **(b)** one
     in a definition-list / field-body position — the `terms.item(text("Examples:"), {...})` shape
     measured in the 2026-09-13 sphinx-autoapi run and reproduced in this project's own
     `api/index.typ`. For each:

     - it asserts on the emitted `.typ`'s **line structure** and on the **absence** of an
       `unknown node type` warning in its build;
     - its failure against the pre-handler translator is **recorded verbatim** — the transcript is
       taken at a commit that does not yet carry the handler and quoted in the phase evidence — and
       its pass is recorded afterwards;
     - its `.typ` goes through **one real `typst.compile()`**, in the
       `tests/test_pdf_render_gate.py` pattern (`sphinx-build` → `typst.compile()` → `pypdf`), not a
       string assertion alone (constraint 3).

     In context (b) the block is placed at a **non-first** position in its container, so the same
     `in_list_item` / `list_item_needs_separator` discipline `visit_literal_block` applies is
     exercised: a missing separator would juxtapose the block with the preceding code-mode
     expression and abort the compile, the way the v0.9.2 image defect did. The fixture's compile
     passing is what proves the discipline holds (TRN-02).

     *AMENDED 2026-09-20 (post-research, owner-approved):* this project's own `api/index.typ` carries
     no `terms.item(...)` doctest shape (measured count 0; the shape exists in the 2026-09-13
     sphinx-autoapi run), and a definition-list body never sets `in_list_item`. Context (b) therefore
     carries two shapes — a definition-list item (the autoapi position) and a bullet-list item (the
     `in_list_item` discipline) — both non-first, both recorded RED (74-CONTEXT.md D-06).

  3. **The docutils message class is discovered by a fresh full build and cleared everywhere it
     occurs, with the build's total not rising.**

     *Discovery.* The census comes from the base clean build's own output under `LC_ALL=C`, filtered
     for `Unexpected indentation` and `Block quote ends without a blank line`, with every hit's
     originating file and line transcribed in full. The search is **not** narrowed to
     `TypstTranslator.visit_toctree`: every occurrence the build reports, from any docstring
     anywhere under `typsphinx/`, is in scope. The 2026-09-16 base carried 3, all attributed to that
     one docstring — a starting point, not the answer (constraint 6).

     *The fix.* Each occurrence is fixed in the docstring's reST itself — indentation and blank
     lines — not suppressed by a filter, a `-W` exemption or a `# noqa`-style silencer.

     *The proof.* On the tip, the same clean build and filter return **zero** for both classes, with
     the base output as the positive control, and the `build succeeded, N warnings.` count is **not
     higher** than the base's. Both builds run in the same environment, with its interpreter
     recorded. The affected docstrings' rendered API-reference output (HTML and `.typ`) is read to
     confirm the edit changed the markup and not the documented meaning (QUA-14; constraints 4, 5).

  4. **The tree is green, the scope fence holds, and the branch is on `origin` with a green 3-OS CI
     run.**
     - **Local gates:** in the provisioned worktree venv, `ruff check .`, `black --check .`,
       `mypy typsphinx/` and the full pytest suite pass on the phase tip, and
       `tests/test_preview_version_sync.py` is green with the `@preview` count still four and no
       version changed.
     - **Scope:** `git diff --stat 6cc44f22..HEAD -- typsphinx/` lists only the handler and
       docstring changes; `.github/workflows/` and `flake.nix` are absent from the milestone diff;
       `pyproject.toml`'s version literal still reads `0.9.2` at this phase's close, because the
       bump belongs to Phase 75. Each fence carries a pathspec control and a widened-diff control.
     - **First push:** the branch census is re-measured and any decoy corrected per constraint 10,
       then `gsd/v0.9.6-doctest-block-rendering-and-release` is pushed with tracking.
     - **CI:** one run dispatched on the phase tip with
       `gh workflow run CI --ref gsd/v0.9.6-doctest-block-rendering-and-release` has **completed**.
       Every job's conclusion is transcribed, and both `windows-latest` and both `macos-latest`
       lanes are named individually and green. `main`'s required status checks are read at phase
       head and phase close and give the same set both times (constraints 7, 10, 11).

**Plans**: 7/7 plans executed (5 waves)

Plans:

**Wave 1**

- [x] 74-01-PLAN.md — base: PHASE_BASE_SHA, clean C-locale base -b typst build with positive controls, QUA-14 raw and attributed census with FIX_LIST (D-07), phase-head reads (wave 1)
- [x] 74-02-PLAN.md — GATE-01 gate and fixture, context (a) and context (b) shapes (b1)/(b2) per D-06, recorded RED on a tree without the handler (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 74-03-PLAN.md — the doctest_block handler per D-01..D-04, the unchanged gate green through real compiles, unit tests, GREEN record (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 74-04-PLAN.md — QUA-14 repairs from the census: blank lines in visit_toctree's and quote_path's docstrings, proven by a clean rebuild (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 74-05-PLAN.md — tip evidence: SC1 and SC3 against a same-venv base rebuild, the D-05 whole-tree diff classified, rendered meaning unchanged (wave 4)
- [x] 74-06-PLAN.md — local gates (lint trio, full pytest plain and LC_ALL=C, @preview), the scope fence with controls, COVERAGE.md (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 74-07-PLAN.md — branch census, first push with tracking, one CI dispatch waited on to completion, required checks at close (wave 5)

**UI hint**: no

### Phase 75: v0.9.6 Release Prep (prep-only)

**Goal**: the 0.9.6 tree is bumped, its CHANGELOG curated into a single `## [0.9.6]` section
covering the six carried `## [Unreleased]` bullets and this milestone's own, the tail link block
moved to match, the `### Known Limitations` question settled on the record either way, the extracted
release body read rather than assumed, and the whole thing handed off — with **zero irreversible
action inside the phase**. No tag, local or remote; no PyPI upload; no GitHub Release; no PR merged.
The merge, the tag push and the publish all execute at `/gsd-complete-milestone` (constraint 1).

v0.9.6 is a **patch-level release with no breaking change**: no new configuration surface, no new
runtime or dev dependency, no `@preview` change. Its user-visible content is one node family that
rendered wrong now rendering right, plus three milestones' worth of contributor-tooling change that
five of the six carried bullets themselves describe as having no effect on installing or using
typsphinx.

**Depends on**: Phase 74
**Requirements**: REL-15, REL-16
**Success Criteria** (what must be TRUE):

  1. **The version moves to 0.9.6 in one commit touching every file that carries it.**
     `git show --name-only` on the bump commit lists `pyproject.toml`, `uv.lock`, `README.md` and
     `CHANGELOG.md` together — a commit touching only `pyproject.toml` is the exact shape that once
     killed every dependabot PR. `pyproject.toml:7` is the **sole hand-edited version literal**
     (`0.9.2` → `0.9.6`); `uv.lock`'s `typsphinx` stanza reads `0.9.6` because `uv lock` regenerated
     it, not because it was edited; `README.md`'s Status line reads `v0.9.6`;
     `uv sync --extra dev --locked` exits 0 against the bumped tree; and
     `tests/test_readme_version_sync.py` is green. `tests/test_changelog_page_gate.py`'s
     `RELEASE_VERSIONS` tuple gains `"0.9.6"`, and the changelog page gate runs with **zero skipped**
     in an environment carrying the `docs` extra (REL-15; constraints 2, 11).

  2. **The CHANGELOG carries one curated `## [0.9.6]` section, and the link block at the file's end
     moves with it in this same phase.**
     - The **six** bullets standing under `## [Unreleased]` are promoted into a new `## [0.9.6]`
       section together with this milestone's own bullets, under a fresh, empty `## [Unreleased]`
       heading placed **above** it. The six are counted at the phase base, not assumed to be six.
     - The **tail link block** is updated: `[Unreleased]`'s compare base moves from `v0.9.2` to
       `v0.9.6`, and a `[0.9.6]: …/releases/tag/v0.9.6` link is added. `grep` finds no `## [0.9.3]`,
       `## [0.9.4]` or `## [0.9.5]` heading and no matching tail link anywhere in the file.
     - `scripts/extract_changelog_section.py 0.9.6` is **executed** and its stdout transcribed into
       the phase evidence: non-empty, reproducing the `## [0.9.6]` section byte-for-byte, and
       carrying no scratch `Planned for Future Releases` block (REL-15; constraint 2).

  3. **The `### Known Limitations` question is settled on the record, in one of two explicit
     shapes — never implicitly.**
     - **Either** `## [0.9.6]` carries a `### Known Limitations` section naming the carried major
       defects — NUM-01's per-master `numref` divergence, the converted-image rehome collision, and
       the `typst_documents` duplicate-target cluster — in the register v0.9.0's MILESTONES.md
       `### Known limitations shipped` entry used;
     - **or** this phase's decision record states that the owner declined it and why, following
       v0.7.1 D-27's precedent for declining one in full.
     - Whichever branch is taken, a `grep` over `CHANGELOG.md` for `Known Limitations` and the
       phase's decision record **agree with each other**, and the phase evidence names which branch
       was taken. None of the three defects is fixed here; only their disclosure is in scope.
     - REL-16 is the one release requirement this phase **does** close, so its checkbox may
       legitimately move to `[x]` at this phase's close. That is exactly why constraint 9's fence is
       line-scoped to REL-15 (REL-16).

  4. **The bumped tree is proven green by runs executed in this phase, not on the preceding phase's
     word.**
     - The full pytest suite passes twice, once under `LC_ALL=C`, since CI runs in English;
       `black --check .`, `ruff check .`, `mypy typsphinx/` and the `@preview` version-sync family
       pass.
     - `tox -e docs-html` and `tox -e docs-pdf` each pass on a **clean** build under `LC_ALL=C`,
       with `build succeeded, N warnings.` compared against a clean baseline taken at **this
       phase's own base** — and with zero `doctest_block` unknown-node lines and zero
       `Unexpected indentation` / `Block quote ends without a blank line` messages, re-proving Phase
       74's result on the bumped tree by measurement rather than inheritance.
     - `tox -e linkcheck` passes on a clean run, with its `working` count equal to the total and
       recorded fresh.
     - **One** fresh CI run is dispatched on the **bumped** tip and has completed; every job's
       conclusion is transcribed, both `windows-latest` and both `macos-latest` lanes named, and
       `ruff`'s verdict read from the `Lint and Format Check` job. If a dispatch returns an HTTP
       5xx, `gh run list` is checked before any retry — a silent second run breaks the
       exactly-one-dispatch reading.
     - A **non-committing** trial merge of `origin/main` into the branch passes `uv lock --check`
       and `ruff check .` on the merged tree, and `main`'s protection, merge method and required
       contexts are read rather than assumed (constraints 5, 10, 11).

  5. **Zero irreversible action, probed twice, REL-15 held by a recorded SHA-256, and the handoff is
     standalone.**
     - **The probes:** `git tag -l 'v0.9.6'` and a remote tag probe both come back **empty** at two
       observations separated by intervening waves rather than by wall-clock luck, each remote probe
       carrying a positive control (`v0.9.2` present). PyPI has no `0.9.6` (200 for `0.9.2` as the
       control) and no `v0.9.6` GitHub Release exists. `git diff` over the phase shows no unintended
       change under `typsphinx/`.
     - **The fence:** a `75-CLOSEOUT-GUARD.md` records `sha256sum .planning/REQUIREMENTS.md`,
       `wc -l`, the `PHASE_BASE_SHA` and the verbatim guarded lines (`grep -n 'REL-15'`) at phase
       head; the same commands re-run and MATCH at phase close **and once more after
       `phase.complete`-family tooling has run** — the observation that actually catches the flip.
       Every plan's `SUMMARY.md` declares `requirements-completed: []` for REL-15, and its checkbox
       is read directly out of `.planning/REQUIREMENTS.md` as `[ ]` at close, never inferred.
     - **The handoff:** a `75-HANDOFF.md` enumerates every step `/gsd-complete-milestone` must
       execute: the PR from the canonical milestone branch to `main` and the checks that must be
       green before merge; the `v0.9.6` tag push; the expected manual approval of the `pypi` GitHub
       Environment (a gate, not a failure); the GitHub Release body being byte-identical to
       `scripts/extract_changelog_section.py 0.9.6`'s stdout; the `typsphinx-doc-translations`
       `update-pin.yml` **manual** dispatch; the Read the Docs `en` and `ja` `stable` endpoints
       reporting `0.9.6`; and the four observations REL-15 is checked on (the merge commit on
       `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`,
       and `gh release list`). It records that `release.yml`'s `create-release` job has never run on
       a v0.9.x tag, and that a failure there is handled inside the release work rather than
       deferred (constraints 1, 9, 13).

**Cross-cutting constraints** *(truths any plan in this phase must carry)*:

- **REL-15 is cited by every plan as a coverage ID only.** No plan closes it and no plan touches its
  checkbox; per constraint 1 it stays `[ ]` and closes at `/gsd-complete-milestone`. The
  `requirements-completed: []` declaration is required in **every** plan's frontmatter, not one —
  the correction the v0.9.1 audit named.
- **REL-16 is different and must not be handled by copy-paste from prior release-prep phases.** It
  closes inside this phase, and the fence is line-scoped so it can.
- **The tail link block is this phase's work, not a follow-up.** REL-15 names it explicitly; a
  version bump that leaves `[Unreleased]` comparing against `v0.9.2` is incomplete.

**Plans**: 5/7 plans executed (4 waves)

Plans:

**Wave 1**

- [x] 75-01-PLAN.md — Closeout-guard baseline on REL-15, the clean C-locale documentation ledger at
      this phase's own base, and SC5 probe observation 1 of 2 (wave 1)
- [x] 75-02-PLAN.md — Phase 74's leftovers: delete the five untracked `probe_*.typ` scratch files,
      file IN-01 as a pending todo, write `COVERAGE.md` (wave 1)
- [x] 75-03-PLAN.md — The one commit: version `0.9.6` across `pyproject.toml` / `uv.lock` /
      `README.md` / `RELEASE_VERSIONS`, the curated `## [0.9.6]` section with its
      `### Known Limitations`, the fresh `## [Unreleased]` and the moved tail links, then the
      extractor transcript (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 75-04-PLAN.md — Green-tree evidence on the bumped tip: lint trio, pytest twice, clean
      `docs-html` / `docs-pdf` re-proving Phase 74's zero counts, clean `linkcheck` (wave 2)
- [x] 75-05-PLAN.md — Non-committing trial merge against `origin/main`, `main`'s protection and
      merge method read live, fresh branch and pull-request census (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 75-06-PLAN.md — Push the bumped tip and dispatch exactly one CI run, waited to completion with
      every job transcribed (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 75-07-PLAN.md — Fence and probe observation 2, the scope fence with controls, `75-HANDOFF.md`,
      the REL-16 settlement record and the SC1–SC5 roll-up (wave 4)

**UI hint**: no

## Progress

**Execution Order:** 74 → 75. The arrow is a real dependency, not a convention: the `## [0.9.6]`
entry must describe a fix that has actually landed and been proven by a real compile, and the
version bump must not sit in the tree while the fix is still in flight. Inside Phase 74, three
orderings are also real dependencies: the base build before any edit, RED before GREEN for both
fixtures, and QUA-14's full-build census before its fix list.

Phases 1–73 shipped or completed across v0.4.4 → v0.9.5; their per-phase plan counts, statuses and
completion dates are preserved in each milestone's archived roadmap under `milestones/`. The table
below tracks the active milestone only.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 74. The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors | v0.9.6 | 7/7 | Complete | 2026-09-20 |
| 75. v0.9.6 Release Prep (prep-only) | v0.9.6 | 5/7 | In Progress | - |

## Roadmap Evolution

Per-milestone evolution notes are archived with their milestone. v0.9.5's live in
[milestones/v0.9.5-ROADMAP.md](milestones/v0.9.5-ROADMAP.md): QUA-08's removal at owner review, the
one-work-phase-plus-close-prep shape, DOC-24's ordering behind QUA-13, and REL-14 mapped to Phase 73
for coverage only.

- **2026-09-16** — v0.9.6 roadmap created. **Phases 74–75**, 5/5 v1 requirements mapped, zero
  orphans, zero duplicates, numbering continued from v0.9.5's Phase 73. No research was run (owner
  decision 2026-09-16 — the technical facts were measured during scoping and are embedded in
  `REQUIREMENTS.md`). Five decisions are built into the structure and should not be re-derived
  during planning:

  - **TRN-01, TRN-02 and QUA-14 share Phase 74 because they share a measurement.** The clean
    `-b typst` build of `docs/source` is the acceptance instrument for all three: TRN-01 drives one
    message class to zero, QUA-14 drives the other to zero, and both are bound by the same
    `build succeeded, N warnings.` total not rising. Splitting them would split one base/tip pair
    across two phases and manufacture a single-requirement phase. Two phases at
    `granularity: standard` (nominally 4–6) is below the range, for the same reason v0.9.4 and
    v0.9.5 recorded.

  - **TRN-02 is not a verification phase for TRN-01.** It is the *shape* requirement — which two
    contexts the handler must be correct in, and the recorded-RED real-compile fixture per context.
    Making it its own phase would manufacture a phase that is pure verification of another phase's
    work, which v0.9.3's roadmap already rejected for the NIX cluster.

  - **REL-15 and REL-16 both map to Phase 75, and they close differently.** REL-15 is coverage-only
    inside the phase and is checked at `/gsd-complete-milestone` on observed publish evidence;
    REL-16 closes inside the phase, because "settled on the record" is a phase artifact. This is the
    first release-prep phase here where the `REQUIREMENTS.md` fence cannot be whole-file, and
    constraint 9 says so explicitly.

  - **QUA-14's discovery is scoped by measurement, not by the requirement's own wording.** The
    success criterion is written so that a census limited to `TypstTranslator.visit_toctree` fails
    it. This is a deliberate correction of a failure mode this project has hit before.

  - **The 3-OS CI run and the first push carry no REQ-ID**, matching v0.9.1–v0.9.5. They are held by
    Phase 74 SC#4 (the first push) and Phase 75 SC#4 (the bumped tip), each dispatched fresh on its
    own phase's tip.

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

**Todos this milestone is scoped to close:**

- `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line` (TRN-01, `severity: major`) —
  captured 2026-09-13 during the Issue #91 re-measurement and acknowledged at the v0.9.4 close. It
  maps to **Phase 74** (TRN-01, TRN-02) and moves to `todos/completed/` when that phase closes. Its
  own record counted **17** `doctest_block` warnings in a `sphinx-autoapi` build of this package,
  against the 2 this project's own docs build carries; both are exposure figures for one handler.

**Still open after v0.9.5, not scoped here:**

- `2026-07-22-add-sphinx-linkcheck-ci-job` — **half closed; it stays in `pending/`.** Phase 72
  landed the `tox -e linkcheck` environment (QUA-13) and listed it on all three surfaces (DOC-24).
  The CI job the todo is actually about (QUA-08, superseding LNK-01) is Future. Its obstacle — a new
  workflow file cannot be scheduled or `workflow_dispatch`-ed from an unmerged milestone branch — is
  unchanged, but the environment it would call is now on `main`, so **a side PR to `main` is the
  route** whenever it is picked up. Its "Solution" section proposed `linkcheck_ignore` up front;
  only a measured failure earns one, and none has been measured (95/95 `working`).

- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures` (NUM-01,
  `severity: major`) — still excluded from every published surface by owner override D-07. **This
  milestone does not fix it, but REL-16 forces the decision on whether to *disclose* it** in the
  `## [0.9.6]` notes.

- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs` (MSG-06,
  `severity: minor`) — `translator.py`'s two relative-path DEBUG logs carry the same
  hardcoded-`'...'` delimiter shape Phase 60 closed in three other modules; the one-line fix is
  `quote_path()`, which now exists. Phase 74 edits `translator.py` and must **not** absorb it
  (constraint 7).

**Dormant seeds:**
- **`SEED-001-readme-quickstart-typst-documents-pdf`** — substantially discharged by v0.7.1's
  CONF-08 + DOC-11 and v0.8.0's DOC-14.
- **`SEED-003-tox-dependency-groups-per-env`** (Future QUA-07) — splitting the `dev` extra into PEP
  735 `[dependency-groups]`. A phase touching `pyproject.toml` or `tox.ini` must not absorb it
  opportunistically; Phase 75 edits `pyproject.toml`'s version literal and must not.
- **`SEED-004-typst-py-maintenance-risk-vendored-compile-path`** — `typst-py` upstream maintenance
  is slowing, and typsphinx may eventually need to carry an equivalent compile path. It is still the
  single largest structural risk on the horizon, and it has never been scoped into any milestone
  across ten consecutive scopings.
- **`SEED-005-gsd-workstreams-for-parallel-roadmap-tracks`** — adopt GSD workstreams so independent
  roadmap tracks run in parallel; dormant since v0.9.3.

**Known limitations still shipped with no published surface** after v0.9.2, carried unchanged
through v0.9.3, v0.9.4 and v0.9.5, none of which changes product behaviour: WR-02's `confdir` gap,
the tripled "Custom template not found" warning, and NUM-01's `numref` per-master divergence. **The
`### Known Limitations` decision is no longer open: this milestone publishes, so REL-16 forces it
either way in Phase 75.**

**Standing risk carried from v0.9.3:** `flake.nix` is load-bearing while keeping **zero CI
coverage** — no workflow references `nix` or `flake`, so a breaking edit is caught only when the
maintainer next enters the shell, and the darwin branch of the per-system guard cannot be exercised
from a Linux machine at all. Accepted deliberately (owner decision 2026-09-02); documented on the
surface itself by v0.9.3's DOC-21. This milestone adds no workflow and does not touch `flake.nix`.

**Standing risk specific to this milestone:** `release.yml`'s `create-release` job has never run on
a v0.9.x tag. Its last end-to-end evidence is the v0.7.1 publish (run `31462027486`) and v0.8.0 (run
`31861043480`). A failure at the real `v0.9.6` tag push is handled inside the release work rather
than deferred (constraint 13).

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15), v0.9.0 (2026-08-22), v0.9.1 (2026-08-30 — completed, not published), v0.9.2 (2026-08-31), v0.9.3 (2026-09-13 — merged, not published), v0.9.4 (2026-09-13 — merged, not published), v0.9.5 (2026-09-16 — merged, not published). Per-milestone phase detail, success criteria, and decisions for completed milestones live in `milestones/vX.Y-ROADMAP.md`. Active milestone: **v0.9.6 — Doctest block rendering and release**, Phases 74–75, created 2026-09-16.*
