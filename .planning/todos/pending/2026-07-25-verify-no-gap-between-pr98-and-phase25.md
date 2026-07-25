---
created: 2026-07-25T00:25:39.888Z
title: PR#98 と Phase 25 実装の間にギャップが無いか確認する
area: translator, planning
files:
  - typsphinx/translator.py
  - tests/test_translator.py
  - .planning/phases/25-captioned-table-figure-wrap-cross-references-reimplement-pr-/25-VERIFICATION.md
---

## Problem

Phase 25「Captioned Table Figure Wrap + Cross-References」は **PR#98 の再実装** として
計画・実行された（ROADMAP の見出しにも `(reimplement PR#98)` と明記）。PR#98 は
2026-07-25 時点で **OPEN のまま**（`gh pr view 98` → `state: OPEN`）で、変更対象は
`typsphinx/translator.py` (+59/-7) と `tests/test_translator.py` (+122/-0) の 2 ファイル。

Phase 25 は独自の SC 5 本（figure ラップ / caption 無しは素の table / caption+width の合成 /
2 枚目以降の stale buffer / `:numref:` ラベル解決）を立てて実装したため、**PR#98 が直していて
Phase 25 が拾い漏らした挙動が無いか**が未検証。PR#98 側にしか無い分岐やテストケースが
残っていると、PR をクローズする際に「再実装済み」と言い切れない。

具体的に突き合わせるべき PR#98 の要素（diff から抽出）:

- `visit_title`/`depart_title` のテーブル内キャプション buffering（インラインマークアップ保持）
- `depart_table` での `figure(\n{table_code},\n caption: {...}, kind: table)` 生成
- `self.table_caption` 初期化と、`table_cell_content` の削除による stale state 防止
- PR#98 のユニットテスト 4 本:
  `test_captioned_table_renders_as_figure` /
  `test_table_caption_supports_inline_markup` /
  `test_table_caption_not_lost_after_previous_table` /
  `test_uncaptioned_table_not_wrapped_in_figure`

## Solution

1. `gh pr diff 98` を取得し、現行 `typsphinx/translator.py` の該当箇所と挙動ベースで突き合わせる
   （実装の書き方の差異ではなく、**出力される Typst が同じか**で判定する）。
2. PR#98 のテスト 4 本それぞれについて、Phase 25 が入れたテスト
   （`tests/test_translator.py` + `tests/test_pdf_render_gate.py`）に等価カバレッジがあるか確認。
   欠けていれば当該ケースを追加する。
3. ギャップ無しと確認できたら、PR#98 に「Phase 25 で再実装済み・該当コミット」を添えて
   コメント＋クローズ（作者への謝意を含める）。ギャップがあれば残差だけを別 todo/phase に切る。

**タイミング**: v0.6.3 のリリース準備（Phase 28）と同時か、その直後。リリース後に
「PR は結局どうなったのか」を残さないため、遅くとも milestone 完了時までに片付ける。
