# Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-29
**Phase:** 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
**Areas discussed:** delimiter-selection rule, path-vs-identifier boundary, plan decomposition and
evidence, helper contract for non-path values

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| 区切り文字の選定規則 | What the helper emits when a path contains BOTH `'` and `"`; whether the helper may emit a backslash of its own | |
| パス値/識別子値の線引き | The classification rule for the five ambiguous values (`target`/`fallback`, `TEMPLATE_OUTPUT_DIR`, `template_filename`, the image-rehome `key`) | |
| プラン分解と証拠ファイル | Wave shape, and whether per-plan evidence files unlock wave-2 parallelism | |
| 非パス値へのヘルパの契約 | Measured: `writer.py:503` really passes `None`; also `bytes`/`list` behaviour | |
| **おすすめで進める** | **All four delegated to Claude's recommendation** | **✓** |

**User's choice:** 「おすすめで進める」— all four gray areas delegated, the same disposition Phase 59
carried.
**Notes:** No area was re-opened. Every recommendation locked as a D-NN in CONTEXT.md, each with the
measurement it rests on recorded inline rather than asserted.

---

## Alternatives considered and rejected (recorded for audit)

### Delimiter-selection rule (→ D-01, D-01a)

| Option | Description | Selected |
|--------|-------------|----------|
| `repr()`-identical rule | `'` default; `"` when the value contains `'` and no `"`; both → `'…'` with only the `'` characters backslash-escaped | ✓ |
| Never emit a backslash | Pick `"` when `'` is present and accept ambiguity in the both-quotes case | |
| Always `"` with `\"` escaping | Single delimiter, escape it when present | |

Rejected because: `57-REVIEW.md` WR-01's defect *is* the loss of `repr()`'s delimiter selection, so
restoring exactly that half is the minimal checkable fix. Measured that the escape it introduces
cannot trip `_assert_no_doubled_separator` (which matches runs of ≥2 backslashes) and cannot reach a
Windows path at all (NTFS refuses `"` in a filename).

### Path-vs-identifier boundary (→ D-05 … D-08)

| Option | Description | Selected |
|--------|-------------|----------|
| Classify by ROLE in the message | "Does the reader read this as a location, or as a name in a namespace?" | ✓ |
| Classify by Python type / separator-bearing capability | Anything that could contain `os.sep` is path-valued | |
| Treat `REQUIREMENTS.md`'s line list as canonical | Use the grep only as a completeness check | |

The third was rejected outright: SC#2 states the execution-time repo-wide grep is the discovery
authority, and the line list was measured stale today (Phase 59 shifted every coordinate). The
second was rejected as under-determined at the four boundary calls D-08 settles.

### Plan decomposition and evidence (→ D-09 … D-12)

| Option | Description | Selected |
|--------|-------------|----------|
| 4 waves: helper → 3 wirings in parallel → acceptance | Per-plan evidence files; each wiring plan asserts only on its own module | ✓ |
| 3 waves: helper → builder → (writer + registry) | Serializes builder ahead of the other two | |
| Fully sequential (Phase 59's shape) | One plan per wave | |

The sequential shapes were rejected once the cause of Phase 59's serialization was traced: not its
code files (`translator.py` was parallel-safe) but its single shared evidence file. Per-plan evidence
files remove that, and SC#4 independently requires per-module test modules — which is what makes the
three wiring plans mergeable.

### Helper contract for non-path values (→ D-03, D-04)

| Option | Description | Selected |
|--------|-------------|----------|
| `None` → bare `None`; `str`/`os.PathLike` quoted; else `TypeError` | Keeps `writer.py:513` a straight substitution and byte-identical | ✓ |
| Silent `repr()` fallback for anything non-path | Never crashes | |
| Strict `TypeError` on `None` too, with a conditional at the call site | Narrowest contract | |

The silent fallback was rejected because it would let a future site route a non-path value through
the path helper with no gate noticing. The strict variant was rejected because the conditional
duplicates the invariant at the one site that has it. Measured driver: `writer.py:503` sets
`template_file = None` on the package-alone build path, so `None` is live, not hypothetical.

---

## Claude's Discretion

All four gray areas were delegated. CONTEXT.md § "Claude's Discretion" additionally leaves the
planner: test-module and fixture naming beyond D-11's placement rule; the internal decomposition of
wave 2's three plans; whether `quote_path()` grows an optional forced-delimiter keyword (default
recorded as "no"); the exact both-quotes idiom provided D-01's output holds; and how wave 3
consolidates the four per-plan evidence files under D-10's read-only rule.

## Deferred Ideas

- `typsphinx/translator.py`'s path-valued `!r`, if any exists — the source todo's own census
  classified its `master_docname` / `path[0]` / `path[-1]` as docnames, i.e. correctly `!r`.
- A caller-forced delimiter keyword on `quote_path()`.
- Re-exporting or documenting `quote_path()` as public API — barred by ROADMAP constraint 14 this
  round.
- Carried forward from Phase 59 and still not in scope: the drive-relative colon in a relocation key
  (59 D-12), and the non-escape key branches carrying a backslash on POSIX.
- `2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` — a real translator defect
  filed today, but an `image()` separator problem, not a message-quoting one. Not in v0.9.1's
  requirement set.
