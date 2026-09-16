# Phase 73: v0.9.5 Close Prep (prep-only, unpublished) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-14
**Phase:** 73-v0-9-5-close-prep-prep-only-unpublished
**Areas discussed:** CHANGELOG bullet placement, Open Dependabot PRs

The two areas were presented together, with measured findings, in one message. The owner answered
both in prose: "1. A 2.A".

---

## CHANGELOG bullet placement and count

| Option | Description | Selected |
|--------|-------------|----------|
| A | Linkcheck under a new `### Added`, the sidebar fix under a new `### Fixed`: two bullets, the house order the released sections use | ✓ |
| B | Both under the existing `### Changed`, as one or two bullets | |

**User's choice:** A.
**Notes:** Both options satisfy SC#2's pure addition and the byte-identity of the four existing
bullets. It was measured that neither the changelog page gate nor the extraction script asserts
which subsections `## [Unreleased]` holds. The content of the evidence sentence was left to
discretion, within D-03 and D-04.

---

## Open Dependabot PRs (#146–#150)

| Option | Description | Selected |
|--------|-------------|----------|
| A | Leave them untouched, name them in the handoff, and merge them after the milestone PR (the order v0.9.3 used: #143, then #142 and #141; Phase 71 D-12) | ✓ |
| B | The owner merges them to `main` before execution, so this phase's runs cover the merged lock and the handoff's branch-update step is live | |

**User's choice:** A.
**Notes:** Measured: all five change `uv.lock` only, and each is `MERGEABLE` and 15/15 `SUCCESS`.
#150 (`sphinx-autodoc-typehints`) is a `docs`-extra dependency that SC#3's trial merge would not
exercise.

## Claude's Discretion

- The bullet prose and the trailing requirement IDs.
- Plan decomposition and evidence-file naming.

## Deferred Ideas

- Choosing the next published version number.
- A docs build of `main` + #150 (it runs as that PR's own checks after the merge).
