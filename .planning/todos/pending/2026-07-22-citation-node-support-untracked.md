---
created: 2026-07-22T00:00:00+09:00
title: translator に citation / label ノードのハンドラが無い（未追跡の機能欠落）
area: translator, examples
source: .planning/phases/22.2-dead-config-value-sweep/ (plans 22.2-02, 22.2-06 の実行時に発見)
files:
  - typsphinx/translator.py:2257 (「citation ハンドラ無し」のコード内コメント)
  - examples/charged-ieee/approach1/source/index.rst (citation 構文を除去済み)
  - examples/charged-ieee/approach2/source/index.rst (citation 構文を除去済み)
---

## 経緯

Phase 22.2（Dead Config-Value Sweep）の実行中、プラン 22.2-02 と 22.2-06 の両方が、
同梱サンプル `examples/charged-ieee/` の rST **citation 構文を削除**した。

削除理由は「サンプルが壊れていたから」ではなく、**typsphinx が citation ノードを扱えないから**である。
`TypstTranslator` に `visit_citation` / `visit_label` ハンドラが存在せず、docutils の visitor が
未知ノードに対して隣接する式をセパレータ無しで並べて出力するため、生成された `.typ` が
Typst の構文エラーで hard fail する。

つまり Phase 22.2 が行ったのは**回避であって修正ではない**。フェーズのスコープ（CONF-01/02/03）
から外れていたため、当時の判断としては正しい。

## なぜ todo として起票するか

この欠落は **どこにも追跡されていなかった**:

- `.planning/REQUIREMENTS.md` に該当する要件 ID なし
- `.planning/todos/` を全文検索しても `citation` にヒットするファイルは 0 件（2026-07-22 時点）
- ROADMAP のどのフェーズにも記載なし

Phase 22.2 の主旨は「サイレントに死んでいる機能を、テストが緑のまま見逃す経路を塞ぐ」ことだった。
citation 未対応をサンプル側の削除だけで閉じて未追跡のまま残すのは、まさにそのフェーズが
潰そうとした欠陥クラスと同型なので、最低限の可視化としてここに残す。

## 検討事項（未決）

1. **そもそも対応すべきか。** typsphinx の対象読者（Sphinx ドキュメント → PDF）にとって
   rST citation がどれだけ重要かは未評価。学術系テンプレート（`charged-ieee` など）を
   Typst Universe から使う導線が Phase 22.2 で開通したので、需要は上がる方向に見える。
2. **Typst 側の対応物。** Typst には `#cite` / `bibliography()` があるが、rST citation は
   BibTeX ではなくインライン定義なので、単純な 1:1 対応にはならない。
   `docutils.nodes.citation` / `citation_reference` / `label` の 3 ノードの扱いを設計する必要がある。
3. **最低限の代替。** 完全対応が重ければ、少なくとも「未対応ノードを無言で壊れた出力にする」
   のではなく、警告を出して graceful degrade する経路（既存の `DEG-*` 系と同じ扱い）にする案。

## 参考

- Phase 22.2 の該当記述: `.planning/ROADMAP.md` §"### Phase 22.2" の 22.2-02 プラン行
  （"the translator has no `visit_citation` handler ... routed to backlog as a flagged assumption"）
- `.planning/phases/22.2-dead-config-value-sweep/22.2-02-SUMMARY.md`
- `.planning/phases/22.2-dead-config-value-sweep/22.2-06-SUMMARY.md`
