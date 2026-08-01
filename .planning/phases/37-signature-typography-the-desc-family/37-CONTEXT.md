# Phase 37: Signature Typography — the `desc_*` Family - Context

**Gathered:** 2026-08-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Restyle `desc_signature` and its inline children so an API signature reads as a signature: each
sub-part carries its own typographic role, a real arrow glyph replaces the ASCII `->`, a long
fully-qualified signature stays inside the right text margin, and a signature is neither split by a
page break nor buried in doubled blank lines.

**In scope** — the handlers that emit signature bytes:
`visit/depart_desc_signature`, `desc_annotation`, `desc_addname`, `desc_name`,
`desc_parameterlist`, `desc_parameter`, `desc_optional`, `desc_returns`, the `desc_sig_*` family
(`desc_sig_keyword`, `desc_sig_space`, `desc_sig_name`, `desc_sig_punctuation`,
`desc_sig_operator`), and the `desc`-level break emission responsible for the doubled `parbreak()`
(SIG-08).

**Out of scope:**

- `visit_desc_content` / `depart_desc_content` — locked out by D-08 below. Both are `pass` today
  (`typsphinx/translator.py:4853, 4859`) and Phase 38 (IND-01) owns them.
- `field_list` — Phase 38 (FLD-01..03).
- `rubric` / admonitions — Phase 39 (ADM-01..05). Phase 36 already decoupled `rubric` from
  `desc_signature`, so restyling one no longer touches the other.
- Citations — Phase 40.
- Anything that makes the styling user-overridable — explicitly not a goal of v0.7.0.

</domain>

<decisions>
## Implementation Decisions

Every measurement cited below was taken **this session (2026-08-01)** by building a `py:` domain
sample (a `py:class::` with a nested `py:method::`, a `py:function::` with an optional group and a
return annotation, and an overload pair) through `sphinx-build -b typst`, `-b typstpdf` and
`-b html`, and by compiling hand-written Typst probes through the real `typst.compile()`
(`typst-py` 0.15.0).

### Typography — SIG-01..SIG-05

- **D-01: the signature is set entirely in monospace, with the parameter name the only italic (owner choice, "案B-1").**
  Per sub-part:

  | Node | Treatment | Emitted shape |
  |---|---|---|
  | `desc_name` | bold monospace | `strong(raw("…"))` |
  | `desc_annotation` (`class`/`exception`) | bold monospace — same as `desc_name`, per SIG-03 | `strong(raw("…"))` |
  | `desc_addname` (`sphinx.builders.latex.`) | regular monospace | `raw("…")` |
  | delimiters `(` `)` `,` `=` `:` and `desc_optional`'s `[` `]` | regular monospace | `raw("…")` |
  | `desc_parameter`'s own parameter name | **italic** monospace | `emph(raw("…"))` |
  | inline type annotation and default value inside `desc_parameter` | regular monospace | `raw("…")` |

  Measured font resolution in the compiled PDF: `strong(raw(…))` → `DejaVuSansMono-Bold`,
  `raw(…)` → `DejaVuSansMono`, `emph(raw(…))` → `DejaVuSansMono-Oblique` — a real oblique face in
  the `typst-py` embedded font set, not a synthesized slant.

- **D-02: this deliberately diverges from the LaTeX reference, and that is allowed.**
  The reference sets the whole `desc_parameter` in *italic proportional*
  (`sphinx/writers/latex.py:1050` wraps the entire `desc_parameter` node in `\sphinxparam{`, and
  `sphinx/texinputs/sphinxlatexstyletext.sty:25` defines `\protected\def\sphinxparam#1{\emph{#1}}`).
  Both the reference recipe and an all-mono "whole parameter italic" variant were rendered and
  rejected by the owner: with the type and the default value also slanted, the name/type/default
  boundary inside `verbosity: int = 0` stops being readable, and realistic annotations such as
  `Iterable[str] | None = None` stop reading as code. The milestone's standing rule — the reference
  is a starting point, not an authority; diverge wherever Typst can do better — covers this.

- **D-03: SIG-04 is satisfied as written; do NOT amend `REQUIREMENTS.md`.**
  SIG-04 says the parameter *including any inline type annotation* must render **distinctly from
  `desc_name`**. Under D-01 every sub-part of `desc_parameter` differs from `desc_name`'s bold
  monospace — the name by being italic, the type and default by being regular weight. The
  requirement does not demand that the whole parameter share one treatment. This reading is
  recorded here so verify-time does not re-open it; the mechanical assertion must be written
  **per sub-part**, not as one blanket check over `desc_parameter`.

- **D-04: `raw(...)` is the monospace primitive — not `text(font: …)`.**
  Measured: `raw(…)` resolves to `DejaVuSansMono` with no font name hard-coded anywhere, it is
  unaffected by the `codly-init` / `#codly(languages: …)` show rules already active in every
  generated document (probe compiled with the real template preamble), and `visit_literal`
  (`typsphinx/translator.py:1282-1360`) already emits `raw("…")` for inline literals, so the
  primitive is proven in the corpus. No new `@preview` package, no font configuration, no new
  version-lockstep site.

- **D-05: the parameter-name discriminator must be measured, not assumed.**
  Measured doctree for `LaTeXBuilder(app, env, *, extra=None, verbosity: int = 0)`: **both** the
  parameter name and its type annotation arrive as `desc_sig_name` (class `n`) — the type one
  wrapping a `pending_xref`. Node type alone cannot tell them apart. The default value arrives as
  `inline` (class `default_value`); `=` and `*` as `desc_sig_operator`; `:` as
  `desc_sig_punctuation`; `*` additionally wraps an `abbreviation`. Whether the discriminator is
  "first `desc_sig_name` child of `desc_parameter`", "has no `pending_xref` child", or something
  else is the planner's call, but it must be derived from a dumped doctree covering positional,
  keyword-only, annotated, defaulted and `**kwargs` parameters — not guessed.

### Overflow — SIG-07

- **D-06: `par(hanging-indent: …)` plus U+200B injection into long dotted names. Nothing else.**
  Measured on A4 with 2.5 cm side margins, using
  `sphinx.ext.autodoc.preserve_defaults.DefaultValueDocumenter(directive: DocumenterBridge, name: str, *, indent: str = '')`:
  - bare concatenation wraps at the spaces inside `text(", ")` but the continuation line sits flush
    left and is indistinguishable from body text;
  - `grid(columns: (auto, 1fr))` — the direct analogue of LaTeX's `\py@sigparams`, which puts the
    parameter list in a `\parbox[t]{\py@argswidth}{\raggedright …}` (`sphinxlatexobjects.sty:133`) —
    collapses the parameter column to a sliver when the qualified name is long, producing four
    ragged lines. **Measured worst of the four; rejected.**
  - `par(hanging-indent: 2.5em)` fits the same signature in two lines with the continuation stepped
    in. **Chosen.**
  - font shrinking was not tried and is **not to be used** — it breaks the one-size-fits-all reading
    of an API page.
- **D-07: U+200B is required, and its scope is every long dotted name — `desc_addname` and dotted type annotations alike.**
  Measured at 9 cm width with a visible text-frame rule: a dotted qualified name with no space and
  no comma **overflows the right edge** under every wrapping strategy, and injecting U+200B after
  each `.` makes it break correctly and pick up the hanging indent. This reuses the U+200B
  *technique* from the v0.6.1 FID-01a wide-table fix but not its rationale — SIG-07 forbids assuming
  the table fix transfers, and the injection site (dotted identifiers in signatures) and the
  evidence (the 9 cm frame measurement above, to be re-measured against the real `doc/` corpus) are
  derived independently.
- **D-08: the hanging-indent step is introduced in Phase 37 as the shared indent constant that Phase 38's IND-04 will reuse.**
  Phase 37 creates exactly one Python-side constant and uses it for the signature hanging indent;
  Phase 38 references that same constant for `desc_content`, `field_list` and `block_quote` rather
  than defining a second one. Rationale: IND-04 exists to prevent per-node magic numbers, and the
  first writer of the number is the natural owner.

### Phase boundary and structure

- **D-09: Phase 37 does not touch `visit_desc_content` / `depart_desc_content`.**
  SIG-09 (signature and the first line of its body not split across a page break) must be satisfied
  from the signature side alone. `block(sticky: true, …)` — Typst's "keep this block with the next
  one" — was confirmed to compile under typst 0.15 in a document shaped like the generated output,
  and is the obvious candidate. Keeping Phase 37 out of `desc_content` structurally prevents the
  double-wrap accident when Phase 38 adds the indent there.
- **D-10: what replaces the `strong({...})` wrapper is Claude's discretion, decided by measurement.**
  Both candidates were compiled successfully this session inside a real generated-document code
  block: a bare content block `{ … }` (strip `strong(` / `)`, children style themselves) and
  `block(sticky: true, { … })`. **Binding constraint:** whatever is chosen must not create a wrapper
  that Phase 38's `desc_content` wrapper would nest inside redundantly, and it must carry the
  SIG-07 hanging indent and the SIG-09 keep-with-next without a second wrapper.

### Newly found defect — folded into this phase

- **D-11: the dropped separator after a `desc_optional` group is fixed in Phase 37.**
  Measured: `.. py:function:: connect(host, port=8080, [timeout], **kwargs)` emits
  `text("[") + text("timeout") + text("]")text("**kwargs")` and renders as
  `connect(host, port=8080, [timeout]**kwargs)`, while Sphinx's own HTML writer renders
  `connect(host, port=8080, [timeout, ]**kwargs)` — the comma belongs *inside* the bracket, after
  the last optional parameter. Root cause: `depart_desc_parameter`
  (`typsphinx/translator.py:4953-4962`) appends `", "` only when the *parameter* has a following
  sibling; the last parameter inside a `desc_optional` has none, so the separator that Sphinx emits
  because the *optional group* has a following sibling is lost. Sphinx's own emission is
  `\sphinxparamcomma` driven by `latex.py`'s `_depart_sig_parameter` bookkeeping.
  A second, cosmetic half of the same site: `text("]")text("**kwargs")` has no `+` joining the two
  expressions — it happens to compile today, but it is juxtaposition by luck, not by design, and
  should be joined explicitly by whatever the rewrite emits.
  This is covered by **no** SIG requirement. It is folded in because Phase 37 rewrites exactly these
  two handlers; it must be recorded as its own success criterion / fixture rather than smuggled into
  a SIG-05 assertion.

### Claude's Discretion

Recorded so planning does not re-open them with the user.

- **D-12: SIG-08's "exactly one break" is Claude's to define.**
  Not selected for discussion. Measured cause of the doubled run: a nested `py:method::` inside a
  `py:class::` produces `parbreak()\nparbreak()` because `depart_desc` emits an unconditional
  `_emit_forced_break("parbreak()")` (`typsphinx/translator.py:4667`) for the inner `desc` and again
  for the outer one. Sibling *signatures* inside one `desc` use a different mechanism — FID-03's
  leading `linebreak()` in `visit_desc_signature` — and whether the two should converge is part of
  this call. If D-10 lands on `block(...)`, block spacing replaces some of this bookkeeping; say so
  explicitly in the plan rather than leaving both mechanisms live.
- **D-13: the SIG-06 arrow glyph is Claude's to pick.**
  Not raised in discussion. Current emission is `text(" -> ")` (`translator.py:4821`). Sphinx's own
  HTML uses `→` (U+2192), and `raw("→")` was verified this session to compile and to survive
  `pypdf` text extraction. Use U+2192 unless measurement says otherwise, and assert that no ASCII
  `->` remains anywhere in signature output (ROADMAP SC#2).
- **D-14: the `golden.typ` migration strategy is Claude's to choose.**
  `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` is Phase 36's byte-identity
  evidence and Phase 37 necessarily breaks its signature lines. Either hand-derive only the changed
  signature lines and leave the rubric / `**bold**` / list sections byte-identical (so the diff
  itself proves Phase 37 touched only signatures), or freeze/narrow the Phase 36 gate and give
  Phase 37 its own fixture. **Binding constraint, non-negotiable:** expected strings are hand-derived
  (ROADMAP SC#5); copying whatever the new code emits into the golden is forbidden by milestone
  invariant #4 and would void the phase's evidence.

### Folded Todos

None. `todo.match-phase 37` returned eight records, all keyword false positives — see Reviewed
Todos below.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and criteria

- `.planning/ROADMAP.md` § "Phase 37: Signature Typography — the `desc_*` Family" — goal, the five
  success criteria. Note SC#5 already mandates hand-derived expected strings plus a recorded
  file/class census; D-14 above is bound by it.
- `.planning/ROADMAP.md` § "🚧 v0.7.0 — API rendering design overhaul" — the standing invariants, in
  particular #4 (GATE-01's RED state is structural for this milestone, because every defect here
  compiles fine today) and #5 (test migration is owned per phase).
- `.planning/REQUIREMENTS.md` lines 31–62 — SIG-01..SIG-09, with the `[M]`/`[V]` verification legend
  at lines 8–21. IND-01..05 (lines 70–88) and FLD-01..03 (lines 92–101) belong to Phase 38; do not
  pull them forward, with the single exception of the shared indent constant per D-08.
- `.planning/PROJECT.md` § "Current Milestone: v0.7.0" — the "reference, not authority" decision that
  licenses D-02's divergence, and the no-new-runtime-dependency / four-`@preview`-packages
  invariants.

### Prior phase context this one builds on

- `.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md` — D-01 (the triplicated
  `visit_strong` body that Phase 37 is expected to make diverge), D-02 (the shared `_strong_was_*`
  attribute names and the `par()`-loss leak they cause, deferred to Phase 39).
- `tests/test_desc_rubric_decoupling_render_gate.py` and
  `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` — Phase 36's SC#1/SC#2 gate; see
  D-14.

### The reference (starting point, not authority)

- `.venv/lib/python3.13/site-packages/sphinx/writers/latex.py:1049-1051` — `visit_desc_parameter`
  wraps the **whole** `desc_parameter` node in `\sphinxparam{`.
- `.venv/lib/python3.13/site-packages/sphinx/texinputs/sphinxlatexstyletext.sty:25, 85, 88` —
  `\sphinxparam#1 = \emph{#1}`; `\sphinxparamcomma = ", "`; `\sphinxparamcommaoneperline`.
- `.venv/lib/python3.13/site-packages/sphinx/texinputs/sphinxlatexobjects.sty:126-171` —
  `\pysigarglistopen = \sphinxcode{(}` (monospace delimiters, supporting SIG-05), and
  `\py@sigparams`'s `\parbox[t]{\py@argswidth}{\raggedright …}`, the strategy D-06 measured and
  rejected.
- `.venv/lib/python3.13/site-packages/sphinx/texinputs/sphinxlatexstyletext.sty:27-29` —
  `\sphinxoptional` sets the optional brackets in `\textnormal{\Large …}`; noted for context, not
  adopted.

### Code under change

- `typsphinx/translator.py:4669-4741` — `visit_desc_signature`, holding the verbatim copy of
  `visit_strong`'s body that this phase replaces, plus the FID-03 sibling `linebreak()`.
- `typsphinx/translator.py:4743-4808` — `depart_desc_signature`, including the `[#metadata(none) <id>]`
  anchor emission that must survive the restyle unchanged (it is what makes `:py:func:` xrefs
  resolve).
- `typsphinx/translator.py:4810-4827` — `visit_desc_returns` (SIG-06's `text(" -> ")`).
- `typsphinx/translator.py:4880-4916` — `desc_annotation` / `desc_addname` / `desc_name`, all `pass`
  today.
- `typsphinx/translator.py:4918-4984` — `desc_parameterlist` / `desc_parameter` / `desc_optional`,
  the `+`-concatenation machinery and the site of D-11's dropped comma.
- `typsphinx/translator.py:5261-5301` — the `desc_sig_*` family, all `pass` today.
- `typsphinx/translator.py:4653-4667` — `depart_desc`'s unconditional `parbreak()`, the measured
  source of SIG-08's doubled run.
- `typsphinx/translator.py:1282-1360` — `visit_literal` / `depart_literal`, the existing proven
  `raw("…")` emission D-04 follows.

### Project standing rules

- `CLAUDE.md` § "Worktree-isolated execution" — worktree isolation is the standing execution mode;
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then `uv run …` is mandatory
  for every executor, not conditional.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — untouched by this phase (D-04 adds no
  package), but the reason "no new lockstep site" is an invariant.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured starting state (2026-08-01, real `sphinx-build` run)

Source:

```rst
.. py:class:: sphinx.builders.latex.LaTeXBuilder(app, env, *, extra=None, verbosity: int = 0)

   A builder.

   .. py:method:: write_documents(docnames: set[str], *, force: bool = False) -> None

      Write docs.

.. py:function:: connect(host, port=8080, [timeout], **kwargs) -> Connection
```

Emitted `.typ`:

```typst
strong({text("class")
text(" ")
text("sphinx.builders.latex.")
text("LaTeXBuilder")
text("(") + text("app") + text(", ") + text("env") + text(", ") + text("*") + text(", ") + text("extra") + text("=") + text("None") + text(", ") + text("verbosity") + text(":") + text(" ") + text("int") + text(" ") + text("=") + text(" ") + text("0") + text(")")})
[#metadata(none) <index:sphinx.builders.latex.LaTeXBuilder>]
par({text("A builder.")})

strong({text("write_documents")
text("(") + … + text(")")
text(" -> ")
text("None")})
[#metadata(none) <index:sphinx.builders.latex.LaTeXBuilder.write_documents>]
par({text("Write docs.")})

parbreak()
parbreak()                          ← SIG-08: nested desc depart + outer desc depart
strong({text("connect")
text("(") + text("host") + … + text("[") + text("timeout") + text("]")text("**kwargs") + text(")")
                                    ↑ D-11: comma dropped, and no `+` joining the two calls
text(" -> ")                        ← SIG-06: ASCII arrow
text("Connection")})
```

Compiled PDF text (`pypdf`), same run:
`connect(host, port=8080, [timeout]**kwargs) -> Connection` — the defect is visible in the output,
not only in the emitted source.

### Measured doctree shape of one `desc_signature`

```
desc_signature
  desc_annotation → desc_sig_keyword['k'] "class", desc_sig_space['w'] " "
  desc_addname['sig-prename'] "sphinx.builders.latex."
  desc_name['sig-name'] "LaTeXBuilder"
  desc_parameterlist
    desc_parameter → desc_sig_name['n'] "app"
    desc_parameter → desc_sig_operator['keyword-only-separator'] → abbreviation "*"
    desc_parameter → desc_sig_name['n'] "extra", desc_sig_operator['o'] "=", inline['default_value'] "None"
    desc_parameter → desc_sig_name['n'] "verbosity", desc_sig_punctuation['p'] ":",
                     desc_sig_space, desc_sig_name['n'] → pending_xref "int",
                     desc_sig_space, desc_sig_operator['o'] "=", desc_sig_space,
                     inline['default_value'] "0"
```

This is the evidence behind D-05: the parameter name and the type annotation are the same node type.

### Reusable assets

- **`visit_literal` / `depart_literal` (`translator.py:1282-1360`)** — the existing `raw("…")`
  emission path, including the escaping helper for the string argument. D-04's primitive already
  has a working precedent here; reuse the escaping rather than re-deriving it.
- **`_emit_forced_break(…)`** — already used by `visit_desc_signature` (sibling `linebreak()`) and
  `depart_desc` (`parbreak()`); the natural lever for D-12.
- **`_emit_id_anchors(node)` and the `[#metadata(none) <label>]` form in `depart_desc_signature`** —
  the anchor emission is orthogonal to typography and must come out byte-equivalent.
- **`_enter_inline_concat_element()` / `_exit_inline_concat_element()`** — the stack-based concat
  helpers the current `strong` copy calls; whatever wrapper D-10 picks still has to interact with
  them correctly.
- **Existing render gates over the same seam** — `tests/test_desc_signature_concat_render_gate.py`,
  `tests/test_desc_signature_anchor_render_gate.py`, `tests/test_desc_sig_space_render_gate.py`,
  `tests/test_desc_container_propagated_target_render_gate.py`,
  `tests/test_desc_rubric_decoupling_render_gate.py`.

### Test blast radius — starting census (verify and extend during planning)

Files referencing the `desc_*` node names or asserting on `strong({text(`:
`tests/test_confval_field_spacing_render_gate.py`, `tests/test_confval_field_body_render_gate.py`,
`tests/test_deflist_nested_definition_render_gate.py`, `tests/test_deflist_term_concat_render_gate.py`,
`tests/test_deflist_term_inline_children_gate.py`,
`tests/test_desc_container_propagated_target_render_gate.py`,
`tests/test_desc_rubric_decoupling_render_gate.py`, `tests/test_desc_sig_space_render_gate.py`,
`tests/test_desc_signature_anchor_render_gate.py`, `tests/test_desc_signature_concat_render_gate.py`,
`tests/test_rubric_option_concat_render_gate.py`, `tests/test_pdf_render_gate.py`,
`tests/test_translator.py`, plus the fixture `golden.typ` under
`tests/fixtures/desc_rubric_decoupling_render_gate/`. Several of these are `deflist`/`rubric` tests
that merely mention the names — the census SC#5 asks for must separate "mentions" from
"asserts on signature bytes".

### Integration points

- `tests/test_corpus_gate.py` — the full-corpus `-b typstpdf` gate is `@pytest.mark.slow` and
  excluded from the default run via `-m "not slow"`; run it explicitly. It is also the source of the
  real long signatures SIG-07 requires measuring.
- `typsphinx/templates/base.typ` — sets no monospace font and no `show raw` rule of its own; the
  active raw-related rules are `codly-init` and `#codly(languages: codly-languages)`. Verified this
  session that inline `raw(…)` renders as `DejaVuSansMono` under exactly that preamble.

</code_context>

<specifics>
## Specific Ideas

- The owner reviewed three real compiled renderings before choosing, and the choices were made
  against the pictures, not against descriptions. The two rejected renderings matter as much as the
  chosen one: (1) the LaTeX-faithful "whole parameter in italic proportional", rejected because the
  serif italic inside a monospace run breaks the baseline and the name/type boundary; (2)
  `grid(columns: (auto, 1fr))`, rejected because a long qualified name starves the parameter column.
  Do not resurrect either as an "improvement" during planning.
- The signature must keep reading **as code**: that framing is what decided both the all-monospace
  choice and the rejection of whole-parameter italics. Any later trade-off should be resolved the
  same way.
- Two claims that were checked against reality this session and would have been wrong if assumed:
  Sphinx renders the optional-group comma *inside* the brackets (`[timeout, ]`), and the parameter
  name and its type annotation are indistinguishable by node type. Measure before building on
  anything in the same family.

</specifics>

<deferred>
## Deferred Ideas

- **Nothing new was deferred from this discussion.** Scope stayed inside SIG-01..09 plus the D-11
  defect, which lives in the handlers this phase rewrites.

### Reviewed Todos (not folded)

`todo.match-phase 37` returned eight records; all are keyword false positives and none is folded.

- `2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md` — the Phase 36 D-02
  deferral; belongs to **Phase 39**, which owns `rubric`.
- `2026-07-22-citation-node-support-untracked.md` — **Phase 40** (CIT-01..06).
- `2026-07-29-release-notes-body-from-changelog-section.md` — **Phase 41** (REL-04).
- `2026-07-25-derive-typst-lang-duplicated-warning-block.md` — `template_engine.py`, unrelated.
- `2026-07-29-project-md-unterminated-html-comments.md` — planning docs, unrelated.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — deferred as Future requirement LNK-01.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — deliberately deferred;
  `CLAUDE.md` forbids doing it opportunistically.
- The eighth record (non-`str` docname `TypeError` hardening) — unrelated hardening, still pending.

</deferred>

---

*Phase: 37-Signature Typography — the `desc_*` Family*
*Context gathered: 2026-08-01*
