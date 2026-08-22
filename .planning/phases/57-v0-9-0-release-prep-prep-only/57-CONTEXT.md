# Phase 57: v0.9.0 Release Prep (prep-only) - Context

**Gathered:** 2026-08-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Prep-only release work for v0.9.0: bump the version in lockstep, curate the `## [0.9.0]` CHANGELOG
entry around four breaking changes, write the `Migrating from 0.8.x to 0.9.0` guide, prove the
post-bump tree green on live runs, assert the standing invariants over the milestone diff, and hand
off a standalone publish checklist — with **zero irreversible action taken**. Requirement:
**REL-08**, prep half only. REL-08 does **not** close here; it closes at
`/gsd-complete-milestone`, and stays `[ ]` through every plan of this phase.

**In scope:**

- `pyproject.toml:7` — `version = "0.8.0"` → `"0.9.0"` (measured this session: still the sole
  version literal), with `uv.lock` and `README.md:347` (`**Status**: Stable (v0.8.0) - Production
  ready`) moved in lockstep and the editable-install metadata regenerated so
  `typsphinx.__version__` reports `0.9.0`. Every version-sync guard test stays green.
- A curated `## [0.9.0]` entry in `CHANGELOG.md` per D-01…D-05, **plus the tail link-block
  rollover** — add the `[0.9.0]` release-tag line and advance `[Unreleased]` to `v0.9.0...HEAD`.
  Unlike Phase 52, the `## [Unreleased]` block **already carries seven real v0.9.0 bullets**; D-02
  promotes them and authors the three missing ones.
- A new `Migrating from 0.8.x to 0.9.0` subsection in `docs/source/changelog.rst`, in the same
  before/after shape as the existing `Migrating from 0.7.x to 0.8.0` (D-06…D-08).
- SC#3 live-run evidence on the post-bump tree: full pytest, `black` / `ruff` / `mypy`, both docs
  tox environments, the multi-template `-b typstpdf` build, and Phase 54's built-wheel content
  check — all re-run **after** the bump, with verbatim evidence recorded (D-12…D-14).
- SC#4's fence proof: the tag/publish probe recorded twice at separated times, a `git diff` showing
  no unintended `typsphinx/` change, and the `REQUIREMENTS.md` checksum guard against the
  `phase.complete` auto-flip. Separately, the SHA-anchored milestone diff that backs D-05's
  `### Verified` claims and milestone invariant #11 (D-15).
- SC#5 handoff: a standalone `57-HANDOFF.md` following the `52-HANDOFF.md` / `46-HANDOFF.md`
  precedent, and the explicit statement that REL-08 remains open until the publish.
- The two documentation findings `56-REVIEW.md` raised (D-10): the 404 link in
  `examples/advanced/README.md:270` and the stale `Python 3.9+` / `Sphinx 5.0+` prerequisites in
  `examples/basic/README.md:7-8`, `examples/advanced/README.md:31-33` **and**
  `docs/source/installation.rst:7-8`.

  **AMENDED 2026-08-16 (post-research, owner-approved) — this is now VERIFICATION work, not a fix.**
  The edit already landed on the live tree as commit `70e24958` ("docs: fix stale version
  prerequisites and dead configuration link", 2026-08-16 22:10:05 +0900), which **predates
  `57-CONTEXT.md`'s own commit** `4dd49979` (22:59:30) by 49 minutes — so the discussion that wrote
  this bullet was already describing finished work. See the AMENDED block on D-10.

- Close-out disposition of the pending todo ledger, including **re-filing** the 56-REVIEW records
  that `STATE.md` claims were filed forward but which do not exist on disk (see `<specifics>` 9).

  **AMENDED 2026-08-16 (post-research, owner-approved) — the re-filing is MOOT; the record exists.**
  `.planning/todos/completed/2026-08-16-stale-version-prerequisites-and-dead-config-link-in-published-docs.md`
  is on disk (created `2026-08-16T12:45:09Z`, committed in `70e24958`). The discuss-session's
  `grep -rl` missed it because the slug appears **only in the filename**, never in the file's body —
  a content grep cannot see it. Ledger disposition stays in scope; *re-filing this record* does not.
  Separately, and per owner decision this session, the pending todo
  `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` is **annotated with evidence and kept in
  `pending/`** — not closed — because it no longer reproduces but no repair commit explains why (see
  the AMENDED block on D-13).

**Out of scope:**

- **Any publish or otherwise irreversible action** — `git tag v0.9.0`, triggering `release.yml`,
  PyPI, the GitHub Release, opening or merging the PR, and the second tag on
  `typsphinx-doc-translations`. `git tag -l v0.9.0` and `git ls-remote --tags origin v0.9.0` must
  both be empty at phase close (measured this session: both already empty). The prep/publish fence
  is absolute — Phase 33 / 35 / 41 / 46 / 52 precedent.
- **Any `typsphinx/` behaviour change**, including `54.1-REVIEW.md` WR-01 (the tripled
  "Custom template not found" warning) and WR-02 (the `confdir`≠`srcdir` carve-out). D-09 and D-10
  hold the prep-only fence even though both are real.
- Revisiting the version number — `0.9.0` is fixed by the milestone name, ROADMAP SC#1,
  `PROJECT.md`'s milestone header, **and** already published in
  `docs/source/user_guide/configuration.rst:625` ("Removed in — v0.9.0").
- **Merging `origin/main`** — measured this session: `origin/main` (`aed773c9`) is already an
  ancestor of HEAD and *is* `git merge-base origin/main HEAD`. A re-check at the head of the phase
  is cheap and should still be made.
- Editing historical CHANGELOG entries or historical migration guides (56-CONTEXT's DOC-17
  recommendation on history is carried forward unchanged).
- Adding a prerequisites-version sync gate (D-11 declined it).

</domain>

<decisions>
## Implementation Decisions

Every measured value below was taken **this session (2026-08-16)** against the live tree, not from
recall.

### The `## [0.9.0]` CHANGELOG entry

- **D-01: Four bullets carry `**Breaking:**`, not two.** ROADMAP SC#2 names two changes (the
  `_template.typ` → `_template/<key>/<file>` relocation and the `typst_template_assets` removal);
  measured this session, **neither is written anywhere in `CHANGELOG.md` yet**, while
  `## [Unreleased]` already carries two *different* `**Breaking:**` bullets — the
  `<srcdir>/base.typ` → `<srcdir>/_typst/base.typ` shadow-route relocation (OUT-04) and the
  pre-write template-layout validation (WR-01/CR-01). SC#2's "exactly the two" is read as a
  **floor on the two that are currently missing** (both must be marked, each with its migration
  sentence), not as a cap on the entry. Rejected: folding all four into two axes to match the goal
  sentence's "two independent axes" literally (buries "what stops your build" inside a long
  bullet), and demoting the two existing marks to ordinary `### Changed` bullets (a shadow template
  that stops applying **with no build-time warning**, and a configuration that used to build and
  now hard-fails, would both ship unmarked). — **Reversibility:** reversible.

- **D-02: The seven existing `## [Unreleased]` bullets are promoted substantially as written, and the three missing ones are authored at the same granularity.** Measured: `### Changed` holds 2
  bullets (12 and 18 lines), `### Fixed` holds 5 (XREF-05, BLD-07, BLD-08, BLD-09, IMG-03). They
  are longer than `## [0.8.0]`'s longest bullet (10 lines) — accepted deliberately, because each
  was written immediately after the phase that measured it, and compressing loses facts that only
  exist there (e.g. OUT-04's "there is **no** build-time warning for this relocation, so this
  changelog entry is the only place it is announced"). Rejected: compressing to the 0.8.0 house
  length (the GitHub Release body is this section verbatim via
  `scripts/extract_changelog_section.py`, so a reader who does not follow a link loses the
  information), and re-authoring from the milestone's requirements as Phase 52 did (Phase 52 had no
  choice — its `## [Unreleased]` was empty; here it would discard measured prose). The final entry
  is roughly `### Changed` 5 + `### Fixed` 5 + `### Removed` 1. — **Reversibility:** reversible.

- **D-03: The `typst_template_assets` removal is a `### Removed` bullet, not a fifth `### Changed` one.** Follows `## [0.7.1]`'s `typst_authors` precedent (`CHANGELOG.md:66-72`) and Keep a
  Changelog's standard section; `## [0.8.0]` omitted `### Removed` only because it had no
  candidate. The bullet keeps its `**Breaking:**` prefix, states the reason in one sentence (the
  whole bundle is now copied wholesale, so no asset list is needed) and cross-references the
  output-relocation bullet in `### Changed`. It should also state that **a warning shim exists**
  (`config-inited` detection, `typsphinx/removed_config.py:92`) — a deliberate contrast with
  0.7.1's "there is no deprecation shim". Rejected: putting it in `### Changed` beside the other
  three Breaking bullets (a future reader seeing an absent `### Removed` concludes nothing was
  removed), and writing it in both places. — **Reversibility:** reversible.

- **D-04 [derived, fixed by ROADMAP SC#2 — not re-asked]: the lead paragraph names the registry as the headline.** SC#2 says so literally ("names the registry as the headline"), and
  `PROJECT.md` § "Current Milestone: v0.9.0 per-document templates" supplies the sentence: every
  `typst_documents` entry can use its own template, package, and template-function arguments. The
  breaking-change declaration lives in the second half of the same paragraph, following
  `52-CONTEXT.md` D-04/D-05's two-way marking (lead declaration plus per-bullet prefix). The entry
  must also say what is **not** breaking: the registry itself is additive, so no existing `conf.py`
  needs editing (ROADMAP Phase 57 preamble).

- **D-05: `### Verified` carries the same three items as 0.7.0, 0.7.1 and 0.8.0, unchanged.**
  Measured this session that all three still hold: `git diff v0.8.0..HEAD -- pyproject.toml`
  touches **no dependency line** (the only change is `[tool.setuptools.package-data]`,
  `templates/*.typ` → `templates/**/*`); `typsphinx/templates/base.typ` still carries exactly
  **4** `@preview` lines; the full-corpus gate still exists. The new built-wheel content check
  (`.github/workflows/ci.yml:151-169`) is recorded in the phase's evidence artifacts, **not**
  promoted to a fourth item — this section's standing character is "here is what did *not*
  change", and its value comes partly from being comparable across releases. — **Reversibility:**
  reversible.

### The 0.8.x → 0.9.0 migration guide

- **D-06: Phase 57 writes `Migrating from 0.8.x to 0.9.0` in `docs/source/changelog.rst`.**
  Measured: that file contains **zero** occurrences of `0.9.0`, while both `## [0.8.0]` and
  `## [0.7.1]` lead paragraphs point the reader at exactly such a guide. Phase 51 wrote 0.8.0's
  (83 lines, a before/after `code-block:: text` pair per breaking change); Phase 56 wrote no
  equivalent, so the pointer D-02's promoted text will carry has no destination unless this phase
  supplies one. Writing documentation prose is not an irreversible action, so the prep-only fence
  is untouched. — **Reversibility:** reversible.

- **D-07: The new migration guide is NOT bound by a test gate.** This carries forward
  `56-CONTEXT.md`'s DOC-17 line — historical release notes and migration guides record what was
  true at the version they document, so they are not held to agreement with current code the way a
  user-guide page is. Measured: `grep -rn "Migrating" tests/*.py` returns **zero** hits, so the
  0.7.x→0.8.0 guide is unbound today and this decision changes nothing. The counter-case that was
  put and declined: Phase 56's uniform rule was "every published claim is machine-checked", and its
  verification hardened three gates with live falsification tests. Owner decision with that on the
  table. — **Reversibility:** reversible — adding a gate later costs nothing structural.

- **D-08: The guide's "before" side is measured by a real build at the `v0.8.0` tag, not derived from records.** With no gate (D-07), the only accuracy guarantee is that the content was
  measured when written. `v0.8.0` is `d9523ea` and an ancestor of HEAD, so a `git worktree add` at
  that tag plus one `-b typst` build of the same fixture yields the actual pre-change file tree.
  The transcript is recorded in a phase evidence artifact. Rejected: deriving "before" from Phase
  54's RED evidence and the 32 rewritten test assertions — those are assertion-level records, so
  what belongs in a before-block file tree would be inference. — **Reversibility:** reversible.

### Disclosure of defects shipping unfixed

- **D-09: `54.1-REVIEW.md` WR-02 ships silent — the CHANGELOG's unconditional wording is kept as-is.** WR-02 measured that `_validate_used_template_paths()` resolves `templates_path` against
  `self.srcdir` (`typsphinx/builder.py:1107-1114`), not the `confdir` Sphinx documents, so a
  project using `-c`/`--confdir` still walks into the republication hole that
  `_copy_used_template_bundles()` has no awareness of either. This is the `52-CONTEXT.md` D-01
  shape applied a third time: the record stays in the phase artifacts and is named in
  `57-HANDOFF.md`; **no `### Known Limitations` section is added and no GitHub issue is filed.**
  The counter-cases that were put and declined: (a) the reviewer's own recommended *minimum*
  remediation was "mention the `-c`/confdir carve-out in the CHANGELOG's new breaking-change
  entry", which is literally this phase's work, and (b) unlike the v0.8.0 four, silence here means
  shipping an over-broad sentence ("template layout is now validated before anything is written")
  rather than merely omitting a caveat. Owner decision with both on the table. — **Reversibility:**
  reversible — scoping the sentence or adding a limitations section later costs nothing structural.

- **D-10: The two `56-REVIEW.md` documentation findings are fixed in this phase; `54.1-REVIEW.md` WR-01 is not.** The split is the prep-only fence: the 56 findings touch documentation only, and
  the phase is already editing documentation for D-06. WR-01 (the "Custom template not found"
  warning firing three times instead of two, `typsphinx/builder.py:1181`) would require a
  `typsphinx/` behaviour change and stays a todo. The deciding measurement for fixing the 56 pair:
  the stale prerequisites live not only in `examples/**/README.md` but in
  `docs/source/installation.rst:7-8`, a published user page that would announce `Python 3.9 or
  higher` / `Sphinx 5.0 or higher` at the same moment v0.9.0 ships with
  `requires-python = ">=3.12"` and `sphinx>=9.1,<10`. — **Reversibility:** reversible.

  **AMENDED 2026-08-16 (post-research, owner-approved). The fix half of D-10 is ALREADY DONE; what
  remains is proof.** Surfaced by `57-RESEARCH.md` and independently re-measured by the plan-phase
  orchestrator against the live tree:
  - Commit `70e24958` (2026-08-16 22:10:05 +0900) corrected **five** files — `docs/source/installation.rst`,
    `docs/source/contributing.rst`, `docs/source/examples/advanced.rst`, `examples/basic/README.md`,
    `examples/advanced/README.md` — replacing `Python 3.9 or higher/later` → `Python 3.12` and
    `Sphinx 5.0 or higher/later` → `Sphinx 9.1 or higher (below 10)`, and rewriting the dead link
    `../../docs/configuration.rst` → `../../docs/source/user_guide/configuration.rst`.
    Note it reached **two surfaces beyond this bullet's enumerated floor** (`contributing.rst`,
    `examples/advanced.rst`) — the standing "discovery is run-time, file lists are floors" rule
    (invariants #4/#11) proving itself again.
  - A repo-wide grep at this session's discovery time over `*.md`/`*.rst`/`*.txt`, excluding
    `.planning/` and the historical `CHANGELOG.md`, returns **zero** remaining stale-prerequisite
    hits and **zero** dead `docs/configuration.rst`-class links.

  **D-10 therefore converts from a fix task to a verification task.** The plan must still cover
  D-10 — by re-running the repo-wide discovery grep at execution time (not by trusting this
  amendment's hit set, which is itself only a floor), asserting zero hits against the truth source
  `pyproject.toml:10` `requires-python = ">=3.12"` / `:28` `sphinx>=9.1,<10`, and recording
  `70e24958` as the closing evidence. If the execution-time grep finds a hit this amendment missed,
  fixing it is in scope — the prose-only, no-gate character of D-11 is unchanged.

- **D-11: The prerequisites correction is a prose fix only — no version-sync gate is added.**
  Rejected: a `tests/test_readme_version_sync.py`-shaped module reading `requires-python` and the
  `sphinx` pin from `pyproject.toml` and sweeping the published pages by run-time discovery. The
  drift is real and repeatable (it survived from the 0.7.x era across three files), so the risk of
  recurrence is accepted knowingly rather than overlooked. Discovery of the sites to fix is still a
  repo-wide grep at discovery time, never the three files named above (milestone invariants
  #4/#11). — **Reversibility:** reversible.

### SC#3 — where "green" comes from

- **D-12: CI is dispatched twice — once before the bump, once after.** Measured: the last full CI
  run on this branch is `31884774067` (2026-08-15, `workflow_dispatch`), so **Phases 54, 54.1, 55
  and 56 have never been through the Windows or macOS lanes** — the lanes that caught a real
  cp1252 defect at the v0.7.0 close and a real path-separator defect at the v0.7.1 close. The
  branch is **188 commits ahead** of `origin/gsd/v0.9.0-per-document-templates`, and `ci.yml`'s
  push trigger is `[main, develop]` only, so `workflow_dispatch` is the only route that does not
  require opening a PR. The pre-bump run separates "this milestone's code fails on another
  platform" from "the bump broke something"; the post-bump run is SC#3's authority. This is the
  `46-CONTEXT.md` D-23 shape; Phase 52 used a single run only because it had no separate repair to
  check first. Pushing a branch and dispatching a workflow are not irreversible actions; opening a
  PR is, and stays out. — **Reversibility:** reversible.

- **D-13 [derived, following 52-CONTEXT D-08]: the dispatched CI runs are the authority for pytest / lint / type; the gates and both docs builds are run locally.** `ruff` still cannot
  execute on this machine
  (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`), which is
  why lint authority sits with CI. **Hard sequencing constraint measured this session:** every CI
  job begins with `uv sync --extra dev --locked`, and `--locked` appears in **eleven** steps across
  four workflows — so `uv.lock` must be regenerated and committed **before** either dispatch, or no
  test, lint or type check runs at all. Two live dependabot PRs (#128, #123) are dying in exactly
  that way right now (`.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md`).

  **AMENDED 2026-08-16 (post-research, owner-approved). Two of D-13's stated premises are false; its
  conclusion survives on independent grounds.** Both re-measured by the plan-phase orchestrator:
  - **`ruff` DOES run on this machine.** `uv run ruff check .` → `All checks passed!`, exit 0,
    `ruff 0.15.20`; `.venv/bin/ruff` is a working 27.9 MB ELF. The pending todo
    `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` no longer reproduces. Per owner
    decision this session it is **annotated with this evidence and kept in `pending/`**, not closed —
    the defect was environment-dependent and no commit explains the repair, so closing it would
    erase the record if it recurs.
  - **The `--locked` census is 10 steps, not eleven** — `ci.yml` 6 (`:37,67,88,109,174,202`),
    `release.yml` 2 (`:36,113`), `docs.yml` 1 (`:29`), `drift.yml` 1 (`:32`). **The hard sequencing
    constraint is completely unaffected:** `uv.lock` must still be regenerated and committed before
    either CI dispatch, or the install step fails before any test, lint or type signal exists.

  **What does not change:** CI remains SC#3's lint/type/test authority. That rests on D-12's
  independent grounds — the Windows and macOS lanes, which no local run reproduces at all and which
  caught a real cp1252 defect at the v0.7.0 close and a real path-separator defect at the v0.7.1
  close. **What may improve:** `ruff` can now also be run locally as part of the pre-dispatch gate
  set, so a lint break is caught before burning a CI dispatch rather than after. That is additive —
  it does not move authority off CI.

- **D-14 [derived]: SC#3's multi-template PDF claim is discharged by re-running the existing permanent gate, not by building a new one.** Unlike Phase 52 — which had to author a new gate for
  its goal claim — `tests/test_two_key_selection_gate.py` already runs `-b typstpdf` over
  `tests/fixtures/two_key_selection_gate/` (three `typst_documents` entries across two registry
  keys) and carries `test_the_two_templates_produce_different_pdfs`, with the two bundled templates
  deliberately differing in page size (`a4` vs `us-letter`) and text size (`11pt` vs `14pt`). SC#3
  asks for "two differently-typeset PDFs"; that is what this gate proves. The phase re-runs it
  post-bump and records the verbatim transcript. The planner owns whether any additional
  standalone project transcript is worth the cost on top.

- **D-15 [derived, following 52-CONTEXT D-09]: the milestone-diff sweep behind `### Verified` is anchored at the `v0.8.0` tag (`d9523ea`).** Note that **Phase 57's SC#4 is a fence criterion, not
  an invariant-sweep criterion** — unlike Phase 52's. The sweep is still needed, because D-05's
  three `### Verified` claims and milestone invariant #11 both assert facts about the whole
  milestone diff. Measured this session: `v0.8.0` is an ancestor of HEAD; `origin/main`
  (`aed773c9`) is also an ancestor and *is* the merge-base; and excluding `.planning/`, both
  `v0.8.0..HEAD` and `aed773c9..HEAD` give the **identical** shortstat (163 files changed,
  +11,262 / −1,615), because the four commits between them are planning/docs only. 270 commits in
  the range. **Note the difference from Phase 52:** `pyproject.toml` is *not* unchanged this time,
  so "no new runtime dependency" is no longer a one-command empty-diff proof — the sweep must show
  that the one `pyproject.toml` hunk is `[tool.setuptools.package-data]` and touches no dependency
  line. If the sweep records a positive control, it must be a real one — an assertion that *would*
  fail if the sweep were vacuous, not a restatement.

### Claude's Discretion

- The exact wording of the `## [0.9.0]` entry and the lead paragraph, which bullets D-02's promoted
  seven resolve to after editing, the section assignment of the new three (`### Added` for the
  registry is the obvious candidate but is not fixed by decision), and how requirement IDs are attached
  (trailing parentheses is the settled house style since Phase 33 D-09).
- The heading structure of the new migration guide, how many `code-block:: text` pairs it carries,
  and the order the four breaking changes are presented in.
- Plan decomposition and ordering, and the `uv.lock` regeneration procedure (acceptance:
  `uv sync --extra dev --locked` green) — subject to D-13's sequencing constraint.
- The mechanical method for D-15's milestone-diff sweep, and how the "no new runtime dependency"
  claim is argued now that `pyproject.toml` is not an empty diff.
- Whether `"0.9.0"` is added to `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py:50-64` in
  this phase — the gate asserts each listed release appears in the built page, so the addition is
  mechanical but must not land before the CHANGELOG entry exists. The 46 and 52 precedents both
  left this to the planner for the same reason.
- The format and heading structure of `57-HANDOFF.md`, and where live-run evidence is recorded —
  subject to the reserved-name constraint: **do not name any evidence file `57-VERIFICATION.md`**
  (46-CONTEXT D-15; the verifier owns that name and will clobber it). The `52-*-EVIDENCE.md` family
  (`52-BUMP-EVIDENCE.md`, `52-CI-EVIDENCE.md`, `52-GREEN-TREE-EVIDENCE.md`,
  `52-GOAL-CLAIM-EVIDENCE.md`, `52-RELEASE-EVIDENCE.md`, `52-SC4-INVARIANTS.md`) is the naming
  precedent.
- How many todo records the re-filing in `<specifics>` 9 produces (one combined or two separate),
  and the granularity of the `REQUIREMENTS.md` checksum SC#4 asks for.

**AMENDED 2026-08-17 (post-CI, owner-approved) — Phase 57's prep-only fence is knowingly broken by
plan 57-11, and SC#4 must be evaluated against this amendment, not against the original "zero
`typsphinx/` behaviour change" wording above.**

Phase 57 was scoped prep-only: the `<domain>` section's "Out of scope" list above states "Any
`typsphinx/` behaviour change" without exception, and SC#4 (`.planning/ROADMAP.md` § Phase 57) asks
for "no unintended `typsphinx/` change" as part of its fence proof. That fence held through plans
57-01 through 57-09.

Two full CI matrix dispatches proved otherwise. Run `31956166848` and run `31959060298` (headSha
`bfcc6f6d`, dispatched by 57-05) both failed the same assertion on **both** `windows-latest` lanes —
a real defect in **this milestone's own new error surface**: `typsphinx/builder.py`'s pre-write
template-path refusal messages interpolate a filesystem-path value with `!r`, and `repr()` doubles
every backslash, so a Windows user reads a message with two literal backslashes where one path
separator belongs. The defect is not cosmetic — it is new in this milestone (the `typst_document_templates`
registry and its refusal messages are v0.9.0 work) and it is user-visible on the platform CI actually
exercises.

The owner was told explicitly, before deciding, that fixing the product (rather than normalizing the
already-merged test assertion to tolerate the escaped form) breaks this phase's own prep-only fence.
The owner chose the product fix anyway (2026-08-17), accepting that cost. Plan 57-11 is the one and
only exception this AMENDED block records: it is the FIRST and ONLY intended change under
`typsphinx/` in this phase, confined by its own task 2 to three named refusal sites in
`typsphinx/builder.py`, with the full local suite passing with **zero test file edits** (proving the
POSIX-rendered output is byte-identical before and after) — see
`57-MESSAGE-FIX-EVIDENCE.md` for the census, the reproduction, and the RED/GREEN transcripts.

**What this means for SC#4 and for `57-08`:** SC#4's "no unintended `typsphinx/` change" clause must
be read, from this point forward, as **"no UNINTENDED `typsphinx/` change — the `builder.py` message
fix landed by 57-11 being the one intended and owner-approved exception."** A downstream fence check
that instead diffs against the ORIGINAL "zero `typsphinx/` change" wording above will report a false
violation. The two readers this block is written for, by name, are:

- **`57-08`** (this phase's SC#4 sweep/verification plan) — its `typsphinx/`-diff check must allow
  exactly the 57-11 commit(s) touching `typsphinx/builder.py` (and the paired
  `tests/test_templates_path_collision_gate.py` addition) and flag anything else under `typsphinx/`
  as before.
- **The phase verifier** — when it re-derives the fence proof for this phase's close, it must read
  this AMENDED block rather than the original "Out of scope" bullet in isolation, or it will
  independently reach the same false-violation conclusion 57-08 is warned against above.

This amendment does not retroactively bless any OTHER `typsphinx/` change in this phase — the fence
stays absolute for everything except the specific, bounded 57-11 fix described above and in
`57-MESSAGE-FIX-EVIDENCE.md`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's requirements and success criteria

- `.planning/ROADMAP.md` § "Phase 57: v0.9.0 Release Prep (prep-only)" (lines 927-975) — the five
  success criteria. SC#2's "exactly the two changes above" is the clause D-01 reinterprets, with
  its reasoning recorded; SC#4's `REQUIREMENTS.md` checksum requirement is the one most likely to
  be skipped.
- `.planning/REQUIREMENTS.md` lines 126-136 — REL-08 verbatim, including the explicit instruction
  that it stays `[ ]` through every plan of Phase 57.
- `.planning/ROADMAP.md` lines 392-472 — the eleven binding milestone constraints. Binding here:
  **#9** (the milestone branch stays pushed to `origin` — measured 188 commits behind right now),
  **#10** (the final phase is prep-only and the `phase.complete` auto-flip must be caught),
  **#11** (repo-wide grep at discovery time; `@preview` count stays four; typing-import
  modernization forbidden; full pytest + black + ruff + mypy green at the phase boundary).
- `.planning/PROJECT.md` § "Current Milestone: v0.9.0 per-document templates" (lines 25-55) — the
  milestone goal sentence D-04 makes the lead paragraph's headline, and the "one output rule, no
  exceptions" framing.
- `.planning/STATE.md` — the Phase 56 close record, the two `54.1-REVIEW.md` findings shipping
  tracked-not-fixed (D-09, D-10), and the measured green baseline (1366 passed / 5 skipped /
  0 failed; black, ruff, mypy clean; docs-html and docs-pdf green).

### The release-prep precedent to follow

- `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-CONTEXT.md` — the closest
  precedent. D-01 (silent internal deferral, D-09 here), D-04/D-05 (two-way breaking marking),
  D-06 (`### Verified`'s three items, D-05 here), D-08 (CI as authority, D-13 here), D-09 (diff
  anchor, D-15 here), and the reserved-filename constraint.
- `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-HANDOFF.md` — the handoff
  document shape SC#5 asks for, and the publish checklist to adapt.
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-CONTEXT.md` — D-15's
  reserved-filename constraint, D-16's todo disposition shape, and **D-23's two-run CI split**,
  which D-12 revives.
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-HANDOFF.md` — the
  seven-item publish checklist this phase's handoff descends from.

### CHANGELOG and migration-guide source material

- `CHANGELOG.md` lines 8-80 — the `## [Unreleased]` block D-02 promotes: two `**Breaking:**`
  bullets under `### Changed` (OUT-04; WR-01/CR-01) and five under `### Fixed` (XREF-05, BLD-07,
  BLD-08, BLD-09, IMG-03), plus the "Planned for Future Releases" list that stays with
  `## [Unreleased]`.
- `CHANGELOG.md` lines 82-154 — `## [0.8.0]`, the structural model (lead paragraph → `### Added` /
  `### Changed` / `### Fixed` → `### Verified`).
- `CHANGELOG.md` lines 66-72 — `## [0.7.1]`'s `### Removed` entry for `typst_authors`, the model
  D-03 follows, including its "there is no deprecation shim" clause that D-03 deliberately inverts.
- `CHANGELOG.md` tail — the link-reference block, currently ending at `[0.7.1]` with `[Unreleased]`
  comparing `v0.8.0...HEAD`. **Both lines move in this phase** (ROADMAP SC#2 says so explicitly).
  Note the block has no `[0.8.0]` line — check whether that is an omission to repair alongside.

  **AMENDED 2026-08-16 (post-research, owner-approved). There is nothing to repair — `[0.8.0]`
  exists.** Measured directly: `CHANGELOG.md:1157` is
  `[0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0`, and it is the **topmost**
  release line in the block (descending order `[0.8.0]` → `[0.1.0b1]`, with `[Unreleased]` last at
  `:1177` comparing `v0.8.0...HEAD`). Phase 52 added it. The block's true state is *complete*, so
  this phase's tail-block work is the routine two-line edit ROADMAP SC#2 asks for and nothing more:
  insert `[0.9.0]: …/releases/tag/v0.9.0` **above** `:1157`, and advance `[Unreleased]` to
  `compare/v0.9.0...HEAD`. Do not plan a "repair the missing 0.8.0 line" task — there is no defect.
- `docs/source/changelog.rst` lines 1-89 — the `.. include::` of the repo-root file, the
  "Migration Guides" heading, and `Migrating from 0.7.x to 0.8.0` (83 lines) as the shape D-06
  copies.
- `docs/source/user_guide/configuration.rst` lines 603-640 — the "Removed Configuration Values"
  table Phase 56 published, which already states `typst_template_assets` / **Removed in v0.9.0** /
  "Delete the setting". The `### Removed` bullet must agree with it.
- `typsphinx/removed_config.py:36-57` — `REMOVED_CONFIG_VALUES`, the single source of the three
  warning strings; `:92` is the bare `logger.warning(message)` call (no `type`/`subtype`, so it is
  not individually suppressible — do not claim a `suppress_warnings` route).

### The findings that ship unfixed

- `.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-REVIEW.md`
  § WR-01 and § WR-02 — the two findings D-09 and D-10 disposition. WR-02's own "Fix:" paragraph
  recommends the CHANGELOG disclosure that D-09 declines; record the decline, do not silently drop
  the recommendation.
- `.planning/phases/56-per-document-template-documentation/56-REVIEW.md` lines 58-90 — the two
  documentation findings D-10 fixes, including the note that the stale prerequisite pair also
  appears in `docs/source/installation.rst:7-8`, outside 56's reviewed file set.

### Version-literal and gate surfaces

- `pyproject.toml:7` — the sole version literal (measured 2026-08-16). `:10` `requires-python` and
  `:28` the `sphinx` pin are the truth D-10's prose fix must match. `:70-77` is the
  `[tool.setuptools.package-data]` hunk D-15's sweep must account for.
- `README.md:347` — `**Status**: Stable (v0.8.0) - Production ready`.
- `tests/test_readme_version_sync.py` — asserts the two agree, so both must move together.
- `tests/test_preview_version_sync.py` — the `@preview` lockstep guard over the sync surfaces.
- `tests/test_changelog_page_gate.py:50-64` — the `RELEASE_VERSIONS` tuple, currently ending at
  `"0.8.0"`.
- `tests/test_corpus_gate.py` — the GATE-02 full-corpus gate (`@pytest.mark.slow`; `pytest.skip`s
  rather than fails when the corpus is unavailable, so a skip is **not** evidence).
- `tests/test_two_key_selection_gate.py` and `tests/fixtures/two_key_selection_gate/` — D-14's
  multi-template `-b typstpdf` evidence, already permanent.

### Release machinery (exercised, not triggered)

- `.github/workflows/ci.yml:3-8` — the push/PR/dispatch triggers D-12 rests on; `:127-169` the
  `build` job and the "Verify wheel carries the template bundle" step SC#3 names; `:37,67,88,109,174,202`
  the `uv sync --locked` steps D-13's sequencing constraint counts.
- `.github/workflows/release.yml` — the `validate` job checks the `## [0.9.0]` heading exists and
  is non-empty before a tag is ever pushed (Phase 41 D-09); `create-release` is the job SC#5's
  checklist must explicitly say to observe.
- `scripts/extract_changelog_section.py` — run against the new `## [0.9.0]` section as a
  **precondition**, never as acceptance. SC#5 requires the GitHub Release body to be byte-identical
  to its output.
- `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — the
  eleven `--locked` steps and the measured failure mode behind D-13's sequencing constraint.

### Standing project constraints

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus `uv run` for every
  executor. Worktree isolation is the standing execution mode. D-08's `v0.8.0`-tag build is a
  *separate* worktree from the executor's own; do not confuse the two.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — the surfaces D-05's second item counts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tests/fixtures/two_key_selection_gate/` — three `typst_documents` entries across two registry
  keys, with `_typst/report/base.typ` (a4, 11pt) and `_typst/memo/base.typ` (us-letter, 14pt)
  deliberately differing so a PDF comparison can see two different templates. Neither declares an
  `@preview` import, precisely to avoid creating a fourth version-lockstep site. This is SC#3's
  multi-template evidence with no new authoring (D-14). It is also the natural fixture for D-08's
  `v0.8.0`-tag before-build, since the same `conf.py` existed after Phase 54.
- `scripts/extract_changelog_section.py` — committed and pytest-covered since Phase 41; this phase
  only exercises it.
- `tests/test_readme_version_sync.py` / `tests/test_preview_version_sync.py` — the established
  "a release-surface fact is pinned by pytest" pattern; both must stay green across the bump. Note
  D-11 declined extending this pattern to the prerequisites prose.
- `docs/source/changelog.rst`'s `Migrating from 0.7.x to 0.8.0` — a finished 83-line model with
  before/after `code-block:: text` pairs, an explicit "these two renames are easy to confuse"
  disambiguation paragraph, and a closing pointer to `/user_guide/output_layout`.
- `docs/source/user_guide/configuration.rst`'s "Removed Configuration Values" table — Phase 56
  already published the `typst_template_assets` migration sentence, so D-03's bullet has a
  finished, gate-bound statement to agree with rather than derive.

### Established Patterns

- **Version literals:** `pyproject.toml:7` is the sole literal; `typsphinx.__version__` derives
  from `importlib.metadata` (so the editable install must be regenerated); `README.md:347` carries
  the human-readable status line; `uv.lock` moves in lockstep — and under D-13 it must move
  *before* any CI dispatch.
- **CHANGELOG entry shape:** lead paragraph → `### Added` / `### Changed` / `### Fixed` /
  (`### Removed`) → `### Verified` → tail link block.
- **Evidence culture:** commands and their output transcribed verbatim; `human_needed` recorded
  honestly; abstain rather than assert without direct evidence. A `pytest.skip` is not evidence.
- **Discovery is run-time, file lists are floors.** Every "anywhere under X" criterion in this
  milestone is verified by a repo-wide grep at discovery time (invariants #4/#11); 54.1's D-13 and
  56's D-10 both recorded live examples of a written floor missing a hit. D-11's prose fix inherits
  this rule.

### Integration Points

- The post-bump commit ↔ the dispatched CI run — D-12/D-13's evidence path. Requires pushing 188+
  commits to `origin/gsd/v0.9.0-per-document-templates`, then dispatching `ci.yml` on that branch,
  because the push trigger does not cover it.
- `CHANGELOG.md` ↔ `docs/source/changelog.rst` ↔ `tests/test_changelog_page_gate.py` — one edit,
  three surfaces. The `.. include::` propagates the release history automatically (DOC-12), so only
  the gate's version tuple is hand-maintained; the migration section is new work this time (D-06).
- `CHANGELOG.md` ↔ `release.yml` — the `## [0.9.0]` heading must exist and be non-empty before any
  tag is pushed, because `validate` checks it.
- `uv.lock` ↔ every CI job — eleven `uv sync --locked` steps across `ci.yml`, `docs.yml`,
  `release.yml` and `drift.yml`. A stale lockfile fails at install, before any signal.
- `.planning/todos/pending/` ↔ `57-HANDOFF.md` — D-09 and the todo-ledger disposition make the
  ledger the only record of the deferred findings, which raises the handoff's importance. The
  measured fact that one such filing already went missing (`<specifics>` 9) is the concrete reason
  to verify each record exists on disk rather than trust a completion narrative.

</code_context>

<specifics>
## Specific Ideas

Everything below was measured this session (2026-08-16) against the live tree, not inferred.

1. **The version literal census is unchanged in shape from v0.8.0's.** `pyproject.toml:7` →
   `version = "0.8.0"`; `README.md:347` → `**Status**: Stable (v0.8.0) - Production ready`. No
   other `0.8.0` literal in either file.

2. **`## [Unreleased]` is NOT empty this time.** Unlike Phase 52, it holds seven real v0.9.0
   bullets written by Phases 54/54.1/55 as each landed. This is the single biggest procedural
   difference from the 52 precedent and the reason D-02 exists at all.

3. ~~**The tail link block ends at `[0.7.1]`** and `[Unreleased]` compares `v0.8.0...HEAD`. There is
   **no `[0.8.0]` line** in the block — worth checking whether the v0.8.0 release-prep phase missed
   it, since this phase must add `[0.9.0]` and advance `[Unreleased]` regardless.~~
   **RETRACTED 2026-08-16 (post-research, owner-approved) — measurably false.** `[0.8.0]` is present
   at `CHANGELOG.md:1157` and is the topmost release line; `[Unreleased]` sits last at `:1177`.
   The block is complete. See the AMENDED block under `<canonical_refs>` → "CHANGELOG.md tail".

4. **The diff anchors coincide.** `v0.8.0` → `d9523ea`, an ancestor of HEAD. `origin/main` →
   `aed773c9`, also an ancestor, and it *is* `git merge-base origin/main HEAD`. Excluding
   `.planning/`, both `v0.8.0..HEAD` and `aed773c9..HEAD` give **163 files changed, +11,262 /
   −1,615** — the four commits between them are planning/docs only. 270 commits in the range.

5. **The milestone-diff invariants are cheaper to state than to prove this time.**
   `git diff v0.8.0..HEAD -- typsphinx/__init__.py | grep add_config_value` shows exactly two
   lines: `-typst_template_assets` and `+typst_document_templates` — one removal and one addition.
   The "no new `typst_*` config value" assertion Phase 52 made therefore does **not** carry over
   (the registry is this milestone's headline feature) and must not be copied forward unexamined.
   `templates/base.typ` still carries exactly **4** `@preview` lines. `pyproject.toml` is **not**
   unchanged, so the runtime-dependency claim in `### Verified` needs a hunk-level argument rather
   than an empty diff.

6. **Only `typst_template_assets` was removed this milestone.** `typst_authors` went in v0.7.1
   (Phase 45.1, commit `d5277d0d`) and `typst_toctree_defaults` in v0.6.3; all three live in
   `REMOVED_CONFIG_VALUES` together, which makes the dict look like three v0.9.0 removals if read
   without the "Removed in" column.

7. **CI reachability on this branch.** `ci.yml`'s `on.push.branches` and `on.pull_request.branches`
   are both `[main, develop]`; `workflow_dispatch` is the only trigger this branch can use without
   opening a PR. Last full CI: `31884774067` (2026-08-15, dispatched, 6m33s, success) — which
   predates Phases 54, 54.1, 55 and 56 entirely. The branch is **188 commits ahead** of
   `origin/gsd/v0.9.0-per-document-templates` (`35ee8a0`).

8. **SC#5's precondition already holds.** `git tag -l v0.9.0` is empty and `v0.9.0` does not appear
   in the tag list (which ends at `v0.8.0`).

9. ~~**A todo filing recorded as done does not exist.** `STATE.md`'s Phase 56 record says its two
   review WARNINGs were "filed forward as the todo
   `stale-version-prerequisites-and-dead-config-link-in-published-docs` by owner decision".
   `grep -rl` across `.planning/` finds that string **only inside `STATE.md` itself`**;
   `.planning/todos/pending/` holds 9 files and `completed/` holds none matching.~~
   **RETRACTED 2026-08-16 (post-research, owner-approved) — the record exists.** It is at
   `.planning/todos/completed/2026-08-16-stale-version-prerequisites-and-dead-config-link-in-published-docs.md`
   (frontmatter `created: 2026-08-16T12:45:09.347Z`, committed in `70e24958` alongside the fix
   itself). The original observation was a **method artifact, not a missing file**: `grep -rl`
   searches file *contents*, and this slug appears only in the *filename* — the body never repeats
   it. `ls .planning/todos/completed/ | grep <slug>` finds it immediately.

   **The lesson survives its own retraction, in a sharper form.** The discussion's conclusion —
   "a completion narrative is not proof a record exists" — was right in spirit and reached by a
   method that could not have distinguished the two cases. So the operative rule for every deferral
   `57-HANDOFF.md` carries is stronger than originally written: **verify each record by listing the
   ledger directory, never by grepping content**, and state which check was run. This retraction is
   itself an instance of the rule that a narrative — including a CONTEXT's own "measured this
   session" claim — is not proof.

10. **The owner's framing across this discussion.** Consistency with the v0.8.0 close was chosen
    where the situation matched (silent deferral again — D-09; the same three `### Verified` items
    — D-05), and departed from where measurement showed the situation had moved (four Breaking
    marks instead of two — D-01; promoting written prose instead of re-authoring — D-02; two CI
    dispatches instead of one — D-12). Twice the owner declined a proposed gate (D-07, D-11),
    accepting recurrence risk knowingly; do not re-litigate either by adding a gate "for safety".

</specifics>

<deferred>
## Deferred Ideas

- **Fixing `54.1-REVIEW.md` WR-02 (resolving `templates_path` against `confdir`)** — declined by
  D-09 and by the prep-only fence. The reviewer's own recommended minimum (a CHANGELOG carve-out
  sentence) was also declined. Recorded here so a later reader does not mistake the silence for an
  oversight: the `-c`/`--confdir` republication hole is real, `_copy_used_template_bundles()` has
  no `templates_path` awareness of its own, and the shipped CHANGELOG sentence reads as
  unconditional.

- **Fixing `54.1-REVIEW.md` WR-01 (the tripled "Custom template not found" warning)** — declined by
  D-10; it needs a `typsphinx/builder.py` change. Reproduced directly against the current tree in
  the review, so it is not speculative.

- **A prerequisites version-sync gate** — declined by D-11 after being put with its measured
  recurrence history. Adding it later costs nothing structural.

- **A test gate over migration guides** — declined by D-07. The 0.7.x→0.8.0 guide is equally
  unbound today.

- **A `### Known Limitations` CHANGELOG section and public GitHub issues** — argued and declined by
  D-09, the third consecutive release to decline it.

- **Promoting the deferred items to ROADMAP backlog entries** — not adopted; the todo ledger is the
  path `/gsd-new-milestone` actually reads (52-CONTEXT D-03's measured reasoning), and the
  `## Backlog` section remains the second ledger that decision avoided creating.

### Reviewed Todos (not folded)

`todo.match-phase 57` returned matches across the entire 9-file pending ledger — keyword noise
against a release-prep phase. **None folded.** Each is deferred with its reason:

- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` (0.9) — an HTML sidebar
  defect in this project's own docs `index.rst`. Real, but it is neither a release surface nor part
  of REL-08; matched only on `area: docs`.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` (0.6) — Future requirement LNK-01; `links.yml`'s
  repo-wide lychee check already covers the links this release adds.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` (0.6) — forbidden by `CLAUDE.md`
  and by the milestone's own binding constraint until the todo itself lands. Doubly deliberate.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` (0.6) — REL-04's record, closed
  at the v0.7.1 publish. Worth confirming it belongs in `todos/completed/` rather than `pending/`
  — flagged for the planner, not decided here (the same flag Phase 52 raised and that evidently
  went unactioned).
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` (0.6) — a `flake.nix`-side toolchain
  repair (Future requirement QUA-06). Does not block SC#3, which takes lint from CI (D-13).
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` (0.6) —
  a translator defect; `51-CONTEXT.md` D-07 excluded `:numref:` from every published surface by
  owner override, and that exclusion is carried forward to this CHANGELOG unchanged.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — CI/tooling, `severity: major`.
  **Not folded, but load-bearing as context:** its measured `--locked` census is what makes D-13's
  sequencing constraint concrete. Fixing dependabot's workflow is not this phase's work.
- `2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md` — a `builder.py` path predicate;
  a code defect, prep-only fence applies.
- `2026-08-16-track-image-escape-branch-basename-not-normalized.md` — same class.

</deferred>

---

*Phase: 57-v0-9-0-release-prep-prep-only*
*Context gathered: 2026-08-16*
