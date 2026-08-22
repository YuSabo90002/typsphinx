# Phase 55: v0.8.0-Derived Defects - Research

**Researched:** 2026-08-16
**Domain:** Sphinx extension internals — docutils→Typst translation (`translator.py`) and build-time
image/output handling (`builder.py`). No new external technology; this phase is five independent,
narrow bug fixes in an existing, well-documented codebase.
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**XREF-05 — where the label-collision fix lands**

- **D-01:** The fix lands in `_sanitize_label` (`translator.py:5065`), by making the sanitization
  injective — the input's own literal escape-token pattern is re-escaped so two distinct docnames
  can never produce one label. It is **not** a Typst-side "does the intended document exist"
  mechanism. Rejected alternatives: a shared-label `metadata` marker carrying the raw docname (the
  existing per-document marker's label is on the colliding side; a second marker's safety under
  `query()` is unmeasured; adds Typst to every guarded reference site), and reusing Phase 49's
  `state("typsphinx:include-edges")` (holds edge keys, not docnames; a master never appears as a
  child of itself; would add an XREF dependency on the include graph). Reversible — confined to one
  function.

- **D-02:** The re-escape targets **the full `_u<hex>_` token pattern only**, not every `_u`
  occurrence — ordinary ids (`foo_util` and friends) keep byte-identical labels. Measured churn: 23
  `_u2f_` and 19 `_u40_` expected-value occurrences across `tests/` stay as they are (they come from
  `/` and `@` inputs containing no escape token); the only literal-`_u<hex>_`-spelling docname in the
  tree is `tests/fixtures/xref_label_collision_guard_gate/a_u2f_b.rst`. No second escaping primitive
  is minted — the rule lives inside `_sanitize_label` and nowhere else.

- **D-03:** The fix is announced in the **`Unreleased` section of `CHANGELOG.md` as `Fixed`, written
  in THIS phase**, not left to Phase 57. Not a breaking change — v0.9.0's two declared breaking axes
  stay two. The entry may note a label name changes for an id literally containing the escape token;
  PDF appearance is unchanged, only the `.typ` label name and the PDF link destination name.

- **D-04:** `tests/test_xref_compile_time_guard_render_gate.py::test_label_collision_guard_links_to_decoy`
  is today's **characterization test of the bug** (asserts `manual.pdf`'s link destinations DO
  include `a_u2f_b:nested-target`, resolving to the decoy). That currently-passing assertion IS SC#1's
  "pre-fix link-to-decoy behaviour recorded first" — capture as RED evidence, then invert. The
  fixture's own `conf.py` load-bearing-properties comment block (a)–(d) is updated in the same change
  so it stops describing an accepted limit.

**Evidence bar per defect (D-05)** — decided per defect rather than uniformly:
- **XREF-05** — real two-master `sphinx-build -b typstpdf` + `typst.compile()` (the existing
  collision fixture is that compile).
- **BLD-07** — **a real `sphinx-build → typst.compile()` fixture** with a `#`-bearing docname
  (output-visible defect: a collided key makes a guard that must not fire, fire). Nearest fixture
  precedent: `tests/fixtures/state_guard_substring_key_gate/`.
- **BLD-08** — **unit level**, in `tests/test_include_edge_derivation_unit.py`. Never reaches
  output (exception-type problem); a synthesized `toctree_includes` mapping is enough — no real
  1000-deep fixture needed.
- **IMG-03** — **unit level**, in `tests/test_builder.py`, beside the Phase 50 relocation tests.
- **BLD-09** — platform-independent **string-shape** test (SC#4), fix on the **product** side
  (`builder.py:1561`); the 52-09 test-side repair does not close it.

### Claude's Discretion

- **IMG-03 key derivation.** Recommendation: `key = f"{RESERVED_IMAGE_NAMESPACE}/{sha1(resolved_uri)[:8]}-{basename}"` —
  a pure function of `resolved_uri` (D-02's write-order independence holds), contains no `..`
  (Phase 50 SC#2 outdir containment holds). The **collision** branch (`builder.py:1602`) does NOT
  change — it already keeps the full `rel_uri` and is injective; the defect is the asymmetry's escape
  half only. The existing warning text at `:1590-1593` already names the original URI and the new
  key — no new content needed.
- **BLD-08 depth bound.** Recommendation: keep the recursion (COMP-05's sibling-order requirement is
  why it is recursive; `49-EXPECTED-STRUCTURE.md` names a forward-push LIFO stack as forbidden) and
  thread a depth counter through `walk()`; raise `sphinx.errors.ExtensionError` above a
  **module-level constant with a commented rationale**, not a value read from
  `sys.getrecursionlimit()`. A *cycle* cannot reach this bound (`traversed` membership only grows, so
  a cycle is already dark) — the message should name the depth and the chain (at least head and tail
  docnames) and must not claim to have found a cycle it did not measure.
- **BLD-07 escape spelling.** Recommendation: one replacement rule, written exactly once, inside
  `make_include_edge_key`, applied to the **two docnames only** — never to the `#`/`>` the format
  itself inserts. `escape_typst_string` keeps its current four-character contract; do not widen it
  (it is used at many sites that do not want `#` escaped).
- **BLD-09 fixture disposition.** Plan 52-09 drive-qualified the fixture in
  `test_post_process_images_rehome_escape_relocates_with_warning` so it stays absolute on Windows
  under CPython 3.13. Recommendation: **add** a driveless-absolute case rather than reverting that
  fixture.
- Plan/wave decomposition, test file naming and placement, and whether the two `translator.py`
  defects (BLD-07, BLD-08) share one plan — left open.

### Deferred Ideas (OUT OF SCOPE)

- **Typst-side "does the intended document exist" evidence** (a shared-label `metadata` marker
  carrying the raw docname, or a published docname array). Rejected for XREF-05 under D-01. A future
  requirement needing docname-level compile-time evidence deserves its own requirement.
- **Widening `escape_typst_string()` to escape `#`/`>`** — rejected; used at many sites that do not
  want `#` escaped.
- **Reverting plan 52-09's drive-qualified fixture** — add a driveless case instead.
- **Making `_track_image()`'s collision branch hash-keyed too** — no; that branch is already
  injective. Recorded so a reviewer does not read the remaining asymmetry as an oversight.
- Release-pipeline `release-create-job-missing-uv-verify-end-to-end` todo — belongs with a release
  phase, not here.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| XREF-05 | A label collision no longer links to a decoy — a reference to the absent docname degrades to plain text | `_sanitize_label` injectivity mechanism verified below (translator.py:5023-5069); collision proof re-derived from source; exact fix construction left as an implementation decision, one candidate offered |
| BLD-07 | Include-edge keys cannot collide through their own `#`/`>` separators | `make_include_edge_key` verified (translator.py:195-231); a concrete, proven-injective escaping construction provided |
| BLD-08 | A too-deep include chain fails by name (`ExtensionError`), not `RecursionError` | `derive_master_edge_keys`/`walk()` verified (translator.py:234-300); `ExtensionError` import precedent found in `template_registry.py`/`template_engine.py`/`builder.py`, confirmed ABSENT from `translator.py` today — new import needed |
| BLD-09 | A driveless-absolute Windows image URI reaches the rehome/relocate/warn branch on Python 3.13 | `_track_image()` verified (builder.py:1499-1616); the exact bare `path.isabs()` call confirmed at builder.py:1561 (NOT :910 as the phase description/ROADMAP states — see Pitfalls); sibling idiom `_is_drive_qualified()` + `posixpath.isabs()` verified at builder.py:85-161; CPython 3.13 `ntpath.isabs()` behavior change independently reproduced this session |
| IMG-03 | Two escaping images sharing a basename stay distinct | Asymmetric key derivation verified at builder.py:1589 vs :1602; hashed-key construction from the todo's own escape hatch verified importable (`hashlib` currently unused anywhere in `typsphinx/`, zero new runtime deps); two existing tests whose assertions embed the CURRENT key format identified and must be updated in the same change |
</phase_requirements>

## Summary

All five defects are narrow, well-diagnosed, already-measured bugs in two files (`typsphinx/translator.py`,
`typsphinx/builder.py`) that this session re-verified line-by-line against the current tree. Every
defect has a pending todo with root-cause analysis, and three of the five (BLD-07, BLD-08, IMG-03)
carry a documented candidate fix from prior-phase review or the todo's own "Solution" section. None
requires a new external dependency: `hashlib` (IMG-03) and `sphinx.errors.ExtensionError` (BLD-08)
are both already used elsewhere in this codebase (`template_registry.py`, `template_engine.py`,
`builder.py`) or are Python stdlib — this phase only adds an import statement to a file that does not
yet have one (`translator.py` has no `ExtensionError` import today; `builder.py` has no `hashlib`
import today).

The two `translator.py` defects (BLD-07, BLD-08) sit in the five module-level functions Phase 49
added immediately after `escape_typst_string()` (`translator.py:195-377`); the two `builder.py`
defects (BLD-09, IMG-03) sit in the same 118-line method, `_track_image()`
(`builder.py:1499-1616`), touching adjacent branches. XREF-05 is isolated to one function,
`_sanitize_label()` (`translator.py:5023-5069`), reached by all label-emitting call sites through
`_namespace_label()`.

One load-bearing cross-cutting finding this session surfaced: fixing IMG-03's key format will change
the exact string two EXISTING passing tests assert
(`test_post_process_images_rehome_escape_relocates_with_warning` at `tests/test_builder.py:511`, and
`test_post_process_images_rehome_cross_drive_value_error_relocates` at `:578`, both currently
asserting `img["uri"] == "_typst_converted/chart.png"` / `"_typst_converted/crossdrive.png"`). These
two assertions are NOT new REDs for IMG-03 to fix — they characterize the escape branch's CURRENT
(pre-fix) behavior — but IMG-03's own fix will flip them to fail unless updated in the same change.
This is a "disjoint files still collide at merge" style risk within a SINGLE plan, not across plans,
and the plan for IMG-03 must account for it explicitly.

**Primary recommendation:** Treat this as five small, independent Wave-packable fixes gated on file
contention only (`translator.py`: XREF-05, BLD-07, BLD-08; `builder.py`: BLD-09, IMG-03), each with
its own RED-first fixture at the evidence level D-05 already fixed per defect. Do not batch XREF-05
with BLD-07/BLD-08 into one plan purely because they share a file — XREF-05's evidence bar (real
two-master compile) and fix surface (`_sanitize_label` only) are unrelated to the include-graph
functions BLD-07/BLD-08 touch.

## Architectural Responsibility Map

This project has no browser/API/DB tiers — it is a single-process Sphinx builder extension. The
relevant "tiers" are its own internal layering (doctree → translator → writer → template engine →
builder → PDF compiler).

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Label collision avoidance (XREF-05) | Translator (`translator.py`, `_sanitize_label`) | — | Sole label-alphabet primitive; reached by all 9 label-emitting sites through `_namespace_label()` |
| Include-edge key escaping (BLD-07) | Translator (`translator.py`, `make_include_edge_key`) | Builder (`_build_include_edge_map`, calls the same function) | Single derivation point called from both the graph side and the emission side — no builder-side change needed, only the shared function |
| Include-chain depth bound (BLD-08) | Translator (`translator.py`, `derive_master_edge_keys`/`walk`) | Builder (`_build_include_edge_map`, the call path the raised error surfaces through) | The recursion lives in the translator module; the builder is only a caller, unchanged |
| Image URI absolute-path classification (BLD-09) | Builder (`builder.py`, `_track_image`) | — | Builder owns all image-tracking/relocation logic; no translator involvement |
| Image relocation key derivation (IMG-03) | Builder (`builder.py`, `_track_image`) | — | Same method, adjacent branch to BLD-09 |

## Standard Stack

No new libraries. This phase modifies existing internal functions only.

### Core (already in use, no version change)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `re` | 3.12+ | `_sanitize_label`'s existing regex substitution (XREF-05 fix site) | Already imported, `translator.py:8` |
| Python stdlib `hashlib` | 3.12+ | `sha1(resolved_uri)` for IMG-03's hashed key (Claude's Discretion recommendation) | Stdlib, zero new runtime deps (binding constraint #11); `[VERIFIED: typsphinx/builder.py grep — no existing `hashlib`/`sha1` import found in `typsphinx/*.py` this session]` |
| `sphinx.errors.ExtensionError` | pinned via Sphinx dependency | BLD-08's named exception, replacing raw `RecursionError` | `[VERIFIED: typsphinx/template_registry.py:31, typsphinx/template_engine.py:15, typsphinx/builder.py:17 — all already `from sphinx.errors import ExtensionError`]`. **Not yet imported in `translator.py`** — `[VERIFIED: typsphinx/translator.py:8-15 — imports are `re`, `typing`, `docutils.nodes`, `sphinx.addnodes`, `sphinx.locale.admonitionlabels`, `sphinx.util.logging`, `sphinx.util.docutils.SphinxTranslator` — no `sphinx.errors` import present]` |
| `posixpath` | stdlib | BLD-09's platform-independent `isabs()` | `[VERIFIED: typsphinx/builder.py:8 — already `import posixpath`]` |

**Installation:** none — no `pip install` / `uv add` needed for any of the five fixes.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero external packages. Both symbols the discretion
recommendations reach for (`hashlib.sha1`, `sphinx.errors.ExtensionError`) are, respectively, Python
stdlib and an already-a-project-dependency (`sphinx`) module already imported elsewhere in this
codebase. No `npm view` / `pip index versions` / registry check applies.

## Architecture Patterns

### System — where each defect's fix intercepts the existing pipeline

```
doctree (docutils)
   |
   v
TypstTranslator.visit_*/depart_*  (translator.py)
   |-- visit_document ---------> _namespace_label() -> _sanitize_label()      [XREF-05 fix site]
   |-- visit_reference (xref) --> _label_existence_guard() (unchanged, D-01)
   |-- visit_toctree -----------> make_include_edge_key()                     [BLD-07 fix site]
   |                                (also called from builder side below)
   v
body string
   |
   v
TypstWriter.translate()  (writer.py) -- template application (unrelated to this phase)
   |
   v
TypstBuilder.write_doc() / post_process_images()  (builder.py)
   |-- post_process_images -> _track_image()
   |      |-- path.isabs(resolved_uri) gate ------------------> [BLD-09 fix site: builder.py:1561]
   |      |-- escape branch key = NAMESPACE/basename ---------> [IMG-03 fix site: builder.py:1589]
   |      |-- collision branch key = NAMESPACE/rel_uri  (unchanged, injective already)
   |
   v
TypstBuilder._build_include_edge_map()  (builder.py:459, calls translator.py's derive_master_edge_keys)
   |-- nested walk() recursion, no depth bound --------------> [BLD-08 fix site: translator.py:291-299]
   |
   v
.typ files -> [typst.compile()] -> PDF
```

A reader tracing XREF-05: a docname enters `visit_document`, gets namespaced+sanitized into a label,
collides with another docname's sanitized label, and the collision is invisible until
`_label_existence_guard()`'s `query()` finds the wrong document's label at Typst compile time — the
guard itself is unchanged (D-01), only the upstream label alphabet changes.

A reader tracing BLD-07/BLD-08: both defects live in the SAME five-function block
(`translator.py:175-377`) that Phase 49 added, called from two places — the graph side
(`TypstBuilder._build_include_edge_map()`, `builder.py:459`) and the emission side
(`visit_toctree`, inside the translator). Because `make_include_edge_key` is the single derivation
point, fixing it once fixes both call sites automatically (no builder.py change needed for BLD-07).
BLD-08's depth bound is local to the translator module's own recursive helper; the builder is
merely the caller through which a raised `ExtensionError` surfaces.

A reader tracing BLD-09/IMG-03: both live inside one 118-line method, `_track_image()`
(`builder.py:1499-1616`), in adjacent branches of the same `if path.isabs(resolved_uri):` block —
BLD-09 fixes the gate condition itself (line 1561), IMG-03 fixes the key format inside the
already-entered escape branch (line 1589). A single plan touching this method twice for two
different reasons is architecturally coherent (CONTEXT.md's own Specifics section makes the same
observation) but must still carry two independent REDs.

### Recommended Project Structure

No new files/directories. Existing layout (unchanged):
```
typsphinx/
├── translator.py      # XREF-05, BLD-07, BLD-08 fixes land here
├── builder.py          # BLD-09, IMG-03 fixes land here
tests/
├── test_xref_compile_time_guard_render_gate.py    # XREF-05's real-compile RED lives here
├── test_include_edge_derivation_unit.py            # BLD-07 (real-compile — new fixture needed
│                                                      elsewhere) and BLD-08 (unit) REDs
├── fixtures/
│   ├── xref_label_collision_guard_gate/            # existing — XREF-05's fixture, conf.py
│   │                                                  (a)-(d) comment block needs updating (D-04)
│   └── state_guard_substring_key_gate/             # nearest precedent shape for BLD-07's
│                                                      real-compile fixture — a NEW fixture
│                                                      directory is needed for a `#`-bearing docname
└── test_builder.py     # IMG-03's unit RED lives beside the Phase 50 relocation cluster
                          # (lines 392-660); BLD-09's string-shape RED likely lives here too
```

### Pattern 1: XREF-05 — injective re-escaping of the encoder's own token shape

**What:** `_sanitize_label` maps every character outside `[A-Za-z0-9_.:-]` to a `_u{codepoint:x}_`
token via a single regex substitution:

```python
# Source: typsphinx/translator.py:5065-5069 [VERIFIED: typsphinx/translator.py:5065-5069]
return re.sub(
    r"[^A-Za-z0-9_.:-]",
    lambda m: f"_u{ord(m.group(0)):x}_",
    name,
)
```

Because `_`, digits, and hex letters are ALL in the allowed set, a literal input substring that
already spells `_u2f_` (the encoder's own output shape for `/`, since `ord('/') == 0x2f`) passes
through completely unchanged. `_namespace_label` (`translator.py:5114-5116`) prefixes `docname:`
before calling this, so docname `a/b` and docname `a_u2f_b` both produce the literal string
`a_u2f_b:nested-target` for a same-named id `nested-target` — collision confirmed by direct reading
of both functions this session.

**When to use:** Any escaping scheme whose escape-token alphabet is a SUBSET of its own "safe"
character range must additionally guard against literal occurrences of its own token shape in the
input — otherwise the encoding is not injective. This is the general lesson; D-01/D-02 constrain the
fix to "re-escape the input's own literal `_u<hex>_` pattern," not the general class.

**Candidate construction (NOT locked — an implementation proposal for the planner to evaluate,
consistent with D-01/D-02's constraints):** Before the main substitution runs, first neutralize any
literal occurrence of the exact token shape `_u[0-9a-f]+_` in the raw input by doubling its leading
underscore (`_u2f_` → `__u2f_`), since the encoder itself never emits a double-underscore-prefixed
token and every character used (`_`) is already in the allowed set, so this pre-pass is itself a
no-op on the character-validity check and introduces no new escaping-order hazard. This keeps
D-02's contract exactly: only a LITERAL `_u<hex>_` substring is touched (verified via
`re.sub(r"_u[0-9a-f]+_", ...)`), an ordinary id like `foo_util` never matches this pattern (no
trailing `_` immediately after hex digits following `_u`), so its `_u`/`_util` substrings are left
alone. **This exact regex and doubling strategy was not verified against a real `typst.compile()`
this session — it is a proposed Python-level string transform, not a Typst-syntax question (no
Typst-invalid characters are introduced), but the planner should still record it as a design decision
requiring the same recorded-RED-first discipline BLD-07/BLD-08 use.** `[ASSUMED]`

### Pattern 2: BLD-07 — injective separator escaping inside the single derivation point

**What:** `make_include_edge_key` currently:

```python
# Source: typsphinx/translator.py:229-231 [VERIFIED: typsphinx/translator.py:229-231]
escaped_parent = escape_typst_string(parent_docname)
escaped_child = escape_typst_string(child_docname)
return f"{escaped_parent}#{occurrence}>{escaped_child}"
```

`escape_typst_string` (`translator.py:141-172`, `[VERIFIED]`) escapes `\`, `"`, `\n`, `\r`, `\t` —
NOT `#` or `>`. A docname containing either character passes through unescaped, so its literal `#`
or `>` is indistinguishable from the format's own inserted separators, producing the collision the
todo demonstrates (`make_include_edge_key('a', 'b#1>c', occurrence=0)` == `make_include_edge_key('a#0>b', 'c', occurrence=1)` == `'a#0>b#1>c'`).

**Candidate construction, proven injective (see reasoning below), matching the Claude's Discretion
recommendation exactly ("applied to the two docnames only... escape_typst_string keeps its current
four-character contract"):**

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

**Why this is injective (research-derived reasoning, not read from any source — offered so the
planner can sanity-check a fix without re-deriving this):** After `escape_typst_string` runs, every
backslash in the result is part of a doubled `\\` pair (originals were doubled; the function
introduces no new lone backslash). Applying `#`→`\#`/`>`→`\>` afterward means every `#`/`>` that
survives in `escaped_parent`/`escaped_child` is now IMMEDIATELY preceded by a backslash that came
from THIS step, not from the original doubling — so the only unescaped (bare, non-backslash-preceded)
`#` and `>` characters anywhere in the final key are the ones `make_include_edge_key`'s own f-string
inserts between the two components. This makes the three-part boundary always uniquely locatable,
which is what full injectivity of `(parent, child, occurrence) -> key` requires. `[ASSUMED]` — this
is a proposed construction, not verified against a real Typst compile; a RED-first fixture with a
`#`-bearing docname (D-05's real-compile bar for this defect) is required before trusting it.

**Anti-pattern to avoid:** Widening `escape_typst_string()` itself to include `#`/`>` — explicitly
rejected (Claude's Discretion, Deferred Ideas): it is called from many sites that emit ordinary
Typst string literals where `#` is meaningful markup-mode syntax outside a string, not something
those call sites want touched, and widening it would churn unrelated emitted bytes across the whole
translator.

### Pattern 3: BLD-08 — depth-bounded recursion with a named exception

**What:** `derive_master_edge_keys`'s nested `walk()`:

```python
# Source: typsphinx/translator.py:288-299 [VERIFIED: typsphinx/translator.py:288-299]
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

No depth parameter, no bound — a sufficiently long straight-line include chain raises Python's own
`RecursionError`, uncaught, through `TypstBuilder._build_include_edge_map()`
(`builder.py:459`, `[VERIFIED: typsphinx/builder.py:459-461 — `edge_map[master_docname] = derive_master_edge_keys(toctree_includes, master_docname)`]`)
and out through Sphinx's own build loop as a raw traceback.

**Recommended construction (Claude's Discretion — keep the recursion, thread a depth counter,
raise a NAMED exception above a module constant):**

```python
from sphinx.errors import ExtensionError  # NEW import — translator.py has none today

# Comfortably under CPython's default sys.getrecursionlimit() (1000), leaving
# headroom for Sphinx's own call-stack frames above this walk and this
# module's own per-call overhead, so this guard fires as a clean
# ExtensionError before Python's own RecursionError would. NOT read from
# sys.getrecursionlimit() at runtime (Claude's Discretion) -- a fixed,
# documented constant so behavior does not vary by interpreter/embedder.
_MAX_INCLUDE_CHAIN_DEPTH = 900  # [ASSUMED — exact value is an implementation choice]

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

Note the message explicitly does NOT claim to have detected a cycle — per Claude's Discretion, a
cycle is already structurally dark (the `traversed` membership check catches it, unconditionally, at
any depth) so this bound can only ever be reached by a genuinely deep acyclic chain. `[ASSUMED]` for
the exact constant value and message wording; the depth-threading shape and named-exception
requirement are locked by CONTEXT.md.

**Existing test suite already exercises this function directly** (`[VERIFIED: tests/test_include_edge_derivation_unit.py:64-149]`,
`TestDeriveMasterEdgeKeysTraversal` — seven tests, all constructing a plain `toctree_includes` dict
and calling `derive_master_edge_keys()` directly, no Sphinx build) — this is the exact unit-level
harness D-05 specifies for BLD-08's RED; a synthesized deep/linear `toctree_includes` dict
(`{"d0": ["d1"], "d1": ["d2"], ..., "d999": ["d1000"]}`) reproducing today's `RecursionError` fits
this file's existing pattern precisely with zero new fixtures.

### Pattern 4: BLD-09 — platform-independent absolute-path detection

**What:** `_track_image()`'s current gate:

```python
# Source: typsphinx/builder.py:1561 [VERIFIED: typsphinx/builder.py:1561]
if path.isabs(resolved_uri):
```

`path` is `os.path` (imported as `from os import path`, `[VERIFIED: typsphinx/builder.py:11]`),
which resolves to `ntpath` on Windows. CPython 3.13 narrowed `ntpath.isabs()`: a driveless path
beginning with a single leading separator is no longer "absolute." **Independently reproduced this
session** (Python 3.13.13, `ntpath` module — platform-independent pure-string logic, reproducible on
any OS):

```
>>> ntpath.isabs('\\typsphinx_test\\chart.png')
False
>>> ntpath.isabs('C:\\typsphinx_test\\chart.png')
True
```
`[VERIFIED: direct interpreter session, Python 3.13.13, this repository's environment]`

The sibling function that already avoids this trap:

```python
# Source: typsphinx/builder.py:153-161 [VERIFIED: typsphinx/builder.py:153-161]
segments = stem.replace("\\", "/").split("/")
# posixpath.isabs(), not path.isabs(): this function's own contract is
# platform-independent (D-05) ...
return ".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)
```

**Fix (locked by CONTEXT.md's success criteria, SC#4): route `_track_image()` onto the identical
predicate:**

```python
if posixpath.isabs(resolved_uri) or _is_drive_qualified(resolved_uri):
```

`posixpath` is already imported (`builder.py:8`, `[VERIFIED]`); `_is_drive_qualified()` is already
defined in the same module (`builder.py:85-117`, `[VERIFIED]`) and already used by `_escapes_outdir()`.
No new symbol, no new import — a pure predicate swap at one call site.

**Important line-number discrepancy found this session:** the Phase 55 description text (sourced
from ROADMAP.md) cites the bug's location as **`builder.py:910`**; the pending todo also cites
`:910`. This session's direct read confirms the bare `path.isabs(resolved_uri)` call is at
**`builder.py:1561`** on the current tree, inside `_track_image()`
(`[VERIFIED: typsphinx/builder.py:1561]`). The function itself spans `1499-1616`. This is very
likely drift from intervening commits (Phase 54/54.1 added ~650 lines to `builder.py` for the
template registry) shifting line numbers after the todo/ROADMAP text was written — the CODE and
BEHAVIOR described are unambiguously the same call site (verbatim-matching surrounding code,
docstring, and branch structure), only the line number is stale. **Do not plan against line 910;
verify the current line number again at execution time**, since further Phase 55 edits will shift it
further.

### Pattern 5: IMG-03 — hashed relocation key breaking the basename-only collision

**What:** the escape branch currently discards directory information:

```python
# Source: typsphinx/builder.py:1589 [VERIFIED: typsphinx/builder.py:1589]
key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"
```

while the sibling collision branch keeps the full relative path:

```python
# Source: typsphinx/builder.py:1602 [VERIFIED: typsphinx/builder.py:1602]
key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"
```

Two absolute URIs in different directories sharing a basename both escape → both flatten to the
identical key → `if key not in self.images` (`builder.py:1610`, `[VERIFIED]`) makes the FIRST one
tracked (by `sorted(docnames)` traversal order in `write()`) win silently; the second document
embeds the wrong image with zero diagnostic.

**Fix (Claude's Discretion recommendation, matching the todo's own documented "escape hatch"):**

```python
import hashlib  # NEW import — not currently used anywhere in typsphinx/

# ...
key = f"{RESERVED_IMAGE_NAMESPACE}/{hashlib.sha1(resolved_uri.encode()).hexdigest()[:8]}-{path.basename(resolved_uri)}"
```

`resolved_uri` is a `str`; `hashlib.sha1()` requires `bytes`, so `.encode()` is required (the
todo's own pseudocode, `sha1(resolved_uri)[:8]`, elides this — flagged so the planner does not copy
it verbatim and hit a `TypeError`). `[ASSUMED]` — the exact hash truncation length (`[:8]`) and
`hashlib.sha1` specifically (vs. a different digest) are the todo's own recommendation, not
independently re-derived or benchmarked this session; `sha1` here is a non-cryptographic collision
key (not a security boundary), so its use is unremarkable, but the planner should note it in
passing since automated security scanners sometimes flag `sha1` calls generically — this one is not
a security-sensitive use.

**Load-bearing pitfall — two EXISTING tests assert the current (pre-fix) key format and will break
if not updated in the same change:**

```python
# tests/test_builder.py:561 [VERIFIED: tests/test_builder.py:561]
assert img["uri"] == "_typst_converted/chart.png"
# tests/test_builder.py:623 [VERIFIED: tests/test_builder.py:623]
assert img["uri"] == "_typst_converted/crossdrive.png"
```

Both are in `test_post_process_images_rehome_escape_relocates_with_warning` (`:511`) and
`test_post_process_images_rehome_cross_drive_value_error_relocates` (`:578`) — both currently GREEN,
both exercising the ESCAPE branch IMG-03's fix changes. **These are not IMG-03's RED evidence** (they
don't reproduce the basename-collision defect); they are collateral — they characterize the escape
branch's key SHAPE, which the fix changes. The plan must update both assertions to the new hashed
format in the same change that lands the fix, or the phase-boundary green gate (binding constraint
#2) will regress.

### Anti-Patterns to Avoid

- **Widening `escape_typst_string()`** for BLD-07 — rejected by name in CONTEXT.md; breaks the
  "used at many sites that don't want `#` escaped" invariant.
- **A second, independently-spelled edge-key expression anywhere** — the whole reason
  `make_include_edge_key` exists (`[VERIFIED: translator.py:198-210]`, docstring: "A second,
  independently-spelled edge-key expression anywhere in the codebase is exactly the drift class this
  single-function rule exists to reject").
- **Reading `sys.getrecursionlimit()` at runtime for BLD-08's bound** — explicitly rejected by
  Claude's Discretion; use a fixed, documented module constant instead (embedder/interpreter
  independence).
- **Claiming cycle detection in BLD-08's error message** — the bound can only be reached by a
  genuinely deep acyclic chain (cycles are already dark via `traversed` membership); a message that
  says "cycle detected" would be false.
- **Hash-keying the collision branch too** (IMG-03) — explicitly rejected (Deferred Ideas); it is
  already injective, and touching it would be unscoped churn.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Platform-independent absolute-path detection | A fresh `startswith(("/", "\\"))` heuristic | The existing `posixpath.isabs(stem) or _is_drive_qualified(stem)` idiom (`builder.py:161`) | Already measured against the `windows-latest` CI lane (`47-10/T2`); a fresh heuristic risks re-discovering the same `ntpath` vs. `posixpath` divergence from scratch |
| Collision-resistant key from an arbitrary string | A custom rolling hash or truncated `id()`/`hash()` | `hashlib.sha1(...).hexdigest()[:8]` (stdlib) | `hash()` is randomized per-process (`PYTHONHASHSEED`) unless seeded — NOT deterministic across builds/machines, which would break Phase 50's "pure function of `resolved_uri`" write-order-independence property (D-02) that IMG-03's fix must preserve |
| Named build-abort exception | A bare `raise RuntimeError(...)` or letting `RecursionError` propagate | `sphinx.errors.ExtensionError` | Already the project's own convention for every fatal user-facing build error (23 raise sites across `builder.py`/`template_registry.py`/`template_engine.py`, `[VERIFIED: grep count this session]`); Sphinx's own CLI renders `ExtensionError` with a clean one-line message instead of a Python traceback |

**Key insight:** Every one of these five defects has an existing, already-measured sibling pattern
elsewhere in the SAME two files (`_escapes_outdir()` for BLD-09, `_is_drive_qualified()` for BLD-09,
`make_include_edge_key`'s own docstring warning for BLD-07, the collision branch's `rel_uri` for
IMG-03, `_namespace_label`'s own docstring for XREF-05). None of these fixes requires new design
research — they require *mirroring an idiom the codebase already trusts*, which is also why D-05
tags most of them LOW risk / unit-level evidence.

## Common Pitfalls

### Pitfall 1: Trusting the phase description's/ROADMAP's cited line numbers for BLD-09

**What goes wrong:** Planning or executing against `builder.py:910` (as both the phase description
and the originating todo cite) when the actual current line is `1561`.
**Why it happens:** Phase 54 and 54.1 added roughly 650+ lines to `builder.py` for the template
registry (bundle copying, CONF-17/CONF-18 validation, the pre-write pass) between when the BLD-09
todo was filed (2026-08-15, mid-Phase-54.1) and now. Line numbers drift; textual/structural
references don't.
**How to avoid:** Grep for the literal code (`if path.isabs(resolved_uri):`) rather than trusting a
cited line number, at both planning and execution time. This RESEARCH.md already did this and
confirms the current line is 1561 as of this session — but ANOTHER shift is possible before this
phase executes if earlier waves of THIS phase touch `builder.py` first (BLD-09 and IMG-03 are both
in the same function, so ordering within a wave/plan matters more than absolute line numbers).
**Warning signs:** A `sed -n '910p' builder.py` / line-number-anchored patch that doesn't match the
`git blame`/context the task description describes.

### Pitfall 2: IMG-03's fix silently regressing two currently-green tests

**What goes wrong:** Landing the hashed-key fix without touching
`tests/test_builder.py:561` / `:623` (see Pattern 5 above) turns two currently-passing tests RED,
and if the executor's own gate only samples the NEW test file it added, this regression escapes
detection until the phase-boundary full-suite run.
**Why it happens:** The two assertions look like generic "does relocation happen" checks, not
"exact key format" checks, so it's easy to read them as unrelated to IMG-03's scope (they were
written for BLD-09/IMG-01/IMG-02's escape branch, not IMG-03).
**How to avoid:** Explicitly list these two lines in IMG-03's plan's `files_modified`/expected-diff
before executing, and run the FULL suite (not just the new fixture) as part of IMG-03's own
per-task/per-plan verification, not only at the wave/phase gate.
**Warning signs:** `pytest tests/test_builder.py -k escape_relocates_with_warning` or
`-k cross_drive_value_error_relocates` failing after an IMG-03 change with an `AssertionError`
comparing the OLD literal key string to a new hashed one.

### Pitfall 3: XREF-05's re-escaping construction introduced ad hoc without a proof of injectivity

**What goes wrong:** A quick fix (e.g., "just also escape underscores near digits") that
*coincidentally* passes the one known collision fixture (`a/b` vs. `a_u2f_b`) but is not actually
injective in general — e.g., it might newly collide two DIFFERENT ids that both happen to contain
partial escape-token-shaped substrings after the new transform runs.
**Why it happens:** The bug is subtle (an encoding whose token alphabet overlaps its own "safe"
range) and the fixture-driven, RED-first workflow can produce a fix that satisfies the one asserted
fixture without being provably general.
**How to avoid:** Write the fix as a clearly-stated, order-sensitive regex pass (escape literal
token-shaped substrings BEFORE the main substitution, using a pattern the main substitution's own
character class provably cannot re-produce), and add at minimum one property-style unit test beyond
the fixture: two synthetic ids designed to probe the boundary (e.g., an id containing `_u` followed
by non-hex text, an id containing the FULL token pattern twice, an id ending in a partial `_u2` with
no closing `_`).
**Warning signs:** A fix that special-cases the exact fixture's docname strings rather than
operating on the general `_u[0-9a-f]+_` shape.

### Pitfall 4: Batching XREF-05 into the same plan as BLD-07/BLD-08 purely on file-contention grounds

**What goes wrong:** Because all three defects touch `translator.py`, it is tempting to fold them
into one plan (fewer merge-contention waves) — but XREF-05's fix (`_sanitize_label`, one function,
real two-master compile evidence) and BLD-07/BLD-08's fixes (the five-function include-graph block,
one real-compile + one unit-level evidence) are functionally and evidentially unrelated.
**Why it happens:** CONTEXT.md's own Specifics section flags file contention as "a wave-packing
concern, not a dependency" — but doesn't forbid a shared plan, and shared-file plans are cheaper to
review.
**How to avoid:** CONTEXT.md's own Specifics section explicitly allows treating BLD-07+BLD-08 as
one plan (both Phase-49 artifacts, adjacent code) while flagging their DIFFERENT evidence levels as
something "not [to] let the shared plan blur." XREF-05 has no such explicit permission — keep it a
separate plan even if it shares a wave with BLD-07/BLD-08 for file-contention scheduling.
**Warning signs:** A single plan whose task list mixes `_sanitize_label` assertions with
`make_include_edge_key`/`derive_master_edge_keys` assertions under one shared RED-evidence file.

### Pitfall 5: The stale carve-out for `tests/test_state_guard_shapes_gate.py`

**What goes wrong:** Treating 7 failures in this file as an accepted pre-existing baseline (a
carve-out recorded before Phase 54.1) rather than requiring true zero-failure green.
**Why it happens:** `PROJECT.md`/`STATE.md`'s history records this carve-out from Phase 53's
`deferred-items.md`.
**How to avoid:** `STATE.md` (`[VERIFIED: .planning/STATE.md:112-120, this session's read]`) already
records this carve-out as **measured STALE on 2026-08-16** — the file now passes 18/18 with the
final Phase 54.1 tree at 1318 passed / 5 skipped / 0 failed. **The green bar for Phase 55 is
UNCONDITIONAL ZERO FAILURES** — do not reintroduce the stale carve-out. `tests/deferred-items.md`
under Phase 53 predates this and is superseded.
**Warning signs:** A plan or verification step citing "7 known-failing tests" as an accepted
baseline.

## Code Examples

Every code excerpt below is a direct, verbatim read from the current tree this session (see inline
`[VERIFIED: path:lines]` tags); the four "candidate construction" snippets under Architecture
Patterns 1, 2, 3, and 5 are clearly marked `[ASSUMED]`/proposals, not verified fixes.

### Existing single-derivation-point convention (the pattern all five fixes must respect)

```python
# Source: typsphinx/translator.py:198-210 (make_include_edge_key docstring)
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

### Existing ExtensionError raise-site convention (precedent for BLD-08)

```python
# Source: typsphinx/builder.py:1877-1887 [VERIFIED: grep-located, representative raise site]
raise ExtensionError(
    # ... project convention: a single f-string message naming the
    # offending value(s), no bare RuntimeError/traceback ...
)
```

## State of the Art

| Old Approach (v0.8.0-era) | Current Approach (this phase) | When Changed | Impact |
|--------------------------|-------------------------------|---------------|--------|
| Bare `path.isabs()` for absolute-URI detection in `_track_image()` | `posixpath.isabs(...) or _is_drive_qualified(...)`, matching `_escapes_outdir()`'s already-established idiom | This phase (BLD-09) | Correct behavior restored under CPython 3.13 on Windows for driveless-absolute paths; `ntpath.isabs()` narrowed its definition of "absolute" starting CPython 3.13, `[VERIFIED: reproduced this session on Python 3.13.13]` |
| `escape_typst_string()`'s four-character contract (`\`, `"`, `\n`, `\r`, `\t`) treated as sufficient for ALL string-embedding uses | A second, narrower escaping layer for `#`/`>` specific to `make_include_edge_key`'s own format, NOT added to `escape_typst_string` itself | This phase (BLD-07) | The four-character contract remains the general-purpose Typst string-literal escaper; format-specific separator collisions are now handled at the format's own derivation point, not by widening a shared primitive |

**Deprecated/outdated:**
- The Phase 48-accepted "label-collision false negative" limit (`48-EVIDENCE.md:519`) — accepted at
  the time as a narrow, documented cost; XREF-05 closes it in this phase.
- `test_label_collision_guard_links_to_decoy`'s current assertion (link resolves to the decoy) — a
  characterization test of the bug, inverted by this phase's fix (D-04).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | XREF-05's exact re-escaping regex/construction (double the leading underscore of a literal `_u<hex>_` token before the main substitution runs) | Pattern 1 | If the construction is not actually injective in some edge case, a NEW, more obscure label collision could be introduced instead of closed — mitigated by requiring property-style tests beyond the one known fixture (Pitfall 3) |
| A2 | BLD-07's exact escaping construction (`#`→`\#`, `>`→`\>`, applied after `escape_typst_string`) | Pattern 2 | If the ordering/composition is implemented differently (e.g., before `escape_typst_string` instead of after), the injectivity proof in this document does not hold and must be re-derived |
| A3 | BLD-08's exact depth constant (`900`) and message wording | Pattern 3 | A too-low constant could reject legitimate large doc trees; a too-high constant could still hit `RecursionError` first depending on the surrounding call-stack depth at invocation time (Sphinx's own frames above this walk are not measured in this session) — the planner/executor should pick a value with margin and note it is a policy choice, not a measured limit |
| A4 | IMG-03's exact hash truncation (`sha1(...)[:8]`) and digest choice (`sha1` vs. another) | Pattern 5 | Purely a key-collision-avoidance choice, not security-sensitive; a shorter truncation increases (unlikely) key-collision probability, a longer one is more verbose in warnings/logs — low risk either way |
| A5 | The `_MAX_INCLUDE_CHAIN_DEPTH` constant should NOT be derived from `sys.getrecursionlimit()` | Pattern 3 | This is directly from CONTEXT.md's locked Claude's Discretion text, not an assumption in the strict sense — listed here only because the CONCRETE numeric value chosen to satisfy it is unverified |

**Risk framing:** None of these assumptions are compliance/security/retention-policy questions —
they are implementation-construction details for internal bug fixes. All five carry the mitigation
of D-05's own RED-first discipline: a wrong construction will surface as a failing test before it
ships, not silently.

## Open Questions

1. **Should BLD-07's and BLD-08's REDs share one plan or two?**
   - What we know: CONTEXT.md's Specifics section explicitly permits (but does not require) treating
     them as one plan, while flagging that their evidence levels (real-compile vs. unit) must not
     blur together.
   - What's unclear: Whether a single plan with two independently-verifiable RED fixtures/tests
     satisfies binding constraint #6 as cleanly as two plans would.
   - Recommendation: Either is acceptable; if combined, ensure the plan's task list has two clearly
     separated RED-then-fix task pairs, not one blended task.

2. **Exact numeric value for BLD-08's `_MAX_INCLUDE_CHAIN_DEPTH`.**
   - What we know: must be a fixed module constant, not derived from `sys.getrecursionlimit()`, with
     margin below Python's actual limit (default 1000) to fire before a raw `RecursionError` would.
   - What's unclear: How much of the ~1000-frame budget the surrounding call stack (Sphinx build
     loop + this module's own per-recursion-level overhead, which is more than one frame per level
     since `walk()` itself plus its `for` loop body are on the stack) consumes before `walk()`'s
     first call — this session did not measure it empirically.
   - Recommendation: Pick a conservative value (this document proposes 900 as a starting point) and
     verify empirically during RED-evidence construction: synthesize a chain at exactly the chosen
     depth and one below/above it, confirming the guard fires before Python's own limit would, using
     the unit-level harness `tests/test_include_edge_derivation_unit.py` already establishes.

3. **Does the XREF-05 fix's CHANGELOG-visible label-name change (D-03) require updating any OTHER
   fixture's expected label bytes beyond `a_u2f_b.rst`?**
   - What we know: D-02 measured churn as confined to the one fixture docname that literally spells
     `_u<hex>_` (`tests/fixtures/xref_label_collision_guard_gate/a_u2f_b.rst`); 23 `_u2f_` and 19
     `_u40_` occurrences elsewhere in `tests/` come from `/`/`@` inputs with no literal escape token
     and are unaffected.
   - What's unclear: This session did not independently re-run the grep D-02 describes to confirm
     the 23/19 counts against the CURRENT tree (only read the CONTEXT.md claim); if any other
     fixture was added between Phase 48 and now with a docname that happens to spell `_u<hex>_`
     literally, it would also be affected.
   - Recommendation: Re-run `grep -rn '_u[0-9a-f]\+_' tests/fixtures/ tests/**/*.py` at planning or
     execution time to reconfirm D-02's churn scope against the current tree before finalizing the
     fix's blast radius.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All five fixes, all tests | ✓ | 3.13.13 (this session's environment) `[VERIFIED]` | — |
| `sphinx` (for `sphinx.errors.ExtensionError`) | BLD-08 | ✓ | already a project dependency | — |
| `hashlib` (stdlib) | IMG-03 | ✓ | stdlib, no version | — |
| `typst-py` | XREF-05's and BLD-07's real-compile RED fixtures | assumed present per project's existing `[tool.pytest]` skip guards (`TYPST_AVAILABLE`) — not independently re-verified this session | — | Tests already skip gracefully (`@pytest.mark.skipif(not TYPST_AVAILABLE, ...)`) if absent |
| `pypdf` | XREF-05's and BLD-07's real-compile RED fixtures (link-destination extraction) | assumed present, same skip-guard pattern | — | Same skip-guard fallback |

No missing dependencies with no fallback. This phase adds zero new environment requirements.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest, `[tool.pytest.ini_options]` in `pyproject.toml:79-99` `[VERIFIED: pyproject.toml:79-99]` |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, markers `slow`/`integration`, `--strict-markers`) |
| Quick run command | `uv run pytest tests/test_include_edge_derivation_unit.py tests/test_builder.py -x` (unit-level, fast — BLD-08/IMG-03/BLD-09) |
| Full suite command | `uv run pytest` (per CLAUDE.md worktree-isolated execution: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then `uv run pytest`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| XREF-05 | Absent-target reference degrades to plain text instead of linking to decoy | integration (real `sphinx-build -b typstpdf` + `typst.compile()`) | `uv run pytest tests/test_xref_compile_time_guard_render_gate.py -k collision -x` | ✅ (existing `test_label_collision_guard_links_to_decoy`, to be inverted) |
| BLD-07 | `#`/`>`-bearing docname cannot collide two edge keys | integration (real compile, per D-05) | new test in a new fixture dir + `tests/test_include_edge_derivation_unit.py` (unit half for the pure-function property) | ❌ Wave 0 — new fixture needed, nearest precedent `tests/fixtures/state_guard_substring_key_gate/` |
| BLD-08 | Deep include chain raises named `ExtensionError`, not `RecursionError` | unit | `uv run pytest tests/test_include_edge_derivation_unit.py -x` | ✅ file exists, ❌ specific test class needs adding |
| BLD-09 | Driveless-absolute Windows URI reaches rehome branch on 3.13 | unit, platform-independent string-shape | `uv run pytest tests/test_builder.py -x` | ✅ file exists, ❌ specific test needs adding |
| IMG-03 | Two escaping same-basename images stay distinct | unit | `uv run pytest tests/test_builder.py -x` | ✅ file exists (Phase 50 cluster at `:392-660`), ❌ specific test needs adding |

### Sampling Rate
- **Per task commit:** the file-scoped quick command above for the file(s) that task touches.
- **Per wave merge:** full suite (`uv run pytest`) plus `black --check .`, `ruff check .`,
  `mypy typsphinx/` — per `STATE.md`'s own recorded lesson from Phase 54.1 ("Run `black --check .`,
  `ruff check .` and `mypy` at every post-merge gate, not just pytest" — a CI-only defect class
  otherwise escapes local gates).
- **Phase gate:** Full suite green (unconditional zero failures, per Pitfall 5 above) before
  `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] A new fixture directory for BLD-07's real-compile RED (docname containing `#`, modeled on
      `tests/fixtures/state_guard_substring_key_gate/`'s shape).
- [ ] BLD-08's synthesized-deep-chain test class inside `tests/test_include_edge_derivation_unit.py`
      (no new file — existing module, existing pattern).
- [ ] BLD-09's driveless-absolute-URI test inside `tests/test_builder.py` (add a case; do not revert
      the Phase 52-09 drive-qualified fixture per Claude's Discretion).
- [ ] IMG-03's two-same-basename-different-directory test inside `tests/test_builder.py`, beside the
      Phase 50 relocation cluster.
- [ ] XREF-05 needs no new fixture — the existing `xref_label_collision_guard_gate` fixture and its
      already-passing characterization test ARE the RED evidence (D-04); only the fixture's
      `conf.py` comment block and the test's assertion direction change.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Not applicable — build-time document processing, no auth surface |
| V3 Session Management | No | Not applicable |
| V4 Access Control | No | Not applicable |
| V5 Input Validation | Marginal — yes | Docname/URI strings originate from the user's own Sphinx project (trusted input, not attacker-controlled network input); the "validation" here is Typst-syntax-safety (label alphabet) and path-containment (outdir escape), both already-established project patterns (`_sanitize_label`, `_escapes_outdir`) this phase extends rather than introduces |
| V6 Cryptography | No | `hashlib.sha1` in IMG-03 is used as a NON-cryptographic collision-avoidance key over a build-local path string, not for any security property (integrity, authentication, secrecy) — no cryptographic requirement applies |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via a crafted `typst_documents`/image URI escaping `outdir` | Tampering | Already-established `_escapes_outdir()` predicate (unchanged by this phase); BLD-09/IMG-03 extend the SAME containment discipline to a branch that had a platform-specific gap, they do not weaken it |
| Denial of service via unbounded recursion (a maliciously or accidentally deep toctree) | Denial of Service | BLD-08's fix directly closes this — a bounded, named failure instead of an uncaught stack-exhaustion crash |
| Label/key collision leading to silent wrong-content substitution (XREF-05, BLD-07, IMG-03) | Tampering (data integrity — wrong content silently substituted, not attacker-triggered in the threat-modeling sense but a correctness/integrity class) | Injective key/label construction (this phase's core fix for all three) |

This phase's fixes are all internal build-time correctness/robustness improvements over inputs the
project's own trust model already treats as trusted (a Sphinx project's own source tree, authored by
the person invoking the build) — there is no new external attack surface introduced or closed by this
phase beyond the DoS-shaped `RecursionError` hardening (BLD-08), which the fix improves regardless of
threat-actor framing (a legitimately huge doc tree hits the same crash today).

## Sources

### Primary (HIGH confidence — direct source reads this session)
- `typsphinx/translator.py` (lines 1-30, 135-380, 925-955, 3470-3560, 5010-5130) — every function
  this phase's five fixes touch or reference, read directly this session.
- `typsphinx/builder.py` (lines 1-30, 80-165, 440-470, 1495-1620) — `_is_drive_qualified`,
  `_escapes_outdir`, `_build_include_edge_map`, `_track_image`, all imports.
- `tests/test_xref_compile_time_guard_render_gate.py` (lines 1-80, 180-359) — the characterization
  test D-04 inverts, and the per-master guard fixture pattern.
- `tests/test_include_edge_derivation_unit.py` (full file, 438 lines) — the unit-test harness shape
  for BLD-07's/BLD-08's REDs.
- `tests/test_builder.py` (lines 380-660) — the Phase 50 relocation test cluster IMG-03's/BLD-09's
  REDs sit beside, including the two tests IMG-03's fix will regress if not updated.
- `pyproject.toml` (lines 79-99) — pytest configuration.
- `.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`
  — XREF-05's full root-cause and rejected-remedy discussion.
- `.planning/todos/pending/2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide.md`
  — BLD-07's full root-cause, three candidate repairs (this document picks the escaping option).
- `.planning/todos/pending/2026-08-14-unbounded-recursion-in-derive-master-edge-keys.md` — BLD-08's
  full root-cause and two candidate repairs (this document picks the depth-guard option, per
  Claude's Discretion).
- `.planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md` —
  BLD-09's full measurement (CI log, CPython source cross-reference) and candidate repair.
- `.planning/todos/pending/2026-08-14-escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide.md`
  — IMG-03's full root-cause, the hashed-key escape hatch (T-50-03), and disposition history.
- `.planning/phases/55-v0-8-0-derived-defects/55-CONTEXT.md` — this phase's locked decisions,
  discretion recommendations, and canonical reference list.
- `.planning/REQUIREMENTS.md` — the five requirement definitions and traceability table.
- `.planning/STATE.md` (lines 1-604) — project history, the stale-carve-out correction (Pitfall 5),
  and the black/ruff/mypy-at-every-gate lesson.
- Direct interpreter session, Python 3.13.13, `ntpath.isabs()` behavior — reproduced this session,
  matching the todo's own claim exactly.

### Secondary (MEDIUM confidence)
- None — this phase required no external documentation lookups; all facts were verifiable directly
  against the project's own source and test tree, plus its own pending todos, which themselves carry
  primary measurements (CI logs, direct interpreter probes) from prior sessions.

### Tertiary (LOW confidence)
- The four "candidate construction" code snippets under Architecture Patterns 1, 2, 3, and 5 —
  explicitly marked `[ASSUMED]` throughout; these are this session's own proposed implementations,
  not verified against a real `typst.compile()` or exercised against the actual codebase, offered so
  the planner has a concrete starting point rather than an open-ended design question.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries; every symbol referenced (`hashlib`, `ExtensionError`,
  `posixpath`, `_is_drive_qualified`) verified present or absent in the current tree this session.
- Architecture: HIGH — every fix site read directly from source this session with line numbers
  reconfirmed (and one stale line-number discrepancy from the phase description caught and flagged).
- Pitfalls: HIGH for Pitfalls 1, 2, 4, 5 (all directly measured/derived this session); MEDIUM for
  Pitfall 3 (XREF-05's construction is a proposal, not a verified fix).
- Candidate fix constructions (Patterns 1, 2, 3, 5): LOW-MEDIUM — logically reasoned and
  internally consistent with CONTEXT.md's locked constraints, but NOT verified against a real Typst
  compile or exercised against the actual code this session; each is explicitly flagged `[ASSUMED]`
  and the phase's own D-05 RED-first discipline is the intended safety net.

**Research date:** 2026-08-16
**Valid until:** Stable — this is internal-codebase research with no external dependency-freshness
concern; the only source of staleness risk is further line-number drift if earlier waves within THIS
phase touch `translator.py`/`builder.py` before later waves execute (see Pitfall 1). Re-verify exact
line numbers at execution time regardless of research age.
