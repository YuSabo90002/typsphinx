---
created: 2026-07-22T23:55:07+09:00
title: 登録済みだが出力に反映されない `typst_*` 設定の第三・第四インスタンス（`typst_elements` の非マッピングキー / `typst_toctree_defaults`）
area: source, config
files:
  - typsphinx/template_engine.py:62-66 (`DEFAULT_PARAMETER_MAPPING` — `project`/`author`/`release` の3キーのみ)
  - typsphinx/template_engine.py:186-213 (`map_parameters()` — `self.parameter_mapping.items()` でループし、マッピングに存在しないキーを無条件に捨てる)
  - typsphinx/writer.py:208-209 (`typst_elements` を `sphinx_metadata.update(typst_elements)` するだけで、`map_parameters` のマッピング外キーはここで既に紛れ込むが最終的に捨てられる)
  - typsphinx/__init__.py:47 (`typst_toctree_defaults` の登録行。`app.add_config_value("typst_toctree_defaults", None, "html", [dict, type(None)])`)
  - typsphinx/templates/base.typ:39-61 (`project()` 関数のデフォルト引数。`papersize: "a4"` (:46), `fontsize: 11pt` (:47) が常に使われる証跡)
  - tests/test_config.py:112-156 (`test_typst_elements_config`/`test_custom_typst_elements_config` — 登録値の読み込みのみ検証、出力への反映は未検証)
  - tests/test_config_template_mapping.py:240 (`# Note: typst_elements integration is tested separately` というコメントがあるが、該当テストは実在しない)
  - tests/test_config_toctree_defaults.py:9-236 (全テストが `assert hasattr(app.config, "typst_toctree_defaults")` / `assert app.config.typst_toctree_defaults == {...}` という登録値の存在確認のみ)
---

## Problem

Phase 22.4 の RESEARCH.md 全文監査で新規発見した、Phase 22.2 が塞いだ `typst_output_dir`/`typst_package`
と同型の「登録済みだが出力に一切反映されない設定」の**第三・第四インスタンス**。

**(1) `typst_elements` の非マッピングキー（discovery #1）:**
README の Custom Templates 例は `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` の
ように書けばテンプレートの `project()` 関数へ渡ると読める。しかし実装を追うと:
1. `typsphinx/writer.py:208-209` — `typst_elements` は `sphinx_metadata` 辞書へ `update()` されるだけ。
2. `typsphinx/template_engine.py:186-213` (`map_parameters`) — `self.parameter_mapping.items()`
   （デフォルトは `{"project": "title", "author": "authors", "release": "date"}` の3キーのみ、
   `template_engine.py:62-66`）でループし、**このマッピングに存在しないキーは無条件で捨てられる**。
3. 最終的に `#show: project.with(...)` に渡るのは上記3キー由来の `params` のみ。

実際に一時プロジェクトで `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` を設定し
`sphinx-build -b typst` を実行したところ、生成された `.typ` の `#show: project.with(...)` には
`title`/`authors`/`date` の3行のみが出力され、`papersize`/`fontsize`/`us-letter`/`20pt` の文字列は
ファイル中に**一切現れなかった**（`grep` で 0 件）。`typsphinx/templates/base.typ` の `project()` 関数
定義側デフォルト（`papersize: "a4"`, `fontsize: 11pt`）がそのまま常に使われる。

**(2) `typst_toctree_defaults`（discovery #5）:**
`typsphinx/__init__.py:47` で登録されているが、`typsphinx/` 配下のどこからも参照されない
（`translator.py`/`writer.py`/`builder.py`/`template_engine.py` いずれにも参照なし）。実際の toctree
オプション（`maxdepth`/`numbered`/`caption`）は `TemplateEngine.extract_toctree_options()` が doctree の
toctree ノードから直接読み取っており、この設定を一切経由しない。

いずれも Phase 22.2 が `typst_output_dir`（登録されるが未使用）・`typst_package`（登録されるが壊れて
いた）に対して塞いだのと**同型の「登録だけして出力に効かない設定」の第三・第四のインスタンス**であり、
registration-only テスト（上記 `tests/*.py` 3ファイル）の陰に隠れて Phase 22.2 の CONF-01〜03 対象には
含まれていなかった。

**Phase 22.4 側の措置:** README の Custom Templates 例（旧 :137-141）から `typst_elements` の
`papersize`/`fontsize`/`lang` を剪定し、`typst_template_mapping` の例も修正した（プランナー実行分は
Plan 01 が担当）。Configuration Options の6件構成（現状5件 + `typst_documents`）は不変 — 本 todo の
対象である `typst_elements`/`typst_toctree_defaults` 自体の記載は元々「設定名の列挙」に留まるため、
README 側の記述自体は嘘ではない（実装の欠陥のみが本 todo の対象）。

## Solution

二択のいずれかを選ぶ:

- **(A)** 非マッピングキーをテンプレート関数へ渡す経路を実装し、`typst_toctree_defaults` を
  `TemplateEngine.extract_toctree_options()` 等から実際に消費させる。
- **(B)** 設定自体を削除する（Phase 22.2 CONF-01 の前例 — `typst_output_dir`/`typst_author_params`
  を全サーフェスから削除した実績）。

**いずれを採る場合も、config→output の回帰フィクスチャ**（Phase 22.2 CONF-03 `test_package_only_config_gate.py`
と同型 — 実 `typst.compile()` を伴い、設定値が実際に生成 `.typ`/PDF に反映されることを検証するテスト）を
同時に追加することを必須条件とする。registration-only な検証だけでは同じ欠陥が第五・第六のインスタンス
として再び埋没する。
