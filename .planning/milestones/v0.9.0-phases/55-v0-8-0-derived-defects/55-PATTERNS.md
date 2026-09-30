# Phase 55: v0.8.0-Derived Defects - Pattern Map

**Mapped:** 2026-08-16
**Files analyzed:** 5 (all pre-existing files being MODIFIED — this phase creates no new source files)
**Analogs found:** 5 / 5 (all "analogs" are sibling code IN THE SAME FILE being modified — this is a
narrow-bugfix phase, not a new-feature phase, so the closest pattern for each fix is the immediately
adjacent, already-correct sibling function/branch in the same module)

**Note on scope:** Phase 55 modifies exactly two source files (`typsphinx/translator.py`,
`typsphinx/builder.py`) and adds test cases to three existing test files, plus possibly one new
fixture directory. There are no "roles" in the controller/component/service sense — everything here
is `translator`-role (docutree→Typst emission) or `builder`-role (Sphinx build orchestration) code,
classified by *defect shape* below instead.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` (`_sanitize_label`, XREF-05) | translator / string-transform | transform (docname → Typst label token) | same file: `_sanitize_label`'s own docstring contract (injectivity requirement already stated, not yet enforced against its own token shape) | exact (self-referential — the fix hardens the function's own documented invariant) |
| `typsphinx/translator.py` (`make_include_edge_key`, BLD-07) | translator / string-transform | transform (docname pair → edge-key string) | same file: `escape_typst_string()` (`translator.py:141-172`) — the sibling escaping primitive whose *pattern* (regex/replace-based character escaping) is mirrored, but scope is deliberately NOT widened into it | role-match (same escaping pattern class, different, narrower scope) |
| `typsphinx/translator.py` (`derive_master_edge_keys`/`walk`, BLD-08) | translator / graph-traversal | transform (recursive DFS) with a new bounded-failure branch | same file: any existing `ExtensionError` raise site is absent in `translator.py`; nearest analog is `typsphinx/builder.py`'s raise-site convention (`builder.py:1877-1887`) | role-match (import needed; message-shape convention borrowed cross-file) |
| `typsphinx/builder.py` (`_track_image`, BLD-09) | builder / path-classification | transform (URI string → boolean gate) | same file: `_escapes_outdir()` / `_is_drive_qualified()` (`builder.py:120-161`, esp. `:153-161`) — the exact sibling predicate already solving the identical platform-independence problem | exact (fix is a literal predicate swap to match this sibling) |
| `typsphinx/builder.py` (`_track_image`, IMG-03) | builder / key-derivation | transform (URI string → relocation key) | same file, same method: the collision branch two lines below (`builder.py:1602`, `key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"`) — already injective, the shape the escape branch must match in spirit (though not literally, since basename-loss is the point of escaping) | role-match (sibling branch, same function, injectivity property to restore) |
| `tests/test_xref_compile_time_guard_render_gate.py` (XREF-05 RED/invert) | test / integration (real compile) | request-response (build → PDF → link-destination assertion) | same file: `test_label_collision_guard_links_to_decoy` (the exact test being inverted — no new test file) | exact |
| `tests/test_include_edge_derivation_unit.py` (BLD-07 unit half + BLD-08) | test / unit | transform (pure function → assertion) | same file: `TestDeriveMasterEdgeKeysTraversal` class (`:64-149`) — the exact harness shape (construct `toctree_includes` dict, call `derive_master_edge_keys()` directly, no Sphinx build) | exact |
| new fixture dir for BLD-07 real-compile RED | fixture / Sphinx test project | file-I/O (rst sources → build) | `tests/fixtures/state_guard_substring_key_gate/` (`conf.py`, `index.rst`, plus doc files) — nearest precedent shape named explicitly in CONTEXT.md/RESEARCH.md | role-match (precedent fixture shape, new docname content) |
| `tests/test_builder.py` (BLD-09 + IMG-03 unit REDs) | test / unit | transform + file-I/O | same file: Phase 50 relocation cluster, esp. `test_post_process_images_rehomes_absolute_uri` (`:390-424`) and the four named siblings in CONTEXT.md D-05 (`:511`, `:578`, etc.) | exact |

## Pattern Assignments

### `typsphinx/translator.py` — XREF-05 fix in `_sanitize_label`

**Analog:** the function's own docstring (`translator.py:5023-5057`, read this session) — it already
states the injectivity property as a design *requirement* ("is deterministic and injective on the
offending character... collision-resistant") but the current implementation does not enforce it
against its OWN encoding-token shape. The fix is "make the code live up to its own documented
contract," not an import from elsewhere.

**Current implementation** (`translator.py:5065-5069`, verified this session):
```python
return re.sub(
    r"[^A-Za-z0-9_.:-]",
    lambda m: f"_u{ord(m.group(0)):x}_",
    name,
)
```

**Collision mechanism:** `_`, digits, and hex letters are ALL in the allowed set, so a literal
input substring that already spells `_u2f_` (the encoder's own output shape for `/`, since
`ord('/') == 0x2f`) passes through this regex completely unchanged. Docname `a/b` and docname
`a_u2f_b` both produce the literal label string `a_u2f_b:nested-target` for a same-named id
`nested-target`.

**Candidate construction** (RESEARCH.md Pattern 1, `[ASSUMED]` — not verified against a real
`typst.compile()`, needs its own RED-first fixture before trusting): pre-pass that doubles the
leading underscore of any literal `_u[0-9a-f]+_` substring in the raw input BEFORE the main
substitution runs (`_u2f_` → `__u2f_`), since the doubled-underscore-prefixed shape is never
emitted by the encoder itself and every character involved (`_`) is already in the allowed
character class, so the pre-pass introduces no new invalid characters.

```python
# Proposed pre-pass, ordering matters (before the existing re.sub):
name = re.sub(r"_u([0-9a-f]+)_", r"__u\1_", name)
return re.sub(
    r"[^A-Za-z0-9_.:-]",
    lambda m: f"_u{ord(m.group(0)):x}_",
    name,
)
```

**Caller** (`_namespace_label`, single call site for docname-namespaced labels — verify exact lines
at execution time; RESEARCH.md cites `:5080-5116`) prefixes `docname:` before calling
`_sanitize_label`, so the collision manifests as `a_u2f_b:nested-target` from two distinct
docnames.

**RED-evidence pattern to copy:** `tests/test_xref_compile_time_guard_render_gate.py`'s existing
`test_label_collision_guard_links_to_decoy` (`:328-360`) — a real `sphinx-build -b typstpdf` +
`typst.compile()` + PDF link-destination extraction, asserting the CURRENT (buggy) behavior first,
then inverted per D-04. Fixture: `tests/fixtures/xref_label_collision_guard_gate/` (existing —
`conf.py`, `index.rst`, `a/b.rst` marked `:orphan:`, `a_u2f_b.rst` the decoy). The fixture's own
`conf.py` load-bearing-properties comment block (a)–(d) must be updated in the same change (it
currently documents the collision as an "accepted limit").

**Property-test pattern to add (Pitfall 3 mitigation):** beyond the one fixture, add synthetic unit
probes for `_sanitize_label` directly — an id containing `_u` followed by non-hex text (should be
untouched), an id containing the full token pattern twice, an id ending in a partial `_u2` with no
closing `_`. No existing analog for this specific property-test shape; write it as a small,
self-contained unit test class near other `_sanitize_label`-adjacent tests (search
`tests/test_translator.py` for existing `_sanitize_label`/label-alphabet unit coverage before
adding a new file).

---

### `typsphinx/translator.py` — BLD-07 fix in `make_include_edge_key`

**Analog:** `escape_typst_string()` (`translator.py:141-172`, verified this session) — the sibling
escaping primitive whose *pattern* (a small, explicit character-substitution function with a
documented, fixed contract) is mirrored for the new `#`/`>` escaping, but is explicitly NOT widened
to include it (Claude's Discretion + Deferred Ideas both reject widening it — it is called from
many sites that do not want `#` escaped).

**Current implementation** (`translator.py:229-231`, verified this session):
```python
escaped_parent = escape_typst_string(parent_docname)
escaped_child = escape_typst_string(child_docname)
return f"{escaped_parent}#{occurrence}>{escaped_child}"
```

`escape_typst_string` escapes `\`, `"`, `\n`, `\r`, `\t` — NOT `#` or `>`. A docname containing
either character passes through unescaped, colliding with the format's own inserted separators.

**Candidate construction** (RESEARCH.md Pattern 2, `[ASSUMED]` but with a stated injectivity
argument — needs RED-first real-compile fixture per D-05 before trusting):
```python
def _escape_include_edge_separators(text: str) -> str:
    """Escape literal '#' and '>' so they can never be mistaken for
    make_include_edge_key's own format separators. Applied AFTER
    escape_typst_string(), which has already doubled every literal
    backslash -- so any backslash this function introduces is
    unambiguously new, and no lone (unescaped) '#'/'>' can survive
    in the result."""
    return text.replace("#", "\\#").replace(">", "\\>")


def make_include_edge_key(parent_docname, child_docname, occurrence=0):
    escaped_parent = _escape_include_edge_separators(escape_typst_string(parent_docname))
    escaped_child = _escape_include_edge_separators(escape_typst_string(child_docname))
    return f"{escaped_parent}#{occurrence}>{escaped_child}"
```

Applied to the two docnames only, never to the `#`/`>` the f-string format itself inserts.

**Single-derivation-point convention this fix must respect** (`translator.py:198-210` docstring,
verbatim):
```python
"""
This is the SINGLE derivation point for this phase's edge-key format,
called by BOTH the builder's graph computation
(``TypstBuilder._build_include_edge_map()``, via
``derive_master_edge_keys()``) and the translator's own guard emission
(``visit_toctree``). A second, independently-spelled edge-key
expression anywhere in the codebase is exactly the drift class this
single-function rule exists to reject...
"""
```
Because this is the single derivation point (two callers: `translator.py:294` graph side,
`translator.py:5336`/`visit_toctree` emission side), fixing it once fixes both automatically — no
`builder.py` change is needed for BLD-07 itself.

**RED-evidence pattern to copy:** `tests/fixtures/state_guard_substring_key_gate/` (`conf.py`,
`index.rst`, plus doc files) is the nearest precedent fixture shape for a real
`sphinx-build → typst.compile()` gate exercising the include-edge-state machinery. A new fixture
directory with a `#`-bearing docname is needed (Wave 0 gap explicitly flagged in RESEARCH.md); model
its `conf.py`/`index.rst` structure on this existing fixture rather than inventing a new shape.
Confirm current test-harness conventions by reading `tests/test_state_guard_shapes_gate.py:660-730`
(the `state_guard_substring_key_gate` build/assertion block) before writing the new fixture's
asserting test.

**Unit-test pattern to copy for the pure-function property half:**
`tests/test_include_edge_derivation_unit.py`'s existing `TestDeriveMasterEdgeKeysTraversal` class
shape (imports at top of file, `from typsphinx.translator import (... make_include_edge_key ...)`,
plain-dict fixtures, no Sphinx build) — add a new test class in the same file asserting
`make_include_edge_key`'s injectivity directly against `#`/`>`-bearing docnames.

---

### `typsphinx/translator.py` — BLD-08 fix in `derive_master_edge_keys`/`walk`

**Analog:** `sphinx.errors.ExtensionError` raise-site convention, already established elsewhere in
this codebase but NOT yet in `translator.py` — nearest concrete raise site is in `builder.py`
(RESEARCH.md cites `builder.py:1877-1887` as "a representative raise site"; also present in
`template_registry.py`, `template_engine.py`). Pattern: a single f-string message naming the
offending value(s), no bare `RuntimeError`/uncaught traceback.

**Current implementation** (`translator.py:288-299`, verified this session):
```python
traversed: List[str] = [master_docname]
edge_keys: List[str] = []

def walk(parent: str) -> None:
    for child in toctree_includes.get(parent, []):
        if child not in traversed:
            edge_keys.append(make_include_edge_key(parent, child, occurrence=0))
            traversed.append(child)
            walk(child)
        # else: already traversed -- dark, no edge emitted (first-encounter-wins)

walk(master_docname)
return tuple(edge_keys)
```
No depth parameter, no bound — a long straight-line include chain raises a bare, uncaught
`RecursionError` through `TypstBuilder._build_include_edge_map()` (`builder.py:459`).

**Candidate construction** (RESEARCH.md Pattern 3, `[ASSUMED]` for the exact constant/wording; the
depth-threading shape and named-exception requirement are LOCKED by CONTEXT.md's Claude's
Discretion):
```python
from sphinx.errors import ExtensionError  # NEW import — translator.py has none today

_MAX_INCLUDE_CHAIN_DEPTH = 900  # fixed module constant, NOT sys.getrecursionlimit()

def derive_master_edge_keys(toctree_includes, master_docname):
    traversed: List[str] = [master_docname]
    edge_keys: List[str] = []

    def walk(parent: str, depth: int, path: Tuple[str, ...]) -> None:
        if depth > _MAX_INCLUDE_CHAIN_DEPTH:
            raise ExtensionError(
                f"typsphinx: include chain from {master_docname!r} exceeds "
                f"{_MAX_INCLUDE_CHAIN_DEPTH} levels (reached depth {depth} at "
                f"{path[0]!r} -> ... -> {path[-1]!r}); this is a very deep "
                f"toctree nesting, not a detected cycle."
            )
        for child in toctree_includes.get(parent, []):
            if child not in traversed:
                edge_keys.append(make_include_edge_key(parent, child, occurrence=0))
                traversed.append(child)
                walk(child, depth + 1, path + (child,))

    walk(master_docname, depth=0, path=(master_docname,))
    return tuple(edge_keys)
```
Message must NOT claim to have detected a cycle (a cycle is already dark via `traversed`
membership at any depth — only a genuinely deep acyclic chain can reach this bound).

**Import verification:** `translator.py:8-15` currently imports `re`, `typing`, `docutils.nodes`,
`sphinx.addnodes`, `sphinx.locale.admonitionlabels`, `sphinx.util.logging`,
`sphinx.util.docutils.SphinxTranslator` — no `sphinx.errors` import present (verified this
session). `builder.py:17` already has `from sphinx.errors import ExtensionError` — copy that exact
import line into `translator.py`.

**Test pattern to copy:** `tests/test_include_edge_derivation_unit.py`'s
`TestDeriveMasterEdgeKeysTraversal` class (`:64-149`) — construct a synthesized deep/linear
`toctree_includes` dict (`{"d0": ["d1"], "d1": ["d2"], ..., "d999": ["d1000"]}`) and call
`derive_master_edge_keys()` directly; assert `pytest.raises(ExtensionError)` instead of the current
uncaught `RecursionError`. Zero new fixtures needed — pure unit level per D-05.

---

### `typsphinx/builder.py` — BLD-09 fix in `_track_image`

**Analog:** `_is_drive_qualified()` + `posixpath.isabs()` composite predicate, already used by
`_escapes_outdir()` at `builder.py:161` — the EXACT platform-independent idiom this fix routes
`_track_image()` onto.

**Sibling function already solving this** (`builder.py:153-161`, verified this session):
```python
segments = stem.replace("\\", "/").split("/")
# posixpath.isabs(), not path.isabs(): this function's own contract is
# platform-independent (D-05) ...
return ".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)
```

**Current buggy gate** (`builder.py:1561`, confirmed this session via `grep -n "path.isabs(resolved_uri)"`
— matches RESEARCH.md's `:1561`, NOT the stale ROADMAP-cited `:910`):
```python
if path.isabs(resolved_uri):
```
`path` is `os.path` (`from os import path`, `builder.py:11`), which resolves to `ntpath` on
Windows. CPython 3.13 narrowed `ntpath.isabs()`: a driveless path beginning with a single leading
separator (`\typsphinx_test\chart.png`) is no longer "absolute."

**Fix (locked by CONTEXT.md SC#4, exact predicate swap):**
```python
if posixpath.isabs(resolved_uri) or _is_drive_qualified(resolved_uri):
```
`posixpath` is already imported (`builder.py:8`); `_is_drive_qualified()` is already defined in the
same module (`builder.py:85-118`, per RESEARCH.md's cited range) — no new symbol, no new import.

**Test pattern to copy:** `tests/test_builder.py`'s Phase 50 relocation cluster, specifically the
existing `test_post_process_images_rehome_escape_relocates_with_warning` (`:511`, per CONTEXT.md
D-05's own citation) — DO NOT revert this test (it was drive-qualified in plan 52-09 to survive
CPython 3.13's Windows narrowing); ADD a new, separate driveless-absolute case beside it, following
the same `temp_sphinx_app` + planted-URI + `self.images`-keys-assertion shape used throughout
`tests/test_builder.py:392-660`.

---

### `typsphinx/builder.py` — IMG-03 fix in `_track_image` (escape branch)

**Analog:** the sibling collision branch two lines below in the SAME method — already injective,
the property to restore in the escape branch (though the exact mechanism differs — the collision
branch keeps `rel_uri` in full; the escape branch's whole point is basename-only naming, so a hash
prefix restores injectivity without losing that intent).

**Current asymmetric implementation** (verified this session):
```python
# Escape branch — builder.py:1589 (defect site)
key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"

# Collision branch — builder.py:1602 (already correct, unchanged by this fix)
key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"
```
`RESERVED_IMAGE_NAMESPACE = "_typst_converted"` (`builder.py:38`). Two absolute URIs in different
directories sharing a basename both escape → both flatten to the identical key →
`if key not in self.images` (`builder.py:1610`) makes the FIRST one tracked win silently.

**Fix (Claude's Discretion recommendation, matching the todo's documented escape hatch):**
```python
import hashlib  # NEW import — not currently used anywhere in typsphinx/

key = f"{RESERVED_IMAGE_NAMESPACE}/{hashlib.sha1(resolved_uri.encode()).hexdigest()[:8]}-{path.basename(resolved_uri)}"
```
`.encode()` is required — `hashlib.sha1()` needs `bytes`, `resolved_uri` is `str` (the todo's own
pseudocode elides this — flagged so the fix doesn't hit a `TypeError`). Pure function of
`resolved_uri` alone (preserves D-02's write-order independence); contains no `..` (preserves Phase
50 SC#2 outdir containment). The collision branch (`:1602`) is explicitly NOT touched — it is
already injective, and touching it is out of scope (Deferred Ideas).

**Load-bearing collateral — two EXISTING tests assert the CURRENT (pre-fix) key format and must be
updated in the SAME change or they regress:**
```python
# tests/test_builder.py:561 (inside test_post_process_images_rehome_escape_relocates_with_warning, :511)
assert img["uri"] == "_typst_converted/chart.png"
# tests/test_builder.py:623 (inside test_post_process_images_rehome_cross_drive_value_error_relocates, :578)
assert img["uri"] == "_typst_converted/crossdrive.png"
```
These are NOT IMG-03's RED evidence (they don't reproduce the basename-collision defect) — they are
collateral characterizing the escape branch's key SHAPE, which the fix changes. Update both
assertions to the new hashed format in the same change (Pitfall 2 in RESEARCH.md).

**Test pattern to copy for the new RED:** same `tests/test_builder.py` Phase 50 cluster shape
(`:392-660`) — plant two URIs in different directories sharing a basename, run
`post_process_images()`/`_track_image()`, assert both keys are present and distinct in
`self.images` (currently they'd collapse to one).

---

## Shared Patterns

### "Single derivation point" discipline (cross-cutting, applies to XREF-05, BLD-07, IMG-03)
**Source:** `make_include_edge_key`'s own docstring (`translator.py:198-210`), `_sanitize_label`'s
own docstring (`translator.py:5023-5057`)
**Apply to:** Every fix in this phase. Each of the five defects exists because exactly ONE shared
string-derivation function has a subtle non-injectivity; the fix must land INSIDE that single
existing function, never as a second, independently-spelled expression beside it. This is the
project's own stated drift-rejection convention, not a Phase-55-specific pattern.

### RED-first evidence discipline (cross-cutting, all five defects)
**Source:** `tests/test_xref_compile_time_guard_render_gate.py::test_label_collision_guard_links_to_decoy`
(the model for "capture today's buggy behavior as a passing assertion, THEN invert it")
**Apply to:** XREF-05 (invert existing test), BLD-07 (new real-compile fixture), BLD-08 (new unit
test asserting today's `RecursionError`, then asserting the new `ExtensionError`), BLD-09/IMG-03
(new unit tests in `tests/test_builder.py`). Binding constraint #6 requires the pre-fix assertion
recorded before implementation for every defect, at the evidence level D-05 sets per-defect.

### `ExtensionError` as the project's named-failure convention
**Source:** `builder.py:17` (`from sphinx.errors import ExtensionError`), used at ~23 raise sites
across `builder.py`/`template_registry.py`/`template_engine.py`
**Apply to:** BLD-08 only (the sole defect introducing a new failure-signaling path). Never use a
bare `RuntimeError` or let `RecursionError` propagate uncaught — this project's established
convention for fatal, user-facing build errors is `ExtensionError` with a single f-string message
naming the offending value(s).

### Platform-independent path predicate (`posixpath.isabs(...) or _is_drive_qualified(...)`)
**Source:** `builder.py:153-161` (inside `_escapes_outdir()`)
**Apply to:** BLD-09 only. This exact composite predicate is already measured against the
`windows-latest` CI lane (per RESEARCH.md's "Don't Hand-Roll" table) — do not invent a fresh
`startswith(("/", "\\"))` heuristic; reuse the existing symbols verbatim.

## No Analog Found

None. Every file this phase touches is a modification to existing, already-analyzed code — there
are no wholly new source files. The closest thing to "no analog" is the property-style unit tests
recommended for XREF-05 (Pitfall 3 mitigation: probing `_sanitize_label`'s boundary with a `_u`
followed by non-hex text, a doubled full token, a partial trailing `_u2`) — no existing test in the
codebase exercises `_sanitize_label` with this kind of adversarial-shape input, so this is a new
test pattern rather than a copied one. Model its structure on ordinary pytest parametrized-case
style already used throughout `tests/test_translator.py` (not independently re-read this session;
grep for existing `_sanitize_label` unit coverage there before writing).

## Metadata

**Analog search scope:** `typsphinx/translator.py`, `typsphinx/builder.py`,
`tests/test_xref_compile_time_guard_render_gate.py`, `tests/test_include_edge_derivation_unit.py`,
`tests/test_builder.py`, `tests/fixtures/state_guard_substring_key_gate/`,
`tests/fixtures/xref_label_collision_guard_gate/`
**Files scanned:** 7 (2 source, 3 test, 2 fixture dirs), plus targeted greps confirming import lists
and the current (non-stale) line number for BLD-09's fix site
**Pattern extraction date:** 2026-08-16
**Note on stale line numbers:** Per this task's instruction and RESEARCH.md Pitfall 1, the
ROADMAP-cited `builder.py:910` for BLD-09 was re-verified this session via
`grep -n "path.isabs(resolved_uri)" typsphinx/builder.py` → confirmed at `:1561`, matching
RESEARCH.md's own measurement, not the stale citation. Re-verify again at execution time if earlier
Phase 55 waves touch `builder.py` first.
