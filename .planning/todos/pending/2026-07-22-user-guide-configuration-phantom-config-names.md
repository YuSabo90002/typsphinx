---
created: 2026-07-22T23:55:07+09:00
title: `docs/source/user_guide/configuration.rst` が実在しない設定名 5 個を記載している
area: docs
files:
  - docs/source/user_guide/configuration.rst:154 (`typst_use_codly = True  # Default` — 未登録)
  - docs/source/user_guide/configuration.rst:160 (`typst_code_line_numbers = True  # Show line numbers` — 未登録)
  - docs/source/user_guide/configuration.rst:170 (`typst_author = ("John Doe", "Jane Smith")` — 未登録。単数形。実在する設定は `typst_authors`（複数形）)
  - docs/source/user_guide/configuration.rst:197 (`typst_papersize = "a4"  # Default: "a4"` — 未登録)
  - docs/source/user_guide/configuration.rst:200 (`typst_fontsize = "11pt"  # Default: "11pt"` — 未登録)
  - docs/source/user_guide/configuration.rst:245-246 (同じ2つの phantom 名 `typst_use_codly`/`typst_code_line_numbers` の再出現)
  - typsphinx/__init__.py:44-62 (登録済み `typst_*` 設定 12 件の唯一の正解源)
---

## Problem

Phase 22.4 の RESEARCH.md Task C（2つのリンク先の実測比較）で発見。README:205 のリンク先を
孤児 `docs/configuration.rst` から `docs/source/user_guide/configuration.rst` へ張り替える判断
（Phase 22.4 D-12）自体は、後者が実際にビルドされ toctree からも到達可能なため**依然として正しい**。

しかし張り替え先の `docs/source/user_guide/configuration.rst` 自体にも独立した誤りが残っている:
実在しない設定名が5個、実際に使える設定であるかのように例示されている。

- `typst_use_codly`（:154, :245）— `typsphinx/__init__.py:44-62` に一切登録されていない
- `typst_code_line_numbers`（:160, :246）— 同上、未登録
- `typst_author`（:170、単数形）— 実在するのは `typst_authors`（複数形）。単数形は未登録
- `typst_papersize`（:197）— 未登録（Phase 22.4 discovery #1 の `typst_elements["papersize"]` とは別物 —
  トップレベルの `typst_papersize` という設定自体が存在しない）
- `typst_fontsize`（:200）— 同上、未登録

いずれも `typsphinx/__init__.py` に登録されていない架空の設定名であり、読者がドキュメントの例をそのまま
`conf.py` にコピーしても、Sphinx は未知の設定値として警告を出すか（`suppress_warnings` 次第）静かに
無視するかのいずれかで、実際の出力には一切反映されない。

## Solution

1. 上記5個の記述を削除するか、実在する設定名への置換を検討する
   （`typst_author` → `typst_authors`、`typst_papersize`/`typst_fontsize` → `typst_elements` 経由での
   指定に書き換える場合は、隣接する pending todo
   `2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`（D-18）が指摘する
   `typst_elements` の非マッピングキー問題が未解決のうちは「動く例」として書けない点に注意 —
   D-18 が解決されるまでは `typst_papersize`/`typst_fontsize` 系の記述は削除のみが安全）。
2. `docs/source/user_guide/configuration.rst` に記載されている全 `typst_*` 名を
   `typsphinx/__init__.py:44-62` の登録集合と突き合わせ、他に phantom 名が残っていないか確認する。
