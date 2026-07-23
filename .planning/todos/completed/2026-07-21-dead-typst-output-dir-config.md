---
created: 2026-07-21T00:00:00+09:00
closed: 2026-07-22
closed_by: Phase 22.2 (dead-config-value-sweep) — CONF-01
status: resolved
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

**2026-07-21 決定（オーナー判断）: 即削除。非推奨期間は置かない。**

撤去対象:

- `typsphinx/__init__.py:60` の `add_config_value` 登録
- `docs/configuration.rst:255-269`（"Output Configuration" 節）と `:348`（フル設定例）
- `tests/test_config_other_options.py:141-179`（登録のみを見る2テスト）
- `tests/test_documentation_configuration.py:46`（`required_configs` からの除去）
- `examples/advanced/conf.py:102` / `examples/advanced/README.md:263`（コメントアウト行）
- `CLAUDE.md:67` の設定サーフェス列挙からの除去
- `CHANGELOG.md` に `### Removed` エントリを追加

非推奨期間を置かない根拠: Sphinx は未登録の conf.py 変数を黙って無視する（実測確認済み）。
削除しても挙動は変わらず、既存ユーザーのビルドは壊れない。一方 deprecation 警告は
「何もしていない設定を消してください」と言うだけで、利用者に何の情報も与えない。

**着手先: バックログ 999.4「Dead Config-Value Sweep」の scope 要素 1。**
999.3（`typst_package` パスが end-to-end で壊れている）と同一根本原因のため1フェーズに統合した。
再発防止の「設定値 → 出力への影響」を検証するリグレッションフィクスチャは 999.4 の scope 要素 3。

## Not now

v0.6.2 のスコープ外。Phase 22（Issue #117）、Phase 22.1（PDF-02）、Phase 23（リリース準備）
はいずれも別件。着手は 999.4 を `/gsd-review-backlog` で昇格させたとき。

## 決着（2026-07-22）

**Phase 22.2「Dead Config-Value Sweep」CONF-01 で解決済み。** 上記 Solution の撤去対象を
すべて実施し、`typst_output_dir` は登録・ドキュメント・examples・`CLAUDE.md`・登録専用テスト
（`test_config_other_options.py` の2本、`test_documentation_configuration.py:46` の
`required_configs`）から消えている。実測: `grep -rn "typst_output_dir"` の実装/ドキュメント側
ヒットは `CHANGELOG.md:489`（初出時の履歴記述、書き換えない）のみ。
併せて `typst_author_params` も同 CONF-01 で削除され、`[0.6.2]` の `### Removed` に両者を記載。

「設定値 → 出力への影響」を検証するリグレッションフィクスチャ（scope 要素 3 / CONF-03）も
同フェーズで着地: `tests/test_package_only_config_gate.py` の config→output 差分マトリクス。

**"Not now" セクションは失効** — 999.4 は 2026-07-22 に Phase 22.2 として v0.6.2 に昇格・完了した。
