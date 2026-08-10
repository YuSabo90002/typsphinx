---
created: 2026-08-04T05:51:32+09:00
title: The docs changelog page is frozen at 0.4.0 — 12 releases missing
area: docs
severity: minor
files:
  - docs/source/changelog.rst
  - CHANGELOG.md
---

## Problem

`docs/source/changelog.rst` — the Changelog page of the published manual — still
presents **0.4.0 as the current release**, and has not been touched since the
0.4.0 bump.

Measured 2026-08-04:

- `git log -- docs/source/changelog.rst` shows only three commits, the newest
  substantive one being `9178655 chore: bump version to 0.4.0`. The only later
  commit (`7821f32`) just repaired dead links, not content.
- The page's heading reads `Version 0.4.0 (Current)`.
- `CHANGELOG.md` has since shipped **0.4.1, 0.4.2, 0.4.3, 0.5.0, 0.6.0, 0.6.1,
  0.6.2, 0.6.3, 0.6.4, 0.6.5, 0.7.0** — none of which appear on the page. Note
  0.4.0 in the page also predates the `0.1.0b1` / `0.2.0` ordering fixes made in
  `CHANGELOG.md` itself.
- The page is internally inconsistent on top of being stale: its
  **Development Status** section claims `v0.3.x: Current stable release`,
  `v0.2.x: Maintenance mode` — which contradicts even the 0.4.0 heading directly
  above it.
- **Migration Guides** stops at "Migrating from 0.2.x to 0.3.x", so the 0.5.0 →
  0.6.0 and 0.6.x → 0.7.0 transitions (which changed emitted `.typ` output for
  every API-documenting project) have no migration note in the manual at all.

Impact is contained: the page does link out to `CHANGELOG.md` on GitHub for "the
complete changelog", so a reader who follows the link gets accurate data. The
harm is that a reader who does *not* follow the link is told the project's latest
release is 0.4.0.

## Solution

Open question to settle first — **duplicate or delegate?**

1. **Keep the hand-maintained duplicate** and backfill 0.4.1 → 0.7.0 (plus fix the
   Development Status and Migration Guides sections). Cheap once, but this todo
   exists precisely because that duplicate drifted silently for 12 releases, and
   nothing prevents it from drifting again.
2. **Delegate to the single source of truth** — reduce the page to its framing
   sections (Deprecation Policy, Versioning, Release Process, See Also) plus a
   rendered include of `CHANGELOG.md`, e.g. via `myst-parser` / `.. include::`
   with a relative path out of `docs/source/`. Then it can never diverge.
   Requires checking that the Markdown renders under the current docs toolchain
   and that the release-prep phase (which already edits `CHANGELOG.md`) needs no
   second edit.

Whichever is chosen, add the corresponding step to the release-prep checklist so
this cannot silently rot again — that is the actual root cause, not the stale
text. See the existing CHANGELOG link-block convention already owned by
release-prep.

Also fold in while touching the file:

- **Development Status** — restate against the real current version.
- **Migration Guides** — add entries for the 0.6.x and 0.7.0 output changes, or
  drop the section if option 2 makes it redundant.
