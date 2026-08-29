# Phase 60: One Delimiter-Aware Path-Quoting Helper, Routed Everywhere - Context

**Gathered:** 2026-08-29
**Status:** Ready for planning

<domain>
## Phase Boundary

One delimiter-aware path-quoting helper exists in a **new leaf module**, and every path-valued
interpolation in `typsphinx/builder.py`, `typsphinx/writer.py` and `typsphinx/template_registry.py`
routes through it. This restores the half of `repr()` that 57-11's hardcoded `'{value}'` dropped —
automatic delimiter selection — while keeping the half it correctly removed (backslash doubling).

- **MSG-02** — the helper: a new leaf module with zero `typsphinx`-internal imports (forced, not
  stylistic — see the placement note below). Accepts `str` **and** `os.PathLike`. Never doubles a
  backslash. Selects a delimiter that cannot appear unescaped in the value, so a path containing a
  literal single quote comes back unambiguously delimited (`57-REVIEW.md` IN-01).
- **MSG-03** — every path-valued interpolation in `builder.py` routes through it: the three
  message builders 57-11 already fixed (`_conf17_violation_message` at `:496`,
  `_templates_path_collision_message` at `:531`, `_bundle_destination_collision_message` at `:572`)
  plus the v0.8.0-era output-path collision family, the docname target-name warnings, the
  image-rehome warning, and the bundle-copy I/O messages.
- **MSG-04** — `writer.py`'s wrapper-render debug log (`:510-514`).
- **MSG-05** — `template_registry.py`'s CONF-17 violation (`:422`) and existence check (`:433`).

**In scope:**

- The helper module + its own unit-test module, then three disjoint wiring changes.
- New test modules only, one per wired product module (SC#4).
- The repo-wide grep that is SC#2's discovery authority, and the SC#3 over-reach audit.

**Out of scope:**

- **Any edit to an existing test assertion under `tests/`** (ROADMAP constraint 9; measured against
  `58-REPR-CENSUS.md`, not claimed). Adding new test *files* is not a test edit.
- **`template_registry.py:410`** — deliberately excluded. Its `template` value is reached precisely
  when it is NOT path-shaped (a `list`, `bytes`, an `int`), so quoting it as a path would be
  actively wrong. SC#3 requires it to be *measurably* still `!r` after the rollout.
- **`TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator`**
  (`tests/test_templates_path_collision_gate.py:445-455`) — path-valued AND format-asserting **by
  design**, `58-REPR-CENSUS.md`'s third bucket. It must not be rewritten and must not be
  re-litigated; MSG-02's own gate depends on it continuing to catch the regression it catches.
- **Identifier-valued `!r`** — docnames, registry keys, config tuples, key lists. Untouched by
  requirement text and by D-02's rule.
- **Any product change to `translator.py`, `template_engine.py`, `pdf.py`, `removed_config.py`,
  `__init__.py`** — outside MSG-03/04/05's named modules.
- Any new runtime dependency, any new `typst_*` config value, any typing-import modernization.

</domain>

<decisions>
## Implementation Decisions

The owner selected **"おすすめで進める"** for all four gray areas, so every D-NN below is Claude's
recommendation locked as a decision — the same disposition Phase 59 carried. Every value marked
*measured* was taken **this session (2026-08-29)** against the live tree at `b7a3e6d5`, not from
recall. **Every line number in this document was re-measured today** — Phase 59 shifted all of
them, so `REQUIREMENTS.md`'s and the ROADMAP's line lists (`697`, `942`…`1015`, `1767`, `2056`,
`2066`) are stale as coordinates while remaining correct as descriptions. This is exactly why SC#2
makes an execution-time repo-wide grep the discovery authority.

### MSG-02 — the helper's delimiter rule and contract

- **D-01: The delimiter rule reproduces `repr()`'s exactly, minus the backslash doubling.**
  Measured `repr()` behaviour today:
  `repr(r"C:\Users\a")` → `'C:\\Users\\a'`;
  `repr("/home/O'Brien/x")` → `"/home/O'Brien/x"`;
  `repr('/tmp/we"ird.png')` → `'/tmp/we"ird.png'`;
  `repr('/tmp/bo\'th"quotes.png')` → `'/tmp/bo\'th"quotes.png'`.
  The helper's rule is therefore: value contains no `'` → wrap in `'…'`; contains `'` and no `"` →
  wrap in `"…"`; contains both → wrap in `'…'` and backslash-escape **only** the `'` characters,
  never the `\` characters. Rationale: `57-REVIEW.md` WR-01's defect is precisely "57-11 lost
  `repr()`'s delimiter selection", so restoring exactly that half is the minimal, checkable fix; it
  matches `research/FEATURES.md`'s table-stakes row and its LOW-cost both-quotes row.
  — **Reversibility:** reversible.

- **D-01a: The helper may emit a backslash of its own, and this does not trip the existing guard.**
  Measured: `_assert_no_doubled_separator` searches `re.findall(r"\\\\+", message)`, which matches
  runs of **two or more** literal backslashes. D-01's both-quotes branch emits a single `\` before
  each `'`, so the guard stays green. Independently, a Windows path can never reach that branch —
  NTFS/Windows refuse `"` in a filename outright — so the both-quotes case is POSIX-only in
  practice, and the escape it introduces can never collide with a Windows separator.
  — **Reversibility:** reversible.

- **D-02: The module is `typsphinx/pathfmt.py` and the function is `quote_path()`, public-named but not re-exported.**
  `research/SUMMARY.md:125` already names `pathfmt.py`; keeping that name means the research, the
  architecture note and the plans all say the same word. No leading underscore, because three
  sibling modules import it. It is **not** added to `__init__.py`'s exports and gets no user-facing
  documentation — this is a bug-fix round with no new capability (ROADMAP constraint 14).
  — **Reversibility:** reversible.

- **D-03: The contract for non-path inputs — `None` renders as bare `None`; `str`/`os.PathLike` are quoted; everything else raises `TypeError`.**
  **Measured and load-bearing:** `writer.py:503` sets `template_file = None` on the package-alone
  path (`if typst_package and not raw_template_path`), so MSG-04's site really does hand the helper
  a `None` on a live build path. Returning the bare four-character string `None` keeps `:513` a
  straight substitution *and* keeps that debug line byte-identical to today's `{template_file!r}`
  output. A conditional in the f-string was rejected: it duplicates the invariant at the one site
  that has it and invites drift. `bytes`/`list`/`int` raise loudly rather than falling back to
  `repr()`, because `template_registry.py:410` is the one production site that can see those types
  and is deliberately excluded — a silent fallback would let a future site route a non-path value
  through the path helper with no gate noticing. This mirrors `tests/_path_naming.py`'s own
  contract, the test-side leaf module Phase 58 wrote as the deliberate mirror of this one.
  — **Reversibility:** reversible.

- **D-04: An empty string is quoted as `''`, NOT refused.**
  Deliberately *unlike* `path_named_in()`, which raises `ValueError` on an empty value. That refusal
  is an assertion-predicate concern (an empty needle matches every haystack vacuously); a formatter
  handed `""` must render something, and `''` is byte-identical to `repr("")`. Recorded because the
  two leaf modules are otherwise deliberate mirrors and a reader will expect them to agree here.
  — **Reversibility:** reversible.

### MSG-03/04/05 — the path-valued vs identifier-valued boundary

- **D-05: The classification rule is the value's ROLE in the message, not its Python type — "does the reader read this as a location on a filesystem, or as a name in a namespace?"**
  A repo-wide grep at execution time is the discovery authority (SC#2); this rule is what the grep's
  hits are then classified by. Its two halves are both load-bearing — SC#2 requires no path-valued
  `!r` left in the three modules, and SC#3 requires the identifier-valued ones measurably untouched.
  — **Reversibility:** reversible.

- **D-06: Routes through `quote_path()` (path-valued), at the sites measured live today.**
  `builder.py`: `resolved_path` + `srcdir` (`:523-526`), `bundle_dir` + `raw_tp_entry` +
  `resolved_tp_entry` (`:557-562`), `dest_dir` (`:594`), `target` + `fallback` (`:890`),
  `relpath` (`:1135`, `:1208`), `content_relpath` + `TEMPLATE_OUTPUT_DIR` (`:1156-1158`),
  `wrapper_relpath` + `TEMPLATE_OUTPUT_DIR` (`:1199-1201`), `resolved_uri` + `key` (`:1943-1944`),
  `src_file` + `dest_file` (`:2231-2232`), `template_filename` + `src_dir` + `dest_dir`
  (`:2241-2242`). `writer.py`: `wrapper_relative_dir`, `include_path`, `template_file`
  (`:511-513`). `template_registry.py`: `template` at `:422` and `:433`.
  — **Reversibility:** reversible.

  **AMENDED 2026-08-29 (post-research, owner-approved).** `60-RESEARCH.md`'s execution-time discovery
  grep found two path-valued sites the enumeration above missed, and the owner elected to fold them
  into this phase rather than defer them. Re-measured by the orchestrator against the live tree:
  `grep -n "{target!r}" typsphinx/builder.py` returns exactly three hits — `:890` (already routed
  above), plus **`:1192`** (`f"target {target!r})"`) and **`:1199`**
  (`f"{docname!r}, target {target!r}) would write its "`). Both live inside
  `_validate_output_path_collisions()`, where `target = entry[1]` is the raw `typst_documents`
  target — **the identical semantic value D-08a already classifies as PATH-valued at `:890`**, merely
  read at a second call site. This is not a contradiction of a locked decision; it is a gap in D-06's
  enumeration, and it is exactly the outcome SC#2 anticipates when it names the execution-time grep,
  not the line list, as the discovery authority. Both sites therefore **route through
  `quote_path()`**, and they belong to `builder.py`'s wave-2 wiring plan (the same function that plan
  already edits for `relpath` at `:1135`/`:1208` and `wrapper_relpath` at `:1199-1201`). Note `:1199`
  is a *mixed* f-string after this amendment: its `docname!r` stays `!r` (D-07) while its `target`
  routes — a second useful mixed site for SC#3's audit alongside D-08d's `:2242`.
  **Zero-test-edit impact, measured:** the only backslash-bearing `typst_documents` targets in the
  suite are in `tests/test_out02_escape_target_gate.py` and its fixture, and that fixture's target is
  *refused* (exit 0 + warning) rather than colliding, so neither `:1192` nor `:1199` ever emits with
  it. Every target reaching a collision message in the suite (`master.typ`, `chapter1.typ`,
  `C:manual`, the `./`-prefixed shapes) renders byte-identically under `repr()` and `quote_path()`.
  No existing test assertion changes.

  **Addendum (plan time, measured):** these two sites need a **type narrowing** that `:890` does not.
  `_is_usable_typst_documents_entry()` (`builder.py:598`) admits an entry on `len(entry) >= 2` and
  `isinstance(entry[0], str)` alone — its own docstring spells the check as
  `not entry or len(entry) < 2 or not isinstance(entry[0], str)` — so it places **no** constraint on
  `entry[1]`. A config typo like `typst_documents = [("index", None, "T", "A")]` therefore reaches
  both sites, and `:1192`'s `_claim` description is built on **every** build, not only on collision.
  Because `quote_path()` raises `TypeError` on a non-`str` by D-03, an *unconditional* route would
  turn a today-warned config typo into an unhandled crash. Both sites therefore bind
  `target_text = quote_path(target) if isinstance(target, str) else repr(target)` once and
  interpolate that — still routed exactly as this amendment decided, with the non-path branch falling
  back to the pre-existing `!r` rendering. `:890` needs no such guard: its warning already sits
  inside an `isinstance(target, str)` branch.
  — **Reversibility:** reversible.

- **D-07: Stays `!r` (identifier-valued), and SC#3's audit measures exactly these.**
  Registry keys (`key`, `existing_key`, `declared_key`, `RESERVED_REGISTRY_KEY`, and every
  `f"{key!r}: {message}"` summary joiner at `builder.py:1565`/`:2410` and throughout
  `template_registry.py:113-132`/`:305-376`/`:514-526`); docnames (`docname` everywhere, including
  the ones sharing an f-string with a routed `target`); config tuples (`entry` at `builder.py:1181`,
  `doc_tuple` at `:2538`/`:2566`); key lists (`sorted(registry.keys())`); and
  `template_registry.py:410`'s `template`. Also `writer.py:154-155` — **measured**: `entry[0]` is a
  docname, and `value`/`default` are a title or author string resolved from `config.project` /
  `config.author` (`writer.py:135-157`), so nothing there is path-valued and MSG-04's restriction to
  `:511-513` is correct as written, not an oversight.
  — **Reversibility:** reversible.

- **D-08: Four boundary calls the rule decides, each with its reason, so no executor has to re-derive them.**
  (a) **`target` and `fallback` are PATH-valued.** `target` is the raw `typst_documents` target,
  which `_escapes_outdir()` itself treats as path-bearing, and `fallback` is
  `posixpath.basename(fallback_source)` (`builder.py:874`) — a surviving path component. Confirmed
  from the other direction by ROADMAP constraint 2, which states this exact site goes RED on POSIX
  the instant it is rewired: `tests/test_out02_escape_target_gate.py:134` pins
  `target = "C:\escape.typ"`. MSG-01 already decoupled it via `path_named_in()`, whose raw-value
  disjunct stays true under D-01's output.
  (b) **`TEMPLATE_OUTPUT_DIR` is PATH-valued.** The tie is broken by the message's own words —
  `"whose first path segment is {TEMPLATE_OUTPUT_DIR!r}"`. Output is byte-identical either way
  (`repr("_template")` == `'_template'` == `quote_path("_template")`), so this cannot break a test;
  routing it removes a judgement call from SC#2's grep audit.
  (c) **The image-rehome `key` at `:1944` is PATH-valued, and is NOT the "registry key" SC#3
  protects.** After Phase 59 it is `_typst_converted/{sha1[:8]}-{basename}` — a relative path with a
  separator. `REQUIREMENTS.md` names this site (as line 1767) as an MSG-03 site explicitly. Record
  the distinction so an executor reading SC#3's "registry keys still render with `!r`" does not skip
  it. Its sibling `resolved_uri` is the value `tests/test_builder.py:598` pins, also already
  decoupled by MSG-01.
  (d) **`template_filename` at `:2242` is PATH-valued.** The message names a file
  (`"registry key {key!r} ({template_filename!r}) was never copied from …"`); the source todo lists
  it under path-valued. Its `key` sibling in the same f-string stays `!r` — a useful mixed site for
  SC#3's audit.
  — **Reversibility:** reversible.

### Plan decomposition, waves, and evidence

- **D-09: Four waves — helper, then three wiring plans IN PARALLEL, then acceptance.**
  Wave 1: `typsphinx/pathfmt.py` + its own test module. No existing file is edited, so nothing can
  collide. Wave 2: three plans, one per product module (`builder.py` / `writer.py` /
  `template_registry.py`), each carrying its own new test module (SC#4) and asserting **only on its
  own module's output**. Wave 3: acceptance — SC#2's repo-wide grep, SC#3's over-reach measurement,
  SC#5's zero-test-edit proof against `58-REPR-CENSUS.md`, and the fresh 3-OS CI dispatch on the
  post-fix tip. Constraint 4 ("a plan that changes an emitted string and a plan that asserts on that
  string must not share a wave") is satisfied because each wave-2 plan changes and asserts within
  itself; no wave-2 plan asserts on a sibling's strings. The audit is one wave *later* than what it
  audits, deliberately — an auditing plan sharing a wave with its subject abstains from its own SC.
  — **Reversibility:** reversible.

- **D-10: Evidence files are PER PLAN, named `60-0N-EVIDENCE.md`, consolidated read-only in wave 3.**
  This is the single change that buys wave 2's parallelism. Phase 59 was forced to one plan per wave
  for five waves *not* by its code files — `translator.py` was parallel-safe — but because every
  plan appended to one D-11-named evidence file and would have collided there at merge with disjoint
  code. Wave 3's acceptance plan writes `60-PATH-QUOTING-EVIDENCE.md` by *referencing* the four
  per-plan files, never by rewriting them. **No file in this phase may be named
  `60-VERIFICATION.md`** — that is a name `gsd-verifier` reserves and overwrites wholesale (59 D-11,
  58 D-07, the `57-MESSAGE-FIX-EVIDENCE.md` precedent).
  — **Reversibility:** reversible.

- **D-11: MSG-02's gate lives in the helper's OWN new test module; the three wiring gates live in three further new modules; `TestWindowsPathEscapingRegressionGuard` is EXTENDED by exactly one plan.**
  SC#1's two halves (no backslash doubling; a literal single quote comes back unambiguously
  delimited) are properties of `quote_path()` and are gated by calling it directly in wave 1 — they
  do not need a build. SC#4's "the existing property is extended to the newly-routed sites" is
  `builder.py`'s wiring plan's job and only its job: it is the only wave-2 plan permitted to touch
  `tests/test_templates_path_collision_gate.py`, and it touches it by **adding** methods to
  `TestWindowsPathEscapingRegressionGuard`, never by modifying `_assert_no_doubled_separator` or any
  existing method. `writer.py`'s and `template_registry.py`'s coverage goes in their own new
  modules, which is what makes the three wave-2 plans mergeable.
  — **Reversibility:** reversible.

- **D-12: Each wiring plan records its own RED against the unfixed tree, in the shape its site allows.**
  For the sites still on `!r` (everything except the three 57-11 builders), RED is the doubled
  backslash. For the three 57-11 builders, RED is the *single-quote* case — the backslash half is
  already green there, so a backslash-only assertion would be tautologically green and prove
  nothing. `writer.py`'s site is a `logger.debug` call, so its gate reads it via `caplog` at DEBUG
  level (the suite already uses `caplog` in ten-plus modules). `template_registry.py`'s two sites
  raise `ExtensionError`, so their gate reads `str(excinfo.value)`; its `template` value may be a
  `pathlib.Path`, whose pre-fix rendering is `PosixPath('…')` — a second, independent RED shape.
  — **Reversibility:** reversible.

### Claude's Discretion

The owner delegated all four gray areas, so the planner additionally retains discretion on:
- Test-module and fixture naming (beyond D-11's placement rule), and the internal decomposition of
  wave 2's three plans.
- Whether `quote_path()` takes an optional keyword for a caller-forced delimiter (default: it does
  not — no call site in D-06 needs one, and adding one widens MSG-02 beyond "select delimiter,
  interpolate raw", which `research/FEATURES.md` explicitly warns against).
- The exact idiom for the both-quotes branch, provided D-01's output is byte-identical to `repr()`'s
  minus the backslash doubling.
- How wave 3 consolidates the four per-plan evidence files, provided D-10's read-only rule holds.

### Folded Todos

`todo.match-phase 60` returned seven matches; **one folded** — it is the source record for all four
of this phase's requirements:

- `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` (score 0.60, area: builder,
  writer, template_registry; `resolves_phase: 60`) — "Path quoting in user-facing messages is
  unfinished on BOTH sides: path-valued `!r` still doubles backslashes at the sites 57-11 did NOT
  touch, and the three sites it DID fix lost `repr()`'s quote-disambiguation for paths containing a
  literal single quote." Its part-1 census is MSG-03/04/05 and its part-2 (`57-REVIEW.md` WR-01) is
  MSG-02's second half. Its own "Suggested fix, part 2" is D-01 verbatim. Closing MSG-02..MSG-05
  closes both halves of this todo, which is why it was filed as one record.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone-binding documents
- `.planning/ROADMAP.md` § "🚧 v0.9.1 — Windows path correctness (ACTIVE)" — the 14 binding
  constraints. Bearing directly on this phase: **1** (RED-first; "CI green" is evidence of nothing),
  **2** (MSG-01 is what makes zero test edits achievable here; `research/SUMMARY.md`'s finding #4 is
  **superseded** and must not be re-litigated), **4** (a plan changing an emitted string and a plan
  asserting on it must not share a wave — see D-09), **6** (the new-leaf-module placement is forced,
  with the measured import-cycle reason), **9** (zero test edits), **10** (CI is not first
  discovery: local RED→green, then a fresh 3-OS dispatch on the post-fix tip), **11** (worktree
  isolation is standing), **14** (no new dependency, no new `typst_*` value, no typing
  modernization).
- `.planning/ROADMAP.md` § "Phase 60" — the five success criteria this CONTEXT.md is scoped to.
- `.planning/REQUIREMENTS.md` **MSG-02** (lines 91-107, including the forced-placement note),
  **MSG-03** (108-115), **MSG-04** (116-118), **MSG-05** (119-124); § "Out of Scope for v0.9.1"
  (line 186 — the `template_registry.py:410` exclusion with its reason); § "Standing constraints for
  every phase in this milestone" (230-243).

### The source record
- `.planning/todos/pending/2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` —
  **folded.** Both problem sections and both "Suggested fix" sections. Part 2's reproduction command
  is a ready-made RED probe for the single-quote half.

### Prior-phase artifacts this phase is bound to
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-REPR-CENSUS.md` — **the enumeration
  the zero-test-edit claim is checked against** (ROADMAP constraint 9), *and* its § "Third bucket"
  naming `TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator` as
  must-not-be-rewritten and must-not-be-re-litigated by **this phase specifically**.
- `tests/test_repr_census_guard.py` — the AST guard that re-derives the census at run time. If it
  goes RED after a plan here touches a test file, the census was incomplete; re-derive it, never
  quietly append to `PASS_CRITERION_REPR_ALLOWLIST`.
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-CONTEXT.md` § D-11 (the
  reserved-`VERIFICATION.md` rule D-10 inherits) and § Deferred Ideas (which hands this phase the
  `57-REVIEW.md` IN-01 single-quote case explicitly).
- `.planning/phases/59-…/59-WINDOWS-URI-EVIDENCE.md` — the evidence-file shape D-10 follows, and the
  reason the relocation `key` at `builder.py:1944` now has the value it has.

### Research (written 2026-08-27)
- `.planning/research/ARCHITECTURE.md` § (a) "Where the delimiter-aware path-quoting helper must
  live" — the measured import-cycle argument behind constraint 6; and its § 172/178 note on the
  shared-test-class hazard D-11 resolves.
- `.planning/research/FEATURES.md` lines 199-221 — the delimiter-selection design space, including
  the both-quotes robustness row (D-01) and the three explicitly-rejected alternatives (bare `!r`,
  hardcoded `'…'`, full shell-style escaping).
- `.planning/research/PITFALLS.md` — Pitfall 2 (a `bytes` `template` reaching a string-only helper,
  behind D-03), Pitfall 3 (`os.PathLike` values), and lines 329-330 (the reader-facing symptom of a
  path that closes its own quote, and of a leaked `PosixPath(…)` wrapper).
- `.planning/research/SUMMARY.md:125-135` — the A/E/F plan units and the `pathfmt.py` name D-02
  keeps. Its Key Finding #2 ("two test edits are expected and required") is **superseded** by
  MSG-01/Phase 58 and must not be re-litigated.

### Code under change
- `typsphinx/builder.py:496-597` — the three 57-11 message builders, each with a docstring stating
  the quoting rule it must follow. Those docstrings are part of the change surface: they currently
  say "quoted with explicit `'...'`, never `!r`" and must be updated to name the helper.
- `typsphinx/builder.py:840-922` — `_resolve_target_stem()`'s `fallback` construction and the three
  docname/target warnings (D-08a).
- `typsphinx/builder.py:1130-1210` — the v0.8.0-era output-path collision family.
- `typsphinx/builder.py:1940-1946` — the image-rehome warning (D-08c).
- `typsphinx/builder.py:2220-2245` — the bundle-copy I/O messages (D-08d).
- `typsphinx/writer.py:498-514` — the `template_file = None` branch and the debug log (D-03).
- `typsphinx/template_registry.py:405-437` — `:410` (excluded, with its own three-point comment
  explaining why `str` AND `os.PathLike` are both accepted), `:422`, `:433`.

### Project standing rules
- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run` for every executor.
- `pyproject.toml` `[tool.pytest.ini_options]` — `filterwarnings` promotes `DeprecationWarning` /
  `PendingDeprecationWarning` to errors; a new test module must not trip them.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/_path_naming.py` — `path_named_in()`, Phase 58's leaf test-support module, written
  explicitly as the mirror of MSG-02's leaf discipline. Its docstring already names "MSG-02's
  delimiter-aware helper" as the third quoting regime it must hold across, and its two-disjunct rule
  (raw value in text, or `repr()` of it in text) is what keeps the two MSG-01 sites green under
  D-01's output without a test edit. **Read it before writing `quote_path()`** — D-03 and D-04 are
  deliberate agreements and one deliberate disagreement with it.
- `tests/test_templates_path_collision_gate.py:412-490` — `TestWindowsPathEscapingRegressionGuard`,
  with its `WINDOWS_SHAPED_PATH` / `WINDOWS_SHAPED_SRCDIR` constants and the docstring rule *call
  the real message-construction function, never a re-pasted f-string*. D-11 extends this class by
  addition only.
- `caplog` — already used in ten-plus test modules (`tests/test_builder.py`,
  `tests/test_track_image_key_construction.py`, `tests/test_copy_image_files_name_too_long.py`, …);
  it is how MSG-04's `logger.debug` site is gated (D-12).
- `os.fspath`, `posixpath` (stdlib) — everything `quote_path()` needs. **Zero new dependencies.**

### Established Patterns
- **One function is the ONE place a message sentence is built.** `_conf17_violation_message()` and
  its two siblings exist precisely so a unit test can call the real construction code with a
  Windows-shaped string rather than a re-pasted f-string. `quote_path()` is the same idea one level
  down; the wiring must not paste the delimiter logic inline anywhere.
- **Leaf modules carry zero package-internal imports**, on both the product side (MSG-02) and the
  test side (`tests/_path_naming.py`). Proven standalone by importing the module on its own — SC#1
  requires exactly that, not just a source read.
- **Windows shapes are hand-built string literals tested on every lane**, never gated on `os.name`.
  This whole phase is POSIX-runnable by construction: every gate is a pure string assertion or a
  `caplog`/`ExtensionError` read, so nothing needs the `windows-latest` lane to go RED first.

### Integration Points
- `builder.py` imports `writer.py` at module scope (`builder.py:29`); `template_registry.py` avoids a
  cycle with `builder.py` only via a lazy function-scoped import (its own comment at ~`:86-90` says
  so). `pathfmt.py` importing nothing from `typsphinx` is what makes all three able to import it.
- `builder.py:1944`'s `key` is the value Phase 59 just changed (`_typst_converted/{digest}-…`).
  ROADMAP constraint 4 is why this phase quotes it and Phase 59 did not — the value settled first.
- `tests/test_out02_escape_target_gate.py:134` and `tests/test_builder.py:598` are the two MSG-01
  sites, and they pin exactly the two values D-08a and D-08c route. They are the phase's live proof
  that MSG-01 did its job: both must stay green with zero edits.
- `template_registry.py:422`/`:433`'s existing tests (`tests/test_template_registry.py:485-641`,
  `:831-896`) assert on substrings — `"CONF-17"`, `"does not exist"`, `"must be a path string"` —
  never on the quoted form. **Measured**: zero test edits is achievable at MSG-05's sites.

</code_context>

<specifics>
## Specific Ideas

1. **Line numbers in `REQUIREMENTS.md` and the ROADMAP are stale coordinates.** Phase 59 shifted
   every one of them: `697 → 890`, `942…1015 → 1135…1208`, `1767 → 1943-1944`, `2056/2066 →
   2231/2241`, and the three message builders `~329-402 → 496-597`. They remain correct as
   *descriptions*. Discovery must be a fresh repo-wide grep (SC#2 says so); use D-06's list only as
   a cross-check that the grep found at least as much.

2. **The single-quote RED and the backslash RED are different halves, and the three 57-11 builders
   only have the first one.** A wiring plan that records a backslash-doubling RED at
   `_templates_path_collision_message()` has recorded nothing — that site stopped doubling in Phase
   57. The todo's own reproduction line
   (`m('mykey', "/home/O'Brien's Projects/_templates/nested", '_templates', '...')`) is the RED probe
   for those three.

3. **`None` really reaches MSG-04's helper.** `writer.py:503` sets `template_file = None` whenever a
   package is configured with no custom template. A `quote_path()` that raises on `None` turns a
   supported build shape into a crash inside a debug log — the worst possible place to find it.
   D-03's `None → "None"` also keeps that line byte-identical, so it cannot regress a caplog
   assertion that does not exist yet.

4. **Do not "finish the job" at `template_registry.py:410`.** It will look like an oversight sitting
   two lines above two routed siblings. SC#3 makes leaving it alone a *measured pass criterion* — the
   audit asserts it is still `!r`. `research/PITFALLS.md:299` records the cosmetic asymmetry as
   always acceptable.

5. **Extending `TestWindowsPathEscapingRegressionGuard` is a one-plan privilege.** Three parallel
   plans each appending methods to that one class is the exact hazard `research/ARCHITECTURE.md:172`
   names and this project has already paid for once. D-11 gives the privilege to `builder.py`'s plan
   alone; the other two write their own modules.

6. **The zero-test-edit claim is checked against `58-REPR-CENSUS.md` and the live AST guard, not
   asserted.** SC#5's proof is a measured diff over the phase's own range plus a green
   `tests/test_repr_census_guard.py` — the same two-tree shape 57-11, 58 and 59 all used.

</specifics>

<deferred>
## Deferred Ideas

- **`typsphinx/translator.py`'s path-valued `!r`, if any exists.** MSG-03/04/05 name three modules
  and SC#2's grep is scoped to those three. The source todo's own census classified `translator.py`'s
  `master_docname!r` / `path[0]!r` / `path[-1]!r` as **docnames despite the variable name**, i.e.
  identifier-valued and correctly `!r` — so there is likely nothing to do. Record rather than widen
  the grep's scope mid-phase; if the wave-3 audit's grep is run repo-wide and surfaces a genuine
  path-valued site in a fourth module, file it as a new requirement.

- **A caller-forced delimiter keyword on `quote_path()`.** No site in D-06 needs one, and
  `research/FEATURES.md:221` explicitly warns against letting the helper grow past "select
  delimiter, interpolate raw". Deferred with the note that a future site needing a
  Typst-string-literal escape should call `translator.py`'s `escape_typst_string()` instead — that
  is a different job with a different correctness bar.

- **Re-exporting `quote_path()` from `typsphinx/__init__.py` or documenting it.** Out of scope by
  ROADMAP constraint 14 (no new user-facing capability this round). Would be a v2 consideration only
  if third-party builders ever need it.

- **Carried forward from Phase 59, still not in scope here:** the drive-relative colon in a
  relocation key (59 D-12), and the non-escape key branches carrying a backslash on POSIX
  (`builder.py:1783` region). Both are IMG-family value defects, not quoting defects.

### Reviewed Todos (not folded)

`todo.match-phase 60` returned six further matches, **none folded** — all score 0.60 on generic
keyword overlap and none touches MSG-02..MSG-05:

- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — CI/release; belongs to Phase 61's
  neighbourhood at most, and REL-09 closes at `/gsd-complete-milestone`.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — local toolchain; CI remains the lint
  authority.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` —
  translator numbering, a separate defect family.
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — CI/tooling.
- `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` — docs.
- `2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` — a translator emission
  defect filed today; a real bug, but an `image()` *separator* problem, not a message-quoting one.
  Not in v0.9.1's requirement set.

</deferred>

---

*Phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere*
*Context gathered: 2026-08-29*
