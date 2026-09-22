# Phase 74: The `doctest_block` Handler, Its Real-Compile Gate, and the Docstring reST Errors - Research

**Researched:** 2026-09-19
**Domain:** docutils/Sphinx translator node-handler addition (`typsphinx/translator.py`), real-`typst.compile()` acceptance gating, autodoc/napoleon docstring reST hygiene
**Confidence:** HIGH (every load-bearing claim below is `[VERIFIED: ...]` against this repo's own `.venv`, this repo's own `git`/`gh` state, or a scratch reproduction built from this repo's own source — no external package research was needed; this phase introduces zero new dependencies)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Language tag (SC1 "the tag chosen and the reason")**
- **D-01 — The handler-supplied fence language is python, not pycon.** Measured 2026-09-19 with typst-py from the main checkout's `.venv` (not transcribed from the roadmap). The same two-prompt doctest fragment was compiled under five fences. `pycon`, no tag, `text` and a nonexistent `bogusxyz` all produced a **byte-identical** PDF (11531 bytes, SHA-256 prefix `5428a015b02591d5`). Only `python` differed (12654 bytes, `9bb09e20e0d2d05a`). An SVG compile counted per glyph: under `pycon` all 58 glyphs were `#000000`. Under `python`, the 28-character function name was blue `#4b69c6`, the 24 string-literal characters green `#198810`, `>>>` red `#d73948`, and the 3 punctuation glyphs black. `@preview/codly-languages:0.1.10`'s `lib.typ` has a `python` entry (name "Python", Python icon, `#306998`) and **zero** `pycon` entries. So `pycon` gives neither syntax highlighting nor the codly language label, while `python` gives both. The known trade-off, accepted by the owner: output lines are coloured as Python source rather than as console output. In the measured example `'index.typ'` comes out green as a string literal.
- **D-02 — A non-empty language already on the node is honoured, and python applies only when it is empty.** Standard Sphinx never sets `language` on a `doctest_block`: `HighlightLanguageTransform` only assigns it to `literal_block`. So in every build this project measures, the tag is the handler's own `python`. That satisfies SC1's "supplied by the handler itself rather than read from `node['language']`" in intent. The honour path only matters if a third-party extension has written a value, and the owner chose not to overwrite that. `highlight_language` / `.. highlight::` are deliberately **not** followed. Sphinx's own HTML path reads a `doctest_block` as `'default'` and `sphinx/highlighting.py:148-151` rewrites any `>>>`-led source under `'default'`/python-ish languages to `pycon`, so a fixed tag is the same behaviour Sphinx has.

**Handler implementation shape**
- **D-03 — The python fallback lives in the language-resolution line of the literal-block visitor, and the doctree is not mutated.** Today `visit_literal_block` reads the language with a bare `node.get("language", "")`. That becomes: use the node's language if non-empty, otherwise `"python"` when the node is a `nodes.doctest_block`, otherwise empty as before. The handler never writes `node["language"]`. Because the fallback is keyed on the node class, every `literal_block` keeps exactly the code path and output it has today. The doctest block shares everything else the literal-block visitor already does, with no second copy: `_emit_id_anchors`, the `in_list_item` / `list_item_needs_separator` separator, the list-item `{ }` wrapper, `codly(number-format: none)`, `in_literal_block` (so `visit_Text` emits the raw text unwrapped), and the depart-side fence close and separator re-arm.
- **D-04 — Explicit delegating methods with docstrings, not a class-attribute alias.** Add `visit_doctest_block(self, node: nodes.doctest_block) -> None` and `depart_doctest_block(...)`, each a one-line delegation to the literal-block visitor or departer. Their docstrings name TRN-01 and note that the shape is the one Sphinx's own writers use (html5's delegating call; latex/texinfo's alias). The `node` annotations of `visit_literal_block` / `depart_literal_block` widen to `nodes.literal_block | nodes.doctest_block`, because `doctest_block` is not a `literal_block` subclass. This keeps `mypy typsphinx/` honest.
- **D-05 — The literal-block path is proven unchanged by a whole-tree diff of the base and tip `-b typst` output.** SC1/SC3 already require a clean base build at `PHASE_BASE_SHA` and a clean tip build. Their complete output trees are diffed, and the phase evidence records that **every** differing hunk falls in one of two classes: a doctest-example region (TRN-01) or the rendered output of a docstring that QUA-14's census fixed. Any other differing hunk is a finding, not noise. The existing literal-block render gates (codly config leak, caption, offset, etc.) also stay green as part of the full suite, but that is not the whole proof.

### Claude's Discretion
The owner discussed only the two areas above. For the other two gray areas presented, the owner accepted Claude's defaults within the ROADMAP constraints:

- **QUA-14 fix granularity.** Make the minimal reST repair to each docstring the base census names: add the missing blank line before a bullet list, and fix continuation indentation. Keep the documented meaning and prose as they are, and don't rewrite or restyle beyond what clears the message. No new regression test is added for this message class. A docs warnings gate is explicitly Future (`REQUIREMENTS.md` § Future), and Phase 75 SC4 re-proves the zero by measurement. The census is the base build's own `LC_ALL=C` output over the whole tree (constraint 6), not the `visit_toctree` docstring alone. A census hit in any other `typsphinx/` docstring is fixed the same way.
- **GATE-01 fixture structure.** Follow `tests/test_inline_image_separator_render_gate.py`: one new `tests/test_*_render_gate.py` module, with one synthetic fixture project under `tests/fixtures/<name>/` carrying both contexts; a single module-scoped `sys.executable -m sphinx -b typstpdf` build shared by all test methods; text-mode utf-8 reads. Context (a) is a `>>>` block in plain paragraph position. Context (b) is a napoleon/field-body or definition-list `Examples:` shape with the doctest block at a **non-first** position in its container, so the separator discipline is exercised. The assertions are: the `.typ` line structure (prompts, continuation and output on separate lines inside a ` ```python ` fence); the absence of `unknown node type: <doctest_block` in the build's captured output; the real compile succeeding, with a PDF written. pypdf text extraction is optional. The RED transcript is taken at a commit without the handler and quoted verbatim in the phase evidence. A small unit test in the existing translator-test style may additionally pin D-02's honour path, which no Sphinx build exercises; this is at the planner's discretion.

### Deferred Ideas (OUT OF SCOPE)
None came up in discussion. The phase stayed within scope.

**Reviewed Todos (not folded):** `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` (MSG-06, stays pending — scope fence forbids absorbing it even though it touches `typsphinx/translator.py`); `2026-07-22-add-sphinx-linkcheck-ci-job.md` (QUA-08, Future); `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` (NUM-01, only its disclosure is in scope, via REL-16 in Phase 75).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TRN-01 | `>>>` renders as a codly-styled code block with a handler-supplied language tag instead of falling through `unknown_visit()`. | Exact code sites confirmed (§ Code Sites). `doctest_block` confirmed NOT a `literal_block` subclass — mypy accepts the D-04 widened union (§ Type Widening). Base build reproduced byte-for-byte: `build succeeded, 5 warnings.`, 2 `unknown node type: <doctest_block` lines, `api/index.typ:811` single `text(...)` run (§ Base Build). |
| TRN-02 | Both autodoc-produced contexts (plain paragraph; definition-list/field-body, non-first position) are covered by a recorded-RED, real-compile GATE-01 fixture. | **Direct measurement contradicts the CONTEXT/REQUIREMENTS claim that this project's own `api/index.typ` reproduces a `terms.item(...)` shape** — see § Contradictions. `in_list_item`/`list_item_needs_separator` is set only by `visit_list_item`, never by `visit_definition`/`visit_field_body` (§ Contradictions). A live 4-context scratch fixture shows context (a) is a **real compile fatal** pre-handler when followed by more content, while (b)/(c)/(d) all compile (RED is content-assertion only) — § Fixture Contexts. |
| QUA-14 | Zero docutils `Unexpected indentation`/`Block quote ends` messages from typsphinx's own docstrings; build total does not rise. | Base census reproduced exactly (3 attributed messages, `visit_toctree` docstring lines 5/6/21). **A previously-unknown phantom pair (4 additional terse, unattributed console lines) traced to a third-party plugin's internal throwaway parse of an imported-but-unrendered `quote_path` symbol** — § Census Nuance. This does not count toward the "N warnings" total and carries no file:line attribution in the raw console text. |
</phase_requirements>

## Summary

This phase adds one missing docutils node handler (`doctest_block`) by delegating wholesale to the
already-correct `visit_literal_block`/`depart_literal_block`, exactly as D-03/D-04 specify — and
every piece of that plan checks out against the real code: `doctest_block` and `literal_block` are
sibling subclasses of `FixedTextElement` (confirmed via a live `docutils.nodes` import in this
repo's `.venv`), `visit_literal_block` reads only `.get()`-style attributes off `node` (never
`node.parent`, never an `isinstance` check that would need widening), and `mypy --strict` accepts
the `nodes.literal_block | nodes.doctest_block` union D-04 calls for. The base build was reproduced
twice, byte-for-byte identical in every emitted `.typ` file (only `.doctrees/environment.pickle` and
`.doctrees/changelog.doctree` — build-cache artifacts, never compared — differ between two clean
runs), which directly supports D-05's whole-tree-diff proof technique.

Two things measured in this session are NOT what CONTEXT.md/REQUIREMENTS.md describe, and are
reported in a dedicated section below rather than worked around silently. First, this project's own
`api/index.typ` does **not** currently contain a `terms.item(...)` call anywhere near either existing
doctest_block warning — both occurrences sit inside a `.. rubric:: Examples` + sibling-paragraph
shape (napoleon's default, non-admonition rendering of a Google-style `Examples:` section), which is
structurally closer to "plain paragraph position" than to "definition-list/field-body position."
Second, the translator's `in_list_item`/`list_item_needs_separator` separator protocol — the one
named in TRN-02's SC2 text as what a definition-list/field-body fixture "respects" — is wired
**only** through `visit_list_item`/`depart_list_item` (bullet/enumerated list items); a genuine
`definition` or `field_body` container never sets `in_list_item = True`, so a fixture literally built
as a definition-list or field-list will exercise a *different* separator mechanism than the one
named. A synthetic bullet-list-item fixture is the one that genuinely exercises the named mechanism.

A live 4-context scratch reproduction (plain paragraph with trailing content; bullet-list item,
non-first; definition list; field list) run against the **current, pre-handler** translator shows all
four still let `sphinx-build -b typst` complete and write `.typ` (RED is a content/line-structure
assertion, matching GATE-01's expected shape) — **except** the plain-paragraph context, which is a
real `-b typstpdf` compile fatal (`TypstError: expected semicolon or line break`) whenever anything
follows the doctest block in the same container, because `unknown_visit`/`unknown_departure` emit
zero separator characters. This is a genuinely stronger RED transcript than a content-only assertion,
and D-03's wholesale delegation is expected to fix it as a side effect (literal_block's own
`depart_literal_block` unconditionally emits a trailing `"\n"`, which is sufficient Typst statement
separation) — worth building the context-(a) fixture with trailing content specifically to capture
that compile-fatal RED, then re-observe on the fixed tree that it becomes a real PDF.

For QUA-14, the base build's raw console output contains **10** total "Unexpected
indentation"/"Block quote ends" substring hits, not the 3 the roadmap's baseline names — but 7 of
those 10 are unattributed, carry no file:line, are byte-identical whether `typsphinx.translator` is
present in `api/index.rst` at all, and do not count toward `build succeeded, N warnings.`. Root-caused
here via a stack-trace patch: they come from `sphinx-autodoc-typehints`'s internal `_inject_rtype()`
throwaway RST parse of `quote_path` (defined in `typsphinx/pathfmt.py`, imported into both
`typsphinx.builder` and `typsphinx.writer`'s namespaces) — a member that is evaluated as a
documentation *candidate* but never actually rendered (imported members are excluded by default).
The roadmap's own baseline (3 messages, all attributed to `visit_toctree`) is correct **if and only
if** the census greps for attributed lines; a naive `LC_ALL=C grep -c "Unexpected indentation"` over
the raw log would overcount by exactly this phantom pair, doubled.

**Primary recommendation:** implement exactly per D-01..D-05 (delegate wholesale, no doctree
mutation, explicit delegating methods, widened type annotation); build the TRN-02 context-(b) GATE-01
fixture as a **bullet-list item** (which genuinely exercises `in_list_item`/`list_item_needs_separator`)
rather than a literal definition-list, and record — as part of the phase's decision trail — that the
`terms.item(...)` claim was checked and found not to match this project's current output; scope
QUA-14's census grep to **attributed** docutils messages (path-qualified, ending `[docutils]`) so the
`quote_path` phantom pair is not mistakenly folded into the fix list or the "N warnings" comparison.

## Contradictions With Locked Decisions

> Per the untrusted-input-boundary / research-verification protocol: these are measured facts that
> conflict with claims in CONTEXT.md and/or REQUIREMENTS.md/ROADMAP.md. They are reported here,
> not silently worked around. Neither concerns D-01..D-05 themselves (which are about the handler's
> own shape and remain correct as decided) — both concern the *supporting factual claims* about what
> this project's docs currently produce, which the planner needs accurately to design the TRN-02
> fixture and the QUA-14 census filter.

### 1. The `terms.item(text("Examples:"), {...})` shape is NOT what this project's own `api/index.typ` currently emits

**Claim (CONTEXT.md § Decisions, D-03 preamble; REQUIREMENTS.md TRN-02):** "a definition-list /
field-body position — the `terms.item(text("Examples:"), {...})` shape measured in the 2026-09-13
sphinx-autoapi run and reproduced in this project's own `api/index.typ`."

**Measured (this session, `.venv/bin/python3 -m sphinx -b typst docs/source <scratch>`, then `grep`):**

```
$ grep -c "terms\.item" <scratch>/api/index.typ
0
$ sed -n '805,812p' <scratch>/api/index.typ
strong(text("Returns") + text(": "))
text("The relative path to hand to Typst's ") + raw("#include()") + text(".")
})

strong({text("Examples")})
linebreak()
text(">>> compute_content_include_path("", "index.typ") 'index.typ' >>> compute_content_include_path("manuals", "guide/index.typ") '../guide/index.typ' >>> compute_content_include_path("guide", "guide/index.typ") 'index.typ'")})
```

`terms.item(...)` DOES appear twice elsewhere in this project's build (`examples/index.typ`,
`user_guide/index.typ`) — but both are ordinary toctree-glossary definition lists with zero
relationship to any doctest_block. Both existing doctest_block warnings
(`compute_content_include_path`, `compute_template_import_path`, `typsphinx/writer.py`) sit inside a
`.. rubric:: Examples` (napoleon's default, non-admonition rendering of a Google-style `Examples:`
section — confirmed by reading `typsphinx.translator`'s own docstring for `visit_toctree`, which
contains a literal `.. rubric:: Notes` the author wrote, and by the `strong({text(...)})` +
`linebreak()` shape matching a rubric heading, not a field/definition entry) followed by the doctest
block as an ordinary **sibling** inside the enclosing `desc_content` — the SAME container class as
"plain paragraph position" (context a), not a definition-list or field-body (context b).

**Recommendation:** do not try to reproduce this claim from this project's own docs. Build the
context-(b) fixture as a **synthetic** construct instead (see § Fixture Contexts below for the
concrete, verified reST). Note the correction in the phase's decision record so a future reader does
not go looking for a `terms.item(...)`-shaped doctest_block in this project's real output.

### 2. `in_list_item` / `list_item_needs_separator` is never set by a definition-list or field-body container

**Claim (ROADMAP.md Phase 74 SC2):** "In (b) it respects the same separator discipline
`visit_literal_block` applies via `in_list_item` / `list_item_needs_separator`... a missing separator
would juxtapose the block with the preceding code-mode expression."

**Measured (read `typsphinx/translator.py`, this session):** `self.in_list_item = True` is assigned
in exactly one place, `visit_list_item` (line 2386, restored via a stack in `depart_list_item`,
line ~2429). `visit_definition_list_item` (line 2782) is a bare `pass`. `visit_definition` (line
2862) swaps `self.body` to `current_definition_buffer` but never touches `in_list_item`.
`visit_field_body` (line 7479) drives its own `_in_field_body`/`_field_body_has_content` inline-concat
machinery, also never touching `in_list_item`. A live scratch build confirms this: a doctest block
placed inside a definition-list `definition` (after a leading paragraph) or inside a field-list
`field_body` (`:Example:`) both compile successfully pre-handler with the SAME
`unknown_visit`/no-separator fallback that crashes the plain-paragraph case (see next section) —
because `depart_paragraph`'s own unconditional trailing blank line already provides adequate spacing
independent of `in_list_item`.

**Recommendation:** if the planner wants the GATE-01 context-(b) fixture to genuinely exercise
`in_list_item`/`list_item_needs_separator` (as ROADMAP's SC2 prose says it should), build it as a
**bullet-list item** containing a leading paragraph then the doctest block (a real, simple, valid
reST construct — `- First paragraph.\n\n  >>> code\n  result\n`), not a literal definition list or
field list. If instead the planner wants to stay literally within "definition-list / field-body"
wording, build a definition-list fixture but record explicitly (during RED recording) which separator
mechanism actually governs that position, since it is provably not `in_list_item`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `doctest_block` → Typst code-block emission | Translator (`typsphinx/translator.py`, docutils-node-visitor tier) | — | This is a pure doctree→markup translation concern; no builder/writer/config involvement beyond what `literal_block` already has |
| GATE-01 real-compile acceptance | Test tier (`tests/test_*_render_gate.py` + `typst-py` compile) | Builder (`sphinx-build -b typstpdf` subprocess) | Matches the standing v0.6.0-era pattern; the builder is invoked as a subprocess, never mocked |
| Docstring reST hygiene (QUA-14) | Source tier (docstrings inside `typsphinx/*.py`) | Sphinx/autodoc/napoleon (consumer, not owner) | The defect is in the RST the docstring author wrote, not in any Sphinx/napoleon/autodoc configuration; the fix is a text edit, never a filter or `-W` exemption |
| Docs measurement (base/tip clean builds) | CI/local build tooling (`sphinx-build`/`tox`) | — | Not a runtime-code concern; purely an evidence-gathering step |

## Code Sites

Every location below was opened with `Read`/`grep -n` in this session against the checked-out tree
(no assumption from CONTEXT.md's line numbers, which are confirmed accurate).

- **`visit_literal_block`** — `typsphinx/translator.py:2431-2574`. `[VERIFIED: typsphinx/translator.py:2431]`
- **`depart_literal_block`** — `typsphinx/translator.py:2576-2614`. `[VERIFIED: typsphinx/translator.py:2576]`
- **The language-resolution line** — `typsphinx/translator.py:2570`: `language = node.get("language", "")`. `[VERIFIED: typsphinx/translator.py:2570]`
- **`visit_Text`'s `in_literal_block` branch** — `typsphinx/translator.py:1790-1806` (`if self.in_literal_block: self.add_text(text_content); return`). `[VERIFIED: typsphinx/translator.py:1790-1806]`
- **`unknown_visit`** — `typsphinx/translator.py:5819-5828` (`logger.warning(f"unknown node type: {node}")`, no `raise`, continues). `[VERIFIED: typsphinx/translator.py:5819]`
- **`TypstTranslator.visit_toctree`'s docstring** — `typsphinx/translator.py:5415-5461` (the QUA-14 site: docstring-relative lines 5/6/21 map to file lines 5421/5422/~5437). `[VERIFIED: typsphinx/translator.py:5415-5461]`
- **`compute_content_include_path`** — `typsphinx/writer.py:32-68`, its `Examples:` section at `:59-65`. `[VERIFIED: typsphinx/writer.py:32-68]`
- **`compute_template_import_path`** — `typsphinx/writer.py:79-113`, its `Examples:` section at `:107-111`. `[VERIFIED: typsphinx/writer.py:79-113]`

### Every attribute `visit_literal_block`/`depart_literal_block` reads off `node`

`[VERIFIED: typsphinx/translator.py:2431-2614]` — the ONLY attribute reads inside these two methods
(confirmed by `sed -n '2431,2614p' typsphinx/translator.py | grep -n "node\."`) are:

- `node.get("linenos", False)` (line ~2521)
- `node.get("highlight_args", {})` (line ~2526)
- `node.get("language", "")` (line 2570)
- `_emit_id_anchors(node)`, which internally reads `node.get("ids")` only — its own signature is
  already `node: nodes.Node` (generic), so it needs **no** widening for D-04.

**None** of these methods reads `node.parent`, and none does an `isinstance(node, ...)` check on
`node` itself. The one place in the whole file that reads `isinstance(child, nodes.literal_block)`
is `visit_container` (line 1390), checking a **child of a `literal-block-wrapper` container** to
extract a `:name:` label — this is exclusively the `.. code-block:: :name:` captioned-block path,
which a parser-level `doctest_block` can never enter (no directive processes it), so this check is
correctly out of scope and needs no widening (matches ROADMAP constraint 8: adjacent mechanisms
already measured working). `[VERIFIED: typsphinx/translator.py:1370-1394]`

**Conclusion for the planner:** every attribute this pair of methods reads is accessed via `.get()`
with a default, which works identically on any `docutils.nodes.Element` subclass regardless of type.
D-03's "shares everything else... with no second copy" claim is fully supported by direct reading —
there is no hidden `isinstance`/`node.parent` dependency that would make a `doctest_block` behave
differently from a `literal_block` inside these two methods.

## Type Widening (D-04)

`[VERIFIED: live `.venv/bin/python3` import + `mypy --strict` in this repo's `.venv`]`

```python
from docutils import nodes
nodes.doctest_block.__mro__   # (doctest_block, General, Body, FixedTextElement, TextElement, Element, Node, object)
nodes.literal_block.__mro__   # (literal_block, General, Body, FixedTextElement, TextElement, Element, Node, object)
issubclass(nodes.doctest_block, nodes.literal_block)  # False
```

`doctest_block` and `literal_block` are **sibling** subclasses of `FixedTextElement`, confirming
D-04's premise that the widened annotation `nodes.literal_block | nodes.doctest_block` is required
(a bare `nodes.literal_block` annotation would not type-check for a `doctest_block` argument). A
scratch file with exactly this signature shape, run through `mypy --strict`, reports
`Success: no issues found in 1 source file` — the widened union type-checks cleanly, and this
project's actual `mypy` config (`pyproject.toml`, `[[tool.mypy.overrides]] module = ["typsphinx.*"]`)
is at least as permissive, so `mypy typsphinx/` (the phase's own gate) will accept it too.

## Base Build (measured this session, context only — plans re-measure at `PHASE_BASE_SHA`)

`[VERIFIED: .venv/bin/python3 -m sphinx -b typst docs/source <scratch>, LC_ALL=C, rm -rf'd output dir, run twice]`

**Command used (recommended form — see § Worktree Docs-Extra Gap for why):**
```
LC_ALL=C .venv/bin/python3 -m sphinx -b typst docs/source <scratch-dir>
```
This matches the GATE-01 test convention (`sys.executable -m sphinx`, never `uv run sphinx-build`),
avoids the NixOS PATH-shadowing hazard CLAUDE.md documents for bare CLI tools, and matches SC1's own
acceptance wording (`sphinx-build -b typst docs/source <tmp>`) exactly modulo the `-m sphinx` spelling.

**Result, reproduced byte-for-byte across two independent clean runs:**
```
build succeeded, 5 warnings.
```
- `unknown node type: <doctest_block` count: **2** (both in `api/index`, at
  `compute_content_include_path` and `compute_template_import_path`).
- `api/index.typ:811` carries the single collapsed run:
  `text(">>> compute_content_include_path(\"\", \"index.typ\") 'index.typ' >>> compute_content_include_path(\"manuals\", \"guide/index.typ\") '../guide/index.typ' >>> compute_content_include_path(\"guide\", \"guide/index.typ\") 'index.typ'")` — three `>>>` prompts, their continuations and outputs all on one physical `.typ` line, exactly as REQUIREMENTS.md TRN-01 describes.
- Attributed docutils messages (QUA-14 class), exact verbatim:
  ```
  /home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
  /home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
  /home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
  ```
  This matches REQUIREMENTS.md's stated 2026-09-16 baseline (3 messages, all attributed to
  `visit_toctree`) **exactly** — the roadmap's own baseline is correct for the counted/attributed set.
- Interpreter: `.venv/pyvenv.cfg` → `home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`, `version_info = 3.13.13`; `sphinx==9.1.0`, `docutils==0.22.4`, `typst==0.15.0`.

### Determinism of the whole-tree diff (D-05)

`[VERIFIED: two independent clean builds, LC_ALL=C diff -rq]`

Two clean builds of the same commit, into two separate scratch directories, produced **byte-identical
console output** (`diff <(grep -E "ERROR|WARNING" build1.log) <(grep -E "ERROR|WARNING" build2.log)`
is empty) and a tree that differs in **exactly two files**, both build-cache metadata, never part of
D-05's proof surface:
```
$ LC_ALL=C diff -rq <build1> <build2>
Files <build1>/.doctrees/changelog.doctree and <build2>/.doctrees/changelog.doctree differ
Files <build1>/.doctrees/environment.pickle and <build2>/.doctrees/environment.pickle differ
```
No `.typ` file, no `_template/` bundle file, and no other `.doctrees/*.doctree` differed.

**Recommendation:** run the whole-tree diff as
`LC_ALL=C diff -rq --exclude=.doctrees <base-dir> <tip-dir>` (or explicitly filter out `.doctrees/`
post-hoc), and every differing hunk found is a genuine content difference to classify per D-05.
`diff` exits `1` when differences exist — never wrap this in `VAR="$(diff ...)" && ...`; capture
output with `diff ... > file.txt; status=$?` or an `if diff ...; then ... fi` form instead.

## Worktree Docs-Extra Gap

`[VERIFIED: pyproject.toml, docs/source/conf.py, live import check]`

`docs/source/conf.py`'s `extensions` list requires `sphinx_autodoc_typehints` and `myst_parser`
(both confirmed importable in the main checkout's `.venv`), both declared **only** under the
`docs` extra (`pyproject.toml:49-54`), never under `dev`. CLAUDE.md's mandatory worktree
provisioning line is `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` — a bare
`dev`-only sync — so a worktree venv provisioned per that standing rule **cannot** run any docs
build at all (`ModuleNotFoundError` on `sphinx_autodoc_typehints` or `myst_parser`).

**Recommendation:** for any task in this phase that needs a clean `-b typst`/`-b typstpdf` build of
`docs/source` (the base/tip measurements for SC1 and SC3), provision with the **superset**:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```
This is a strict superset of the standing rule (adds the `docs` extra on top, does not remove `dev`),
so it satisfies both the mandatory rule and the build's needs in the same venv/interpreter used for
the rest of the phase's gates — no second `.tox` environment to separately track. This mirrors the
already-documented ROADMAP constraint 11 precedent (the CHANGELOG page gate has the identical
`dev`-lacks-`docs` problem). Do **not** run a bare `uv sync --extra dev` a second time afterward in
the same venv (it would not remove `docs`, since `uv sync` without `--exact` is additive, but there
is no reason to re-narrow it either). Do **not** run this in the **main checkout** (per the existing
memory/CLAUDE.md warning: an exact sync there drops the docs extra it currently carries) — this
applies to worktree venvs only.

An alternative, `tox -e docs-pdf` (`tox.ini:75-81`), creates its **own** separate tox-managed venv
with `extras = docs` (no `dev`), independent of the phase's main venv. This works too and is what CI
effectively exercises, but introduces a second interpreter to separately record (`pyvenv.cfg`) and
does not use the `sys.executable -m sphinx` invocation style the GATE-01 tests already use — the
`uv sync --extra dev --extra docs` + `python -m sphinx` route above is recommended as the more
consistent choice, but either is defensible.

## Fixture Contexts (TRN-02)

`[VERIFIED: scratch 4-context reST fixture built against typsphinx's own .venv, this session, both `-b typst` and `-b typstpdf`]`

A single scratch `index.rst` with four sections was built against the **pre-handler** (current)
translator:

```rst
Context A: plain paragraph
---------------------------

Some text before.

>>> 1 + 1
2

Some text after.

Context B: bullet list item, non-first position
--------------------------------------------------

- First paragraph in the item.

  >>> 1 + 1
  2

  Trailing paragraph in the same item.

Context C: definition list
----------------------------

term
    First paragraph of definition.

    >>> 1 + 1
    2

Context D: field list
-----------------------

:Example:
    >>> 1 + 1
    2
```

`-b typst` (write-only) succeeds for all four (`build succeeded, 4 warnings.`, one `unknown node
type` per context). Their emitted `.typ` bodies, verbatim:

```
Context A: text(">>> 1 + 1 2")par({text("Some text after.")})
Context B: list({ parbreak() text("First paragraph in the item.") text(">>> 1 + 1 2") parbreak() text("Trailing paragraph in the same item.") })
Context C: terms(separator: linebreak(), terms.item(text("term"), {par({text("First paragraph of definition.")}) text(">>> 1 + 1 2")}))
Context D: pad(left: 2.5em, {strong(text("Example") + text(": ")) text(">>> 1 + 1 2") })
```

`-b typstpdf` (real compile) on **Context A alone** fails outright:
```
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: expected semicolon or line break
Details: expected semicolon or line break
```
This is because `text(">>> 1 + 1 2")` and the following `par({...})` land on the **same physical
output line with zero separating characters** — `unknown_visit`/`unknown_departure` emit nothing at
all, unlike a real `literal_block`, whose `depart_literal_block` unconditionally emits a trailing
`"\n"` in the non-list, non-captioned case (`typsphinx/translator.py`, the `else:` branch ending
`self.add_text("\n")`). Rebuilding with Context A removed, Contexts B+C+D alone **do** compile
(`build succeeded, 3 warnings.`, `Generated PDF: .../fixture.pdf`) — confirming the RED for B/C/D is
purely a content/line-structure assertion, never a compile crash, while A is a genuine compile fatal.

**Recommendation:** build the context-(a) GATE-01 fixture with **trailing content after the doctest
block in the same container** (not merely a lone `>>>` block with nothing following) — this captures
the stronger, real `typst.compile()`-failure RED transcript (matching constraint 3's real-compile bar
even more directly than a content-only RED would), and gives a concrete, high-confidence prediction
that D-03's wholesale delegation fixes it as a side effect of reusing `depart_literal_block`'s
existing trailing-newline emission (worth confirming empirically once the handler lands, not assumed).
Build context-(b) as the **bullet-list-item** shape (Context B above), non-first position, per the
§ Contradictions recommendation — it is simple, realistic, and demonstrably exercises
`in_list_item`/`list_item_needs_separator`.

## QUA-14 Census Nuance

`[VERIFIED: stack-trace patch on docutils.utils.Reporter.system_message, this session, against this project's real `docs/source` build]`

The base build's **raw** console text contains 10 total lines matching "Unexpected indentation" or
"Block quote ends" (`LC_ALL=C grep -c` over each pattern, summed) — not 3. Bisection (progressively
narrowing `docs/source/api/index.rst`'s `automodule` directives, then a stack-trace patch on
`docutils.utils.Reporter.system_message` to capture the caller) attributes the extra 4 unattributed,
file-less lines (2 ERROR + 2 WARNING, appearing identically **twice**) to `sphinx_autodoc_typehints`'s
internal `_inject_rtype()` call chain:

```
sphinx/ext/autodoc/_dynamic/_loader.py:_load_object_by_name
  -> sphinx/ext/autodoc/_dynamic/_docstrings.py:_process_docstrings (events.emit "autodoc-process-docstring")
    -> sphinx_autodoc_typehints/__init__.py:_inject_types_to_docstring -> _inject_rtype
      -> sphinx_autodoc_typehints/_formats/_sphinx.py:get_rtype_insert_info -> _safe_parse
        -> a throwaway docutils Parser().parse() on the accumulated docstring lines
```

A traced run confirms the member name at the point of the warning: `typsphinx.builder::quote_path`
and `typsphinx.writer::quote_path` — **not** any member actually defined in `typsphinx.translator`,
`typsphinx.builder`, or `typsphinx.writer`. `quote_path` is defined in `typsphinx/pathfmt.py:46` and
imported into both `builder.py` and `writer.py`'s namespaces (`from typsphinx.pathfmt import
quote_path`). It is gathered as a documentable-member *candidate* during autodoc's member-discovery
pass (which triggers the `autodoc-process-docstring` event, and therefore
`sphinx-autodoc-typehints`'s probe-parse, for every name in the module's namespace) but is then
**excluded** from the final rendered page (imported members are excluded by default; confirmed —
`grep -c quote_path api/index.typ` is `0`). The probe-parse's own system-message output goes straight
to the docutils reporter (bypassing Sphinx's attributed-warning logging pipeline entirely, since the
parse result itself is discarded after `_safe_parse` extracts insertion-point info), which is why it
prints to console but carries no file:line attribution and never appears in the `build succeeded, N
warnings.` count. This reproduces deterministically (byte-identical across two clean runs, confirmed
above) and is unrelated to `quote_path`'s own docstring being malformed in any way that matters to a
real reader — the defect (a genuine, minor reST issue: a nested-bullet continuation two lines apart)
never reaches a rendered page.

**Recommendation:** scope the QUA-14 census grep to lines carrying source attribution, e.g.:
```
LC_ALL=C grep -nE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' <build.log>
```
This recovers exactly the roadmap's stated 3-message baseline and is what the "N warnings" count
actually reflects. If the planner additionally wants a defensive check against the raw substring
count changing (e.g., to catch a REAL second occurrence introduced by a future edit), record BOTH
numbers (raw substring count and attributed count) at base and tip, and treat the raw count as
informational only unless it can be attributed to a real file:line via the same bisection/trace
technique used here — a bare, un-attributable terse line is not something a docstring text edit can
target.

## Standard Stack

No new runtime or dev dependency is introduced by this phase (ROADMAP constraint 7). No `Standard
Stack`/`Package Legitimacy Audit` table applies.

## Package Legitimacy Audit

**Not applicable.** This phase installs no new packages (no new `pyproject.toml` dependency, no new
`@preview` import). `tests/test_preview_version_sync.py`'s existing four-package lockstep
(`codly`, `codly-languages`, `mitex`, `gentle-clues`) is unaffected — the handler reuses
`visit_literal_block`'s existing codly usage wholesale, adding no new import.

## Architecture Patterns

### System Architecture Diagram

```
reST source (>>> prompt, docutils/parsers/rst/states.py:1251/:1698)
        |
        v
  docutils parser  ---builds--->  doctest_block node (sibling of literal_block,
                                    under FixedTextElement)
        |
        v
TypstTranslator.dispatch_visit (SphinxTranslator base)
        |
        +--[TODAY]--> unknown_visit()  --warns, continues--> children (Text) visited
        |                                                     as ordinary inline text
        |                                                     (no separator, no fence)
        |
        +--[THIS PHASE]--> visit_doctest_block()  --delegates-->  visit_literal_block(node)
                                                                       |
                                                                       v
                                                          language = node.get("language","")
                                                              or "python" (new fallback,
                                                               keyed on isinstance check)
                                                                       |
                                                                       v
                                                          ```<language>\n<raw text>\n```\n
                                                          (codly-styled fence, same
                                                           in_list_item / separator
                                                           discipline as literal_block)
                                                                       |
                                                                       v
                                                          depart_doctest_block() --delegates-->
                                                              depart_literal_block(node)
```

### Recommended Project Structure

No new files/directories beyond the new test module + fixture project:
```
typsphinx/
└── translator.py                # + visit_doctest_block/depart_doctest_block (D-04),
                                  #   language-line fallback (D-03), docstring fixes (QUA-14)
tests/
├── test_<name>_render_gate.py   # new GATE-01 module (naming at planner's discretion,
│                                #   e.g. test_doctest_block_render_gate.py)
└── fixtures/
    └── <name>/                  # new synthetic fixture project, both TRN-02 contexts
```

### Pattern 1: Delegate-wholesale node handler (this repo's own established pattern)

**What:** a new node type that should render identically to an existing one gets two one-line
methods that call the existing visitor/departer directly, rather than a duplicated implementation.
**When to use:** the new node is a sibling/variant of an already-correctly-handled node and shares
every emission concern (separators, fences, ids, list-item wrapping).
**Example (Sphinx's own precedent, confirmed via a live `sphinx` install in this repo's `.venv`):**
```python
# sphinx/writers/latex.py:2324 (installed package, this repo's .venv)
visit_doctest_block = visit_literal_block

# sphinx/writers/html5.py:665 — a delegating call, not an alias:
def visit_doctest_block(self, node: Element) -> None:
    self.visit_literal_block(node)
```
D-04 explicitly chooses the html5-style delegating-call-with-docstring shape over the latex-style
bare alias, specifically so each method can carry its own TRN-01-referencing docstring and its own
(differently widened, in the depart case unchanged) type annotation.

### Anti-Patterns to Avoid

- **Mutating the doctree to set `node["language"]`:** D-03 explicitly forbids this — the fallback
  lives in the *read* line (`language = node.get("language", "") or (...)`), never a write back onto
  the node. Mutating the doctree would be a side effect visible to any later transform/writer pass
  over the same node and is unnecessary since the read-side fallback is sufficient.
- **A second, parallel code-block emission implementation for `doctest_block`:** would immediately
  create a second site to keep in sync with every future `literal_block` fix (codly config,
  `:linenos:`, captioned-block interaction, etc.) — exactly the class of drift `pathfmt.py`'s
  docstring (bug MSG-02/quote_path) and the `@preview` version-lockstep hazard (CLAUDE.md) already
  warn about elsewhere in this codebase.
- **Filtering/`-W`-exempting the QUA-14 message class instead of fixing the reST:** explicitly
  forbidden by both CONTEXT.md's discretion note and REQUIREMENTS.md's acceptance text ("not
  suppressed by a filter, a `-W` exemption, or a `# noqa`-style silencer").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Code-block emission (fence, codly config, list-item wrapping, id anchors) | A second doctest-specific emission routine | Delegate to `visit_literal_block`/`depart_literal_block` (D-03/D-04) | Already correct, already tested, already carries every separator/list-item/codly edge case this project has fixed over many phases |
| Real-compile acceptance proof | A string/regex assertion on the `.typ` output alone | `sphinx-build -b typstpdf` subprocess + `typst.compile()`/pypdf pattern (`tests/test_pdf_render_gate.py`, `tests/test_inline_image_separator_render_gate.py`) | Constraint 3 is a standing project bar since v0.6.0 Phase 11; string-only assertions have historically missed real compile fatals (v0.9.2's image bug, this phase's own Context-A finding) |
| Docstring reST fix verification | Trusting the fix "looks right" | Rebuild a scratch copy and re-grep the attributed message class | The exact reST rule that trips "Unexpected indentation" is subtle (nested-bullet continuation spacing) — verify by compiling, not by inspection |

**Key insight:** this codebase's whole node-handler history (image separators, math separators, this
phase) shows the SAME defect shape recurring: an "unhandled" or "under-handled" node emits content
with **zero** separator against its neighbors, and Typst's code-mode statement-juxtaposition rule
turns that into either a silent rendering collapse (when the following content starts a fresh
statement on its own line) or a hard compile fatal (when it lands on the same physical line, as this
phase's Context A does). Delegating to an already-separator-aware handler is not just less code, it
is the only way this project has found to inherit the fix for both symptoms at once.

## Common Pitfalls

### Pitfall 1: A naive raw-substring grep overcounts QUA-14's message classes

**What goes wrong:** `LC_ALL=C grep -c "Unexpected indentation"` over the full build log returns a
number larger than what `build succeeded, N warnings.` actually reflects, because
`sphinx-autodoc-typehints`'s internal probe-parse of an imported-but-unrendered member
(`quote_path`) emits the identical message text to console with no file attribution.
**Why it happens:** a third-party autodoc extension does its own throwaway RST parse using a fresh,
unconfigured `Reporter` that writes directly, bypassing Sphinx's attributed-warning pipeline.
**How to avoid:** filter for the **attributed** form (`<path>:docstring of <fqname>:<line>: (ERROR|WARNING): ...`) as shown in § QUA-14 Census Nuance.
**Warning signs:** a census count that doesn't match the number of `[docutils]`-suffixed lines, or a
terse `:LINE: (ERROR/N) message` line with no preceding file path anywhere on it.

### Pitfall 2: Assuming this project's "definition-list/field-body" example is `terms.item(...)`

**What goes wrong:** searching this project's own `api/index.typ` for a `terms.item(...)` call near
either doctest_block warning finds nothing, because both are actually in a rubric+sibling shape.
**Why it happens:** the referenced measurement was from a **different tool** (sphinx-autoapi) in a
**different session** (2026-09-13); it was not re-verified against this project's actual napoleon +
autodoc output before being written into CONTEXT.md/REQUIREMENTS.md.
**How to avoid:** build the context-(b) fixture as a genuinely synthetic construct (§ Fixture
Contexts), and record in the phase's own decision trail that this correction was made.
**Warning signs:** `grep -c "terms\.item" api/index.typ` returning `0`.

### Pitfall 3: Assuming a definition-list/field-body doctest block exercises `in_list_item`

**What goes wrong:** building the context-(b) GATE-01 fixture as a literal definition list or field
list and asserting on `in_list_item`/`list_item_needs_separator` behavior that never actually fires
for that container.
**Why it happens:** `visit_literal_block`'s `in_list_item` check is real and load-bearing for
**bullet/enumerated list items**, and it is natural to assume "list-like" containers (definition
lists, field lists) share the same flag — they do not; `visit_definition`/`visit_field_body` use
entirely separate buffering/concat mechanisms.
**How to avoid:** use a bullet-list-item fixture for genuinely exercising this mechanism (§
Contradictions #2).
**Warning signs:** a RED assertion that never becomes a compile fatal or content-collapse in a
definition-list/field-body position (both already compile fine pre-handler per this session's
measurement), which would make it hard to demonstrate the separator discipline is actually needed
there.

### Pitfall 4: A worktree venv silently cannot build docs at all

**What goes wrong:** a task tries `sphinx-build -b typst docs/source <tmp>` in a worktree provisioned
only per CLAUDE.md's standing `--extra dev` rule and gets `ModuleNotFoundError:
sphinx_autodoc_typehints` (or `myst_parser`).
**Why it happens:** the standing worktree provisioning rule is scoped to running tests/lint/type
gates, none of which need the `docs` extra; the docs build needs it and CLAUDE.md's own constraint 11
already names this exact gap for a different gate (the CHANGELOG page gate).
**How to avoid:** re-sync the SAME worktree venv with the strict superset
`uv sync --extra dev --extra docs` before any docs-build task in this phase (§ Worktree Docs-Extra
Gap).
**Warning signs:** `ModuleNotFoundError` naming `myst_parser` or `sphinx_autodoc_typehints`
specifically (both `docs`-extra-only packages).

## Code Examples

### The delegating handler shape (D-04), matching Sphinx's own html5 writer precedent

```python
# Source: sphinx/writers/html5.py:665 (installed package in this repo's .venv, sphinx==9.1.0)
def visit_doctest_block(self, node: Element) -> None:
    self.visit_literal_block(node)
```

### The language-resolution fallback (D-03), as a one-line change to the existing read

```python
# typsphinx/translator.py:2570 today:
language = node.get("language", "")

# D-03's shape (illustrative — exact wording is implementation's call):
language = node.get("language", "") or (
    "python" if isinstance(node, nodes.doctest_block) else ""
)
```

### D-02's honour-path unit test, matching this repo's existing translator-test style

```python
# Source: tests/test_translator.py:1028-1044 (existing `literal_block` pattern this repo already uses)
def test_doctest_block_honours_existing_language(simple_document, mock_builder):
    from docutils import nodes
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    node = nodes.doctest_block(text=">>> 1 + 1\n2")
    node["language"] = "pycon"  # third-party-set, non-empty
    translator.visit_doctest_block(node)
    translator.visit_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_doctest_block(node)

    output = translator.astext()
    assert "```pycon" in output  # honoured, not overwritten to python


def test_doctest_block_defaults_to_python(simple_document, mock_builder):
    from docutils import nodes
    from typsphinx.translator import TypstTranslator

    translator = TypstTranslator(simple_document, mock_builder)

    node = nodes.doctest_block(text=">>> 1 + 1\n2")  # no language set
    translator.visit_doctest_block(node)
    translator.visit_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_Text(nodes.Text(">>> 1 + 1\n2"))
    translator.depart_doctest_block(node)

    output = translator.astext()
    assert "```python" in output
```

### RED-restore technique for the pre-handler translator (this repo's own v0.9.2 precedent)

```
# Source: .planning/milestones/v0.9.2-phases/62-.../62-RED-EVIDENCE.md (this repo, committed)
git checkout <PHASE_BASE_SHA> -- typsphinx/translator.py
git diff HEAD --numstat -- typsphinx/translator.py   # confirm the exact inverse of the eventual diff
uv run python -m sphinx -b typstpdf tests/fixtures/<name> <BUILD_DIR>   # non-zero exit allowed
# ... capture stdout/stderr verbatim, redact only machine-specific absolute paths ...
git checkout HEAD -- typsphinx/translator.py   # restore, never git stash
```

## State of the Art

Not applicable in the usual "library version drifted" sense — no external library version changed.
The one relevant "old vs current" fact: Sphinx's own `sphinx-autodoc-typehints` internals
(`sphinx/ext/autodoc/_dynamic/`) are a newer, refactored member-discovery pipeline (confirmed via the
live traceback captured this session, e.g. `_gather_members`, `_load_object_by_name` — module paths
that did not exist in older Sphinx autodoc versions), which is why the QUA-14 phantom-pair mechanism
traced cleanly to a specific, nameable function in this exact Sphinx 9.1.0 install; a prior Sphinx
version's autodoc internals might route the same symptom through different internal call sites, but
the *symptom* (an unattributed terse console line for a candidate-but-unrendered imported member)
would likely still exist as long as `sphinx-autodoc-typehints` keeps doing its own throwaway parse.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | D-03's wholesale delegation will, as a side effect, resolve Context A's compile fatal (via `depart_literal_block`'s existing trailing `"\n"`) once the handler lands. | § Fixture Contexts | If wrong, the context-(a) GATE-01 fixture's real-compile assertion would fail post-fix too, and the plan would need an explicit extra separator emission — low risk since the mechanism (a bare unconditional trailing newline) is simple and already reused verbatim by delegation, but not literally re-verified against the FIXED tree in this research session (fixing is execution's job). |
| A2 | The minimal QUA-14 fix for `visit_toctree`'s docstring is a blank-line/indentation correction around the nested-bullet continuation shape identified in the converted-RST dump (§ QUA-14 Census Nuance background investigation, not fully reproduced in this file). | QUA-14 fix mechanics | The exact minimal edit was not derived or verified against a real rebuild in this session (execution's job per binding ordering — census before fix, fix during execution); if the eventual fix differs in shape, no research claim here is contradicted, since none commits to a specific diff. |

**All claims not listed above are `[VERIFIED]` against this session's own tool calls (docutils/mypy
introspection, live Sphinx builds, `git`/`gh` state, `grep`/`diff` over this repo's own files) or
`[CITED: installed sphinx package source in this repo's own .venv]` for the html5/latex/texinfo
writer precedents.**

## Open Questions

1. **Should the context-(a) GATE-01 fixture assert on the compile-fatal RED, the content-collapse
   RED, or both?**
   - What we know: a lone `>>>` block with nothing following it does NOT crash pre-handler (RED is
     content-only); a `>>>` block followed by more content in the same container DOES crash
     pre-handler (a real `TypstError`).
   - What's unclear: whether the planner wants the STRONGER (compile-fatal) RED transcript as the
     primary evidence, matching how the v0.9.2 image-separator gate's own RED was a compile fatal, or
     whether a simpler no-trailing-content fixture (matching this project's own two REAL occurrences,
     which never have trailing content in the same container) is preferred for fidelity to the actual
     motivating case.
   - Recommendation: use the WITH-trailing-content version — it is a strictly stronger, more
     representative RED (matches ROADMAP constraint 3's "real compile" bar even more directly), and
     costs nothing extra to construct.

2. **Exact minimal QUA-14 diff for `visit_toctree`'s docstring.**
   - What we know: the two ERROR positions are docstring-relative lines 5 and 21 (mapping to
     `typsphinx/translator.py:5421` and roughly `:5437`), both "Unexpected indentation" at a
     nested-bullet continuation; the WARNING is line 6 (`:5422`), "Block quote ends without a blank
     line."
   - What's unclear: the precise minimal reST edit (add a blank line before a nested sub-bullet? fix
     a continuation's indent width?) was not derived and compile-verified in this research session —
     per ROADMAP's binding ordering, the census happens in this phase but the fix derivation and
     verification is execution work, re-run fresh at `PHASE_BASE_SHA`.
   - Recommendation: during execution, isolate the docstring in a scratch copy (as this research
     session did for `quote_path`), try the minimal blank-line/indent fix, and confirm via a real
     rebuild that both the ERROR and WARNING disappear and the total warning count does not rise.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `sphinx` | All docs builds, GATE-01 | ✓ | 9.1.0 | — |
| `docutils` | Node/message classes | ✓ | 0.22.4 (pinned `>=0.21,<0.23`) | — |
| `typst` (typst-py) | Real-compile gate | ✓ | 0.15.0 | — |
| `myst_parser`, `sphinx_autodoc_typehints`, `furo`, `sphinx-intl` (`docs` extra) | Any `docs/source` build | ✓ in main `.venv`; ✗ in a bare `--extra dev` worktree venv | per `pyproject.toml` `docs` extra | Re-sync worktree venv with `--extra dev --extra docs` (§ Worktree Docs-Extra Gap) |
| `ruff` (bare CLI) | Local lint gate | ✓, but ONLY via the NixOS FHS shim on PATH (`ruff` resolved to a `typsphinx-fhs-run`-wrapping script this session); `python -m ruff` bypasses the shim and fails with a dynamic-linking error | 0.16.x (per `pyproject.toml` range) | Always invoke bare `ruff`, never `python -m ruff`, on this maintainer's NixOS machine |
| `gh` CLI | Branch-protection/CI-dispatch reads | ✓, authenticated as `YuSabo90002` | 2.100.0 | — |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** the `docs` extra in a freshly-provisioned worktree venv (see
above).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x (per `pyproject.toml` `dev` extra range `>=8.4,<10`), config in `pyproject.toml` |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, not separately verified line-by-line this session — matches existing project convention) |
| Quick run command | `uv run pytest tests/test_<name>_render_gate.py -x` (new module); `uv run pytest tests/test_translator.py -x` (unit test) |
| Full suite command | `uv run pytest` (main `.venv` measured this session: **1547 passed, 1 skipped** in ~129-131s; the one skip is `tests/test_corpus_gate.py:530`, env-gated on `TYPSPHINX_CORPUS_REPORT=1`, unrelated to this phase) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TRN-01 | `doctest_block` renders as a codly-styled fence with a non-empty language tag | unit + render-gate | `uv run pytest tests/test_translator.py -k doctest_block` / `uv run pytest tests/test_<name>_render_gate.py` | ❌ Wave 0 (both new) |
| TRN-02 | Both contexts (plain paragraph; non-first-position list/definition/field-body) compile via real `typst.compile()`, recorded RED first | render-gate | `uv run pytest tests/test_<name>_render_gate.py` | ❌ Wave 0 |
| QUA-14 | Zero attributed `Unexpected indentation`/`Block quote ends` messages from `typsphinx/` docstrings; total warnings not risen | manual/scripted build + `LC_ALL=C grep` (not a pytest test — no automated regression test added, per Claude's Discretion in CONTEXT.md) | `LC_ALL=C uv run python -m sphinx -b typst docs/source <tmp>` + attributed-line grep (§ QUA-14 Census Nuance) | N/A — evidence file, not a test |

### Sampling Rate
- **Per task commit:** the new render-gate test file/method being worked on, plus `uv run pytest tests/test_translator.py` (fast, no Sphinx subprocess).
- **Per wave merge:** `uv run pytest` (full suite).
- **Phase gate:** full suite green, plus the base/tip clean-build evidence, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_<name>_render_gate.py` — covers TRN-01/TRN-02 (module name at planner's discretion; e.g. `test_doctest_block_render_gate.py`)
- [ ] `tests/fixtures/<name>/` — the synthetic fixture project carrying both TRN-02 contexts (recommend a bullet-list-item shape for context b, per § Contradictions #2)
- [ ] Framework install: none — pytest/typst-py/sphinx are all already present in `dev`+base dependencies; no new install needed for the render-gate test itself (only the docs-build evidence tasks need the `docs` extra re-sync)

## Security Domain

`security_enforcement` is enabled (`.planning/config.json`); ASVS review is required.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No auth surface in this phase |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | The "input" is reST/docstring text already fully trusted (this project's own source tree and its own docs/source tree — not user-supplied at runtime); no new external input path is introduced |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst code-injection via unescaped doctest content | Tampering | Already mitigated identically to `literal_block`: `in_literal_block` emits raw text UNESCAPED inside a fenced code block (` ```lang ... ``` `), which is Typst's own raw-block semantics — this is the SAME trust model `literal_block` has used since v0.6.0 Phase 11, not a new exposure. The content originates from the project's own reST/docstring source, never from an end-user request at render time. |

No new threat surface is introduced: the handler reuses an existing, already-reviewed emission path
verbatim (D-03), and the docstring fix (QUA-14) only touches this project's own maintainer-authored
source text, never external input.

## Sources

### Primary (HIGH confidence — measured this session)
- `typsphinx/translator.py` (this repo, read directly) — all code-site line numbers, `visit_literal_block`/`depart_literal_block`/`unknown_visit`/`visit_toctree`/`visit_definition*`/`visit_field_*`/`visit_list_item` bodies
- `typsphinx/writer.py` (this repo, read directly) — `compute_content_include_path`/`compute_template_import_path` docstrings
- Live `docutils.nodes` introspection in this repo's `.venv` — `doctest_block`/`literal_block` MRO and subclass relationship
- Live `mypy --strict` run in this repo's `.venv` — widened-union type-check
- Live `sphinx-build -b typst`/`-b typstpdf` runs (this repo's own `docs/source`, and a scratch 4-context fixture) — base build reproduction, determinism check, compile-fatal discovery
- A `docutils.utils.Reporter.system_message` stack-trace patch (scratch script, this session) — root-caused the QUA-14 phantom pair to `sphinx_autodoc_typehints`
- `tests/test_inline_image_separator_render_gate.py`, `tests/test_translator.py` (this repo, read directly) — GATE-01 and unit-test patterns
- `.planning/milestones/v0.9.2-phases/62-.../62-RED-EVIDENCE.md` (this repo, read directly) — the `git checkout <SHA> -- <file>` RED-restore technique
- `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks` (live, read-only GET) — current required-checks list
- `git branch --list/-r`, `git rev-parse HEAD` (live) — branch/decoy census

### Secondary (MEDIUM confidence)
- Installed `sphinx` package source (`sphinx/writers/html5.py`, `.../latex.py`) in this repo's `.venv` — the delegating-vs-alias precedent (CITED, not modified/re-verified beyond direct reading)

### Tertiary (LOW confidence)
- None — no WebSearch-only claims were needed for this phase; it is entirely an in-repo translator/docstring change with zero new external dependencies.

## Metadata

**Confidence breakdown:**
- Standard stack: N/A — no new stack introduced
- Architecture (D-03/D-04 delegation shape): HIGH — directly confirmed against live code and a live Sphinx install
- TRN-02 fixture contexts: HIGH — directly measured via a live 4-context scratch build, including the compile-fatal discovery
- QUA-14 census: HIGH — root-caused via a live stack-trace patch, not guessed
- The two Contradictions sections: HIGH — both are direct, repeatable `grep`/build measurements against this project's own real output

**Research date:** 2026-09-19
**Valid until:** until `docs/source/api/index.rst`, `typsphinx/writer.py`'s two `Examples:` docstrings, `typsphinx/pathfmt.py`'s `quote_path` docstring, or the `sphinx`/`sphinx-autodoc-typehints`/`docutils` pinned versions change — none of which this phase is expected to touch except the two files this phase edits by design (`typsphinx/translator.py`'s docstring fixes). The base-build numbers here are explicitly restated as context-only; every plan re-measures at its own `PHASE_BASE_SHA` per binding constraint 4.
