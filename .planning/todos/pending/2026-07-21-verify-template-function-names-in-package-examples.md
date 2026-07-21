---
created: 2026-07-21T20:40:31+09:00
title: Verify typst_template_function names in Typst Universe examples
area: docs
files:
  - docs/source/examples/advanced.rst:33 (charged-ieee — verified correct)
  - docs/source/examples/advanced.rst:59 (modern-cv — suspected wrong)
  - docs/source/user_guide/templates.rst:42
  - docs/source/user_guide/configuration.rst:83,218
---

## Problem

`typst_template_function = {"name": ...}` の `name` は **パッケージ名ではなく、
そのパッケージが export している Typst 関数名**。`template_engine.py:212-215` が
`#import "{typst_package}": {name}` を生成し、`:320,332` でその名前を呼び出す。

- **charged-ieee の例は正しい。** `~/.cache/typst/packages/preview/charged-ieee/0.1.4/lib.typ:3`
  に `#let ieee(` があり、`"name": "ieee"` で `#import "@preview/charged-ieee:0.1.4": ieee`
  が生成される。`"charged-ieee"` にするとむしろ壊れる。
- **modern-cv の例 (advanced.rst:59) は疑わしい。** `"name": "modern-cv"` と
  パッケージ名をそのまま書いているが、modern-cv が export するエントリ関数は
  `resume` のはず（未検証：ローカルキャッシュに modern-cv 未取得）。
  もしそうなら `#import "@preview/modern-cv:0.7.0": modern-cv` はコンパイルエラーになる。

ドキュメント例が実際にコンパイルできるか未検証のまま公開されている点がリスク。

## Solution

1. modern-cv 0.7.0 の `lib.typ` を取得して export 名を確認（`typst` で一度
   コンパイルすればキャッシュに落ちる）。
2. 誤っていれば `docs/source/examples/advanced.rst` の modern-cv 例を修正し、
   `docs/locale/ja/LC_MESSAGES/examples/advanced.po` も追随。
3. 併せて「`name` は**関数名**であってパッケージ名ではない」旨の注記を
   `docs/source/user_guide/templates.rst` / `configuration.rst` の
   `typst_template_function` 説明に追加する。
4. 可能なら他のパッケージ例も同様に実コンパイルで検証。
