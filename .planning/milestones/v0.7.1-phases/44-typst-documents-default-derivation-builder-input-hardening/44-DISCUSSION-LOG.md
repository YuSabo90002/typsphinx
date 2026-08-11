# Phase 44: `typst_documents` Default Derivation + Builder Input Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-04
**Phase:** 44-typst-documents-default-derivation-builder-input-hardening
**Areas discussed:** Degenerate project names, Derived entry shape, Derivation wiring site, Explicit empty list, Scope of the recorded user-visible change

---

## Gray area selection

Four areas were offered; three were selected.

| Option | Description | Selected |
|--------|-------------|----------|
| Degenerate project names | `make_filename_from_project()` collapses non-ASCII names to the `'sphinx'` sentinel — accept verbatim or fall back | ✓ |
| Explicit empty list | What `typst_documents = []` means once unset can never be empty, and what the warning should say | ✓ |
| BLD-01 error shape and validation width | Aggregate into `failures` vs. immediate raise; non-`str` docname only vs. broader entry-shape validation | |
| Scope of the recorded user-visible change | SC#4's before/after record: filename only, or filename plus the content change | ✓ |

---

## Degenerate project names

Measured before asking (Sphinx 9.1.0): `make_filename_from_project()` removes a trailing
`' Documentation'`, deletes every character matching `[^a-zA-Z0-9_-]`, lowercases, and returns
`'sphinx'` when the result is empty. `'日本語 プロジェクト'` → `'sphinx'`, `'Проект'` → `'sphinx'`,
`'ドキュメント v1'` → `'v1'`, `'MyApp Documentation'` → `'myapp'`.

| Option | Description | Selected |
|--------|-------------|----------|
| Accept the sentinel verbatim | Identical to the LaTeX builder; a Japanese-named project gets `sphinx.typ` just as it already gets `sphinx.tex`. One line, no branch. | ✓ |
| Fall back to `root_doc` on degradation | Japanese-named projects would keep `index.typ`, narrowing the rename's blast radius; breaks LaTeX consistency and adds a branch plus tests. | |
| Fall back plus a warning | Same fallback with a `logger.warning` explaining the name; would make `-W` builds of non-ASCII-named projects fail until they add config. | |

**User's choice:** Accept the sentinel verbatim ("latex の仕様に合わせる").
**Notes:** Became the governing principle for the rest of the discussion.

---

## Derived entry shape

Measured before asking: typsphinx reads only `entry[0]` and `entry[1]` — `writer.py:68`,
`builder.py:118`, `builder.py:165-166`, `builder.py:928` are the complete set of indexed accesses.
`docs/source/user_guide/configuration.rst` nevertheless publishes a 5-element contract.

| Option | Description | Selected |
|--------|-------------|----------|
| 5 elements (matches the published contract) | `(root_doc, '<project>.typ', project, author, 'typst')`; matches `docs/source/conf.py`'s own style and is copy-pasteable, but creates three values nothing reads. | |
| 4 elements | Matches CONF-08's wording (`root_doc`, `project`, `author`) exactly; LaTeX's 5th element is `latex_theme`, which typsphinx has no analogue for in this tuple. | |
| 2 elements | Only what is actually read; diverges visibly from the published 5-element contract. | |

**User's choice:** Free text — "documents が書かれているときは documents 優先で配線できないか？
いずれにせよ latex と仕様を合わせたい."
**Notes:** Measured the premise instead of answering from memory. Sphinx's `LaTeXBuilder` **does**
consume `entry[2]`/`entry[3]`: `write_documents()` destructures
`docname, targetname, title, author, themename = entry[:5]` and feeds `update_doc_context(title,
author, theme)` and `docsettings._title` / `._author`; `init_document_data()` keeps `entry[2]` in
`self.titles`. So the user's instinct matched LaTeX's real behaviour. This reframed the question as a
scope question, asked next.

---

## Wiring explicit `entry[2]`/`entry[3]` (scope decision)

Measured blast radius: of 104 `typst_documents` entries in the repo, only 5 have
`entry[2] != project` (`examples/advanced`, `integration_basic`, `integration_sibling`,
`template_named_dir_master`, `tests/roots/test-basic`).

| Option | Description | Selected |
|--------|-------------|----------|
| Fold into Phase 44 as a new requirement | Amend REQUIREMENTS/ROADMAP mid-discussion as Phase 43 did for FIG-01; derive 5 elements and actually consume explicit title/author. Grounded in PROJECT.md's core value. Cost: two user-visible changes in one patch release. | |
| Match the shape only, file the wiring as a todo | Derive the LaTeX-shaped 5-tuple now; record the missing consumption, with its measurements, as a todo outside v0.7.1. Keeps v0.7.1's user-visible change list at one item. | ✓ |
| Wire it but derive only 4 elements | Wire consumption now while refusing to emit a 5th element that has no meaning in typsphinx's code. | |

**User's choice:** Match the shape only, file the wiring as a todo.
**Notes:** Todo created at
`.planning/todos/pending/2026-08-04-typst-documents-title-author-elements-ignored.md`, carrying the
LaTeX destructuring, the complete list of typsphinx's indexed accesses, and the 5-entry blast radius.

---

## Explicit empty list

| Option | Description | Selected |
|--------|-------------|----------|
| Opt-out; keep `WARNING`, fix the wording only | Severity unchanged so `-W` builds keep failing, matching LaTeX's `no "latex_documents" config value found` warning; new text says the setting is present and empty. | ✓ |
| Opt-out; demote to `logger.info` | Treats an explicit empty list as deliberate; lets a `-b typst`-only user pass `-W` CI. Diverges from LaTeX. | |
| Treat an empty list as unset and derive anyway | Strongest "a PDF always appears" guarantee, but contradicts SC#2 — writing `[]` is also an explicit setting — and LaTeX does not behave this way. | |

**User's choice:** Opt-out; keep the warning, fix the wording only.

---

## Derivation wiring site

Verified live before asking, with typsphinx's own registration signature
(`app.add_config_value(name, <callable>, "html", [list])`): a callable default passes type
validation, unset yields the derived list, and an explicit `[]` yields `[]`.

| Option | Description | Selected |
|--------|-------------|----------|
| Callable default (same registration LaTeX uses) | Every reader — `writer.py:55`, `builder.py:117`, `builder.py:160`, `builder.py:904` — sees the same resolved value automatically. One function plus one registration line, no branches. `-b typst` gets the rename and templating too (the roadmap's accepted cost). | ✓ |
| Materialize at `config-inited` | Value is burned into the config so third-party readers see one identity; adds a handler and its priority to manage and diverges from LaTeX. | |
| Resolve in a builder-local helper | Leaves `config.typst_documents` empty for external tools; missing one of the four call sites would silently desynchronize the writer's untemplated `index.typ` from `finish()`'s lookup of `<project>.typ`. | |

**User's choice:** Callable default.

---

## Scope of the recorded user-visible change (SC#4)

Measured before asking, on a real build with no `typst_documents`: exit 0, one `WARNING`, zero PDFs,
and `out/index.typ` at 373 bytes containing imports plus body with **no template applied** (because
`_is_master_document` returns False). That file does compile standalone — `typst.compile()` produced
an 8209-byte PDF. After the change: `mycoolproject.typ` + `mycoolproject.pdf`, fully templated.

| Option | Description | Selected |
|--------|-------------|----------|
| Filename and content change both | Records that the emitted `.typ` changes structure, not just name — lets the CHANGELOG explain how a user who `#include`s the old `index.typ` is affected. | ✓ |
| Filename only | Matches SC#4 / CONF-08 wording literally; smallest CHANGELOG surface. | |
| Both plus a migration recipe | Adds a copy-pasteable `conf.py` snippet, plus the note that the old *content* cannot be reproduced by config (setting `typst_documents` is what makes a document a master). | |

**User's choice:** Filename and content change both.

---

## Claude's Discretion

Not selected for discussion; left to research/planning with measured grounds recorded in CONTEXT.md:

- **BLD-01's error shape and validation width** — aggregate into `failures` vs. immediate raise; and
  whether to validate only "docname is not `str`" or widen toward the entry-shape validation and
  `difflib` suggestion that Phase 22.3 deferred.
- **Which existing tests are updated and how** (SC#5's traceability requirement).
- **Where the SC#4 evidence file lives and what it is named.**
- **Whether `-b typst` alone should warn on an explicit empty list** — D-03 settled only the
  `typstpdf` path.

## Deferred Ideas

- Wiring `typst_documents` `entry[2]` / `entry[3]` into rendered output — todo filed 2026-08-04.
- Giving the 5th tuple element an actual meaning — recorded in the same todo.
- Exhaustive `typst_documents` shape validation and a `difflib` "did you mean" suggestion — still
  deferred from Phase 22.3.
- A `-b typst`-side warning for an explicit empty list.
