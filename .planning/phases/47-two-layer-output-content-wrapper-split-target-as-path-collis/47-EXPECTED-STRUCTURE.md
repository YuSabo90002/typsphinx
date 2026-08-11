# Phase 47 Plan 01 — Expected Two-Layer Output Structure

**Written:** 2026-08-11
**Binding constraint #6 compliance:** every path and `#include()` string below is derived from each
fixture's `conf.py` list and `.rst` toctree, read literally, against the DECISIONS recorded in
`47-CONTEXT.md` (D-01..D-09) and the measured Typst `#include()` semantics recorded in
`47-RESEARCH.md` (Pattern 2 / Pitfall 3). **No builder was run to produce this document.** The
"CURRENT (unfixed) output" tables are derived from `47-RESEARCH.md`'s own directly-measured
pre-fix evidence (its Pitfall 1/2/5 sections and Summary), not from a fresh build either — that
research was captured against the unfixed tree in a prior session and is treated here as a
citation, not a new measurement.

---

## Reversal notice

**OUT-01 is a deliberate reversal of Phase 44's D-05, D-06 and D-07.** Those three decisions
(v0.7.1, `_resolve_output_stem()`/`_directory_preserving_relpath()`) rejected any path component
in a `typst_documents` target name, truncated the target to its basename, and force-relocated a
nested docname's output into its own docname-derived directory regardless of what the target
actually said. Phase 47's OUT-01 reverses all three of these: a target is now a path relative to
the output directory — a bare name (`"manual.typ"`) writes at the output root, and an explicit
path (`"manuals/guide.typ"`) writes exactly where written, with no truncation and no forced
relocation. **The existing `_resolve_output_stem()`/`_directory_preserving_relpath()` guard code
implementing D-05/D-06/D-07 is therefore not sacred** — ROADMAP.md's own instruction for this
phase is to disentangle OUT-02's surviving security terms from the reversed separator-membership
term (see `47-RESEARCH.md` Pitfall 4), not to preserve the old guard's behavior. OUT-02 keeps the
three escape-rejection terms (`..` segments, absolute paths, drive-qualified paths) — only the
"any path component at all is rejected" term is reversed.

---

## Fixture 1: `two_layer_root_master_gate`

**Source read literally:** `conf.py` — one docname `index` (root doc, no toctree children);
`typst_documents = [("index", "manual.typ", "Root Master Gate", "Probe Author")]`.
`index.rst` body carries `ROOT-BODY-MARKER-AAA`.

### Expected (GREEN, post-fix) emitted-file table

| Logical role | Outdir-relative path | Template applied? | `#include()` argument (wrappers only) |
|---|---|---|---|
| Content (docname `index`) | `index.typ` | No (D-06 preamble only) | n/a |
| Wrapper (entry `index`→`manual.typ`) | `manual.typ` | Yes | `"index.typ"` |

**Derivation arithmetic:** the target `"manual.typ"` carries no path separator, so per OUT-01 it
resolves at the output root: `outdir/manual.typ`. The wrapper's resolved directory is therefore
`""` (the outdir root itself). `compute_content_include_path(wrapper_resolved_dir="", content_path="index.typ")`
= `posixpath.relpath("index.typ", start=".")` = `"index.typ"` — no `../` needed since both files
sit at the outdir root. The wrapper's template import (for the outdir-root `_template.typ`, via
the unchanged depth-only `_compute_template_import_path()`) is `"_template.typ"` (depth 0).

### Current (unfixed) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| Single file (docname `index`, is-master) | `manual.typ` | `_resolve_output_stem("index")` returns `"manual"` (target has no separator, not guarded); `_is_master_document("index")` is `True`, so the FULL template is applied directly to this one file — there is no separate `index.typ` content file today, because the pre-phase model writes exactly one file per docname under its resolved stem. `manual.typ` therefore contains both the template application AND `ROOT-BODY-MARKER-AAA` in one file. |

---

## Fixture 2: `two_layer_nested_master_gate`

**Source read literally:** `conf.py` — docnames `index` (root doc, toctree lists `guide/index`) and
`guide/index`; `typst_documents = [("index", "outer.typ", "Outer Master", "Probe Author"),
("guide/index", "manuals/guide.typ", "Nested Master", "Probe Author")]`. `index.rst` body carries
`OUTER-PROSE-MARKER`; `guide/index.rst` body carries `GUIDE-BODY-MARKER`.

### Expected (GREEN, post-fix) emitted-file table

| Logical role | Outdir-relative path | Template applied? | `#include()` argument (wrappers only) |
|---|---|---|---|
| Content (docname `index`) | `index.typ` | No (D-06 preamble only) | n/a — but its own BODY carries the toctree's `#include("guide/index.typ")`, per Corpus migration rule R5 below |
| Content (docname `guide/index`) | `guide/index.typ` | No (D-06 preamble only) | n/a |
| Wrapper (entry `index`→`outer.typ`) | `outer.typ` | Yes | `"index.typ"` |
| Wrapper (entry `guide/index`→`manuals/guide.typ`) | `manuals/guide.typ` | Yes | `"../guide/index.typ"` |

**Derivation arithmetic (the nested case, shown explicitly per the plan's instruction):** the
second entry's target `"manuals/guide.typ"` carries a path — under OUT-01 this resolves exactly
where written: `outdir/manuals/guide.typ`. The wrapper's resolved directory is `"manuals"`. The
content file for docname `guide/index` sits, unconditionally and independently of any wrapper's
target (COMP-01/OUT-03), at `outdir/guide/index.typ`. Therefore:

```
compute_content_include_path("manuals", "guide/index.typ")
    == posixpath.relpath("guide/index.typ", start="manuals")
    == "../guide/index.typ"
```

And the template import from that same wrapper directory (`"manuals"`) back to the outdir-root
`_template.typ` is:

```
posixpath.relpath("_template.typ", start="manuals") == "../_template.typ"
```

(Both computed and confirmed with `python3 -c "import posixpath; ..."` against the stdlib
`posixpath.relpath` this task's own execution — not against any emitter, per the plan's "no
builder run" constraint; `posixpath` is a pure path-string library with no filesystem or Typst
dependency.)

The first entry's wrapper (`outer.typ`, bare target, resolves at the outdir root) includes its own
entry's content file: `compute_content_include_path("", "index.typ") == posixpath.relpath("index.typ", start=".") == "index.typ"`.

The OUTER content file's own body (not its wrapper) carries the toctree-generated
`#include("guide/index.typ")` — this is the SAME docname-to-docname include computation the
translator has always performed for toctree children (`visit_toctree`), now correct because
`guide/index`'s content file is unconditionally at its docname-derived path `guide/index.typ`
regardless of what its OWN wrapper's target says. This is exactly the fix for B-1 (COMP-03): the
mismatch that produced `file not found` was between a docname-derived include path and a
target-derived actual file location; once content files are always docname-derived, that mismatch
cannot occur.

### Current (unfixed) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| Single file (docname `index`, is-master) | `outer.typ` | Target `"outer.typ"` has no separator, not guarded; resolves cleanly. Full template applied. Body contains `OUTER-PROSE-MARKER` plus the toctree's docname-derived `#include("guide/index.typ")`. |
| Single file (docname `guide/index`, is-master) | `guide/guide.typ` | Target `"manuals/guide.typ"` HAS a separator — the OUT-01-reversed `is_guarded` term trips, `_resolve_output_stem` warns (`"a path is not supported in a typst_documents target name: 'manuals/guide.typ' -- using 'guide' instead"`) and falls back to the basename `"guide"`; `_directory_preserving_relpath` (Phase 44 D-05/D-06/D-07) then force-relocates that basename into the DOCNAME's own directory, `guide/`, giving the physical path `guide/guide.typ`. Full template applied; body contains `GUIDE-BODY-MARKER`. |

**Measured pre-fix consequence (cited from `47-RESEARCH.md` Pitfall 1, this session's own prior
measurement, not re-run here):** `outer.typ`'s `#include("guide/index.typ")` names a file that
does not physically exist (`guide/guide.typ` exists instead), so `typst.compile("outer.typ", root=outdir)`
raises `TypstError('file not found (searched at .../guide/index.typ)')` — the classic-`TypstError`
RED shape COMP-03's gate test asserts. B-2 (COMP-04)'s mid-body template re-expansion defect is a
SEPARATE, subsequent defect that only becomes independently observable once B-1's file-not-found
is worked around (`47-RESEARCH.md` Pitfall 2 isolated it with a copied-file workaround); on this
fixture, as configured, the compile fails at B-1 before B-2 can manifest. Both are closed by the
same content/wrapper split: COMP-03's gate asserts the compile SUCCEEDS post-fix, and COMP-04's
gate asserts (once it does) that the resulting PDF's page-text sequence carries no second
title-page-shaped block or second `"Contents"` heading between `OUTER-PROSE-MARKER` and
`GUIDE-BODY-MARKER`.

---

## Fixture 3: `bld02_duplicate_target_gate`

**Source read literally:** `conf.py` — docnames `index` (toctree lists `other`) and `other`;
`typst_documents = [("index", "manual.typ", "Index Master", "Probe Author"), ("other", "manual.typ",
"Other Master", "Probe Author")]` — both entries target the identical string `"manual.typ"`.
`index.rst` body carries `INDEX-MASTER-MARKER-AAA`; `other.rst` body carries
`OTHER-MASTER-MARKER-BBB`.

### Expected (GREEN, post-fix) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| — | — | **No file is written at all.** The unified pre-write validator (D-02/D-03) builds one logical-file-to-physical-path map before any write; both entries' wrapper paths casefold to the identical key `"manual.typ"`, so the validator raises a single `ExtensionError` naming BOTH entries (`index` and `other`) before either write begins. D-02's no-partial-write rule means neither `manual.typ`, nor the two content files `index.typ`/`other.typ`, nor `_template.typ` exist in the build directory. |

### Current (unfixed) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| Single surviving file | `manual.typ` | Both docnames resolve stem `"manual"` (no separator, not guarded). `builder.py`'s write loop iterates `sorted(docnames)`, so `"index"` is written first and `"other"` second — `"other"`'s write silently OVERWRITES `"index"`'s file at the same physical path, with no collision check (today's CR-01 only compares a target against `env.found_docs ∪ {"_template"}`, never against an already-resolved SIBLING target). The surviving `manual.typ` therefore carries the FULL template applied to docname `other`, containing `OTHER-MASTER-MARKER-BBB`; `INDEX-MASTER-MARKER-AAA` is gone entirely — silently dropped, no warning, exit 0. (Cited from `47-RESEARCH.md`'s own BLD-02 reproduction this session: "exit 0, `manual.typ` contains `OTHER-MASTER-MARKER-BBB` (count 1) but NOT `INDEX-MASTER-MARKER-AAA` (count 0), no collision warning anywhere in stdout/stderr".) |

---

## Fixture 4: `bld03_self_collision_gate`

**Source read literally:** `conf.py` — one docname `index`;
`typst_documents = [("index", "index.typ", "Self Collision Gate", "Probe Author")]` — the target's
stem is identical to the docname itself. `index.rst` body carries `SELF-COLLISION-BODY-MARKER`.

### Expected (GREEN, post-fix) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| — | — | **No file is written.** Content file `index.typ` (docname-derived, COMP-01, always exists) and wrapper file `index.typ` (entry `index`→`index.typ`, resolves to the SAME physical path under OUT-01's bare-target-at-root rule) collide — this is D-01's canonical self-collision case. The unified validator raises `ExtensionError` before any write. |

### Current (unfixed) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| Single file (docname `index`, is-master) | `index.typ` | `_resolve_output_stem("index")` returns `"index"` unmodified: target `"index.typ"` has no separator (not guarded by the OUT-01-reversed term), and the CR-01 collision check at `builder.py:275` explicitly reads `effective != docname` — since `effective == "index" == docname`, this branch is the `effective != docname` check's FALSE case, so no collision is flagged and no fallback triggers. Build succeeds, exit 0, single `index.typ` with the full template applied and `SELF-COLLISION-BODY-MARKER` in its body. This is precisely the "builds successfully in v0.7.x, stops building" configuration D-01 names. |

---

## Fixture 5: `bld04_case_collision_gate`

**Source read literally:** `conf.py` — docnames `index` and `manual` (deliberately NOT linked by
any toctree — see the fixture's own `conf.py` comment for why: a toctree edge here would
confound BLD-04's case-collision defect with the unrelated B-1 docname/target-mismatch defect);
`typst_documents = [("index", "index-wrapper.typ", "Index Wrapper Master", "Probe Author"),
("manual", "Manual.typ", "Manual Master", "Probe Author")]` — the second entry's target differs
from the docname `manual` only by the capital `M`. `index.rst` body carries
`INDEX-WRAPPER-BODY-MARKER`; `manual.rst` body carries `MANUAL-BODY-MARKER`.

### Expected (GREEN, post-fix) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| — | — | **No file is written for the `manual`-related pair.** Docname `manual`'s own content path is `manual.typ`; the second entry's wrapper target is `Manual.typ`. D-05 mandates `casefold()`-normalized comparison on EVERY platform: `"manual.typ".casefold() == "Manual.typ".casefold()`, so these are the SAME logical-to-physical map key — a collision, even though Linux's case-sensitive filesystem would treat them as two different paths if written. The unified validator raises `ExtensionError` before any write; per D-02 this aborts the WHOLE build (including the unrelated `index`/`index-wrapper.typ` pair), not just the colliding entries. |

### Current (unfixed) emitted-file table

| Logical role | Outdir-relative path | Notes |
|---|---|---|
| Single file (docname `index`, is-master) | `index-wrapper.typ` | Target has no separator, not guarded; resolves cleanly. Full template applied; body contains `INDEX-WRAPPER-BODY-MARKER` only — no toctree include (the fixture deliberately does not link `manual` from `index`'s toctree). |
| Single file (docname `manual`, is-master) | `Manual.typ` | Target `"Manual.typ"` has no separator, not guarded. CR-01's `effective != docname` check compares the RAW strings `"Manual" != "manual"` — TRUE (they differ as plain strings on this case-sensitive comparison), so no collision is flagged even though `_resolve_output_stem` performs no `casefold()` anywhere. Build succeeds, exit 0, no warning. Full template applied; body contains `MANUAL-BODY-MARKER`. Two DISTINCT files coexist on Linux's case-sensitive filesystem (`index-wrapper.typ` and `Manual.typ`) — this is precisely `47-RESEARCH.md` Pitfall 5's measured gap: the same configuration would silently overwrite one file with the other on Windows/macOS's default case-insensitive filesystem, invisibly to Linux CI. |

---

## Corpus migration rules

The existing 87 fixture projects and 68 test modules this phase does NOT touch are migrated by
plans 47-04 through 47-08, against the authority of the two rules below — both derived from the
locked decisions (D-01..D-09) and this document's own derivations, not from any emitter's output.

### Assertion-class relocation table (R1–R5)

| Rule | Assertion class | Where it reads after the split |
|------|------------------|-------------------------------|
| R1 | Translator body markup (the doctree-derived Typst source a `visit_*`/`depart_*` method emits — prose, tables, figures, code blocks, admonitions, etc.) | Stays on the docname-named **content** file (e.g. `index.typ` for docname `index`) — content files unconditionally carry the translated body under D-06's preamble, per COMP-01/OUT-03. |
| R2 | Template application (a template import such as `#import "@preview/..."` for the TEMPLATE itself — not the D-06 four package imports, which stay on content — a `#show:` application of the project/template function, `title`/`author` parameters, the `#outline()` call) | Moves to the **wrapper** file (e.g. `manual.typ`, `outer.typ`) — wrappers carry the FULL template application per COMP-02/D-08, content files carry none. |
| R3 | A `typst.compile()` call targeting a complete, self-contained document | Targets the **wrapper** file — only wrappers carry a template application, so only a wrapper compiles to a standalone, correctly-titled document; compiling a content file directly would produce an untitled, template-less fragment. |
| R4 | A `-b typstpdf` produced PDF (`typst.compile()`'s `output=` result, or the builder's own PDF write) | Is the **wrapper**'s `.pdf` (Claude's Discretion in `47-CONTEXT.md`: `typstpdf` compiles wrappers only, matching today's "only master documents are compiled" rule). |
| R5 | A toctree `#include()` emission (the Typst source a parent document's `visit_toctree` emits to pull in a child docname) | Stays on the **content** file — this is a docname-to-docname computation (parent content → child content), unaffected by either document's own wrapper target, exactly as demonstrated in Fixture 2's derivation above. |

### Fixture de-collision rule

Once OUT-01 makes a target a literal output path (reversing the Phase 44 truncation that
previously made `[("index", "index.typ", ...)]`-shaped configs "safe" by accident), any EXISTING
fixture whose `typst_documents` entry's resolved target path `casefold()`-equals a docname's own
content path (self-collision, D-01), or where two entries resolve to one target (BLD-02, D-03),
must have that entry's element `[1]` (the target) changed to a distinct name. **The canonical
replacement is `"master.typ"`**, unless the fixture's own stated purpose already names its target
for a reason unrelated to the collision (e.g. a fixture specifically testing template-collision
behavior against `_template.typ`), in which case a purpose-specific distinct name is chosen instead
and the reason is written into that fixture's own `conf.py` comment block, following the
load-bearing-facts convention `tests/fixtures/derived_docname_collision_gate/conf.py` establishes.
**Elements `[0]` (docname), `[2]` (title), `[3]` (author) and `[4]` (the reserved fifth element,
per D-09) are never changed** by this rule — only `[1]` (the target) is ever touched, and only when
its current value collides under the new casefold-normalized, path-as-path comparison rule.
