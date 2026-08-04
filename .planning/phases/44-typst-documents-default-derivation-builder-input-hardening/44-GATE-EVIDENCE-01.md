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

RED commit SHA: `PENDING — filled in immediately after the commit below`

Plan 44-03 consumes this SHA as the pre-change side of the SC#4 two-build
record. This commit touches no path under `typsphinx/`.

## 3. GREEN — after the derivation

_Appended after Task 1(e)._

## 4. Existing tests updated for CONF-08 (SC#5 share)

_Appended after Task 2._

## 5. SC#2 — the explicit setting wins

_Appended after Task 3._
