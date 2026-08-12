# Phase 48: Compile-Time Cross-Reference Guard - Pattern Map

**Mapped:** 2026-08-12
**Files analyzed:** 7 (2 modified source modules, 5 test/fixture areas — this phase is
overwhelmingly a MODIFY-in-place phase per CONTEXT.md; the only genuinely NEW files are two
test fixtures + two evidence artifacts)
**Analogs found:** 7 / 7

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` (new shared guard helper) | utility (translator private method) | transform (string-in/tuple-out) | `_reference_anchor_decision()` (`translator.py:3011-3103`), `_namespace_label()` (`translator.py:4579-4620`) | exact — same class, same "one shared derivation point" house style |
| `typsphinx/translator.py` (`visit_reference` cross-doc branch, `:4985-5007`) | controller (node visitor) | streaming (visit opens, depart via later code closes) | itself (in-place modify); sibling same-doc branches at `:4941-4950`/`:4980-4984` for prefix-computation style | exact |
| `typsphinx/translator.py` (`visit_citation` backref loop, `:3267-3284`) | controller (node visitor, buffer-swap idiom) | transform (value expression, not streaming) | itself (in-place modify); `label_expr` string-concat pattern already present | exact |
| `typsphinx/translator.py` (`visit_pending_xref`/`depart_pending_xref`, `:4262-4303`) | controller (node visitor pair) | streaming (visit opens `#link(<L>)[`, depart closes `]`) | `visit_reference`'s `#"` prefix computation (`prefix = "#" if self._in_markup_mode else ""`, `:4977`) — the site currently lacks this and hardcodes `#` | role-match (site itself is the analog for shape; `visit_reference` is the analog for the `prefix` pattern it currently lacks) |
| `typsphinx/builder.py` (deletions: `_compute_master_included_docnames()`, `master_included_docnames` attr, `init()` doc-comment, `write()` call site) | service (builder state) | CRUD (pure deletion) | `_is_usable_typst_documents_entry()` (`builder.py:106-164`) — the surviving predicate whose docstring's consumer-count (5→4) must be corrected in the same change | exact (this is the "fifth consumer" being removed) |
| `tests/fixtures/<new two-master SC#1 fixture>/` | test fixture (conf.py + rst) | request-response (sphinx-build → typst.compile → pypdf) | `tests/fixtures/bld03_ghost_entry_xref_gate/` (closest two-entry-`typst_documents` + xref shape); `tests/fixtures/two_layer_root_master_gate/` (closest clean two-layer single-master shape, for the load-bearing-comment convention) | role-match |
| `tests/test_pdf_render_gate.py::TestXrefRefidRenderGate` (or new class) | test (integration, real-compile) | request-response (subprocess + typst.compile + pypdf) | `TestXrefRefidRenderGate` (`:742-825`) for `.typ`-source + PDF-text assertions; `tests/test_citation_render_gate.py`'s `_link_rect_x0_values()` (`:473-486`) for real `/Link` annotation readback via `/Annots` | exact |

## Pattern Assignments

### 1. The new shared guard helper (Claude's Discretion: name/location; D-07 contract)

**Analogs:** `_reference_anchor_decision()` (`typsphinx/translator.py:3011-3103`) and
`_namespace_label()` (`typsphinx/translator.py:4579-4620`) — both are private `TypstTranslator`
methods that are the SINGLE derivation point for a judgement multiple call sites must not
re-derive independently. The new helper must match this house style: NamedTuple-typed return
(if returning more than 2 items — D-07 fixes it at exactly `(open_str, close_str)` so a plain
2-tuple or a tiny NamedTuple both fit house style), a long docstring explaining WHY a shared
point exists (citing which sites call it and what silently drifting apart looked like before),
and a "SILENT by contract" note if applicable.

**Declaration style to imitate** (`translator.py:3011-3017`):
```python
def _reference_anchor_decision(
    self, node: nodes.reference
) -> _ReferenceAnchorDecision:
    """
    The SINGLE D-14 citing-site anchor judgement (WR-03, D-05/D-06/
    D-07, `40.1-CONTEXT.md`): does ``node`` get its own
    bracket-attached anchor, and if so what is that anchor's label?
    ...
```

**Docstring convention for "why one shared point"** (`translator.py:3019-3027`, paraphrase
target): explicitly names the sites that will drift apart if the derivation is duplicated —
for the new helper this must name `visit_reference`, `visit_citation`'s backref loop, and
`visit_pending_xref`/`depart_pending_xref` by name, mirroring how `_reference_anchor_decision`'s
docstring names its own two consumers.

**"Never a second spelling" convention** (`translator.py:4590-4600`, `_namespace_label`
docstring) — the new helper must likewise be positioned as the ONE place the `context`/`query`
Typst syntax is spelled, with a note that any site building its own `context { ... }` string is
the exact class of drift this phase's own D-07 rejects (see Anti-Patterns in RESEARCH.md: "A
boolean-only guard helper... was rejected").

**Return-type shape (D-07):** a plain 2-tuple `(open_str, close_str)` or a 2-field `NamedTuple`
— `_ReferenceAnchorDecision` (`translator.py:33-102`) is the house NamedTuple precedent if a
named-field return is preferred over a bare tuple:
```python
class _ReferenceAnchorDecision(NamedTuple):
    refuri: str
    refid: str
    xref: Tuple[str, str] | None
    degrade_xref_to_text: bool
    opens_wrapper: bool
    next_is_target: bool
    eligible: bool
    anchor_label: str | None
```

**Label derivation — MUST route through `_namespace_label`, never re-derive:**
```python
# translator.py:4579
def _namespace_label(self, docname: str | None, raw_id: str) -> str:
    """Namespace a docutils id/name by its owning document, then sanitize.
    ...
```
Every guarded site's label argument to the new helper must be a label ALREADY computed via
`_namespace_label` (as `visit_reference`'s existing branches already do at `:4949`, `:4983`,
`:5006`) — the guard helper's OWN job (per D-07) is only to wrap that already-namespaced label
in the `context`/`query`/`link`/`else` shape, not to compute labels itself.

**The corrected D-08 Typst shape the helper must emit** (RESEARCH.md Pattern 1, verified this
session against typst-py 0.15.0 — do NOT reproduce the CONTEXT.md sketch's line break before
the `if`'s `{`, see Pitfall 1):
```typst
open_str  = "{prefix}context { let __b = ["
close_str = "]; if query(<the-label>).len() > 0 { link(<the-label>, __b) } else { __b } }"
```
`{prefix}` is the SAME `"#" if self._in_markup_mode else ""` computation `visit_reference`
already performs at `translator.py:4977` — the helper (or its caller) must apply it identically
at all three sites, including `visit_pending_xref`, which currently hardcodes `#` unconditionally
(see item 2c below).

**Unit-testing convention to imitate:** `_reference_anchor_decision` is directly unit-tested
(not only through end-to-end compiles) in `tests/test_citation_degradation_gate.py`'s
`TestWr03EligibilityDecisionAgreesWithEmission` (`:1039-1107`) — a `@pytest.mark.parametrize`
table of hand-built doctree cases, each asserting the method's return value directly. The new
guard helper should get an equivalent direct-unit-test class asserting on `(open_str,
close_str)` content (e.g. "close_str contains `query(<label>)`", "open_str ends with `let __b =
[`"), separate from the real-compile acceptance gate.

---

### 2. The three emission sites (CURRENT code, streaming vs. value-expression shape)

#### 2a. `visit_reference`'s resolved cross-document branch — STREAMING (`translator.py:4985-5007`)

Current code (the primary XREF-03 site, to be modified):
```python
elif xref is not None:
    # Resolved CROSS-document reference (`<relpath><out_suffix>#anchor`).
    if degrade_xref_to_text:
        # Target document is NOT part of the compiled master (orphan /
        # excluded from every toctree). ...
        logger.warning(
            f"cross-reference to non-included document '{xref[0]}' "
            f"rendered as plain text (typstpdf includes only "
            f"toctree-reachable documents): {node.astext()}"
        )
        self._skip_link_wrapper = True
        return
    # In the flattened master this must become a real label link, not a
    # dead string url: namespace with the TARGET docname so it byte-
    # matches the anchor the target document emitted.
    target_docname, anchor = xref
    label = self._namespace_label(target_docname, anchor)
    self.add_text(f"{prefix}link(<{label}>, ")
```
Shape: STREAMING — `visit_reference` opens with `self.add_text(f"{prefix}link(<{label}>, ")`,
children stream via the normal walker, and `depart_reference` (not shown above, elsewhere in the
same method family) closes with `")"` / `"]"` as appropriate. Post-fix, this becomes
unconditional (D-01/D-09 delete the `degrade_xref_to_text` branch and its `logger.warning`
entirely — no diagnostic replacement): the guard helper's `open_str` replaces the
`f"{prefix}link(<{label}>, "` text, and its `close_str` must be emitted at the corresponding
`depart_reference` point instead of the plain closer used today.

#### 2b. `visit_citation`'s back-reference loop — VALUE EXPRESSION, not streaming (`translator.py:3267-3284`)

Current code (the one buffer-swapping site — body already fully computed as Python strings
before any `add_text()` call):
```python
decision = self._reference_anchor_decision(ref_node)
if not decision.eligible:
    continue
backref_targets.append(decision.anchor_label)

if len(backref_targets) == 1:
    label_body = f"link(<{backref_targets[0]}>, {label_content})"
else:
    label_body = label_content

label_expr = f'text("[") + {label_body} + text("]")'

if len(backref_targets) >= 2:
    markers = ",".join(
        f"link(<{target}>, [{i}])"
        for i, target in enumerate(backref_targets, start=1)
    )
    label_expr += f' + text(" (") + ({markers}).join(",") + text(")")'
```
Shape: per RESEARCH.md Pitfall 3, this site does NOT stream — `label_body`/`label_expr` are
fully computed Python strings before any `add_text()` call, so D-07's helper is consumed as a
**value expression**: `open_str + label_content_or_marker_body + close_str` concatenated
directly into the `label_body`/`markers` string, exactly the way RESEARCH.md's verified example
does:
```typst
text("[") + context { if query(<cite-target>).len() > 0 { link(<cite-target>, [1]) } else { [1] } } + text("]")
```
No outer parentheses are required (verified). D-05 requires EVERY `backref_targets.append(...)`
site here to route through the guard, not only the single-target `label_body` line — including
the `markers` comprehension's `link(<{target}>, [{i}])` calls, since each is an independent
guarded reference to a (possibly citing-caption-pruned, per Pitfall 5) anchor.

#### 2c. `visit_pending_xref`/`depart_pending_xref` — STREAMING, but currently prefix-less (`translator.py:4262-4303`)

Current code (the fourth independent degradation site, D-04):
```python
def visit_pending_xref(self, node: nodes.Node) -> None:
    reftarget = node.get("reftarget", "")
    reftype = node.get("reftype", "")

    if reftarget:
        label = self._namespace_label(
            self._current_docname(),
            reftarget.replace(".", "-").replace("_", "-"),
        )
        self.add_text(f"#link(<{label}>)[")
    # Continue processing children to get the link text

def depart_pending_xref(self, node: nodes.Node) -> None:
    reftarget = node.get("reftarget", "")
    if reftarget:
        self.add_text("]")
```
Shape: STREAMING — `visit_*` opens `#link(<label>)[`, children stream, `depart_*` closes `]`.
Note it hardcodes `#` with NO `prefix` variable, unlike `visit_reference`'s
`prefix = "#" if self._in_markup_mode else ""` (`:4977`) — RESEARCH.md flags this as a
"verify at implementation, do not fix speculatively" item, moot if D-04's unconstructible-RED
conclusion holds. Guard it defensively per D-04's own instruction ("brought under the guard, not
merely rewired") even though no real-build RED could be constructed this session (Pitfall 4 —
Sphinx's `ReferencesResolver` post-transform replaces every `pending_xref` before the writer
runs unconditionally).

---

### 3. Same-document branches that MUST stay UNGUARDED (D-06 negative assertion)

`translator.py:4941-4950` (bare-refid same-document target):
```python
if not refuri and refid:
    prefix = "#" if self._in_markup_mode else ""
    label = self._namespace_label(self._current_docname(), refid)
    self.add_text(f"{prefix}link(<{label}>, ")
    ...
    return
```

`translator.py:4980-4984` (`#`-prefixed internal refuri, same-document):
```python
if refuri.startswith("#"):
    label = self._namespace_label(self._current_docname(), refuri[1:])
    self.add_text(f"{prefix}link(<{label}>, ")
```

**Planner note:** these two branches emit the plain `f"{prefix}link(<{label}>, "` form
UNCHANGED — per SC#4/D-06, same-document anchors are always present because content files are
included wholesale, so no guard is needed. A plan touching `visit_reference` must add an
explicit test/assertion (or at minimum a code comment) that these two branches were NOT routed
through the new guard helper, to prevent an executor over-applying the guard everywhere it
touches `visit_reference`.

---

### 4. The deletions (grep-zero targets)

**`builder.py:240-330` (approx.) — attribute + method + doc-comment, full deletion:**

Attribute declaration and its surrounding doc-comment (`builder.py:240-255`, inside `init()`):
```python
        # The SET of docnames whose .typ is physically part of the compiled
        # master (each master in typst_documents plus the transitive toctree
        # closure reachable from it). ...
        self.master_included_docnames: set[str] = set()
```

Method (`builder.py:257-322`):
```python
    def _compute_master_included_docnames(self) -> set[str]:
        """Compute the transitive toctree closure of the master document(s).
        ...
        """
        typst_documents = getattr(self.config, "typst_documents", []) or []
        masters = [
            entry[0]
            for entry in typst_documents
            if _is_usable_typst_documents_entry(entry)
        ]
        toctree_includes = getattr(self.env, "toctree_includes", {}) or {}

        included: set[str] = set()
        stack = list(masters)
        while stack:
            docname = stack.pop()
            if docname in included:
                continue
            included.add(docname)
            for child in toctree_includes.get(docname, []):
                if child not in included:
                    stack.append(child)
        return included
```

**`builder.py:758` — the `write()` call site, full deletion:**
```python
        # Compute the master include-set NOW (the read phase is complete, so
        # env.toctree_includes is fully populated) rather than lazily during
        # visit_toctree: ...
        self.master_included_docnames = self._compute_master_included_docnames()
```

**`_is_usable_typst_documents_entry()`'s docstring — consumer count correction (D-10):**
`builder.py:106-164` currently says "FIVE sites" (`:111-116`) and explicitly names
`_compute_master_included_docnames()` as "this fifth consumer" (`:116-124`); after deletion this
must read "FOUR" and drop the named fifth-consumer paragraph — do not leave a stale "five"/"fifth"
reference anywhere in that docstring.

**Every read site of `master_included_docnames` that must go to zero (`grep -rn
master_included_docnames typsphinx/` must return nothing after this phase):**
- `typsphinx/translator.py:3073-3075` (inside `_reference_anchor_decision`, the
  `degrade_xref_to_text` computation — deleted along with the field itself, D-09)
- `typsphinx/builder.py:246` (comment prose, "via builder.master_included_docnames" — the
  whole comment block needs rewriting, not just the code line, since it currently documents the
  now-false claim that the translator "consults this set")
- `typsphinx/builder.py:255` (attribute declaration)
- `typsphinx/builder.py:257` (method name/definition)
- `typsphinx/builder.py:758` (write() call site)

**`_ReferenceAnchorDecision.degrade_xref_to_text` field — deletion (D-09):**
`translator.py:33-102`'s NamedTuple loses the `degrade_xref_to_text: bool` field (`:98`) and its
docstring paragraph (`:59-64`); `translator.py:3071-3077`'s computation
(`degrade_xref_to_text = False` / `if xref is not None: master_included = getattr(...)`/
`opens_wrapper = bool(refuri or refid) and not degrade_xref_to_text`) collapses to
`opens_wrapper = bool(refuri or refid)` unconditionally per D-09.

---

### 5. Test analogs

#### 5a. `tests/test_pdf_render_gate.py` — the `sphinx-build → typst.compile() → pypdf` fixture pattern

**Fixture layout convention** (`test_pdf_render_gate.py:132-191`):
```python
@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def xref_refid_render_gate_dir(fixtures_dir):
    ...  # one such fixture-dir accessor per fixture project

@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"

def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst",
         *extra_args, str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )
```
Invoked as `sys.executable -m sphinx`, NEVER `["uv", "run", "sphinx-build", ...]` — see the long
comment at `:157-171` explaining why (a NixOS/`.venv/bin` PATH hazard, now moot since QUA-04, but
the pattern is kept regardless because it depends on no PATH resolution at all).

**Real-compile + link-annotation assertion pattern** — combine `TestXrefRefidRenderGate`
(`:742-825`, `.typ`-source + PDF-text assertions) with `_link_rect_x0_values()` from
`tests/test_citation_render_gate.py:473-486` (real `/Link` annotation readback):
```python
def _link_rect_x0_values(pdf_bytes: bytes, page_index: int) -> list[float]:
    """Return the left-edge (``/Rect`` x0) of every ``/Link`` annotation on
    the given page."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    page = reader.pages[page_index]
    annots = page.get("/Annots") or []
    values = []
    for annot in annots:
        obj = annot.get_object()
        if obj.get("/Subtype") == "/Link":
            rect = obj.get("/Rect")
            if rect:
                values.append(float(rect[0]))
    return values
```
For SC#1 the assertion shape needed is COUNT-based, not position-based: assert `len(annots
filtered to /Subtype == "/Link")` is `>= 1` for the master that includes the target document,
and `== 0` for the master that does not (no `TypstError` in either compile) — this is a simpler
consumer of the same `/Annots` readback idiom than `_link_rect_x0_values`'s x0-comparison use
case.

**Pytest markers convention:** every GATE-01-class real-compile test class carries
```python
@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class Test...RenderGate:
```
(`test_pdf_render_gate.py:393-398`, `:737-742`, etc.) — the `not (TYPST_AVAILABLE and
PYPDF_AVAILABLE)` skip reason string is copy-pasted verbatim across every such class; SC#1's new
class must use the same two module-level booleans (`test_pdf_render_gate.py:29-40`) rather than
re-deriving its own import-guard.

#### 5b. Closest two-master fixture shape for SC#1 (one master includes the target, one does not)

`tests/fixtures/bld03_ghost_entry_xref_gate/` (`conf.py`, full text):
```python
typst_documents = [
    ("index", "manual.typ", "Real Master", "Probe Author"),
    ("ghost",),
]
```
This is the closest EXISTING two-`typst_documents`-entry fixture with a real cross-reference
into a document one entry includes and the other structurally cannot (`ghost`'s entry is
under-length and produces no wrapper at all, rather than being a second WELL-FORMED master that
simply omits the target from its own toctree) — SC#1 needs a NEW fixture with two well-formed
4-tuple entries (two real masters, each producing a wrapper), one whose toctree includes the
target document and one whose does not, closer in spirit to
`tests/fixtures/two_layer_root_master_gate/`'s clean single-target-per-entry shape than to
`bld03_ghost_entry_xref_gate`'s malformed-entry shape. Use `bld03_ghost_entry_xref_gate` for its
`:ref:`-into-a-conditionally-included-document CONTENT shape, and
`two_layer_root_master_gate`/`two_layer_nested_master_gate` for the "two well-formed
`typst_documents` entries, each a real compiling master" structural shape.

#### 5c. "Load-bearing properties" `conf.py` comment-block convention (quoted verbatim)

From `tests/fixtures/bld03_ghost_entry_xref_gate/conf.py:11-25`:
```python
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the fifth-site gap:
#   - The SECOND entry MUST stay a 1-tuple naming a REAL docname (`ghost`)
#     -- making it well-formed removes the under-length shape and collapses
#     this fixture into the already-green `bld03_under_length_entry_gate`.
#   - `ghost.rst` MUST keep BOTH its `:orphan:` field AND its `toctree`
#     directive -- the toctree is the only thing that pulls `ghost_child`
#     into the pre-fix include closure, and without `:orphan:` the fixture
#     emits an unrelated "not included in any toctree" consistency warning
#     that muddies the transcript.
#   - `index.rst` MUST keep its `:ref:` into `ghost_child`'s label -- that
#     reference IS the defect.
#   - The FIRST entry MUST stay a well-formed 4-tuple whose target basename
#     (`manual.typ`) differs from its docname (`index`), so `manual.pdf`
#     proves the well-formed sibling master still compiles.
```
Any new SC#1 fixture must carry an equivalent block naming exactly which property (the second
master's toctree omission of the target document; the shared content file's single write) would
silently stop the fixture exercising the per-master-divergence defect if touched.

#### 5d. `xfail(strict=True)` pre-fix RED convention + `47-EXPECTED-STRUCTURE.md` shape

`tests/test_master_include_set_predicate_gate.py:1-31` module docstring (the convention to
imitate, paraphrase target for the new XREF-03 RED):
```python
"""
...
Structured like ``tests/test_collision_predicate_completeness_gate.py`` (one
fixture-directory constant per scenario, one ``_run_sphinx_build`` helper
duplicated per this repo's own convention) but recording the pre-fix RED as
``xfail(strict=True)``: six of the eight tests below fail on the unfixed
tree; two are invariance guards that already pass and must keep passing. The
verbatim pre-fix transcripts each xfail's ``reason=`` paraphrases are
recorded in full in ``47-GAP2-RED-EVIDENCE.md``.
"""
```
`47-EXPECTED-STRUCTURE.md` shape (write-expected-values-first artifact, D-03's own precedent) —
per-fixture sections with an explicit "Derivation arithmetic" paragraph computed from `conf.py`/
`.rst` alone, e.g.:
```markdown
## Fixture 1: `two_layer_root_master_gate`

**Source read literally:** `conf.py` -- one docname `index` ...

### Expected (GREEN, post-fix) emitted-file table
| Logical role | Outdir-relative path | Template applied? | `#include()` argument (wrappers only) |
|---|---|---|---|
| Content (docname `index`) | `index.typ` | No (D-06 preamble only) | n/a |
| Wrapper (entry `index`→`manual.typ`) | `manual.typ` | Yes | `"index.typ"` |

**Derivation arithmetic:** the target `"manual.typ"` carries no path separator, so per OUT-01
it resolves at the output root ...
```
For this phase, the equivalent artifact is the NEW expected value for
`TestBld03GhostEntryXref::test_ghost_entry_subtree_xref_degrades_typst` (line 103 of
`tests/test_master_include_set_predicate_gate.py`) — must state, BEFORE the new emitter runs,
that the `.typ` source now contains a guarded `context { let __b = [...]; if
query(<label>).len() > 0 { link(...) } else { __b } }` expression rather than plain degraded
text, derived purely from reading the guard contract (D-07/D-08) against the fixture's own
`:ref:` target, never from running the new emitter first.

`47-GAP2-RED-EVIDENCE.md` shape (`:1-30`) — a verbatim `sphinx-build` transcript block per
failure mode, headed by exact reproduction commands and provenance (worktree isolation
confirmation), e.g.:
```markdown
## Failure mode 1 -- ghost entry's phantom-included subtree, silent dangling label

**Fixture:** `tests/fixtures/bld03_ghost_entry_xref_gate/` -- ...

### `-b typst`
**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld03_ghost_entry_xref_gate /tmp/red2-d`
**Raw output:**
```
...verbatim transcript...
```
```
This phase's D-05 citation-in-caption reproduction (RESEARCH.md's own transcript, `TypstError:
label <index:id1> does not exist in the document`) should become a `*-RED-EVIDENCE.md` section in
this same shape, per binding constraint #4.

#### 5e. `tests/test_citation_degradation_gate.py`'s `_StubBuilder` — every attribute must lose `master_included_docnames`

`tests/test_citation_degradation_gate.py:593-618` (full class, current state):
```python
class _StubBuilder:
    """
    A locally-scoped stub builder for the assembled-doctree harness, NOT
    imported from ``tests/conftest.py``'s ``mock_builder`` and NOT from the
    frozen ``tests/test_citation_render_gate.py`` module (D-02).

    Shaped on ``conftest.py``'s ``mock_builder`` (nested ``MockConfig``/
    ``MockDomains``/``MockEnv``) plus four extra attributes that fixture's
    ``mock_builder`` lacks and the D-06/D-08 xref-resolution routes need:
    ``out_suffix``, ``current_docname``, ``master_included_docnames``
    (deliberately excluding ``"second"`` -- plan ``40.1-03`` depends on that
    exclusion to exercise the ``degrade_xref_to_text`` route), and
    ``get_target_uri``. ...
    """

    config = _MockConfig()
    env = _MockEnv()
    out_suffix = ".typ"
    current_docname = "index"
    master_included_docnames = {"index"}

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return docname + self.out_suffix
```
Every test case in this file that constructs a doctree via `_wr03_case_refuri_excluded_document`
(`:1007-1021`) relies on `_StubBuilder.master_included_docnames = {"index"}` EXCLUDING
`"second"` to exercise the (now-deleted) `degrade_xref_to_text` route. After this phase:
- The `master_included_docnames = {"index"}` class attribute is deleted from `_StubBuilder`.
- The docstring's "``master_included_docnames`` (deliberately excluding `"second"`...)" clause
  is deleted along with it.
- `_wr03_case_refuri_excluded_document` (case iii, `:1007-1021`) and its parametrized assertion
  at `:1056` (`("refuri_excluded_document", _wr03_case_refuri_excluded_document, False)`) flip
  their `expected_eligible` from `False` to `True` per D-09 (`opens_wrapper` becomes
  unconditional), written down BEFORE the new emitter runs per D-03.
- `TestWr03XrefResolutionAndWarningFireOnce`'s `_build_cross_doc_reference_doctree` (`:1119-1129`)
  docstring's "degrades to plain text" claim, keyed to the same excluded-`"second"` stub state,
  also needs its expected behaviour re-derived (the warning it tests for firing "exactly once"
  no longer exists at all, per D-01 — this whole test class's premise may need re-scoping to the
  guard's own compile-time non-warning behaviour instead).

## Shared Patterns

### Guard helper docstring / "single derivation point" convention
**Source:** `typsphinx/translator.py:3011-3103` (`_reference_anchor_decision`),
`typsphinx/translator.py:4579-4620` (`_namespace_label`)
**Apply to:** the new D-07 guard helper
Both existing helpers open their docstring by naming exactly which sites would silently drift
apart without the shared point, and close with an explicit "never a second spelling" warning.
The new helper's docstring must do the same, naming `visit_reference`, `visit_citation`, and
`visit_pending_xref`/`depart_pending_xref` explicitly.

### Real-compile GATE-01 acceptance-test scaffold
**Source:** `tests/test_pdf_render_gate.py:132-266` (fixtures + `_run_sphinx_build_typst` +
class-scoped compile-once fixture pattern), `tests/test_citation_render_gate.py:473-486`
(`/Annots` readback)
**Apply to:** SC#1's new render-gate test class
Every GATE-01-class test compiles via `sys.executable -m sphinx` subprocess +
`typst.compile()` (never mocked), reads back via `pypdf.PdfReader`, and is gated behind
`@pytest.mark.slow` + `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)`.

### Load-bearing-properties fixture comment block
**Source:** `tests/fixtures/bld03_ghost_entry_xref_gate/conf.py:11-25`
**Apply to:** any new fixture this phase adds
Every fixture `conf.py` for a defect-reproduction scenario names, in a bulleted comment block,
exactly which property would silently stop the fixture exercising its defect if changed.

### `xfail(strict=True)` pre-fix RED + standalone RED-EVIDENCE.md transcript
**Source:** `tests/test_master_include_set_predicate_gate.py:1-31` (module docstring convention),
`.planning/phases/47-.../47-GAP2-RED-EVIDENCE.md` (transcript artifact shape)
**Apply to:** D-04's (if constructible) and D-05's pre-fix REDs, and XREF-03's flipped assertion
Binding constraint #4/#6 compliance: every pre-fix RED is either an `xfail(strict=True)` with a
`reason=` paraphrasing a transcript recorded in full in a sibling `*-RED-EVIDENCE.md`, or (D-03)
an expected-value table derived from `conf.py`/`.rst` alone, written before the new emitter runs
— mirroring `47-EXPECTED-STRUCTURE.md`'s "Derivation arithmetic" paragraph shape.

## No Analog Found

None — every file/change this phase touches has a strong same-repo analog; RESEARCH.md's own
direct `typst.compile()` verification stands in for "analog" on the pure-Typst-syntax question
(D-08), which has no Python-side codebase precedent to copy from.

## Metadata

**Analog search scope:** `typsphinx/translator.py`, `typsphinx/builder.py`,
`tests/test_pdf_render_gate.py`, `tests/test_citation_render_gate.py`,
`tests/test_citation_degradation_gate.py`, `tests/test_master_include_set_predicate_gate.py`,
`tests/fixtures/bld03_ghost_entry_xref_gate/`, `tests/fixtures/two_layer_root_master_gate/`,
`tests/fixtures/two_layer_nested_master_gate/`,
`.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/` artifacts.
**Files scanned:** 2 source modules read in full at the cited line ranges; 5 test files read at
targeted ranges; 3 fixture directories inspected; 2 Phase 47 artifacts read in full.
**Pattern extraction date:** 2026-08-12
