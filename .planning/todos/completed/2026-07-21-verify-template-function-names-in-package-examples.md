---
created: 2026-07-21T20:40:31+09:00
updated: 2026-07-21T21:05:00+09:00
closed: 2026-07-22
closed_by: Phase 22.2 (dead-config-value-sweep) — CONF-02 / CONF-03
status: resolved
title: typst_package (Typst Universe) path is broken end-to-end
area: general
files:
  - typsphinx/writer.py:151-153
  - typsphinx/builder.py:371-374
  - typsphinx/template_engine.py:185-191
  - typsphinx/template_engine.py:423 (_format_authors_with_details — dead code)
  - docs/source/examples/advanced.rst:22-68
  - docs/source/user_guide/templates.rst:42
  - docs/source/user_guide/configuration.rst:83,218
---

## Problem

元々は「`typst_template_function = {"name": "ieee"}` は正しいか」というドキュメント確認の
todo だったが、実ビルド＋実コンパイルで検証したところ **`typst_package` を使う
Typst Universe パッケージ経路そのものが動作しない**ことが判明した。ドキュメントの
"Using Typst Universe Packages" セクション全体が、コンパイルできない設定例を掲載している。

### 検証方法

`typst 0.15.0` / `typst-py`（`.venv`）で、docs の charged-ieee 例をそのまま
`conf.py` に写した最小 Sphinx プロジェクトを `sphinx-build -b typst` し、
生成された `.typ` を `typst.compile()` にかけた。

### 確認済みの事実

1. **`"name": "ieee"` 自体は正しい。** `name` はパッケージ名ではなく export される
   Typst 関数名。`~/.cache/typst/packages/preview/charged-ieee/0.1.4/lib.typ:3` に
   `#let ieee(` がある。`"charged-ieee"` にするとむしろ `unresolved import` になる。
   → **元の疑問への答えは「合っている」。**

2. **BUG-A（致命的）: `_template.typ` が無いのに import される。**
   `writer.py:151-153` は `template_file="_template.typ"` を無条件に渡すため、
   出力に `#import "_template.typ": ieee` が必ず入る。一方
   `builder.py:371-374` は `typst_package` が設定されていると
   `_write_template_file()` を早期 return して `_template.typ` を書かない。
   結果、`typst_package` だけを設定した（`typst_template` は未設定の）構成で
   `file not found (searched at .../_template.typ)` となりコンパイル不能。
   ※ `advanced.rst:126-133` の important 注記は「`typst_package` と `typst_template`
   を併用するな」と書いているが、実際には **`typst_package` 単独でも同じ失敗をする**。
   注記の因果説明が実態と食い違っている。

3. **BUG-B: `date` が無条件に注入される。** `template_engine.py:190-191` が
   `params["date"]` を常に設定するため `#show: ieee.with(..., date: "")` が出る。
   `charged-ieee` の `ieee()` は `date` 引数を持たないので、BUG-A を手で回避しても
   次に `unexpected argument: date` で落ちる（実測）。`title`/`authors` も同様に
   無条件注入（`:186-189`）なので、それらを受け取らないパッケージ関数は全滅する。

4. **BUG-C: `typst_authors` / `typst_author_params` が完全に無視されている。**
   `_format_authors_with_details()` (`template_engine.py:423`) は
   **どこからも呼ばれていない dead code**（`grep` でヒットは定義行のみ）。
   実際の出力は `authors: ("John Doe",)` という素の文字列 tuple で、
   docs が謳う department/organization/email 付き dict にはならない。

5. **BUG-D（docs）: modern-cv の例は二重に誤り。**
   `advanced.rst:59` の `"name": "modern-cv"` は `unresolved import`（実測）。
   modern-cv 0.7.0 の entry 関数は `resume`（`lib.typ:193`）。
   さらに `resume(author:, date:, accent-color:, ...)` は `title`/`authors` を
   受け取らないため、`resume` に直しても BUG-B により
   `unexpected argument: title` で落ちる（実測）。
   例の params（`name`/`job-title`/`email`/`github`）も `resume` の引数ではなく、
   `author` dict の中身。

### 補足

`advanced.rst` の "Custom Template Wrapping"（ラッパー `.typ` を `typst_template`
で指定する経路）は、ラッパー側が `project(title:, authors:, date:, body)` を
受け取るので BUG-B を回避でき、現状で唯一動くパッケージ利用法と思われる（未実測）。

## Solution

コード修正が要るので docs todo ではなくフェーズ相当。想定スコープ：

1. `writer.py` — `typst_package` かつ `typst_template` 未設定なら
   `template_file` を渡さない（`_template.typ` の import を出さない）。
2. `template_engine.map_parameters` — `title`/`authors`/`date` の無条件注入をやめ、
   対象テンプレート関数が受け取る引数だけ渡す仕組みにする
   （`typst_template_mapping` での除外、あるいは明示 opt-in など要設計）。
3. `_format_authors_with_details()` を実際に配線するか、削除して
   `typst_authors`/`typst_author_params` を docs から落とす（どちらか決める）。
4. docs の modern-cv 例を `resume` + 正しい `author` dict に修正、
   `advanced.rst:126-133` の important 注記を実態に合わせて書き直し、
   ja `.po` も追随。
5. **GATE-01 準拠**: `typst_package` 経路の実 `typst.compile()` リグレッション
   fixture を追加する（これが無かったから壊れたまま出荷されている）。

再現手順は上記「検証方法」の通り。最小再現プロジェクトは
scratchpad に作成済み（セッション破棄で消えるので必要なら再作成）。

## 着手先（2026-07-21 更新）

バックログ **999.4「Dead Config-Value Sweep」の scope 要素 2** に統合。
元の 999.3 は 999.4 に merge され、BUG-A..BUG-D の証拠記録として ROADMAP に残置。

統合理由: 死んだ `typst_output_dir`（`.planning/todos/pending/2026-07-21-dead-typst-output-dir-config.md`）
と根本原因が同一 — 「登録されている」「文書化されている」ことだけを検証するテストが緑のまま、
**設定値が実際に出力へ影響するかを誰も検証していない**。上記スコープ 5 のフィクスチャは
999.4 の scope 要素 3（config→output リグレッションフィクスチャ）として両者をまとめて塞ぐ。

## 決着（2026-07-22）

**Phase 22.2 CONF-02/CONF-03 で解決済み。** BUG-A..BUG-D をすべて閉じた:

- **BUG-A** — `_template.typ` の有無について `writer.py` と `builder.py` が食い違う問題は、
  ルーティング規則を単一の `resolve_package_for_engine()`（`template_engine.py:15`）に集約して解消。
  両者が再び分岐できない構造になった（コードレビュー WR-04）。
- **BUG-B** — パッケージ経路での `title`/`authors`/`date` 無条件注入をゲート。
- **BUG-C** — `typst_authors` はネイティブな `list[dict]` として配線済み（dead code のまま放置しない選択）。
  `typst_author_params` の方は CONF-01 で削除。
- **BUG-D** — `advanced.rst` のパッケージ例を実測挙動に合わせて修正（ja `.po` も追随）。
- **BUG-E/F**（22.2 で追加検出）— 明示設定が自動導出デフォルトに勝つよう修正。

**GATE-01 準拠のフィクスチャも着地**: `tests/test_package_only_config_gate.py`（12 tests、
実 `typst.compile()` バック、各 BUG の pre-fix failure proof 付き）、
`tests/test_package_template_routing.py`、`tests/test_examples_charged_ieee_gate.py`。
verifier が BUG-A 修正前のコミットに対して現行ゲートを再実行して赤になることを確認済み
（vacuous でない red→green）。

同梱サンプル `examples/charged-ieee/approach2` が既定テンプレートへ黙ってフォールバックしつつ
exit 0 していた件も同フェーズで発覚・修正され、`@preview/charged-ieee:0.1.4` を実際にロードした
PDF を出すようになった。

**残件（このtodoからは切り出し済み）**: サンプルから撤去した rST citation の恒久対応は
`.planning/todos/pending/2026-07-22-citation-node-support-untracked.md` で追跡中。
