---
created: 2026-07-23T12:06:54.747Z
title: PR#98 のキャプション付きテーブル figure ラップを現行 main に再実装する
area: translator, tests
files:
  - typsphinx/translator.py:453 (visit_title)
  - typsphinx/translator.py:531 (depart_title)
  - typsphinx/translator.py:2337 (visit_table)
  - typsphinx/translator.py:2422 (depart_table)
  - tests/test_translator.py
---

## Problem

`.. table:: Caption` ディレクティブのキャプションは docutils では `table` の
`title` 子ノードとして格納される。汎用の `visit_title` がこれに反応し、テーブルの
前に余計な `heading(level: N, {text("...")})` を出力してしまう。さらに、直前の
テーブルが残した `table_cell_content` バッファにキャプションが吸われて消える
ケースもある。

現行 main（commit 9f8e075）で再現を確認済み。実際に翻訳すると:

```typst
heading(level: 1, {text("My caption")})   ← 余計な見出し

table(
  columns: (1fr, 1fr),
  ...
)
```

期待する出力は `figure(table(...), caption: {...}, kind: table)` で、「Table N」
番号付けが効く形。`kind: table` を扱う処理は現行コードのどこにも存在しない。

外部コントリビューター AlCalzone の PR#98
(https://github.com/YuSabo90002/typsphinx/pull/98) がこのバグを修正しているが、
**そのままマージできない**:

- マージ状態は `dirty`（コンフリクト）。ベースが 2026-06-12 の `6d13667` で、以降
  v0.6.2 まで進み translator.py は ~2700 行 → ~4900 行に大きく変化。
- PR が触る `visit_title` / `depart_title` / `depart_table` はいずれも現行では
  別実装（`in_list_item` 制御・admonition/topic 分岐・section-id アンカー、
  `:width:` → `block(width: ...)[#table(...)]` ラップ、colwidth ベースの
  `columns: (1fr, 1fr)`）に置き換わっており、機械的リベース不可。

## Solution

PR#98 の設計意図とテストを流用しつつ、現行 main に対して再実装する。

- `visit_title`/`depart_title`: `self.in_table` の場合はキャプションとして
  バッファ（インラインマークアップ保持）し、`depart_table` で消費する。現行の
  `in_list_item`/`list_item_needs_separator` の save/restore、admonition/topic
  分岐、section-id アンカーと衝突しないよう組み込む。
- `depart_table`: captioned table を `figure(table(...), caption: {...},
  kind: table)` でラップ。**現行の `:width:` → `block(width: ...)[#table(...)]`
  ラップとの合成**を必ず考慮（caption + width 両方のケース）。
- テスト: AlCalzone の 4 本（figure 化 / インラインマークアップ保持 /
  stale buffer 漏れ防止 / キャプション無しは非 figure）を移植。ただし現行の
  セル形式は `{par({text("...")})}`、columns は `columns: (1fr, 1fr)` なので
  アサーションをそれに追従させる。

作者 AlCalzone には PR にコメントし、現行実装への追従が必要な旨と、こちらで
再実装を引き取る意向を伝える。
