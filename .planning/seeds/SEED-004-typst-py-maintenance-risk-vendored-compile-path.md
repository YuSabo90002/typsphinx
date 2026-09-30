---
id: SEED-004
status: dormant
planted: 2026-08-16
planted_during: v0.9.0 / Phase 56 (per-document-template-documentation)
trigger_when: when relevant
scope: unknown
audit_acknowledged:
  milestone: v0.9.1
  at: 2026-08-29
  status: dormant
---

# SEED-004: typst-py upstream maintenance is slowing — typsphinx may need to carry an equivalent compile mechanism itself

Original capture (verbatim, ja):

> typst-py の更新が途絶えつつあるので同様の仕組みをこのレポジトリに持たす必要がでてくるかも

## Why This Matters

_To be filled in. Run `/gsd-capture --seed --enrich SEED-004` to add context._

Initial framing at capture time: `typst-py` is the single dependency that makes the
`typstpdf` builder work without an external Typst CLI, and "no external Typst CLI required"
is stated as a headline property of this project. If upstream stalls, that property — not
merely a version pin — is what is at risk.

## When to Surface

**Trigger:** when relevant

This seed will surface during `/gsd-new-milestone` when the milestone scope matches.

Candidate narrower triggers to consider at enrich time (not yet chosen):

- when `typst>=0.15.0,<0.16` can no longer be widened to a current Typst release
- when the weekly `drift.yml` re-resolution starts failing on the typst pin
- when a needed Typst compiler feature exists in the CLI but not in the Python binding

## Scope Estimate

**Unknown** — run `/gsd-capture --seed --enrich SEED-004` to estimate effort.

## Breadcrumbs

Coupling surface is narrow, which is favourable for this idea:

- `typsphinx/pdf.py` (229 lines) — the ENTIRE typst-py coupling: `check_typst_available()`,
  `get_typst_version()`, and the compile call, plus `TypstCompilationError` which carries the
  underlying typst error. Everything else in the pipeline produces `.typ` text and is
  binding-agnostic.

- `pyproject.toml:30` — `"typst>=0.15.0,<0.16"`, the pinned dependency
- `pyproject.toml:97` — an existing comment referencing typst-py 0.15.0 and its
  verified zero-third-party-warnings behaviour (recorded in `08-RESEARCH.md`)

- `.github/workflows/drift.yml` — weekly re-resolution of latest allowed deps; this is the
  existing early-warning channel for the pin going stale

- `CLAUDE.md`, `README.md`, `docs/source/index.rst` — all state the
  "no external Typst CLI required" property that this seed is really about protecting

Related planning context:

- `.planning/todos/pending/` — no existing todo covers the typst-py dependency
- No prior seed overlaps (SEED-001 README quickstart, SEED-002 captioned-table label,
  SEED-003 tox dependency groups)

## Notes

_Captured via one-shot seed capture. Enrich with trigger, why, and scope at your convenience._

Written in English per the project convention that `.planning/` artifacts are English; the
user's original Japanese phrasing is preserved verbatim above so the intent is not lost to
translation.
