# Phase 70: Typing Modernization and Its Behaviour-Identity Evidence - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-13
**Phase:** 70-typing-modernization-and-its-behaviour-identity-evidence
**Areas discussed:** CLAUDE.md:75 wording, QUA-12 (d) corpus, DOC-23 build scope

The three areas and their options were presented in one message with the measurements behind them.
The owner replied "全部おすすめで進める" ("go with the recommendation on all of them"), so the
recommended option was taken in each area.

---

## CLAUDE.md:75 wording

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | Keep only `Python 3.12+ is required.`; say nothing about typing | |
| (b) | Add the instruction: annotations use builtin generics (`dict[str, Any]`) and `collections.abc` | ✓ |
| (c) | (b) plus prohibitions on `from __future__ import annotations` and a `X \| None` sweep | |

**User's choice:** the recommended option, (b).
**Notes:** (c) was rejected because those are milestone scope fences, and `typsphinx/` already has 52
`| None` annotations.

---

## QUA-12 (d) corpus

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | The 12 committed golden files (already asserted by tests, so it overlaps leg (b)) | |
| (b) | All 167 `conf.py` projects under `tests/` (166 fixtures + 1 roots), built `-b typst` on both sides, every `.typ` hashed | ✓ |
| (c) | (b) plus the 4 `examples/` projects | |

**User's choice:** the recommended option, (b).
**Notes:** the build time is unmeasured, so the plan pilots it first and escalates rather than narrowing the corpus.

---

## DOC-23 build scope

| Option | Description | Selected |
|--------|-------------|----------|
| (a) | HTML build only | |
| (b) | HTML plus the `.typ` from the typstpdf build. `index.rst:59` includes `api/index`, so the dogfood PDF's `.typ` changes too | ✓ |

**User's choice:** the recommended option, (b).
**Notes:** the docs `.typ` is covered by DOC-23 and kept out of leg (d).

---

## Claude's Discretion

- The exact wording of the CLAUDE.md bullet, the plan split, evidence file naming, the choice of mask
  pilot file, how the base side is materialised, and whether the docs diff is taken on raw HTML or
  extracted text.

## Deferred Ideas

- None new. Five matched todos were reviewed and not folded: MSG-06, TRN-01, NUM-01, DOC-18, QUA-08.
