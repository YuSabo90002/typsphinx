# Phase 1: Pin Runtime Dependencies to Known-Good - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-04
**Phase:** 1-Pin Runtime Dependencies to Known-Good
**Areas discussed:** Pin Expression Style, Ceiling Load-Bearing (PIN-06), Commit/Plan Granularity, Ceiling Target Scope

---

## Pin Expression Style

| Option | Description | Selected |
|--------|-------------|----------|
| 範囲据え置き+lockで再現 | Upper bounds only (`typst>=0.14.1,<0.15`, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22`); keep floors; strict reproducibility via `uv.lock`. Minimal-diff, idiomatic. | ✓ |
| typst を == で厳密ピン | Pin `typst==0.14.x` exactly in `pyproject.toml`; safe if lock breaks but future patch bumps become manual. | |
| floor も引き上げ | Raise the sphinx floor (e.g. `>=7.0`) to narrow the resolution matrix; risks overlapping PYVER scope (Phase 3). | |

**User's choice:** 範囲据え置き+lockで再現
**Notes:** Reproducibility is carried by `uv.lock`; `pyproject.toml` expresses the compatible range. DUR-01 (Phase 5) later enforces lock currency, so a range is safe.

---

## Ceiling Load-Bearing Determination (PIN-06)

| Option | Description | Selected |
|--------|-------------|----------|
| 上限付与→typst単独も検証し記録 | Apply all three ceilings (PIN-02) AND empirically verify whether `typst<0.15` alone turns docs-pdf green; record load-bearing finding in PROJECT.md. | ✓ |
| 上限のみ、判定は省略 | Apply ceilings, mark them precautionary; satisfies PIN-06 documentation but root-cause stays unconfirmed. | |

**User's choice:** 上限付与→typst単独も検証し記録
**Notes:** Ceilings are required regardless (PIN-02); the extra step establishes whether sphinx/docutils bounds are load-bearing vs precautionary, per PIN-06.

---

## Commit / Plan Granularity

| Option | Description | Selected |
|--------|-------------|----------|
| 別コミットに分離 | Land the PIN change and the `black` reformat as separate commits/plans — honors ROADMAP's unambiguous red/green directive; keeps blame clean. | ✓ |
| 1コミットにまとめる | Single bundled commit; concise but mixes pin effect with reformat. | |

**User's choice:** 別コミットに分離
**Notes:** ROADMAP explicitly requires the pin fix to land alone so a red/green result is unambiguous.

---

## Ceiling Target Scope

| Option | Description | Selected |
|--------|-------------|----------|
| ランタイム3依存のみ | Bound only `typst`/`sphinx`/`docutils`; dev/docs deferred to Phase 4 / elsewhere. Minimal diff, clean attribution. | ✓ |
| docs依存にも予防上限 | Also bound `furo`, `sphinx-autodoc-typehints`, `sphinx-intl`; kills a drift source now but out of this phase's requirement scope. | |

**User's choice:** ランタイム3依存のみ
**Notes:** Matches REQUIREMENTS scope; docs.yml green is confirmed in Phase 2, dev tooling is Phase 4.

---

## Claude's Discretion

- Exact `typst` patch within `0.14.x` (empirically confirmed in CI, not assumed at plan time).
- Precise plan decomposition (plan count and ordering, within the separate-commit constraint).
- Mechanical `uv.lock` regeneration invocation.

## Deferred Ideas

None — discussion stayed within phase scope. Forward-port (sphinx 9 / typst 0.15), configurable `@preview` versions, dev-tooling bumps, and durability guardrails are already tracked as v2 / later phases.
