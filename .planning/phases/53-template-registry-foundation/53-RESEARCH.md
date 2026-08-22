# Phase 53: Template Registry Foundation - Research

**Researched:** 2026-08-15
**Domain:** Sphinx builder/writer/template-engine integration — adding a validated, resolved-once
config registry that a per-document write path consumes with zero output change
**Confidence:** HIGH

## Summary

This phase's code surface is small and already fully mapped by the milestone-level research
(`ARCHITECTURE.md`, `PITFALLS.md`, `STACK.md`) and locked by `53-CONTEXT.md`'s twelve decisions
(D-01..D-12). This document does **not** re-derive that work. Its job is the phase-scoped delta the
planner cannot get from CONTEXT.md alone: the concrete shape of the new registry-entry dataclass and
its resolver, the exact widening of `TemplateResolution`, the precise placement of D-08's per-key
divergence, the seven CONF-18 predicates as runnable Python, the CONF-17 path-arithmetic expression,
a real reproducible procedure for SC#2's byte-identity evidence (naming actual fixtures on disk), a
re-confirmed count of the "31 test files" claim (measured: **32**, not 31 — see Q7), and the measured
state of the two candidate milestone branches for SC#5.

**Primary recommendation:** build a `typsphinx/template_registry.py` module carrying one frozen
dataclass (`TemplateRegistryEntry`) and one resolver function
(`resolve_template_registry(config) -> dict[str, TemplateRegistryEntry]`), called once in `write()`
right after `_validate_output_path_collisions()` (builder.py:713) and before `prepare_writing()`
(builder.py:716); widen `TemplateResolution` (template_engine.py:37-56) with a fourth field carrying
the resolved `Path`, populated at each of the three existing branches inside `resolve_template()`
rather than via a second method — the only three construction sites are all inside
`resolve_template()` itself (verified: `grep -n "TemplateResolution(" typsphinx/*.py tests/*.py`
returns exactly those three, line 311/324/336, no test constructs it directly), so widening is a
safe, minimal-diff change with zero call-site migration cost.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Registry config declaration (`typst_document_templates`) | Config surface (`__init__.py`) | — | New `app.add_config_value`, mirrors every existing `typst_*` registration |
| Registry validation + built-in-key synthesis | Builder (new `template_registry.py`, orchestrated from `builder.py write()`) | — | Config-shape validation belongs with the OTHER build-wide validators this codebase already runs exactly once (`_validate_output_path_collisions()` precedent); filesystem orchestration is `builder.py`'s existing job, not `template_engine.py`'s |
| Template file resolution (path walk) | Template engine (`template_engine.py`) | — | `resolve_template()`'s three-priority walk already owns this; widened, not duplicated |
| Wrapper construction from resolved definition | Writer (`writer.py render_wrapper()`) | Builder (threads the registry in) | `render_wrapper()` already builds `TemplateEngine`; only its INPUT source changes (definition object vs. raw `config`) |
| CI evidence for SC#5 | Release/CI mechanics (git + GitHub Actions), not application code | — | Push + dispatched workflow run; no `typsphinx/` code involved |

This map is a discovery aid, not a new decision: every row already matches CONTEXT.md D-notes and
`ARCHITECTURE.md` §2's file:line inventory. No capability needs reassignment.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Registry-key shape is validated by **denylist enumeration only** — each of ROADMAP SC#4's
  cases is judged individually and emits its own case-specific error message. No allowlist regex is
  used, not even as a trailing catch-all. This rejects STACK.md's `re.fullmatch(r"[A-Za-z0-9_-]+", key)`
  suggestion in favour of PITFALLS.md's per-case predicate, because SC#3 requires "a message naming the
  specific reason".
- **D-02:** The denylist is **exactly SC#4's seven cases** and nothing more: empty or whitespace-only,
  `.`/`..`, containing `/` or `\`, a Windows reserved device name (case-folded, with or without a
  trailing extension), a trailing dot, a trailing space, and differing from another registered key only
  by case. Windows-illegal characters (`< > : " | ? *`), control characters (0x00–0x1F), a leading dot,
  and interior whitespace all stay **accepted** in Phase 53. Reversibility: costly.
- **D-03:** Registry validation reports errors in the **same shape as `_validate_output_path_collisions()`**
  (accumulate every failure, raise once at the end) but through an **independent** `ExtensionError`.
  Do not merge registry failures into the collision validator's `failures` list; do not change its
  `"typst: N output path collision(s): …"` message text.
- **D-04:** Only the **literal** string `"typst"` is reserved (CONF-16). `"Typst"`/`"TYPST"` pass as
  ordinary user-defined keys, because CONF-18's case-collision check compares **registered** keys
  against each other and the synthesized built-in is not a member of that set. The resulting Phase 54
  bundle-directory collision is deferred.
- **D-05:** Validation covers **every declared key**, not only keys referenced by element [4]. The FS
  existence check costs a few `os.path.isfile` calls, which is not worth an exception. ROADMAP SC#3's
  order-independence then holds trivially.
- **D-06:** An element [4] that is **present but not a `str`** (`None`, `123`, a tuple, …) raises the
  **same CONF-14-class `ExtensionError`** as an unregistered key, naming the offending value and the
  registered keys. It does **not** join `_is_usable_typst_documents_entry()`'s tolerate-and-skip
  contract and is **not** silently coerced to `"typst"`. An **absent** element [4] (a four-element
  tuple) still means `"typst"` per TPL-04.
- **D-07:** CONF-17's predicate rejects when the resolved parent directory **is `srcdir` itself, or is
  an ancestor of `srcdir`**. srcdir's **siblings** (`../shared/tpl.typ`) and absolute paths outside
  srcdir stay legal. Measured: `os.path.join(srcdir, "/abs/x.typ")` yields `/abs/x.typ`. Reversibility:
  costly.
- **D-08:** A registry `template` pointing at a **file that does not exist** raises `ExtensionError`
  **for user-defined keys only**. The built-in `"typst"` key keeps today's behaviour unchanged:
  `resolve_template()` Priority 1 logs `"Custom template not found: … Falling back to default
  template."` and falls through to Priority 2/3 (template_engine.py:308-313). Reversibility: costly.
- **D-09:** CONF-17's predicate is **path arithmetic on the declared value**, independent of whether the
  file exists, so CONF-17 and D-08's existence check are two separate failures that can both be
  reported in the same accumulated raise.
- **D-10:** A user-defined key that **omits** `template_function` does **not** inherit global
  `typst_template_function`. Omission means `None`, which `render()` already resolves to the literal
  `"project"` for both the `#import` line and the `#show:` call (template_engine.py:654, 664). Registry
  definitions are self-contained; TPL-03's built-in-key clause is the only inheritance route.
- **D-11:** Global `typst_template_mapping` is passed to the **`"typst"` key's engine only**, not to
  every key. A user-defined key therefore gets `DEFAULT_PARAMETER_MAPPING`, or `{}` when the definition
  carries a `package`. Reversibility: costly.
- **D-12:** SC#2 is proven by a **one-off evidence artifact only** — `53-RED-EVIDENCE.md` recording
  before/after commit SHAs, per-file SHA-256 of the emitted `.typ` files, and PDF page counts across the
  four existing shapes. **No new golden-file pytest gate is added.** Note the file name —
  `53-VERIFICATION.md` is reserved by `gsd-verifier` and must not be used for evidence.

### Claude's Discretion

- Where the registry resolver lives — `ARCHITECTURE.md` §2 recommends a new
  `typsphinx/template_registry.py`, keeping `template_engine.py` pure content/parameter logic and
  `builder.py` filesystem orchestration.
- The exact widening of `TemplateEngine.resolve_template()` so the resolved `Path` is recoverable — a
  new field on `TemplateResolution` versus a separate `resolve_template_path()` method. Constraint:
  must stay the **single** priority walk, never a second independently-written lookup.
- How the once-per-build resolution result reaches `render_wrapper()` — a builder attribute threaded
  like `self._master_include_edges` versus a new parameter.
- Exact error message wording, subject to SC#3's "names the specific reason" and CONF-14's "the error
  names the registered keys".
- Test file naming and placement.

### Deferred Ideas (OUT OF SCOPE)

- **Phase 54 — `"Typst"` vs `"typst"` bundle collision.** D-04 accepts `"Typst"` as an ordinary
  user-defined key; the resulting `<outdir>/_template/<key>/` collision on case-insensitive filesystems
  is Phase 54's problem.
- **Later phase — Windows-illegal and control characters in registry keys.** D-02 leaves
  `< > : " | ? *` and 0x00–0x1F accepted. Cheap to add later; deliberately not in Phase 53.
- **Adjacent cleanup (not this milestone's responsibility).** `writer.py:170-216`
  `_compute_template_import_path()` is dead code (zero non-docstring callers), superseded by
  `compute_template_import_path_for_dir()`. Not to be confused with the function Phase 54 needs to
  generalize.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| TPL-01 | Named template definitions in `typst_document_templates`, `template` xor `package`, optional `template_function` | Q1 (registry entry shape + resolver), Q1's TemplateEngine constructor-argument mapping table |
| TPL-03 | Built-in `"typst"` key resolves to existing global config, zero-edit equivalence | Q1 (synthesis of the built-in entry), Q6 (byte-identity evidence procedure) |
| TPL-04 | Four-element tuple behaves identically to fifth element `"typst"` | Q1 (default-key resolution), D-06 (absent vs. non-str element [4]) |
| TPL-05 | Several `typst_documents` entries share one registry key | Q1 (dict-keyed resolution — no per-entry re-validation) |
| CONF-14 | Unregistered key stops the build, error names registered keys | Q3 (validator placement), D-06 |
| CONF-15 | Entry carrying both `template` and `package` stops the build | Q1 (validator xor-check) |
| CONF-16 | User-defined `"typst"` key stops the build | Q1 (validator reserved-key check), D-04 |
| CONF-17 | `template` pointing directly under `srcdir` stops the build | Q5 (path-arithmetic predicate) |
| CONF-18 | Registry-key shape unsafe as single path segment stops the build | Q4 (seven predicates as runnable Python) |
</phase_requirements>

---

## Q1 — The registry data structure and its resolver

### Recommended shape

```python
# typsphinx/template_registry.py (NEW MODULE)

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TemplateRegistryEntry:
    """One resolved `typst_document_templates` entry -- either declared by
    the user or synthesized for the reserved "typst" key. Carries exactly
    the fields `render_wrapper()` needs to build a `TemplateEngine` with no
    further lookup against `config`.
    """

    key: str
    template: str | None
    """srcdir-relative path string, exactly as declared (or synthesized
    from global `typst_template` for the "typst" key). `None` when the
    entry carries `package` instead."""

    package: str | None
    """Typst Universe package spec, exactly as declared (or synthesized
    from global `typst_package` for the "typst" key, already passed
    through `resolve_package_for_engine()`'s routing rule). `None` when
    the entry carries `template` instead."""

    template_function: Any | None
    """`str` or `{"name": str, "params": dict}`, passed straight to
    `TemplateEngine.__init__`'s `typst_template_function` parameter
    unmodified -- that constructor already parses both shapes
    (template_engine.py:251-264)."""


def resolve_template_registry(config) -> dict[str, TemplateRegistryEntry]:
    """Validate every declared `typst_document_templates` entry (D-05) and
    return the full resolved registry, including the synthesized "typst"
    key. Raises ExtensionError, once, accumulating every failure
    (D-03/D-05), for: template+package both set (CONF-15), a user-defined
    "typst" key (CONF-16), a key whose shape fails the CONF-18 denylist
    (Q4), a `template` failing CONF-17's path-arithmetic check (Q5), and a
    user-defined key's `template` that does not exist on disk (D-08/D-09).
    Called once from `write()`, after `_validate_output_path_collisions()`
    and before `prepare_writing()` -- mirrors
    `self._master_include_edges = self._build_include_edge_map()`
    (builder.py:730)."""
```

The unregistered-key check (CONF-14) is **not** this function's job — it fires when an ENTRY's
element [4] names a key absent from this returned dict, which is `_write_typst_files()`'s wrapper loop
(builder.py:1074-1092), not the registry resolver itself. `resolve_template_registry()` validates the
registry's own declared shape; a second, small check at the wrapper-loop call site (or inside a thin
`resolve_key(registry, entry) -> TemplateRegistryEntry` helper) raises CONF-14 by looking up
`entry[4] if len(entry) > 4 else "typst"` against the resolved dict and raising, naming
`sorted(registry.keys())`, on a miss. Because D-05 already validates every key up front, this lookup
can never itself discover a NEW validation failure — it only asks "is this key present" — so it stays
a plain `dict.get()`-with-raise, not a second validation pass.

### TemplateEngine constructor-argument mapping (writer.py:344-352, template_engine.py:202-211)

`render_wrapper()`'s current `TemplateEngine(...)` call takes exactly these 7 arguments. For each,
whether it now comes from the resolved `TemplateRegistryEntry` or stays a plain global-`config` read:

| Constructor argument | Today (writer.py:344-352) | Phase 53 source | Per-key or global |
|---|---|---|---|
| `template_path` | `os.path.join(srcdir, raw_template_path)` if `typst_template` set, else `None` | `os.path.join(srcdir, entry.template)` if `entry.template` set, else `None` | **Per-key** (synthesized from global `typst_template` for `"typst"`) |
| `template_name` | not passed (defaults to `"base.typ"`) | unchanged — not passed | Global (unaffected; not a registry field) |
| `search_paths` | `[self.builder.srcdir]` | unchanged | Global — every key's Priority-2 search still checks `<srcdir>/base.typ` |
| `parameter_mapping` | `getattr(config, "typst_template_mapping", None)` | `getattr(config, "typst_template_mapping", None)` **only when `entry.key == "typst"`**, else `None` | **Per-key**, effectively global-only (D-11) — `None` for every user-defined key, which `TemplateEngine.__init__` then resolves to `DEFAULT_PARAMETER_MAPPING` or `{}` per its own existing package-branch logic (template_engine.py:230-238) |
| `typst_package` | `resolve_package_for_engine(typst_package, raw_template_path)` | `resolve_package_for_engine(entry.package, entry.template)` — same helper, same rule, now fed per-key values | **Per-key** (synthesized from global `typst_package`/`typst_template` for `"typst"`) |
| `typst_template_function` | `getattr(config, "typst_template_function", None)` | `entry.template_function` | **Per-key** (D-10: no inheritance for user-defined keys; synthesized from global for `"typst"`) |
| `typst_package_imports` | `getattr(config, "typst_package_imports", None)` | unchanged | **Global** — Out of Scope table locks this explicitly |

The `"typst"` entry is synthesized by `resolve_template_registry()` as:
`TemplateRegistryEntry(key="typst", template=getattr(config, "typst_template", None), package=getattr(config, "typst_package", None), template_function=getattr(config, "typst_template_function", None))`
— i.e. read the same three globals `_write_template_file()` (builder.py:1124-1132) and today's
`render_wrapper()` (writer.py:324-325, 350) already read, unmodified. Because every downstream
consumer (`os.path.join`, `resolve_package_for_engine()`) is fed the identical values it is fed today
for this one key, wrapper output is byte-for-byte unchanged (TPL-03's zero-edit-equivalence).

## Q2 — `TemplateEngine.resolve_template()` widening

**Recommendation: widen `TemplateResolution` with a fourth field, populated inline at each of the
three existing branches. Do not add a separate `resolve_template_path()` method.**

Measured, not assumed: `grep -n "TemplateResolution(" typsphinx/*.py tests/*.py` returns exactly three
hits, all inside `resolve_template()` itself (template_engine.py:311, 324, 336) — no test or other
call site constructs a `TemplateResolution` directly. Widening the dataclass therefore has **zero
call-site migration cost**: every existing consumer (`load_template()`, which reads only `.content`;
`tests/test_template_engine.py`'s `TestTemplateResolutionProvenance` class, which reads only `.source`)
keeps working unmodified.

```python
@dataclass(frozen=True)
class TemplateResolution:
    content: str
    source: str
    path: Path | None
    """The resolved template's own file path -- `self.template_path` at
    Priority 1, `Path(search_dir) / self.template_name` at Priority 2,
    `Path(get_default_template_path())` at Priority 3. `None` only for a
    hypothetical fourth caller that never resolves a file at all (no
    branch in `resolve_template()` itself produces this; the field stays
    Optional only because a package-only TemplateEngine, which this
    method is never called for today, would have no template to resolve
    -- deliberately typed for that future caller without adding one)."""
```

The alternative (a separate `resolve_template_path()` method) fails the class's own documented
constraint two ways: either it re-implements the three-branch walk independently (the literal
duplication CONF-07/D-06 forbids — see template_engine.py:290-295's docstring), or it becomes a thin
wrapper that calls `resolve_template()` and extracts a path from its result — at which point
`TemplateResolution` must already carry the path, making the separate method redundant scaffolding
around the widened-dataclass approach anyway. There is no version of "separate method" that avoids
duplicating the walk without first widening the dataclass, so the discretion resolves cleanly in
favour of the field.

## Q3 — D-08's per-key divergence: where does the branch live?

**In the registry validator (`resolve_template_registry()`), not inside `resolve_template()`.**
`resolve_template()` is behaviourally **untouched** in Phase 53 beyond the Q2 widening — its Priority-1
warn-and-fallback (template_engine.py:308-315) still fires exactly as today, because its only caller in
Phase 53 remains `_write_template_file()` (builder.py:1109-1179, explicitly **not deleted** this phase
per CONTEXT.md's canonical_refs), which is called exactly once per build and only ever resolves the
single global `typst_template` value — i.e. only ever the synthesized `"typst"` key's own template,
never a user-defined key's.

A user-defined key's `template` value has **no runtime consumer at all in Phase 53** — Phase 54 is what
first reads a user-defined key's template bytes (for the bundle copy) or constructs a `TemplateEngine`
from it via `render_wrapper()` for an entry actually naming that key. D-08's raise is therefore a
**pre-emptive validation-time check with no Phase-53 behavioural side effect of its own** beyond the
fail-loud gate: `resolve_template_registry()` runs `os.path.isfile(os.path.join(srcdir, entry.template))`
for every user-defined key with a `template` set (per D-05, regardless of whether any `typst_documents`
entry currently references that key) and raises if the file is absent, while explicitly **skipping**
this same check for the `key == "typst"` entry so that entry's Priority-1-not-found path continues to
reach `resolve_template()`'s existing warn-and-fallback unobstructed, exactly as it does today.

**Measured consequence of the alternative placement (inside `resolve_template()`):** would require
`resolve_template()` to know which key it is resolving on behalf of, threading a new
`is_reserved_key: bool` (or similar) parameter through the class's single priority walk — a parameter
this class's constructor has no other reason to carry, and one that couples `TemplateEngine` (pure
content/parameter logic, per the module boundary `ARCHITECTURE.md` §5 documents) to registry-validation
concerns that belong in `builder.py`/`template_registry.py`. The registry-validator placement keeps
`TemplateEngine` unaware that registries exist at all — it is constructed from a plain
`TemplateRegistryEntry`'s fields exactly as it is constructed from raw `config` values today.

## Q4 — CONF-18's seven denylist cases as platform-independent predicates

All seven are pure string-shape functions, testable on Linux CI, per the project's own D-05
platform-independence precedent (`_is_drive_qualified()`'s docstring, builder.py:36-67).

| # | Case (D-02) | Python predicate |
|---|---|---|
| 1 | Empty or whitespace-only | `key.strip() == ""` |
| 2 | `.` or `..` | `key in (".", "..")` |
| 3 | Contains `/` or `\` | `"/" in key or "\\" in key` |
| 4 | Windows reserved device name, case-folded, with or without trailing extension | see below |
| 5 | Trailing dot | `key.endswith(".")` |
| 6 | Trailing space | `key.endswith(" ")` |
| 7 | Differs from another registered key only by case | see below (reuses `_collision_key()`) |

**Case 4 — canonical reserved-name set** `[CITED: learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file]`:
`CON, PRN, AUX, NUL, COM1–COM9, LPT1–LPT9` — 22 names. Microsoft's own documentation confirms these are
reserved case-insensitively and **regardless of extension** (`CON.txt` is still reserved). `COM0` and
`LPT0` are explicitly **not** on this list (a common but incorrect over-inclusion seen in some secondary
sources, e.g. `PITFALLS.md`'s mention of `CLOCK$`, which is a legacy DOS device name absent from
Microsoft's current documented list — do not include it without a second citation).

```python
_WINDOWS_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


def _is_windows_reserved_name(key: str) -> bool:
    # Extension-stripping per Microsoft's documented behaviour: the
    # reserved match is against everything BEFORE the first ".", not the
    # whole string -- "CON.txt" is reserved, "ICONIC" is not (no dot, no
    # match against the FULL string either).
    stem = key.split(".", 1)[0]
    return stem.upper() in _WINDOWS_RESERVED_NAMES
```

**Case 7 — case-collision, reused through `_collision_key()`** (SC#4's own requirement — "runs through
the same casefold comparison `_collision_key()` already uses"). Verified by reading builder.py:422-500:
`_collision_key()`'s body is exactly `relative_path.replace("\\", "/")` → `posixpath.normpath(...)` →
`.casefold()` (builder.py:498-500, quoted verbatim: `folded_separators = relative_path.replace("\\",
"/")`, `normalized_shape = posixpath.normpath(folded_separators)`, `return
normalized_shape.casefold()`). Because case 3 already rejects any key containing `/` or `\`, a
denylist-surviving key is always a single segment with no separator, so `posixpath.normpath()` is a
no-op on it (no `.`/`..`/redundant-slash shape survives to this point either, per cases 1/2/5) — the
function degenerates to a pure `.casefold()` call for every value CONF-18's other six cases have
already let through, but reusing the actual function (not re-deriving `.casefold()` inline) is what
satisfies SC#4's "not a second independently-written check" requirement:

```python
def _has_case_collision(key: str, other_keys: set[str]) -> bool:
    folded = TypstBuilder._collision_key(key)
    return any(
        other != key and TypstBuilder._collision_key(other) == folded
        for other in other_keys
    )
```

**Confirmed by reading D-02 against the case list above:** exactly seven cases, no more. Windows-illegal
characters (`< > : " | ? *`), control characters (0x00–0x1F), a leading dot, and interior whitespace are
explicitly *not* checked in Phase 53 (deferred, per Deferred Ideas above) — a predicate implementation
must not add an eighth case "for safety."

## Q5 — CONF-17 as path arithmetic (D-07/D-09)

**Predicate:** reject when the resolved template's parent directory is `srcdir` itself, or is an
ancestor of `srcdir`. In one expression, given `template_abs_path = os.path.join(srcdir, entry.template)`
(the same resolution `render_wrapper()`/`_write_template_file()` already perform,
writer.py:330-333/builder.py:1128-1130):

```python
def _violates_conf17(template_abs_path: str, srcdir: str) -> bool:
    parent = os.path.normpath(os.path.dirname(os.path.abspath(template_abs_path)))
    norm_srcdir = os.path.normpath(os.path.abspath(srcdir))
    # commonpath(...) == parent  <=>  parent is norm_srcdir itself, OR an
    # ancestor of it -- a single `os.path.commonpath` call covers both of
    # D-07's rejected shapes (`parent == srcdir` and `parent` is a proper
    # ancestor) without needing two separate comparisons.
    return os.path.commonpath([norm_srcdir, parent]) == parent
```

**Measured, matching D-07's own citation:** `os.path.join(srcdir, "/abs/x.typ")` returns `/abs/x.typ`
verbatim — this is documented stdlib behaviour of `os.path.join` (a later absolute component discards
every earlier component) and is what lets an absolute `typst_template` value bypass `srcdir` entirely,
so `_violates_conf17` naturally evaluates `parent = "/abs"` against `srcdir`, and unless `/abs` happens
to be `srcdir` or an ancestor of it, the check passes — matching D-07's "absolute paths outside srcdir
stay legal" clause with no special-casing needed.

**Independent of D-08 (D-09):** `_violates_conf17` takes no filesystem-existence branch — it is pure
path arithmetic on the *declared* string, so a `template` value that is both CONF-17-violating AND
points at a nonexistent file (the rare case where the parent-dominates-srcdir shape happens to name a
file that also doesn't exist) reports **both** failures in one accumulated `ExtensionError`, per D-03's
"accumulate every failure" shape — the two checks are structurally independent function calls inside the
same validation pass, not an if/elif chain that would short-circuit one in favour of the other.

## Q6 — SC#2's byte-identity evidence procedure (D-12)

This is a **one-off measurement**, `53-RED-EVIDENCE.md`, not a pytest gate. Below is the concrete,
reproducible procedure, naming real fixtures already on disk wherever one exists.

### Environment note (measured this session, differs from the milestone-level research)

`typst.compile()` **succeeds** in this sandbox as of 2026-08-15 — measured directly:
```
$ uv run python -c "import typst; typst.compile(...)"
COMPILE OK
```
This **contradicts** `51-RESEARCH.md`'s 2026-08-14 finding that `typst.compile()` raised
`FileNotFoundError` under NixOS's dynamic linker in this same sandbox. The user's own memory record
(`nixos-sandbox-test-env.md`) independently notes the uv-shim class of failure "失効" (expired/resolved)
as of 2026-08-14 — this session's direct measurement confirms the PDF-compile path is now live, not
just the markup-only `-b typst` path. **Do not assume this is permanent** — re-verify with a live
`typst.compile()` call at evidence-gathering time rather than trusting this note, since the underlying
cause of the prior failure (a NixOS dynamic-linker/binary-execution mismatch) is exactly the kind of
environment detail that can regress between sessions.

### The four shapes, mapped to real fixtures/roots on disk

| Shape | Existing fixture (real, on disk) | Notes |
|---|---|---|
| `typst_template` set | `docs/source/conf.py:96` (`typst_template = "_typst/custom_template.typ"`) — the project's own dogfood build | Real, buildable via `sphinx-build -b typstpdf docs/source <build>` (requires `--extra docs` synced per `51-RESEARCH.md`'s measured note). Also: `tests/fixtures/documented_params_contract_gate/conf.py:36` (`typst_template = "_templates/documented.typ"`), a smaller, faster fixture for a scratch-build alternative. |
| `typst_package` set (alone, no `typst_template`) | `examples/charged-ieee/approach1/conf.py:22` (`typst_package = "@preview/charged-ieee:0.1.4"`, no `typst_template`) — real dogfood example, package-only route | Also `tests/fixtures/typst_lang_gate/package_no_lang/conf.py:55` for a smaller fixture (pairs `typst_package` with `typst_template_function`, which is fine — this shape only requires `typst_template` to be UNSET). |
| `typst_template_function` set (alone — bundled default template + custom function, no `typst_template`, no `typst_package`) | `tests/fixtures/params_exclusivity_gate/zero_params_default/conf.py` — confirmed via `grep -rL "typst_template\s*=\|typst_package\s*="  $(grep -rl "typst_template_function\s*=" tests/fixtures/*/conf.py tests/fixtures/*/*/conf.py)`, the ONE fixture in the whole suite matching this exact isolated shape | This is the narrowest match; every other `typst_template_function`-setting fixture also sets `typst_template` or `typst_package` alongside it. |
| Nothing set (bundled `base.typ`, no template/package/function at all) | `tests/roots/test-basic/conf.py` — confirmed by direct read: only `typst_documents` is set, no other `typst_*` value | Smallest, fastest candidate. `tests/fixtures/default_typst_documents_gate/conf.py` and `tests/fixtures/missing_and_malformed_master_gate/conf.py` are documented (in their own header comments) as deliberately setting none of `typst_template`/`typst_package`/`typst_template_function` either — three independent confirmations of this shape. |

### Procedure

1. **Record the pre-change baseline commit SHA** (`git rev-parse HEAD` before any Phase 53 code lands
   — the current tip at research time is `c7e02d27`, but re-measure at plan-execution time since more
   planning-only commits may land first).
2. For each of the four shapes, run, under the worktree's own `uv run` (per `CLAUDE.md`'s standing
   isolation rule):
   ```bash
   uv run python -m sphinx -b typstpdf <source_dir> <scratch_build_dir_pre>
   ```
   using the fixture named in the table above as `<source_dir>` (for `docs/source`, this also needs
   `--extra docs` synced first, per `51-RESEARCH.md`'s measured note about `myst_parser`).
3. Compute `sha256sum` for every emitted `.typ` file under `<scratch_build_dir_pre>` and record the
   file list + hashes verbatim in `53-RED-EVIDENCE.md`.
4. `pypdf.PdfReader(str(pdf_path))` then `len(reader.pages)` for the compiled PDF — this exact call
   shape is already a live precedent in this test suite (`tests/test_admonition_locale_title_precedence_gate.py:301`,
   `reader = pypdf.PdfReader(str(pdf_output))`); record the page count.
5. Record the post-change commit SHA once Phase 53's code lands, re-run steps 2-4 into
   `<scratch_build_dir_post>`, and diff: every `.typ` file's SHA-256 must match its pre-change
   counterpart exactly (byte-identity, not "looks the same"), and every PDF's page count must match.
6. **The fifth shape** — a four-element `typst_documents` tuple vs. the same tuple with a fifth element
   `"typst"` — needs no separate fixture: re-run step 2 twice against the SAME source tree, once with
   the fixture's `typst_documents` entries as authored (four elements, if that's how they're authored)
   and once with an explicit `"typst"` appended to each entry, and diff the two `<scratch_build_dir>`
   trees against EACH OTHER (not against a stored baseline) — this is TPL-04's own equivalence claim,
   independent of the four-shapes baseline above. None of the fixtures in the table above currently
   author a bare four-element tuple by inspection alone; confirm the exact tuple shape each fixture uses
   at evidence-gathering time (they use varying element counts — e.g.
   `zero_params_default/conf.py:30` uses `("index", "master", project, author)`, already four elements,
   making it directly usable for this comparison without modification).

## Q7 — Re-confirmed count of the "31 test files"

**Measured this session:**
```
$ grep -rl "_template\.typ" tests/ | wc -l
32
```
The full file list (`grep -rl "_template\.typ" tests/`) matches `ARCHITECTURE.md` §4's own enumerated
list **exactly**, item for item — 6 `tests/fixtures/*/conf.py` files plus 26 `tests/test_*.py` files.
`ARCHITECTURE.md`'s own enumerated list, counted by hand, is also 32 (6 + 26), even though its
surrounding prose says "31 (not ~20 — a direct grep count)". **This is a pre-existing off-by-one in the
milestone-level research's prose, not a new finding about the code** — the enumerated list itself was
already correct; only the summary number in the sentence above it undercounts by one. Flagging loudly
per the research brief's instruction: **the correct count is 32, and the planner/executor should use
32 (or better, re-run the grep at execution time) rather than propagating "31" as a target number in
any acceptance criterion.** No test in this list needs to CHANGE in Phase 53 — every one of the 32
still asserts `_template.typ` at the outdir root, and Phase 53's own goal statement ("this phase
changes no output") is exactly why: `_write_template_file()` is explicitly not deleted this phase (see
Q3), so every one of these assertions continues to hold unmodified. This is the expected, confirming
result, not a contradiction — flagged here only because research_focus asked for the count to be
independently verified, and the milestone research's headline number was one off from its own list.

## Q8 — SC#5's CI mechanics

### Measured branch state

```
$ git branch -a
  gsd/v0.9.0-milestone
* gsd/v0.9.0-per-document-templates
  ...
$ git rev-parse gsd/v0.9.0-milestone gsd/v0.9.0-per-document-templates
aed773c9807ab871468b1b2a7e1ec36b54e82907
c7e02d2733fb77118058dffaffd698a076fa2e1f
$ git merge-base gsd/v0.9.0-milestone gsd/v0.9.0-per-document-templates
aed773c9807ab871468b1b2a7e1ec36b54e82907
```

**Finding, flagged loudly:** `gsd/v0.9.0-milestone` — the branch name ROADMAP.md/STATE.md/PROJECT.md
all cite for SC#5 — is **stale**. It sits exactly at the merge-base with the CURRENTLY CHECKED-OUT
branch, `gsd/v0.9.0-per-document-templates`, meaning `gsd/v0.9.0-milestone` has received **zero**
commits since the two diverged, while `gsd/v0.9.0-per-document-templates` (the branch this research
session and all of Phase 53's planning-stage commits are actually landing on) is 5 commits ahead
(`50ee2950` requirements → `3d2f94d0` roadmap → `7fd4587c` todo-tagging → `76ec6077` Phase 53 CONTEXT →
`c7e02d27` state update). **All real Phase 53 work is happening on `gsd/v0.9.0-per-document-templates`,
not on `gsd/v0.9.0-milestone`.** The planner must resolve this before SC#5 can be satisfied: either (a)
push `gsd/v0.9.0-per-document-templates` to `origin` and treat IT as the milestone branch going
forward (renaming `git branch -m` locally to `gsd/v0.9.0-milestone`, or updating STATE.md/ROADMAP.md to
name the branch that actually carries the work), or (b) merge/rebase the current branch's 5 commits
onto `gsd/v0.9.0-milestone` and push that. Option (a) is lower-risk (no history rewriting); this
research recommends it but the choice is the planner's/owner's, not this document's, to make — flagging
the discrepancy is this document's job.

Neither branch is on `origin`:
```
$ git ls-remote --heads origin | grep -i v0.9
(no output)
```

### CI trigger mechanics

`.github/workflows/ci.yml:3-8`:
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
```
**A plain `git push origin gsd/v0.9.0-per-document-templates` does NOT trigger CI** — the push trigger
is scoped to `main`/`develop` only, and this branch is neither. Two ways to get a completed 3-OS run
over the pushed branch, both already precedented in this repository's own history:

1. **`workflow_dispatch`, no PR needed** — exactly how v0.8.0 satisfied its own SC#5. Measured via
   `gh run list --branch gsd/v0.8.0-multi-master-composition`: run `31858016832` (event
   `workflow_dispatch`, workflow `CI`, `completed`/`success`, `6m18s`) ran directly against the
   milestone branch with no PR open at the time. Command: `gh workflow run CI --ref
   gsd/v0.9.0-per-document-templates` (or whatever branch name Q8's finding above resolves to), then
   poll with `gh run list --branch <branch> --limit 5` / `gh run view <run-id>` until `completed`/
   `success`, checking specifically for the `windows-latest` and `macos-latest` matrix legs inside that
   run (the `test` job's matrix, ci.yml:16-18).
2. **Open a (draft) PR against `main`** — the `pull_request` trigger then runs CI against the branch's
   HEAD. Also measured in the same v0.8.0 history: run `31860724860` (`pull_request` event, same
   branch, `success`, `6m11s`). This additionally exercises `Documentation`/`Link Check` workflows,
   which `workflow_dispatch` alone does not.

**Recommended evidence-capture command sequence** (mirrors the v0.8.0 precedent exactly):
```bash
git push origin <resolved-branch-name>
gh workflow run CI --ref <resolved-branch-name>
# poll (not sleep-loop) until the run's status is completed:
gh run list --branch <resolved-branch-name> --limit 5
gh run view <run-id> --json jobs -q '.jobs[] | {name, conclusion}'
```
The last command's output must show `conclusion: success` for both the `windows-latest` and
`macos-latest` legs of the `test` job (there are 2 Python versions × 3 OSes = 6 `test` job instances;
CONF-18's reserved-device-name and case-collision predicates are string-shape tests that pass
identically on every OS per Q4, so this run is confirming CI plumbing/packaging correctness on those
platforms, not exercising a platform-specific code path that could only fail there — consistent with
D-01's "denylist enumeration, no filesystem probe" design).

## Package Legitimacy Audit

Not applicable. `STACK.md`'s own verdict for this milestone: **"Add nothing"** — zero new runtime
dependencies, zero new stdlib imports not already used elsewhere in this codebase. Phase 53 installs no
external package.

## Common Pitfalls

Fully covered by `.planning/research/PITFALLS.md`'s five pitfalls (registry-key validation reusing the
wrong guard, `copytree` symlink defaults, `Path(__file__).parent` vs `importlib.resources`, the
`_template.typ` relocation changing relative-path resolution, and the silent `typst_template_assets`
removal) — do not re-derive. **Pitfalls 2-4 belong to Phase 54** (directory copy, bundle relocation);
only **Pitfall 1** (registry-key validation) is live in Phase 53's own scope, and D-01/D-02 already
resolve it by locking the denylist-enumeration approach Pitfall 1 recommends.

**One Phase-53-specific pitfall not named elsewhere:** a plan that has `resolve_template_registry()`
call `resolve_template()` (to reuse the Priority-1 warn/raise logic) for a USER-DEFINED key's
existence check would accidentally exercise Priority 2/3 fallback for that key too, silently returning
the BUNDLED default template's content as if it were a successful resolution rather than raising — the
existence check must be a bare `os.path.isfile()` against the declared path alone (D-08's own wording:
"a file that does not exist" is a existence question, not a resolution question), never a call into
`resolve_template()`'s multi-priority walk, which is specified (CONF-07/D-06) to always succeed by
falling back to the bundled default and therefore can never itself signal "not found" for a
user-defined key the way D-08 needs.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), `tox` as task runner — unchanged from the rest of this project |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest tests/test_template_registry.py tests/test_template_engine.py -v` (new module name is the planner's/executor's choice, per CONTEXT.md's discretion note) |
| Full suite command | `uv run pytest tests/ -v` locally as a spot-check; dispatched `gh workflow run CI --ref <branch>` is the matrix/lint/type authority (per the v0.7.1/v0.8.0 precedent already established in this project) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TPL-01 | Named definitions accepted, `template` xor `package`, optional `template_function` in both forms | unit | new `tests/test_template_registry.py::test_*` | ❌ Wave 0 |
| TPL-03 | `"typst"` key resolves to global config, byte-identical output | e2e/gate | `53-RED-EVIDENCE.md` procedure (Q6) — a one-off measurement, not a pytest command; **also** covered structurally by the existing 32-file regression net (Q7) staying green unmodified | ✅ existing net; ❌ RED-EVIDENCE artifact (Wave 0/1) |
| TPL-04 | Four-element tuple == fifth-element `"typst"` tuple | unit/e2e | new unit test + Q6 step 6's comparison | ❌ Wave 0 |
| TPL-05 | Several entries share one key | unit | new `tests/test_template_registry.py::test_shared_key_resolves_once` | ❌ Wave 0 |
| CONF-14 | Unregistered key raises, names registered keys | unit | new test asserting `ExtensionError` message contains `sorted(registry.keys())` | ❌ Wave 0 |
| CONF-15 | `template` + `package` both set raises | unit | new test | ❌ Wave 0 |
| CONF-16 | User-defined `"typst"` raises | unit | new test | ❌ Wave 0 |
| CONF-17 | Path arithmetic (Q5) raises/passes per case | unit | new test covering: `parent == srcdir`, `parent` ancestor of `srcdir`, sibling (legal), absolute-outside (legal) | ❌ Wave 0 |
| CONF-18 | Seven denylist cases (Q4) | unit | new test, one case per parametrized example, platform-independent (runs identically on Linux CI) | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** the new registry-module test file alone (seconds).
- **Per wave merge:** `uv run pytest tests/ -v` locally, confirming the 32 files from Q7 stay green
  unmodified (spot-check only — not authoritative for lint/matrix, that's CI).
- **Phase gate:** dispatched CI run (`gh workflow run CI --ref <branch>`) all-green across all 6
  matrix legs, INCLUDING `windows-latest`/`macos-latest` (SC#5's own requirement, Q8), before
  `/gsd-verify-work`. `53-RED-EVIDENCE.md` (Q6) must also be complete and committed before the phase
  gate closes — it is evidence, not a gate, but SC#2 has no other acceptance mechanism per D-12.

### Wave 0 Gaps

- [ ] `tests/test_template_registry.py` (or planner-chosen name) — covers TPL-01, TPL-04, TPL-05,
  CONF-14..18. No existing test file exercises `resolve_template_registry()` since it does not yet
  exist.
- [ ] `53-RED-EVIDENCE.md` — the one-off SC#2 evidence artifact (Q6). Not a pytest file; a markdown
  artifact recording commit SHAs, SHA-256 hashes, and page counts.
- [ ] Existing `tests/test_template_engine.py::TestTemplateResolutionProvenance` — no NEW file needed,
  but the widened `TemplateResolution` (Q2) should get one or two additive assertions confirming the
  new `.path` field is populated correctly at each of the three priorities, alongside the existing
  `.source` assertions (same test class, additive only — do not restructure the existing 3 tests that
  already pass).
- Framework install: none — pytest/tox already fully provisioned per this project's standing `uv sync
  --extra dev` convention.

## Security Domain

`security_enforcement` is on project-wide. This phase's only new "input" is `conf.py`-authored config
(author-controlled, not untrusted network/user input) — consistent with `STACK.md`'s own framing
("the key space is small, author-controlled `conf.py` config, not untrusted user input").

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — no auth surface |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Yes | Registry-key shape validated by the D-01/D-02 denylist (Q4) BEFORE any `path.join()`/`mkdir()` call touches the key — no directory is created in Phase 53 itself (that's Phase 54), but the validation must still run before any value derived from the key reaches a filesystem call, per `PITFALLS.md`'s own "validate BEFORE use" security note |
| V6 Cryptography | No | N/A — SHA-256 hashing in `53-RED-EVIDENCE.md` (Q6) is an integrity check for evidence, not a security control |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A `conf.py`-authored registry key crafted to look like a Windows device path, exploited by a LATER phase's `mkdir()`/`copytree()` call | Tampering (deferred harm — Phase 54 is the actual write site) | CONF-18's denylist (Q4) rejects the shape at validation time, in Phase 53, before Phase 54's write site ever exists to be exploited — validate-then-use is already the design, not a retrofit |
| A registry entry's `template` path crafted to point at `srcdir` itself or an ancestor, intending a future bundle-copy to leak the entire source tree | Information Disclosure (deferred harm — the actual copy is Phase 54) | CONF-17 (Q5) rejects this shape at validation time in Phase 53, closing the door before Phase 54's `copytree()` exists |
| A test or plan silently loosening the CONF-18 denylist back toward an allowlist (D-01 explicitly rejects allowlists) to make a broader class of keys pass | Tampering (weakened gate) | Review discipline — the seven cases in Q4 are exhaustive per D-02; a plan or diff introducing an eighth rejected case, or converting the denylist to an allowlist, contradicts a locked decision and should be flagged in code review |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `typst.compile()` succeeding in this sandbox today (2026-08-15) is a genuine, repeatable environment state, not a one-off fluke | Q6 environment note | If it regresses before `53-RED-EVIDENCE.md` is actually gathered, the PDF-page-count half of SC#2's evidence must fall back to the `-b typst`-only, hash-only procedure `51-RESEARCH.md` used, and the plan should name that fallback explicitly rather than assume PDF compilation will work |
| A2 | `COM0`/`LPT0` are correctly excluded from the Windows reserved-name set (Q4), against `PITFALLS.md`'s broader (uncited) list that includes `CLOCK$` | Q4 | If Microsoft's Win32 API actually still special-cases `COM0`/`LPT0`/`CLOCK$` in some code path this research's single citation didn't surface, a key using one of those names could still fail `mkdir()` on real Windows CI despite passing this phase's string-shape gate — low risk (Phase 53 creates no directories; Phase 54 would surface this on its own 3-OS CI run before shipping) |
| A3 | The recommended resolution to the Q8 branch-name discrepancy (push `gsd/v0.9.0-per-document-templates`, treat it as the milestone branch) is what the owner will choose, rather than merging onto `gsd/v0.9.0-milestone` | Q8 | If the owner instead wants history preserved under the `gsd/v0.9.0-milestone` name, the push/rename step in the plan needs a different git sequence (merge or rebase) — either is mechanically simple, but the plan must not hardcode one branch name as if it were already decided |

## Open Questions

1. **Which branch name does SC#5 actually target?**
   - What we know: `gsd/v0.9.0-milestone` is named in ROADMAP.md/STATE.md/PROJECT.md but carries zero
     Phase 53 commits; `gsd/v0.9.0-per-document-templates` is the actively-worked branch.
   - What's unclear: whether the owner wants the stale branch name reconciled by push+rename, by
     merge, or by simply updating the planning docs to name the branch that is actually in use.
   - Recommendation: surface this explicitly at plan time (or via `checkpoint:decision`) rather than
     having the plan silently assume one resolution — see A3 above.

## Sources

### Primary (HIGH confidence — read directly this session)

- `typsphinx/builder.py` (lines 1-170, 420-620, 620-760, 990-1180) — `_is_drive_qualified()`,
  `_escapes_outdir()`, `_collision_key()`, `_validate_output_path_collisions()`, `write()`,
  `prepare_writing()`, `_write_typst_files()`, `_write_template_file()`.
- `typsphinx/writer.py` (full read) — `render_wrapper()`, `compute_template_import_path_for_dir()`,
  `_entry_element_value()`, `translate()`.
- `typsphinx/template_engine.py` (lines 1-350, 600-715) — `TemplateResolution`, `resolve_template()`,
  `TemplateEngine.__init__`, `render()`.
- `typsphinx/__init__.py` (full read) — config registration block.
- `.planning/phases/53-template-registry-foundation/53-CONTEXT.md` (full read) — D-01..D-12.
- `.planning/REQUIREMENTS.md` lines 1-179 — TPL/CONF requirement text and traceability table.
- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/PROJECT.md` — milestone framing and locked
  decisions.
- `.planning/research/{ARCHITECTURE,PITFALLS,STACK,SUMMARY}.md` (all read in full) — milestone-level
  research, cited and not re-derived per this document's mandate.
- Live commands executed this session: `grep -rl "_template\.typ" tests/ | wc -l` (32),
  `grep -n "TemplateResolution(" typsphinx/*.py tests/*.py` (3 hits, all inside `resolve_template()`),
  `git branch -a` / `git rev-parse` / `git merge-base` (branch discrepancy), `git ls-remote --heads
  origin` (neither v0.9.0 branch present), `gh run list --branch gsd/v0.8.0-multi-master-composition`
  (workflow_dispatch + pull_request precedent), `uv run python -c "import typst; typst.compile(...)"`
  (COMPILE OK, live measurement).
- `.github/workflows/ci.yml` (full read) — trigger scoping (`push`/`pull_request` limited to
  `main`/`develop`; `workflow_dispatch` always available).
- Fixture files read/grepped: `tests/roots/test-basic/conf.py`,
  `tests/fixtures/params_exclusivity_gate/{partial_params_template,zero_params_default}/conf.py`,
  `tests/fixtures/package_only_config_gate/conf.py`, `tests/fixtures/documented_params_contract_gate/conf.py`,
  `docs/source/conf.py`, `examples/charged-ieee/{approach1,approach2}/conf.py`,
  `tests/test_admonition_locale_title_precedence_gate.py` (pypdf page-count precedent).

### Secondary (MEDIUM confidence)

- [Naming Files, Paths, and Namespaces - Win32 apps | Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
  — Windows reserved device names, cross-checked against the web search's own synthesis of the same
  page (CON, PRN, AUX, NUL, COM1-9, LPT1-9; extension does not exempt a name; COM0/LPT0 excluded).

### Tertiary (LOW confidence)

- None — every claim in this document is either read directly from the working tree this session, a
  live command's measured output, or the single Microsoft Learn citation above.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies (STACK.md's verdict, unchanged); every stdlib usage
  already precedented in this codebase.
- Architecture: HIGH — every integration point is file:line grounded, either from this session's own
  reads or from `ARCHITECTURE.md`'s prior HIGH-confidence pass (not re-derived, cited).
- Pitfalls: HIGH for Phase-53-scoped Pitfall 1 (fully resolved by D-01/D-02); Phase-54-scoped Pitfalls
  2-4 correctly out of this phase's scope.
- CONF-18 Windows reserved-name set: MEDIUM-HIGH — single authoritative citation, cross-checked against
  the web search's independent synthesis of the same source, but not cross-checked against a second
  independent source.
- Branch/CI mechanics (Q8): HIGH — every claim is either a live `git`/`gh` command's measured output or
  a direct read of `ci.yml`.

**Research date:** 2026-08-15
**Valid until:** Re-verify the `typst.compile()` environment note (A1) and the branch-name discrepancy
(Q8/A3) at plan-execution time — both are the kind of environment/process facts that can change
between sessions. The code-level findings (Q1-Q5, Q7) are stable until Phase 53's own code lands.
