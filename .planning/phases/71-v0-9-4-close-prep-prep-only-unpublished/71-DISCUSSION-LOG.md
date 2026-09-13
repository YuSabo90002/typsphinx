# Phase 71: v0.9.4 Close Prep (prep-only, unpublished) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-13
**Phase:** 71-v0-9-4-close-prep-prep-only-unpublished
**Areas discussed:** the ja sentence in the CHANGELOG bullet, evidence depth in the bullet

The ROADMAP SC and Phase 69's D-01..D-14 fixed everything else, so the discussion covered only these
two. That included the placement under `### Changed`, `main` absorption, the merge method, the fence,
the single CI dispatch, the decoy re-check and the unclaimed version numbers. `main` absorption was
measured unnecessary today: `origin/main` = merge-base `d14ca458`. Open dependabot PRs: none.

Both questions were asked in prose, not via AskUserQuestion, so that the measurements reached the
owner under focus mode.

---

## The ja sentence in the CHANGELOG bullet

Finding presented first: REL-13 / SC#2's clause "the ja translation catalogs pick it up at the next
published release" is inaccurate. `update-pin.yml` in `typsphinx-doc-translations` runs on a daily
`schedule` and follows `main`, not releases. The daily runs succeeded through 2026-09-12T10:22Z. The
pin stayed at `6181768f` only because `main` did not move until #137 at 10:38Z. Positive control:
v0.9.3's `tox-uv` bullet appears on `en/latest` (3 hits) and not yet on `ja/latest` (0). `api/index.po`
has 668 msgids, 0 translated, and 2 of them carry `~typing.Dict` / `~typing.Tuple` roles.

| Option | Description | Selected |
|--------|-------------|----------|
| (a) Rewrite to match reality | ja `latest` updates via the daily sync, `stable` at the next published release; AMENDED blocks on REL-13 and SC#2 | |
| (b) Drop the ja sentence | The ja API reference is untranslated (0/668) and shows the same English type text; the en description suffices; AMENDED blocks record it | ✓ |
| (c) Keep the literal requirement wording | Publishes an inaccurate timing claim | |

**User's choice:** (b)
**Notes:** Claude recommended (a). The owner chose (b). The AMENDED blocks were appended to
`REQUIREMENTS.md` REL-13 and ROADMAP Phase 71 SC#2 in the same commit as CONTEXT.md, before the
phase's fence baseline.

---

## Evidence depth in the bullet

| Option | Description | Selected |
|--------|-------------|----------|
| (a) One evidence sentence | Emitted Typst output and runtime behaviour unchanged; `.typ` byte-identical over the test-fixture corpus; numbers transcribed from Phase 70 evidence at execution | ✓ |
| (b) No evidence | Only "no effect on installing or using typsphinx" | |
| (c) All five measurements | Enumerate QUA-12 legs (a)–(e) | |

**User's choice:** (a), the recommended option.

---

## Claude's Discretion

- The exact bullet prose within D-01..D-03.
- Plan split, waves and evidence-file naming (the Phase 69 set).
- How the SC#1 masked-AST re-run is invoked.
- The clean-build docs warning baselines.

## Deferred Ideas

- The next published version number, left to the next milestone's scoping.
- The REQUIREMENTS Out of Scope row's "at the next published release" timing, noted in REL-13's
  AMENDED block and left for the milestone-close archive.
