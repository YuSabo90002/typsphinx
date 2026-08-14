---
created: 2026-08-14T19:32:35+09:00
title: "numref numbers diverge per master and vanish entirely for figures reachable only from a non-root master"
area: translator, docs
resolves_phase: 52
source: .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md (## numref measurement)
severity: major
files:
  - typsphinx/translator.py  # figure/caption emission -- no numref override exists here today, and D-01 keeps it that way; a future fix would need to touch it
  - .planning/phases/51-documentation/  # Phase 51's own doc obligation (does not exist yet -- filed here as a forward pointer)
  - .planning/phases/52-changelog/  # Phase 52's own CHANGELOG obligation (does not exist yet -- filed here as a forward pointer)
  - tests/fixtures/state_guard_numref_two_case_gate/  # the live fixture this todo's own measurement came from
  - tests/test_state_guard_numref_gate.py  # the measurement gate (not an assertion gate for the numbering outcome)
---

## Problem

Phase 49 の状態ガード付き per-master 合成では、`:numref:` の番号付けに **2つの独立した数え方**
が併存する。Sphinx は `root_doc` を起点とする**単一の**走査（`assign_figure_numbers()` /
`env.toc_fignumbers`、`sphinx/environment/collectors/toctree.py:285-378`）でプロジェクト全体に
わたって図番号を焼き込むのに対し、Typst 自身の `figure()` カウンタは**コンパイルされる
wrapper ごとに独立**している。両者の食い違いを検知するコンパイルエラーはどこにも存在しない。

`tests/fixtures/state_guard_numref_two_case_gate/` で実測した2ケース
（`49-EVIDENCE.md` の `## numref measurement` セクションに生データあり）:

- **Case (a) — 番号が食い違う:** 図 `fig-x` は両方の master（`index` と `other_master`）から、
  それぞれ異なる走査位置で到達可能。Sphinx は `:numref:` の参照テキストに **同一の焼き込み済み
  番号**（`"Fig. 1."`）をどちらの master にも埋め込む（numref の置換は master を意識しない）。
  一方 Typst 側のキャプション番号は master ごとに別々に数えられる: `index` 単独コンパイルでは
  `fig-x` が唯一の図なので Typst 番号 `1`（たまたま一致）。`other_master` コンパイルでは
  `fig-x` の手前に2つの図（filler 図と `fig-y`）があるため Typst 番号は `3`（不一致）。
  同じ参照文言 `"Fig. 1."` が、片方の master では正しく、もう片方では誤った番号を指す。
- **Case (b) — 番号が一切割り当てられない:** 図 `fig-y` は `other_master` からしか到達できず
  （`root_doc` である `index` からは一切到達不能）、`root_doc` 起点の `env.toc_fignumbers` 走査
  には現れない。`get_fignumber()` が `ValueError` を送出し、`_resolve_numref_xref()` は生の
  ラベル文字列 `"fig-y."` にフォールバックする（図のキャプションタイトル
  `"Figure Y Caption"` ではなく、raw label）。Typst 自身はこの図に独自の番号（`2`）を
  ちゃんと割り当てているが、参照側のテキストは番号どころか何の対応も示さない。

**重要な訂正:** `49-CONTEXT.md` D-01 および `49-EXPECTED-STRUCTURE.md` fixture specification
entry 10 はいずれも Case (b) を「ゼロ警告での静かなフォールバック」と特徴づけていたが、これは
**実測により誤りと判明した**。Sphinx 9.1.0 の実際のソース
(`sphinx/domains/std/__init__.py` `_resolve_numref_xref()` の `except ValueError:` 節) は
`logger.warning(...)` を呼んでから `contnode` を返す。実際のビルドでも
`WARNING: クロスリファレンスの作成に失敗しました。番号が割り当てられていません: fig-y`
（英語: "Failed to create a cross reference. Any number is not assigned: fig-y"）という警告が
1件だけ出る。つまり：**コンパイル済み PDF の読者には何の手がかりもないが、ビルドログの読者には
対象ラベル名を名指しした診断が渡る。** この訂正はオーナー承認済み（49-06 の checkpoint 応答で
確認済み）。

## Solution

これは **修正がスケジュールされた todo ではなく、ドキュメント化された制限事項**である。D-01 が
既に決めている通り、この乖離は Phase 49 では直さず、Phase 51 と Phase 52 に引き継ぐ。

- **Phase 51（ドキュメント）が書くべきこと:**
  1. 複数の master から到達可能な図は、master によって `:numref:` の参照番号が実際の
     キャプション番号と一致しない場合がある（コンパイルエラーなし）。
  2. root master からしか到達できない図と異なり、非 root master からしか到達できない図への
     `:numref:` 参照は、番号ではなく生のラベル文字列（例: `fig-y`）にフォールバックする。
  3. 上記2のケースでは Sphinx のビルドログに
     `Failed to create a cross reference. Any number is not assigned: <label>`
     という警告が出る（PDF 自体には手がかりが出ない）。
- **Phase 52（CHANGELOG）が書くべきこと:** これを per-master 合成の既知の制限として告知する
  こと（このマイルストーンで導入された退行ではなく、Sphinx の単一 root 番号付けモデルと
  Typst のコンパイル単位ごとのカウンタが出会うことで元々内在していた不整合が、Phase 47 の
  two-layer split で per-master 合成が可能になって以来ずっと存在し、Phase 49 で初めて実測
  された、という位置づけ）。
- **もし将来 実際に直すなら（あくまで方向性であって計画ではない）:** `:numref:` 解決を
  master 単位で再計算する仕組み（Typst 側のカウンタを Sphinx 側に投影し直すか、逆に
  Sphinx の焼き込み済み番号を捨てて Typst 側のカウンタを `:numref:` 参照テキストにも
  反映させる）が要る。後者は `typsphinx/translator.py` の figure/caption 発行箇所と
  参照解決の両方を触る必要があり、D-01 が明示的に対象外としている「番号付け機構の変更」に
  該当するため、Phase 49 の範囲では選択されなかった。コストは未見積もり。

再測定データの一次ソース: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md`
の `## numref measurement` セクション（抽出値テーブルが最初、読み解きがその後という順序で
記録されている）。
