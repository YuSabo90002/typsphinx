---
created: 2026-07-22T23:55:07+09:00
title: typing の modernize（`UP006`/`UP035` の ignore 解除と組み込みジェネリクスへの書き換え）
area: source
files:
  - pyproject.toml:122 (ruff `[tool.ruff.lint] ignore` の `"UP035",  # typing.Dict/List/Set deprecation (Python 3.10+ support)` 行)
  - pyproject.toml:123 (ruff `[tool.ruff.lint] ignore` の `"UP006",  # Use dict instead of Dict (Python 3.10+ support)` 行)
  - typsphinx/__init__.py:15 (`from typing import Any, Dict`)
  - typsphinx/writer.py:9 (`from typing import Any` — Dict/List 等の非該当は既に確認済み、変更なしの可能性あり)
  - typsphinx/template_engine.py:10 (`from typing import Any, Dict, List`)
  - typsphinx/builder.py:12 (`from typing import List, Set, Tuple`)
  - typsphinx/translator.py:9 (`from typing import Any, List, Tuple`)
---

## Problem

`pyproject.toml:122-123` の ruff `ignore` リストは `UP035`（`typing.Dict`/`List`/`Set` 非推奨警告の抑制）と
`UP006`（組み込みジェネリクス `dict`/`list` の代わりに `Dict`/`List` を使い続けることの抑制）を
`(Python 3.10+ support)` というコメントとともに維持している。しかし `pyproject.toml:10` の
`requires-python = ">=3.12"` である以上、`dict[str, Any]` 等の組み込みジェネリクスは何の問題もなく使え、
`typsphinx/{__init__,template_engine,builder,translator}.py` が `from typing import Dict, List, Set, Tuple`
を使い続ける技術的必然性は現在存在しない。

実装調査の結果、ignore が残っている実際の理由は、単に **Phase 6 (v0.5.0) で Python フロアを 3.10 から
3.12 へ引き上げた際に、3.10 互換用に追加されていたこの ignore を一緒に外し損ねた** というメンテナンスの
取りこぼしである。技術的な制約や意図的な後方互換維持ではない — 正直な理由であり、技術的正当化を
捏造してはならない（Phase 22.4 D-08/Research Task D の裁定どおり）。

`CLAUDE.md` 側の `- **Python 3.10+ compatibility is required.**` という記述コメントは Phase 22.4 で
「D-15 が着地するまでの意図的な先送り」という趣旨に書き換えられる予定（Phase 22.4 Plan 01 が対応）。
本 todo が着地した時点で、その CLAUDE.md の文言も「先送り完了」を反映するよう再度更新が必要。

## Solution

1. `pyproject.toml` の `[tool.ruff.lint] ignore` から `"UP035"` と `"UP006"` の 2 行を除去する。
2. `ruff check --fix` を実行し、`typsphinx/__init__.py` / `typsphinx/template_engine.py` /
   `typsphinx/builder.py` / `typsphinx/translator.py` の `typing.Dict`/`List`/`Set`/`Tuple` の
   インポートと型注釈を組み込みジェネリクス（`dict`/`list`/`set`/`tuple`）へ書き換える。
   `typsphinx/writer.py` は現状 `Dict`/`List` 等を使っていない可能性が高いため、対象外なら
   スキップしてよい（着手時に `grep -n 'Dict\|List\|Set\|Tuple' typsphinx/writer.py` で再確認）。
3. `mypy typsphinx/` と全テストスイート（`pytest`、`uv run pytest`）が green であることを確認する。
4. `CLAUDE.md` の該当記述（Phase 22.4 で「D-15 が着地するまでの意図的な先送り」と書き換えられる箇所）を、
   本 todo 着地時に「モダナイズ完了」を反映するよう再度更新する。

**Plan 03（Phase 22.4）がこの todo のファイルパスを `CLAUDE.md`/`pyproject.toml` のコメントから参照するため、
ファイル名は上記のとおり厳守すること。改名しない。**
