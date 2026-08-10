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
