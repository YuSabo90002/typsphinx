# Phase 48 Plan 01 — Expected Post-Fix Structure

**Written:** 2026-08-12
**No builder was run to produce this document.** Every expected value below is derived from three
inputs only: each fixture's `conf.py`/`.rst` read literally, the D-07/D-08 guard contract as
corrected by `48-RESEARCH.md`, and `48-EVIDENCE.md`'s `## Body-mode measurement` (Step 0's real
`typst.compile()` probes, run BEFORE this document was written). Binding constraint #6 forbids
deriving these values by reading the new emitter's output — `git status --porcelain typsphinx/`
prints nothing throughout this task.

---

## Guard contract

The single D-07 shared guard-string derivation point:

```python
class _LabelGuardStrings(NamedTuple):
    open_str: str
    close_str: str


def _label_existence_guard(
    self, label: str, *, prefix: str = "", code_mode_body: bool = False
) -> _LabelGuardStrings:
    ...
```

- The bound identifier the guard's `let` statement introduces is **`__tsx_body`** (fixed by this
  plan so all four Phase 48 plans and all three call sites agree — Claude's Discretion in
  `48-CONTEXT.md` left the exact spelling unfixed; `__b`/illustrative names elsewhere in
  `PROJECT.md`/`48-RESEARCH.md` are NOT the bound identifier this codebase uses).
- **`code_mode_body=True` is the spelling ADOPTED by `48-EVIDENCE.md`'s Body-mode measurement**
  (Step 0, all five probe cases compiled clean in both target-present and target-absent
  configurations) — this is the form used at all three of this phase's D-07 sites, since every
  site's children already stream in code mode today. When `code_mode_body` is `True`: `open_str`
  ends with `= [#{` and `close_str` begins with `}];`. (The `code_mode_body=False` bare-`[`
  spelling — `open_str` ending `= [`, `close_str` beginning `];` — is kept as the helper's other
  branch for any FUTURE caller whose children already stream in markup mode; no site in this phase
  uses it.)
- `close_str`'s conditional is **one unbroken statement** — the `if query(<L>).len() > 0` condition
  and its opening `{` are never separated by a newline in the emitted bytes (Typst's parser
  requires them on one unbroken statement; a newline there is a hard `expected block` parse error,
  `48-RESEARCH.md` Common Pitfalls Pitfall 1). The illustrative line break in `48-CONTEXT.md`'s
  `<specifics>` sketch is the shape that does NOT compile and must never appear in emitted output.
- **Own-anchor composition:** when the caller has also opened the `_reference_own_anchor`
  bracket-wrap (`visit_reference`'s D-14 own-ids anchor — `self.add_text("[")` +
  `self._in_markup_mode = True`), the `#label("…")]` closing pair lands AFTER `close_str`, OUTSIDE
  the `context { … }` block — measured and confirmed compiling in `48-EVIDENCE.md` Probes 4/5 (the
  query for the own anchor found it in BOTH the target-present and target-absent configurations,
  proving the anchor attaches independently of whether the guard's own cross-document query
  succeeds).

**Fully substituted example** for label `target:guarded-target-section` (`code_mode_body=True`,
`prefix=""`):

```
open_str:  context { let __tsx_body = [#{
close_str: }]; if query(<target:guarded-target-section>).len() > 0 { link(<target:guarded-target-section>, __tsx_body) } else { __tsx_body } }
```

Both strings on effectively one line each; the whole `close_str` above is byte-for-byte on ONE
line, with `if query(<target:guarded-target-section>).len() > 0 {` unbroken.

---

## Fixture: `tests/fixtures/xref_per_master_guard_gate`

**Source read literally:** `conf.py` — two well-formed 4-tuple entries,
`("index", "alpha.typ", "Alpha Master", "Probe Author")` and
`("bravo", "bravo_master.typ", "Bravo Master", "Probe Author")`, plus
`extensions = ["typsphinx", "sphinx.ext.autosectionlabel"]` and
`autosectionlabel_prefix_document = False`. `index.rst` (master alpha) toctrees `target` and ends
its body with `See :ref:\`guarded target section\` for the guarded section.` `bravo.rst` (master
bravo, `:orphan:`, no toctree) carries the byte-identical `:ref:` sentence. `target.rst` carries a
SINGLE section titled "Guarded Target Section" — deliberately no explicit `.. _label:` directive
(the conf.py comment block records why, measured this session: an explicit target directly above a
section makes typsphinx emit a SEPARATE `#metadata(none) <label>` anchor, and Typst's PDF export
registers a Named Destination only for a HEADING anchor via `#outline()`, never for a bare metadata
one — so a `:ref:` resolving to a metadata-only label compiles a real link whose PDF `/Dest` is an
unnamed positional array, making a destination-based PDF assertion unwritable).
`sphinx.ext.autosectionlabel` resolves `:ref:`guarded target section`` DIRECTLY to the section's own
auto id with no separate node, so the referenced label IS the heading anchor and DOES get a real
Named Destination — verified this session against a real compiled PDF's `/Names/Dests` name tree.

**Derivation of the label:** `_namespace_label("target", "guarded-target-section")` =
`"target:guarded-target-section"` (no Typst-invalid characters, `_sanitize_label` is a no-op; the
docutils auto id for the title "Guarded Target Section" slugifies to `guarded-target-section`). The
reference's link text is the target section's title, per Sphinx's standard `:ref:` auto-text rule:
`text("Guarded Target Section")`.

### Expected `index.typ` AND `bravo.typ` — IDENTICAL guarded expression in both

Since the `:ref:` sentence is byte-identical in both source `.rst` files and the guard is a PURE
function of the reference's own properties (never of which master is compiling it — the whole
point of moving the decision to compile time), both content files emit the exact same guarded
reference line:

```
context { let __tsx_body = [#{text("Guarded Target Section")}]; if query(<target:guarded-target-section>).len() > 0 { link(<target:guarded-target-section>, __tsx_body) } else { __tsx_body } }
```

No `#` prefix — `_in_markup_mode` is `False` at this call site (a plain `:ref:` with empty `ids`
never enters the D-14 own-anchor branch, matching the CURRENT unguarded form's own prefix, recorded
in `48-RED-EVIDENCE.md`: `link(<target:guarded-target-section>, `).

### Expected compiled-PDF behaviour (destination-based, never count-based)

`typsphinx/templates/base.typ` calls `outline(...)` UNCONDITIONALLY (the caption heading above it
is the only conditional part), and Typst emits one GoTo `/Link` annotation per outline entry — so
ANY heading in either master's own content produces link annotations unrelated to the guard. A
`len(annotations) == 0` assertion would therefore fail (or pass) for a reason having nothing to do
with what this fixture proves. Every link assertion below reads link **destinations**, never
counts:

| Compiled PDF | `target:guarded-target-section` among link destinations? | Why |
|---|---|---|
| `alpha.pdf` | **YES** | `alpha.typ` (the wrapper for `index`) `#include()`s `target.typ` via the toctree — Typst's `query(<target:guarded-target-section>)` inside THIS wrapper's compile finds a real label, so the guard's `if` branch fires and emits a real `link(...)`. |
| `bravo_master.pdf` | **NO** | `bravo_master.typ` `#include()`s only `bravo.typ` — `target.typ` is never included in this wrapper's compile, so `query(<target:guarded-target-section>)` finds nothing here, the guard's `else` branch fires, and `bravo.typ`'s reference renders as plain inline content with no link annotation. |

Both compiles succeed with exit 0 overall for `-b typstpdf`; no `does not exist in the document`
text appears anywhere in the combined build output (CURRENT pre-fix behaviour: `bravo_master.typ`
FATALS with exactly that text, per `48-RED-EVIDENCE.md` Failure mode 1 — this is the assertion
that flips from a strict xfail to a real invariance guard once 48-02 lands).

### D-02 invariance: identical visible text in both PDFs

Per D-02 ("a degraded reference renders as exactly the same visible text as the linked form, with
no visual marking"), the `pypdf`-extracted text of BOTH `alpha.pdf` and `bravo_master.pdf` contains
the substring `"Guarded Target Section"` — the reader sees the identical prose
whether or not the reference happens to be clickable in that particular compiled wrapper.

**CURRENT (pre-fix) values, stated honestly:** both content files ALREADY emit the identical PLAIN
`link(<target:guarded-target-section>, ...)` today (no guard, no `context`/`query`) — this half is NOT
new; `48-RED-EVIDENCE.md` records the byte-identical pre-fix lines side by side. What flips is the
expression's SHAPE (plain `link(` → guarded `context { ... }`) and `bravo_master.typ`'s compile
outcome (FATAL → clean degrade). The two content files agreeing at write time was never broken;
the fatal was always at `bravo_master.typ`'s compile, not at either content file's emission.

---

## Fixture: `tests/fixtures/citation_caption_dangling_label_gate`

**Source read literally:** `conf.py` — single well-formed entry
`("index", "manual.typ", "Citation Caption Gate", "Probe Author")`. `index.rst` carries a
`code-block` directive whose `:caption:` option contains `[Smith2020]_`, and the citation
definition `.. [Smith2020] Smith et al. *A Paper*. 2020.` in the same document.

**Derivation of the label:** the citing node's `ids` (docutils-assigned, e.g. `id1`) is namespaced
via `_namespace_label(self._current_docname(), ids[0])` where `self._current_docname()` is
`"index"` — same document — giving `"index:id1"` (matches `48-RED-EVIDENCE.md`'s verbatim pre-fix
fatal, `label \`<index:id1>\` does not exist in the document`). The citation label's own text is
`"Smith2020"`.

### Expected `index.typ` — the citation definition's guarded backref (D-05, value-expression form)

Per `48-RESEARCH.md` Pitfall 3, this site does NOT stream open/close around a live child walk —
`visit_citation`'s `label_body`/`label_expr` are already fully computed Python strings BEFORE any
`add_text()` call. D-07's contract still applies: `label_body` (currently the bare
`f"link(<{backref_targets[0]}>, {label_content})"` at `translator.py:3273`) becomes the guard's
open string + the already-computed `label_content` + the guard's close string, concatenated as one
Python string:

```
context { let __tsx_body = [#{text("Smith2020")}]; if query(<index:id1>).len() > 0 { link(<index:id1>, __tsx_body) } else { __tsx_body } }
```

The full grid row (unchanged bracket-wrap machinery around it, D-13's own-definition-anchor
attachment untouched):

```
[#{text("[") + context { let __tsx_body = [#{text("Smith2020")}]; if query(<index:id1>).len() > 0 { link(<index:id1>, __tsx_body) } else { __tsx_body } } + text("]")} <index:smith2020>], ...
```

**Why the guard fixes this defect:** `visit_caption`'s `SkipNode` (`translator.py:2670-2671`)
prevents `visit_reference` from EVER running on the citing node inside the `:caption:` option, so
NO `<index:id1>` anchor is ever attached anywhere in the compiled document — not "not yet in this
wrapper" (SC#4's same-document assumption), but genuinely absent, full stop. At Typst compile time,
`query(<index:id1>).len() > 0` therefore evaluates to `0` (false) in EVERY compile, so the guard's
`else` branch ALWAYS fires for this specific site: the citation marker renders as plain,
non-clickable `[Smith2020]` text instead of a dangling `link()`.

### Expected `-b typstpdf` behaviour

Exit 0. The wrapper PDF (`manual.pdf`) exists and starts with the PDF magic bytes (`%PDF`). No
`does not exist in the document` text anywhere in the combined build output (flips from
`48-RED-EVIDENCE.md`'s recorded fatal, `TypstError: label \`<index:id1>\` does not exist in the
document`, exit 2).

### `-b typst` — unchanged (already green pre-fix, stays green)

`48-RED-EVIDENCE.md` already records `-b typst` exits 0 with zero warnings on the unfixed tree —
this half is a plain, non-xfail invariance guard, not a flip.

---

## Fixture: `tests/fixtures/xref_label_collision_guard_gate` — the measured false-negative

**Source read literally:** `conf.py` — single well-formed entry
`("index", "manual.typ", "Collision Gate", "Probe Author")`. `index.rst` toctrees `a_u2f_b` ONLY
and ends its body with `See :ref:\`nested-target\` for the nested section.` `a_u2f_b.rst`'s section
is titled "Nested Target" (docutils auto id `nested-target`, no explicit label). `a/b.rst` is
`:orphan:`, in no toctree, and carries `.. _nested-target:` immediately above a section titled
"Alpha Nested Section" — the ONLY explicit registration of the `nested-target` label, so Sphinx
resolves the `:ref:` to `a/b`'s section.

**Derivation of the label:** `_namespace_label("a/b", "nested-target")` — `_sanitize_label` maps
`/` → `_u2f_` — gives `"a_u2f_b:nested-target"`. This is BYTE-IDENTICAL to
`_namespace_label("a_u2f_b", "nested-target")`, the label `a_u2f_b.rst`'s OWN section heading emits
for its docutils auto id. `48-RED-EVIDENCE.md`'s Baseline 3 measured both emitted `.typ` files
carrying this literal token, confirming the collision is real at the compiled-bytes level, not
merely argued. The reference's link text (auto-derived from `a/b`'s section title) is
`"Alpha Nested Section"`.

### Expected `index.typ` — guarded expression on the COLLIDING label

```
context { let __tsx_body = [#{text("Alpha Nested Section")}]; if query(<a_u2f_b:nested-target>).len() > 0 { link(<a_u2f_b:nested-target>, __tsx_body) } else { __tsx_body } }
```

### Expected `-b typstpdf` behaviour: exit 0, and the ACCEPTED false-negative

`-b typstpdf` exits 0. `a_u2f_b.rst` IS included in the compiled master (via `index`'s toctree), so
`a_u2f_b.typ`'s own heading anchor `<a_u2f_b:nested-target>` genuinely exists in the compile.
`query(<a_u2f_b:nested-target>).len() > 0` therefore evaluates TRUE, and the guard emits a REAL
`link(<a_u2f_b:nested-target>, ...)` — the compiled PDF's link destinations **DO include**
`a_u2f_b:nested-target`, resolving to the DECOY's heading (`a_u2f_b.rst`'s "Nested Target"
section), even though the reference's REAL intended target (`a/b`, marked `:orphan:`, excluded
from the toctree) is absent from the compiled master.

**This is the expected AND ACCEPTED outcome, not a defect to fix in Phase 48.** The guard asks
"does a label with THIS SPELLING exist in this compile", never "does the document I actually meant
exist" — a coincidental namespace collision therefore converts an absent target into a
present-looking one. This class is narrow by construction: because labels are namespaced
`docname:id` and `_sanitize_label` is injective per character, a collision requires the DOCNAME
segment to collide too, and the only route available in this codebase is the `/` → `_u2f_`
transform this fixture exercises. No expected value in this document treats this outcome as
something 48-02/48-03/48-04 must fix.

---

## `tests/test_xref_orphan_degrade_render_gate.py`

**Source read literally (already-existing fixture, `xref_orphan_degrade_render_gate`):** master
`index` (target `master.typ`, casefold-de-collided from the docname per the Phase 47 fixture rule)
toctrees `included`; `orphan` is `:orphan:`, in no toctree. `included.rst` carries a `:ref:` to
`orphan.rst`'s `.. _orphan-target:` labelled section (title "Orphan Target Section") AND a `:ref:`
to a label in `included` itself (`included-target`).

Three assertions flip; one negative assertion (D-06) does not and is restated as an explicit
invariance guard.

### 1. The non-included-target assertion INVERTS

**Current:** `"link(<orphan:" not in scannable` (asserts NO label link is emitted — build-time
suppression).

**New expected value:** the emitted `included.typ` DOES carry the orphan document's namespaced
label, inside the guard's `if`/`else` expression:

```
context { let __tsx_body = [#{text("Orphan Target Section")}]; if query(<orphan:orphan-target>).len() > 0 { link(<orphan:orphan-target>, __tsx_body) } else { __tsx_body } }
```

New assertion: `"link(<orphan:orphan-target>," in scannable` — present, but now as part of the
GUARDED conditional expression, not a bare unconditional link.

### 2. The plain-text-rendering assertion — re-derived, not assumed

**Current:** `'text("Orphan Target Section")' in scannable` (asserts the reference's text renders
as a bare code-mode `text(...)` call — true pre-fix because the reference degrades entirely to
plain inline content).

**New expected value, derived from the ADOPTED `code_mode_body=True` spelling:** since Step 0
adopted the code-mode-body form (children stream in code mode exactly as today,
`48-EVIDENCE.md`'s whole rationale for adopting it), this assertion's literal string does NOT
change — `text("Orphan Target Section")` STILL appears verbatim in the emitted body, now nested one
level deeper inside the guard's `[#{ ... }]` wrapper rather than as a bare unwrapped `text(...)`
argument to `link(`. The assertion `'text("Orphan Target Section")' in scannable` is therefore
UNCHANGED as written, but its justification changes: it now proves the guard's code-mode-body
choice preserved this exact substring rather than proving the reference degraded to plain text
outside any link wrapper.

### 3. The included-target (same-document) assertion — UNCHANGED, restated as D-06 invariance

**Current and new (identical):** `'link(<included:included-target>,' in scannable` and
`'<included:included-target>]' in included_typ` both still hold. `:ref:` to a target inside the
SAME document (`included` referencing its own `included-target` label) is NOT a cross-document
`xref` and never enters the D-07 guard — it stays on `visit_reference`'s unguarded internal-refuri
branch (`refuri.startswith("#")`), per D-06. This is the explicit invariance guard: only the
CROSS-document form (the `xref is not None` branch) is guarded; the SAME-document form is
byte-identical before and after this phase.

### 4. Whole-project no-dangling-label outcome — UNCHANGED outcome, changed mechanism

**Current and new (identical outcome):** `-b typstpdf` exits 0, `master.pdf` exists and starts with
`%PDF`. This assertion's TRUTH VALUE does not flip — what changes is the MECHANISM producing it:
pre-fix, the build-time `master_included_docnames` union suppressed the dangling link before it
was ever written; post-fix, the compile-time guard prevents the same fatal by degrading at Typst
compile time instead. The module's docstring must be rewritten (in the plan that implements this)
to describe the compile-time mechanism, since its current prose ("the fix computes the master's
transitive toctree closure up-front...") describes the exact mechanism this phase deletes.

---

## `tests/test_master_include_set_predicate_gate.py`

**Source read literally (`bld03_ghost_entry_xref_gate`):** `typst_documents = [("index",
"manual.typ", "Real Master", "Probe Author"), ("ghost",)]`. `index.rst` carries a `:ref:` into
`ghost_child`'s label (`ghost-child-label`); `ghost` is a 1-tuple entry producing NO wrapper file
(the `_is_usable_typst_documents_entry()` predicate rejects it), so `ghost_child.typ` is never
`#include()`d into the compiled `manual.typ`, regardless of whether `ghost.rst`'s own toctree lists
it.

### The line-103 test flips: `test_ghost_entry_subtree_xref_degrades_typst`

**Current:** `"link(<ghost_child:" not in scannable` (build-time suppression via the deleted
`_compute_master_included_docnames()`'s over-permissive `if entry` filter admitting the
under-length entry's whole toctree closure).

**New expected value:** the emitted `index.typ` DOES carry the `ghost_child`-namespaced label
inside the guard:

```
context { let __tsx_body = [#{text("Ghost Child Target Section")}]; if query(<ghost_child:ghost-child-label>).len() > 0 { link(<ghost_child:ghost-child-label>, __tsx_body) } else { __tsx_body } }
```

The compiled PDF (`manual.pdf`) still shows the reference's text (`"Ghost Child Target Section"`)
with NO link annotation for `ghost_child:ghost-child-label` among its destinations (`ghost_child`'s
content is never `#include()`d into `manual.typ`, so the query genuinely finds nothing), and no
`TypstError` — the existing `test_ghost_entry_no_dangling_label_typstpdf` (line 129) already
asserts this outcome and does not need to change.

### D-10: three end-to-end tests keep their EXACT current expected values, unchanged

- `test_ghost_entry_no_dangling_label_typstpdf` (line 129) — asserts `-b typstpdf` still fails
  overall (the malformed `('ghost',)` entry is STILL separately reported by `finish()`'s existing
  under-length-entry diagnostic, unrelated to the guard), `"does not exist in the document"` absent,
  `"has no target element"` present, and `manual.pdf` exists and starts with `%PDF`. All unchanged.
- `test_unhashable_docname_skipped_gracefully_typst` (line 196) — asserts `-b typst` exits 0, no
  `TypeError`/`unhashable type` leaked, `"produces no wrapper file"` warning present, both
  `index.typ` and `real.typ` exist. Unrelated to the guard entirely (a different fifth-site
  predicate-guard defect, already fixed in Phase 47); unchanged.
- `test_unhashable_docname_reported_by_finish_typstpdf` (line 227) — asserts `-b typstpdf` fails
  overall with `"non-str docname"` present, no `TypeError`, `real.pdf` exists. Unrelated to the
  guard; unchanged.

### D-10: four unit tests bound directly to the deleted function are REMOVED, not rewritten

`_compute_master_included_docnames()` is deleted outright (SC#3). These four tests call it
DIRECTLY and lose their subject entirely — they are removed, not adapted:

- `TestGhostEntryIncludeSetUnit::test_ghost_entry_excluded_from_master_include_set` (line 165)
- `TestUnhashableDocnameIncludeSetUnit::test_compute_master_included_docnames_tolerates_unhashable_docname`
  (line 260)
- `TestMasterIncludeSetInvarianceGuards::test_well_formed_masters_still_yield_full_toctree_closure`
  (line 288)
- `TestMasterIncludeSetInvarianceGuards::test_empty_typst_documents_still_yields_empty_set`
  (line 319)

Net: 8 tests today → 1 flips + 3 survive unchanged + 4 removed = 4 tests after this change.
`_is_usable_typst_documents_entry()` itself SURVIVES for its four remaining consumers (the
collision validator, `write()`'s D-07 wrapper report, `_write_typst_files()`'s wrapper loop, and
`TypstPDFBuilder.finish()`) — its docstring's consumer count corrects from FIVE to FOUR in the same
change (the fifth consumer, `_compute_master_included_docnames()`, no longer exists).

---

## `tests/test_citation_degradation_gate.py`

Three sites change, all consuming the now-unconditional `opens_wrapper = bool(refuri or refid)`
(D-09: `degrade_xref_to_text` is deleted from `_reference_anchor_decision` entirely, so the
`and not degrade_xref_to_text` term simply disappears).

### `TestWr03EligibilityDecisionAgreesWithEmission`'s parametrized case: `refuri_excluded_document` flips

**Current (line 1056):** `("refuri_excluded_document", _wr03_case_refuri_excluded_document, False)`
— `expected_eligible=False`, because `_StubBuilder.master_included_docnames = {"index"}` excludes
`"second"` (the case's `refuri="second.typ#anchor-c"` target), so `degrade_xref_to_text=True` forces
`opens_wrapper=False` forces `eligible=False`.

**New expected value:** `expected_eligible` becomes **`True`**. Under D-09, `opens_wrapper` is
`bool(refuri or refid)` UNCONDITIONALLY — `refuri` is present, so `opens_wrapper=True` regardless
of any include-set membership (the concept no longer exists on the builder). `eligible =
bool(node.get("ids")) and opens_wrapper and not next_is_target` — `ids=("citer-c",)` (populated),
`opens_wrapper=True`, `next_is_target=False` (no following target sibling) → `True`. The case's own
docstring premise ("`opens_wrapper` degrades to `False`... NOT eligible") is exactly what D-09
reverses; the case's NAME (referencing "excluded document") becomes a historical label for a
scenario the code no longer treats specially — the anchor is `_current_docname()`-derived (always
same-document) and is granted regardless of whether the CROSS-document target the reference points
at is present anywhere.

### `TestWr03DegradedCitingSiteAnchor` — the whole premise moves from degrade to eligible

`_build_degraded_doctree()`'s citing reference (`refuri="second.typ#krizhevsky2012"`,
`ids=("id1",)`) is, post-fix, ALWAYS eligible for its own D-14 anchor (same reasoning as above):
`opens_wrapper=True` unconditionally, `ids` populated, no following target. Its cross-document
`link` to `second:krizhevsky2012` now routes through the D-07 guard instead of the deleted
build-time degrade branch.

- `test_wr03_degraded_citing_site_emits_no_dangling_backref` — assertion `dangling == set()` KEEPS
  its truth value (still passes), but via a DIFFERENT mechanism: pre-fix, the body contains ZERO
  `link()` calls at all (the reference degraded to bare `text("[Krizhevsky2012]")` and the citation
  backref loop, seeing `decision.eligible=False`, appended no marker — trivially no dangling link).
  Post-fix, the body contains the guarded cross-document expression PLUS a real
  `link(<index:id1>, ...)` in the citation definition's grid row, targeting the citing site's OWN
  now-attached anchor (`index:id1`, emitted via the D-14 bracket-wrap composition) — a real link
  with a real matching anchor, non-trivially satisfying the same "no dangling" assertion.
- `test_wr03_degraded_citing_site_body_compiles` — stays green (unchanged truth value): pre-fix,
  compiles because there are no links to dangle; post-fix, compiles because the guard prevents any
  fatal AND the own-anchor is correctly attached — never a `TypstError` either way.
- `test_wr03_degraded_citation_renders_plain_label_shape` — **FLIPS.** Current assertion:
  `"link(" not in row` (the citation row must be plain, non-linked, because the sole backref was
  filtered out as ineligible). New expected value: the row DOES contain a `link(` call — the
  backref is no longer filtered (decision.eligible is now True), so the citation definition emits a
  real, guarded `link(<index:id1>, ...)` targeting the citing site's own attached anchor. The
  assertion must be rewritten to check the label cell carries a `link(` call whose target is
  `index:id1` (or, if wrapped by the D-07 citation-site guard per D-05's own reasoning, the guard's
  `context { ... link(<index:id1>, ...) ... }` form), never a bare unlinked bracketed label.

### `TestWr03XrefResolutionAndWarningFireOnce` — the warning half has no subject after D-01

- `test_wr03_xref_resolution_happens_once_per_reference`'s FIRST assertion (`_resolve_xref_docname`
  called exactly once) is **UNCHANGED** — `visit_reference` (`translator.py:4859`) calls
  `_reference_anchor_decision(node)` exactly once and consumes `decision.xref`; it never
  re-invokes `_resolve_xref_docname` itself, before or after this phase.
- The SECOND assertion (`mocked_warning.call_count == 1`, naming `"second"` in the message) **HAS
  NO SUBJECT AFTER D-01.** The cross-document degrade-to-text warning
  (`translator.py:4995-4999`) is deleted outright, with no diagnostic replacement. New expected
  value: `mocked_warning.call_count == 0` — NO warning is emitted for a cross-document reference,
  regardless of whether its target is present or absent in any particular compile (the whole
  question moved to Typst's `query()`, which raises no Python-side warning either way).

---

## Assertions that must NOT change (D-06)

The two SAME-document `visit_reference` branches keep emitting the plain unguarded `link(<label>, `
form, with NO guard wrapping, in every existing test in the corpus:

1. **Bare-refid branch** (`translator.py:4945-4961`, `if not refuri and refid`) — an internal
   same-document `:target:` (e.g. a figure/image target) resolves to a bare `refid` with no
   `refuri`. Stays: `{prefix}link(<{label}>, ` with no `context`/`query` wrapper.
2. **`#`-prefixed internal refuri branch** (`translator.py:4980-4984`,
   `if refuri.startswith("#")`) — an internal same-document `:ref:`/`:doc:` resolved to a
   `#anchor`-shaped `refuri`. Stays: `{prefix}link(<{label}>, ` with no guard.

Every existing same-document-anchor test in the corpus (e.g.
`tests/test_xref_orphan_degrade_render_gate.py`'s `included:included-target` assertions above,
`tests/test_translator.py`'s xref/refid unit tests, `tests/fixtures/xref_refid_render_gate/`'s
render gate) keeps its CURRENT expected value unchanged. SC#4's rationale: content files are
included wholesale (unconditionally, per COMP-01), so a same-document target's presence is
guaranteed — EXCEPT the one measured exception this phase brings under the guard anyway (D-05's
citation-caption route, where `SkipNode` structurally prunes the anchor's emission even though the
file IS included).

---

## How to find any assertion I missed

Two repo-wide greps a later plan must run to prove this document's enumeration is complete, so the
phase does not rely on this document's completeness alone:

```bash
# 1. Every remaining reference to the symbols this phase deletes. Any hit outside
#    typsphinx/builder.py's own deletion diff, or outside a test this document already
#    names, is an assertion this document missed.
grep -rn 'master_included_docnames\|degrade_xref_to_text\|_compute_master_included_docnames' \
  tests/ typsphinx/

# 2. Every assertion that inspects a cross-document link( emission or its absence -- the
#    exact shape a guard-introducing change can silently break without a matching
#    grep-based sweep. Cross-reference each hit against this document's "Fixture:" and
#    per-module sections above; any file NOT named here that matches is a candidate this
#    document missed.
grep -rln 'link(<[a-z_]*[a-z0-9_]*:' tests/*.py
grep -rln '"link(<"' tests/*.py
```

Both commands were run against this plan's own tree during Task 2 authoring (read-only, no
`typsphinx/` change). Grep 1 confirms the six named sites above are the complete set for the
deleted SYMBOLS (`master_included_docnames`/`degrade_xref_to_text`/
`_compute_master_included_docnames`) — every hit falls inside `typsphinx/builder.py`'s own
deletion diff, `typsphinx/translator.py`'s own deletion diff, or a test/fixture-comment already
named above.

Grep 2 is DELIBERATELY broader and surfaces MORE files than the six sites above:
`test_desc_container_propagated_target_render_gate.py`,
`test_duplicate_include_label_render_gate.py`, `test_citation_render_gate.py`,
`test_cross_doc_label_namespace_render_gate.py`, `test_rubric_propagated_target_render_gate.py`,
`test_field_body_typography_render_gate.py`, `test_signature_typography_gate.py`,
`test_paragraph_propagated_target_render_gate.py`. **A critical structural fact makes almost all of
these ROBUST to the guard wrap, not additional flips:** the guard's `.typ` SOURCE text contains
BOTH branches' bytes always — `if query(<L>).len() > 0 { link(<L>, __tsx_body) } else { __tsx_body
} }` — regardless of which branch Typst's `query()` actually takes at compile time. A test
asserting `"link(<label>" in text` (a POSITIVE substring/regex-membership check, the pattern every
one of these eight files uses, verified by reading each) stays TRUE whether the guard's target is
present or absent, because the literal bytes `link(<label>,` sit inside the `if` branch's source
text either way. This was checked concretely:

- `test_cross_doc_label_namespace_render_gate.py`'s `"pageb:shared-topic" in pagea_link_labels`
  (a `re.findall(r"link\(<([^>\n]+)>", ...)` extraction) stays true post-fix for exactly this
  reason — it does not need an entry above.
- `grep -n 'not in.*link\|link.*not in\|assert.*not.*link(<' tests/*.py` (a targeted search for the
  ONE assertion SHAPE that would actually break — a NEGATIVE assertion on cross-document link
  presence) found exactly two hits, both in `test_citation_render_gate.py`, and BOTH are about
  mechanisms this phase does not touch: line 603 (`nosuchkey_anchor not in link_targets_index`) is
  an UNRESOLVED citation key (Sphinx warns and leaves it unresolved before the translator ever
  runs — never reaches `visit_reference`/the guard at all), and line 779 (`"link(" not in
  never1999_row`) is a ZERO-backref uncited citation (`visit_citation`'s `len(backref_targets) ==
  1` branch is the ONLY one D-05 guards — a zero-backref citation takes the untouched
  `label_body = label_content` branch with no link at all, guarded or otherwise).
- No file in the corpus asserts the EXACT literal byte sequence `[#link(<` or any full-string
  equality involving a cross-document `link(<label>` expression (`grep -n '"\[#link(<'` and
  `grep -n '== .*link(<'` both returned zero hits across `tests/*.py`) — the one assertion SHAPE
  that a byte-level guard-wrap change would genuinely break, and it does not occur anywhere outside
  the six sites already enumerated above.

**Conclusion, stated honestly:** the six sites above are the complete set of assertions whose TRUTH
VALUE flips. Grep 2's wider hit list is expected and was individually triaged, not a gap — a later
plan must still re-run both commands against its own diff, since a future edit to any of these
"robust" files could introduce a genuinely fragile assertion this reasoning does not anticipate.
