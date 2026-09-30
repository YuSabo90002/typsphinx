---
created: 2026-07-25T00:00:00+09:00
title: v0.6.3 リリース後に PR#98 を謝意コメント付きでクローズする
area: planning
files:
  - .planning/todos/completed/2026-07-25-verify-no-gap-between-pr98-and-phase25.md
---

## Problem

PR#98（AlCalzone、`fix: render captioned tables as figure(kind: table) instead of
broken heading`）は 2026-07-25 時点で **OPEN のまま**。Phase 25 が同 PR の再実装として
入っており、**ギャップ無しは実測確認済み**（PR#98 の 4 テストを verbatim 移植して 4/4
PASS、現行実装は厳密な上位集合 — 詳細は
`.planning/todos/completed/2026-07-25-verify-no-gap-between-pr98-and-phase25.md`）。

残るのはクローズという外向き・不可逆の操作だけ。オーナー判断（2026-07-25）で
**v0.6.3 が PyPI に出た後**に実施することにした。理由: 実際にリリースされたバージョン
番号を添えられるほうが、投稿者への説明として明確なため。

放置すると「PR は結局どうなったのか」が残る。**遅くとも v0.6.3 milestone 完了時まで**。

## Solution

**トリガ**: `/gsd-complete-milestone` で v0.6.3 が publish された直後（タグ `v0.6.3` →
`release.yml` → PyPI + GitHub Release の完了後）。

1. リリース済みを確認: `gh release view v0.6.3` / PyPI に 0.6.3 が出ていること
2. PR#98 に謝意付きコメントを投稿。含める要素:
   - 報告と修正への感謝（キャプション付きテーブルが heading に化ける問題の指摘そのものが
     Phase 25 の起点になった）
   - v0.6.3 で出荷済みであること + 該当コミット/フェーズ
   - PR の内容に加えて取り込んだもの: `:width:` との合成（`block(width:)[#figure(...)]`）、
     `<label>` 二重定義の回避（Typst の "label occurs multiple times" 回避）、
     csv-table/list-table/`:numref:` を含む実 `typst.compile()` 回帰ゲート
   - 意図的な差分 1 件: 空キャプションはプレーン table にフォールバックする
     （空 caption の figure は無意味な "Table N" 番号を生むため）
3. クローズ（マージではなくクローズ — 実装は別経路で入っているため）

**注意**: 他者の PR に対する不可逆操作。実行前にコメント文面をオーナーに提示して確認を取る。

## Result (2026-07-25)

実施済み。v0.6.3 の PyPI 公開（`typsphinx-0.6.3-py3-none-any.whl` / `.tar.gz`）と
GitHub Release 作成を確認したうえで、PR#98 にコメントを投稿してクローズした。
コメント: https://github.com/YuSabo90002/typsphinx/pull/98#issuecomment-5078139533

**当初の想定と変わった点（重要）:** 投稿前に PR#98 のスレッドを確認したところ、
2026-07-23 のオーナー返信に対して AlCalzone が

> Given the divergence, would you rather like to have issues reported with the details instead?

と**問い返しており、2 日間未応答のまま**だった。この質問に触れずに謝辞＋クローズを
投稿すると「質問を黙殺して閉じた」形になるため、文面の主眼を**質問への回答**に変更した
（オーナー判断: **PR を歓迎する**）。

またオーナーの指摘で、PR が 1 ヶ月放置された実際の原因は「ブランチが古かった」ことでは
なく **dependabot の PR に埋もれて見落とした**ことだと判明。当初の下書きは "the age of the
base" を理由に置いており、投稿者側の落ち度に読める文面だったため書き直した。最終版では
「あなたの PR は送った時点で古くなかった、こちらが見落とした」と一文だけ置き、経緯の詳説と
再発防止の約束（未実施のため外向きの約束にできない）は削除。オーナー方針で全体も 40 行 →
12 行に圧縮した。

**教訓:** 他者の PR/issue に投稿する前に、必ずスレッド全体を読んで未応答の質問が無いか
確認すること。todo に書かれた「謝意してクローズ」だけを実行すると、相手が待っている
問いを踏み潰す。
