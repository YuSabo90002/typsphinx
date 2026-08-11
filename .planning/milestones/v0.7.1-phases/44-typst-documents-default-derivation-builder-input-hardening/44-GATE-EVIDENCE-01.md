# Phase 44 Plan 01 — Gate Evidence 01

CONF-08: `typst_documents` default derivation. All output below was produced
by commands run in this plan's own execution session (worktree
`agent-a4dc8670ea2a386f8`), never transcribed from a planning document.

## 1. RED — the unchanged code

Both commands below were run against the unmodified `typsphinx/` tree, before
any production code in this plan was touched.

### `sphinx-build -b typstpdf`

```
$ uv run python -m sphinx -b typstpdf -E tests/fixtures/default_typst_documents_gate /tmp/gate01-red-typstpdf
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typstpdf]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/gate01-red-typstpdf/_template.typ
done
writing output... [index] done
WARNING: No documents defined in typst_documents. Nothing to compile.
build succeeded, 1 warning.
```

**Exit status: 0.** Warning text (full, verbatim): `WARNING: No documents
defined in typst_documents. Nothing to compile.`

`ls -la /tmp/gate01-red-typstpdf/`:

```
total 8
drwxr-xr-x 1 yuta users    62  8月  4 14:10 .
drwxrwxrwt 1 root root  67568  8月  4 14:10 ..
drwxr-xr-x 1 yuta users    62  8月  4 14:10 .doctrees
-rw-r--r-- 1 yuta users  2438  8月  4 14:10 _template.typ
-rw-r--r-- 1 yuta users   412  8月  4 14:10 index.typ
```

**Zero PDFs written.** `index.typ` is 412 bytes. First 20 lines of
`index.typ` (no template call — only `@preview` imports and body):

```
1	// Essential imports for included document
2	#import "@preview/codly:1.3.0": *
3	#import "@preview/codly-languages:0.1.10": *
4	#import "@preview/mitex:0.2.7": mi, mitex
5	#import "@preview/gentle-clues:1.3.1": *
6	
7	// Initialize codly
8	#show: codly-init.with()
9	#codly(languages: codly-languages)
10	
11	#{
12	[#heading(level: 1, {text("Quickstart Default Gate")}) <index:quickstart-default-gate>]
13	
14	par({text("QSDEFAULTBODY")})
15	
16	
17	}
```

### `sphinx-build -b typst`

```
$ uv run python -m sphinx -b typst -E tests/fixtures/default_typst_documents_gate /tmp/gate01-red-typst
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/gate01-red-typst/_template.typ
done
writing output... [index] done
build succeeded.
```

**Exit status: 0.**

`ls -la /tmp/gate01-red-typst/`:

```
total 8
drwxr-xr-x 1 yuta users    62  8月  4 14:10 .
drwxrwxrwt 1 root root  67568  8月  4 14:10 ..
drwxr-xr-x 1 yuta users    62  8月  4 14:10 .doctrees
-rw-r--r-- 1 yuta users  2438  8月  4 14:10 _template.typ
-rw-r--r-- 1 yuta users   412  8月  4 14:10 index.typ
```

Same 412-byte untemplated `index.typ` as the typstpdf run (the `-b typst`
build path shares the same write_doc/`_resolve_output_stem` machinery).

### `pytest tests/test_default_typst_documents_gate.py -q`

```
$ uv run python -m pytest tests/test_default_typst_documents_gate.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dc8670ea2a386f8
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_default_typst_documents_gate.py F                             [100%]

=================================== FAILURES ===================================
_ TestDefaultTypstDocumentsDerivationGate.test_unset_typst_documents_produces_pdf _

    def test_unset_typst_documents_produces_pdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(DEFAULT_GATE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode == 0, (
            f"Expected a successful build with typst_documents unset:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

>       assert (build_dir / "quickstartdefaultgate.typ").exists(), (
            f"Expected the derived target quickstartdefaultgate.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
E       AssertionError: Expected the derived target quickstartdefaultgate.typ:
E         ...
E       assert False
E        +  where False = exists()
E        +    where exists = (PosixPath('.../build') / 'quickstartdefaultgate.typ').exists

tests/test_default_typst_documents_gate.py:82: AssertionError
=========================== short test summary info ============================
FAILED tests/test_default_typst_documents_gate.py::TestDefaultTypstDocumentsDerivationGate::test_unset_typst_documents_produces_pdf
============================== 1 failed in 0.28s ===============================
```

## 2. RED commit

RED commit SHA: `eeb930429c2608c5245f2769fc6b7edbbed206c5`

Plan 44-03 consumes this SHA as the pre-change side of the SC#4 two-build
record. This commit touches no path under `typsphinx/` (confirmed:
`git show --stat eeb930429c2608c5245f2769fc6b7edbbed206c5 --name-only | grep -c '^typsphinx/'`
→ `0`).

## 3. GREEN — after the derivation

After implementing `_default_typst_documents(config)` in `typsphinx/builder.py`
and switching the `typst_documents` registration to that callable default in
`typsphinx/__init__.py`.

### `sphinx-build -b typstpdf`

```
$ uv run python -m sphinx -b typstpdf -E tests/fixtures/default_typst_documents_gate /tmp/gate01-green-typstpdf
...
preparing documents... Template written to /tmp/gate01-green-typstpdf/_template.typ
done
writing output... [index] done
Compiling 1 master document(s) to PDF...
Generated PDF: /tmp/gate01-green-typstpdf/quickstartdefaultgate.pdf
build succeeded.
```

**Exit status: 0.**

`ls -la /tmp/gate01-green-typstpdf/`:

```
total 28
drwxr-xr-x 1 yuta users   144  8月  4 14:11 .
drwxrwxrwt 1 root root  67646  8月  4 14:11 ..
drwxr-xr-x 1 yuta users    62  8月  4 14:11 .doctrees
-rw-r--r-- 1 yuta users  2438  8月  4 14:11 _template.typ
-rw-r--r-- 1 yuta users 17308  8月  4 14:11 quickstartdefaultgate.pdf
-rw-r--r-- 1 yuta users   532  8月  4 14:11 quickstartdefaultgate.typ
```

**`quickstartdefaultgate.typ` is 532 bytes** (RED's `index.typ` was 412
bytes — the file grew because the template import + function call are now
present). Full content:

```
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Quickstart Default Gate",
  authors: ("Test Author",),
  date: "1.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Quickstart Default Gate")}) <index:quickstart-default-gate>]

par({text("QSDEFAULTBODY")})


}
```

Lines 10 (`#import "_template.typ": project`) and 12-17 (`#show:
project.with(...)`) are the template import and template function call —
proving `root_doc` ("index") is now treated as a master document, unlike
RED's untemplated `index.typ`.

### `sphinx-build -b typst`

```
$ uv run python -m sphinx -b typst -E tests/fixtures/default_typst_documents_gate /tmp/gate01-green-typst
...
build succeeded.
```

**Exit status: 0.**

### `pytest tests/test_default_typst_documents_gate.py -x -q`

```
$ uv run python -m pytest tests/test_default_typst_documents_gate.py -x -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dc8670ea2a386f8
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_default_typst_documents_gate.py .                             [100%]

============================== 1 passed in 0.34s ===============================
```

### Acceptance-criteria commands (all measured this session)

- `grep -c 'Quickstart Default Gate' tests/fixtures/default_typst_documents_gate/conf.py` → `2`
- AST assignment census: `uv run python -c "import ast; print(sorted({t.id for n in ast.parse(open('tests/fixtures/default_typst_documents_gate/conf.py').read()).body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}))"` → `['author', 'copyright', 'extensions', 'project', 'release']`
- `grep -c 'def _default_typst_documents' typsphinx/builder.py` → `1`
- `grep -c 'make_filename_from_project' typsphinx/builder.py` → `3` (the import, the docstring mention, and the call — ≥2 required)
- `grep -c '_default_typst_documents' typsphinx/__init__.py` → `2` (the import and the registration)
- `uv run python -c "import typsphinx, types; c=types.SimpleNamespace(root_doc='index', project='My Cool Project', author='A. Author'); print(typsphinx.builder._default_typst_documents(c))"` → `[('index', 'mycoolproject.typ', 'My Cool Project', 'A. Author', 'typst')]`
- `uv run python -m sphinx -b typstpdf -E tests/fixtures/default_typst_documents_gate /tmp/gate01-accept` → exit 0; `quickstartdefaultgate.pdf` exists; `index.typ` absent
- `uv run python -m pytest tests/test_missing_and_malformed_master_gate.py tests/test_builder_output_stem.py tests/test_pdf_generation.py -q` → `56 passed`

## 4. Existing tests updated for CONF-08 (SC#5 share)

This section covers only what THIS plan (44-01) touched. The repo-wide
version of this audit is plan 44-04's job.

### Verbatim pre-change failure output

Measured with `uv run python -m pytest tests/test_builder.py -q` immediately
after the GREEN commit landed (i.e. against the derivation already in
place, before either test was updated):

```
FAILED tests/test_builder.py::test_write_doc_creates_output_file - AssertionError: assert False
 +  where False = exists()
 +    where exists = PosixPath('.../build/html/index.typ').exists

FAILED tests/test_builder.py::test_write_doc_generates_typst_content - FileNotFoundError: [Errno 2] No such file or directory: '.../build/html/index.typ'

2 failed, 18 passed in 0.30s
```

Both failures are exactly the predicted mechanism: `temp_sphinx_app`'s
`conf.py` omits `typst_documents` and sets `project = 'Test Project'`, so
`_resolve_output_stem("index")` now returns `testproject` (via
`make_filename_from_project("Test Project")`) and `write_doc` writes
`testproject.typ`, not `index.typ`.

### Route taken

**Route 1 — rename to the derived target name.** Both
`test_write_doc_creates_output_file` and
`test_write_doc_generates_typst_content` were updated to assert on
`Path(builder.outdir) / "testproject.typ"` instead of `"index.typ"`, each
with a comment naming CONF-08 and explaining the filename now comes from
`make_filename_from_project(project)`. The measured failure was *only* the
filename (a clean `AssertionError`/`FileNotFoundError` on the path, no
exception from applying the full template inside the unit-level harness),
so the rename route was viable and Route 2 (pinning
`builder.config.typst_documents = []`) was not needed.

### Diff of `tests/test_builder.py`

```diff
     # Write a document
     builder.write_doc("index", sample_doctree)

-    # Check that output file was created
-    output_file = Path(builder.outdir) / "index.typ"
+    # CONF-08: temp_sphinx_app's conf.py omits typst_documents, so the
+    # config value now resolves through _default_typst_documents, which
+    # names the "index" master's output via
+    # make_filename_from_project("Test Project") -> "testproject.typ"
+    # rather than the old literal "index.typ".
+    output_file = Path(builder.outdir) / "testproject.typ"
     assert output_file.exists()
     assert output_file.is_file()
```

```diff
     # Write a document
     builder.write_doc("index", sample_doctree)

-    # Check that output file contains Typst content
-    output_file = Path(builder.outdir) / "index.typ"
+    # CONF-08: temp_sphinx_app's conf.py omits typst_documents, so the
+    # config value now resolves through _default_typst_documents, which
+    # names the "index" master's output via
+    # make_filename_from_project("Test Project") -> "testproject.typ"
+    # rather than the old literal "index.typ".
+    output_file = Path(builder.outdir) / "testproject.typ"
     content = output_file.read_text()
```

### `tests/test_config.py`, `tests/test_builder_output_stem.py`,
`tests/test_pdf_generation.py` needed no change

Proof, not assertion of belief — `uv run python -m pytest
tests/test_default_typst_documents_derivation.py tests/test_builder.py
tests/test_config.py tests/test_builder_output_stem.py
tests/test_pdf_generation.py -q`:

```
tests/test_default_typst_documents_derivation.py .............          [ 13%]
tests/test_builder.py ....................                              [ 34%]
tests/test_config.py ........                                           [ 43%]
tests/test_builder_output_stem.py ........................              [ 68%]
tests/test_pdf_generation.py ..............................             [100%]

95 passed in 1.38s
```

`test_config.py`'s `test_default_typst_documents_config` and
`test_typst_documents_config_structure` assert only that the config value
exists and is a `list` (`test_config.py:6-19`) — both still hold under a
callable default, so no change was needed there. Every fixture in
`test_builder_output_stem.py` and `test_pdf_generation.py` sets
`typst_documents` explicitly, so the derived default changes nothing for
either module.

## 5. SC#2 — the explicit setting wins

### Build command and exit status

```
$ uv run python -m sphinx -b typstpdf -E tests/fixtures/explicit_typst_documents_wins_gate /tmp/gate01-sc2
...
preparing documents... Template written to /tmp/gate01-sc2/_template.typ
done
writing output... [index] done
Compiling 1 master document(s) to PDF...
Generated PDF: /tmp/gate01-sc2/manual.pdf
build succeeded.
```

**Exit status: 0.**

### `ls -la` of the build directory

```
total 28
drwxr-xr-x 1 yuta users    84  8月  4 14:14 .
drwxrwxrwt 1 root root  67784  8月  4 14:14 ..
drwxr-xr-x 1 yuta users    62  8月  4 14:14 .doctrees
-rw-r--r-- 1 yuta users  2438  8月  4 14:14 _template.typ
-rw-r--r-- 1 yuta users 17677  8月  4 14:14 manual.pdf
-rw-r--r-- 1 yuta users   520  8月  4 14:14 manual.typ
```

Exactly `manual.typ` + `manual.pdf` — no `explicitwinsgate.typ`/`.pdf`, no
`index.typ`/`.pdf`.

### Passing pytest output

```
$ uv run python -m pytest tests/test_default_typst_documents_gate.py -x -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a4dc8670ea2a386f8
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_default_typst_documents_gate.py ..                            [100%]

============================== 2 passed in 0.60s ===============================
```

## 6. Deviations discovered while proving the whole-plan gate

Two deviations surfaced while running the plan-level `<verification>` (full
suite + black/ruff/mypy), both auto-fixed under the executor's Rule 1/Rule 3
(fix directly caused by this plan's own production change / blocking issue
preventing the required green signal) and recorded here for transparency:

**(a) `tests/test_builder_requirement13.py` also encoded the old
`[]`-default, missed by the planning-time census.** `44-CONTEXT.md`'s
repo-wide count ("all 103 `conf.py` files that mention `typst_documents`
already set it") only covered `tests/fixtures/*/conf.py` files on disk. It
did not cover `conf.py` content written inline by a test fixture function
(`multifile_srcdir` in `test_builder_requirement13.py`, which sets `project
= 'Multi-File Test'` and omits `typst_documents`). Running the full suite
after Task 2's fix surfaced 3 additional failures there
(`test_builder_generates_independent_typ_files`,
`test_toctree_with_nested_paths_generates_correct_includes`,
`test_toctree_with_missing_document_warning`), all asserting on the old
literal `index.typ`. Fixed the same way as `test_builder.py`'s two tests:
renamed the assertion target to the derived stem
(`make_filename_from_project("Multi-File Test")` -> `multi-filetest.typ`,
confirmed live) with a CONF-08 traceability comment on each. Re-run:
`uv run python -m pytest tests/test_builder_requirement13.py -q` -> `5
passed`. Plan 44-04 still owns the exhaustive repo-wide audit; this is only
the instance the plan's own full-suite verification step surfaced.

**(b) The worktree's `.venv/bin/uv` and `.venv/bin/ruff` needed the
documented NixOS-sandbox shim before `uv run python -m pytest -q` (full
suite) or `uv run black`/`ruff`/`mypy` could give a trustworthy signal.**
`uv sync --extra dev` installs generic-linux ELF wheels for `uv` and `ruff`
into this fresh worktree venv; NixOS cannot exec them directly (`exit
127`), which produced 45-48 failures in
`tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py` (they
`subprocess.run(["uv","run","sphinx-build",...])`) that were pre-existing
environmental noise, not caused by this plan's diff. Fixed per this
project's established runbook: `ln -sf <nix-store uv> .venv/bin/uv` and
`ln -sf <main-tree's already-patchelf'd ruff> .venv/bin/ruff`, each verified
with the acceptance test `.venv/bin/<tool> --version` actually executing
before re-running the suite. Not a code change; no commit needed for this
fix (venv contents are gitignored). Confirmed clean afterwards:
`uv run python -m pytest -q` -> `852 passed, 1 skipped`.

### Full-suite and lint/type gate (plan-level `<verification>`)

```
$ uv run python -m pytest -q
852 passed, 1 skipped in 77.26s

$ uv run black --check .
All done! 221 files would be left unchanged.

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```
