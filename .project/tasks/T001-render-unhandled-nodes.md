---
id: T001
title: Render option lists, classifiers and productionlists, and make unknown_visit compile-safe
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - typsphinx/translator.py
  - tests/test_unhandled_nodes_render_gate.py
  - tests/fixtures/unhandled_nodes_render_gate
---

# T001 — Render option lists, classifiers and productionlists, and make unknown_visit compile-safe

## Context

Issue #194: at a31fd6ca, a document with an rST option list, a definition-list classifier, or a Sphinx `productionlist` makes `sphinx-build -b typstpdf` exit 2 with `TypstError: expected semicolon or line break`. Each content `.typ` body is one code-mode `#{ ... }` block; these nodes have no visitor, so `unknown_visit` (typsphinx/translator.py:5804-5815) logs `unknown node type: ...` and descends, `unknown_departure` (5817-5825) does nothing, and child expressions are juxtaposed. Observed bodies: option list → `text("-a")par({text("option a")})`, `text("-c")text("--see")text("FILE")par(...)`; classifier → `text("classifier")text("c1")text("c2")terms(...)` (classifier text lands before the whole `terms(...)` because `visit_term`/`depart_term`, translator.py:2784-2841, redirect `self.body` to a term buffer and `classifier` is a sibling of `term`); productionlist → `strong(raw("expr"))text(" ::= ")text("term (\"+\" term)*")...`. A single option between two paragraphs is enough to fail. No existing test or docs page uses these constructs. Owner rulings (INTENT.md): render option lists as `terms(...)` (4A), classifiers as `term : classifier` in italics (5A), productionlists as an aligned three-column monospace grammar with anchors (6A); keep the `unknown node type` warning (7A); add a separator fallback in `unknown_visit` (2A); existing output byte-identical (9A).

## Approach

- Read INTENT.md SC1–SC5, Edge coverage E1–E9 and Prohibitions N1–N2; they are the contract.
- Option list nodes: `option_list`, `option_list_item`, `option_group`, `option`, `option_string`, `option_argument` (its `delimiter` attribute holds `" "` or `"="`), `description`. Emit one `terms(separator: linebreak(), ...)` per list, mirroring `visit_definition_list`/`depart_definition_list` (translator.py:2598-2687): term = options as `raw(...)`, arguments as `emph(raw(...))` (or equivalent italic monospace), options of a group joined by `, `; body = description content wrapped like `_wrap_definition_arg`. Reuse the list-item separator flags (`in_list_item`, `list_item_needs_separator`) and `_emit_id_anchors` as the definition list does. Escape strings through the translator's existing string-escaping helpers (E3: `"`, `\`, `#`).
- Classifier: route each `classifier` into the current definition-list item's term (the `_deflist_items_stack` / term-buffer frame), as ` : ` + italic classifier, in source order, keeping inline markup inside (E4, E5). The term buffer is a `+`-concat code-mode context (`_CONCAT_CONTEXTS`, translator.py:1625-1650); joined pieces must stay valid there, and the term's `<label>` anchor wrap in `depart_term` must still apply.
- Productionlist: `sphinx.addnodes.productionlist` (Body element; may carry a group name) containing `production` nodes (`tokenname` attribute; rule text children, continuation productions have an empty `tokenname`). Emit a monospace three-column layout (name, `::=`, rule) with continuation lines in the rule column. Anchor each production from its node ids via `_namespace_label` / the existing anchor form so `:token:` references (resolved by Sphinx to `reference` nodes and rendered by `visit_reference`, translator.py:5542+) link to it; an unresolved `:token:` must render as plain text and the build still exit 0 (E6, E7).
- `unknown_visit`: keep the warning and the descent (text must still appear — N1, N2); add the separation that keeps juxtaposed children valid in each code-mode context the node can sit in (body paragraph, list item, table cell, term/heading concat contexts — E8). Do not change emission for any node that has a visitor (SC5, E9).
- Tests: one subprocess gate `tests/test_unhandled_nodes_render_gate.py` building fixture projects under `tests/fixtures/unhandled_nodes_render_gate/` with `sys.executable -m sphinx -b typstpdf -E` into a temp outdir under `LC_ALL=C`, asserting exit status, absence/presence of `unknown node type` warnings, `.typ` shapes, and PDF text via `pypdf`. The SC4 fixture registers a test-only node class with no Typst visitor (e.g. via a fixture-local extension calling `app.add_node` with only an HTML visitor, or a directive returning a custom `nodes.Inline, nodes.TextElement` node) placed in a paragraph, a list item, a table cell and a definition-list term/heading.
- Do not edit any pre-existing test's expected .typ assertion (SC5). Python 3.12 builtin generics; black 88; ruff; mypy clean.
- Out of scope (vetoes): hlist/hlistcol, sidebar, centered, acks, PEP 695 type-parameter nodes; any version bump; README/CHANGELOG (T002).

## Interface contract

- None

## Intent coverage

- SC1
- SC2
- SC3
- SC4
- SC5

## Acceptance criteria

1. SC1 (E1–E3): the option-list fixture (single item between two paragraphs; `-c FILE, --see=FILE` group; description with `"`, `\`, `#`) builds with `typstpdf` at exit 0 with no `unknown node type` warning for any option-list node; `index.typ` shows `terms(...)` with raw options, italic raw arguments, `, ` join and preserved delimiters; pypdf text contains every option, argument and the literal `"` `\` `#`.
2. SC2 (E4, E5): the classifier fixture builds at exit 0 with no `unknown node type` warning for `classifier`; each classifier is inside its `terms.item` term as ` : ` + italic text in source order, inline markup kept inside; PDF text shows `term : c1 : c2`.
3. SC3 (E6, E7): the productionlist fixture (group-named list, multi-`|` continuation) builds at exit 0 with no `unknown node type` warning for `productionlist`/`production`; `.typ` shows the three-column monospace grammar with continuation lines in the rule column and a per-production anchor; a resolved `:token:` emits a link to that anchor; an unresolved `:token:` is plain text and the build exits 0.
4. SC4 (E8, N1, N2): a test-only visitor-less node with two inline children in a paragraph, list item, table cell and term/heading builds at exit 0 in each placement, the `unknown node type` warning is logged, and its text appears in the PDF text.
5. SC5 (E9): no pre-existing test's expected-.typ assertion is edited (`git diff a31fd6ca -- tests/` touches only the new gate and fixtures); `LC_ALL=C uv run pytest tests/` reports 0 failed; black/ruff/mypy are clean; a clean `typstpdf` build of `docs/source` succeeds.

## Verify

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/test_unhandled_nodes_render_gate.py -v && LC_ALL=C uv run pytest tests/ -q && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/ && rm -rf docs/_build && cd docs && LC_ALL=C uv run sphinx-build -b typstpdf -E source _build/pdf
```

Heavy: yes

## Log

- 2026-11-23 — created by plan (quick lane, orchestrator-written)
