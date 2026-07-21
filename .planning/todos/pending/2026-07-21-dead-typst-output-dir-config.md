---
created: 2026-07-21T00:00:00+09:00
title: 死んだ設定 typst_output_dir — 実装するか、登録とドキュメントごと削除するか
area: builder
files:
  - typsphinx/__init__.py:60 (typst_output_dir 登録 — 唯一の実装側ヒット)
  - docs/configuration.rst:255-269 ("Output Configuration" 節の説明)
  - docs/configuration.rst:348 (フル設定例に登場)
  - tests/test_config_other_options.py:141-179 (登録のみを検証する2テスト)
  - tests/test_documentation_configuration.py:46 (文書化必須リストに含む)
  - examples/advanced/conf.py:102 (コメントアウト)
  - examples/advanced/README.md:263 (同上)
  - CHANGELOG.md:489 (初出時に機能として告知)
  - CLAUDE.md:67 (設定サーフェスの列挙)
---

## 経緯

Phase 22（Issue #117 ターゲット名バグ）の discuss 中に判明した3つの問題 A/B/C のうち、
**C だけがこの todo に残っている**。

- **A**（`-b typstpdf` と `-b typst` で相対パス解決の基準が食い違う実バグ）
  → **2026-07-21 に Phase 22.1 / PDF-02 として v0.6.2 に差し込み済み**
  （`.planning/phases/22.1-typstpdf-compile-root-alignment-for-nested-masters/`）
- **B**（複数マスター宣言時に成果物が build ツリーの別階層に散らばる利便性の問題。
  出力位置を動かして `include()`/`image()` の相対パスを振り直す設計変更が必要だった）
  → **2026-07-21 オーナー判断で不採用・記録ごと削除。** やらない。
- **C** → 以下。

## Problem

`typsphinx/__init__.py:60` で

```python
app.add_config_value("typst_output_dir", "_build/typst", "html", [str])
```

として登録され、`docs/configuration.rst:255-269` に独立した "Output Configuration" 節として

> Output directory for generated Typst files. / Default: `'_build/typst'`
> **Note:** Path is relative to the build directory specified in sphinx-build command.

と文書化され、フル設定例（`docs/configuration.rst:348`）にも載っている。
`CHANGELOG.md:489` では初出時に機能として告知済み。

**しかし実装側から読まれている箇所はゼロ。** `grep -rn "typst_output_dir" typsphinx/` の
ヒットは上記の登録1行のみ。ユーザーが設定しても出力先は一切変わらない。

### なぜテストで検出されなかったか

テストは2本あるが、**どちらも「登録されていること」しか検証していない**:

- `tests/test_config_other_options.py:141` `test_typst_output_dir_config_registered`
  — `hasattr(app.config, "typst_output_dir")` と値の一致を見るだけ
- `tests/test_config_other_options.py:162` `test_typst_output_dir_default_value`
  — デフォルト値を見るだけ
- `tests/test_documentation_configuration.py:46` — configuration.rst に名前が出現するかだけ

つまり「登録されている」「文書化されている」は緑になるが、
「**設定した値が出力に影響する**」を検証するフィクスチャが1つも無い。
バックログ **999.3**（`typst_package` パスが end-to-end で壊れている）と同じ根本原因。
「文書化されているが動かない設定」という同一系統の欠陥。

### Sphinx のモデルとの衝突（実装可否の判断材料）

outdir は `sphinx-build -b typst SOURCE OUTDIR` のコマンドライン引数（あるいは `-M` の
builddir）で決まる。`app.outdir` は Sphinx インスタンス生成時に確定し、Sphinx 自身が
outdir の管理（クリーン、`.buildinfo`、doctreedir との対応、並列ビルド）を前提にしている。
conf.py から builder が自分の outdir を差し替えるのは、このモデルと真っ向から衝突する。
実際、他の Sphinx ビルダーに同種の設定は存在しない（`latex_output_dir` も
`html_output_dir` も無い）。

### 削除した場合の互換性（実測済み・2026-07-21）

Sphinx は **conf.py 内の未登録の変数を黙って無視する**。`-W --keep-going` 付きでも
警告すら出ないことを実測で確認済み（`typst_totally_bogus_setting` を conf.py に置いて
`sphinx-build -b html -W` が build succeeded）。

したがって登録を削除しても、`typst_output_dir` を conf.py に書いているユーザーの
ビルドは壊れない — **今日と同じく何も起きないまま**になる。挙動の変化はゼロ。

## Solution

TBD — 2026-07-21 に方針を検討中。選択肢:

1. **削除する**（登録・ドキュメント・登録専用テストを撤去し、CHANGELOG に「実装されて
   いなかった設定を削除」と記載）。Sphinx のモデルとの衝突を踏まえると最も正直。
2. **非推奨経由で削除**（1リリース分 deprecation 警告を出してから撤去）。
3. **実装する**（`typst_output_dir` が指す場所を実際の出力先にする）。B を不採用にした
   以上、これを入れる動機は「ドキュメントとの契約を守る」だけになる。

いずれを採るにせよ、999.3 と共通の再発防止として**「設定値が出力に影響することを検証する
フィクスチャ」**を1本立てるかどうかを併せて決める。

## Not now

v0.6.2 のスコープ外。Phase 22（Issue #117）、Phase 22.1（PDF-02）、Phase 23（リリース準備）
はいずれも別件。
