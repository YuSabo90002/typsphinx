# Phase 46 — Green-Tree Evidence (Local Half of SC#3)

**Provisioning note:** all commands below were run inside this plan's isolated git worktree
(`.claude/worktrees/agent-a0d74dbd9860a1388`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`, per this
project's `CLAUDE.md` § "Worktree-isolated execution". Every command below was invoked through
`uv run`. Tree state: `pyproject.toml` `version = "0.7.1"`, `CHANGELOG.md` carries the
`## [0.7.1]` heading, HEAD is the same commit `26b2e6c6fff77520f36e4ff90c165922ef7026fc` pushed
and proven green in `46-CI-EVIDENCE.md`'s "D-23 run 2" section.

Per D-11's authority split (see `46-CI-EVIDENCE.md` § "Why this run is the authority"), **this
file records no claim of authority for pytest, `black`, `ruff`, or `mypy`** — the D-23 run 2 CI
run is the authority for those, since local never exercises Windows/macOS and
`.venv/bin/ruff` is a generic-linux ELF the NixOS stub loader rejects (a filed, out-of-scope
environmental defect). This file covers exactly what CI structurally does not: both docs builds,
the full-corpus `-b typstpdf` gate, and a single `ja` build.

---

## Local evidence — docs builds

### `tox -e docs-html`

Command:
```
$ uv run tox -e docs-html
```

Environment provisioning (via `uv-venv-lock-runner`, `extras = docs`):
```
docs-html: venv> uv venv -p .venv/bin/python --allow-existing ... .tox/docs-html
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
ビルド中 [html]: 更新された 13 件のソースファイル
環境データを更新中[新しい設定] 13 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[  8%] api/index
  ... (progresses through all 13 source files: changelog, contributing,
       examples/advanced, examples/basic, examples/index, index, installation,
       quickstart, user_guide/builders, user_guide/configuration,
       user_guide/index, user_guide/templates)
```

Interleaved with the source read: a `sphinx_autodoc_typehints._parser.py:30:
RemovedInSphinx10Warning` (upstream `sphinx-autodoc-typehints` deprecation notice, unrelated to
typsphinx) repeats 102 times, once per autodoc-processed member — elided here as noise; every
occurrence is byte-identical.

Docstring warnings (pre-existing, unrelated to this plan's scope — `visit_toctree`'s own
docstring, a known carried item, not touched by this plan):
```
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: ERROR: Unexpected indentation. [docutils]
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:15: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:20: ERROR: Unexpected indentation. [docutils]
```

Final lines:
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (7.28=setup[0.18]+cmd[7.10] seconds)
  congratulations :) (7.38 seconds)
```

Exit code: `0`. `build succeeded` present.

### `tox -e docs-pdf`

Command:
```
$ uv run tox -e docs-pdf
```

Transcript follows the same shape as `docs-html` (same 13 source files, same 102x
`RemovedInSphinx10Warning` from `sphinx-autodoc-typehints`, same three pre-existing
`visit_toctree` docstring warnings), diverging at the PDF-specific tail:
```
docs-pdf: commands[0] docs> sphinx-build -b typstpdf source _build/pdf
...
preparing documents... Template written to .../docs/_build/pdf/_template.typ
done
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
writing output... [user_guide/templates] done
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a0d74dbd9860a1388/docs/_build/pdf/typsphinx.pdf
build succeeded, 3 warnings.
  docs-pdf: OK (7.87=setup[0.16]+cmd[7.71] seconds)
  congratulations :) (7.95 seconds)
```

Exit code: `0`. `build succeeded` present, generated PDF path named.

### Produced PDF

Command:
```
$ stat -c '%s' docs/_build/pdf/typsphinx.pdf
```
Verbatim output:
```
2452632
```

`docs/_build/pdf/typsphinx.pdf` exists, **2,452,632 bytes**, produced by typsphinx's own
`typstpdf` builder (`Generated PDF: .../docs/_build/pdf/typsphinx.pdf` above).

---

## Local evidence — full-corpus gate

Command:
```
$ uv run pytest tests/test_corpus_gate.py -v
```

Transcript:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a0d74dbd9860a1388
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items

tests/test_corpus_gate.py::test_catalogue_unknown_visit_multiline PASSED [ 20%]
tests/test_corpus_gate.py::test_catalogue_unknown_visit_windows_crlf_and_prefix PASSED [ 40%]
tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 60%]
tests/test_corpus_gate.py::test_count_empty_url_warnings PASSED          [ 80%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

======================== 4 passed, 1 skipped in 29.76s =========================
```

**Summary: `4 passed, 1 skipped in 29.76s`.** The gate's own class,
`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`, is **PASSED** — Sphinx's own
`doc/` tree (a shallow clone at the tag matching the installed `sphinx.__version__`, `v9.1.0`)
compiled end-to-end through `typsphinx`'s `typstpdf` builder with no fatal Typst error. The
network was reachable in this environment, so the gate ran for real rather than skipping.

The one `SKIPPED` test, `test_empty_url_before_after`, is unrelated to the gate itself — per the
plan's read_first note and the test's own skip reason, it is gated on
`TYPSPHINX_CORPUS_REPORT=1` (an opt-in reporting measurement, RESEARCH Open Question 1), not on
network or corpus availability. This skip is expected and does not weaken the gate's PASSED
result.

---

## Local evidence — ja build (D-12)

_Pending — filled by task 3._
