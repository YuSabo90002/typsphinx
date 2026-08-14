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

---

# Phase 48 Plan 05 — Whole-Document Reference Path (G-48-4 / XREF-03 gap closure)

**Written:** 2026-08-14. **No emitter change exists while this section was written** —
`git status --porcelain typsphinx/` printed nothing throughout Task 3. Every value below is
derived from `48-EVIDENCE.md`'s "Guard contract, fixed by this measurement" (quoted verbatim where
substituted), the existing `_namespace_label`/`_sanitize_label`/`_emit_id_anchors` code read
literally (`typsphinx/translator.py`), a real `docutils.nodes.make_id` transcript run this session,
and the fixture-comment convention established by
`tests/fixtures/xref_orphan_degrade_render_gate/conf.py` and
`tests/fixtures/xref_per_master_guard_gate/conf.py`. Binding constraint #6 forbids deriving any of
this from a fresh build — none was run for this section.

## 1. The self-anchor token

**Fixed token: `__tsx-doc__`** — the planner's derived preference recorded in `48-05-PLAN.md`
Task 3, matching the project-wide `__tsx_` prefix convention `48-EVIDENCE.md` already fixed for the
D-07 guard's own bound identifier (`__tsx_body`). It lives as **one module-level constant** in
`typsphinx/translator.py` (suggested name: `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN`), consumed by both
the definition site (§2 below) and the reference site (§3 below) — never re-spelled at either.

**Collision-safety argument, run rather than asserted.** The token deliberately carries BOTH an
underscore (`_`) and a hyphen (`-`). Two claims must both hold for that combination to be safe
against the two label sources named in the plan task, and both were measured this session rather
than assumed:

**Claim 1 — `make_id` never emits an underscore, even when the input already contains one.**
Verbatim transcript, `uv run python` against this worktree's pinned docutils
(`docutils.nodes.make_id`), nine adversarial probes including inputs that already carry
underscores:

```
make_id('Guarded Target Section') = 'guarded-target-section'   contains '_': False
make_id('already_has_underscore') = 'already-has-underscore'   contains '_': False
make_id('already_has__double__underscore') = 'already-has-double-underscore'   contains '_': False
make_id('Mixed_Case With Spaces_and-Hyphens') = 'mixed-case-with-spaces-and-hyphens'   contains '_': False
make_id('trailing_underscore_') = 'trailing-underscore'   contains '_': False
make_id('_leading_underscore') = 'leading-underscore'   contains '_': False
make_id('C++ / weird @#$% chars') = 'c-weird-chars'   contains '_': False
make_id('1234 numeric start') = 'numeric-start'   contains '_': False
make_id('') = ''   contains '_': False
```

Every probe — including the two that deliberately fed `make_id` an input already containing one or
two underscores — comes back with the underscore(s) mapped to hyphen(s). `make_id` cannot produce a
raw docutils auto-id (the source `_emit_id_anchors`/`_namespace_label` namespace for every
same-document target, section heading, and figure/table anchor) containing `_` at all.

**Claim 2 — a Sphinx domain object id (a Python identifier) cannot contain a hyphen.** Python's own
identifier grammar (`[A-Za-z_][A-Za-z0-9_]*`) structurally excludes `-`; every python-domain object
id in this corpus is built from a dotted chain of such identifiers. Measured directly against this
worktree's own real corpus build (`docs/_build/pdf/api/index.typ`, produced by Task 1's build,
read-only — no emitter change), a representative sample of the actual namespaced labels this build
emitted for real domain objects:

```
<api_u2f_index:typsphinx.builder.TypstBuilder.write_doc>
<api_u2f_index:typsphinx.builder.TypstBuilder.get_target_uri>
<api_u2f_index:typsphinx.pdf.TypstCompilationError.message>
<api_u2f_index:module-typsphinx.translator>
```

Every domain-object segment (`typsphinx.builder.TypstBuilder.write_doc`, etc.) is dots and word
characters only — zero hyphens anywhere in any of the 40+ domain-object ids this corpus's `api/index`
page emits (spot-checked; every hit in the corpus grep carries `_` freely inside identifier
segments, e.g. `get_target_uri`, but never `-`).

**Conclusion:** `make_id` output can contain `-` but never `_`; a Sphinx domain object id can
contain `_` but never `-` (Python identifiers exclude it structurally). A token requiring the raw
id to contain BOTH `_` and `-` simultaneously — `__tsx-doc__` — is therefore unreachable from
either generation mechanism. (This argument is scoped to the two sources the plan task names —
`make_id` output and Sphinx domain ids; it does not claim protection against a user's own
hand-written explicit target name that happens to spell `__tsx-doc__` literally, an edge case this
phase does not defend against, matching the accepted-limit precedent already recorded for the
label-collision false negative above.)

## 2. The definition-site form

Immediately after the document's opening code-block brace — `visit_document`
(`typsphinx/translator.py:672-705`) currently ends with `self.add_text("#{\n")` and nothing else —
a new line is added directly after it, using the SAME zero-width `[#metadata(none) <label>]` anchor
form `_emit_id_anchors` already establishes (`typsphinx/translator.py:668`), with the label computed
through `_namespace_label(current_docname, _WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN)` per D-13 — no second
label-derivation spelling.

**Emitted only when the builder supplies a current docname** (`self._current_docname()` is
truthy) — hand-built test doctrees (no builder docname) keep byte-identical output, matching every
other `_current_docname()`-gated site in the translator.

**Fully substituted example, docname `included`:**

`_namespace_label("included", "__tsx-doc__")` = `_sanitize_label("included:__tsx-doc__")` — every
character in `included:__tsx-doc__` is already in `_sanitize_label`'s valid set
(`[A-Za-z0-9_.:-]`), so sanitize is a no-op: `"included:__tsx-doc__"`.

```
#{
[#metadata(none) <included:__tsx-doc__>]
```

(the second line immediately follows `#{\n`, with no leading blank line — the code-block brace's
own trailing newline is what separates them).

## 3. The reference-site form

The D-07 guard contract (`48-EVIDENCE.md` "Guard contract, fixed by this measurement"),
`code_mode_body=True`, `prefix=""`, with the label substituted for the whole-document self-anchor
instead of an anchored xref's own label — no second guard-string derivation point, one
`_label_existence_guard` call whose second argument is the reference's own anchor when it has one
(the existing `xref is not None` branch, unchanged) and the whole-document self-anchor token when it
does not (the `xref is None` branch this gap fix newly routes through the guard instead of the
string-url `else`).

**Docname `included`** (`_namespace_label("included", "__tsx-doc__")` = `"included:__tsx-doc__"`,
link text = the target document's title, per Sphinx's `:doc:` auto-text rule — this fixture's
`included.rst` is titled "Included Whole-Document Target", per §4 below):

```
context { let __tsx_body = [#{text("Included Whole-Document Target")}]; if query(<included:__tsx-doc__>).len() > 0 { link(<included:__tsx-doc__>, __tsx_body) } else { __tsx_body } }
```

**Docname `orphan`** (`_namespace_label("orphan", "__tsx-doc__")` = `"orphan:__tsx-doc__"`,
`orphan.rst` titled "Orphan Whole-Document Target", per §4 below):

```
context { let __tsx_body = [#{text("Orphan Whole-Document Target")}]; if query(<orphan:__tsx-doc__>).len() > 0 { link(<orphan:__tsx-doc__>, __tsx_body) } else { __tsx_body } }
```

Both strings are byte-for-byte the `48-EVIDENCE.md` contract with only the label and body text
substituted (diffed by eye against that section's "Fully substituted example" while writing this —
`close_str`'s `if query(...).len() > 0 {` stays on one unbroken statement in both, per Pitfall 1).
The guard's `query`/`link` arguments are the identical string in both cases (the label appears
twice, byte-identical, exactly as the contract requires).

## 4. The fixture's expected emission

`tests/fixtures/xref_whole_document_guard_gate/` (files created by plan 48-06, designed here on
paper per D-03):

- `conf.py`: single well-formed entry `("index", "manual.typ", "Whole Document Guard Gate", "Probe
  Author")` — target `manual.typ` does NOT casefold-collide with the docname's own content path
  `index.typ` (fixture de-collision rule, `47-EXPECTED-STRUCTURE.md`, same convention every sibling
  fixture in this phase already follows).
- `index.rst`: toctrees `included` ONLY. Body carries one whole-document reference to each target:
  `:doc:`included`` and `:doc:`orphan``.
- `included.rst`: titled "Included Whole-Document Target", body carries a distinctive marker string
  `INCLUDED_BODY_MARKER_TEXT` so the compiled PDF's extracted text can identify this page by
  content.
- `orphan.rst`: marked `:orphan:`, in NO toctree, titled "Orphan Whole-Document Target", body
  carries a distinctive marker string `ORPHAN_BODY_MARKER_TEXT`.

**Per emitted file, what must be present and what must be absent:**

- `index.typ` carries BOTH guarded expressions from §3 above, and carries NO string-url form naming
  either target's output file (i.e. no `link("included.typ", ...)` / `link("included.pdf", ...)`
  anywhere — the whole point of routing the `xref is None` whole-document case through the guard
  instead of the external-link `else` branch).
- `included.typ` carries its own self-anchor from §2 exactly once:
  `[#metadata(none) <included:__tsx-doc__>]`.
- `orphan.typ` carries its own self-anchor from §2 exactly once:
  `[#metadata(none) <orphan:__tsx-doc__>]`.

## 5. The expected PDF shape

Derived from the compiled master (`manual.typ` `#include()`s `index.typ` and `included.typ` via
`index`'s own toctree; `orphan.typ` is written but never `#include()`d, matching the established
orphan-degrade pattern this phase's other fixtures already exercise), NOT from a build:

- The master's PDF carries **ZERO** URI actions whose target ends in the builder's `out_suffix` —
  both whole-document references route through the guard now, never the string-url branch.
- The master's PDF carries **exactly ONE** link annotation with a **positional (non-string)
  destination** — the whole-document reference to `included`. Its target is a `metadata` anchor
  (§2's zero-width form), not a heading anchor; per
  `tests/test_xref_compile_time_guard_render_gate.py`'s `_link_annotation_dests` docstring
  (`typsphinx/translator.py`-adjacent, already measured this phase): Typst registers a NAMED PDF
  destination only for a label that participates in `#outline()` (a heading anchor) — a link to a
  non-heading label still compiles and still produces a real `/Link` annotation, but its `/Dest` is
  an unnamed positional array with no string to recover. `included.typ` IS `#include()`d in
  `manual.typ` (via `index`'s toctree), so `query(<included:__tsx-doc__>)` finds the self-anchor
  and the guard's `if` branch fires — a real link, positional destination.
- The reference to `orphan` produces **NO annotation at all** — `orphan.typ` is never
  `#include()`d into `manual.typ`, so `<orphan:__tsx-doc__>` never exists in that compile;
  `query(<orphan:__tsx-doc__>)` finds nothing, the guard's `else` branch fires, and the reference
  renders as plain non-clickable text.
- The visible text of BOTH references — "Included Whole-Document Target" and "Orphan Whole-Document
  Target" — is present in the extracted page text, identically shaped, per D-02: the reader sees
  the same words whether or not the reference happens to be clickable in this compile.

The positional destination's page is resolvable through `pypdf` (walk `/Annots`, find the one
`/Link` whose `/Dest` is a non-string array, read its page-reference entry), and the gate will
assert that page's extracted text contains `included`'s body marker
(`INCLUDED_BODY_MARKER_TEXT`). **Stated honestly:** if this fixture's whole compiled document lays
out on a single PDF page (plausible — it is a minimal three-document fixture), this assertion is
TRUE but WEAK — it would pass even if the annotation pointed at the wrong page, because there is
only one page to point at. The gate module implementing this in plan 48-06 must say so in its own
docstring rather than overclaim page-level precision, matching the honesty standard
`_link_annotation_dests`'s own docstring already sets for this exact class of PDF-structural
caveat.

## 6. The owner's decision (Task 2 checkpoint), recorded verbatim

**Selected: option-a** — "Leave them as they are — guard only references that resolve onto a real
document." Recorded verbatim from the checkpoint's option text (`48-05-PLAN.md` Task 2): "Smallest
change; the policy predicate is a plain `found_docs` membership test; nothing that is not a real
document changes behaviour at all; zero risk to any relative link to a genuine file asset."
Consequence, also verbatim: "Sub-population B's annotations stay in the PDF as dead file links —
clicking 'Index', 'Module Index' or 'Search Page' still produces the owner's original
ERR_FILE_NOT_FOUND. The gap is closed for every real document but not for these." **This choice was
made by the owner at the blocking checkpoint task, not by the executor** — the executor's earlier
checkpoint return presented both options with their full pros/cons and awaited the decision without
recommending either.

**Predicate the chosen option implies:** a plain `found_docs` membership test — the SAME test
already available at the D-07 guard's single existing call site (`visit_reference`'s `xref is
not None` branch already namespaces via the target docname; the `xref is None` whole-document case
this gap adds routes through the identical `_label_existence_guard` call, gated by whether
`_resolve_xref_docname`'s target-path resolution lands on a docname Sphinx's own `env.found_docs`
contains). No second degrade mechanism, no second guard-string derivation point (D-07), no second
label helper (D-13) — the predicate lives as one condition at the one existing call site, exactly as
the checkpoint's option text promised.

**The single expected post-fix number, subtracted from the baseline pinned in Task 1:**

- **Baseline (pre-fix, `48-RED-EVIDENCE.md` "Baseline 4"):** 40 URI-action annotations across 20
  distinct targets, built via `uv run tox -e docs-pdf` (the SAME invocation plan 48-07 must re-run).
- **Sub-population A — 15 distinct targets, 35 annotations — CLOSES.** Every target resolves onto a
  real docname per Task 1's measurement, so under option-a's `found_docs` test every one of these
  routes through the D-07 guard instead of the string-url branch post-fix. In THIS corpus every
  resolved docname is toctree-reachable from the single `typst_documents` master
  (`docs/source/conf.py` defines exactly one master, `typsphinx.typ`, and Task 1's own
  `found_docs` enumeration — 13 docnames — matches the corpus's full toctree closure), so
  `query()` finds every one of these self-anchors at Typst compile time: all 35 annotations convert
  from broken `/URI` file-actions into real, working internal `/Dest` links. Zero of them remain as
  URI actions ending in `.pdf`.
- **Sub-population B — 5 distinct targets, 5 annotations — REMAINS, by policy.** `genindex.pdf`
  (cited from `index`), `py-modindex.pdf` (cited from `index`), `search.pdf` (cited from `index`),
  `../genindex.pdf` (cited from `api/index`), `../py-modindex.pdf` (cited from `api/index`) — none
  resolves onto a member of `found_docs` (`genindex`/`py-modindex`/`search` are Sphinx-generated
  virtual pages, never real documents), so option-a's predicate leaves every one of them on the
  UNCHANGED string-url branch. Each stays exactly as it was pre-fix: a `link("<target>.pdf", ...)`
  URI action pointing at a file the Typst output never produces.
- **Expected post-fix count: `5`** URI actions ending in the builder's `out_suffix` (`.pdf`) in the
  rebuilt `docs/_build/pdf/typsphinx.pdf`, built via `uv run tox -e docs-pdf` — NOT `0`. Plan
  48-07's end-to-end re-measurement task asserts this exact number, subtracted from the 40-annotation
  baseline this section names, using the identical build invocation Task 1 pinned.

## 7. The collateral-change budget

**The one emission change that is corpus-wide:** every content file gains one line at its top — §2's
self-anchor metadata line, emitted for EVERY document that has a builder-supplied current docname
(unconditionally, regardless of whether anything actually references that document whole-document-
style — `visit_document` cannot know in advance whether a future reference will need the anchor).
This is the expected CAUSE of any existing test asserting an exact byte-for-byte match against a
document's opening bytes (the line immediately after `#{\n`).

**Measured this session, honestly, not assumed:** `grep -rn 'startswith("#{'"'"'\|"#{\\\\n"' tests/*.py`
found exactly one hit, `tests/test_citation_degradation_gate.py:786-787`
(`if not body.startswith("#{"): body = "#{\n" + body`) — a DEFENSIVE normalization that PREPENDS the
wrapper when absent, not a brittle equality assertion; it is unaffected by an extra line appearing
after the brace. No test in this corpus was found asserting an exact multi-line equality against a
document's opening bytes that would break from this one-line insertion. **The rule plan 48-07 must
still follow regardless:** any test whose expected value DOES turn out to depend on a document's
exact opening bytes has its new expected value derived from THIS artifact's §2, written into the
test with a comment tracing it here — never copied out of a fresh build. A later plan must re-run
the grep above (and its own broader sweep, per the "How to find any assertion I missed" section
above) against its own diff, since this finding is only as complete as the corpus this session
measured it against.

---

# Phase 48 Plan 07 — Collateral Test Changes (G-48-4 / XREF-03 emitter fix)

**Written:** 2026-08-14, after the emitter change (Task 1) landed and the full suite was re-run
(Task 2's own action). Per §7's own prediction, the corpus-wide one-line-per-content-file emission
change surfaced exactly one failure — no more, no fewer than the grep in §7 found.

## Tests whose expected value changed

| Test | File | Sub-part derived from | Reason |
|------|------|------------------------|--------|
| `test_emitted_typ_is_byte_identical_to_golden` | `tests/test_desc_rubric_decoupling_render_gate.py` (fixture: `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`) | "Phase 48 Plan 05" §2's definition-site form, docname `index` | This fixture's `index.rst` is built via a real `-b typst` `sphinx-build` (a builder-supplied current docname of `index`), so `visit_document` now emits `[#metadata(none) <index:__tsx-doc__>]` immediately after the opening `#{` — exactly the corpus-wide emission change §7 predicted. `golden.typ` gained that one line at the position §2 fixes; the test file's own docstring was updated with a comment tracing the change to this section. |

No other test's expected value moved. `uv run pytest -q` was run to completion once the emitter
change landed (Task 1's own commit) and surfaced this single failure; fixing it (updating the
committed golden fixture, not the emitter) returned the suite to fully green with no further
iteration needed.

## Real regressions found

None. Every hand-built-doctree test (no builder docname) stayed byte-unchanged, confirming the
"only when a docname is supplied" gate in `visit_document` is correctly wired. No duplicate-label
fatal was observed on any fixture, including the diamond-include case
(`tests/test_duplicate_include_label_render_gate.py`, run explicitly per Task 1's own acceptance
criteria).

## Quality trio

- `uv run pytest -q` → **1083 passed, 1 skipped, 0 failed, 0 errors, 0 xfailed, 0 XPASS.**
- `uv run black --check .` → one file needed reformatting after Task 1's edit
  (`typsphinx/translator.py`, the `_reference_anchor_decision` policy-gate `if` statement's line
  wrap); reformatted via `uv run black typsphinx/translator.py`, re-verified clean, and the suite
  re-run green afterward (no behavioural change — a pure line-wrap).
- `uv run mypy typsphinx/` → `Success: no issues found in 6 source files`.
- `uv run ruff check .` → could not execute locally: `Could not start dynamically linked
  executable: ruff` / `NixOS cannot run dynamically linked executables intended for generic linux
  environments out of the box.` This is the documented, pre-existing NixOS deferral
  (`ruff-generic-linux-elf-unrunnable-on-nixos`, `.planning/todos/pending/`, PROJECT.md's Deferred
  Items, and every prior Phase 48 plan's own note) — no standalone nix-store `ruff` package was
  available to symlink in this worktree (plan 48-06 recorded the identical finding). CI carries
  lint authority per the same documented deferral; this is recorded plainly rather than claimed as
  a clean result.
