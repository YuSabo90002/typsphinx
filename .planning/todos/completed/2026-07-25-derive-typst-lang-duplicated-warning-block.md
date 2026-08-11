---
created: 2026-07-25T00:00:00+09:00
title: derive_typst_lang() の警告ブロックが 2 つの棄却分岐で逐語的に重複
area: template_engine
resolves_phase: 45
source: .planning/phases/27.1-typst-text-lang-from-sphinx-language-config/27.1-REVIEW.md (IN-01, Info)
files:
  - typsphinx/template_engine.py (`derive_typst_lang()` の 2 つの棄却分岐)
---

## 経緯

Phase 27.1 のコードレビューが Info 深刻度で報告し、オーケストレータが意図的に見送った
もの。**記録のみ。ここでは直さない。**

## 症状

`derive_typst_lang()` は入力を 2 箇所で棄却する（非 str/None・空文字列と、
`re.fullmatch(r"[a-z]{2,3}", head)` 不一致）。どちらの分岐も同じ `logger.warning(...)`
呼び出しを逐語的にコピーしている。

## 見送った理由

- レビュア自身が「今日時点では低リスク」と評価している。
- 共通化すると D-03（棄却時は警告してパラメータを省略、ビルドは絶対に落とさない）の
  棄却セマンティクスに触れることになり、機能上の利得がない。
- 分岐が 3 つ目に増えるか、警告文面を変える必要が出た時点で初めてドリフトの実害が出る。
  その時にまとめて直すのが妥当。

## 直すなら

警告文面の組み立てを 1 つのヘルパに寄せ、各分岐は棄却理由だけを渡す形にする。
`tests/test_template_engine.py` の `caplog` テストが警告に値 (`repr(malformed)`) が
含まれることを固定しているので、そこは維持すること。
