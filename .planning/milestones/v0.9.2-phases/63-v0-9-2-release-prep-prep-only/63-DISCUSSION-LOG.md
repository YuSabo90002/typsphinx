# Phase 63: v0.9.2 Release Prep (prep-only) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-30
**Phase:** 63-v0-9-2-release-prep-prep-only
**Areas discussed:** all four presented areas, delegated en bloc

---

## Gray-area selection

One question was asked. The owner answered **"おすすめ"** — delegating all four areas to Claude's
measured recommendation, the same route taken at Phase 62 ("おすすめ設定"). No per-area follow-up
questions were asked as a result.

| Option | Description | Selected |
|--------|-------------|----------|
| A. `[0.9.2]` エントリの構成 | Lead paragraph の有無、blocker を見出し扱いにするか、v0.9.1 由来の既存3バレットの扱い、`### Verified` の有無 | ✓ (delegated) |
| B. 公開済み 0.9.0 への言及の強さ | `### Fixed` バレットに留めるか、アップグレード喚起を足すか、README の Known Limitations に触れるか | ✓ (delegated) |
| C. リリース周辺のガード更新 | `RELEASE_VERSIONS` に `0.9.2` を足すか、Migration Guide 節を作るか | ✓ (delegated) |
| D. `63-HANDOFF` の範囲と REL-04 | 継承3ステップ + `create-release` ジョブの再提案と失敗時の扱い | ✓ (delegated) |

**User's choice:** "おすすめ" — all four, Claude's recommendation.
**Notes:** Recorded in CONTEXT.md as D-01 … D-21, each grounded in a measurement taken during this
session against the tree at `dd385436`.

---

## Measurements taken during this discussion

Recorded here because each one settled a decision that could otherwise have gone the other way.

| Measurement | Result | Settled |
|---|---|---|
| `awk` over `CHANGELOG.md` for `### Verified` per section | Present in 9 consecutive releases, 0.6.1 → 0.9.0, no gap | D-06 (write one) |
| Lead-paragraph presence per released section | Present in all of 0.6.1 … 0.9.0 | D-01 |
| `## [0.6.5]` full section read | Hotfix patch, one compile-blocking separator defect, lead + `### Fixed` + `### Verified`, no migration guide | D-01, D-07, D-12 |
| `README.md:283-300` | `## Known Limitations` still holds its two original entries; nothing about the image blocker was ever added | D-09 (nothing to remove) |
| `docs/source/changelog.rst` Migration Guides inventory | 7 guides; **none** for `0.6.5`, the only prior no-breaking-change patch | D-12 |
| `tests/test_changelog_page_gate.py:50-66` + `git log` on that file | `RELEASE_VERSIONS` ends at `0.9.0`; Phases 46, 52, 57 each extended it at release-prep | D-11 |
| `pyproject.toml:49-54` + the gate module's own docstring/guard | `myst_parser` is in the `docs` extra only, so both build classes skip under `uv sync --extra dev` | code_context hazard for D-11 |
| `scripts/extract_changelog_section.py` docstring + `_SECTION_HEADER_RE` | Extraction is purely positional; two `## [Unreleased]` headings exist by design | D-20 |
| `uv.lock` self-package stanza | line 1467 reads `version = "0.9.0"`, independent of `pyproject.toml:7` | D-17 |
| `git tag -l 'v0.9.2'`, `git ls-remote --tags origin \| grep 0.9.2` | both empty | specifics #6 |
| `git branch -vv` | one `0.9.2` branch, canonical, `dd385436`, ahead 10, no decoy present | specifics #5 |

---

## Claude's Discretion

Everything. The owner delegated all four areas at once. CONTEXT.md's `### Claude's Discretion`
subsection names what planning may still refine (plan decomposition, exact prose, the mechanical
form of the fence, the handoff's headings) and the five decisions planning may **not** weaken
without returning to the owner (D-02, D-07, D-16, D-17, D-19).

## Deferred Ideas

- A GitHub Security Advisory, a PyPI yank of 0.9.0, or a README upgrade banner for the blocker live
  in the published 0.9.0 — declined for this phase by D-10 (outward-facing and irreversible).
- A `Migrating from 0.9.0 to 0.9.2` guide — declined by D-12 (nothing breaks; no precedent).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run, which would let D-06's third
  `### Verified` bullet reuse nine prior releases' exact wording — not adopted; D-06 substitutes a
  claim this milestone actually measured.

## Todos reviewed, none folded

All eight matched by `todo.match-phase 63` stay in `.planning/todos/pending/`. REL-04's todo
(`2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`) is *named in the handoff* by D-14 —
the re-offer `61-HANDOFF.md` instructed — which is a record, not a fold.
