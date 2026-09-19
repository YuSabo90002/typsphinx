# Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors - Context

**Gathered:** 2026-09-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Give `doctest_block` the `TypstTranslator` handler it has never had, so that a `>>>` example renders
in Typst output as a codly-styled code block, with its line structure intact and a non-empty
language tag, in both positions autodoc/napoleon place one: plain paragraph position and
definition-list / field-body position. Each position is proven by a recorded-RED GATE-01 fixture
that goes through a real `typst.compile()`. The same clean `-b typst` build of `docs/source` must
also stop reporting the docutils `Unexpected indentation` / `Block quote ends without a blank line`
messages that come from typsphinx's own docstrings, and its total warning count must not rise.

The phase is bounded by `.planning/ROADMAP.md` § Phase 74 (SC 1–4) and binding constraints 1–13.
Those are **not** re-decided here: the base-first / RED-before-GREEN / census-before-fix /
sequenced-not-parallel / evidence-last ordering, the `typsphinx/` scope fence (handler and docstring
text only), clean builds under `LC_ALL=C` with positive controls, worktree provisioning, the first
push, and the CI dispatch. Requirements: TRN-01, TRN-02, QUA-14.

</domain>

<decisions>
## Implementation Decisions

### Language tag (SC1 "the tag chosen and the reason")
- **D-01 — The handler-supplied fence language is python, not pycon.** Measured 2026-09-19 with typst-py from the main checkout's `.venv` (not transcribed from the roadmap). The same two-prompt doctest fragment was compiled under five fences. `pycon`, no tag, `text` and a nonexistent `bogusxyz` all produced a **byte-identical** PDF (11531 bytes, SHA-256 prefix `5428a015b02591d5`). Only `python` differed (12654 bytes, `9bb09e20e0d2d05a`). An SVG compile counted per glyph: under `pycon` all 58 glyphs were `#000000`. Under `python`, the 28-character function name was blue `#4b69c6`, the 24 string-literal characters green `#198810`, `>>>` red `#d73948`, and the 3 punctuation glyphs black. `@preview/codly-languages:0.1.10`'s `lib.typ` has a `python` entry (name "Python", Python icon, `#306998`) and **zero** `pycon` entries. So `pycon` gives neither syntax highlighting nor the codly language label, while `python` gives both. The known trade-off, accepted by the owner: output lines are coloured as Python source rather than as console output. In the measured example `'index.typ'` comes out green as a string literal.
- **D-02 — A non-empty language already on the node is honoured, and python applies only when it is empty.** Standard Sphinx never sets `language` on a `doctest_block`: `HighlightLanguageTransform` only assigns it to `literal_block`. So in every build this project measures, the tag is the handler's own `python`. That satisfies SC1's "supplied by the handler itself rather than read from `node['language']`" in intent. The honour path only matters if a third-party extension has written a value, and the owner chose not to overwrite that. `highlight_language` / `.. highlight::` are deliberately **not** followed. Sphinx's own HTML path reads a `doctest_block` as `'default'` and `sphinx/highlighting.py:148-151` rewrites any `>>>`-led source under `'default'`/python-ish languages to `pycon`, so a fixed tag is the same behaviour Sphinx has.

### Handler implementation shape
- **D-03 — The python fallback lives in the language-resolution line of the literal-block visitor, and the doctree is not mutated.** Today `visit_literal_block` reads the language with a bare `node.get("language", "")`. That becomes: use the node's language if non-empty, otherwise `"python"` when the node is a `nodes.doctest_block`, otherwise empty as before. The handler never writes `node["language"]`. Because the fallback is keyed on the node class, every `literal_block` keeps exactly the code path and output it has today. The doctest block shares everything else the literal-block visitor already does, with no second copy: `_emit_id_anchors`, the `in_list_item` / `list_item_needs_separator` separator, the list-item `{ }` wrapper, `codly(number-format: none)`, `in_literal_block` (so `visit_Text` emits the raw text unwrapped), and the depart-side fence close and separator re-arm.
- **D-04 — Explicit delegating methods with docstrings, not a class-attribute alias.** Add `visit_doctest_block(self, node: nodes.doctest_block) -> None` and `depart_doctest_block(...)`, each a one-line delegation to the literal-block visitor or departer. Their docstrings name TRN-01 and note that the shape is the one Sphinx's own writers use (html5's delegating call; latex/texinfo's alias). The `node` annotations of `visit_literal_block` / `depart_literal_block` widen to `nodes.literal_block | nodes.doctest_block`, because `doctest_block` is not a `literal_block` subclass. This keeps `mypy typsphinx/` honest.
- **D-05 — The literal-block path is proven unchanged by a whole-tree diff of the base and tip `-b typst` output.** SC1/SC3 already require a clean base build at `PHASE_BASE_SHA` and a clean tip build. Their complete output trees are diffed, and the phase evidence records that **every** differing hunk falls in one of two classes: a doctest-example region (TRN-01) or the rendered output of a docstring that QUA-14's census fixed. Any other differing hunk is a finding, not noise. The existing literal-block render gates (codly config leak, caption, offset, etc.) also stay green as part of the full suite, but that is not the whole proof.

### Post-research amendments (AMENDED 2026-09-20, post-research, owner-approved)
Two supporting claims in REQUIREMENTS.md TRN-02 / ROADMAP SC2 were falsified by measurement in `74-RESEARCH.md` § Contradictions and re-measured by the orchestrator (clean `LC_ALL=C` `-b typst` build of `docs/source`, main `.venv`, Python 3.13.13). The REQUIREMENTS.md text stays literal; the reframing lives here.
- Falsified claim 1: "the `terms.item(text("Examples:"), {...})` shape ... reproduced in this project's own `api/index.typ`". Measured `grep -c 'terms\.item' api/index.typ` = 0. Both doctest blocks in this project's docs sit after a napoleon rubric (`strong({text("Examples")})` + `linebreak()`), a sibling position close to context (a). The `terms.item` shape is real only in the 2026-09-13 sphinx-autoapi run recorded in the folded todo.
- Falsified claim 2: "In (b) it respects the same separator discipline ... via `in_list_item` / `list_item_needs_separator`". `in_list_item = True` is set by list_item, title, emphasis, strong, legend, desc_signature and rubric visitors, never by `visit_definition` or `visit_field_body`. A definition-list fixture does not exercise that mechanism.

- **D-06 — Context (b) is one fixture section carrying two shapes, both at a non-first position.** Shape (b1) is a definition-list item reproducing the autoapi `terms.item(...)` position that TRN-02 names, with a leading paragraph before the doctest block in the definition. Shape (b2) is a bullet-list item with a leading paragraph, then the doctest block, then a trailing paragraph, which genuinely exercises `in_list_item` / `list_item_needs_separator`. Each shape gets its own line-structure assertion, both are recorded RED on the pre-handler translator, and both are covered by the same real `typst.compile()`. The evidence record states which separator mechanism governs each shape. Context (a) is built with trailing content after the doctest block so its RED captures the pre-handler compile failure (`expected semicolon or line break`) that research measured.
- **D-07 — The QUA-14 census counts raw and attributed lines, and the quote_path docstring is in the fix list.** The base build prints 4 unattributed `Unexpected indentation` / `Block quote ends` lines (no file:line, not counted in `N warnings`) that come from `sphinx-autodoc-typehints` probe-parsing `quote_path`'s docstring in `typsphinx/pathfmt.py`, whose `Delimiter rule (D-01)` bullet list lacks a preceding blank line. It is a typsphinx docstring raising the message class, so per constraint 6 it is fixed the same minimal way as `visit_toctree`'s. Base and tip each record two numbers under `LC_ALL=C` — the raw substring count over the whole console log and the attributed count (lines matching `.py:docstring of ...:N: (ERROR|WARNING): ...`) — and both must be zero on the tip.

### Claude's Discretion
The owner discussed only the two areas above. For the other two gray areas presented, the owner accepted Claude's defaults within the ROADMAP constraints:

- **QUA-14 fix granularity.** Make the minimal reST repair to each docstring the base census names: add the missing blank line before a bullet list, and fix continuation indentation. Keep the documented meaning and prose as they are, and don't rewrite or restyle beyond what clears the message. No new regression test is added for this message class. A docs warnings gate is explicitly Future (`REQUIREMENTS.md` § Future), and Phase 75 SC4 re-proves the zero by measurement. The census is the base build's own `LC_ALL=C` output over the whole tree (constraint 6), not the `visit_toctree` docstring alone. A census hit in any other `typsphinx/` docstring is fixed the same way.
- **GATE-01 fixture structure.** Follow `tests/test_inline_image_separator_render_gate.py`:
  - one new `tests/test_*_render_gate.py` module, with one synthetic fixture project under `tests/fixtures/<name>/` carrying both contexts;
  - a single module-scoped `sys.executable -m sphinx -b typstpdf` build shared by all test methods;
  - text-mode utf-8 reads.

  Context (a) is a `>>>` block in plain paragraph position. Context (b) is a napoleon/field-body or definition-list `Examples:` shape with the doctest block at a **non-first** position in its container, so the separator discipline is exercised. The assertions are:
  - the `.typ` line structure: prompts, continuation and output on separate lines inside a ```` ```python ```` fence;
  - the absence of `unknown node type: <doctest_block` in the build's captured output. That substring is typsphinx's own untranslated f-string, so it is locale-stable, but the RED run must still be observed finding it;
  - the real compile succeeding, with a PDF written.

  pypdf text extraction is optional. The RED transcript is taken at a commit without the handler and quoted verbatim in the phase evidence. A small unit test in the existing translator-test style may additionally pin D-02's honour path, which no Sphinx build exercises; this is at the planner's discretion.

### Folded Todos
- **`2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line.md`**: already bound to this phase via `resolves_phase` at roadmap creation. It is the origin of TRN-01/TRN-02 (the 2026-09-13 sphinx-autoapi measurement of the `terms.item(text("Examples:"), {...})` shape), and the phase resolves it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope, constraints, acceptance
- `.planning/ROADMAP.md` § "v0.9.6 — Doctest block rendering and release": binding constraints 1–13, especially 3 (GATE-01 real-compile bar), 4 (counts measured fresh), 5 (clean builds, `LC_ALL=C`, positive control), 6 (QUA-14 census is a full-build measurement), 7 (scope fence), 8 (adjacent mechanisms out of scope; language tag cannot be inherited), 10 (branch census, decoy handling, first push, CI dispatch) and 11 (worktree provisioning)
- `.planning/ROADMAP.md` § "Phase 74": goal, binding in-phase ordering, SC 1–4
- `.planning/REQUIREMENTS.md`: TRN-01, TRN-02, QUA-14 (lines 13, 14, 18); § Future (docs warnings gate is out of scope); § Out of Scope table
- `.planning/milestones/v0.9.5-REQUIREMENTS.md` § Future: names the QUA-14 message class as a warnings-gate prerequisite
- `CLAUDE.md` § "Worktree-isolated execution", § "NixOS development shell" (Locale, Interpreters may differ)
- `.planning/todos/` → `2026-09-13-doctest-block-unhandled-collapses-examples-to-one-line.md`: the originating measurement

### Code under change
- `typsphinx/translator.py`: `visit_literal_block` / `depart_literal_block` (from `:2431`; language line near `:2570`), `visit_Text` literal branch (`:1806`), `unknown_visit` (`:5819`), `visit_toctree` docstring (`:5415`, the 2026-09-16 QUA-14 site)
- `typsphinx/writer.py:32-67`: `compute_content_include_path` docstring, the `api/index.typ` example SC1 inspects

### Test patterns
- `tests/test_inline_image_separator_render_gate.py`: the most recent GATE-01 real-compile gate (module-scoped build, `sys.executable -m sphinx`, text-mode utf-8 reads, RED-evidence choreography)
- `tests/test_pdf_render_gate.py`: the original `sphinx-build` → `typst.compile()` → `pypdf` pattern (v0.6.0 Phase 11 / 08.1)

### Upstream behaviour relied on (read in the installed venv, not the repo)
- `sphinx/writers/html5.py:665`, `sphinx/writers/latex.py:2324-2325`, `sphinx/writers/texinfo.py:812-813`: all three Sphinx writers route `doctest_block` through their literal-block path
- `sphinx/highlighting.py:148-151`: `>>>`-led source under python/`'default'` is rewritten to `pycon` (basis for D-02 not following `highlight_language`)
- `~/.cache/typst/packages/preview/codly-languages/0.1.10/lib.typ`: `python:` entry at `:471`, no `pycon` entry (D-01)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `visit_literal_block` / `depart_literal_block`: already carry the whole code-block emission contract (anchors, list-item separator and `{ }` wrapper, codly per-block config, fence open/close, separator re-arm). D-03/D-04 reuse it wholesale.
- `visit_Text`'s `in_literal_block` early return: emits raw text unwrapped. Setting the flag (which the delegated visitor does) is what preserves the doctest's line breaks.
- `tests/fixtures/<name>/` + module-scoped build fixture pattern from the inline-image gate.

### Established Patterns
- Node-handler changes ship a recorded-RED GATE-01 fixture through a real compile (constraint 3; standing since v0.6.0 Phase 11).
- Subprocess Sphinx is invoked as `sys.executable -m sphinx`, never `uv run sphinx-build`, so the test's own venv is used.
- `unknown_visit` only warns. The node's `Text` children are still visited as ordinary inline text, which is the collapse mechanism being fixed.

### Integration Points
- A `doctest_block` reaches the translator only from `>>>`-led reST (`docutils/parsers/rst/states.py:1251`/`:1698`). `sphinx.ext.doctest` directives already build `literal_block` subclasses and are out of scope (constraint 8).
- `TrimDoctestFlagsTransform` already strips `# doctest: +FLAG` before the writer, so no translator-side trimming (constraint 8).

</code_context>

<specifics>
## Specific Ideas

- The measurement scripts behind D-01 were throwaway probes in the session scratchpad (a five-fence PDF byte/SHA comparison and a two-fence SVG per-glyph fill census). The planner may reproduce the SVG census as supporting evidence for SC1's "tag and reason" record, but the decision itself does not depend on re-running it.
- Many other `>>>` docstrings exist under `typsphinx/` (e.g. `builder.py`, `writer.py`). Only those autodoc actually renders into `docs/source` appear in the build. That is expected, not a gap: TRN-01 is a translator fix, not a docstring sweep.

</specifics>

<deferred>
## Deferred Ideas

None came up in discussion. The phase stayed within scope.

### Reviewed Todos (not folded)
- `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`: touches `typsphinx/translator.py`, but constraint 7's scope fence limits `typsphinx/` changes to the handler and docstring text. Stays pending.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md`: that is QUA-08, deferred to Future at v0.9.5. Not this phase.
- `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`: NUM-01. Only its disclosure is in this milestone's scope, via REL-16 in Phase 75, and it is not fixed here.

</deferred>

---

*Phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docstring-rest-errors*
*Context gathered: 2026-09-19*
