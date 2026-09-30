# Architecture Research: v0.7.0 Style-Module Integration

**Domain:** Sphinx→Typst compiler extension (subsequent-milestone integration research, not
greenfield)
**Researched:** 2026-07-29
**Confidence:** HIGH (every claim below is a direct file:line read of the current repo state,
several confirmed by executing docutils/Sphinx directly — see per-section notes)

## Verdict Summary

- A new bundled Typst module (call it `typsphinx/templates/_typsphinx.typ` — must live under
  `typsphinx/templates/` to ride the existing package-data glob, `pyproject.toml:71`) is written
  **unconditionally**, once per build, from a new builder method modeled on but structurally
  **not identical to** `_write_template_file()` — because unlike `_template.typ` it must exist
  even on the `typst_package`-alone route (§1).
- Its import must be injected at **two** independent emission sites in `writer.py`'s
  `translate()` (§2) — the master path goes through `TemplateEngine.render()`
  (`template_engine.py:571-658`) and the included path is the inline import-prelude
  (`writer.py:149-166`) — because `TypstTranslator` emits calls into this module from
  `self.body`, and `self.body` is identical code whether the document is a master or an
  `#include()`d child.
- The three in-repo custom templates are **verified safe by construction**: nothing in
  `builder.py`/`template_engine.py` ever parses or rewrites `typst_template` content — it is
  loaded as an opaque string (`_try_load_file`, `template_engine.py:719-733`) and only the
  function name `project` is imported from it by name (`template_engine.py:624`,
  `writer.py`'s `_write_template_file` calls the same engine). The one real collision risk is
  **not** with the custom templates themselves but with a hypothetical style-module design that
  re-imports `@preview/gentle-clues` internally — flagged as an open design question in §3.
- `desc_*`/`field_*`/`rubric`/admonition redesign touches five interacting shared protocols
  (§4); the admonition helper pair is the safest per-node seam, `field_body`'s inline-concat
  context is the most fragile.
- Citations need **no footnote-style pre-pass** — confirmed by executing docutils directly
  (§6) — because Typst's `link(<label>, ...)` (already used for `:ref:`-style xrefs) resolves
  against the WHOLE compiled document regardless of source order, unlike `footnote()`, whose
  stdlib API forces the body to be supplied at the call site, which is what made the FN-01
  pre-pass necessary for footnotes specifically.

---

## 1. Where the style module is written, and by whom

### The existing `_template.typ` write path (traced)

`TypstBuilder.prepare_writing()` (`typsphinx/builder.py:318-332`) is the once-per-build hook —
called from `write()` (`builder.py:365`) before any document is translated. It does exactly two
things: construct `self.writer = TypstWriter(self)`, then call `self._write_template_file()`.

`_write_template_file()` (`builder.py:521-592`) is **conditionally skipped**:

```python
# builder.py:565-566
if typst_package and not raw_template_path:
    return
```

i.e. it writes `_template.typ` (`builder.py:588`) **only when a custom `typst_template` is
configured** (with or without a package — D-03 lets `typst_template` win). On the
package-alone route (`typst_package` set, `typst_template` unset) it is never written, because
`writer.py:288-291` also skips computing an import path for it in that case
(`template_file = None`). This conditional-skip is *load-bearing* for `_template.typ` — the
package IS the template in that route, so importing a nonexistent `_template.typ` would abort
the compile (this exact bug is documented as the "Unconditional Shared Template Import" anti-
pattern in `.planning/codebase/ARCHITECTURE.md:262-268`).

### Why the style module CANNOT reuse this same conditional

The style module is a different kind of dependency. `_template.typ` supplies the `project()`
template *function* — only relevant to whichever code path calls
`#show: project.with(...)`. The style module instead supplies helper functions that
**`TypstTranslator`'s node handlers call directly while emitting `self.body`** (e.g. a
redesigned `visit_desc_signature` emitting `#api-signature(...)` instead of raw `strong({...})`).
`self.body` is generated identically regardless of routing — master-with-custom-template,
master-with-bundled-default, master-with-package-alone, and every **included** document (which
never touches `TemplateEngine` at all, see §2) all run the same `TypstTranslator` over the same
node types. Therefore the style module's import cannot be gated on `typst_template`/
`typst_package` the way `_template.typ` is: **it must be written and importable in every
routing branch**, including the one branch (`typst_package` alone) where `_write_template_file`
deliberately no-ops.

### Concrete new code path

Add a sibling method, e.g. `_write_style_module_file()`, called unconditionally from
`prepare_writing()` right alongside the existing call:

```python
# builder.py:318-332, extended
def prepare_writing(self, docnames: Set[str]) -> None:
    self.writer = TypstWriter(self)
    self._write_template_file()        # unchanged, still conditional
    self._write_style_module_file()    # NEW, unconditional
```

Implementation shape mirrors `_write_template_file`'s file-read-and-write tail
(`builder.py:584-592`) but with no `typst_package`/`typst_template` branching: read the bundled
module's source via `Path(__file__).parent / "templates" / "_typsphinx.typ"` (same directory
`TemplateEngine.get_default_template_path()` already resolves via `template_engine.py:260-272`,
so no new search-path concept is needed) and write it verbatim to
`path.join(self.outdir, "_typsphinx.typ")`.

**Packaging note (load-bearing):** `pyproject.toml:71` — `"typsphinx" = ["templates/*.typ"]` —
is the *only* package-data glob in the project. The new module file must physically live inside
`typsphinx/templates/` (not a new `typsphinx/styles/` directory) or the glob needs a matching
edit, or the module silently ships missing from the built wheel while local dev (running from a
source checkout) keeps working — the exact "green in dev, broken once packaged" failure shape
this project has hit before with `@preview` version drift.

### Nested master documents and relative-path resolution

`_template.typ` is always written at the **outdir root** (`builder.py:588`), regardless of
where any given master document lives (`api/index` vs `index`). A master's import path is
computed *purely from its own docname's directory depth* by
`TypstWriter._compute_template_import_path()` (`writer.py:73-119`):

```python
# writer.py:118-119
depth = len(PurePosixPath(docname).parent.parts)
return "".join(["../"] * depth) + "_template.typ"
```

This function is deliberately depth-based rather than a docname-to-docname relativizer — the
docstring (`writer.py:74-117`) records the CR-01 defect this replaced: relativizing against a
synthetic `"_template"` sentinel docname could collide with a real directory literally named
`_template`. **The style module needs the identical treatment**, and for a stronger reason than
`_template.typ` does: it must resolve correctly not just for masters but for **every included
document at any nesting depth**, because included documents get their import prelude
independently (see §2) and are never routed through `_compute_template_import_path` today (that
function is currently called from only the master branch, `writer.py:291`). The clean move is
to generalize `_compute_template_import_path` into a filename-parameterized helper (e.g.
`_compute_outdir_relative_import_path(docname, filename)`) reusable from both the master branch
and the included-document branch — same depth arithmetic, different target filename
(`_template.typ` vs `_typsphinx.typ`), avoiding a second depth-computation implementation
diverging from the first.

---

## 2. Where the import gets emitted — both writer.py paths

`TypstWriter.translate()` (`writer.py:121-292`) is the single control point, and it branches on
`is_master = self._is_master_document(docname)` at `writer.py:147`. **Both branches must gain
the style-module import**, because both branches assemble a complete standalone `.typ` file
that `self.body` (produced identically by `TypstTranslator` in both cases,
`writer.py:131-134`) is appended into.

### Included-document path (writer.py:149-166)

Today this branch hardcodes a fixed import prelude with **no filesystem-relative import** at
all — the four imports are `@preview` package references, resolved by Typst's package manager,
not by path:

```python
# writer.py:153-163 (current)
imports = []
imports.append("// Essential imports for included document")
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.10": *')
imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.3.1": *')
imports.append("")
imports.append("// Initialize codly")
imports.append("#show: codly-init.with()")
imports.append("#codly(languages: codly-languages)")
imports.append("")
self.output = "\n".join(imports) + "\n" + body
```

The new style-module import is a **filesystem path** import, unlike the four `@preview` lines —
so it needs the depth-aware helper from §1, computed from `docname` (already in scope as the
parameter to this whole method chain via `self.builder.current_docname`, `writer.py:144`), and
inserted into this `imports` list, e.g. immediately after the four `@preview` lines and before
`self.output = ...` is assembled. **Ordering constraint:** it must come *before* `body` is
appended (trivially true here — the whole `imports` block already precedes `body` at
`writer.py:165`), and it should come *after* the `@preview` imports if the style module's own
top-level code references any of `codly`/`mitex`/`gentle-clues` names — see §3 for why that
matters (module scoping).

### Master-document path (writer.py:168-292, through TemplateEngine.render())

This branch never assembles `self.output` directly — it delegates everything after body-content
gathering to `template_engine.TemplateEngine.render()` (`writer.py:292` →
`template_engine.py:571-658`). `render()` is where the file's full import section is actually
built:

```python
# template_engine.py:594-619 (current)
package_import = self.generate_package_import()          # @package import, if typst_package set
...
will_inline_default_template = not template_file and not self.typst_package
if not will_inline_default_template:
    output_parts.append("// Essential package imports")
    output_parts.append('#import "@preview/codly:1.3.0": *')
    ... (4 @preview imports + codly-init block) ...

if template_file:
    template_func = self.typst_template_function_name or "project"
    output_parts.append(f'#import "{template_file}": {template_func}')
else:
    if not self.typst_package:
        template = self.load_template()          # inlines base.typ, which ITSELF
        output_parts.append(template)             # carries the same 4 @preview imports

output_parts.append(f"#show: {template_func}.with(")
... params ...
output_parts.append(body)
```

**Critical asymmetry vs. the `@preview` imports:** the hoisted block at `template_engine.py:610-
619` is deliberately gated by `will_inline_default_template` — it is skipped precisely when the
bundled `base.typ` is about to be inlined, because `base.typ` *itself* already contains those
four `#import` lines (`typsphinx/templates/base.typ:7-19`), and duplicating them would double-
import the same package (flagged explicitly in the code comment, `template_engine.py:606-608`,
as avoiding CR-01 duplicate-line churn). **The new style module is not inside `base.typ`** (it
is a separate file, §1), so this same exception must **not** apply to it — the style-module
import has to be emitted in **all three** cases: custom `template_file` set, bundled-default
inlined, and `typst_package`-alone. Concretely this means adding a *new*, unconditionally-
emitted `output_parts.append(...)` line to `render()` — placed before the `#show: ...` call
(`template_engine.py:636`) since translator-emitted calls in `body` (appended at
`template_engine.py:656`) need the module's names bound by the time Typst reaches that source
position, and `#import` bindings are available for any code after them in the same file
regardless of where `#show:` sits.

**Ordering recap (both paths):** style-module import can be placed either immediately before or
after the four `@preview` imports — Typst import order among *unrelated* files does not matter
for compilation — but it must precede any code that calls into it, i.e. it must precede
`#show: project.with(...)` and precede `body`. Placing it *after* the `@preview` block is the
simpler convention to hold (groups "third-party" vs. "typsphinx's own" imports), and matters
only if the module itself needs a `@preview` name resolved from the **outer** file's scope,
which per §3 it can't rely on anyway.

**Function needed:** `render()`'s signature (`template_engine.py:571-573`,
`render(self, params, body, template_file=None)`) does not currently receive a style-module
import path at all — the caller (`writer.py:292`) will need to pass one (or `render()` computes
it itself from a `docname` it does not currently receive as a parameter — passing it in from
`writer.py`, mirroring how `template_file` is already computed there at `writer.py:291`, is the
lower-friction change since `TypstWriter.translate()` already has `docname` in scope at
`writer.py:144`).

---

## 3. The override story — verified, plus one real open risk

### Verified: custom-template content is never touched

Both write paths that matter — `builder.py:_write_template_file()` (writes `_template.typ` to
disk) and `writer.py:translate()`'s master branch (imports it) — load a custom template purely
as opaque bytes:

- `TemplateEngine.resolve_template()` (`template_engine.py:274-330`) walks
  explicit-path → search-path → bundled-default priority and returns raw file content via
  `_try_load_file()` (`template_engine.py:719-733`), a bare `open(...).read()`.
- `render()` never parses that content — it either imports the function name `project` from it
  by reference (`template_engine.py:624`, when `template_file` is set) or, for the bundled-
  default-inline case only, string-concatenates it verbatim into `output_parts`
  (`template_engine.py:630-631`).

So a custom template's own file on disk is **never rewritten, never re-parsed, never string-
substituted**. Since the style module is written to a *different* file (`_typsphinx.typ`, not
`_template.typ`), and its import is injected as a *new, additive* line in the generated master
`.typ` (§2) rather than by editing the custom template's source, the three in-repo custom
templates —

- `examples/advanced/_templates/custom.typ`
- `docs/source/_typst/custom_template.typ`
- `examples/charged-ieee/approach2/source/_templates/_template.typ`

— compile with **byte-identical own content** before and after this milestone. Each was read in
full (see files list) and confirmed to declare only its own `@preview` imports (all three
independently import the same four packages at the same pinned versions, guarded by
`tests/test_preview_version_sync.py`'s `test_example_templates_match_canonical_versions`) plus,
for the two non-`approach2` templates, their own `#let project(...)` definition. None of the
three imports anything from a file named `_typsphinx.typ` — they don't need to, because the
NEW `#import "_typsphinx.typ": *` line lives in the *generated* master `.typ` file (added by
`render()`, §2), not inside the custom template file itself.

### Where a real collision *could* occur — module scoping (flag for planning)

The one non-obvious risk, confirmed by reading how Typst resolves imports (not by executing
typst — no typst CLI is installed in this environment; this is inferred from the existing
codebase's own documented understanding of Typst import semantics, e.g.
`translator.py:3287-3320`'s label-syntax notes and `template_engine.py:606-608`'s explicit
double-import-avoidance comment): **a `#import`ed Typst file's own top-level code runs in that
file's own lexical scope, not the importing file's scope.** Concretely: if the style module's
own Typst source calls `info(...)` (a `gentle-clues` function) to help render a redesigned
admonition, that call resolves against whatever `_typsphinx.typ` itself has imported — **not**
against the `#import "@preview/gentle-clues:1.3.1": *` line that already exists in the outer
`.typ` file (`template_engine.py:614` / `writer.py:157` / `base.typ:17`). If the style module
needs `gentle-clues`/`codly`/`mitex` internally, it would need to `#import` them itself,
independently — which would make it a **fourth** site carrying the same four version pins that
`tests/test_preview_version_sync.py` (`tests/test_preview_version_sync.py:1-34`) currently
enforces across exactly three sites (`writer.py`, `template_engine.py`, `templates/base.typ`).
This is explicitly the class of hazard the milestone brief says must NOT be introduced
("the `@preview` package count stays at four... this milestone creates no fifth version-
lockstep site — the new module is bundled, not fetched" — `.planning/PROJECT.md:89-92`); that
sentence guarantees the module itself isn't a fifth *fetched* package, but does not by itself
prevent the module from becoming a fourth *internal* site re-declaring the same four existing
pins.

**Recommendation for requirements/roadmap:** scope the style module to typography primitives
that need **no** `@preview` package dependency at all (monospace signature blocks, hanging-
indent bodies, two-column field tables, nesting indent — none of gentle-clues/codly/mitex is
needed for these). Keep admonition rendering's actual `info(`/`warning(`/etc. calls exactly
where they are today (`translator.py:_visit_admonition`/`_depart_admonition`,
`translator.py:4106-4164`), which already execute in the OUTER file's scope where those names
are already bound — i.e. redesign admonition *typography* (spacing/title treatment) without
routing the gentle-clues call itself through the style module. If a later requirement genuinely
needs the module to wrap gentle-clues calls, that is a version-sync-surface decision that should
be made explicitly (and `test_preview_version_sync.py` extended to a fourth site) rather than
falling out of an implementation detail.

---

## 4. Translator methods in scope and the shared protocols they touch

### `__init__`-declared state relevant to this milestone (`translator.py:66-262`)

| Protocol | State variables | Declared at |
|---|---|---|
| Paragraph separation | `in_paragraph`, `paragraph_has_content` | `translator.py:129-130` |
| List-item separation | `in_list_item`, `_list_item_stack`, `list_item_needs_separator`, `is_first_list_item` | `translator.py:131-145` |
| Code-mode concat contexts | `in_desc_parameter`/`_desc_parameter_has_content` (desc-specific), `_in_field_body`/`_field_body_has_content`/`_field_body_stack` (field-specific), `_in_link`/`_link_has_content`, `_in_attribution`, `_in_term`, generic `_inline_concat_stack` + `_enter_inline_concat_element()`/`_exit_inline_concat_element()` (`translator.py:977-1030`, referenced at `translator.py:1216-1220`) | `translator.py:152-229` |
| Buffer-swap for titles/captions | `_saved_body_for_figure_caption`, `_saved_body_for_admonition_title`, `_in_admonition_title`, `_pending_admonition_title`, `_title_section_ids` | `translator.py:112-247` |
| Id-anchor emission | `_emit_id_anchors()` (`translator.py:331-393`), `_namespace_label()`/`_sanitize_label()` (`translator.py:3287-3380`) | shared helper, not per-node state |
| Forced hard breaks | `_emit_forced_break()` (`translator.py:289-317`) | shared helper |

### Handler inventory in scope

**`desc_*` family** (`translator.py:4619-5134`):

| Method | Current emission | Shared protocol touched |
|---|---|---|
| `visit_desc`/`depart_desc` (4619, 4648) | `_emit_id_anchors`; resets `_is_first_desc_signature`; `depart` emits unconditional `parbreak()` via `_emit_forced_break` | id-anchor; forced-break |
| `visit_desc_signature`/`depart_desc_signature` (4664, 4690) | delegates to `visit_strong`/`depart_strong` (dummy node trick); emits sibling `linebreak()` via `_emit_forced_break`; emits `[#metadata(none) <id>]` anchors per id | forced-break; id-anchor; **borrows the `strong` inline-block protocol wholesale** |
| `visit_desc_returns` (4724) | `text(" -> ")`, guarded by `in_list_item`/`list_item_needs_separator` | list-item separation |
| `visit_desc_signature_line`/`depart` (4743, 4763) | per-line `linebreak()`, first-line suppressed via `_is_first_desc_signature_line` | forced-break, but manually inlined rather than via `_emit_forced_break` (predates the helper — worth folding in during the redesign) |
| `visit_desc_content`/`depart_desc_content` (4767, 4773) | **both `pass`** — this is defect (2) from PROJECT.md verbatim | none currently — this is exactly the seam that needs the new hanging-indent wrapper |
| `visit_desc_inline`/`depart` (4777) | `pass` (deliberately, to suppress `strong()`, comment at 4782-4787) | none |
| `visit_desc_annotation`/`depart` (4794) | `pass`/`pass` | none |
| `visit_desc_addname`/`visit_desc_name` (4810, 4820) | `pass`; `depart_desc_name` sets `list_item_needs_separator` | list-item separation |
| `visit_desc_parameterlist`/`depart` (4832, 4851) | opens `text("(") + `, manages `in_desc_parameter`/`_desc_parameter_has_content`, closes `text(")")` | **desc-specific concat context** (a THIRD hand-rolled concat pattern alongside the field-body one and the generic `_inline_concat_stack`) |
| `visit_desc_parameter`/`depart` (4859, 4867) | `depart` appends `+ text(", ")` when a following sibling exists | desc-parameter concat |
| `visit_desc_optional`/`depart` (4878, 4895) | literal `[`/`]` bracket wrap, reuses `_desc_parameter_has_content` | desc-parameter concat |
| `desc_sig_keyword`/`desc_sig_space`/`desc_sig_name`/`desc_sig_punctuation`/`desc_sig_operator` (5096-5134) | all `pass`/`pass` | none — these are exactly where monospace-run styling for signature TEXT needs to attach, since today the wrapping `strong()` from `visit_desc_signature` is the ONLY styling any of this text gets |

**`field_list`/`field`/`field_name`/`field_body`** (`translator.py:4900-5033`):

| Method | Current emission | Shared protocol touched |
|---|---|---|
| `visit_field_list` (4900) | conditional leading `\n` if `in_list_item` and separator pending | list-item separation |
| `depart_field_list` (4916) | trailing `\n`; sets `list_item_needs_separator` | list-item separation |
| `visit_field`/`depart_field` (4929, 4935) | `depart` emits `\ntext("  ")\n` inter-field spacer **only when** `_last_field_body_was_inline` and a following sibling exists | reads `_last_field_body_was_inline`, set by `depart_field_body` |
| `visit_field_name`/`depart_field_name` (4960, 4976) | opens `strong(`, temporarily clears `in_paragraph`, closes with `+ text(": "))\n` | paragraph-state save/restore; this IS the "bold inline label" defect (4) from PROJECT.md |
| `visit_field_body`/`depart_field_body` (4989, 5020) | detects **all-inline** vs **block** body shape; activates `_in_field_body` concat context only for the all-inline case; pushes/pops `_field_body_stack` | field-body concat context (own protocol, distinct from desc-parameter's) |

**`rubric`** (`translator.py:5034-5076`): delegates open/close to `visit_strong`/`depart_strong`
(dummy-node trick, same as `desc_signature`); `depart_rubric` emits an **unconditional**
`linebreak()` via `_emit_forced_break`, with an explicit extra `add_text("\n")` first because
(per its own docstring, `translator.py:5067-5075`) `depart_strong`'s `})` carries no trailing
separator the way `depart_desc_signature`'s does — this asymmetry is exactly what let the
FID-04 rubric/next-line-merge bug through originally and would need to be re-derived if
`depart_strong`'s trailing-separator behavior changes as part of the redesign.

**`topic`/admonition helpers** (`translator.py:4106-4335`): `_visit_admonition`/
`_depart_admonition` is the single shared implementation behind 13 distinct
`visit_note`/`visit_warning`/`visit_tip`/.../`visit_admonition`/`visit_topic` wrappers
(`translator.py:4170-4335`). It opens a **code-mode content-block call**
(`f"{clue_type}({{"`, `translator.py:4140`) — i.e. it is NOT delegating to `visit_strong`'s
inline-block protocol the way `desc_signature`/`rubric` do; it has its own, simpler open/close
shape. Title handling is via the buffer-swap idiom in `visit_title`'s admonition-aware branch
(`translator.py:541-557`) — this is the **fourth** distinct buffer-swap consumer alongside
figure captions, table captions, and (per D-05) `.. contents::` topic titles, all sharing the
"swap `self.body` out, accumulate, swap back, wrap in `{...}`" pattern but each with its own
save/restore variable names (no shared helper function exists yet — worth extracting one if
the redesign adds a fifth buffer-swap consumer, e.g. a citation body).

### Which protocols are most likely to be disturbed

1. **The `strong()`-delegation trick** (`desc_signature`, `rubric` both call
   `self.visit_strong(dummy_strong)`/`self.depart_strong(dummy_strong)`) is the single highest-
   blast-radius seam: any change to `visit_strong`'s inline-block open/close shape
   (`translator.py:1203-1262`) — e.g. to stop emitting literal `strong({...})` and instead emit
   a new monospace-signature wrapper — simultaneously changes two unrelated node families that
   currently share it *for convenience*, not by design intent. The redesign should almost
   certainly **stop delegating** and give `desc_signature` its own open/close pair, decoupling
   it from `strong`'s general-purpose bold-inline behavior (which callers elsewhere, e.g. plain
   `**bold**` markup, still need unchanged).
2. **The desc-parameter concat context** (`in_desc_parameter`/`_desc_parameter_has_content`) is
   a hand-rolled third implementation of "join adjacent inline children with `+`" alongside the
   generic `_inline_concat_stack` machinery (`_enter_inline_concat_element`/
   `_exit_inline_concat_element`) and the field-body-specific `_in_field_body` context. A
   redesign that reworks parameter-list rendering (e.g. into a real hanging-indent parameter
   table) touches this concat context directly and should decide whether to fold it into the
   generic stack machinery rather than adding a fourth hand-rolled variant.
3. **`_last_field_body_was_inline`** cross-talk between `depart_field_body` and `depart_field`
   is a narrow, easy-to-silently-break coupling: any redesign of `field_body`'s emission shape
   that changes when/whether the all-inline detection fires will silently change whether
   `depart_field`'s inter-field spacer fires, without an obvious test failure signature (it's a
   whitespace-only change, not a compile fatal).
4. **Buffer-swap idiom proliferation**: if citation rendering (§6) or a redesigned admonition
   title needs its own buffer-swap, this is the fifth hand-copied instance of the same pattern
   — a natural, low-risk factoring opportunity (extract `_swap_body_buffer()`/
   `_restore_body_buffer()` helpers) that would reduce the redesign's own blast radius rather
   than expand it.

---

## 5. Suggested build order

Ordered by hard dependency, not narrative convenience — each step's own regression gate
(GATE-01 fixture, per the milestone's standing invariant) should be green before the next step
begins, since later steps assume the module import machinery already resolves.

1. **Style-module plumbing (additive, low blast radius).** Land `typsphinx/templates/_typsphinx.typ`
   as an *empty or near-empty* module (even a single comment + one placeholder function), the
   new `_write_style_module_file()` builder method (§1), and both import-injection sites in
   `writer.py`/`template_engine.py` (§2). This step touches **zero** `visit_*`/`depart_*`
   translator methods and produces byte-identical body content — its own regression gate is
   "every existing GATE-01/GATE-02 fixture still compiles and its body content is unchanged;
   the new `_typsphinx.typ` file appears in `outdir` and is importable from a master, an
   included doc, a custom-template master, and a package-alone master." This step is **required
   before any translator method below can call into the module** and should be the first phase.
2. **`desc_*`/`field_list` redesign (broad blast radius).** Depends on step 1 (needs real module
   functions to call). Internally sequence: (a) decouple `desc_signature`/`rubric` from the
   `visit_strong` delegation trick first (§4 finding 1) since it is a prerequisite for changing
   either independently without cross-breaking the other; (b) implement `desc_content`'s hanging
   indent (currently dead `pass`/`pass`, so this is pure addition, not modification of existing
   behavior); (c) implement nesting-depth-aware indentation for nested `py:method::`; (d)
   redesign `field_list`'s two-column layout. This is the highest-blast-radius step — it touches
   the desc-parameter concat context and invalidates GATE-01 fixture strings at scale (an
   accepted cost per PROJECT.md).
3. **Admonition/rubric/topic redesign (moderate blast radius, additive-shaped).** Can proceed in
   parallel with step 2 once step 1 lands, since `_visit_admonition`/`_depart_admonition` is
   structurally independent of the `desc_*` family (no shared state beyond the generic
   `in_list_item` protocol both already participate in). Sequence rubric's `depart_rubric`
   asymmetric-separator fix (§4, FID-04 note) together with this step since rubric shares the
   `visit_strong` delegation being decoupled in step 2(a) — these two should not land out of
   order relative to that decoupling, or rubric silently reverts to the old shared-strong shape.
4. **Citation support (additive, greenfield, independently landable).** No dependency on steps
   2-3 (citations render through the existing `link()`/`_emit_id_anchors` machinery, §6, not
   through desc/field/admonition machinery). Could land in parallel with step 2 once step 1 is
   done, or before it — the only shared dependency is the style-module plumbing from step 1 if
   the bibliography-list rendering is styled through the new module (a design choice, not a
   hard requirement — a first cut could render entirely with existing `list()`/`link()`
   primitives with zero module dependency).
5. **`visit_math_block` blank-line fix + `release.yml` CHANGELOG extraction.** Both are
   self-contained, unrelated to the module/translator work above (different files entirely:
   `visit_math_block` is a narrow single-method fix, `release.yml` is CI-only). Safe to land at
   any point, but grouping them at the end (their historical position in the milestone
   description) avoids interleaving unrelated diffs with the desc/field GATE-01 fixture churn
   from step 2.
6. **Release prep (version bump + CHANGELOG).** Standard final phase, depends on everything
   above being green.

**Explicit blast-radius call-outs:**
- **Safe/additive:** style-module plumbing (step 1), `desc_content` implementation (currently
  dead code), citation handlers (greenfield, no existing behavior to regress).
- **Broad blast radius:** `desc_signature`/`rubric` strong-delegation decoupling (touches two
  node families' shared code path), `field_list`/`field_body` redesign (touches three
  interacting concat/separator protocols simultaneously and invalidates exact-string test
  fixtures at scale per the milestone's own accepted-cost note).

---

## 6. Citation integration

### Where the nodes appear in the doctree — verified by executing docutils

Ran `docutils.core.publish_doctree()` directly (full parse + transform pipeline, the same
pipeline Sphinx's read phase drives) against:

```rst
Intro paragraph citing [Ref1]_ inline.

.. [Ref1] First reference bibliography entry.
```

Result:

```
<document source="<string>">
    <paragraph>
        Intro paragraph citing
        <citation_reference ids="citation-reference-1" refid="ref1">
            Ref1
         inline.
    <citation backrefs="citation-reference-1" ids="ref1" names="ref1">
        <label>
            Ref1
        <paragraph>
            First reference bibliography entry.
```

This confirms, concretely:

- **`citation_reference`** appears **inline**, wherever `[Ref1]_` occurs in running prose —
  structurally a sibling of `Text` nodes inside a `paragraph`, exactly like
  `footnote_reference`.
- **`citation`** appears as a **document/section-level block sibling**, at its own definition
  position in source order — in the tested (and the project's own stripped `charged-ieee`)
  examples this is typically clustered at the end of the document, but nothing in the docutils
  grammar requires that; a `citation` can appear anywhere a block-level element is valid.
- **After the transform pipeline runs**, `citation_reference` carries a resolved **`refid`**
  attribute (`refid="ref1"`) pointing directly at the `citation` node's own `id` — **not** the
  pre-transform `refname` that a raw parse (no transforms) would leave behind. This is the same
  shape `footnote_reference.refid` already has by the time `TypstTranslator` sees it (both
  Sphinx's read phase and this test both run full docutils transforms before the translator is
  ever invoked), confirmed structurally identical to the pattern
  `visit_footnote_reference` already reads (`translator.py:2335`, `node.get("refid")`).
- **`citation.ids[0]` matches `citation_reference.refid` directly, one-to-one** — no dict lookup
  ambiguity, and `citation` additionally carries a `backrefs` attribute back to the citing
  reference(s) (not required for a first cut, but available for a "jump back to citation" link
  later).
- `citation`'s own first child is a `<label>` node carrying the visible bracket text (`Ref1`) —
  structurally identical in position to `footnote`'s own `label` child that
  `visit_footnote_reference`'s docstring already documents skipping
  (`translator.py:2300-2308`, "skipping the footnote node's leading `label` child").

### Does citation rendering need a footnote-style pre-pass?

**No — and the reason is a concrete, verifiable difference in the Typst API each target uses,
not a stylistic preference.**

The footnote mechanism (`visit_document`'s FN-01 index, `translator.py:429-434`, plus the lazy
render in `visit_footnote_reference`, `translator.py:2295-2401`) exists specifically because
Typst's `footnote()` stdlib function is an **API that requires the note's body content to be
supplied as an argument at the call site**: `footnote({...body...})` on first use,
`footnote(<label>)` on reuse. Since `footnote_reference` nodes routinely appear in doctree order
*before* their defining `footnote` node (the milestone's own footnote work found this exact
ordering, per the docstring at `translator.py:410-424`, citing "footnote definitions are
frequently positioned AFTER their citing footnote_references... e.g. under a trailing
`.. rubric:: Footnotes`"), the translator cannot render the first reference correctly without
already knowing the full body — hence the document-order pre-pass built in `visit_document`
before any body content streams.

Citations do not need this, because the target rendering shape described in the milestone
("a `thebibliography`-equivalent labelled list plus a working `[Label]` → definition link") maps
onto Typst's **label/link** mechanism instead — the same one `visit_pending_xref`/
`depart_reference` already use for same-document `:ref:` cross-references
(`translator.py:3685-3701`, the `link(<label>, ...)` pattern). Typst resolves `<label>`
anchors and `link(<label>, ...)` references **against the whole compiled document**,
independent of which came first in source order — this is exactly what already lets
`visit_pending_xref`/`_emit_id_anchors` handle arbitrary forward AND backward same-document
references today with no pre-pass of any kind (a target can be anchored after the link that
points to it, and the link still resolves once the whole document compiles). Citation, therefore:

- `visit_citation` can run its own `_emit_id_anchors`-style anchor (namespaced via
  `_namespace_label(docname, node["ids"][0])`, the same helper every other anchor site uses)
  purely locally, at its own natural traversal position, rendering the definition entry (label
  text from its `label` child + body from its `paragraph` child) with **no dependency on
  anything having been recorded earlier**.
- `visit_citation_reference` can equally locally emit `link(<namespaced-refid>, [...its own
  children...])`, exactly mirroring the existing same-document-refid branch at
  `translator.py:3685-3701`, with **no pre-pass lookup needed** — the target's existence is
  guaranteed by Typst's whole-document label resolution, and a genuinely dangling refid (a
  malformed doctree) would surface as Typst's own "label does not exist" compile fatal, the same
  graceful-failure mode every other same-document link already has, rather than needing typsphinx
  to detect and warn about it proactively (though doing so, mirroring the existing dangling-
  footnote warning at `translator.py:2338-2343`, is cheap defensive parity worth keeping).

**Net finding:** citation support is a genuinely local, three-method addition
(`visit_citation`/`visit_label`(as citation's child)/`visit_citation_reference`, each following
an existing precedent — `_emit_id_anchors` for the definition anchor, the `link(<label>, ...)`
pattern for the reference) with **no new pre-pass machinery required**, distinguishing it
structurally from the footnote mechanism it superficially resembles.

---

## Sources

- `typsphinx/builder.py` (full read) — `_write_template_file` (521-592), `prepare_writing`
  (318-332), `write` (334-394), `_compute_master_included_docnames` (95-131)
- `typsphinx/writer.py` (full read) — `translate()` (121-292), `_is_master_document` (41-71),
  `_compute_template_import_path` (73-119)
- `typsphinx/template_engine.py` (full read) — `render()` (571-658), `resolve_template()`
  (274-330), `map_parameters()` (387-483), `resolve_package_for_engine()` (152-176)
- `typsphinx/translator.py` (targeted read: 1-262 init/helpers, 400-500 document/title,
  1203-1262 strong, 2278-2401 footnote, 3287-3380 label helpers, 3650-3751 reference,
  4106-4335 admonition/topic, 4619-5134 desc/field/rubric)
- `pyproject.toml:67-71` — package-data glob (`"typsphinx" = ["templates/*.typ"]`)
- `tests/test_preview_version_sync.py` (full read) — 3-way `@preview` version-sync gate
- `typsphinx/templates/base.typ` (lines 1-80) — bundled default template's own import block
- `examples/advanced/_templates/custom.typ`, `docs/source/_typst/custom_template.typ`,
  `examples/charged-ieee/approach2/source/_templates/_template.typ` (headers read in full) —
  the three custom templates whose non-breakage is verified in §3
- `.planning/todos/pending/2026-07-22-citation-node-support-untracked.md` — origin record of the
  citation gap, confirms `translator.py` has zero citation handlers today
- `.planning/PROJECT.md:19-100` — v0.7.0 milestone scope (read in full)
- `.planning/codebase/ARCHITECTURE.md` (full read) — baseline architecture map, anti-patterns
  section corroborating the `_write_template_file` conditional-skip rationale
- Direct execution: `docutils.core.publish_doctree()` against a two-node citation sample
  (this session) — confirms `citation_reference.refid` → `citation.ids[0]` resolution shape
  used in §6

---
*Architecture research for: typsphinx v0.7.0 API rendering design overhaul*
*Researched: 2026-07-29*
