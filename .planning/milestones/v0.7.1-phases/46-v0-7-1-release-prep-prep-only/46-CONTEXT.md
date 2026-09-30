# Phase 46: v0.7.1 Release Prep (prep-only) - Context

**Gathered:** 2026-08-10
**Updated:** 2026-08-11 — second discussion pass. Phase 45.2 landed, `origin/main` moved to
`9b2b76b` (PR #131 merged), and the branch CI went RED on the Windows lanes. D-01..D-10, D-12,
D-13, D-15, D-18, D-19 are unchanged and remain locked. D-11, D-14 and D-16 are amended in place;
**D-17 is retracted — it was wrong**. D-20..D-28 are new.
**Status:** Ready for planning

<domain>
## Phase Boundary

Prep-only release work for v0.7.1: bump the version in lockstep, curate the `## [0.7.1]` CHANGELOG
entry, prove the post-bump tree green live, discharge REL-04's in-phase share, and hand off a
checklist — with **zero irreversible action taken**. Requirements: **REL-06** (prep half only) and
**REL-04** (verification-and-handoff share only; the requirement itself does not close here).

**In scope:**

- **Merging `origin/main` (`9b2b76b`) into the milestone branch at the head of the phase** (D-20).
  The branch does not contain it: `git merge-base --is-ancestor origin/main HEAD` → false.
- **One-line repair of `tests/test_docs_contract_claims_gate.py:170`** so the two Windows CI lanes
  go green (D-22). Test file only — no `typsphinx/` change, so the prep-only fence holds.
- `pyproject.toml:7` — `version = "0.7.0"` → `"0.7.1"` (measured this session: still the sole
  version literal), with `uv.lock` and `README.md:342` (`**Status**: Stable (v0.7.0) - Production
  ready`) moved in lockstep and the editable-install metadata regenerated so
  `typsphinx.__version__` reports `0.7.1`.
- A curated `## [0.7.1]` entry in `CHANGELOG.md` per D-05..D-10, **plus the tail link-block
  rollover** — add the `[0.7.1]` release-tag line and advance `[Unreleased]` to `v0.7.1...HEAD`.
- The matching edit to `docs/source/changelog.rst` — which is a **new "Migrating from 0.7.0 to
  0.7.1" section**, not a release entry (D-09; the page `.. include::`s `CHANGELOG.md`, so the
  release history is already automatic).
- SC#3 live-run evidence on the post-bump tree per D-11..D-13.
- SC#4's invariant proof over the SHA-anchored full milestone diff, anchored at the **`v0.7.0` tag
  (commit `75fd8ed`)** and re-measured on the post-merge HEAD (D-21, superseding D-14's `87f242a`).
- REL-04's in-phase share: verify `release.yml`'s `create-release` job carries the
  `astral-sh/setup-uv` + `Set up Python` steps (**already confirmed this session** at
  `release.yml:162-168`), and run `scripts/extract_changelog_section.py` against the new
  `## [0.7.1]` section — both recorded as *preconditions*, never as acceptance.
- SC#5 handoff: a standalone `46-HANDOFF.md` following the `41-HANDOFF.md` precedent.
- Closing-record hygiene per D-16/D-17.

**Out of scope:**

- **Any publish or otherwise irreversible action** — `git tag v0.7.1`, triggering `release.yml`,
  PyPI, the GitHub Release, opening or merging the PR. `git tag -l v0.7.1` and
  `git ls-remote --tags origin v0.7.1` must both be empty at phase close. The prep/publish fence is
  absolute (Phase 33/35/41 precedent).
- **Any `typsphinx/` code change**, including a deprecation shim for the removed `typst_authors`
  (D-03) **and the two measured `TypstBuilder._track_image()` defects that arrive with PR #131**
  (D-27) — the prep-only fence is held even though both silent-failure modes are real. The
  Windows repair (D-22) is not an exception to this: it touches a test module, not `typsphinx/`.
- **The `tox-uv` → `tox-uv-bare` dependency repair** — routed to a newly inserted **Phase 45.2**
  (D-18). Inserting that phase into `ROADMAP.md` / `REQUIREMENTS.md` is a separate `/gsd-phase`
  action and is **NOT** Phase 46 work (the Phase 41 D-11 precedent for Phase 40.1).
- ~~**PR #131 / Issue #130** — the absolute-image-URI fix stays out of v0.7.1 (D-17).~~
  **Retracted 2026-08-11 — D-17 was wrong. PR #131 is MERGED and ships in v0.7.1** (D-28).
- The 10 pending todos (D-16).
- Revisiting the version number — `0.7.1` is locked by D-01.
- Editing historical CHANGELOG entries.

</domain>

<decisions>
## Implementation Decisions

Every measured value below was taken **this session (2026-08-10)** against the live tree, not from
recall. Where a measurement contradicts a prior artifact, the contradiction is stated explicitly
rather than silently corrected.

### Version number and how breakage is framed

- **D-01: The release ships as `0.7.1`.** ROADMAP SC#1 fixes it and the owner declined `v0.8.0` on
  2026-08-04. The counter-argument was stated in full before the decision and rejected: that
  2026-08-04 judgment was made when CONF-08's filename rename was the only user-visible change,
  whereas CONF-10/CONF-11/CONF-12 were added on 2026-08-10; that this project's precedent for
  breaking config removal in a patch release (`typst_output_dir` / `typst_author_params` in 0.6.2,
  `typst_toctree_defaults` in 0.6.3) covered only **inert** values, while `typst_authors` is live
  and CONF-11 changes rendering with no error at all; and that Phase 44.2 published a notice
  promising removal in a future **major** release. Owner reaffirmed `0.7.1` with all three facts on
  the table. Consequence, and the reason D-02 exists: the version number carries no warning, so the
  CHANGELOG is the only surface that can.

- **D-02: Breakage is marked three ways.** (a) The lead paragraph states plainly that this patch
  release can break a working configuration; (b) each of CONF-10 / CONF-11 / CONF-12 carries a
  `**Breaking:**` prefix on its bullet; (c) a `### Removed` section is created — the first in this
  CHANGELOG's history — to hold `typst_authors`. Rejected: lead-declaration-only (the Phase 41 D-03
  shape, which was justified there by the measured fact that *nothing* broke, a premise that does
  not hold here), and per-bullet markers without the `### Removed` section (leaves a public config
  value's disappearance without its own heading). `docs/source/changelog.rst`'s migration guide
  already uses `**Breaking:**`, so the two surfaces share vocabulary.

- **D-03: The silent failure of a leftover `typst_authors` is accepted and handled in documentation only.**
  Measured this session: `typst_authors` now returns **zero** hits across `typsphinx/`,
  `docs/source/`, `examples/` and `tests/`, and Sphinx ignores an unregistered `conf.py` variable
  without warning — so a user upgrading with `typst_authors` set loses author information silently.
  A fail-loud shim was offered (re-register the name and raise, matching the `ELEMENTS_ALLOWLIST`
  stance that unknown configuration fails loudly) and declined: Phase 46 takes no code change. The
  shim is kept as the option of record in `<deferred>`. Note this is a *stricter* reading of the
  prep-only fence than Phase 41 took — Phase 41's D-12 accepted one docstring edit — and the
  difference is deliberate, because this one would be a behaviour change.

- **D-04: The published-notice contradiction is stated in both places, split by kind.** The
  **fact** ("0.7.0's documentation announced removal in a future major release; this patch release
  removes it") goes in the CHANGELOG's `### Removed` bullet, which reaches the GitHub Release body.
  The **rationale** (LaTeX parity, per 45.1 D-F) and the rewrite steps go in the migration guide.
  This discharges 45.1 D-F's explicit instruction that "Phase 46's CHANGELOG curation can say so
  plainly".

### The `## [0.7.1]` CHANGELOG entry

- **D-05: Bullets are cut at user-visible-change granularity — 6 to 8 of them — with requirement IDs in trailing parentheses.**
  Direct continuation of Phase 33 D-09 / Phase 41 D-01. Rejected: one
  bullet per requirement (18 bullets, which would put QUA-01's docstring fix and QUA-03's planning-
  document hygiene in release notes), and a phase-level roll-up (7 bullets, but phase boundaries are
  an internal partition users cannot see, and it buries CONF-11 inside "Phase 45.1").

- **D-06: The lead paragraph's axis is "the configuration the documentation promises actually takes effect."**
  It is the project's own core-value sentence and it covers the largest share of the
  milestone's 18 requirements at once — CONF-08 (following the Quick Start now produces a PDF),
  CONF-09 (`typst_documents`' title/author reach the render), DOC-13/CONF-11/CONF-12 (the published
  template contract becomes true). Rejected: "v0.7.0's debts cleared" (the milestone-goal wording —
  accurate but told from the project's side, not the user's), and leading with the breaking-change
  warning (D-02 already places that in the same paragraph; leading with it would bury the fact that
  this release mostly repairs things that were broken).

- **D-07: CONF-08's callout names both measured facts, not just the rename.** Phase 44's SC#4
  handoff (`44-GATE-EVIDENCE-03.md` § 7) records that an unset-`typst_documents` build changes
  **both** its emitted filename (`index.typ` → `quickstartdefaultgate.typ`, derived from `project`)
  **and** its emitted structure (untemplated body → fully templated). ROADMAP SC#2's wording names
  only "the output-filename change"; the entry must carry both. Quote § 7 rather than re-deriving.

- **D-08: `### Verified` carries the same three items as 0.6.5 / 0.7.0, with the dependency claim scoped to runtime.**
  Measured this session: the milestone diff adds `myst-parser` (and transitively
  `mdit-py-plugins`) to the **`docs` extra** in `pyproject.toml:53` — a Phase 45 / DOC-12
  consequence — with no change to `[project] dependencies`. Writing the first item as "No new
  **runtime** dependencies" keeps the claim true and pre-empts a reader who diffs `uv.lock`.
  Rejected: listing `myst-parser` as a fourth item (the section exists to enumerate what did *not*
  change), and dropping the section (the last three releases all carry it).

- **D-09: `docs/source/changelog.rst` gains a "Migrating from 0.7.0 to 0.7.1" section with before/after code fragments.**
  Measured: that page is `.. include:: ../../CHANGELOG.md` with a
  hand-written "Migration Guides" tail, so the migration section is the *only* hand-written surface
  and ROADMAP SC#2's "gains the matching `0.7.1` entry" resolves to it. Three items need fragments:
  `typst_authors` → the `typst_template_function` `params` route; a project that sets `params` today
  must now enumerate all nine parameters (CONF-11's exclusivity); and a custom template that does
  not declare `lang` starts failing with `unexpected argument: lang` (CONF-12). Every existing
  Migrating section is prose bullets only — code fragments enter this page here for the first time.
  Rejected: prose-only (does not convey "write all nine") and omitting the section (incoherent
  immediately after D-02's triple marking).

- **D-10 [derived, not separately asked]: the Keep-a-Changelog section split is `### Added` / `### Changed` / `### Fixed` / `### Removed` / `### Verified`.**
  `### Removed` is new per D-02.
  The planner assigns requirements to sections; the only fixed assignment is `typst_authors`
  (CONF-10) → `### Removed`.

### SC#3 — what "green" means and where the evidence comes from

- **D-11: The branch CI run on the post-bump commit is the authority for pytest / lint / type; local `tox` supplies what CI does not run.**
  The milestone branch is already on `origin`
  (invariant #5), so pushing the post-bump commit and reading its run — including the Windows lanes,
  which caught a real cp1252 defect at the v0.7.0 close — is a **live** result, not an inherited
  one, and therefore satisfies SC#3. The full-corpus `-b typstpdf` gate and both docs builds are run
  locally. Rejected: promoting the local run to the authority (never sees Windows or
  macOS), and requiring both full green runs (largest pre-release wait for the least new
  information).

  **Amended 2026-08-11 (a) — the Phase 45.2 dependency is discharged.** 45.2 completed 2026-08-11
  (`ROADMAP.md:361`, 5/5 plans; `pyproject.toml:38` now `tox-uv-bare>=1.35,<2`, `tox.ini:11`
  `requires = tox-uv-bare~=1.35`). The original wording "local `tox` does not currently run at all"
  no longer holds and is struck.

  **Amended 2026-08-11 (b) — the local half is per-environment, not the whole `env_list`.**
  Measured and recorded as todo `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos`:
  `.venv/bin/ruff` is a generic-linux ELF that NixOS's stub loader rejects (exit 127) and no other
  `ruff` resolves on PATH, so a bare `tox` still cannot go green locally — its `lint` env dies.
  This does **not** weaken SC#3, because this decision already assigns lint/type/pytest authority to
  CI (green on that job: run `31445582363`, `Lint and Format Check` → success). The local evidence
  is therefore `tox -e docs-html`, `tox -e docs-pdf` and the full-corpus `-b typstpdf` gate,
  invoked per-environment.

- **D-12: The `ja` evidence is a single local `SPHINX_LANGUAGE=ja` docs-pdf build, not Phase 41's four-check glyph bar.**
  The bar was justified in Phase 41 by two measured facts about that
  milestone; both were re-measured here and **neither holds**: `raw(` call sites in
  `typsphinx/translator.py` are **41 before and 41 after** (`git show main:` versus the working
  tree), and the milestone diff over `typsphinx/` names no font family. What does warrant touching
  `ja` at all is CONF-12, which changes the route by which `lang` reaches a template. Rejected:
  re-running the full four-check bar (pays Phase 41's cost with none of its triggers), and skipping
  `ja` entirely (CONF-12 would reach a published artifact unexercised).

- **D-13 [correction of record]: there is nothing to remove in `typsphinx-doc-translations`, and the `ja` build exercises this repository's own files.**
  45.1's `<deferred>` carries "the
  translations repo's copy of the `lang` workaround" as a handoff item. Measured this session via
  the GitHub API: that repository contains **no `conf.py` and no `.typ` template** — its tree is
  `.readthedocs.yaml`, `Makefile`, `locale/ja/**`, and the parent mounted as the submodule
  `typsphinx/`. The `lang` workaround existed only in `docs/source/conf.py`, which 45.1 already
  removed (the file now carries a "do not re-add that workaround" comment). `docs/source/_typst/
  custom_template.typ:64-75` declares all nine parameters including `lang`, so the docs build is
  safe on both languages. The handoff item is retired; the standing **two-repository tagging** cost
  is unaffected.

- **D-14 [SUPERSEDED by D-21 on 2026-08-11] — SC#4's invariant sweep runs over merge-base 87f242a..HEAD.**
  Measured 2026-08-10: 323 commits, and excluding `.planning/` the code delta is
  119 files / +10,052 / −847. Re-measured 2026-08-11 before the merge: 371 commits, 125 files,
  +10,568 / −932. Kept as a record of what the figure was; **use D-21's anchor, not this one**. The
  `@preview` count and its four sync surfaces are asserted mechanically; the dependency assertion is
  worded per D-08 — both of those clauses carry forward into D-21 unchanged.

- **D-15 [derived]: evidence is NOT written to `46-VERIFICATION.md`.** That name is reserved by the
  verifier and will be clobbered — the Phase 41 D-15/`41-RELEASE-EVIDENCE.md` precedent.

### Close-out disposition

- **D-16: Every pending todo is explicitly deferred, each with its reason recorded** — the
  Phase 41 D-14 shape. None relates to REL-04 / REL-06 and none blocks the release. See
  `<deferred>` for the enumerated list. **Amended 2026-08-11: the ledger is 12 records, not 10.**
  Phase 45.2 filed two (`2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos`,
  `2026-08-11-windows-path-separator-breaks-contract-claims-gate`). The second one is **not**
  deferred — D-22 resolves it in this phase, so it is filed to `todos/completed/` at phase close.
  The two `_track_image` records change category rather than count: they described PR-only code on
  2026-08-10 and now describe code that is on `main` and ships in v0.7.1 (D-27, D-28).

- **D-17 [RETRACTED 2026-08-11, the claim was false, see D-28] — PR #131 is NOT in v0.7.1.**
  The 2026-08-10 measurement it rests on (`gh pr view 131` →
  `state: OPEN`, `mergedAt: null`) was taken before the merge landed at
  `2026-08-10T13:54:05Z`. `STATE.md` was right and this decision was wrong. Retained rather than
  deleted so a later reader can see that the "correction of record" was itself corrected, and so
  the instruction it issued — "Phase 46 corrects the `STATE.md` sentence" — is visibly cancelled:
  **`STATE.md` needs no correction on this point.**

### Routed out of this phase

- **D-18: The `tox-uv` → `tox-uv-bare` dependency repair ships in v0.7.1, in a newly inserted Phase 45.2, before Phase 46.**
  Discovered and fully measured during this discussion; see
  `<specifics>` items 1–6 for the evidence chain. The short form: `pyproject.toml`'s `dev` extra
  depends on `tox-uv`, which is a meta package (`tox-uv-bare==1.35.2` + `uv<1,>=0.9.27`), and the
  PyPI `uv` wheel installs a **generic-linux ELF** at `.venv/bin/uv` that NixOS cannot exec. That one
  file breaks two things at once: `tox` is **completely non-functional locally** (every env exits
  127), and every test that shells out to `["uv", "run", "sphinx-build", …]` fails, because `uv run`
  prepends `.venv/bin` to PATH. Both halves of the repair were measured (items 4 and 5). The owner
  chose to land it **before** the release rather than after, accepting that `pyproject.toml` /
  `tox.ini` / `uv.lock` move shortly before the release phase, because it raises the quality of the
  very evidence SC#3 collects (D-11). **Inserting Phase 45.2 into `ROADMAP.md` and `REQUIREMENTS.md`
  is a separate `/gsd-phase` action and is not Phase 46 work.** — **Reversibility:** reversible —
  a dev-extra dependency name in two files plus the lockfile; no published contract and no runtime
  surface is touched.

- **D-19: Phase 45.2's change gets no `## [0.7.1]` CHANGELOG bullet.** It is confined to the `dev`
  extra and changes nothing for a user *of* typsphinx. Consistent with the 0.6.5-era rule that test
  and verification machinery is not user-visible. Measured mitigating fact: the only person the
  bundled `uv` actually served is someone who installs via `pip install -e ".[dev]"` **and** then
  runs a bare `tox` — `docs/source/contributing.rst:117-128` instructs `uv run tox …` everywhere, so
  the documented path already requires uv independently, and `poetry` appears nowhere in the
  repository. Under `tox-uv-bare` that person gets tox-uv's own three-option error message rather
  than a silent failure.

### Taking `origin/main` into the release branch (added 2026-08-11)

- **D-20: `origin/main` (`9b2b76b`) is merged into the milestone branch at the head of Phase 46.**
  Measured 2026-08-11: `git merge-base --is-ancestor origin/main HEAD` → false; `origin/main` is
  four commits ahead (`fa1ab88`, `b248ddd`, `fe284a7`, `9b2b76b` — the PR #131 merge). A read-only
  `git merge-tree --write-tree HEAD origin/main` reports **exactly one conflict, `CHANGELOG.md`**;
  `typsphinx/builder.py` and `tests/test_builder.py` auto-merge clean. The conflict sits in the
  `## [Unreleased]` block — the very text D-05..D-10 rewrite — so conflict resolution *is* the
  CHANGELOG curation work rather than an extra cost. Merging first means the tree SC#3 proves green
  and the tree that eventually gets tagged are the same tree. Rejected: merging inside the CHANGELOG
  plan (crosses `uv.lock` regeneration with the merge); rebasing onto `origin/main` (rewrites 371
  commits and force-pushes a branch already on `origin`, against milestone invariant #5); and
  deferring to `/gsd-complete-milestone` (resolves a CHANGELOG conflict inside the irreversible
  half, and tags a tree no CI run ever saw). A merge into a local milestone branch takes no
  irreversible action, so the prep/publish fence is untouched. — **Reversibility:** reversible — the
  merge commit can be dropped before anything is tagged or published.

- **D-21: SC#4's invariant sweep is anchored at the `v0.7.0` tag (commit `75fd8ed`), re-measured on the post-merge HEAD.**
  Supersedes D-14. Measured 2026-08-11: `v0.7.0..HEAD` excluding `.planning/` is 126 files /
  +10,582 / −932, against `87f242a..HEAD`'s 125 files / +10,568 / −932 — `87f242a` is one commit
  after the tag and is merely where this branch happened to fork. Anchoring at the tag makes the
  swept diff identical to "what a v0.7.0 user receives", which is the same diff the CHANGELOG's
  completeness is judged against. Both figures above are **pre-merge** and must be re-taken after
  D-20's merge. Rejected: keeping `87f242a` (measures branch contribution, not the release), and
  recording both anchors (the two differ by one file and 14 lines — redundant).

### The Windows CI lanes (added 2026-08-11)

- **D-22: The Windows CI failure is repaired inside Phase 46, in the test module only.**
  Measured: CI run `31445582363` on this branch is `failure`, and the **only** failing jobs are
  `Test Python 3.12 on windows-latest` and `Test Python 3.13 on windows-latest` — lint, type,
  coverage, build, both integration jobs, and every ubuntu/macos lane are green.
  `tests/test_docs_contract_claims_gate.py::TestContractClaimPageEnumerationIsClosed` fails because
  `_discovered_claim_pages()` at `:170` builds `str(page.relative_to(REPO_ROOT))`, which yields
  backslash paths on Windows and cannot match the forward-slash literals in the reviewed set or in
  `EXCLUDED_CLAIM_PAGES`. The file was added by **Phase 45.1** (commit `a6fa38b`, "test(45.1-07):
  add permanent cross-page contract-claim guard") and does not exist in `v0.7.0` — this is a
  regression the milestone itself introduced and would ship. The repair touches a test module, not
  `typsphinx/`, so D-03's prep-only fence is intact; Phase 41 D-12 is the precedent for a
  non-`typsphinx/` edit inside a prep phase. Rejected: inserting a Phase 46.1 (the Phase 45.2
  procedure for a one-line change), and excluding the Windows lanes from SC#3 — that last one is
  self-defeating, because D-11 makes CI the authority *precisely because* the Windows lanes caught
  a real cp1252 defect at the v0.7.0 close.

- **D-23: Two CI runs back SC#3 — a check run and an authority run.**
  Run 1 carries D-20's merge plus D-22's Windows repair, and exists to confirm the Windows lanes
  actually go green; that cannot be verified locally, because there is no Windows on this machine.
  Run 2 carries the bump and the `## [0.7.1]` entry and **is** SC#3's authority per D-11. Rejected:
  one combined push (a missed Windows repair would only surface at the end of the phase, with the
  retry commits landing after the bump), and three separated runs (a third CI wait buys no new
  information — the merge and the test repair touch disjoint files).

### PR #131 in the release notes (added 2026-08-11)

- **D-24: PR #131's `[Unreleased]` entry is compressed to house granularity, not moved verbatim.**
  The entry `origin/main` carries is one bullet with ~14 lines of prose; `## [0.7.0]`'s `### Fixed`
  bullets run 3–5 lines, so it would be roughly triple the length of everything around it. Its
  title form already matches the house style (`**… (Issue #130)**`). The compression keeps the
  user-visible fact — building with an image-conversion extension or a downloaded image copied no
  image and aborted the Typst compile — and drops the internal mechanism (`os.path.join()`
  swallowing its first argument once the second is absolute; the bogus `../..` depth prefix), which
  belongs in the PR, not the release notes. This makes PR #131 the **sixth** user-visible change in
  the milestone, so D-05's "6 to 8 bullets" now has a named sixth. Rejected: moving the 16 lines
  verbatim, and rewriting from scratch (discards a contributor's own account for no gain).

- **D-25: The bullet credits `@christianwehe` in its trailing parentheses.**
  Measured: this CHANGELOG has **no** contributor-attribution precedent — zero hits for `Thanks`,
  `@handle`, or `contributed` — because every prior change was the maintainer's. It does have a
  settled identifier convention (`(DOC-09, DOC-10, Issue #119)`, `(PDF-01, Issue #117)`) and a
  `(PR #14)`-style trailing form from the 0.4.x era, so the credit fits an existing slot rather than
  inventing one. The credit reaches the GitHub Release body by the same route D-04 uses for the
  early-removal fact. This sets the precedent for future external contributions. Rejected: Issue
  number only (renders the first external contribution anonymous on the release notes), and a new
  `### Contributors` section (a second brand-new section in a release that already introduces
  `### Removed` per D-02).

- **D-26: PR #131 gets no requirement ID, and `REQUIREMENTS.md` is not touched.**
  The fix belongs to none of the milestone's 19 v1 requirements and no phase delivered it — it
  arrived on `main` by an independent route. `Issue #130` plus `PR #131` identify it, which the
  CHANGELOG already has precedent for (`- **Issue #114 — fatal figure/image bugs**`, and the 0.4.x
  `- **Issue #5**: … (PR #14)` form). Coverage stays **19/19 mapped, zero orphans**, and the
  requirements table keeps meaning "what this milestone planned and delivered". Rejected: minting a
  new requirement and mapping it to Phase 46 (would attribute to Phase 46 something Phase 46 did not
  implement), and adding a coverage-line footnote (bookkeeping for a fact the CHANGELOG already
  states).

### The `_track_image()` defects that arrive with PR #131 (added 2026-08-11)

- **D-27: Both `_track_image()` defects ship in v0.7.1 unfixed, disclosed internally only.**
  The two records stay in `todos/pending/` and are named in `46-HANDOFF.md`; **no `### Known
  Limitations` section is added to the CHANGELOG and no GitHub issue is filed.** The counter-case
  was put fully and declined, and is recorded here so a later reader does not mistake this for an
  oversight: (a) the major defect is a *regression in failure mode* — the review's probe measured
  `Copying 1 image file(s)...` where two exist, both documents emitting the identical
  `image("images/diagram.png")`, `build succeeded` with no warning, where pre-PR `main` reported
  `Copying 2 image file(s)` and failed loudly as Issue #130; (b) reachability is not exotic —
  it needs only an image-conversion extension plus a `<srcdir>/images/` directory whose basename
  collides, and `images/` is the most common asset layout in Sphinx; (c) silent wrong output is the
  failure class this project's core value names directly; (d) `### Known Limitations` has precedent
  at `CHANGELOG.md:817`; and (e) the only open GitHub issue today is #91, so nothing external
  records these at all. Owner decision after all five points were on the table. Fixing them in
  Phase 46 was also rejected on consistency grounds — D-03 declined the `typst_authors` shim
  specifically to hold the prep-only fence, and a `typsphinx/builder.py` change here would
  contradict that. The minor defect (`relpath` returning `../` for a non-`doctreedir` absolute URI,
  measured to write outside `outdir`) travels with the major one.

- **D-28 [correction of record]: PR #131 is merged and ships in v0.7.1; `STATE.md` was right and D-17 was wrong.**
  Measured 2026-08-11: `gh pr view 131` → `state: MERGED`, `mergedAt: 2026-08-10T13:54:05Z`,
  `mergeCommit: 9b2b76b`, `baseRefName: main`; `gh issue view 130` → `state: CLOSED`;
  `git rev-parse origin/main` → `9b2b76b`, while the local `main` ref is stale at `87f242a`. The
  stale local ref is what made D-17's corroborating check ("`_track_image` appears in neither `main`
  nor the milestone branch") come out false-negative. `reviewDecision` is still
  `CHANGES_REQUESTED` — the PR was merged over an unresolved review, which is why D-27's two
  defects exist. Consequences: Phase 46 makes **no** correction to `STATE.md` on this point, and
  Issue #130 is closed rather than carried.

### Claude's Discretion

- The exact wording of the `[0.7.1]` entry, the lead paragraph's phrasing, which 6–8 bullets D-05
  resolves to, and how requirement IDs are attached.
- Which requirements land in `### Added` versus `### Changed` versus `### Fixed` (D-10 fixes only
  `typst_authors` → `### Removed`).
- The migration section's exact fragments and headings (D-09 fixes only that it exists, and which
  three items it must cover).
- Plan decomposition and ordering, and the `uv.lock` regeneration procedure (acceptance:
  `uv sync --extra dev --locked` green).
- The mechanical method for D-14's invariant sweep over the 119-file diff.
- The format and heading structure of `46-HANDOFF.md`.
- Where live-run evidence is recorded, subject to D-15.
- Whether the `RELEASE_VERSIONS` tuple in `tests/test_changelog_page_gate.py:49-63` gains `"0.7.1"`
  in this phase — the gate asserts each listed release appears in the built page, so adding it is
  mechanical but must not be done before the CHANGELOG entry exists.
- The exact form of D-22's repair at `tests/test_docs_contract_claims_gate.py:170` (`.as_posix()`
  on the `relative_to()` result is the obvious shape, but the planner owns it) and whether the
  `EXCLUDED_CLAIM_PAGES` literals move to the same normalisation.
- The compressed wording of D-24's PR #131 bullet, and exactly where `@christianwehe` sits in the
  trailing parentheses (D-25 fixes only that the credit is there and that it is in that slot).
- Whether the `## [0.7.1]` heading is created before or as part of resolving D-20's CHANGELOG
  conflict — either order reaches the same file.
- Which plan owns the merge, and whether D-22's repair rides in that plan or its own.

**Ordering interaction the planner must resolve:** D-09 adds migration fragments to
`docs/source/changelog.rst`, which is listed in `EXCLUDED_CLAIM_PAGES`. That page currently makes
*no* contract claim under the gate's scan — which is why the Windows failure includes a second
assertion calling the exclusion stale. Once D-09's fragments name published parameter names and
route tokens, the page will claim again and the exclusion becomes live. D-22's repair and D-09's
edit therefore interact; whichever lands second must be checked against the gate rather than
assumed green.

### Folded Todos

None. `todo.match-phase 46` returned keyword-noise matches only; see `<deferred>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's requirements and success criteria

- `.planning/ROADMAP.md` § "Phase 46: v0.7.1 Release Prep (prep-only)" — the five success criteria
  this phase is judged against, plus the milestone's five binding constraints.
- `.planning/REQUIREMENTS.md` § "Release and CI (REL)" — REL-06 and REL-04 verbatim, and the
  traceability rows that stay `Pending` through this phase.
- `.planning/STATE.md` § "Active Milestone (v0.7.1)" — the milestone invariants and the standing
  `--skip-ui` / api-coverage false-positive notes. **Contains one error corrected by D-17.**

### The release-prep precedent to follow

- `.planning/milestones/v0.7.0-phases/41-v0-7-0-release-automation-release-prep/41-CONTEXT.md` —
  the prep/publish fence, the version-literal census, the CHANGELOG-entry decision shape (D-01..D-05),
  and D-11's precedent for routing work into an inserted phase.
- `.planning/milestones/v0.7.0-phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md` —
  the handoff document shape SC#5 asks for.
- `.planning/milestones/v0.7.0-phases/41-v0-7-0-release-automation-release-prep/41-RELEASE-EVIDENCE.md`
  — the evidence-file shape, and the reason it is not named `41-VERIFICATION.md` (D-15).

### CHANGELOG source material handed forward by earlier phases

- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-03.md`
  § 7 — the quotable CHANGELOG source text for CONF-08, with the measured
  `index.typ` → `quickstartdefaultgate.typ` pair and the untemplated→templated structure change (D-07).
- `.planning/phases/45.1-custom-template-parameter-contract-correction/45.1-CONTEXT.md` § D-F —
  the instruction that Phase 46's CHANGELOG state the early-removal fact plainly (D-04), and
  § `<deferred>`, whose translations-repo handoff item D-13 retires.
- `.planning/phases/44.2-typst-documents-title-and-author-consumption/44.2-CONTEXT.md` — CONF-09's
  entry-resolution work, for the title/author callout.
- `CHANGELOG.md` — the `## [0.7.0]` entry as the structural model, and the tail link block that must
  roll over.
- `docs/source/changelog.rst` — the `.. include::` plus the hand-written "Migration Guides" tail
  (D-09's target).

### REL-04's in-phase share

- `.github/workflows/release.yml:147-190` — the `create-release` job. The `astral-sh/setup-uv` +
  `Set up Python` steps are present at `:162-168` (verified 2026-08-10), with an inline comment
  naming run `30848860064` as the failure they repair.
- `scripts/extract_changelog_section.py` — the extractor to exercise against `## [0.7.1]`.
- `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — REL-04's
  own record; stays pending until the publish.

### PR #131 and the `_track_image()` defects (added 2026-08-11)

- `origin/main` `9b2b76b` — the merge commit D-20 takes in. Its `CHANGELOG.md` `## [Unreleased]`
  block holds the 16-line `### Fixed` entry D-24 compresses.
- `typsphinx/builder.py` on `origin/main` — `TypstBuilder._track_image()` and
  `post_process_images()`, the code both deferred defects describe. **Not present in the local
  `main` ref, which is stale at `87f242a`** — read it via `git show origin/main:…`.
- `tests/test_absolute_image_render_gate.py` and `tests/fixtures/absolute_image_render_gate/`
  (both on `origin/main`) — PR #131's own gate, and the fixture a future collision regression test
  would extend.
- `.planning/todos/pending/2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md`
  — the major defect, with the measured probe transcript and two candidate fixes (D-27).
- `.planning/todos/pending/2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md`
  — the minor defect, with the three measured rehome outcomes (D-27).

### The Windows CI lane (added 2026-08-11)

- `tests/test_docs_contract_claims_gate.py:168-173` — `_discovered_claim_pages()`, D-22's repair
  site. Added by Phase 45.1 commit `a6fa38b`; absent from `v0.7.0`.
- `.planning/todos/pending/2026-08-11-windows-path-separator-breaks-contract-claims-gate.md` —
  the verbatim CI failure text from run `31445582363`, job `93638966551`. **Filed to
  `todos/completed/` at phase close, since D-22 resolves it.**
- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — why a bare
  local `tox` still cannot go green, and why D-11's local evidence is per-environment.

### Version-literal and gate surfaces

- `pyproject.toml:7` — the sole version literal.
- `README.md:342` — `**Status**: Stable (v0.7.0) - Production ready`.
- `tests/test_readme_version_sync.py` — asserts the two agree, so both must move together.
- `tests/test_preview_version_sync.py` — the `@preview` lockstep guard over `writer.py` /
  `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`.
- `tests/test_changelog_page_gate.py:49-63` — the `RELEASE_VERSIONS` tuple.

### Standing project constraints

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree `uv sync` + `uv run` for
  every executor. **Read alongside `<specifics>` items 1–5**, which measure why `uv run` is exactly
  what triggers the local test failures until Phase 45.2 lands.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — the surfaces D-14's sweep counts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `scripts/extract_changelog_section.py` — already committed and pytest-covered (Phase 41 D-06);
  Phase 46 only exercises it, it does not modify it.
- `tests/test_readme_version_sync.py` / `tests/test_preview_version_sync.py` — the established
  "a release-surface fact is pinned by pytest" pattern; both must stay green across the bump.
- `44-GATE-EVIDENCE-03.md` § 7 — pre-written CHANGELOG source text, so CONF-08's figures are quoted,
  not re-derived.
- `.envrc` + `flake.nix` (both git-tracked) — the devshell that provides the working nix-store `uv`.

### Established Patterns

- **Version literals:** `pyproject.toml:7` is the sole literal; `typsphinx.__version__` derives from
  `importlib.metadata`; `README.md:342` carries the human-readable status line; `uv.lock` moves in
  lockstep.
- **CHANGELOG entry shape:** lead paragraph → `### Added` / `### Changed` / `### Fixed` →
  `### Verified` → tail link block. `[0.7.0]`, `[0.6.5]`, `[0.6.4]`, `[0.6.3]` all follow it.
  D-02 inserts `### Removed` into that shape for the first time.
- **Evidence culture:** commands and their output transcribed verbatim; `human_needed` recorded
  honestly; the honest-verifier rule (abstain rather than assert without direct evidence).
- **Test-invocation convention:** newer gate modules invoke Sphinx as `sys.executable -m sphinx`
  and their docstrings state "NEVER `uv run sphinx-build`" with the exit-127 reason. 13 older test
  files still hard-code `["uv", "run", …]` — the inconsistency `<specifics>` item 5 measures.

### Integration Points

- The post-bump commit ↔ the branch CI run — D-11's evidence path. Requires the post-bump commit to
  be pushed, which is not an irreversible action and does not violate the prep/publish fence.
- `CHANGELOG.md` ↔ `docs/source/changelog.rst` ↔ `tests/test_changelog_page_gate.py` — one edit,
  three surfaces. The `.. include::` means the release history propagates automatically; only the
  migration section and the gate's version tuple are hand-maintained.
- `CHANGELOG.md` ↔ `release.yml` — the REL-04 link, live since Phase 41. The `## [0.7.1]` heading
  must exist and be non-empty before a tag is ever pushed, because the `validate` job checks it
  (Phase 41 D-09).
- Phase 46 ↔ Phase 45.2 — a cross-phase dependency introduced by D-18. **Discharged 2026-08-11:
  45.2 completed, so D-11's local-tox half is unblocked** (subject to D-11's amendment (b) — the
  `lint` env still cannot run locally).
- `origin/main` ↔ the milestone branch — D-20's merge. One conflicting file (`CHANGELOG.md`), and
  the conflict region is the same region D-05..D-10 rewrite.
- `tests/test_docs_contract_claims_gate.py` ↔ `docs/source/changelog.rst` — the gate scans that
  page and excludes it; D-09's migration fragments flip it from "makes no claim" back to "makes a
  claim", which is the ordering interaction recorded under Claude's Discretion.

</code_context>

<specifics>
## Specific Ideas

Everything below was measured during this discussion (2026-08-10) against the live tree or the
GitHub API, not inferred.

1. **`.venv/bin/uv` is a PyPI wheel binary, and it is unrunnable on this machine.**
   `file .venv/bin/uv` → `ELF 64-bit LSB pie executable, dynamically linked, interpreter
   /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32`. NixOS has no such loader, so any exec of it
   dies with `Could not start dynamically linked executable: uv` (stub-ld), exit 127. The
   dependency chain is `pyproject.toml:33 [project.optional-dependencies] dev` → `tox-uv>=1.35,<2`
   → `tox-uv 1.35.2 requires ['tox-uv-bare==1.35.2', 'uv<1,>=0.9.27']` → the `uv` wheel ships
   `bin/uv` and `bin/uvx`. **The project's recorded diagnosis — "`uv` not on PATH for subprocess
   children", "`uv: command not found`" — is wrong**; `uv` is on PATH, it is the wrong build of it.

2. **`tox` is completely non-functional locally.** `.venv/bin/tox -e lint --notest` →
   `lint: venv> .venv/bin/uv venv …` → `Could not start dynamically linked executable` →
   `lint: FAIL code 127`. `uv.find_uv_bin()` returns `.venv/bin/uv` and consults **no environment
   variable** (its whole source was read: it walks `sysconfig` script directories, `.venv/bin`
   first). So every `tox -e …` command in `CLAUDE.md` and `docs/source/contributing.rst` —
   including `docs-html` and `docs-pdf` — has never run on this machine.

3. **nixpkgs cannot substitute for it.** `nixpkgs#tox` does not exist; `nixpkgs#python3Packages.tox`
   is **4.34.1**, below the project's `tox>=4.56,<5` floor; `nixpkgs#python3Packages.tox-uv` does
   not exist. `tox.ini` requires `tox-uv~=1.35` and sets `runner = uv-venv-lock-runner` on every
   env, so tox alone cannot evaluate the file.

4. **`TOX_UV_PATH` repairs tox without touching the project** — `tox_uv/_venv.py:222-230` reads it
   *before* `find_uv_bin()` and passes it through `shutil.which()`, so an absolute path works.
   Measured: `TOX_UV_PATH=$(command -v uv) .venv/bin/tox -e lint --notest` → all 8 envs report
   `using uv from TOX_UV_PATH: /nix/store/…-uv-0.11.25/bin/uv`, `lint: OK`, `congratulations :)`.
   This is flake.nix-expressible as `TOX_UV_PATH = "${pkgs.uv}/bin/uv";`. **It repairs tox only** —
   it cannot reach the pytest failures, which are PATH resolution inside test subprocesses.

5. **The local test failures are caused by the same file, and removing it fixes them.** Measured
   pair over `tests/test_integration_advanced.py`, `test_integration_basic.py`,
   `test_integration_multi_doc.py`, `test_integration_nested_toctree.py`, both runs under an outer
   `uv run --no-sync pytest`:

   | state | result |
   |---|---|
   | as-is (`.venv/bin/uv` present) | **42 failed, 5 passed** |
   | `.venv/bin/uv` + `uvx` moved aside (= what Phase 45.2 produces) | **47 passed** |

   With the file absent the child process resolves `/nix/store/…-uv-0.11.25/bin/uv`. `uv run`
   prepends `.venv/bin` ahead of everything, which is why wrapping in `nix develop` does **not**
   help — measured: `nix develop -c uv run --no-sync python -c "shutil.which('uv')"` still returns
   `.venv/bin/uv`. Without an outer `uv run`, the same four files pass as-is, which is why the
   `.venv/bin/python -m pytest` habit works in the main tree and why worktrees (where `CLAUDE.md`
   mandates `uv run`) hit the failures.

6. **`tox-uv-bare` alone is sufficient.** Built a scratch venv containing `tox 4.58.0` +
   `tox-uv-bare 1.36.0` with no `uv` distribution and no `bin/uv`; temporarily set
   `tox.ini`'s `requires = tox-uv-bare~=1.35`; ran with `TOX_UV_PATH` unset:
   `lint: uv-sync> /nix/store/…-uv-0.11.25/bin/uv sync --locked …` → `lint: OK` → `EXIT=0`.
   `uv-venv-lock-runner` comes from `tox-uv-bare` (the registered plugin is literally
   `tox-uv-bare-1.35.2`), and `_venv.py`'s fallback branch documents "install tox-uv-bare and ensure
   system uv is in PATH" as a supported configuration. `tox.ini` was restored (`git diff` clean).
   **Limits of this measurement, stated honestly:** the scratch venv resolved versions the project's
   `uv.lock` does not pin; only `-e lint --notest` (the provisioning layer, which is where 127 died)
   was run, not a full `docs-pdf`; and the CI side (`uv run tox` after `astral-sh/setup-uv`) was not
   measured.

7. **`typst_authors` is gone without a trace.** Zero hits across `typsphinx/`, `docs/source/`,
   `examples/`, `tests/` — the input to D-03.

8. **The v0.7.0 → HEAD diff, for D-14.** 323 commits from merge-base `87f242a`; excluding
   `.planning/`, 119 files changed, +10,052 / −847. `pyproject.toml`'s only dependency movement is
   `myst-parser>=5.0` added to the `docs` extra (`:53`); `[project] dependencies` is untouched.

9. **Owner's framing across this discussion.** At every fork the owner chose the option that keeps
   the *release tree* honest over the one that is cheapest: `0.7.1` was kept but paid for with
   triple breakage marking; the `typst_authors` shim was declined specifically to hold the
   prep-only fence; and Phase 45.2 was pulled *into* the release rather than deferred, because a
   noisy local suite degrades the evidence SC#3 rests on.

---

### Measured 2026-08-11 (second discussion pass)

10. **The branch does not contain `origin/main`, and the merge is nearly trivial.**
    `git merge-base --is-ancestor origin/main HEAD` → false. `origin/main` is four commits ahead:
    `fa1ab88` (the fix), `b248ddd` (main merged into the PR branch), `fe284a7`, `9b2b76b` (the PR
    merge). Read-only dry run:

    ```
    $ git merge-tree --write-tree HEAD origin/main
    Auto-merging typsphinx/builder.py
    Auto-merging tests/test_builder.py
    CONFLICT (content): Merge conflict in CHANGELOG.md
    ```

    One conflicting file, and it is the file Phase 46 rewrites anyway.

11. **PR #131 is merged; the local `main` ref is stale.** `gh pr view 131` → `state: MERGED`,
    `mergedAt: 2026-08-10T13:54:05Z`, `mergeCommit: 9b2b76b`, `reviewDecision: CHANGES_REQUESTED`.
    `gh issue view 130` → `CLOSED`. `git rev-parse origin/main` → `9b2b76b` versus local
    `main` → `87f242a`. **The stale local ref is the mechanical cause of D-17's error**: the check
    "`_track_image` appears in neither `main` nor the milestone branch" queried a ref two commits
    behind the truth. `git show origin/main:typsphinx/builder.py | grep -c _track_image` → 4.

12. **The release anchor and the branch anchor differ by one commit.** `v0.7.0` resolves to commit
    `75fd8ed` (`git ls-remote` shows `7327d01`, the annotated-tag object, pointing to the same
    commit). Excluding `.planning/`: `v0.7.0..HEAD` → 126 files, +10,582 / −932;
    `87f242a..HEAD` → 125 files, +10,568 / −932. Both are **pre-merge** figures.

13. **SC#5's precondition holds right now.** `git tag -l v0.7.1` and
    `git ls-remote --tags origin v0.7.1` are both empty (measured 2026-08-11).

14. **The branch CI is red on Windows and nowhere else.** Run `31445582363`
    (`conclusion: failure`) job breakdown: `success` for `Lint and Format Check`, `Type Check`,
    `Code Coverage`, `Build Package`, `Integration Test - basic`, `Integration Test - advanced`,
    and all four ubuntu/macos test jobs; `failure` for `Test Python 3.12 on windows-latest` and
    `Test Python 3.13 on windows-latest` only.

15. **The Windows failure is this milestone's own.**
    `git log --diff-filter=A -- tests/test_docs_contract_claims_gate.py` → `a6fa38b`
    ("test(45.1-07): add permanent cross-page contract-claim guard");
    `git cat-file -e v0.7.0:tests/test_docs_contract_claims_gate.py` → absent. The offending
    expression is `str(page.relative_to(REPO_ROOT))` at `:170`.

16. **The CHANGELOG has an identifier convention but no attribution convention.** Zero hits for
    `Thanks` / `@handle` / `contributed`. Identifier precedent:
    `- **Seven dead documentation links … (DOC-09, DOC-10, Issue #119)**`,
    `- **… (PDF-01, Issue #117)**`, `- **Issue #114 — fatal figure/image bugs**`, and the 0.4.x
    `- **Issue #5**: … (PR #14)` form. `### Known Limitations` exists at `CHANGELOG.md:817`. The
    only open GitHub issue is **#91**.

17. **The major `_track_image()` defect made a loud failure silent.** From the 2026-08-10 review
    probe (73-byte real source image, 68-byte converted image, same basename):

    ```
    Copying 1 image file(s)...            ← two exist, one is tracked
    outdir/images/diagram.png = 68 byte   ← the converted image won
    index.typ:29  image("images/diagram.png")
    index.typ:37  image("images/diagram.png")
    build succeeded.                       ← no warning
    ```

    The same probe on pre-PR `main` reports `Copying 2 image file(s)` and fails loudly as Issue
    #130. Which image wins depends on `write_doc` order (roughly alphabetical docname).

</specifics>

<deferred>
## Deferred Ideas

- **A fail-loud shim for the removed `typst_authors`** — re-register the name and raise
  `ExtensionError` (or warn) when a `conf.py` still sets it, matching the `ELEMENTS_ALLOWLIST`
  stance that unknown configuration fails loudly rather than being dropped. Declined for v0.7.1 by
  D-03 to hold the prep-only fence. Kept as the option of record; the silent-loss failure mode is
  real and measured.

- **Unifying the 13 test files that hard-code `["uv", "run", "sphinx-build", …]` onto
  `sys.executable -m sphinx`** — the project's own documented convention, already applied to the
  newer gate modules. Phase 45.2 makes those files *work* (item 5) but does not make them
  *consistent*. A follow-up worth filing, not part of 45.2's dependency swap.

- **Raising `v0.8.0` instead of `0.7.1`** — argued in full and declined by D-01. Recorded here so a
  later reader does not mistake the patch number for an oversight.

- ~~**PR #131 / Issue #130 (absolute image URIs from `ImageConverter`/`ImageDownloader`)** — OPEN
  with `CHANGES_REQUESTED` (D-17). Out of v0.7.1.~~ **Retracted 2026-08-11 (D-28): merged, closed,
  and shipping in v0.7.1.** What is deferred instead is the pair below.

- **The two `TypstBuilder._track_image()` defects** (D-27) — deferred to a post-v0.7.1 phase, and
  now genuinely actionable, because the code is on `main` rather than in an unmerged PR:
  - *major* — a rehomed converted image keys to `images/<basename>` and collides with a real
    `<srcdir>/images/` image; the loser is never copied and both documents emit the same
    `image()` path, silently rendering the wrong picture with no warning. The record proposes two
    fixes (a reserved `_typst_converted/` namespace, or collision detection with suffix
    uniquification) and requires a regression test either way.
  - *minor* — `path.relpath(resolved_uri, self.doctreedir)` returns `../`-prefixed paths for any
    absolute URI outside `doctreedir`, and `copy_image_files()` joins it onto `outdir`, writing
    outside the build directory.

  The records themselves note these are naturally fixed together. **Not disclosed externally in
  v0.7.1** — no CHANGELOG `### Known Limitations` entry and no GitHub issue (D-27).

- **A `### Known Limitations` entry and a public GitHub issue for the above** — argued in full and
  declined by D-27. Recorded so a later reader does not mistake the silence for an oversight; the
  precedent (`CHANGELOG.md:817`) and the empty public issue tracker (only #91 open) were both on
  the table.

### Reviewed Todos (not folded)

`todo.match-phase 46` returned 7+ candidates, all keyword noise against a release-prep phase. The
ledger is **12** records as of 2026-08-11 (was 10). All are deferred per D-16 **except**
`2026-08-11-windows-path-separator-breaks-contract-claims-gate`, which D-22 resolves in this phase:

- `2026-07-22-add-sphinx-linkcheck-ci-job` — Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the links this release adds.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` — forbidden by `CLAUDE.md` and by
  the milestone's own constraint #6 until the todo itself lands.
- `2026-08-04-documented-custom-template-parameter-contract-is-wrong-and-t` — DOC-13's source
  record; delivered by Phase 45.1. Should be filed to `todos/completed/` rather than deferred —
  flagged for the planner to confirm against 45.1's artifacts.
- `2026-08-04-duplicate-typst-documents-target-silently-drops-a-master` — a `typst_documents`
  defect; note Phase 44's plan `44-05` added a target-name collision guard, so this record's
  current status is worth re-measuring before it is carried again.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end` — this **is** REL-04; stays pending
  until a real tag push runs `create-release` to completion.
- `2026-08-04-typst-documents-title-author-elements-ignored` — CONF-09's source record; delivered
  by Phase 44.2. Same filing question as DOC-13's record above.
- `2026-08-05-a-master-that-is-also-a-toctree-child-is-unrepresentable` — `typst_documents`
  modelling defect, unrelated to release prep.
- `2026-08-05-shared-document-silently-dropped-from-all-but-first-master` — the per-build-not-
  per-master include-dedup ledger defect.
- `2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir` and
  `2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` — both describe
  `TypstBuilder._track_image()`. **Amended 2026-08-11:** that code is on `origin/main` and ships in
  v0.7.1, so these are actionable — deferred by owner decision (D-27), not by impossibility.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` *(new)* — a `flake.nix`-side toolchain
  repair in the same family as QUA-04. Does not block SC#3, which takes lint from CI (D-11
  amendment (b)).
- `2026-08-11-windows-path-separator-breaks-contract-claims-gate` *(new)* — **not deferred**;
  D-22 fixes it in this phase and it is filed to `todos/completed/` at phase close.

</deferred>

---

*Phase: 46-v0-7-1-release-prep-prep-only*
*Context gathered: 2026-08-10; updated 2026-08-11 (second discussion pass, D-20..D-28)*
