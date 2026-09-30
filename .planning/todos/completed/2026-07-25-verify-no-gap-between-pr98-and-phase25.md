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

## Result (2026-07-25)

**ギャップ無し。** 検証方法と結果:

### 1. 挙動ベースの突き合わせ（ステップ 1）

PR#98 の 4 本のユニットテストを **verbatim で移植し、現行実装に対して実行** → **4/4 PASS**。
（`_build_table` ヘルパー・アサーション文字列とも PR#98 の diff から無改変。検証後に一時
ファイルは削除。）実装の書き方は Phase 25 の方が大きく異なるが、**出力される Typst は
PR#98 のアサーションを全て満たす**。

現行実装は PR#98 の**厳密な上位集合**:

| 要素 | PR#98 | 現行（Phase 25） |
|------|-------|------------------|
| caption buffering (`visit_title`/`depart_title`) | あり | あり（`_caption_saved_list_state` の save/restore まで同一） |
| `figure(..., caption: {...}, kind: table)` | あり | あり（同一書式） |
| stale buffer 対策 (`del self.table_cell_content`) | あり | あり |
| `:width:` との合成 (`block(width:)[#figure(...)]`) | なし | あり（D-04） |
| `<label>` 自己アンカー + 二重定義回避 (TBL-02) | なし | あり（`visit_table` 側の `_emit_id_anchors` スキップ） |
| `columns:` fr 重み付け | `columns: N` | `columns: (1fr, 1fr)`（FID-01a 由来、PR#98 の後） |
| 実 `typst.compile()` 回帰ゲート | なし | あり（`tests/fixtures/captioned_table_render_gate/`、csv-table/list-table/`:numref:` 含む） |

**意図的な差分 1 件**: 空キャプションの扱い。PR#98 は `if self.table_caption is not None:`
で空 caption でも `figure(caption: {})` を出す。現行は `if self.table_caption:`（truthy）で
プレーン table にフォールバックする。Phase 25 が
`test_empty_table_title_falls_back_to_plain_table` で明示的に選択した挙動であり、退行では
なく設計判断（空 caption の figure は無意味な "Table N" を生む）。

### 2. テスト等価カバレッジ（ステップ 2）

PR#98 の 4 本は Phase 25 に**同名で全て存在**。ただしアサーションの厳密さに差があったため
**補強済み**（`tests/test_translator.py`、テストのみ・実装無変更）:

- `test_captioned_table_renders_as_figure` — `caption: {text("...")}` の**スロット内**であること、
  および figure ラップ後も内側の `table(` とセルが残ることを追加
- `test_table_caption_supports_inline_markup` — `emph({text("Important")})` の**合成形**と
  caption スロット内であることを追加
- `test_table_caption_not_lost_after_previous_table` — caption が**ちょうど 1 回**しか出ない
  ことを追加（セルへの漏れ検出）
- `test_table_caption_not_lost_after_uncaptioned_table` — **新規**。PR#98 の元の再現手順
  （非キャプション表 → キャプション表の順）を明示的に固定

全スイート **605 passed / 1 skipped**、black・ruff クリーン。

### 3. 残作業

PR#98 のクローズ（謝意付きコメント）— **未実施**。外部の PR に対する不可逆操作のため
オーナー判断待ち。
