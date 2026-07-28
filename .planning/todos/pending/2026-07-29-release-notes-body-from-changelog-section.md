---
created: 2026-07-29T00:50:46+09:00
title: The GitHub Release body should be the CHANGELOG section, not a commit dump
area: ci, release
files:
  - .github/workflows/release.yml (the `create-release` job's `Generate release notes` step at line 152, whose commit-dump command sits at line 164 and whose Installation block starts at line 170)
  - CHANGELOG.md (the source the reworked step would extract the `## [X.Y.Z]` section from)
---

## Problem

The v0.6.4 GitHub Release body is 308 lines. Lines 1 through 296 are the commit dump the workflow
itself produces from a `git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` range — one line per
commit, including planning commits (e.g. `docs(33-04): …`) that mean nothing to a reader of the
release. Lines 297 through 303 are the Installation block (`pip install typsphinx==${TAG#v}`).
Lines 304 through 308 are GitHub's own output from the `generate_release_notes: true` option — a
single "What's Changed" pull-request line plus a Full Changelog compare link. The auto-generated
portion is already compact; the bloat is entirely the hand-rolled commit-dump block
(`.github/workflows/release.yml`'s `create-release` job, `Generate release notes` step at line 152,
commit-dump command at line 164, Installation block starting at line 170).

The second measured fact: `release.yml` never reads `CHANGELOG.md` at all today — nothing in the
`Generate release notes` step, or anywhere else in the workflow, opens or greps that file. The
Phase 33 CONTEXT statement describing the `[0.6.4]` CHANGELOG entry as "the single source for the
GitHub Release body" contradicts the workflow as written, and only becomes true once this todo is
resolved. This correction is the reason the todo exists in this form rather than as a cosmetic
cleanup.

This rework was deliberately excluded from v0.6.5 per decision D-11 in
`.planning/phases/35-v0-6-5-release-prep/35-CONTEXT.md`: v0.6.5 is a hotfix release, and editing the
release-publishing workflow itself immediately before a release is out of scope for a plan that is
not reviewing publish behavior.

## Solution

Design direction, as concrete steps:

- Remove the commit-dump block (the `git log $PREV_TAG..$TAG --pretty=format:"- %s (%h)"` command
  and its surrounding `## Changes since $PREV_TAG` / `## Initial Release` scaffolding) from the
  `Generate release notes` step.
- Extract the single `## [X.Y.Z]` section matching the tag's version from `CHANGELOG.md` and use it
  as the release body instead.
- Keep the Installation block as-is.
- Keep the `generate_release_notes: true` option enabled on the `Create GitHub Release` step, so the
  auto-generated "What's Changed" pull-request line and Full Changelog link continue to survive.

Failure mode a future implementer must handle: the tag's version may have no matching `## [X.Y.Z]`
section in `CHANGELOG.md` (e.g. a version bump forgotten in the changelog, or a mismatched tag). The
step must fail loudly (non-zero exit, clear error message) rather than publish a release with an
empty or malformed body.
