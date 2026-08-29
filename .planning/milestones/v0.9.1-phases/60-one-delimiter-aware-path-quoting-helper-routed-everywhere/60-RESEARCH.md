# Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere - Research

**Researched:** 2026-08-29
**Domain:** Python string-formatting helper (stdlib-only), routed into three existing Sphinx-extension
modules; zero new runtime behavior beyond message text.
**Confidence:** HIGH — every claim below is either a direct `Read` of the live tree at commit
`a0232ea7` (working tree clean, `gsd/v0.9.1-windows-path-correctness`), a `.venv`-executed Python
measurement against that tree, or a locked CONTEXT.md decision restated for traceability. This phase's
own scoping instructions correctly predict that the design space is already closed — this document is
a measurement report, not a design exploration.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: The delimiter rule reproduces `repr()`'s exactly, minus the backslash doubling.** Value
  contains no `'` → wrap in `'…'`; contains `'` and no `"` → wrap in `"…"`; contains both → wrap in
  `'…'` and backslash-escape **only** the `'` characters, never the `\` characters.
- **D-01a:** The both-quotes branch's own escape (`\'`) never trips
  `_assert_no_doubled_separator`'s `re.findall(r"\\\\+", message)` guard (needs 2+ consecutive
  backslashes; D-01a emits exactly one), and is POSIX-only in practice (NTFS refuses `"` in a
  filename).
- **D-02:** The module is `typsphinx/pathfmt.py`, function `quote_path()`, public-named but not
  re-exported from `__init__.py`, no leading underscore (three sibling modules import it).
- **D-03:** `None` renders as bare `None`; `str`/`os.PathLike` are quoted; everything else (`bytes`,
  `list`, `int`, …) raises `TypeError`. Load-bearing: `writer.py:503` really does hand the helper a
  live `None` on the package-alone build path.
- **D-04:** An empty string is quoted as `''`, NOT refused (deliberately unlike
  `tests/_path_naming.py`'s `path_named_in()`, which raises `ValueError` on empty).
- **D-05:** Classification rule — value's ROLE in the message ("filesystem location" vs. "namespace
  name"), not its Python type. A repo-wide grep at execution time is SC#2's discovery authority; D-05
  is what the grep's hits are then classified by.
- **D-06:** The routed (path-valued) site list as measured at CONTEXT-gathering time (2026-08-29,
  before this session's re-measurement — see § "Repo-Wide Discovery Grep" below for the
  execution-time authority this research adds).
- **D-07:** The stays-`!r` (identifier-valued) site list, plus the explicit note that
  `writer.py:154-155` (`entry[0]`, `value`, `default`) is identifier/title/author-valued, not
  path-valued.
- **D-08:** Four named boundary calls: (a) `target`/`fallback` in `_resolve_target_stem()` are
  PATH-valued; (b) `TEMPLATE_OUTPUT_DIR` is PATH-valued; (c) the image-rehome `key` at (measured)
  `:1944` is PATH-valued and is NOT the "registry key" SC#3 protects; (d) `template_filename` is
  PATH-valued.
- **D-09:** Four waves — helper (wave 1), three wiring plans in parallel (wave 2, one per product
  module), acceptance (wave 3).
- **D-10:** Evidence files are per-plan, `60-0N-EVIDENCE.md`, consolidated read-only in wave 3. No
  file in this phase may be named `60-VERIFICATION.md`.
- **D-11:** MSG-02's gate lives in the helper's own new test module; the three wiring gates live in
  three further new modules; `TestWindowsPathEscapingRegressionGuard` is extended by exactly ONE plan
  (`builder.py`'s), by addition only.
- **D-12:** Each wiring plan records its own RED in the shape its site allows — doubled-backslash for
  everything except the three 57-11 builders, single-quote for those three; `caplog` for `writer.py`;
  `str(excinfo.value)` for `template_registry.py`, including the `PosixPath('…')` leak shape.

### Claude's Discretion

- Test-module and fixture naming (beyond D-11's placement rule), and internal decomposition of wave
  2's three plans.
- Whether `quote_path()` takes an optional caller-forced-delimiter keyword (default: it does not).
- The exact idiom for the both-quotes branch, provided output is byte-identical to `repr()` minus
  backslash doubling.
- How wave 3 consolidates the four per-plan evidence files, provided D-10's read-only rule holds.

### Deferred Ideas (OUT OF SCOPE)

- `typsphinx/translator.py`'s path-valued `!r`, if any exists — SC#2's grep is scoped to
  `builder.py`/`writer.py`/`template_registry.py` only. The source todo already classified
  `translator.py`'s `master_docname!r`/`path[0]!r`/`path[-1]!r` as docname-valued, not path-valued.
- A caller-forced delimiter keyword on `quote_path()` — no D-06 site needs one.
- Re-exporting or documenting `quote_path()` — out of scope by ROADMAP constraint 14 (no new
  user-facing capability this round).
- The drive-relative colon in a relocation key (59 D-12) and non-escape-branch backslash-on-POSIX
  key components (`builder.py:1783` region) — value defects, not quoting defects.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MSG-02 | The delimiter-aware helper: new leaf module, zero `typsphinx`-internal imports, accepts `str`/`os.PathLike`, never doubles a backslash, disambiguates a literal single quote. | § "Import-Cycle Confirmation", § "D-01 Byte-Identity Measurement", § "D-03 Contract Pitfall" below give the exact contract and the one implementation trap a naive reading of D-03 would miss. |
| MSG-03 | Every path-valued interpolation in `builder.py` routes through the helper. | § "Repo-Wide Discovery Grep" is the full classified census, cross-checked against D-06/D-07 with **one divergence found and reported**. |
| MSG-04 | `writer.py`'s wrapper-render debug log routes through the helper. | § "RED Reproduction — `writer.py`" gives the measured `caplog` RED shape (11 doubled-backslash runs) and the `None`-safe path. |
| MSG-05 | `template_registry.py`'s CONF-17 violation and existence check route through the helper; `:410` stays excluded. | § "RED Reproduction — `template_registry.py`" gives both `str(excinfo.value)` RED shapes (doubled-backslash and the `PosixPath('…')` leak), and § "Zero-Test-Edit Achievability" proves `:410`'s two guarding tests (`repr(["a","b"])`/`repr(b"base.typ")`) stay green untouched. |
</phase_requirements>

## Summary

This phase's design is entirely closed by CONTEXT.md's twelve locked decisions; the only research
value is measurement. This session re-ran the repo-wide discovery grep SC#2 names as the authority,
classified every hit under D-05's role-based rule, and cross-checked the result against D-06/D-07.
**One real divergence was found**: `builder.py`'s `_validate_output_path_collisions()` interpolates
the raw `typst_documents` target (`target = entry[1]`) with `!r` at two sites — lines **1192** and
**1199** — that are the exact same semantic value D-08a already classifies as path-valued at line
890, but neither line is named in D-06's enumerated list. This is not a contradiction of a locked
decision (D-05's rule, applied faithfully, points the same direction D-08a already reasoned from); it
is exactly the kind of gap the CONTEXT itself predicted the execution-time grep would need to catch.

Every other line D-06/D-07 name was independently re-derived and matches exactly. D-01's delimiter
rule was verified byte-identical to `repr()` minus backslash-doubling across the four CONTEXT-cited
cases plus the empty string, `None`, and one further edge case this session added (a value carrying
BOTH a backslash and both quote characters) — no divergence found. The import-cycle argument behind
constraint 6 (D-02's forced placement) was confirmed by reading all three modules' import blocks
directly. Zero-test-edit achievability (SC#5) was checked site-by-site against the actual existing
test assertions; every one is either a substring check that survives quoting-style changes, an
`ExtensionError`-class-only check with no message assertion, or (at the two MSG-01 sites) the new
`path_named_in()` predicate, which was independently verified to hold across all four of D-01's
delimiter branches, including the double-escaping branch, via its `repr()`-form disjunct.

**Primary recommendation:** implement `quote_path()` exactly to D-01/D-03/D-04's letter, route the
D-06 list PLUS the two divergent `target!r` sites at `builder.py:1192,1199`, and implement the
`bytes`-rejection half of D-03 by mirroring `tests/_path_naming.py`'s own idiom (`os.fspath()` then an
explicit `isinstance(result, str)` check) rather than relying on `os.fspath()` alone to raise —
measured this session: `os.fspath(b"foo")` returns `b"foo"` **unchanged**, it does not raise.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Delimiter-aware path quoting (`quote_path()`) | API/Backend (library internals) | — | Pure string-formatting helper consumed only by the extension's own builder/writer/registry modules; no client, no I/O, no config surface. |
| Message construction (`builder.py`'s three 57-11 functions, and the inline sites) | API/Backend | — | Sphinx extension internals — logs and raised `ExtensionError`s consumed by the Sphinx build process, never rendered to an end-user UI. |
| Debug logging (`writer.py`'s `logger.debug`) | API/Backend | — | Developer-facing diagnostic output via Python's `logging`, captured by `caplog` in tests. |
| Registry validation errors (`template_registry.py`) | API/Backend | — | Raised at `resolve_template_registry()` time, before any file is written — a `conf.py`-authoring-time feedback loop, not a runtime API. |

This phase has no browser, SSR, CDN, or database tier — it is a single-process, stdlib-only
string-formatting change inside a Sphinx builder extension. `ui.plan-gate`'s standing false-positive on
this milestone (noted in every phase's `**UI hint**: no` line) applies here too.

## Repo-Wide Discovery Grep

**Grep commands used** (reusable verbatim as SC#2's execution-time audit):

```bash
grep -n "!r" typsphinx/builder.py typsphinx/writer.py typsphinx/template_registry.py
grep -n "repr(" typsphinx/builder.py typsphinx/writer.py typsphinx/template_registry.py
grep -n "%r" typsphinx/builder.py typsphinx/writer.py typsphinx/template_registry.py
grep -noE "'\{[a-zA-Z_.]+\}'" typsphinx/builder.py typsphinx/writer.py typsphinx/template_registry.py
```

The first three find every `!r`/`repr(`/`%r`-style interpolation (raw counts at measurement time:
40 lines in `builder.py`, 5 in `writer.py`, 21 in `template_registry.py` — line-count, not
occurrence-count, since several lines carry two interpolations). The fourth finds the three already-
`!r`-decoupled 57-11 message builders' hardcoded `'{value}'` sites, which carry the delimiter-
selection defect (D-01's whole reason for existing) without using `!r` at all — a plain `!r` grep
would miss them entirely. **No `%r` occurrences exist in any of the three modules.**

Every hit was read in its surrounding function (not just the grep line) and classified under D-05's
rule: does the reader read this value as a filesystem location, or as a name in a namespace? The full
classified result, organized by module:

### `typsphinx/builder.py` — PATH-valued (route through `quote_path()`)

| Line(s) | Value(s) | Function | D-06/D-08 match |
|---------|----------|----------|------------------|
| 524, 526 | `resolved_path`, `srcdir` (hardcoded `'…'`) | `_conf17_violation_message()` | ✓ D-06 |
| 558, 560, 561 | `bundle_dir`, `raw_tp_entry`, `resolved_tp_entry` (hardcoded `'…'`) | `_templates_path_collision_message()` | ✓ D-06 |
| 594 | `dest_dir` (hardcoded `'…'`) | `_bundle_destination_collision_message()` | ✓ D-06 |
| 890 | `target`, `fallback` | `_resolve_target_stem()` | ✓ D-06/D-08a |
| 1135 | `relpath` | `_validate_output_path_collisions()` (`_claim()` closure) | ✓ D-06 |
| 1157 | `content_relpath` | `_validate_output_path_collisions()` | ✓ D-06 |
| 1158 | `TEMPLATE_OUTPUT_DIR` | `_validate_output_path_collisions()` | ✓ D-06/D-08b |
| **1192** | **`target`** (`= entry[1]`, the raw `typst_documents` target) | `_validate_output_path_collisions()` | **⚠ NOT in D-06's list — see § "Divergence" below** |
| **1199** | **`target`** (same variable, second message site) | `_validate_output_path_collisions()` | **⚠ NOT in D-06's list** |
| 1200 | `wrapper_relpath` | `_validate_output_path_collisions()` | ✓ D-06 |
| 1201 | `TEMPLATE_OUTPUT_DIR` | `_validate_output_path_collisions()` | ✓ D-06/D-08b |
| 1208 | `relpath` (failures-list joiner) | `_validate_output_path_collisions()` | ✓ D-06 |
| 1943 | `resolved_uri` | `_track_image()` (image rehome warning) | ✓ D-06 |
| 1944 | `key` (the relocation path, NOT a registry key) | `_track_image()` | ✓ D-06/D-08c |
| 2232 | `src_file`, `dest_file` | bundle file copy (`_copy_bundle_directory` region) | ✓ D-06 |
| 2241 | `template_filename` | bundle file copy | ✓ D-06/D-08d |
| 2242 | `src_dir`, `dest_dir` | bundle file copy | ✓ D-06 |

**24 individual path-valued interpolations across 16 lines** (14 `!r` lines + the 6 hardcoded-quote
lines counted once, minus overlaps where a line carries two values).

### `typsphinx/builder.py` — identifier-valued (stays `!r`, untouched)

`key`/`existing_key`/`declared_key`/`RESERVED_REGISTRY_KEY` at 523, 557, 592, 593, 1470, 1471, 1479,
1565, 2224, 2231, 2241 (the `key` half only — its `template_filename` sibling on the same line routes),
2410; `docname` at 884, 885, 905 (×2), 918 (×2), 1151, 1156, 1191, 1198, 2551, 2583; `entry` (whole
tuple) at 1181; `doc_tuple` at 2538, 2566 (plus the two `repr(doc_tuple)`/`repr(docname)` calls at
2539/2554, same identifier class).

### Divergence found (SC#2's execution-time discovery authority at work)

`_validate_output_path_collisions()` (`builder.py:1059-1213`) extracts `target = entry[1]` from each
usable `typst_documents` entry (line 1187, mirroring the exact same raw config value
`_resolve_target_stem()` receives as its own `target` parameter — the value D-08a already reasons
about: *"`target` is the raw `typst_documents` target, which `_escapes_outdir()` itself treats as
path-bearing"*). That reasoning applies identically here — this is the SAME value, read at a
different call site, describing a collision or a reserved-directory violation in a message the reader
reads as naming a location. It is interpolated with `!r` twice: once in the `_claim()` description at
line 1192 (`f"target {target!r})"`), and once in the reservation-failure message at line 1199
(`f"{docname!r}, target {target!r}) would write its "`). Neither line appears in D-06's enumerated
site list, and neither appears in D-07's identifier-valued exclusion list either — it is a gap in the
enumeration, not a contested classification. **Recommendation: the `builder.py` wiring plan routes
`builder.py:1192` and `builder.py:1199`'s `target!r` through `quote_path()` alongside the D-06 list,
by the same D-08a reasoning already locked for line 890.** This does not contradict any locked
decision — D-05's rule, honestly applied, already gives this answer; it was simply not enumerated.

### `typsphinx/writer.py`

| Line(s) | Value(s) | Classification |
|---------|----------|-----------------|
| 154 | `entry[0]` | Identifier (docname) — stays `!r` |
| 155 | `value`, `default` | Identifier (title/author string, per D-07's own measured note) — stays `!r` |
| 511 | `docname` | Identifier — stays `!r` |
| 512 | `wrapper_relative_dir` | PATH — route |
| 513 | `include_path`, `template_file` | PATH — route (`template_file` may be `None`, see D-03) |

No divergence from D-06/D-07 in this module.

### `typsphinx/template_registry.py`

| Line(s) | Value(s) | Classification |
|---------|----------|-----------------|
| 113, 115, 118, 123, 127, 129, 132, 332, 340, 341, 363, 376, 410 (the `key` half), 422 (the `key` half), 433 (the `key` half), 514, 524 | `key` (registry key, in every form) | Identifier — stays `!r` |
| 305 | `declared` (a non-`dict` truthy value: `list`, `int`, …) | Non-path type — stays `!r` |
| 364 | `raw_definition` (a non-`dict` truthy value) | Non-path type — stays `!r` |
| **410** | `template` | **Deliberately excluded (MSG-05's own text) — reached only when `template` is NOT `str`/`os.PathLike`** — stays `!r`, this is a *measured pass criterion* of SC#3, not an oversight |
| **422** | `template` | PATH — route (CONF-17 violation) |
| **433** | `template` | PATH — route (existence check) |
| 516, 526 | `sorted(registry.keys())` | Identifier (key list) — stays `!r` |

No divergence from D-06/D-07 in this module. `template_registry.py:323`'s `repr(k)` is a **sort key**,
not a message interpolation — outside SC#2's scope entirely (it never reaches a user-facing string).

## Standard Stack

### Core

No new dependency of any kind — `os.fspath()` and string formatting are the entire implementation
surface (ROADMAP constraint 14, measured: `typsphinx/pathfmt.py`'s planned import block needs nothing
beyond stdlib `os`).

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A hand-rolled delimiter selector | `shlex.quote()` | Rejected by `research/FEATURES.md`'s explicitly-rejected-alternatives row — shell-quoting semantics (POSIX `'…'` with embedded `'\''`) do not match D-01's `repr()`-derived contract and would change output shape for every existing test. |
| A hand-rolled delimiter selector | Bare `repr()` | Rejected — this is precisely the half of `repr()` 57-11 correctly removed (backslash doubling); reintroducing it regresses the whole milestone. |

**Installation:** none — no `pip install`/`uv add` step in this phase.

## Package Legitimacy Audit

Not applicable — this phase introduces zero new packages, per ROADMAP constraint 14 and confirmed by
the Standard Stack section above (stdlib-only).

## Architecture Patterns

### System Architecture Diagram

```
conf.py (typst_documents, typst_document_templates)
        │
        ▼
TypstBuilder.write()/finish()  ──┐
        │                        │  writer.py: TypstWriter.translate()
        │  (path-shape decisions,│         │
        │   collision checks,    │         ▼
        │   bundle copy)         │  logger.debug(wrapper_relative_dir=…,
        │                        │            include_path=…, template_file=…)
        ▼                        │         │
logger.warning(...) /            │         │
raise ExtensionError(...)        │         │
        │                        │         │
        └────────────┬───────────┴─────────┘
                      ▼
        every path-valued f-string argument
                      │
                      ▼
        typsphinx/pathfmt.py :: quote_path(value)
        (new leaf module — imports NOTHING from typsphinx)
                      │
                      ▼
        delimiter-selected, non-doubled string
        substituted back into the log/warning/error message
                      │
                      ▼
        Sphinx's own logging/error-reporting surface
        (terminal output, captured by caplog / subprocess stdout in tests)

template_registry.py :: resolve_template_registry()
        │  (CONF-17 check, existence check)
        ▼
raise ExtensionError(...) ──► same quote_path() call, same output surface
```

The diagram's single arrow into `pathfmt.py` from three independent call sites (`builder.py`,
`writer.py`, `template_registry.py`) IS the architectural point of this phase: today three modules each
independently decide how to quote a path, with `builder.py`'s three 57-11 functions using one
(incomplete) convention and everything else using `!r`. After this phase, all three funnel through one
function with one contract.

### Recommended Project Structure

```
typsphinx/
├── pathfmt.py         # NEW — quote_path(), zero typsphinx-internal imports
├── builder.py          # MSG-03: 16 lines wired to quote_path() (14 !r-decoupled +
│                        #         6 hardcoded-quote-decoupled, D-06 list plus 1192/1199)
├── writer.py            # MSG-04: 2 lines (512, 513) wired
└── template_registry.py # MSG-05: 2 lines (422, 433) wired; :410 deliberately untouched
tests/
├── test_pathfmt.py                       # NEW — MSG-02's own gate (D-11)
├── test_templates_path_collision_gate.py # EXTENDED (builder.py's plan only, D-11) —
│                                          #   TestWindowsPathEscapingRegressionGuard gains
│                                          #   methods, _assert_no_doubled_separator untouched
├── test_writer_path_quoting_gate.py      # NEW (name is Claude's discretion, D-11)
└── test_template_registry_path_quoting_gate.py # NEW (name is Claude's discretion, D-11)
```

### Pattern 1: One function is the ONE place a message sentence is built

**What:** `_conf17_violation_message()`, `_templates_path_collision_message()`, and
`_bundle_destination_collision_message()` already exist so a unit test can call the real
construction code with a Windows-shaped string, never a re-pasted f-string (`builder.py:496-595`,
verified this session by `Read`). `quote_path()` is the same discipline one level down.

**When to use:** Every wiring site. Never inline the delimiter-selection logic at a call site — always
call `quote_path(value)`.

**Example (measured this session, D-01's reference implementation, verified against all cited cases
plus one added combined-edge case):**

```python
# Verified 2026-08-29 against Python 3.12's repr() on the live tree's interpreter.
def quote_path_ref(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    # both present: wrap in single quotes, escape ONLY the single quote
    escaped = value.replace("'", "\\'")
    return f"'{escaped}'"
```

Measured outputs (this session, `.venv` Python 3.12):

| Input | `quote_path_ref()` output | `repr()` output (for comparison) |
|-------|---------------------------|-----------------------------------|
| `C:\Users\a` | `'C:\Users\a'` | `'C:\\Users\\a'` (doubled — the defect D-01 fixes) |
| `/home/O'Brien/x` | `"/home/O'Brien/x"` | `"/home/O'Brien/x"` (identical) |
| `/tmp/we"ird.png` | `'/tmp/we"ird.png'` | `'/tmp/we"ird.png'` (identical) |
| `/tmp/bo'th"quotes.png` | `'/tmp/bo\'th"quotes.png'` | `'/tmp/bo\'th"quotes.png'` (identical) |
| `""` (empty) | `''` | `''` (identical) |
| `C:\both'quotes"here` (added edge case: backslash AND both quote types) | `'C:\both\'quotes"here'` | `'C:\\both\'quotes"here'` (repr DOUBLES the backslash here — this is the one case that would silently fail if an implementation naively delegated to `repr()` after stripping doubled backslashes as a post-process, rather than building the escape from D-01's stated rule directly) |

No divergence found between D-01's stated rule and this reference implementation across any measured
case, including the combined edge case added this session. **This is a positive validation — no
`⚠ Measurement contradicts a locked decision` heading is needed for D-01.**

### Anti-Patterns to Avoid

- **Relying on `os.fspath()` alone to reject `bytes`:** measured this session —
  `os.fspath(b"foo")` returns `b"foo"` **unchanged** (type `bytes`), it does **not** raise. Only
  `list`/`int`/other truly-unfspathable types raise from `os.fspath()` itself. A `quote_path()` that
  does `value = os.fspath(value)` and then proceeds to `"'" in value` will crash with a confusing
  native `TypeError: a bytes-like object is required, not 'str'` deep inside the delimiter-selection
  logic instead of D-03's clean, intentional `TypeError` at the boundary. **Mirror
  `tests/_path_naming.py:50-55`'s exact idiom**: call `os.fspath(value)`, then explicitly
  `isinstance(value_str, str)`-check the RESULT, and raise `TypeError` yourself if it fails. See
  "Common Pitfalls" below.
- **Handling `None` with a branch inside the caller's f-string** instead of inside `quote_path()`
  itself — CONTEXT.md D-03 already rejected this ("duplicates the invariant at the one site that has
  it and invites drift"). `quote_path(None)` must itself return the string `"None"`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Delimiter-safe quoting of an arbitrary string | A regex-based sanitizer, or shell-style quoting (`shlex.quote`) | D-01's two-branch rule (mirrors `repr()` minus backslash doubling) | `research/FEATURES.md` lines 199-221 already surveyed and rejected the alternatives; `shlex.quote()` produces POSIX shell-escaped output (`'can'"'"'t'`), not a `repr()`-shaped diagnostic string, and would break every existing substring-matching test that expects the value's raw characters to survive. |

**Key insight:** this is a formatting problem with exactly one already-measured, already-verified
correct algorithm (D-01). There is no complexity here that would justify a library — the entire
"library" is an 8-line function.

## Common Pitfalls

### Pitfall 1: `os.fspath()` does not reject `bytes`

**What goes wrong:** A `quote_path()` implementation that trusts `os.fspath()` to enforce D-03's
`TypeError`-on-non-path-non-str contract will silently accept a `bytes` value, then crash later (or
worse, produce a mangled message) when the delimiter-selection logic tries a `str`-only operation
(`"'" in value`) against a `bytes` object.

**Why it happens:** `os.fspath()`'s actual contract (measured this session) is "accept `str`, `bytes`,
or `os.PathLike`, and return whichever of `str`/`bytes` the input already was (calling `__fspath__()`
first if it's `PathLike`)" — it is NOT "coerce everything to `str`, rejecting what it can't." `bytes`
passes straight through.

**How to avoid:** `value_str = os.fspath(value)` then `if not isinstance(value_str, str): raise
TypeError(...)` — the exact two-line idiom `tests/_path_naming.py:50-55`'s `path_named_in()` already
uses for the same reason, stated in its own docstring. `list`/`int`/etc. are already caught by
`os.fspath()`'s own native `TypeError` before this check is even reached (measured this session:
`os.fspath(["a","b"])` and `os.fspath(42)` both raise directly).

**Warning signs:** A test driving `quote_path(b"some/path")` raises anything other than a clean
`TypeError` from `quote_path()` itself, or does not raise at all.

### Pitfall 2: The `target!r` divergence at `builder.py:1192`/`:1199`

**What goes wrong:** A wiring plan that routes exactly D-06's enumerated list and nothing else leaves
two path-valued `!r` sites unrouted, failing SC#2's "no path-valued `!r` left in those three modules"
bar even though every line D-06 named was correctly handled.

**Why it happens:** D-06's list was compiled from the CONTEXT-gathering session's own grep, which
apparently enumerated `_resolve_target_stem()`'s `target` at line 890 but not
`_validate_output_path_collisions()`'s separate `target = entry[1]` extraction at lines 1187-1199 —
same underlying config value, different call site, easy to miss in a manual enumeration.

**How to avoid:** Run this phase's own repo-wide grep (§ "Repo-Wide Discovery Grep" above) as the
actual discovery step, not just a cross-check against D-06's list — exactly what SC#2's own text
already instructs ("A repo-wide grep run at execution time — not the line list above — is the
discovery authority").

**Warning signs:** `grep -n "!r" typsphinx/builder.py` after the wiring plan lands still shows a
`target!r` occurrence anywhere in `_validate_output_path_collisions()`.

### Pitfall 3: `pathlib.Path.__repr__()` leaking as `PosixPath('…')`

**What goes wrong:** `template_registry.py`'s Test H (`test_pathlike_template_field_still_resolves`)
proves a `pathlib.Path`-typed `template` is a supported, working shape. If such a `Path` fails the
existence check at line 433, the CURRENT (pre-fix) message leaks Python's internal `PosixPath('…')`
wrapper to the user — measured this session:
`registry key 'mykey''s template PosixPath('/some/path/_templates/nested') does not exist`. This is
D-12's SECOND independent RED shape for this site (the first being ordinary backslash-doubling for a
`str` template).

**Why it happens:** `repr(pathlib.Path(...))` always renders the class name wrapper; `quote_path()`
must call `os.fspath(value)` FIRST (converting the `Path` to its plain string form) before applying
D-01's delimiter logic, or the leak persists even after routing.

**How to avoid:** `quote_path()`'s `str`/`os.PathLike` branch must normalize via `os.fspath()` before
any quote-character inspection — never quote a `Path` object's own `repr()`.

**Warning signs:** A gate driving a `pathlib.Path`-typed `template` through the existence check and
asserting `"PosixPath" not in str(excinfo.value)` fails.

## Import-Cycle Confirmation (constraint 6 / D-02)

Read directly from the live tree this session (`typsphinx/builder.py:1-30`,
`typsphinx/writer.py:1-27`, `typsphinx/template_registry.py:1-100`):

- `builder.py` imports `typsphinx.pdf`, `typsphinx.template_registry`, `typsphinx.translator`, and
  `typsphinx.writer` — all **at module scope** (`builder.py:23-29`).
- `writer.py` imports `typsphinx.template_engine`, `typsphinx.template_registry`, and
  `typsphinx.translator` — all **at module scope** (`writer.py:15-25`).
- `template_registry.py` imports `typsphinx.builder.TypstBuilder` — but **only inside
  `_has_case_collision()`'s function body** (`template_registry.py:92`), with the function's own
  docstring explaining why: *"Imported locally (not at module scope) to avoid a circular import:
  `builder.py` imports this module at its own module scope, so importing `typsphinx.builder` back at
  THIS module's scope would deadlock the import graph."*

**Measured consequence:** placing `quote_path()` in `builder.py` would force `writer.py` to import it
from `builder.py` — but `builder.py` already imports `writer.py` at module scope, so this is an
immediate, unconditional two-file cycle (`builder ↔ writer`). Placing it in `writer.py` would force
`template_registry.py` to import from `writer.py` — but `writer.py` already imports
`template_registry.py` at module scope, producing the identical cycle one module over
(`writer ↔ template_registry`). A brand-new leaf module with **zero** `typsphinx`-internal imports is
the only placement all three can import from without touching any existing edge in this graph — D-02's
`pathfmt.py` is exactly that, and this session's read confirms the constraint is real, not
speculative.

`pathfmt.py` **may** import: `os` (for `os.fspath()`). It **may not** import anything under
`typsphinx.*` — not even `typsphinx.template_registry`, despite that module having the least
restrictive existing import graph (see above), because D-02 requires provable zero-import leaf status,
verified by importing the module standalone (SC#1's own text).

## Zero-Test-Edit Achievability

Checked against the actual assertions in every test this session identified as exercising a routed
site (not merely believed to — each grep result below was read):

| Site | Existing test(s) | Assertion form | Survives `quote_path()`? |
|------|-------------------|-----------------|-----------------------------|
| `builder.py:890` (`target`/`fallback`) | `tests/test_out02_escape_target_gate.py` | `path_named_in(target, warning_lines[0])` (post-Phase-58 rewrite) | ✓ — `path_named_in`'s `repr()`-form disjunct exactly covers D-01's both-quotes escape branch (see analysis below) |
| `builder.py:1943` (`resolved_uri`) | `tests/test_builder.py:592,597` | `"could not rehome image URI" in message` (substring) and `path_named_in(abs_uri, message)` (post-Phase-58 rewrite) | ✓ |
| `builder.py:1157/1158/1200/1201` (`TEMPLATE_OUTPUT_DIR`, `content_relpath`, `wrapper_relpath`) | `tests/test_typst_documents_collision_gate.py` | `"_template/index" in combined_output` / `"reserved" in combined_output` (substring on forward-slash-only values — no backslash, no quote char, unaffected by delimiter choice) | ✓ |
| `builder.py:1192/1199` (`target`, the divergent sites) | `tests/test_builder_output_stem.py:391-460` | `pytest.raises(ExtensionError)` with **no message assertion at all** | ✓ trivially |
| `writer.py:511-513` | none found (no existing test drives this debug log at all) | n/a — genuinely new coverage | ✓ (nothing to break) |
| `template_registry.py:422` (`template`, CONF-17) | `tests/test_template_registry.py:485-521` | `"CONF-17" in str(excinfo.value)` (substring only) | ✓ |
| `template_registry.py:433` (`template`, existence) | `tests/test_template_registry.py:592-641` | `"does not exist" in str(excinfo.value)` (substring only) | ✓ |
| `template_registry.py:410` (excluded) | `tests/test_template_registry.py:485-492` (list) and `:497-506` (bytes) | `assert repr(["a", "b"]) in message` / `assert repr(b"base.typ") in message` — **these are the live regression proof that `:410` must stay `!r`**; routing `:410` would break both | N/A — `:410` is not routed (SC#3 requires it stays `!r`, and these two tests are the falsification gate for accidentally routing it) |

**`path_named_in()` compatibility with `quote_path()`'s both-quotes escape branch — verified by
construction this session:** `path_named_in()` checks `value_str in text or repr(value_str) in text`.
For a value containing both quote characters (D-01's third branch), `quote_path()`'s output is DEFINED
to be byte-identical to `repr(value_str)` (D-01: "wrap in `'…'` and backslash-escape only the `'`
characters" — exactly `repr()`'s own behavior in that branch, since the divergence between D-01 and
`repr()` is ONLY the backslash-doubling half, which this branch's example values don't otherwise
exercise differently). So `repr(value_str) in text` is true whenever `quote_path()` used this branch,
and `path_named_in()`'s second disjunct catches it even though the first disjunct (`value_str in
text`) is false (the raw value's un-escaped single quote is not literally present once
`quote_path()` has inserted a backslash before it). No new test-side change is needed for this.

**Overall conclusion: SC#5's zero-test-edit claim is achievable at every site this session checked,
including the two divergent sites this research adds to the routed set.**

## RED Reproduction — the three 57-11 message builders (single-quote case, D-12)

Measured this session (`.venv` Python 3.12, calling the REAL functions, not re-pasted f-strings):

```python
>>> _conf17_violation_message("mykey", "/home/O'Brien/x", "/srcdir")
"typst_document_templates: registry key 'mykey''s resolved template '/home/O'Brien/x' has a "
"parent directory that is srcdir itself, or an ancestor of srcdir ('/srcdir') -- put the "
"template in its own subdirectory (CONF-17, A-01)"
```

The value `/home/O'Brien/x` is wrapped in the hardcoded `'…'` and its own internal `'` visually closes
the quote early — `'/home/O'Brien/x'` reads as an empty-then-broken quote to a human eye, exactly the
`57-REVIEW.md` IN-01 defect. The todo's own reproduction line for
`_templates_path_collision_message()` was also run and produces the identical shape:

```python
>>> _templates_path_collision_message(
...     "mykey", "/home/O'Brien's Projects/_templates/nested",
...     "_templates", "/srcdir/_templates")
"registry key 'mykey''s resolved template bundle directory '/home/O'Brien's Projects/_templates/"
"nested' collides with the Sphinx templates_path entry '_templates' (resolved to "
"'/srcdir/_templates') -- ..."
```

`re.findall(r"\\\\+", message)` returns `[]` for all three functions on this input — confirming D-12's
claim that the backslash-doubling gate is ALREADY green here (these three sites' backslash-doubling
defect was 57-11's fix) and only the single-quote-disambiguation half is available as RED for these
three specific sites. A wiring plan that records a backslash-doubling RED at any of these three
functions has recorded nothing meaningful.

## RED Reproduction — `builder.py`'s other sites (doubled-backslash case, D-12)

```python
>>> from typsphinx.builder import _build_relocation_key
>>> resolved_uri = r"C:\Users\a\image.png"
>>> key = _build_relocation_key(resolved_uri)   # post-Phase-59 key construction
>>> key
'_typst_converted/db149fb1-image.png'           # separator-free, per IMG-04/IMG-06
>>> message = (f"could not rehome image URI {resolved_uri!r} relative "
...            f"to the doctree directory -- relocated to {key!r}")
>>> re.findall(r"\\\\+", message)
['\\\\', '\\\\', '\\\\']   # THREE doubled runs -- the RED
```

Confirms `resolved_uri!r` still doubles all three of the Windows path's backslashes (RED, as
expected), while the post-Phase-59 `key` value itself carries no backslash (Phase 59's fix already
holds) — but `key` should still be routed through `quote_path()` for the delimiter-selection half
(D-08c), since a converted image whose original basename happened to carry a literal single quote
would otherwise reproduce the same IN-01-class defect one level down.

## RED Reproduction — `writer.py`

```python
>>> message = (f"Rendering wrapper for docname {docname!r} at "
...            f"wrapper_relative_dir={wrapper_relative_dir!r}, "
...            f"include_path={include_path!r}, template_file={template_file!r}")
>>> # with docname="manual", the other three = r"C:\Users\a\..." shapes
>>> re.findall(r"\\\\+", message)
['\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\', '\\\\']  # ELEVEN doubled runs
```

This confirms D-12's instruction that `writer.py`'s gate reads via `caplog` at DEBUG level — the
suite already has this pattern in ten-plus modules (`grep -c caplog tests/*.py` counted 12 files this
session with at least one occurrence). The `None` case was also measured:
`f"template_file={None!r}"` → `"template_file=None"` — confirming D-03's contract keeps this line
byte-identical for the package-alone build path, so no `caplog` assertion that does not yet exist can
regress from it.

## RED Reproduction — `template_registry.py`

Two independent RED shapes, both measured this session, both via `str(excinfo.value)` (the pattern
already used in `tests/test_hand_compile_root_gate.py:221`, `tests/test_registry_container_shape_gate.py:140`,
and throughout `tests/test_template_registry.py`):

```python
# Shape 1: an ordinary str template with a Windows-shaped backslash
>>> msg422 = (f"registry key {key!r}'s template {template!r} "
...           "resolves to a parent directory that is srcdir "
...           "itself, or an ancestor of srcdir (CONF-17)")
# template = r"C:\Users\a\_templates\nested"
>>> re.findall(r"\\\\+", msg422)
['\\\\', '\\\\', '\\\\', '\\\\']    # FOUR doubled runs -- RED

# Shape 2: a pathlib.Path template (Test H's supported shape) that does NOT exist
>>> from pathlib import Path
>>> template_path = Path("/some/path/_templates/nested")
>>> f"registry key {key!r}'s template {template_path!r} does not exist"
"registry key 'mykey''s template PosixPath('/some/path/_templates/nested') does not exist"
```

Shape 2's `PosixPath('…')` leak has **no existing test coverage** — every current
`test_user_defined_key_template_names_nonexistent_file_raises`-family test drives a plain `str`
template. This is new coverage the wiring plan must add (see Pitfall 3 above), not a modification of
an existing assertion — it does not threaten SC#5's zero-test-edit bar.

## Code Examples

### The `_assert_no_doubled_separator` guard, read verbatim (D-11's extension target)

```python
# Source: tests/test_templates_path_collision_gate.py:444-453 (read this session)
@staticmethod
def _assert_no_doubled_separator(message: str) -> None:
    """No run of consecutive backslashes longer than 1 may appear --
    that is what ``repr()`` escaping would produce and what this
    guard exists to catch."""
    doubled = re.findall(r"\\\\+", message)
    assert not doubled, (
        f"Expected every backslash run to be a single unescaped "
        f"separator, found a doubled/escaped run in:\n{message!r}"
    )
```

D-01a's claim that the both-quotes branch's single `\` escape never trips this is directly verifiable
from the regex itself: `r"\\\\+"` in a raw Python string matches two-or-more literal backslashes; D-01's
both-quotes branch emits exactly one `\` before each `'`, which can never form a run of 2+ unless the
input value ITSELF already contained a `\` immediately before a `'` — and even then, that would be
`\'` becoming `\\'` (still only 2, at the input's own boundary, not introduced by the escape) — no
combination of D-01's rule and this guard's regex produces a false RED. Confirmed by direct regex
reasoning, not merely restated from CONTEXT.md.

### `path_named_in()`, read verbatim (the test-side mirror `quote_path()` must agree/disagree with per D-03/D-04)

```python
# Source: tests/_path_naming.py:33-62 (read this session)
def path_named_in(value: str | os.PathLike, text: str) -> bool:
    value_str = os.fspath(value)
    if not isinstance(value_str, str):
        raise TypeError(
            f"path_named_in() requires a value that normalizes to str via "
            f"os.fspath(), got {type(value_str).__name__}"
        )
    if value_str == "":
        raise ValueError(
            "path_named_in() refuses an empty value -- an empty value "
            "would match every text vacuously, which is never a "
            "meaningful naming proof"
        )
    return value_str in text or repr(value_str) in text
```

This is the exact idiom Pitfall 1 recommends mirroring for `quote_path()`'s own `bytes`-rejection
(the `isinstance(value_str, str)` check after `os.fspath()`), and it is the reason D-04 deliberately
records `quote_path()`'s DISAGREEMENT with this module on the empty-string case (`path_named_in`
raises `ValueError` on empty; `quote_path` must return `''` instead) — so a reader comparing the two
leaf modules side-by-side does not mistake the disagreement for an inconsistency.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (version pinned via `uv.lock`; `[tool.pytest.ini_options]` in `pyproject.toml:79-101`, read this session) |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, `python_files/classes/functions` standard, `addopts = "-v --strict-markers"`) |
| Quick run command | `uv run pytest tests/test_pathfmt.py -x` (or the equivalent new module per wiring plan) |
| Full suite command | `uv run pytest` |

**Worktree note (CLAUDE.md, standing):** every executor runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree first, then all
commands via `uv run`. This research session ran directly against the main tree's `.venv` (not a
worktree — this is a research/measurement pass, not an execution phase), which is why the commands
above show bare `python3` in the measurement transcripts but `uv run pytest` in the prescribed
executor commands.

**`filterwarnings` constraint (measured, `pyproject.toml:89-101`):** `error::DeprecationWarning` and
`error::PendingDeprecationWarning` are both promoted to hard errors. `pathfmt.py`'s stdlib-only
surface (`os.fspath()`, string methods) carries no deprecation risk on Python 3.12 — confirmed no
`DeprecationWarning` fired during any measurement this session.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|--------------------|--------------|
| MSG-02 | `quote_path()` never doubles a backslash; disambiguates a literal single quote; accepts `str`/`os.PathLike`; rejects `bytes`/`list`/`int` with `TypeError`; `None → "None"`; `"" → "''"`. | unit | `uv run pytest tests/test_pathfmt.py -x` | ❌ Wave 1 |
| MSG-02 (leaf-import proof) | Importing `typsphinx.pathfmt` standalone (e.g. `python -c "import typsphinx.pathfmt"` in isolation) succeeds with no other `typsphinx` module loaded as a side effect. | unit (import-graph) | `uv run python -c "import sys; import typsphinx.pathfmt; assert not any(m.startswith('typsphinx.') and m != 'typsphinx.pathfmt' and m != 'typsphinx' for m in sys.modules)"` | ❌ Wave 1 |
| MSG-03 | `TestWindowsPathEscapingRegressionGuard` extended: the 6 hardcoded-quote sites plus the 14 `!r` sites (D-06 list + the 2 divergent `target` sites) all pass `_assert_no_doubled_separator` on a Windows-shaped input; the three 57-11 builders additionally pass a single-quote-disambiguation assertion. | unit | `uv run pytest tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard -x` | Existing file, ❌ new methods Wave 2 |
| MSG-04 | `writer.py`'s debug log, captured via `caplog` at DEBUG, shows no doubled backslash for a Windows-shaped `wrapper_relative_dir`/`include_path`/`template_file`, and correctly renders `template_file=None` for the package-alone path. | unit (caplog) | `uv run pytest tests/test_writer_path_quoting_gate.py -x` (name is Claude's discretion) | ❌ Wave 2 |
| MSG-05 | `template_registry.py:422`/`:433`'s `ExtensionError` messages, via `str(excinfo.value)`, show no doubled backslash for a `str` template and no `PosixPath('…')` leak for a `pathlib.Path` template; `:410` stays measurably `!r` (the existing `repr(["a","b"])`/`repr(b"base.typ")` assertions stay green, unmodified). | unit | `uv run pytest tests/test_template_registry_path_quoting_gate.py -x` (name is Claude's discretion) | ❌ Wave 2 |

### Sampling Rate

- **Per task commit:** the relevant module's own new test file (`uv run pytest tests/test_pathfmt.py`
  in wave 1; each wiring module's new test file in wave 2).
- **Per wave merge:** `uv run pytest` (full suite) plus `uv run black --check . && uv run ruff check .
  && uv run mypy typsphinx/`.
- **Phase gate:** full suite green, local RED→green recorded for every SC, before the fresh 3-OS CI
  dispatch (ROADMAP constraint 10).

### Wave 0 Gaps

None — the test framework, `caplog` pattern, `pytest.raises(ExtensionError)` pattern, and
`tests/_path_naming.py` leaf-module precedent are all already established in this suite (confirmed by
direct `Read` and `grep` this session). No new fixture or framework install is needed.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|--------------------|
| V2 Authentication | no | N/A — no auth surface in this extension |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes (narrow) | D-03's explicit `TypeError` on non-`str`/non-`PathLike`/non-`None` input is the entire input-validation surface — `quote_path()` never writes to disk, never shells out, and never feeds a value back into a Typst compile (that boundary is `translator.py`'s `escape_typst_string()`, already closed by Phase 59's IMG-05, and explicitly out of scope here per CONTEXT.md's Deferred Ideas). |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Log/message injection via an attacker-controlled path segment (e.g. a malicious filename embedding ANSI escape codes or newline-based log-forging text) | Tampering / Information Disclosure | Out of scope for this phase — `quote_path()`'s job is delimiter selection for HUMAN readability, not sanitization against terminal-escape or log-injection payloads; the values it quotes originate from the local filesystem/`conf.py`, which are already trusted inputs in this extension's threat model (a malicious `conf.py` author already has arbitrary code execution via Sphinx's own extension-loading mechanism). No new attack surface is introduced by this phase relative to the `!r`/hardcoded-`'…'` status quo it replaces — both quote a filesystem path exactly as `repr()` would, with the same (non-)sanitization properties. |
| Type confusion at the helper boundary (a caller accidentally passing a `list`/`int`/`bytes` where a path was expected) | Tampering | D-03's `TypeError`-on-mismatch contract, verified this session to require an EXPLICIT `isinstance` check after `os.fspath()` (see Pitfall 1) rather than relying on `os.fspath()`'s own, incomplete, native rejection. |

No `threats_open` count applies — this phase introduces no new attack surface; it is a strict
readability fix over the existing, already-accepted trust boundary (local filesystem paths / `conf.py`
authorship).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|-----------------|
| — | (none) | — | Every claim in this document was either directly `Read` from the live tree this session, or executed as a Python measurement against the live `.venv`, or is a verbatim restatement of a CONTEXT.md-locked decision (tagged as such). No claim in this document is `[ASSUMED]`. |

**This table is empty — all claims in this research were verified or cited; no user confirmation is
needed beyond CONTEXT.md's already-owner-approved decisions.**

## Open Questions

1. **Should the divergent `target!r` sites at `builder.py:1192`/`:1199` be added to the routed set, or
   should the phase proceed on D-06's literal enumeration and treat the divergence as a follow-up?**
   - What we know: D-05's classification rule, applied honestly, and D-08a's own stated reasoning
     both point to routing them — they are the identical semantic value D-08a already classifies as
     path-valued, read at a second call site.
   - What's unclear: whether the owner would prefer this session's finding folded into this phase
     (since SC#2 explicitly names the execution-time grep, not D-06's list, as the discovery
     authority) or filed as a fast-follow todo to keep this phase's diff minimal.
   - Recommendation: fold it in — SC#2's own text anticipates exactly this outcome ("A repo-wide grep
     run at execution time — not the line list above — is the discovery authority"), the fix is two
     more `!r` → `quote_path()` substitutions inside a function the `builder.py` wiring plan is
     already touching, and leaving it unrouted would fail SC#2 on a technicality after the audit
     grep runs in wave 3.

## Sources

### Primary (HIGH confidence — direct `Read`/execution against the live tree, this session)

- `typsphinx/builder.py` (full file structure via `grep`; lines 1-30, 490-600, 840-925, 1120-1213,
  1925-1954, 2200-2245 read in full)
- `typsphinx/writer.py` (lines 1-30, 125-160, 490-516 read in full)
- `typsphinx/template_registry.py` (lines 1-100, 295-440, 495-529 read in full)
- `tests/_path_naming.py` (read in full)
- `tests/test_templates_path_collision_gate.py:400-492` (read in full)
- `tests/test_out02_escape_target_gate.py`, `tests/test_builder.py`, `tests/test_builder_output_stem.py`,
  `tests/test_template_registry.py` (targeted `grep`/`Read` of every assertion touching a routed site)
- `pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.mypy]`, `[tool.ruff]` sections read in full)
- Live `.venv` Python 3.12 execution: `repr()` behavior across 6 cases, `os.fspath()` behavior on
  `bytes`/`list`/`int`, `_conf17_violation_message()`/`_templates_path_collision_message()`/
  `_bundle_destination_collision_message()` called directly, `_build_relocation_key()` called
  directly, and the `_assert_no_doubled_separator` regex reasoned through directly.

### Secondary (MEDIUM confidence)

- `.planning/phases/60-.../60-CONTEXT.md` — the twelve locked decisions, restated verbatim in
  `<user_constraints>` above per this agent's write contract.
- `.planning/research/{ARCHITECTURE,FEATURES,PITFALLS,SUMMARY}.md` — cited by CONTEXT.md; not
  independently re-verified this session (CONTEXT.md's own instruction: read rather than redo).

### Tertiary (LOW confidence)

- None used this session — no web research was needed (CONTEXT.md's own instruction, confirmed: this
  phase is entirely local measurement).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib-only, zero ambiguity, confirmed by reading the planned module's own
  dependency surface.
- Architecture (import-cycle placement): HIGH — read all three modules' import blocks directly this
  session, cross-checked against the lazy-import comment's own stated rationale.
- Site classification / discovery grep: HIGH — every site independently re-derived from source, one
  genuine divergence found and reported with full reasoning rather than silently absorbed.
- Pitfalls: HIGH — the `os.fspath(bytes)` and `PosixPath` leak pitfalls were both directly executed
  and measured this session, not inferred.

**Research date:** 2026-08-29
**Valid until:** This phase's own tip commit changes under `typsphinx/builder.py`,
`typsphinx/writer.py`, or `typsphinx/template_registry.py` (line numbers are coordinates, not
descriptions — re-grep before trusting them past that point, exactly as this document's own
predecessor CONTEXT.md warns about Phase 59's shift). No external-ecosystem drift risk (stdlib-only).
