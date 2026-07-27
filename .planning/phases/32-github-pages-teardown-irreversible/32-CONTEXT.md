# Phase 32: GitHub Pages Teardown (IRREVERSIBLE) - Context

**Gathered:** 2026-07-27
**Status:** Ready for planning

<domain>
## Phase Boundary

typsphinx のドキュメントホスティングを Read the Docs 単独にする — GitHub Pages の公開経路
(`docs.yml` の `peaceiris/actions-gh-pages` デプロイステップ)と配信元(`origin/gh-pages`
ブランチ)を撤去し、`tox -e docs-pdf` の typstpdf 回帰ゲートとタグ時の
`Upload PDF to Release` ステップは無傷で残す。**Requirements: CI-04.**

これはマイルストーン唯一の undo 不能アクションであり、撤去は「RTD が今この瞬間 en HTML /
ja HTML / PDF を配信している」というフェーズ内で新規取得した証拠(SC#1)の後ろにのみ立つ。

**Explicitly NOT this phase:** リダイレクトスタブ追加(オーナー決定 2026-07-25 で恒久的に
無し)、`CHANGELOG.md:393` の github.io 履歴記述(据え置き、Phase 24 D-02 前例)、版バンプ +
CHANGELOG(Phase 33)、`typsphinx/` ランタイムコード変更(マイルストーン不変量 #3)。
docs.yml の multilang→html スワップ・PDF コピーステップ削除は Phase 30 で完了済み。

**実行前提(STATE.md):** Phase 30 の UAT 完了が本フェーズの計画/実行の前提。Phase 30 の
最後の UAT 項目(観測 CI 実行)は本 CONTEXT の D-08/D-09 が解消する — draft PR を
**Phase 32 の前に**開く。

</domain>

<decisions>
## Implementation Decisions

### 撤去前ゲートの証拠深度(SC#1)

- **D-01: ja HTML は内容照合まで踏む。** `/ja/latest/user_guide/builders.html`(65/65 全訳
  docname、Phase 30.1 実測)を curl し、既知の翻訳済み文字列の実在を grep で確認する。
  I18N-01 の故障モード「ビルドは緑なのに 100% 英語配信」(カタログ 24.3% 翻訳)は撤去後も
  存続するため、HTTP 200 + 言語マーカーでは不足。en HTML とルート URL の解決も同時に取る。
- **D-02: PDF は en+ja 両方を配信確認、忠実性の再検証はしない。** 両 PDF URL
  (en は `https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/`、ja は RTD ja
  プロジェクトのダウンロード URL)を curl し、HTTP 200 + PDF マジックバイト + 常識的
  サイズ/ページ数を確認。グリフ・内容一致は Phase 29(en)/ Phase 30.1(ja, D-03 ゲート)が
  検証済みで、`latest` は main 追従のため SHA 比較の基準も動く — ゲートが問うのは
  「今も配信されているか」のみ。
- **D-03: ゲートと撤去は別プランに分離する。** Plan 1 = ゲート(証拠取得・記録のみ、
  リポジトリ変更なし)、Plan 2 = 撤去(Plan 1 の緑を依存条件に)。ゲートが赤(RTD 配信停止を
  検出)なら Plan 2 に構造的に入らず、オーナーにエスカレーションする。
- **D-04: 証拠鮮度は「撤去と同日 + 直前再確認」。** ゲートプランの完全な証拠は同日内で
  有効。撤去プランの先頭で最小の再確認(4 URL の HTTP ステータスのみ)をもう一度取る。
  日をまたいだ場合はゲートプランの完全版を再実行する。
- 記録形式は既定の前例に従う: 逐語のコマンド + 出力転記(Phase 29 D-15 形式)。

### docs.yml の削減深度(SC#2/SC#3)

- **D-05: デプロイステップ + 未使用権限も削除する。** `peaceiris/actions-gh-pages` ステップ
  に加え、`permissions:` から `pages: write` と `id-token: write` を落とす(実測: peaceiris
  方式は `contents: write` でブランチ push するため両権限は現状でも未使用 — 公式
  `actions/deploy-pages` 方式用)。**`contents: write` はタグ時 Release 添付(softprops)に
  必要なので残置。** SC#3 の byte-unchanged 制約は `Upload PDF to Release` ステップにのみ
  かかる。
- **D-06: 再発防止ガードテストを追加する。** docs.yml に gh-pages デプロイ(peaceiris /
  pages 権限)が不在であること + `Upload PDF to Release` ステップが存在することを断定する
  小テスト。`tests/test_readthedocs_config.py` の既存パターン
  (`test_build_python_matches_docs_workflow` が docs.yml を読んで形状断定)を踏襲。
- **D-07: HTML/PDF アーティファクト upload ステップは残置。** ROADMAP の「撤去対象は公開
  経路のみ」の対象外。`.planning/codebase/INTEGRATIONS.md` の差分更新(docs.yml 削減の
  反映)は Phase 31 D-18 の既決により本フェーズが持つ。

### SC#3 観測 CI 実行の手段

- **D-08: マイルストーン draft PR を main に向けて開き、その pull_request トリガーで
  docs.yml の観測実行を得る。** リポジトリ変更ゼロで Phase 30 UAT test 1(同一構造で
  blocked)と Phase 32 SC#3 の両方を解決する。workflow_dispatch 追加も backstop 繰り延べも
  採らない。正式な ready 化とマージは従来どおり `/gsd-complete-milestone` で。
- **D-09: draft PR は Phase 32 の前に開く。** 順序の循環(Phase 30 完了が Phase 32 の前提 ↔
  Phase 30 の最終 UAT 項目が PR 待ち)を解消するため、次のアクションとして先に draft PR を
  開き、`/gsd-verify-work 30` で Phase 30 UAT を完結させてから Phase 32 を計画/実行する。
  Phase 32 実行中は既存の開いた PR にコミットを積むだけで SC#3 の観測(撤去コミットを head
  とする緑の run の逐語転記)が取れる。

### オーナー手動ステップ(自動化不可、REQUIREMENTS.md 手動手順 #7)

- リポジトリ Settings → Pages で GitHub Pages サイトを無効化する。ブランチ削除だけでは
  Pages 機能がソース欠損のまま有効に残り得る。観測可能な結果は SC#2 の github.io 404。

### 議論外のハザード(planner/オーナー判断 — 対処は未決)

- **gh-pages 復活ハザード:** `main` 側の docs.yml はマイルストーンマージまで旧デプロイ
  ステップを保持する。マージ前に main へ push が起きる(実測: dependabot PR #123 がオープン
  中)と、main 上の docs.yml が発火し peaceiris が `gh-pages` を再作成 — SC#2 の
  `git ls-remote` 証明が事後に覆る。オーナーはこの領域の議論をスキップ。対処
  (マージまで main への push を控える / マージ後・マイルストーン close 時の ls-remote
  再検証 / その他)は planner の提案とオーナー判断に委ねる。少なくとも
  `/gsd-complete-milestone` での ls-remote 再確認を推奨として記録する。

### Claude's Discretion

- ゲートで grep する具体的な翻訳済み文字列の選定(D-01)と PDF の「常識的サイズ/ページ数」
  のしきい値(D-02)。
- ガードテストの関数名・断定の厳密さ(D-06)。
- draft PR のタイトル・本文(英語・簡潔 — 外向き成果物の既定に従う)。
- 404 確認のリトライ姿勢(Pages 無効化直後の CDN キャッシュ猶予)。
- INTEGRATIONS.md 差分更新の記述粒度(D-07)。

### Folded Todos

- **`.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md`** —
  `resolves_phase: 32`。RTD 移行マイルストーンの起点 todo。Phase 31 CONTEXT が「Pages 撤去
  (Phase 32)までオープン」と明記済み。**本フェーズの撤去コミットが landed した時点で
  クローズする。**

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### マイルストーンのスコープと制約
- `.planning/ROADMAP.md` § "Phase 32" — ゴール、3 成功基準、オーナー手動依存
  (Settings → Pages 無効化)、Notes(docs.yml の multilang 系は Phase 30 で完了済み、
  本フェーズは公開経路のみ)。
- `.planning/REQUIREMENTS.md` — CI-04 本文、§ 手動手順 #7(Pages 無効化)、
  § Milestone Invariants(#3 ランタイム変更なし、#4 fresh grep)。
- `.planning/STATE.md` § "Current Position" — Phase 30 完了ゲート(D-09 が解消手順)、
  `ui.plan-gate` / `api-coverage` の docs フェーズ偽陽性ノート(`--skip-ui` + 記録付き
  オーバーライドの前例)。

### 先行フェーズの決定(再導出しない)
- `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-CONTEXT.md`
  — D-14(publish_dir repoint は暫定、ステップ削除は本フェーズ)。
- `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-CONTEXT.md` — D-18
  (INTEGRATIONS.md の Phase 32 差分は本フェーズ持ち)、D-03(links.yml は CHANGELOG.md を
  除外済み — 撤去後の github.io 404 で link check が赤くならない)。
- `.planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md`
  — Branch A 確定(レジストリ到達可・RTD が PDF 配信)、en PDF URL
  `https://typsphinx.readthedocs.io/_/downloads/en/latest/pdf/`、逐語転記の証拠形式(D-15)。
- `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-UAT.md` —
  test 1 の blocked 記録(D-08/D-09 が解消する対象)。

### 本フェーズが触る/測るファイル
- `.github/workflows/docs.yml` — peaceiris ステップ削除 + `pages: write` /
  `id-token: write` 削除(D-05)。`Upload PDF to Release` は byte-unchanged(SC#3)。
- `tests/test_readthedocs_config.py` — ガードテスト追加先(D-06、既存の docs.yml 形状断定
  パターンあり)。
- `.planning/codebase/INTEGRATIONS.md` — docs.yml 削減の差分更新(D-07)。
- `origin/gh-pages`(削除対象、実測 2026-07-27: `f97862d` で現存)。
- `.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md` —
  撤去 landed 時にクローズ(Folded Todos 参照)。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`tests/test_readthedocs_config.py`** — docs.yml を YAML として読み形状を断定する既存
  テストパターン(D-06 のガードテストの雛形)。
- **RTD 公開 URL/API は認証不要で curl 実測可能**(Phases 29/30.1/31 で確立)— ゲートの
  検証手段はすべて手元にある。
- **逐語のコマンド + 出力転記**(Phase 29 D-15 形式)— ゲート証拠と SC#3 の CI run 転記の
  記録形式。

### Established Patterns
- **fresh grep / fresh fetch at execution time**(マイルストーン不変量 #4)— ゲート証拠は
  必ずフェーズ内で新規取得。先行フェーズの証拠の引用は SC#1 が明示的に禁じる。
- **外向き成果物は英語・簡潔**(PR#98 の教訓)— draft PR のタイトル・本文に適用。
- **honest-verifier 規約**(GATE-01)— 直接証拠なしに真を断定せず `human_needed` へ。

### Integration Points
- **GitHub リポジトリ設定(オーナー手動):** Settings → Pages の無効化。リポジトリ内から
  断定不能で、観測可能な結果(github.io 404)のみ検証可能。
- **`docs.yml` のトリガー構造:** push to `main` / `v*` タグ / PR to `main` のみ
  (workflow_dispatch 無し)— SC#3 の観測は D-08 の draft PR 経由。
- **`/gsd-complete-milestone` への追記:** マイルストーン close 時の `git ls-remote`
  再確認(gh-pages 復活ハザードの推奨緩和)、draft PR の ready 化とマージ。

</code_context>

<specifics>
## Specific Ideas

実測 2026-07-27(実行時に再測定):

- `origin/gh-pages` は現存(`f97862dfea151dd904591a18d2ddbd0bf72fd851`)。
- マイルストーン PR は未オープン。オープン中の PR は dependabot #123(ruff 版レンジ)のみ
  — マージ前に main へ入ると gh-pages 復活ハザードの実例になる。
- 現行 docs.yml(Phase 30 適用後): `docs-html` / `docs-pdf` ビルド + アーティファクト
  upload + peaceiris デプロイ(`publish_dir: ./docs/_build/html`、main push 時のみ発火) +
  タグ時 Release 添付。
- ja の全訳済み docname(ゲート照合対象): `user_guide/builders`(65/65)、
  `examples/basic`(30/30)。`api/index` / `contributing` / `changelog` /
  `user_guide/templates` は 0% — 照合対象にしてはならない。

</specifics>

<deferred>
## Deferred Ideas

- **gh-pages 復活ハザードの恒久対処**(議論スキップ、planner/オーナー判断)— 上記
  `<decisions>` § 議論外のハザード参照。

### Reviewed Todos (not folded)

- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — Future LNK-01 として据え置き
  (オーナー決定 2026-07-25)。本フェーズと無関係。
- **`2026-07-22-citation-node-support-untracked.md`** /
  **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`** /
  **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`** /
  **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`** — いずれも
  `typsphinx/` ランタイム変更を要し、マイルストーン不変量 #3 で本フェーズ対象外。

</deferred>

---

*Phase: 32-GitHub Pages Teardown (IRREVERSIBLE)*
*Context gathered: 2026-07-27*
