---
created: 2026-07-21T00:00:00+09:00
title: マスター出力の配置問題 — PDF コンパイルの root 不整合と死んだ typst_output_dir
area: builder
files:
  - typsphinx/pdf.py:140-149 (一時ファイルを outdir 直下に作って compile)
  - typsphinx/builder.py:329 (.typ 出力先 = docname 基準)
  - typsphinx/builder.py:646 (typstpdf の .typ 出力先)
  - typsphinx/builder.py:721 (.pdf 出力先 = docname 基準)
  - typsphinx/translator.py:2928 (_compute_relative_include_path — docname 基準)
  - typsphinx/translator.py:3043 (_compute_relative_image_path — docname 基準)
  - typsphinx/__init__.py:60 (typst_output_dir 登録)
  - docs/configuration.rst:255-267 (typst_output_dir の説明)
---

## Problem

Phase 22（Issue #117 ターゲット名バグ）の discuss 中に判明した、**名前とは別の3つの問題**。
Phase 22 のスコープ（`builder.py` のファイル名導出のみ）を超えるため分離して記録する。

### A. PDF コンパイルの root 基準が出力ファイルの位置と不整合（実バグ）

`compile_typst_to_pdf()` はマスターの中身を **`outdir` 直下の一時ファイル**に書き出してから
`typst.compile()` に渡す（`pdf.py:140-149`、`dir=root_dir` かつ `root_dir=self.outdir`）。
したがって `-b typstpdf` 経路では `include()` / `image()` の相対パスは**常に outdir ルートから**
解決される。

一方 translator は `_compute_relative_include_path()` / `_compute_relative_image_path()` で
**docname のディレクトリ基準**の相対パスを出力している。

→ docname がルート直下（`index`）のマスターだけ両者がたまたま一致して動く。
**docname がネストしたマスター（`api/index` 等）は `-b typstpdf` で既に壊れている**
（`include("../foo.typ")` が outdir ルートから解決され file not found になる）。
`-b typst` の出力を手で `typst compile` する場合は docname 基準で正しいので、
**2つのビルダーで解決基準が食い違っている**のが本質。

未検証: 実際にネストしたマスターを持つプロジェクトを作って再現させること。
既存のテスト/コーパスはすべてマスターがルート直下（`index`）なので検出されていない。

### B. マスター成果物が build ディレクトリ内に散らばる（利便性）

outdir はソースツリーを1対1で写す（`builder.py:329` + `ensuredir`）。マスターの `.typ`/`.pdf` も
docname の位置にそのまま出るため、複数マスターを宣言すると成果物が別々の階層に散る:

```python
typst_documents = [
    ('index',     'manual',        …),   # → _build/pdf/manual.pdf
    ('api/index', 'api-reference', …),   # → _build/pdf/api/api-reference.pdf
]
```

欲しいのは成果物2つだが、片方はサブディレクトリの奥に埋まる。さらに子文書の `.typ`
（`#include()` 用の部品で単体では意味を持たない）とマスターが同じ階層に混在していて
見分けがつかない。

成果物を1箇所に集めるには **A の相対パス基準を出力位置基準に作り直す**必要があり、
A と B は同じ修正で片付く可能性が高い。

### C. `typst_output_dir` が死んだ設定

`__init__.py:60` で `app.add_config_value("typst_output_dir", "_build/typst", "html", [str])`
として登録され、`docs/configuration.rst:255-267` に「出力先ディレクトリ」として文書化されて
いるが、**コード中のどこからも読まれていない**（`grep -rn "typst_output_dir" typsphinx/` は
`__init__.py:60` の1件のみ）。B の解決手段として本来使えるはずの入口が機能していない。

背景 999.3（`typst_package` パスが end-to-end で壊れている）と同種の
「文書化されているが動かない設定」であり、同じ根本原因（設定値のリグレッションフィクスチャ不在）
から来ている。

## Why it matters

- A は silent な壊れ方（ネストしたマスターを使った瞬間にコンパイルが落ちる、または
  画像が欠ける）で、ユーザー側からは原因が追えない。
- C はドキュメントとの契約違反。ユーザーが設定しても何も起きない。
- B は単体では利便性の問題だが、A を直すなら同時に解決できる。

## Proposed scope

1. ネストしたマスターの再現テストを作り、A が実際に壊れることを確認する（GATE-01 形式・実
   `typst.compile()`）。
2. 相対パスの基準を「docname の位置」から「マスターの出力位置」に統一する。`-b typst` と
   `-b typstpdf` で同じ結果になること。
3. その上でマスター成果物の集約先を決める（outdir ルート集約 / `typst_output_dir` を生かす）。
4. `typst_output_dir` を実装するか、実装しないなら登録とドキュメントを削除する。どちらでも
   よいが「登録だけされて動かない」状態は解消する。

## Not now

Phase 22 は Issue #117（ターゲット名がファイル名に反映されない）だけを直す。Phase 23 は
v0.6.2 のリリース準備。この項目は v0.6.2 のスコープ外。

Phase 22 の該当決定: `.planning/phases/22-typstpdf-target-name-pdf-fix-issue-117/22-CONTEXT.md`
D-05（マスターは docname と同じディレクトリに置き、名前だけ差し替える）。
