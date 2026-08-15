# Phase 52: v0.8.0 Release Prep (prep-only) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-15
**Phase:** 52-v0-8-0-release-prep-prep-only
**Areas offered:** deferred-defect disclosure, SC#3 "green" authority, goal-claim PDF evidence,
`## [0.8.0]` entry shape
**Areas selected and discussed:** deferred-defect disclosure, `## [0.8.0]` entry shape

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Deferred-defect disclosure | Whether the four minor defects Phases 48/49/50 filed against themselves are published (CHANGELOG `### Known Limitations`, GitHub issues) or kept internal | ✓ |
| SC#3 "green" authority | CI (push 155 commits + `workflow_dispatch`) versus local per-environment runs as the authority for pytest/lint/type | |
| Goal-claim PDF evidence | Permanent `tests/` gate versus one-off evidence run; reuse `state_guard_three_master_gate` versus a new fixture | |
| `## [0.8.0]` entry shape | Breaking-change marking strength, bullet granularity, section structure, lead-paragraph axis | ✓ |

**Notes:** The two unselected areas were recorded in CONTEXT.md as derived decisions (D-08, D-09,
D-10) following the 46-CONTEXT D-11 and 51-CONTEXT D-10 precedents, with the defaults stated back
to the user before they chose to proceed.

---

## Deferred-defect disclosure

### Q1 — How far outward are the four minor defects disclosed?

Context given before the question: all four are `severity: minor`; reachability conditions measured
(docname containing `#`/`>`; a docname colliding with another's `/`→`_u2f_` transform; a 1000+ deep
include chain; two escaping absolute image URIs sharing a basename). The v0.7.1 comparison was put
explicitly — D-27 kept **major** defects silent whose reachability was the most common Sphinx asset
layout — as was the distinguishing fact that all four here are new failure classes created by
features this milestone shipped.

| Option | Description | Selected |
|--------|-------------|----------|
| Internal only (D-27 shape) | Stay in `todos/pending/`, listed in the handoff; no CHANGELOG entry, no GitHub issue | ✓ |
| List in the CHANGELOG | New `### Known Limitations` section in `## [0.8.0]` (precedent `CHANGELOG.md:817`), reaching the GitHub Release body | |
| File GitHub issues | Public issues for traceability, optionally referenced by number from the CHANGELOG (only #91 is open today) | |

**User's choice:** Internal only. → **D-01**

### Q2 — Where do the two documented behaviours go in `## [0.8.0]`?

Context given: ROADMAP SC#2 requires Phase 49's measured-and-documented limitations to appear in
the CHANGELOG, and Phase 51 documented exactly two (standalone content file yields only its own
body; a shared child's heading level varies per master). 51-CONTEXT D-08 deliberately wrote the
first as prose rather than a `.. note::` so it reads as intended behaviour.

| Option | Description | Selected |
|--------|-------------|----------|
| Fold into descriptive bullets | Written inside the output-shape / composition bullets, preserving D-08's non-warning tone | ✓ |
| Own `### Known Limitations` section | Collect the two under a limitations heading — conflicts with D-08's "not a limitation" judgement | |
| Docs link only | Say nothing in the CHANGELOG; link to `output_layout.rst`. Would not reach a GitHub Release reader | |

**User's choice:** Fold into descriptive bullets. → **D-02**

### Q3 — By what route do the deferred records reach the next milestone?

Context given: the ROADMAP `## Backlog` has been empty since 2026-08-04 and would next number
`999.3`, but v0.8.0's own scope was assembled directly from `todos/pending/` at
`/gsd-new-milestone`.

| Option | Description | Selected |
|--------|-------------|----------|
| Todo ledger as-is | Stay in `todos/pending/`, enumerated with reasons in the handoff and CONTEXT `<deferred>` (D-16 shape) | ✓ |
| Promote to backlog `999.x` | Numbered ROADMAP backlog entries — harder to lose, but a second ledger for the same records | |
| Todos + PROJECT.md "Next" | Name them as next-milestone candidates in PROJECT.md, which is normally written by phase-complete / milestone close | |

**User's choice:** Todo ledger as-is. → **D-03**

---

## `## [0.8.0]` entry shape

### Q1 — How strongly are breaking changes marked?

Context measured before the question: the milestone diff contains **zero** `add_config_value`
additions or removals, so v0.7.1's third marking channel (`### Removed`) has no candidate; three
output changes are breaking, and the third (collision hard error) stops a build that used to
succeed for the most common configuration shape.

| Option | Description | Selected |
|--------|-------------|----------|
| Lead declaration + `**Breaking:**` | v0.7.1's triple marking minus the inapplicable `### Removed`; reuses the same vocabulary | ✓ |
| Add a dedicated section | Also create `### Breaking Changes` and collect the three there — a second never-before-used heading | |
| Lead declaration only | Phase 41 D-03 shape; reads the minor bump as sufficient signal under sub-1.0 SemVer | |

**User's choice:** Lead declaration + `**Breaking:**`. → **D-04**

### Q2 — What is the lead paragraph's axis?

Context given: v0.7.1's D-06 refused to lead with the breaking-change warning so repairs would not
be buried; here the asymmetry is different — the output-shape change lands on every user, while the
multi-master repairs only reach projects declaring more than one master.

| Option | Description | Selected |
|--------|-------------|----------|
| Multi-master now works | The milestone goal itself; breaking changes declared in the same paragraph's second half | ✓ |
| The output shape changed | Lead with the fact that touches every user — one entry now writes two files | |
| Content that was silently dropped | The repair narrative binding defect A / B-1 / B-2 into one failure class | |

**User's choice:** Multi-master now works. → **D-05**

### Q3 — What does `### Verified` carry?

Context measured: 0.7.0 and 0.7.1 carry an identical three-item list. SC#4 adds a fourth mechanical
invariant (no new `typst_*` config value) and SC#3 produces a multi-master round-trip result.

| Option | Description | Selected |
|--------|-------------|----------|
| The same three items | Unchanged from 0.7.0 / 0.7.1; SC#4's fourth invariant and SC#3's round trip stay in phase evidence artifacts | ✓ |
| Four items | Add "no new `typst_*` config value" — directly useful to someone upgrading | |
| Five items | Also add the real multi-master round-trip result, pinning the headline claim on a public surface | |

**User's choice:** The same three items. → **D-06**

---

## Claude's Discretion

Recorded in CONTEXT.md `<decisions>` § "Claude's Discretion":

- Exact `## [0.8.0]` wording, the lead paragraph's phrasing, the final 8–9 bullet cut, requirement-ID
  attachment, and `### Added` / `### Changed` / `### Fixed` assignment.
- Plan decomposition, ordering, and the `uv.lock` regeneration procedure.
- The mechanical method for the SC#4 invariant sweep and what its positive control is.
- Whether `"0.8.0"` joins `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py` in this phase.
- The name and shape of the new goal-claim gate module, and whether it reuses or extends
  `state_guard_three_master_gate`.
- `52-HANDOFF.md`'s structure and where live-run evidence is written — subject to the reserved-name
  constraint (never `52-VERIFICATION.md`).
- Whether the CI dispatch is one run or two.

## Deferred Ideas

- Fixing any of the four minor defects in this phase (prep-only fence, D-01).
- A `### Known Limitations` CHANGELOG section and public GitHub issues for them (declined, D-01).
- Promoting them to ROADMAP backlog items `999.3`+ (declined, D-03).
- The `:numref:` divergence — excluded from every published surface by 51-CONTEXT D-07; a later
  milestone picks it up as a bug.
