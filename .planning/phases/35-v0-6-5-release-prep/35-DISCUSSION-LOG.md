# Phase 35: v0.6.5 Release Prep - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 35-v0.6.5 Release Prep
**Areas discussed:** CHANGELOG の書き方, Phase 34 レビュー 4 Warning の扱い,
`/gsd-complete-milestone` への申し送り, リリースページの肥大（ユーザー提起）,
SC#3 の実走証跡の範囲

**提示したが選ばれなかった領域:** なし（4 領域提示中 3 領域を選択、SC#3 は最後に追加で議論）

---

## 領域選択

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG の書き方 | 報告された形と実測で壊れていた形の食い違いをどう書くか | ✓ |
| Phase 34 レビュー 4 Warning の扱い | 拾うか据え置くか | ✓ |
| complete-milestone への申し送り | ハンドオフ文書と 2 リポジトリタグ | ✓ |
| SC#3 の実走証跡の範囲 | docs ビルドを足すか | ✓（最後に追加） |

---

## CHANGELOG の書き方

### Q1: `### Fixed` 本文で壊れていた範囲をどの粒度で書くか

| Option | Description | Selected |
|--------|-------------|----------|
| 文脈を列挙する | 箇条書き項目 / 定義リストの用語 / フィールド値を具体的に列挙。判定しやすいが長い | |
| 一般文のみ | 「テキストの直後の inline math で落ちていた」だけ。実態より広く読まれる | |
| 一般文＋括弧で代表例 | 「テキストの直後の inline math（箇条書き項目や定義リストの用語など）」 | ✓ |

**Notes:** 実測で fixture の Construct A（トップレベル段落、空白なし形を含む）は修正前から緑、
赤だったのは B〜F。この食い違いが質問の前提。

### Q2: display math（list item 内）を別項目にするか

| Option | Description | Selected |
|--------|-------------|----------|
| 同じ項目に含める | 1 bullet に inline も display も。前例 D-09 の粒度規則 | ✓ |
| 別の bullet にする | 未追跡の欠陥だったので独立した修正として見せる | |

### Q3: `## [0.6.5]` の節構成

| Option | Description | Selected |
|--------|-------------|----------|
| リード＋Fixed＋Verified | 0.6.1/0.6.3/0.6.4 の前例踏襲 | ✓ |
| リード＋Fixed のみ | ホットフィックス最小 | |
| Fixed のみ（リードなし） | 過去エントリと体裁が変わる | |

### Q4: `### Verified` に載せる項目

| Option | Description | Selected |
|--------|-------------|----------|
| 不変量2点＋コーパスゲート | 新規依存ゼロ / `@preview` 未バンプ / フルコーパス fatal-free | ✓ |
| 上記＋fixture の RED→GREEN | GATE-01 のバーを対外にも示す | |
| 不変量 2 点のみ | Phase 33 D-03 の厳格版 | |

**User's choice:** D-01〜D-04 として CONTEXT に記録。文面の具体は Claude 裁量。

---

## Phase 34 レビュー 4 Warning の扱い

### Q1: どこまで拾うか

| Option | Description | Selected |
|--------|-------------|----------|
| 全件据え置き（todo 化） | 最小ホットフィックス方針に忠実、リリース最速 | |
| テスト 3 件だけ拾う | WR-02/03/04 は `typsphinx/` 無変更で不変量 #3 に抵触しない | ✓ |
| 4 件全部拾う | WR-01 も直す。translator 再変更で GATE-01 と コーパスゲートの再走が必要 | |

### Q2: WR-02 を閉じる形

| Option | Description | Selected |
|--------|-------------|----------|
| 既存 fixture に Construct G を追加 | ビルド回数が増えず、6 構成と同じ場所に集約 | ✓ |
| 別 fixture / 別テストにする | 既存出力を動かさないが `sphinx-build` が 2 回分増える | |

### Q3: テスト追加のフェーズ内位置付け

| Option | Description | Selected |
|--------|-------------|----------|
| 版バンプの前の独立プラン | REL-03 スコープ外の付随作業として CONTEXT に明記 | ✓ |
| ROADMAP に SC を 1 つ追加 | verify の判定対象にするがフェーズ境界を公式に広げる | |

**User's choice:** D-05〜D-07。WR-01 は todo 化（D-10 で Phase 35 が todo ファイルを作る）。

---

## `/gsd-complete-milestone` への申し送り

### Q1: 2 リポジトリタグ（v0.6.4 D-07 の standing cost）を守るか

| Option | Description | Selected |
|--------|-------------|----------|
| 守る（今回も両方に打つ） | `/ja/stable/` と `/en/stable/` が同じ版を指す状態を維持 | ✓ |
| 今回は打たない | docs 無変更なので省略。standing cost に例外を作ることになる | |

**Notes:** 実測 — 翻訳リポジトリのタグは `v0.6.4` のみ、RTD の en `stable` も tag `v0.6.4`
（identifier `2bf6ef3`）。今回の `docs/` 差分はゼロ。

### Q2: 申し送りをどこに書くか

| Option | Description | Selected |
|--------|-------------|----------|
| 専用の `35-HANDOFF.md` | Phase 33 前例。complete-milestone がそれ 1 枚を読めば済む | ✓ |
| SUMMARY / VERIFICATION 内の節 | ファイルを増やさない最小限 | |
| 作らない | ROADMAP 注記と standing decision に任せる | |

### Q3: 帳簿類をどちらの側でやるか

| Option | Description | Selected |
|--------|-------------|----------|
| WR-01 todo は 35、REL-03 は close 側 | 拾わない決定は今記録、チェックボックスは publish 後 | ✓ |
| 全部 Phase 35 でやる | REL-03 の `[x]` 化を先行させる | |
| 全部 close 側に回す | Phase 35 は版バンプ＋CHANGELOG＋テスト＋HANDOFF に専念 | |

**User's choice:** D-08〜D-10。

---

## リリースページの肥大（ユーザー提起）

**提起:** 「次バージョンの release ページだが、コミットを全部挙げつらっているのでくっそ長い。
コンパクトにしたい」

**実測して提示した事実:** v0.6.4 のリリース本文は 308 行。1〜296 行が `release.yml` の
"Generate release notes" ステップの `git log $PREV_TAG..$TAG --pretty="- %s (%h)"` によるコミット
羅列、297〜303 行が Installation、304〜308 行が `generate_release_notes: true` による GitHub
自動生成分（What's Changed の PR 1 行 + Full Changelog リンク）。自動生成は既にコンパクトで、
肥大の原因は自前の `git log` ブロック。あわせて `release.yml` が `CHANGELOG.md` を一度も読んで
いないことも判明（Phase 33 CONTEXT の「CHANGELOG が Release body の単一ソース」は実態と食い違い）。

### Q1: `release.yml` の修正を Phase 35 に入れるか

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 35 で直す | v0.6.5 からコンパクトになる。ただしタグ push 時にしか実行されない | |
| v0.6.5 は見送り、todo に落とす | 最小ホットフィックス方針を守る。今回は 33 コミットなので v0.6.4 よりは短い | ✓ |

### Q2: 直す場合のリリース本文の形（todo に設計方針として記録）

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG 抽出＋Installation＋自動生成 | `git log` を廃し `## [X.Y.Z]` 節を抽出。What's Changed と Full Changelog は残る | ✓ |
| 自動生成＋Installation のみ | 最も単純だがキュレーションした文章がリリースページに出ない | |
| コミットを選別して残す | `docs(`/`chore(` を除外。プレフィックス規則に依存する脆い仕組み | |

**User's choice:** D-11 — v0.6.5 では見送り、設計方針（CHANGELOG 抽出案）ごと todo に記録する。

---

## SC#3 の実走証跡の範囲

| Option | Description | Selected |
|--------|-------------|----------|
| docs ビルドも実走する | `tox -e docs-html` / `docs-pdf` を足す。Phase 28 D-05 の前例 | ✓ |
| SC 名指しの 3 種だけ | docs は今回 1 行も変わっていない | |

**User's choice:** D-12。

---

## Claude's Discretion

- CHANGELOG `[0.6.5]` の具体的な文面・リード段落の言い回し・要件 ID の付け方
- WR-02/03/04 の assertion の具体的な文字列と Construct G の reST の書き方
- フェーズ内のプラン分割（順序だけ D-07 で固定）
- `35-HANDOFF.md` の形式・見出し構成
- `uv.lock` の再生成手順
- 2 件の todo ファイルの文面・frontmatter・ファイル名
- 実走証跡の記録先（`35-VERIFICATION.md` は verify の予約名なので回避すること）

## Deferred Ideas

- **WR-01**: `visit_math_block` の余分な空行（`typsphinx/translator.py:4079-4088`）→ todo 化
- **`release.yml` のリリース本文改修**（CHANGELOG 抽出方式）→ todo 化、v0.6.6+
- **30.1 レビューの 3 Warnings** — REQUIREMENTS § Out of Scope で既決、v0.6.5 対象外
- **5 件の pending todo** — 同上（`todo.match-phase 35` が返したが、既決のため折り込みは問わず）
