# Phase 58: `repr()`-Format Decoupling (test-side only) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-27
**Phase:** 58-repr-format-decoupling-test-side-only
**Areas discussed:** replacement assertion predicate, predicate helper placement, SC#2
falsification route, census scope and artifact

---

## Gray-area selection

One `AskUserQuestion` turn was presented (multiSelect over four phase-specific gray areas). The
owner answered **"おすすめで進める"** — delegating all four to Claude's recommendation. No
per-area follow-up turns were run; every option below was resolved by Claude and locked in
CONTEXT.md as D-01…D-10.

---

## Replacement assertion predicate

| Option | Description | Selected |
|--------|-------------|----------|
| Enumerate allowed quoting forms (raw / `repr()` / `'…'` / `"…"`) | Explicit four-way disjunction, self-documenting | |
| Two-form minimal-complete disjunction (raw or `repr()`) | The two delimiter forms are strictly subsumed by the raw check | ✓ |
| Collapse `\\`→`\` in the message, then match raw | Normalizes the message before comparison | |
| Identifying substring (drive letter + separator, or basename) | Decomposed structural property | |

**User's choice:** delegated — Claude selected the two-form disjunction (D-01).
**Notes:** the collapse option was rejected as directly conflicting with
`TestWindowsPathEscapingRegressionGuard`, whose whole purpose is to *detect* doubled backslashes —
a predicate that erases them would hide the defect the milestone exists to fix. The
basename/component option was rejected on a measured fact: `builder.py:697` interpolates both
`{target!r}` and `{fallback!r}`, and for the `drive` shape `fallback == "escape.typ"` is exactly
`target`'s basename, so a basename predicate stays GREEN with `target` fully removed — the
tautology SC#2 explicitly forbids (D-03). Two additional refinements were added beyond the option
as presented: the predicate is applied to the extracted warning **line** rather than the whole
subprocess capture (D-02), and it always takes the full path value (D-03).

---

## Where the shared predicate lives

| Option | Description | Selected |
|--------|-------------|----------|
| `tests/conftest.py` | Existing shared location, but fixtures-only today; `from conftest import …` is a pytest anti-pattern | |
| New `tests/_path_naming.py` leaf module | No non-`test_` module exists in `tests/` yet; verified importable | ✓ |
| Inline duplication in both test modules | No new file, but two copies of a predicate Phases 59/60 depend on | |

**User's choice:** delegated — Claude selected the new leaf module (D-04).
**Notes:** the import mechanism was **verified live**, not assumed — a throwaway
`tests/_probe_helper.py` + `tests/test_zzprobe.py` pair was created, collected and passed under
`pytest`, then removed. `tests/` has no `__init__.py` and `pyproject.toml` sets
`testpaths = ["tests"]` with the default `prepend` import mode, so `tests/` lands on `sys.path`
and a bare `from _path_naming import …` resolves. The leaf-module shape also mirrors MSG-02's
forced leaf-module placement on the product side.

---

## SC#2 falsification route

| Option | Description | Selected |
|--------|-------------|----------|
| Temporary product edit, run, record RED, revert | Proves the real wiring; leaves nothing behind | |
| Permanent meta-test feeding synthetic messages to the predicate | Durable, runs in CI forever | |
| Both | Each covers what the other cannot | ✓ |

**User's choice:** delegated — Claude selected both (D-05).
**Notes:** the meta-test alone proves the predicate is sound but not that the rewritten tests are
wired to a message that actually carries the path; the temporary edit alone proves nothing
durable. SC#2's literal wording ("real runs, not asserted") is only satisfiable by the temporary
edit. A containment rule was attached (D-06): the edit is made, measured and reverted inside one
plan, with `git status --porcelain typsphinx/` recorded empty before that plan commits — a dirty
`typsphinx/` at commit time is a halt, not a deviation. The evidence file was named
`58-DECOUPLING-EVIDENCE.md` rather than `58-VERIFICATION.md`, which `gsd-verifier` reserves and
overwrites wholesale (D-07).

---

## Census scope and artifact

| Option | Description | Selected |
|--------|-------------|----------|
| Enumerate all 341 `repr(` / `!r` occurrences flat | Exhaustive but unclassifiable at that size | |
| Restrict to `assert`-expression occurrences only | Small and precise, but drops the reason the rest are safe | |
| Whole-tree sweep, classified on role × value-type axes | Every occurrence accounted for; only pass-criterion × path must be zero | ✓ |
| Markdown file only | Satisfies SC#3's "written down" literally | |
| Markdown file + AST-based guard test | Snapshot plus a mechanism that detects future incompleteness | ✓ |

**User's choice:** delegated — Claude selected the two-axis sweep plus both artifacts (D-08, D-09).
**Notes:** deriving the enumeration set from the two sites MSG-01 names was rejected outright — it
would inherit the same blind spot the census exists to close. The sweep was **prototyped this
session**: an `ast` walk over every `ast.Assert(...).test` in `tests/**/*.py` returned exactly 9
pass-criterion sites, all `repr()` calls, zero `!r` conversions, of which 2 are path-valued (the
MSG-01 pair) and 7 are identifier/list/bytes/other. A third bucket was added rather than dropped:
*path-valued but format-asserting by design* —
`TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator`, which asserts the
**absence** of `repr()`'s doubled form and which MSG-02's gate depends on. It is recorded in
writing so Phase 60 does not re-litigate it. The guard test must exclude its own file from the
sweep (its allowlist literals contain `repr(` in source form) and must re-derive the count at
runtime rather than hardcoding 9.

---

## Claude's Discretion

All four gray areas were delegated by the owner ("おすすめで進める"), so every decision D-01…D-10
is Claude's recommendation locked as a decision. Explicitly left open for the planner:

- Plan decomposition — D-05's two falsification routes may be one plan or two; the census document
  and its guard test may be one plan or two.
- The exact signature and naming of `path_named_in`, and whether it returns `bool` or raises.
- Whether `58-REPR-CENSUS.md`'s table is generated by the same script that backs D-09's guard.

## Deferred Ideas

- `57-REVIEW.md` IN-01 (a path containing a literal single quote) — belongs to MSG-02's gate in
  Phase 60, which names it explicitly.
- Routing `builder.py:697` / `:1767` off `!r` — Phase 60, MSG-03. Deliberately untouched here so
  "zero test edits in 59/60" stays a meaningful claim.
- Extending the AST guard to `typsphinx/` (a product-side `!r` census) — MSG-03 already enumerates
  the product sites; duplicating it here would pre-empt Phase 60's decisions.

## Todos reviewed, none folded

`todo.match-phase 58` returned four matches; three carry an explicit `resolves_phase` tag pointing
at Phase 59, 60 and 46 respectively, and the fourth is a release-pipeline concern. Folding any of
them would put product code inside a phase whose SC#4 forbids it. Full disposition in
`58-CONTEXT.md` `<deferred>`.
