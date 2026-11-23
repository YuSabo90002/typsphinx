# Evidence — codebase

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-07 (Audited HEAD a31fd6ca45bfb1a1873f3f191ca8fb565416e2e9, verify sidecar)
Checks run: `git diff --stat c1606cd9 HEAD -- typsphinx pyproject.toml uv.lock tox.ini .github` → empty (no product, dependency or CI change since the M008 scan; M008 touched only README.md, CHANGELOG.md, docs/source/**, and 4 test files: `git diff --stat c1606cd9 HEAD`); `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` → ok (`.venv/pyvenv.cfg` home `~/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin`, `version_info = 3.14`); `LC_ALL=C uv run pytest -q -p no:cacheprovider` → 1908 passed, 1 skipped in 218s (M008 scan: 1897 passed; +11 from M008 README/docs gates); `uv run black --check .` → 401 files would be left unchanged; `uv run ruff check .` → All checks passed; `uv run mypy typsphinx/` → no issues in 10 source files; `gh issue view 194`, `gh issue list --state open`, `gh pr list --state open`, `gh release list -L 2` (read-only) → 1 open issue (#194, label `bug`, opened 2026-11-04), 0 open PRs, v0.10.0 Latest; per-construct probe: 9 scratch Sphinx projects under the session scratchpad (outside the repo) built with `LC_ALL=C uv run python -m sphinx -b typstpdf -E -q` from the sidecar (results in findings).

## Map

- **Stack**: unchanged from the M008 scan (no manifest diff): Python >=3.12 (3.12/3.13/3.14 classifiers), Sphinx >=9.1,<10, docutils >=0.21,<0.23, typst-py >=0.15.0,<0.16; setuptools backend; uv + uv.lock; tox with `tox-uv~=1.35`; black/ruff/mypy; pytest with `sphinx.testing` fixtures. Version 0.10.0 (pyproject.toml:7).
- **Entry points**: `typsphinx.setup(app)` (typsphinx/__init__.py) registers `TypstBuilder` (`typst`) and `TypstPDFBuilder` (`typstpdf`), the `typst_*` config values and a `config-inited` handler; `sphinx.builders` entry points in pyproject.toml.
- **Architecture**: builder → writer → translator → template engine. `TypstBuilder.write()` writes docs serially; each doc becomes a content `.typ` whose body is one code-mode `#{ ... }` block (observed in every probe's `index.typ`), wrappers are rendered per `typst_documents` entry, `finish()` writes `_typsphinx/deps.typ` and copies template bundles; `typstpdf` compiles masters with typst-py. Node conversion lives in typsphinx/translator.py (8078 lines, 189 `visit_`/`depart_` methods); nodes without a visitor fall to `unknown_visit` (translator.py:5804-5815), which only logs `unknown node type: <node>` and lets children be visited, and `unknown_departure` (translator.py:5817-5825), which does nothing.
- **Conventions**: integration tests are subprocess gates (`tests/test_*_gate.py`; 199 entries under tests/, 170 fixture dirs under tests/fixtures/) that build a fixture project with `sys.executable -m sphinx` and assert on emitted `.typ`/PDF text and warnings. Code-mode separation is handled per context with flags such as `list_item_needs_separator` and `_in_term` (translator.py:769, 2618-2620, 2804) — the translator's own comments cite the "expected semicolon or line break" error as the failure mode they guard (translator.py:2609-2617). Comments cite phase/requirement/bug ids. Commit subjects follow GSD Path (`T00N: ...`, `build: ...`, `plan: ...`, `ship: M00N — <slug>`) plus PR merges.
- **Maturity**: full suite green (1908 passed, 1 skipped) on CPython 3.14; lint/format/type clean; CI matrix ubuntu/windows/macos × 3.12/3.13/3.14 (.github/workflows/ci.yml:17-18). Unbuilt self-declared items unchanged: index generation, pre-commit hooks, "Additional Typst Universe template integration" under CHANGELOG `[Unreleased]` "Planned for Future Releases" (CHANGELOG.md:13-16).
- **Recent activity**: since the M008 scan (c1606cd9), only M008 (readme-simplify) commits: 28433758 T001 (manual additions), 28d0e7d9 T002 (README rewrite + gates + CHANGELOG bullet), ship 979cca2e, PR #195 merge a31fd6ca (2026-11-05). Last product-code change remains 7b6a1c63 (M004 codly 2). CHANGELOG `[Unreleased]` now holds one `### Documentation` bullet (CHANGELOG.md:10-11).

## Finding: Issue #194 still reproduces at HEAD — option lists, classifiers and productionlist fail the PDF compile

- **Claim**: At a31fd6ca each of three constructs makes `typstpdf` exit 2 with `TypstError: expected semicolon or line break`. Emitted code-mode bodies: option list → `text("-a")par({text("option a")})`, `text("-c")text("--see")text("FILE")par(...)`; classifier → `text("classifier")text("c1")text("c2")terms(...)`; productionlist → `strong(raw("expr"))text(" ::= ")text("term (\"+\" term)*")text(" ")text("         ")text("| other")text(" ")`. Warnings logged (typst builder): `option_list`, `option_list_item`, `option_group`, `option`, `option_string`, `option_argument`, `description`; `classifier`; `productionlist`, `production`. A one-option list between two paragraphs is enough to fail (`mixed` probe).
- **Source**: probe builds `optlist`, `classifier`, `prod`, `mixed` (Checks run) → rc=2, `ExtensionError: typstpdf: 1 master document(s) failed`; `gh issue view 194` body matches these outputs; translator.py:5804-5825 (`unknown_visit`/`unknown_departure`).
- **Confidence**: high
- **Why it matters here**: #194 is the only open issue and the only external backlog item. Its reproduction is unchanged from the M008 evidence, so any plan can take the issue's emitted-code examples as the failing baseline. `grep -rln 'option_list\|productionlist\|classifier'` over tests/ finds no coverage, and docs/source/ uses none of these constructs, so neither the suite nor the dogfood `tox -e docs-pdf` build would catch a regression.

## Finding: Classifier text is emitted outside and before the `terms(...)` call, not inside the term

- **Claim**: `visit_term` redirects `self.body` to a term buffer and `depart_term` restores it (translator.py:2784-2830). A `classifier` is a sibling of `term` inside `definition_list_item`, so its `Text` child is visited after the body is restored and lands in the outer body, while `terms(...)` is only emitted at `depart_definition_list`. Result: all classifiers of the list appear concatenated before the whole `terms(...)` expression.
- **Source**: `classifier` probe `index.typ` (`text("classifier")text("c1")text("c2")terms(separator: linebreak(), terms.item(text("term"), ...), terms.item(text("term2"), ...))`); translator.py:2598-2640, 2764-2830.
- **Confidence**: high
- **Why it matters here**: Fixing only the separator (e.g. a generic unknown-node newline) would compile but would still print classifiers detached from their terms and in the wrong place. A correct fix has to route classifier content into the term buffer (or a dedicated slot) of the current definition-list frame.

## Finding: Warning-only nodes compile but lose or distort structure

- **Claim**: `hlist`/`hlistcol`, `sidebar`, `centered`, `acks`, and `desc_type_parameter_list`/`desc_type_parameter` each log `unknown node type` and the PDF compiles (rc=0). Observed output: hlist with `:columns: 2` becomes two separate `list(...)` calls (columns lost); the sidebar title becomes `heading(depth: 1, {text("Side")})` (a real top-level heading, which will enter the PDF outline); `.. py:function:: ident[T](x: T)` renders `raw("ident")` then `raw("T")` with no brackets.
- **Source**: probe builds `hlist`, `sidebar`, `centered`, `acks`, `pep695` → rc=0, warnings as listed; their `index.typ` content.
- **Confidence**: high (compile result and emitted code); medium (rendered PDF appearance not inspected visually)
- **Why it matters here**: #194's "Additional Context" lists these nodes; `-W` builds fail on them. The sidebar-as-heading effect was not recorded in the M008 evidence and changes the document outline, so it is more than a cosmetic warning.

## Finding: The only generic fallback is warn-and-descend, with no content-mode safety net

- **Claim**: `unknown_visit` neither raises `SkipNode` nor emits a separator or wrapper; `unknown_departure` is a no-op. Because the body is a single code-mode block, any unhandled node whose children produce two consecutive inline expressions yields juxtaposed calls, which Typst rejects. Known visitors avoid this through context-specific separator flags rather than a shared mechanism (translator.py:2609-2620 comment cites the same error at "GATE-02 fatal #8").
- **Source**: translator.py:5804-5825, 2609-2620; probe outputs above.
- **Confidence**: high
- **Why it matters here**: Whether M009 adds visitors for named nodes only or also changes the fallback (e.g. newline separation, or wrapping unknown-node content) is a design choice with test-surface consequences: a fallback change affects every visitor-less node, including ones transformed away in practice.

## Finding: Carried state from the M008 scan, unchanged at HEAD

- **Claim**: No product code changed since c1606cd9, so these M008 observations still hold: the write loop is serial despite `parallel_write_safe: True` / `allow_parallel = True` (builder.py:702, 1746-1752); index nodes are skipped (translator.py:6515-6521); `pre-commit>=3.0` is in the dev extra with no `.pre-commit-config.yaml`.
- **Source**: empty `git diff --stat c1606cd9 HEAD -- typsphinx pyproject.toml uv.lock tox.ini .github`; .project/archive/008-readme-simplify/research/evidence-codebase.md.
- **Confidence**: high
- **Why it matters here**: Planners need not re-derive these; they remain candidate scope only if the user picks them.

## Finding: CHANGELOG `[Unreleased]` already carries an M008 entry; no release is pending

- **Claim**: `[Unreleased]` holds `### Documentation` "README simplified: ..." (CHANGELOG.md:10-11) above "Planned for Future Releases"; the compare link is `v0.10.0...HEAD` (CHANGELOG.md:1677). v0.10.0 is the Latest release.
- **Source**: CHANGELOG.md:8-16, 1677; `gh release list -L 2`.
- **Confidence**: high
- **Why it matters here**: A #194 fix is a user-visible bug fix and, per LESSONS.md (006), needs its own `[Unreleased]` entry (likely a `### Fixed` section next to the existing `### Documentation`).

## Finding: Sidecar runs on CPython 3.14

- **Claim**: The sidecar `.venv` uses uv-managed CPython 3.14; the suite result above is a 3.14 result. Issue #194 was reported on Python 3.13.13; the probe reproduces identically on 3.14.
- **Source**: `.venv/pyvenv.cfg`; `gh issue view 194` Environment block.
- **Confidence**: high
- **Why it matters here**: Test-count comparisons with the main checkout must account for the interpreter (CLAUDE.md "Interpreters may differ").

## Apparent intent

- (inference) M009 is likely to address issue #194 — it is the only open issue, labelled `bug`, filed by the maintainer the day after the M008 scan reported the same probe results — based on `gh issue list --state open` and the issue body matching the M008 evidence verbatim in structure.
- (inference) The project stays in maintenance/polish mode; node-coverage completeness is the visible remaining product gap — based on M001–M008 slugs and no product-code change since M004.

## Open questions for define

- Scope of #194: the three compile-breaking constructs only, or also the warning-only nodes (hlist, sidebar, centered, acks, PEP 695 type parameters) named in its Additional Context?
- Fix shape: dedicated visitors per node, a safer generic `unknown_visit` fallback, or both? Should unknown nodes keep warning?
- Rendering targets: how should option lists render (table-like two columns, `terms(...)`, other)? Classifier style (e.g. `term : classifier` in italics, as HTML/LaTeX do)? Productionlist as a monospace grammar block with aligned `::=`?
- Should the sidebar title stop being emitted as a real `heading(depth: 1, ...)` (it enters the outline)?
- Does the fix need a docs/manual mention (supported-constructs list) and a release (0.10.1) in this milestone, or only an `[Unreleased]` `### Fixed` entry?
- Should issue #194 be closed by the integration PR (e.g. `Fixes #194` in the PR body)? Note per LESSONS.md (001) that issue closure happens after merge and cannot be a success criterion.

## Blocked areas

- none (rendered PDF appearance of warning-only nodes not inspected visually; `tox` and docs HTML/PDF builds not run)
