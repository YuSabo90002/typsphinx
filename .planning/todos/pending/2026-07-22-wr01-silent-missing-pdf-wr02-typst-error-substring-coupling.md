---
created: 2026-07-22T00:00:00+09:00
title: WR-01 マスター .typ 欠損時の無言スキップ / WR-02 テストが typst-py のエラー文言に結合
area: builder, tests
source: .planning/phases/22.1-typstpdf-compile-root-alignment-for-nested-masters/22.1-REVIEW.md
files:
  - typsphinx/builder.py:895-897 (`if not path.exists(typ_file): logger.warning(...); continue` — failures に入らない)
  - typsphinx/builder.py:850-856 (docstring の「もう黙って成功しない」という主張)
  - tests/test_nested_master_render_gate.py (typst-py のエラー文字列に依存する assertion)
---

## 経緯

Phase 22.1（PDF-02 コンパイルルート整合）の `/gsd-code-review` で検出された Warning 2 件。
2026-07-22 の UAT テスト 5 で**オーナー判断により「バックログへ」**と決定（フェーズブロッカーにはしない）。

同レビューの Critical **CR-01** は別扱い — 「今直す」と判断され、gap `G-22.1-4` として
Phase 22.1 内で修正する。この todo には含めない。

## WR-01 — マスターの .typ が無いとビルドは黙って成功する

`TypstPDFBuilder.finish()` の docstring はこう主張している:

> If any master failed, a single ExtensionError naming every failure is raised after the loop,
> which surfaces as a non-zero sphinx-build exit -- a build can no longer "succeed" while
> silently producing no PDF for a broken master.

しかし `typsphinx/builder.py:895-897` の既存分岐:

```python
if not path.exists(typ_file):
    logger.warning(f"Master document not found: {typ_file}")
    continue
```

は `failures` リストに何も積まずに `continue` する。したがって
**「設定済みマスターの .typ が生成されていない」場合、`finish()` は exit 0 のまま
その PDF を黙って落とす。** docstring の保証（D-04「no silent success」）は不完全。

コンパイル失敗だけが `failures` に入り、ファイル欠損は入らない、という非対称。

### 検討事項

- 単純に `failures.append(...)` を足すと、これまで警告で済んでいたケースがビルド失敗に変わる。
  破壊的変更になり得るので、v0.6.2 のパッチ範囲でやるか次のマイナーに回すかの判断が要る。
- あるいは docstring の主張を実態に合わせて弱める（「コンパイル失敗については」と限定する）
  だけに留める選択肢もある。**どちらを取るかは未決。**
- 同じ扱いをすべきか要確認: 直前の malformed `doc_tuple` スキップ（`builder.py:885-890` 付近）も
  同様に `continue` している。

## WR-02 — SC#2 のテストが typst-py のエラー文言に結合している

`tests/test_nested_master_render_gate.py` の SC#2 / G-22.1-2 系テストは、
typst-py が返すエラーメッセージのリテラル部分文字列に対して assert している:

`"escape"`, `"not found"`, `"usage.typ"`, `"_template.typ"`

これらは typst / typst-py の**契約された API ではない**。上流が文言を変えると
typsphinx 側に何の問題も無いのにテストが赤くなる。

現時点（typst-py 0.15.0）では 4/4 通っており、**実害は無い。将来リスクのみ。**

### 検討事項

- `"usage.typ"` / `"_template.typ"` への依存は落としづらい — G-22.1-2 の要求そのものが
  「どちらの失敗クラスか」をファイル名で判別することだったため。安易に緩めると
  レビュアーが却下した「どちらでも通る tolerant な assertion」に逆戻りする。
- 現実的な緩和は `"escape"` / `"not found"` のような**分類語**の方を、より安定した
  シグナル（例外型、終了コード、あるいは複数候補の許容）に置き換える方向か。
- typst-py のバージョンを pin して「上流更新時に気づける」形にする案もある。

## Not now

v0.6.2 のスコープ外。Phase 22.1 は CR-01（G-22.1-4）のみ対応して閉じる。
着手は `/gsd-review-backlog` で昇格させたとき。
