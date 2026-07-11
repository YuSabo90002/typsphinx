# Phase 7 Plan 01 — Deferred Items

Out-of-scope discoveries found during Task 3's empirical `docs-pdf` compile / visual glance.
Not fixed here per the SCOPE BOUNDARY rule (issue is pre-existing and lives in a file not in
this plan's `files_modified` list).

## 1. Admonitions render literal Typst source instead of typeset prose

**Discovered during:** Task 3, coarse D-01/D-04 visual glance of the compiled `docs/_build/pdf/index.pdf`.

**Symptom:** Every `.. note::` / admonition whose paragraph contains any inline markup (or
even a single plain-text run) renders as literal, unevaluated Typst source text in the PDF,
e.g. page 10 of the compiled docs shows:

```
par({text("This setting only applies to local custom templates (") raw("typst_template")
text(").nTypst Universe packages (") raw("typst_package") text(") handle assets
automatically.")})
```

instead of the intended rendered sentence.

**Root cause (not fixed):** `typsphinx/translator.py::_visit_admonition` opens the gentle-clues
call using Typst markup-mode brackets (`info[`, `warning[`, etc.), but the paragraph content
inside is emitted by `visit_paragraph`/`visit_Text` using the "unified code mode" `par({...})`
function-call form (no `#` prefix). Inside `[...]` markup-mode content, `par({...})` is not
re-entered as code — it prints as literal characters. This is orthogonal to the `@preview`
package versions bumped by this plan; it reproduces with any gentle-clues/mitex/codly version
because it is a Typst markup-vs-code-mode mismatch in the translator's own admonition/paragraph
interaction.

**Evidence it predates this phase:** `git blame` on the `.. note::` block that exposed the bug
(`docs/source/user_guide/configuration.rst:116-119`) shows it was added 2025-11-01, and
`typsphinx/translator.py`'s `_visit_admonition`/`visit_note`/`visit_paragraph` methods are
untouched by any commit in this phase (07-01 touched only `pyproject.toml`, `uv.lock`,
`typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`).
`docs-pdf` never successfully compiled before this phase's `kai` fix landed, so this
long-standing bug was never visible in a rendered PDF until now.

**Occurrences found in the compiled docs (4 total):**
- `docs/source/user_guide/configuration.rst` — the `typst_template_assets` note
- `docs/source/user_guide/templates.rst` — a similar note
- `typsphinx/translator.py` docstrings (2x) — surfaced via the auto-generated API reference
  (`docs/source/api/`), both single-`text()`-only notes

**Suggested next step:** A follow-up phase/plan should fix `_visit_admonition` (and/or
`visit_paragraph`) to either (a) prefix the injected content with `#` to re-enter code mode
inside `[...]`, or (b) switch gentle-clues invocation to pure function-call form
(`info(par({...}))`) so it stays in code mode throughout. This is a translator behavior change
affecting all admonitions project-wide — out of scope for this atomic version-bump plan
(Rule 4 architectural-change territory, not a version-string edit).

**Disposition:** Not blocking Phase 7 Plan 01. The plan's hard gate (`tox -e docs-pdf` exits 0
with zero `TypstError`, no `unknown variable: kai`) is satisfied — this is a rendering-content
bug, not a compile error. Per D-01/D-04, the coarse visual glance targets "no blank/broken
boxes, no missing-glyph tofu, no error glyphs" specifically as a backstop against regressions
*introduced by the package bump*; this bug predates the bump and is unrelated to it.
