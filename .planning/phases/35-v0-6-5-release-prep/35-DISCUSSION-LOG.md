# Phase 35: v0.6.5 Release Prep - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 35-v0.6.5 Release Prep
**Areas discussed:** CHANGELOG wording, handling of the four Phase 34 review Warnings,
handoff to `/gsd-complete-milestone`, release-page bloat (raised by the user),
scope of SC#3 live-run evidence

**Offered but not selected:** none — three of four offered areas were selected, and SC#3 was
discussed at the end as an addition.

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG wording | How to write up the divergence between the reported shape and the shapes measured broken | ✓ |
| Handling of the four Phase 34 review Warnings | Pick them up or park them | ✓ |
| Handoff to complete-milestone | Handoff document and two-repository tagging | ✓ |
| Scope of SC#3 live-run evidence | Whether to add the docs builds | ✓ (added at the end) |

---

## CHANGELOG wording

### Q1: At what granularity should `### Fixed` describe what was broken?

| Option | Description | Selected |
|--------|-------------|----------|
| Enumerate the contexts | Spell out bullet-list items / definition-list terms / field values. Easy to self-diagnose against, but long | |
| General sentence only | Just "inline math immediately after text used to fail." Reads broader than reality | |
| General sentence + parenthetical examples | "inline math immediately after text (in bullet-list items, definition-list terms, and the like)" | ✓ |

**Notes:** Measured — fixture Construct A (top-level paragraph, including the no-space form) was
already green before the fix; B–F were the red ones. That divergence is the premise of the question.

### Q2: Should display math (inside a list item) be a separate item?

| Option | Description | Selected |
|--------|-------------|----------|
| Same item | One bullet covering both inline and display. The D-09 granularity rule | ✓ |
| Separate bullet | It was an untracked defect, so show it as an independent fix | |

### Q3: Section structure of `## [0.6.5]`

| Option | Description | Selected |
|--------|-------------|----------|
| Lead + Fixed + Verified | Follows the 0.6.1 / 0.6.3 / 0.6.4 precedent | ✓ |
| Lead + Fixed only | Minimal, hotfix-sized | |
| Fixed only (no lead) | Diverges in form from every past entry | |

### Q4: What goes in `### Verified`?

| Option | Description | Selected |
|--------|-------------|----------|
| Two invariants + corpus gate | Zero new deps / `@preview` unbumped / full corpus fatal-free | ✓ |
| The above + the fixture's RED→GREEN | Shows the GATE-01 bar externally | |
| Two invariants only | The strict version of Phase 33 D-03 | |

**User's choice:** recorded in CONTEXT as D-01–D-04. Exact wording at Claude's discretion.

---

## Handling of the four Phase 34 review Warnings

### Q1: How much to pick up

| Option | Description | Selected |
|--------|-------------|----------|
| Park all four (file as todos) | Faithful to the minimal-hotfix policy; fastest release | |
| Pick up the three test-side ones | WR-02/03/04 leave `typsphinx/` untouched, so invariant #3 is safe | ✓ |
| Pick up all four | Also fix WR-01. A second translator change forces re-running GATE-01 and the corpus gate | |

### Q2: How to close WR-02

| Option | Description | Selected |
|--------|-------------|----------|
| Add Construct G to the existing fixture | No extra builds; consolidated with the existing six constructs | ✓ |
| Separate fixture / separate test | Leaves existing output untouched but adds two more `sphinx-build` runs | |

### Q3: How the test additions sit within the phase

| Option | Description | Selected |
|--------|-------------|----------|
| Independent plan before the version bump | Recorded in CONTEXT as work outside REL-03's scope | ✓ |
| Add one success criterion to the ROADMAP | Makes it a verify target but widens the phase boundary officially | |

**User's choice:** D-05–D-07. WR-01 is filed as a todo (D-10 has Phase 35 write the todo file).

---

## Handoff to `/gsd-complete-milestone`

### Q1: Keep the two-repository tagging standing cost (v0.6.4 D-07)?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep it (tag both again) | Preserves `/ja/stable/` and `/en/stable/` pointing at the same version | ✓ |
| Skip it this time | `docs/` unchanged, so omit. Would carve an exception into the standing cost | |

**Notes:** Measured — the translations repo carries only `v0.6.4`, and RTD's en `stable` is likewise
tag `v0.6.4` (identifier `2bf6ef3`). This milestone's `docs/` diff is empty.

### Q2: Where does the handoff live?

| Option | Description | Selected |
|--------|-------------|----------|
| A dedicated `35-HANDOFF.md` | The Phase 33 precedent; complete-milestone reads one file | ✓ |
| A section inside SUMMARY / VERIFICATION | Minimal, adds no files | |
| Don't write one | Rely on the ROADMAP note and the standing decision | |

### Q3: Which side does the bookkeeping?

| Option | Description | Selected |
|--------|-------------|----------|
| WR-01 todo in 35, REL-03 at close | Record the not-picked-up decision now; flip the checkbox post-publish | ✓ |
| Everything in Phase 35 | Flip REL-03 to `[x]` ahead of the publish | |
| Everything at close | Phase 35 sticks to bump + CHANGELOG + tests + HANDOFF | |

**User's choice:** D-08–D-10.

---

## Release-page bloat (raised by the user)

**Raised:** "The release page for the next version lists every single commit, so with this many
commits it gets absurdly long. I want it compact."

**Measured facts presented back:** the v0.6.4 release body is 308 lines. Lines 1–296 are the commit
dump from `release.yml`'s "Generate release notes" step
(`git log $PREV_TAG..$TAG --pretty="- %s (%h)"`); lines 297–303 are Installation; lines 304–308 are
GitHub's own output from `generate_release_notes: true` (a one-line "What's Changed" PR entry plus the
Full Changelog link). The auto-generated part is already compact — the bloat is the hand-rolled
`git log` block. It also came out that `release.yml` never reads `CHANGELOG.md`, so the Phase 33
CONTEXT claim that the CHANGELOG entry is the single source for the Release body contradicts reality.

### Q1: Fix `release.yml` inside Phase 35?

| Option | Description | Selected |
|--------|-------------|----------|
| Fix it in Phase 35 | v0.6.5 onward gets compact. But the workflow only runs on a tag push | |
| Skip for v0.6.5, file a todo | Keeps the minimal-hotfix policy; this milestone is 33 commits, shorter than v0.6.4's | ✓ |

### Q2: If fixed, what shape should the body take? (recorded as the todo's design direction)

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG extract + Installation + auto-generated | Drop `git log`, extract the `## [X.Y.Z]` section. What's Changed and Full Changelog remain | ✓ |
| Auto-generated + Installation only | Simplest, but the curated prose never appears on the release page | |
| Filter the commit list | Exclude `docs(` / `chore(`. A brittle mechanism dependent on prefix conventions | |

**User's choice:** D-11 — skip for v0.6.5 and record the design direction (the CHANGELOG-extract
approach) in the todo.

---

## Scope of SC#3 live-run evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Also run the docs builds | Add `tox -e docs-html` / `docs-pdf`. The Phase 28 D-05 precedent | ✓ |
| Only the three SC names | `docs/` did not change by a line this milestone | |

**User's choice:** D-12.

---

## Claude's Discretion

- The exact wording of the `[0.6.5]` CHANGELOG entry, the lead paragraph, and requirement-ID placement
- The exact assertion strings for WR-02/03/04 and the reST for Construct G
- Plan decomposition within the phase (D-07 fixes only the ordering)
- The format and heading structure of `35-HANDOFF.md`
- The `uv.lock` regeneration procedure
- The wording, frontmatter, and filenames of the two todo files
- Where live-run evidence is recorded (`35-VERIFICATION.md` is reserved by the verifier — avoid it)

## Deferred Ideas

- **WR-01**: `visit_math_block`'s redundant blank line (`typsphinx/translator.py:4079-4088`) → todo
- **Reworking `release.yml`'s release body** (CHANGELOG-extract approach) → todo, v0.6.6+
- **The three 30.1-review Warnings** — already excluded by REQUIREMENTS § Out of Scope
- **The five pending todos** — same (returned by `todo.match-phase 35`, but folding was not
  re-litigated since it is already decided)
