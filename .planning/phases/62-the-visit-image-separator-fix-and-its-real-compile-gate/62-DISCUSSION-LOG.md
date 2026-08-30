# Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-30
**Phase:** 62-the-visit-image-separator-fix-and-its-real-compile-gate
**Areas discussed:** RED evidence granularity & master layout; what the 9 must-pass shapes are
bound to; CHANGELOG bullet ownership; push / CI dispatch placement

---

## Gray-area selection

One multi-select turn was presented offering four phase-specific gray areas. The owner answered
via free text: **"おすすめ設定"** — delegating all four at once to Claude's recommendation rather
than selecting a subset.

| Option | Description | Selected |
|--------|-------------|----------|
| RED 証拠の粒度と master 構成 | typst's error string carries no file/line and no multiplicity, so per-shape attribution only exists per-master; also decides where SC#1's no-image blast-radius master lives | delegated |
| 9 must-pass shape に何を縛るか | ROADMAP SC#3 says "all compiling"; research/FEATURES.md Q2 says "byte-identical" — the gate binds one of them, which in turn settles the triad's insertion point | delegated |
| CHANGELOG bullet の担当フェーズ | Measured precedent is split: v0.9.0's fix phase wrote its own bullet, v0.9.1's release-prep phase wrote all of them | delegated |
| push と CI ディスパッチの位置 | `ci.yml` triggers are `main`/`develop` only, so a push runs no CI; placement changes the plan wave structure | delegated |

**User's choice:** "おすすめ設定" (use the recommended configuration for all four).
**Notes:** No area was excluded and no constraint was added. All thirteen decisions in CONTEXT.md
are therefore Claude-authored recommendations accepted en bloc, each grounded in a measurement
taken during this session rather than in prior prose.

---

## Measurements taken during this discussion

These were run to make the options factual rather than remembered, and both ended up load-bearing
for the recommendation.

| Measurement | Command / site | Result |
|---|---|---|
| Does typst report one error or many per file? | `typst.compile()` on a probe `.typ` with **three** independent unseparated `text()image(` juxtapositions | Exactly one message: `expected semicolon or line break`. No file, no line, no multiplicity. |
| Does one failing master abort the whole build? | `typsphinx/builder.py:2505-2642` (`TypstPDFBuilder.finish()`) | No — every master is attempted, failures are collected, and one aggregate `ExtensionError` joins `f"{docname}: {err}"` per failure. |
| Does a push run CI on a feature branch? | `.github/workflows/ci.yml` triggers | `push`/`pull_request` scoped to `main`/`develop` + `workflow_dispatch`. A push alone runs nothing. |
| Is the decoy branch live right now? | `git branch -vv` | One `0.9.2` branch, the canonical one, at `6224298e`, local-only with no upstream. No decoy at present. |
| Who wrote CHANGELOG bullets in the last two milestones? | `git log --oneline -- CHANGELOG.md` | v0.9.0: fix phase (`d0394773 docs(55-04)`). v0.9.1: release-prep only (`70b2823b`, `8bb0288e docs(61-01)`) — fix phases 59/60 wrote none. |
| Does `_emit_id_anchors()` interact with a new triad? | `typsphinx/translator.py:1006-1028` | Early-returns for a node with no ids; otherwise emits `\n[#metadata(none) <id>]\n` **and** sets `list_item_needs_separator = True`. |
| Is a multi-master fixture precedented? | `tests/fixtures/*/conf.py` | 52 fixtures declare more than one `typst_documents` entry; `state_guard_three_master_gate` has 3 masters over 6 documents with shared toctree'd children. |

---

## Alternatives considered and rejected

| Alternative | Why rejected |
|---|---|
| All 16 failing shapes in one document under one master | Collapses to a single indistinguishable refusal (measured), so SC#2's "for each failing shape" becomes unsatisfiable. |
| Group the 16 failing shapes into ~5 container-family masters | Fewer refusals than shapes; the same attribution gap, only smaller. |
| Give each of the 9 passing shapes its own master too (26 masters) | Attribution is not needed for shapes that pass; one document per PASS shape already gives byte-level granularity without 9 extra wrappers and PDFs. |
| Bind the 9 passing shapes to "still compiles" only (ROADMAP SC#3's literal wording) | The realistic failure mode of this fix is a cosmetic extra `\n` that still compiles. "Compiles" cannot see it; byte-identity can, and byte-identity implies compiling, so SC#3 stays satisfied. |
| Decide the triad's placement relative to `_emit_id_anchors()` by argument now | The goldens decide it by measurement. Recording the hazard is useful; pre-committing to a placement is not. |
| Write the `## [Unreleased]` bullet in Phase 62 (the v0.9.0 precedent) | Phase 63 must curate one `## [0.9.2]` entry covering v0.9.1's bullets *and* this fix, and constraint 7's scratch-block relocation has to precede the heading rename. Splitting the authorship across two phases invites a half-written entry. |
| Dispatch CI mid-phase and iterate on it | One authority run against the phase's last commit is what SC#5 asks for; extra runs cost minutes without changing the verdict. The early push is separate and free (it triggers nothing). |

---

## Claude's Discretion

The owner delegated all four gray areas ("おすすめ設定"), so every decision D-01..D-13 in
CONTEXT.md is Claude's. Planning may refine the fixture's internal file names and the
golden-comparison helper's shape. It may **not** weaken D-06 (byte-identity), D-09 (no CHANGELOG
edit in this phase), or D-13 (zero pre-existing test edits) without returning to the owner.

## Deferred Ideas

- A cheap string-level (non-compiling) regression test alongside the real-compile gate — a
  `research/FEATURES.md` Q3 differentiator. TEST-05 specifies one gate module and the real compile
  is the authority; 144 `image(` substring assertions across 20 test files already cover the string
  level.
- A doc-comment in `visit_image()` cross-referencing `visit_Text`'s triad by name — zero
  behavioural risk, fold in if free, not a requirement.
- Four pending todos were reviewed against this phase and left unfolded (MSG-06, REL-04, QUA-10,
  NUM-01, CI-01) — all are REQUIREMENTS.md v2 items. See CONTEXT.md `<deferred>` for the per-todo
  reason; note the NUM-01 one is also a fixture-design constraint (the new fixture must not use
  `numref`).
