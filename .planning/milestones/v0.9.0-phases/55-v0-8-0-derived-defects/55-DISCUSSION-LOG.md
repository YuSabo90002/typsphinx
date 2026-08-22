# Phase 55: v0.8.0-Derived Defects - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-16
**Phase:** 55-v0-8-0-derived-defects
**Areas discussed:** XREF-05 fix locus, Evidence bar per defect

---

## Gray area selection

Four areas were offered; the two ROADMAP already locks (BLD-07's "escape `#` and `>`", BLD-09's
`posixpath.isabs(…) or _is_drive_qualified(…)` predicate) were excluded from the offer.

| Option | Description | Selected |
|--------|-------------|----------|
| XREF-05 fix locus | Sanitizer injectivity vs a compile-time docname-existence mechanism | ✓ |
| IMG-03 key derivation | Hashed prefix vs another flattening; whether the collision branch changes too | |
| BLD-08 depth bound | Threshold value and source; recursion + counter vs iteration | |
| Evidence bar for the five defects | Which need a real `typst.compile()` fixture vs a unit RED | ✓ |

**User's choice:** XREF-05 fix locus, Evidence bar.
**Notes:** IMG-03 and BLD-08 were left to Claude's discretion with the todos' own recommendations.

---

## XREF-05 fix locus

| Option | Description | Selected |
|--------|-------------|----------|
| Make the sanitizer injective | Re-escape the literal `_u<hex>_` token inside `_sanitize_label`; both definition and reference sites already route through this one function (9 call sites), so no Typst-side mechanism is added. Measured churn: only ids literally spelling the escape token — in-tree, one fixture docname | ✓ |
| Give the guard docname evidence | Leave labels alone; emit a per-document `metadata` whose value is the raw docname and query that. Requires a new shared-label marker (the existing `<docname:__tsx-doc__>` anchor is itself on the colliding side) and an unmeasured assumption about duplicate labels under `query()`; adds Typst per reference site | |
| Reuse Phase 49's include-edge state | Read `state("typsphinx:include-edges")` to ask whether the target docname is in this master's include set. Array holds `parent#0>child` edge keys, not docnames, and a master never appears as its own child — a separate docname array would have to be published, and the XREF guard would depend on the include graph | |

**User's choice:** "おすすめ" — deferred to the recommendation, which was the sanitizer fix.
**Notes:** Locked as D-01/D-02. The two rejected alternatives and the measurements behind the
rejection are recorded in CONTEXT.md so they are not re-litigated at planning.

---

## Announcement of the label-spelling change

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG, as `Fixed` | One line under `Unreleased` → `Fixed`, written in this phase (Phase 54/54.1 precedent); not treated as a breaking change — v0.9.0's two breaking axes stay two | ✓ |
| Not in the CHANGELOG | Reachability is narrow enough (a docname literally spelling another docname's `/`-transform) to fix silently | |

**User's choice:** CHANGELOG に Fixed として記載.
**Notes:** Locked as D-03. Phase 57 curates rather than authors this entry.

---

## Evidence bar per defect

| Option | Description | Selected |
|--------|-------------|----------|
| BLD-07 only gets a real compile | BLD-07 is output-visible (a wrongly-fired guard silently drops a child's content), so a `#`-bearing docname fixture compiles for real; BLD-08 is exception-shaped and never reaches output (the todo states a 1000-deep fixture is unnecessary); IMG-03 sits beside the existing Phase 50 relocation unit tests | ✓ |
| All three at unit level | Close all three in the files their todos name; reachability is artificial in every case and fixture cost is not repaid | |
| All three at real-compile level | Strictest reading of binding constraint #6; BLD-08 would need a synthesized deep toctree fixture, raising build time and maintenance cost | |

**User's choice:** BLD-07 だけ実コンパイル.
**Notes:** Locked as D-05, together with the two levels the ROADMAP already fixes — XREF-05's real
two-master compile (SC#1) and BLD-09's platform-independent string-shape test (SC#4).

---

## Claude's Discretion

- IMG-03's relocation-key form (recommendation: the todo's `sha1(resolved_uri)[:8]-basename`), and
  whether the collision branch changes too (recommendation: no).
- BLD-08's depth threshold and its constant's home (recommendation: own module-level constant with a
  commented rationale, not `sys.getrecursionlimit()`), and recursion + counter over iteration.
- BLD-07's escape spelling, applied to the two docnames only and written once inside
  `make_include_edge_key`.
- Whether plan 52-09's drive-qualified fixture is reverted or supplemented (recommendation:
  supplemented).
- Plan/wave decomposition, test file naming and placement.

## Deferred Ideas

- A Typst-side docname-existence mechanism (the two rejected XREF-05 alternatives) — would need its
  own requirement if ever wanted.
- Widening `escape_typst_string()` to cover `#`/`>` — rejected; it is used at sites that do not want
  `#` escaped.
- Reverting the 52-09 fixture; hash-keying `_track_image()`'s collision branch.
- Reviewed but not folded: `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — release
  pipeline work, matched only on generic keywords.
