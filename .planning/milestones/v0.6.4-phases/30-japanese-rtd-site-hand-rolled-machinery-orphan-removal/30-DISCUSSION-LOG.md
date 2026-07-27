# Phase 30: Japanese RTD Site + Hand-Rolled Machinery & Orphan Removal - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-26
**Phase:** 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
**Areas discussed:** ja サイトの PDF 出力, ja カタログの翻訳率, I18N-03 の台帳上の扱い,
ja プロジェクトのビルドソース（翻訳リポジトリ分離）, REL-02 / `/ja/stable/`, submodule ピン運用,
ロードマップ再分割, `docs/usage.rst` の中身, 削除セットの境界

---

## Gray area selection

Four areas were offered. The user selected two:

| Area offered | Selected |
|---|---|
| ja サイトの PDF 出力 | ✓ |
| 削除セットの境界 | (later, at the wrap-up check) ✓ |
| SC#3 grep の合否基準 | |
| docs/usage.rst 606 行の中身 | ✓ |

---

## ja サイトの PDF 出力

| Option | Description | Selected |
|--------|-------------|----------|
| ja では PDF を出さない | I18N-03 の据え置きを守る。PDF ジョブを `READTHEDOCS_LANGUAGE` で分岐させるなどして抑制 | |
| ja でも日本語 PDF を出す | 共有 yaml の振る舞いを受け入れ、グリフ検証ゲートを ja 側にも張る。実質 I18N-03 の前倒し | ✓ |
| ja サイトでも英語 PDF を配る | PDF ジョブの sphinx-build を en 固定に。`tests/test_readthedocs_config.py:270` の改定が伴う | |

**User's choice:** ja でも日本語 PDF を出す
**Notes:** 提示した実測は「`.readthedocs.yaml` が en/ja 両プロジェクトで共有され、`conf.py:52` が
`READTHEDOCS_LANGUAGE` を読むため ja プロジェクトは黙って日本語 PDF を作る」という衝突。選択後に
ローカル実測を追加（94 ページ / 1.81MB / CJK 1,997 文字 / exit 0）。

---

## ja カタログの翻訳率

| Option | Description | Selected |
|--------|-------------|----------|
| 24% のまま公開する | I18N-01 のバーは「実際の日本語散文が配信されている」であり 100% 翻訳ではない。未翻訳部は英語フォールバック | ✓ |
| 目次到達分だけ埋めてから公開 | api/index を除く約 285 件をこのフェーズで翻訳。スコープが大きく広がる | |
| PDF は完訳セクションのみに限定 | ja 専用 master document 定義が必要になり、en と ja で目次構成が分岐 | |

**User's choice:** 24% のまま公開する
**Notes:** 実測 257/1058 = 24.3%。`api/index.po` 0/513、`contributing.po` 0/97、
`changelog.po` 0/86、`user_guide/templates.po` 0/77 が丸ごと未翻訳。この事実は I18N-01 の SC#1
プローブ選定に直結するため CONTEXT.md `<specifics>` に記録した。

---

## ja PDF のグリフ検証ゲート

| Option | Description | Selected |
|--------|-------------|----------|
| ローカル ja PDF との内容比較＋抽出目視 | D-12 と同型だが「影響する 2 ページ」ではなく抽出したページを目視 | ✓ |
| CJK フォント埋め込みの確認だけ | 人間の目視を省く。D-14（テキスト抽出では豆腐を検出できない）をフォント存在で代替 | |
| en と同じ 4 項目をそのまま適用 | 逐語適用。固定 3 ページ目視 | |

**User's choice:** ローカル ja PDF との内容比較＋抽出目視

---

## I18N-03 の台帳上の扱い

| Option | Description | Selected |
|--------|-------------|----------|
| I18N-03 を v1 に昇格し Phase 30 に割当 | REQUIREMENTS.md の Future → v1、Traceability に行追加 | ✓ |
| I18N-01 の範囲内として扱う | 要件表は触らず CONTEXT.md に経緯だけ記録 | |
| I18N-03 をクローズ扱いにする | Future から削除し Deferred Items 行を書き換え | |

**User's choice:** I18N-03 を v1 に昇格し Phase 30 に割当
**Notes:** 後の分割決定（Phase 30.1）により、割当先は 30.1 になった。

---

## ja プロジェクトのビルドソース

RTD 公開 API の実測（`projects/sphinx/translations/` が 15 件、全て別プロジェクト・全て
`sphinx-doc/sphinx-doc-translations` をビルド）を提示した上で選択。

| Option | Description | Selected |
|--------|-------------|----------|
| 同一リポジトリを 2 回インポート（現行計画） | REQUIREMENTS.md Owner-Manual Steps 項目 2 のまま。`.readthedocs.yaml` も `docs/locale/ja/` も共有 | |
| 翻訳専用リポジトリに分離（Sphinx 方式） | `docs/locale/ja/` を別リポジトリへ移し、ja 専用 `.readthedocs.yaml` を持たせる | ✓ |

**User's choice:** 翻訳専用リポジトリに分離（Sphinx 方式）
**Notes:** 選択後、`sphinx-doc-translations` の実際の構造（submodule / `locales/` /
`.readthedocs.yml` / Transifex 駆動の `main.yml`）を実測し、乗ってくる作業量と **2 つの懸念**
（① I18N-02「自前機構を消す」と逆を向く、② REL-02 の `/ja/stable/` が崩れる）を提示して
再確認を求めた。

### 再確認

| Option | Description | Selected |
|--------|-------------|----------|
| 同一リポジトリ 2 回インポートに戻す | 現行計画。I18N-02 / REL-02 が自然に成立 | |
| 分離を進める | Sphinx 方式を採用。ROADMAP / REL-02 / Makefile unchanged の前提を書き換える必要 | ✓ |
| 別マイルストーンの候補にする | v0.6.4 は同一リポジトリで出し、分離は Future 要件として記録 | |

**User's choice:** 分離を進める（懸念提示後の再確認でも同じ判断）

---

## REL-02 / `/ja/stable/`

| Option | Description | Selected |
|--------|-------------|----------|
| 翻訳リポジトリにも連動タグを打つ | REL-02 の文面をそのまま満たす。リリース手順に 2 リポジトリ目の bump + tag push が恒久的に加わる | ✓ |
| ja は latest 運用にし要件を改訂 | Sphinx 本家と同じ。REL-02 の `/ja/stable/` 条項を改訂 | |
| Phase 33 に先送り | REL-02 のバーが未確定のまま Phase 31/32 を通る | |

**User's choice:** 翻訳リポジトリにも連動タグを打つ

---

## submodule ピンの運用

| Option | Description | Selected |
|--------|-------------|----------|
| GH Actions で自動 bump | Sphinx の `main.yml` と同型。新リポジトリにワークフロー執筆が必要 | ✓ |
| リリース時のみ手動 bump | 作業量は最小だが、間の期間は ja サイトが古い英語原文を基にビルドされる | |
| タグにピンする | ja サイトが常に「直近のリリース版の翻訳」になる | |

**User's choice:** GH Actions で自動 bump
**Notes:** Sphinx の `main.yml` は Transifex 前提（`TX_TOKEN` / `tx` CLI /
`lock-translations.py` / `generate_templates.sh` / `update.sh`）で typsphinx には写せないことを
実測済み。CONTEXT.md D-08 に「逐語コピー禁止」を明記。

---

## ja PDF の再確認（分離後）

| Option | Description | Selected |
|--------|-------------|----------|
| 維持する | ja 側にも `formats: [pdf]` と typstpdf ジョブを書く。グリフゲートも確定済みのまま | ✓ |
| ja は HTML のみに戻す | 共有 yaml の制約が消えたので抑制可能。I18N-03 を Future に戻す | |

**User's choice:** 維持する
**Notes:** 分離により前提（共有 yaml の強制）が消えたため、惰性で引き継がず新しい前提の上で
明示的に再確認した。

---

## ロードマップ上の扱い

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 30 を拡張して吸収 | ROADMAP の Phase 30 Goal / SC を書き換え、1 フェーズに収める | |
| Phase 30.1 として分割 | 30 = 自前機構削除＋孤児削除（I18N-02/DOC-08）、30.1 = 翻訳リポジトリ＋ja サイト（I18N-01/03）。v0.6.3 の 27/27.1 前例と同型 | ✓ |

**User's choice:** Phase 30.1 として分割

---

## docs/usage.rst の中身

| Option | Description | Selected |
|--------|-------------|----------|
| 丸ごと削除する | Phase 27 の `docs/configuration.rst` と同じ扱い。テストも同じコミットで削除 | ✓ |
| 所見を todo に残して削除 | 拾う価値のある内容を pending todo に記録してから削除 | |
| 不足 2 節を移設してから削除 | CI 節と Build Commands Reference 節を `user_guide/builders.rst` 等へ取り込む | |

**User's choice:** 丸ごと削除する
**Notes:** 実測 606 行、toctree 到達不能、`Continuous Integration` と
`Build Commands Reference` の 2 節は `docs/source/` 側に対応なし＝内容は完全に消える、を
提示した上での判断。

---

## 削除セットの境界

### `docs/Makefile` の gettext / locale-init / locale-update

| Option | Description | Selected |
|--------|-------------|----------|
| 翻訳リポジトリへ移す | Sphinx 方式。`.pot` 生成も `.po` 更新も submodule 経由で翻訳リポジトリ側 | ✓ |
| 本体に残す | ROADMAP の「unchanged」を守れるが、書き込み先の `docs/locale/` が消えるので実質壊れる | |
| gettext だけ本体に残す | 職分けは自然だが、生成物の受け渡しが 2 リポジトリにまたがる | |

**User's choice:** 翻訳リポジトリへ移す

### `html-ja` ターゲット

| Option | Description | Selected |
|--------|-------------|----------|
| 削除する | カタログが本体から消えると 100% 英語を出す＝緘いなく壊れるため | ✓ |
| 翻訳リポジトリへ移す | ローカル日本語プレビュー手段として翻訳リポジトリの Makefile へ | |

**User's choice:** 削除する

### `docs.yml` の `publish_dir`

| Option | Description | Selected |
|--------|-------------|----------|
| `docs/_build/html` へ向け直す | 1 行修正でツリーとの整合を保つ。ステップ削除は Phase 32 のまま | ✓ |
| ステップを無効化する | `if: false` 等で止め、削除は Phase 32 に残す | |
| Phase 30 でステップごと消す | Phase 32 の CI-04 を前倒し。不可逆作業を最後にする並びを崩す | |

**User's choice:** `docs/_build/html` へ向け直す

---

## Claude's Discretion

ユーザーが明示的に裁量へ委ねた、または議論せず確定させた項目:

- **`custom.css` 周り** — 全 7 ルールが `.language-switcher` 専用と実測済みのため、`custom.css`
  削除＋`html_css_files` 削除＋`html_static_path` 削除を裁量で確定（議論の場で提示、異論なし）。
- **翻訳リポジトリ名 `typsphinx-doc-translations`** — Sphinx 本家の命名に合わせて裁量で確定
  （提示済み、異論なし）。
- **ja RTD プロジェクトのスラッグ** — 当初 D-03 で「Phase 30 で決める」とされていたが、議論の
  結果「publish されないので決定事項ではない」と結論。`typsphinx-ja` を既定とし、埋まっていても
  止まらず任意の別名で可、という裁量枠に格下げ。
- **SC#3 の grep 合否基準** — 領域として選択されなかったが、実測で偽陽性 2 件
  （`tests/fixtures/confval_field_body_render_gate/index.rst:15`、
  `tests/test_readthedocs_config.py` の `html_context` アサーション 4 箇所）が判明したため
  CONTEXT.md の Claude's Discretion に扱いを記録。
- 翻訳リポジトリ側 `.readthedocs.yaml` の具体形、pin-bump ワークフローのトリガー設計、
  D-03 の目視対象ページの選び方、Furo 既定サイドバー復帰後の `conf.py` 追加調整の要否。

## Deferred Ideas

- ja カタログ翻訳率を 24.3% から引き上げる作業（api/index の 513 件を除いて約 285 件）
- D-07 の 2 リポジトリ連動タグを将来やめる選択肢（Sphinx 方式の `default_version = master` +
  REL-02 改訂）— リリースを 1〜2 回回してから再考
- RTD Default Version `latest` → `stable` の切替（Phase 33 のオーナー手動）
- RTD Default branch を `main` へ戻す（マイルストーンマージ後）
- PR プレビュービルド（RTD-05）、v0.6.4 以前のタグのドキュメント（RTD-06）
- ルートのブラウザ言語自動判定リダイレクト喪失（受容済みの回帰）
