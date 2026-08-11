# Phase 46: v0.7.1 Release Prep (prep-only) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-10
**Phase:** 46-v0-7-1-release-prep-prep-only
**Areas discussed:** Version number and breakage framing, CHANGELOG entry shape and migration guide,
Green-tree evidence scope, Close-out disposition of open items

---

## Version number and breakage framing

### Q1 — Ship under the version number 0.7.1 as planned?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep 0.7.1 | ROADMAP SC#1 fixes it; owner declined v0.8.0 on 2026-08-04; project precedent (0.6.2 / 0.6.3) allows breaking config removal in a patch; zero cost since milestone name, branch, ROADMAP, REQUIREMENTS and STATE already agree | ✓ |
| Raise to 0.8.0 | The 2026-08-04 judgment predates CONF-10/11/12 (added 2026-08-10); the precedent's removed values were all **inert** whereas `typst_authors` is live and CONF-11 changes output with no error; Phase 44.2 published a "future major release" removal notice | |

**User's choice:** Keep 0.7.1
**Notes:** All three counter-arguments were presented with their measurements before the choice.
Recorded as D-01, with the explicit consequence that the CHANGELOG becomes the only surface carrying
the warning — which is what Q2 then decides.

### Q2 — How strongly is breakage marked in the CHANGELOG?

| Option | Description | Selected |
|--------|-------------|----------|
| lead declaration + per-bullet `**Breaking:**` + a new `### Removed` section | Triple marking; `changelog.rst`'s migration guide already uses `**Breaking:**` so vocabulary matches across the two surfaces | ✓ |
| lead declaration only | The Phase 41 D-03 shape — but that was justified by the measured fact that nothing broke, a premise that does not hold here | |
| per-bullet markers only | Keeps the heading structure unchanged, but leaves a public config value's disappearance without its own heading | |

**User's choice:** lead declaration + per-bullet Breaking + Removed section
**Notes:** Recorded as D-02. `### Removed` is new to this CHANGELOG.

### Q3 — Act on the silent failure of a leftover `typst_authors` before release?

| Option | Description | Selected |
|--------|-------------|----------|
| Documentation only — hold the prep-only fence | No code change; the CHANGELOG `### Removed` entry and the migration guide carry the notice | ✓ |
| Insert Phase 45.2 with a fail-loud shim | Matches the `ELEMENTS_ALLOWLIST` stance that unknown configuration fails loudly, at the cost of one more phase before the release | |
| Take the shim inside Phase 46 (D-12 precedent) | Phase 41 took one docstring fix in-phase — but that changed no behaviour, whereas this would, enlarging SC#3's own proof obligation | |

**User's choice:** Documentation only
**Notes:** Recorded as D-03. Measured input: `typst_authors` returns zero hits across `typsphinx/`,
`docs/source/`, `examples/`, `tests/`, and Sphinx ignores an unregistered `conf.py` variable without
warning — so the loss is silent. The shim is preserved as the option of record in `<deferred>`.

### Q4 — Where is the published-notice contradiction stated?

| Option | Description | Selected |
|--------|-------------|----------|
| Fact in the CHANGELOG `### Removed` bullet; rationale and rewrite steps in the migration guide | The CHANGELOG reaches the GitHub Release body, so the fact travels furthest; the how-to lives where an upgrader looks | ✓ |
| CHANGELOG only | Self-contained, but lengthens the bullet and unbalances it against the other callouts | |
| Migration guide only | Reaches upgraders but not readers of the GitHub Release | |

**User's choice:** CHANGELOG fact + migration-guide rationale
**Notes:** Recorded as D-04. Discharges 45.1 D-F's explicit instruction.

---

## CHANGELOG entry shape and migration guide

### Q1 — Bullet granularity for `## [0.7.1]` (18 v1 requirements)?

| Option | Description | Selected |
|--------|-------------|----------|
| user-visible granularity, 6–8 bullets, requirement IDs in trailing parentheses | Continues Phase 33 D-09 / Phase 41 D-01; reads consistently with `[0.7.0]` and `[0.6.5]` | ✓ |
| one bullet per requirement (18) | Full traceability, but puts QUA-01's docstring fix and QUA-03's planning-document hygiene into release notes | |
| phase-level roll-up (7) | Short, but phase boundaries are an internal partition users cannot see, and CONF-11 gets buried inside "Phase 45.1" | |

**User's choice:** user-visible granularity, 6–8 bullets
**Notes:** Recorded as D-05.

### Q2 — What is the lead paragraph's axis?

| Option | Description | Selected |
|--------|-------------|----------|
| "the configuration the documentation promises actually takes effect" | The project's own core-value sentence; covers CONF-08, CONF-09 and DOC-13/CONF-11/CONF-12 at once | ✓ |
| "v0.7.0's debts cleared" | The milestone-goal wording — accurate but told from the project's side | |
| lead with the breaking-change warning | Unmissable, but buries the fact that this release mostly repairs things that were broken | |

**User's choice:** documented configuration actually takes effect
**Notes:** Recorded as D-06. D-02's breakage declaration still sits in the same paragraph.

### Q3 — Add a "Migrating from 0.7.0 to 0.7.1" section to `docs/source/changelog.rst`?

| Option | Description | Selected |
|--------|-------------|----------|
| Add it with before/after `conf.py` and template fragments | Three items need fragments: `typst_authors` → `params`; a `params`-setting project must now enumerate all nine parameters; a template not declaring `lang` starts failing. Code fragments would enter this page for the first time | ✓ |
| Add it as prose bullets only | Matches the existing sections' form but cannot convey "write all nine" | |
| Do not add it | Incoherent immediately after D-02's triple marking | |

**User's choice:** Add it with before/after examples
**Notes:** Recorded as D-09. Measured: the page is `.. include:: ../../CHANGELOG.md` plus a
hand-written "Migration Guides" tail, so this section is the only hand-written surface and is what
ROADMAP SC#2's "gains the matching 0.7.1 entry" actually resolves to.

### Q4 — What does `### Verified` carry, given `myst-parser` was added to the docs extra?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the same three items, wording the first as "no new **runtime** dependencies" | Keeps the claim true and pre-empts a reader who diffs `uv.lock` | ✓ |
| Keep three and list `myst-parser` as a fourth | Honest, but the section exists to enumerate what did *not* change | |
| Drop the section | The last three releases all carry it; absence would read as a regression | |

**User's choice:** three items, dependency claim scoped to runtime
**Notes:** Recorded as D-08. Measured: `pyproject.toml:53` adds `myst-parser>=5.0` to the `docs`
extra (a Phase 45 / DOC-12 consequence); `[project] dependencies` is untouched.

---

## Green-tree evidence scope

> This area was interrupted twice for clarification and expanded into a substantial measurement
> session on the local toolchain. The investigation is recorded in CONTEXT.md `<specifics>` 1–6; the
> alternatives considered are below.

### Q1 — How deep is the `ja` build evidence?

| Option | Description | Selected |
|--------|-------------|----------|
| One `SPHINX_LANGUAGE=ja` docs-pdf build | CONF-12 changed the route by which `lang` reaches a template, so `ja` should not go unexercised — but Phase 41's triggers do not recur | ✓ |
| Re-run Phase 41's full four-check glyph bar | Safest, but pays that cost with none of its triggers present | |
| Skip `ja` entirely | Cheapest; a break would surface only after publication | |

**User's choice:** single `SPHINX_LANGUAGE=ja` docs-pdf build
**Notes:** Recorded as D-12. Measured inputs: `raw(` call sites are **41 before and 41 after**
(`git show main:typsphinx/translator.py` vs. the working tree) and the milestone diff names no font
family — so both facts that justified Phase 41's bar are absent. Separately measured and recorded as
D-13: `typsphinx-doc-translations` contains **no `conf.py` and no `.typ` template** (its tree is
`.readthedocs.yaml`, `Makefile`, `locale/ja/**`, plus the parent as a submodule), which retires
45.1's translations-repo handoff item.

### Q2 — Where does the authority for "green" sit?

| Option | Description | Selected |
|--------|-------------|----------|
| Branch CI is the authority; local `tox` supplies what CI does not run | The branch is already on `origin` (invariant #5); the CI run is live, not inherited, and includes the Windows lanes that caught a real cp1252 defect at the v0.7.0 close | ✓ |
| Promote the local run to the authority | Attractive once 45.2 removes the noise, but never sees Windows or macOS | |
| Require both full green runs | Strictest; largest pre-release wait for the least new information | |

**User's choice:** branch CI primary, local supplementary
**Notes:** Recorded as D-11. Re-confirmed after the Phase 45.2 decision, since 45.2 is what makes
the local half executable at all.

### Q3 — When does the `tox-uv` → `tox-uv-bare` repair land?

| Option | Description | Selected |
|--------|-------------|----------|
| Insert Phase 45.2 and land it before the release | Raises the quality of the evidence SC#3 collects; costs a dependency and lockfile move shortly before the release phase | ✓ |
| After Phase 46, at the head of v0.7.2 | Leaves the release tree untouched | |
| Immediately, outside any GSD phase | Fastest, but the evidence baseline still moves mid-discussion | |

**User's choice:** Insert Phase 45.2 before the release
**Notes:** Recorded as D-18. The alternative repair (`TOX_UV_PATH` in `flake.nix`) was measured
working and rejected as insufficient: it fixes `tox` but not the test failures, and it is a
NixOS-local workaround rather than a fix. The decisive measurements: 42 failed → 47 passed with
`.venv/bin/uv` moved aside, and `tox -e lint --notest` green under `tox-uv-bare` alone with no
`TOX_UV_PATH`. **Inserting the phase is a separate `/gsd-phase` action, not Phase 46 work.**

### Q4 — Does Phase 45.2's change get a `## [0.7.1]` CHANGELOG bullet?

| Option | Description | Selected |
|--------|-------------|----------|
| No — dev extra only | Changes nothing for a user *of* typsphinx; consistent with the 0.6.5-era rule that dev/verification machinery is not user-visible | ✓ |
| Yes — contributors installing via `pip install -e ".[dev]"` no longer get uv automatically | Formally true, but `contributing.rst:117-128` instructs `uv run tox …` everywhere, so the documented path already requires uv | |

**User's choice:** No bullet
**Notes:** Recorded as D-19. The owner raised the counter-consideration themselves (that bundling
uv helps non-nix users who venv via poetry); measured answer: `poetry` appears nowhere in the
repository, and under `tox-uv-bare` the affected user gets tox-uv's own three-option error message
rather than a silent failure.

---

## Close-out disposition of open items

### Q1 — How are the open items handled at the close?

| Option | Description | Selected |
|--------|-------------|----------|
| Defer all 10 todos with reasons recorded; PR #131 waits for the next round; correct `STATE.md` | The Phase 41 D-14 shape | ✓ |
| Consider pulling PR #131 into v0.7.1 | Issue #130 breaks builds for converted/downloaded images — but the review's two findings are unfixed, so it would need another phase | |

**User's choice:** Defer all; PR #131 to the next round
**Notes:** Recorded as D-16 and D-17. Measured: `gh pr view 131` reports `state: OPEN`,
`mergedAt: null`, one review `CHANGES_REQUESTED` — contradicting `STATE.md`'s claim that it was
merged. Corroborated by `_track_image` being absent from both `main` and the milestone branch.

---

## Claude's Discretion

- Exact wording of the `[0.7.1]` entry, the lead paragraph's phrasing, and which 6–8 bullets D-05
  resolves to.
- Which requirements land in `### Added` / `### Changed` / `### Fixed` (D-10 fixes only
  `typst_authors` → `### Removed`).
- The migration section's exact fragments and headings.
- Plan decomposition and ordering; the `uv.lock` regeneration procedure.
- The mechanical method for D-14's invariant sweep over the 119-file diff.
- The format of `46-HANDOFF.md`, and where live-run evidence is recorded (subject to D-15).
- Whether `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` tuple gains `"0.7.1"` this phase.

## Deferred Ideas

- A fail-loud shim for the removed `typst_authors` (declined by D-03; option of record).
- Unifying the 13 test files that hard-code `["uv", "run", "sphinx-build", …]` onto
  `sys.executable -m sphinx` — Phase 45.2 makes them work but not consistent.
- Raising `v0.8.0` instead of `0.7.1` (argued and declined by D-01).
- PR #131 / Issue #130, and the two todos its review filed against code that exists only on the PR
  branch.
- All 10 records in `.planning/todos/pending/`, enumerated with reasons in CONTEXT.md `<deferred>`.
  Two of them (DOC-13's and CONF-09's source records) look already-delivered and are flagged for the
  planner to confirm and file to `todos/completed/`.

---
---

# Second discussion pass

**Date:** 2026-08-11
**Trigger:** existing CONTEXT.md offered for update; four premises had changed since 2026-08-10 —
Phase 45.2 completed, `origin/main` advanced to `9b2b76b` (PR #131 merged), the branch CI went RED
on the Windows lanes, and the pending-todo ledger grew from 10 to 12 records.
**Areas discussed:** origin/main merge, Windows CI RED, PR #131 CHANGELOG integration,
`_track_image()` defects

---

## Context handling

| Option | Description | Selected |
|--------|-------------|----------|
| Update it | Keep D-01..D-19 locked, re-discuss only the changed premises | ✓ |
| Use as-is (skip) | Go straight to `/gsd-plan-phase 46`; planner absorbs the drift | |
| View it | Walk each section before deciding | |

**Notes:** Presented with the five measured drift points first, including the fact that D-17's
"correction of record" was itself wrong.

---

## origin/main merge

| Option | Description | Selected |
|--------|-------------|----------|
| Merge at head of Phase 46 | Before bump and CHANGELOG; SC#3's tree == the tagged tree | ✓ |
| Merge with the CHANGELOG plan | One pass, but crosses `uv.lock` regeneration with the merge | |
| Rebase onto origin/main | Linear history, but rewrites 371 commits and force-pushes | |
| Defer to `/gsd-complete-milestone` | Resolves the CHANGELOG conflict inside the irreversible half | |

**Notes:** `git merge-tree --write-tree HEAD origin/main` was run read-only first — one conflict
(`CHANGELOG.md`), `typsphinx/builder.py` and `tests/test_builder.py` auto-merge clean. → **D-20**

| Option | Description | Selected |
|--------|-------------|----------|
| Anchor SC#4 at the `v0.7.0` tag (`75fd8ed`) | Swept diff == what a v0.7.0 user receives | ✓ |
| Keep `87f242a` | D-14 as written; one commit off the tag | |
| Record both | 1 file / 14 lines apart — redundant | |

**Notes:** → **D-21**, superseding D-14.

---

## Windows CI RED

| Option | Description | Selected |
|--------|-------------|----------|
| Fix inside Phase 46 | One line in a test module; no `typsphinx/` change, fence holds | ✓ |
| Insert Phase 46.1 | The Phase 45.2 procedure applied to a one-line change | |
| Exclude as known RED | Contradicts D-11's own justification for CI being the authority | |

**Notes:** Run `31445582363` breakdown shown — only the two `windows-latest` jobs fail. The gate was
traced to Phase 45.1's commit `a6fa38b` and confirmed absent from `v0.7.0`, i.e. a regression this
milestone introduced. → **D-22**

| Option | Description | Selected |
|--------|-------------|----------|
| Two CI runs: check then authority | Run 1 proves Windows green (unverifiable on NixOS); run 2 is SC#3 | ✓ |
| One combined run | Single wait, but a missed repair surfaces after the bump | |
| Three separated runs | Full causal separation; a third wait buys nothing | |

**Notes:** Local `ruff` is unrunnable on NixOS, so a bare `tox` still cannot go green locally; D-11
already assigns lint/type/pytest to CI, so this narrows the local evidence rather than weakening
SC#3. → **D-23**, D-11 amendment (b)

---

## PR #131 CHANGELOG integration

| Option | Description | Selected |
|--------|-------------|----------|
| Compress to house granularity | ~14 lines → 3–5, matching `[0.7.0]`'s `### Fixed` bullets | ✓ |
| Move verbatim | Respects the contributor's text; ~3× everything around it | |
| Rewrite from scratch | Most consistent; discards the contributor's own account | |

**Notes:** → **D-24**. Makes PR #131 the sixth user-visible change, filling one of D-05's 6–8 slots.

| Option | Description | Selected |
|--------|-------------|----------|
| Credit `@christianwehe` in the trailing parentheses | First external contribution; sets the precedent | ✓ |
| Issue/PR number only | Matches existing form exactly; renders the contributor anonymous | |
| New `### Contributors` section | A second brand-new section alongside D-02's `### Removed` | |

**Notes:** Measured that the CHANGELOG has no attribution precedent at all (zero `Thanks` / `@` /
`contributed`) but does have a `(PR #14)`-style trailing slot from the 0.4.x era. → **D-25**

| Option | Description | Selected |
|--------|-------------|----------|
| `Issue #130` only; leave REQUIREMENTS.md alone | Coverage stays 19/19, zero orphans | ✓ |
| Mint a new requirement mapped to Phase 46 | Full traceability; attributes work Phase 46 didn't do | |
| Footnote on the coverage line | Bookkeeping for a fact the CHANGELOG already states | |

**Notes:** → **D-26**

---

## `_track_image()` defects

| Option | Description | Selected |
|--------|-------------|----------|
| Insert Phase 46.1 and fix both | The Phase 45.2 precedent; keeps Phase 46 prep-only | |
| Ship in v0.7.1, defer | Faster release; converter users get silent wrong images | ✓ |
| Fix inside Phase 46 | Fastest; contradicts D-03's reason for declining the `typst_authors` shim | |
| Drop PR #131 from v0.7.1 | Reverts a merged external contribution; Issue #130 stays unfixed | |

**Notes:** The full counter-case was put before the choice — the review probe transcript showing
`Copying 1 image file(s)` / identical `image()` paths / `build succeeded` with no warning, the fact
that pre-PR `main` failed *loudly* on the same shape, and that `images/` is Sphinx's most common
asset layout. Owner chose to ship. → **D-27**

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub issue + CHANGELOG `### Known Limitations` | Converter users learn before upgrading | |
| CHANGELOG only | Visible in release notes, nowhere to track | |
| Internal only (todo + `46-HANDOFF.md`) | Nothing external; release notes show #131 as fixed | ✓ |

**Notes:** `### Known Limitations` precedent at `CHANGELOG.md:817` and the near-empty public issue
tracker (only #91 open) were both presented. Owner chose internal-only. → **D-27**

---

## Claude's Discretion (added this pass)

- The exact form of the `tests/test_docs_contract_claims_gate.py:170` repair, and whether
  `EXCLUDED_CLAIM_PAGES` moves to the same normalisation.
- The compressed wording of the PR #131 bullet and where the credit sits in its parentheses.
- Whether `## [0.7.1]` is created before or during the merge-conflict resolution.
- Which plan owns the merge, and whether the Windows repair rides along or gets its own.
- Resolving the D-09 ↔ contract-claims-gate ordering interaction on `docs/source/changelog.rst`.

## Deferred Ideas (added this pass)

- Both `TypstBuilder._track_image()` defects — now actionable (the code is on `main`), deferred by
  owner decision rather than by impossibility.
- A public `### Known Limitations` entry and a GitHub issue for them — argued and declined.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos` — a `flake.nix`-side repair in the QUA-04
  family; does not block SC#3.

## Corrections of record (this pass)

- **D-17 retracted.** PR #131 is MERGED (`9b2b76b`, `2026-08-10T13:54:05Z`) and Issue #130 is
  CLOSED. `STATE.md` was right; the 2026-08-10 measurement predated the merge, and its
  corroborating check queried a local `main` ref stale at `87f242a`. Phase 46 makes no `STATE.md`
  correction on this point. → **D-28**
- **D-11's Phase 45.2 dependency discharged** — 45.2 completed 2026-08-11.
- **D-16's ledger corrected** — 12 pending records, not 10, one of which this phase resolves.
