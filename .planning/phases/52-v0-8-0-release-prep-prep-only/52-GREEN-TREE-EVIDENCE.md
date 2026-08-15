# Phase 52 — Green-Tree Evidence (Local Half of SC#3)

**Provisioning note:** all commands below were run inside this plan's isolated git worktree
(`.claude/worktrees/agent-ad418208b39cc9bf9`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, per this project's
`CLAUDE.md` § "Worktree-isolated execution". Every command below was invoked through `uv run`.
Tree state confirmed before any command ran: `pyproject.toml` `version = "0.8.0"`,
`CHANGELOG.md` carries exactly one `## [0.8.0]` heading (`grep -c` returned `1`) — waves 1
(52-01, version bump) and 2 (52-02 CHANGELOG, 52-03 D-10 gate) have merged back onto this
worktree's base commit `aaeec80439c7b5f0dfe5e0d64f4af83bd0550b3e`.

Per D-08's authority split, **this file records no claim of authority for pytest, `black`,
`ruff`, or `mypy`** — the dispatched CI run plan 52-04 collects is the authority for those
(and for the OS matrix, which local Linux-only runs cannot exercise). This file covers exactly
what CI structurally does not: both docs builds, the full-corpus `-b typstpdf` GATE-02 gate, and
an honest local suite spot-check.

---

## Local evidence — docs builds

### tox -e docs-html

Command:
```
$ uv run --extra dev tox -e docs-html
```

Environment provisioning (via `uv-venv-lock-runner`, `extras = docs`):
```
docs-html: venv> uv venv -p .venv/bin/python --allow-existing '--prompt=agent-ad418208b39cc9bf9[docs-html]' --python-preference system .tox/docs-html
docs-html: uv-sync> uv sync --locked --python-preference system --extra docs -p .venv/bin/python
docs-html: commands[0] docs> sphinx-build -b html source _build/html
```

Build transcript (translated log lines shown in original Japanese locale; structurally
identical to the English CI equivalent):
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
loading intersphinx inventory 'python' from https://docs.python.org/3/objects.inv ...
loading intersphinx inventory 'sphinx' from https://www.sphinx-doc.org/en/master/objects.inv ...
ビルド中 [mo]: 更新された 0 件のpoファイル
ビルド中 [html]: 更新された 14 件のソースファイル
環境データを更新中[新しい設定] 14 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[  7%] api/index
  ... (progresses through all 14 source files: api/index, changelog, contributing,
       examples/advanced, examples/basic, examples/index, index, installation,
       quickstart, user_guide/builders, user_guide/configuration, user_guide/index,
       user_guide/output_layout, user_guide/templates)
```

Interleaved with the source read: a `sphinx_autodoc_typehints/_parser.py:30:
RemovedInSphinx10Warning: 'sphinx_autodoc_typehints._parser._RstSnippetParser.set_application'
is deprecated` (upstream `sphinx-autodoc-typehints` deprecation notice, unrelated to typsphinx)
repeats **203 times** (`grep -c RemovedInSphinx10Warning`, exact count), once per
autodoc-processed member — elided here as noise; every occurrence is byte-identical. This is
more than Phase 46's 102 occurrences on the same 13→14-file corpus proportionally, consistent
with the larger API surface this milestone's two-layer output split added.

Docstring warnings (pre-existing, unrelated to this plan's scope — `visit_toctree`'s own
docstring, a known carried item tracked as WR-01 in `47-REVIEW.md`, not touched by this plan):
```
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
```

Consistency-check notices (expected — several docs are deliberately cross-listed in more than
one toctree; Sphinx picks the first for the HTML nav tree, unrelated to typsphinx's own output):
```
整合性をチェック中... .../docs/source/examples/advanced.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/advanced
.../docs/source/examples/basic.rst: document is referenced in multiple toctrees: ['examples/index', 'index'], selecting: index <- examples/basic
.../docs/source/user_guide/builders.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/builders
.../docs/source/user_guide/configuration.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/configuration
.../docs/source/user_guide/templates.rst: document is referenced in multiple toctrees: ['index', 'user_guide/index'], selecting: user_guide/index <- user_guide/templates
完了
```

Final lines:
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.78=setup[0.13]+cmd[3.65] seconds)
  congratulations :) (3.83 seconds)
```

Exit code: `0`. `build succeeded` present, `docs-html: OK` present.

### tox -e docs-pdf

Command:
```
$ uv run --extra dev tox -e docs-pdf
```

Transcript follows the same shape as `docs-html` (same 14 source files, same 203x
`RemovedInSphinx10Warning` upstream noise, same three pre-existing `visit_toctree` docstring
warnings, same five multiple-toctree consistency notices), diverging at the PDF-specific tail:
```
docs-pdf: commands[0] docs> sphinx-build -b typstpdf source _build/pdf
...
preparing documents... Template written to .../docs/_build/pdf/_template.typ
done
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
'index.typ'
>>> compute_content_include_path("manuals", "guide/index.typ")
'../guide/index.typ'
>>> compute_content_include_path("guide", "guide/index.typ")
'index.typ'</doctest_block>
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path_for_dir("")
'_template.typ'
>>> compute_template_import_path_for_dir("manuals")
'../_template.typ'
>>> compute_template_import_path_for_dir("a/b")
'../../_template.typ'</doctest_block>
writing output... [api/index] done
writing output... [changelog] done
writing output... [contributing] done
writing output... [examples/advanced] done
writing output... [examples/basic] done
writing output... [examples/index] done
writing output... [index] done
writing output... [installation] done
writing output... [quickstart] done
writing output... [user_guide/builders] done
writing output... [user_guide/configuration] done
writing output... [user_guide/index] done
writing output... [user_guide/output_layout] done
writing output... [user_guide/templates] done
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.11=setup[0.11]+cmd[4.00] seconds)
  congratulations :) (4.16 seconds)
```

The two `WARNING: unknown node type: <doctest_block ...>` lines are Sphinx `doctest` directives
in `docs/source/user_guide/output_layout.rst` (`>>> compute_content_include_path(...)` and
`>>> compute_template_import_path_for_dir(...)` REPL examples) that `typsphinx`'s translator has
no `visit_doctest_block` handler for and degrades gracefully rather than aborting — the two
extra warnings beyond `docs-html`'s 3 (5 total). This is a graceful-degradation warning, not a
compile fatal; the build still exits 0 and produces a complete PDF.

Exit code: `0`. `build succeeded` present, `docs-pdf: OK` present, generated PDF path named.

### Produced PDF

Command:
```
$ stat -c '%s' docs/_build/pdf/typsphinx.pdf
```
Verbatim output:
```
2614546
```

`docs/_build/pdf/typsphinx.pdf` exists, **2,614,546 bytes** — well over the 100,000-byte floor
this task's acceptance criteria set, and larger than Phase 46's 2,452,632-byte v0.7.1 English
PDF, consistent with this milestone's larger 14-document corpus.

First-page text and page count, extracted via `pypdf` (not assumed):
```python
from pypdf import PdfReader
r = PdfReader('docs/_build/pdf/typsphinx.pdf')
print('pages:', len(r.pages))
print(repr(r.pages[0].extract_text()[:300]))
```
Verbatim output:
```
pages: 128
'typsphinx\nYuSabo\n0.8.0\n1'
```

The title page reads project `typsphinx`, author `YuSabo`, and version **`0.8.0`** — the exact
post-bump version this phase's Task 1 (52-01) landed — confirming the PDF is a real,
128-page, non-empty artifact produced by this project's own `typstpdf` builder rather than an
empty stub, and that the version bump actually reached the rendered document metadata.

Repo cleanliness check (the build wrote only into the gitignored `_build` tree):
```
$ git diff --name-only -- typsphinx/
```
(no output)
```
$ git diff --name-only -- tox.ini pyproject.toml
```
(no output)

---
