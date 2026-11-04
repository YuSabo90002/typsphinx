# Evidence — codebase

Repo root: /home/yuta/Documents/typsphinx
Scanned: 2026-11-04 (Audited HEAD c1606cd9ebb4f4e33a6c9301ca6e7abb39a88601, verify sidecar)
Checks run: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs` → ok (uv-managed CPython 3.14, `.venv/pyvenv.cfg` home `~/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu`); `LC_ALL=C uv run pytest -q -p no:cacheprovider` → 1897 passed, 1 skipped in 216s; `uv run black --check .` → 400 files unchanged; `uv run ruff check .` → all checks passed; `uv run mypy typsphinx/` → no issues in 10 source files; `gh release list` / `gh run list` / `gh issue list --state open` / `gh pr list --state open` (read-only) → v0.10.0 is Latest release (2026-11-03T14:34Z), Release workflow run for v0.10.0 succeeded, 0 open issues, 0 open PRs; node-coverage probe: script listing docutils/sphinx.addnodes classes with no `visit_*` on `TypstTranslator` MRO (52 names), then scratch Sphinx projects (outside the repo, under the session scratchpad) built with `uv run python -m sphinx -b typstpdf -E -q` per construct (results in findings).

## Map

- **Stack**: Python >=3.12 (classifiers 3.12/3.13/3.14), Sphinx >=9.1,<10 (9.1.1 resolved), docutils >=0.21,<0.23, typst (typst-py) >=0.15.0,<0.16; setuptools build backend; uv + uv.lock; tox (`env_list = py312, py313, py314, lint, type, cov, docs`, `requires = tox-uv~=1.35`); black 26 / ruff / mypy; pytest with `sphinx.testing` fixtures; dev-only pypdf, pillow, sphinxcontrib-bibtex (pyproject.toml:33-54, tox.ini:1-17). Version 0.10.0 (pyproject.toml:7).
- **Entry points**: `typsphinx.setup(app)` (typsphinx/__init__.py:29-80) registers `TypstBuilder`/`TypstPDFBuilder`, eleven `typst_*` config values, and a `config-inited` handler; `sphinx.builders` entry points `typst` and `typstpdf` → `typsphinx` (pyproject.toml:63-65).
- **Architecture**: builder → writer → translator → template engine. `TypstBuilder.write()` overrides Sphinx's write loop (typsphinx/builder.py:1700-1760): validates output collisions, resolves the template registry, validates keys/paths/`typst_dependencies`, then writes documents serially in sorted order via `env.get_doctree` (preserving toctree nodes). Each doc gets a content `.typ` with the `/_typsphinx/deps.typ` preamble; `typst_documents` masters additionally get a wrapper rendered by `TemplateEngine` (builder.py:2162-2190). `finish()` writes `_typsphinx/deps.typ`, copies used template bundles, warns on dependency drift; `TypstPDFBuilder.finish()` (builder.py:2721) compiles masters with typst-py. Module sizes: translator.py 8078 lines, builder.py 2858, template_engine.py 837, template_registry.py 550, writer.py 509, typst_deps.py 241, pdf.py 229 (13,692 total incl. templates).
- **Conventions**: Integration tests are subprocess gates (`tests/test_*_gate.py`, 197 entries under tests/, 170 fixture dirs) asserting on emitted `.typ`/PDF text; docs/CHANGELOG/README claims are pinned by text-asserting gates. Unknown docutils nodes go to `unknown_visit`, which logs `unknown node type: <node>` and does not skip children (translator.py:5804-5826). Long docstrings/comments cite phase/requirement ids (e.g. `Phase 54 (CONF-19)`, __init__.py:65). Commits follow GSD Path subjects: `T00N: ...`, `build: ...`, `plan: ...`, `ship: M00N — <slug>`, plus PR merges.
- **Maturity**: Full suite green on 3.14 (1897 passed / 1 skipped); lint, format and type checks clean; CI matrix ubuntu/windows/macos × 3.12/3.13/3.14 (.github/workflows/ci.yml:16-25); 0.10.0 released to GitHub/PyPI via release.yml on tag push. Scaffolding: `pre-commit` in dev extra with no `.pre-commit-config.yaml`; index entries skipped (translator.py:6515-6521); both listed under CHANGELOG `[Unreleased]` "Planned for Future Releases".
- **Recent activity**: 129 commits since 2026-10-01. M001–M007 shipped 2026-11-02..03 (release 0.9.8, externalized deps.typ, Windows test portability, codly 2.0 upgrade, housekeeping + Python 3.14, release 0.10.0, release-notes follow-up). Last product-code change: 7b6a1c63 (codly 2 code-mode emission, M004). HEAD c1606cd9 is the PR #193 merge and carries tag v0.10.0. No milestone goal was supplied in the brief for M008.

## Finding: Option lists, definition-list classifiers and production lists produce Typst that fails to compile

- **Claim**: A document containing an rST option list (`-a  option a`), a definition-list term with a classifier (`term : classifier`), or a `.. productionlist::` directive stops the `typstpdf` build with `TypstError: expected semicolon or line break`; each emits `unknown node type` warnings first. Example emitted code for an option list: `text("-a")par({text("option a")})` and `text("--bee")text("VAL")par(...)` — juxtaposed code-mode expressions with no separator; productionlist emits `strong(raw("expr"))text(" ::= ")text(...)`.
- **Source**: per-construct scratch builds (Checks run) → optlist, classifier, prod: "Typst compilation failed ... expected semicolon or line break"; emitted `index.typ` lines 8-10 for optlist; `unknown_visit` at typsphinx/translator.py:5804-5815 warns but does not skip children. No test or fixture references `option_list`, `classifier` (as a node) or `productionlist` (`grep -rln` over tests/ → only unrelated hits).
- **Confidence**: high
- **Why it matters here**: README.md:21 claims "Full support for paragraphs, sections, lists, tables, admonitions, and more"; option lists are standard in CLI docs and classifiers appear in numpy-style definition lists. Any milestone touching node coverage should treat these three as hard failures, not cosmetic warnings.

## Finding: Several other standard nodes have no visitor but still compile (content passes through unstyled)

- **Claim**: `hlist`/`hlistcol`, `sidebar`, `centered`, `acks`, and PEP 695 type parameters (`desc_type_parameter_list`, `desc_type_parameter` from `.. py:function:: ident[T](x: T)` / `.. py:class:: Box[T: int]`) each log `unknown node type` warnings but the PDF compiles. `.. option::` and `.. cpp:function::` compile with no warning.
- **Source**: scratch builds (Checks run) → "compiled OK" with warnings for hlist, sidebar, centered, acks, pep695, classtype; MRO scan reported 52 visitor-less classes in docutils.nodes + sphinx.addnodes (many are transformed away before writing, e.g. `only`, `pending`, `substitution_reference`).
- **Confidence**: high (compile result); medium (rendered appearance not inspected)
- **Why it matters here**: Every such construct adds a warning per node to a user's build; `-W` builds would fail. Sidebar title/body and hlist columns lose their structure. This is the visible coverage gap list if node support is in scope.

## Finding: The build is serial even though the extension declares parallel-write safety

- **Claim**: `setup()` returns `parallel_write_safe: True` and the builder sets `allow_parallel = True` (builder.py:702), but `TypstBuilder.write()` writes every document in a plain `for docname in sorted(docnames)` loop (builder.py:1746-1752) and never calls Sphinx's `_write_parallel`; per-build accumulators (`_used_template_keys`, builder.py:767, 2180) are mutated inside `write_doc`.
- **Source**: typsphinx/__init__.py:76-80; typsphinx/builder.py:702, 1700-1760, 2180; Sphinx 9.1.1 `Builder._write_parallel` source (child processes call `write_doc`, so state set there would not return to the parent).
- **Confidence**: high
- **Why it matters here**: `-j N` gives no write-phase speedup today, and a planner who "enables parallel writing" would silently lose bundle-copy and include-edge state unless that state moves to `write_doc_serialized` or is re-derived.

## Finding: No open issues, no open PRs, release 0.10.0 complete

- **Claim**: GitHub has 0 open issues and 0 open PRs; v0.10.0 is the Latest release and its Release, Documentation and Link Check runs succeeded; tag v0.10.0 points at HEAD c1606cd9.
- **Source**: `gh issue list --state open` → `[]`; `gh pr list --state open` → `[]`; `gh release list -L 3`; `gh run list -L 8`; `git ls-remote --tags origin v0.10.0`.
- **Confidence**: high
- **Why it matters here**: There is no external backlog driving M008; scope must come from the user. Any user-visible change now lands in `## [Unreleased]`, which today holds only "Planned for Future Releases" (CHANGELOG.md:8-13). Per LESSONS.md (006), each shipped user-facing change needs an Unreleased entry.

## Finding: Long-standing "planned" items remain unbuilt

- **Claim**: Index generation (index nodes skipped: translator.py:6515-6521) and pre-commit hooks (`pre-commit>=3.0` in dev extra, pyproject.toml:43; no `.pre-commit-config.yaml`) are unbuilt and listed as "Planned for Future Releases" in CHANGELOG `[Unreleased]`; earlier inspections (archive 002, 004, 007) recorded the same state.
- **Source**: files cited; `ls .pre-commit-config.yaml` → absent; .project/archive/002-externalize-typst-deps/research/evidence-codebase.md:54.
- **Confidence**: high
- **Why it matters here**: These are the only self-declared roadmap items in the repo; they are candidate scope only if the user picks them.

## Finding: Fresh sidecar runs on CPython 3.14, not the main checkout's interpreter

- **Claim**: The sidecar `.venv` was built on uv-managed CPython 3.14; the suite result above is a 3.14 result.
- **Source**: sidecar `.venv/pyvenv.cfg` (`version_info = 3.14`).
- **Confidence**: high
- **Why it matters here**: Test counts compared against the main checkout must account for interpreter differences (CLAUDE.md "Interpreters may differ").

## Apparent intent

- (inference) The project is a mature, released Sphinx→Typst/PDF extension in maintenance/polish mode; recent milestones were release hygiene and dependency upgrades rather than new features — based on M001–M007 slugs and the last product-code commit being M004's codly 2 work.
- (inference) Broadening rST/Sphinx node coverage is a natural next direction, since the remaining gaps (option lists, classifiers, productionlist, hlist, sidebar, PEP 695 type params) are concrete and three of them break PDF builds — based on the probe results above. Not confirmed by any issue or plan.

## Open questions for define

- What is M008's goal? No open issue, PR, carry-forward item, or brief statement names one.
- If node coverage is in scope: fix only the three compile-breaking nodes (option_list, classifier, productionlist), or also the warning-only ones (hlist, sidebar, centered, acks, PEP 695 type parameters)?
- Should unknown nodes keep warning-and-pass-through, or degrade more safely (e.g. emit children as content-mode text) so an unhandled node cannot produce non-compiling Typst?
- Do index generation and pre-commit hooks stay "planned", get built, or get removed from the Unreleased list (and `pre-commit` from the dev extra)?
- Is a release (0.10.1/0.11.0) part of this milestone, given per-milestone release-prep precedent (M001, M006)?

## Blocked areas

- none (rendered appearance of warning-only nodes not inspected visually; docs HTML/PDF builds and `tox` not run)
