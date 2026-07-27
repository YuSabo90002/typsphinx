# Phase 33: v0.6.4 Release Prep - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

<domain>
## Phase Boundary

v0.6.4 の prep-only リリース準備。**Requirements: REL-02（本フェーズで満たせる半分のみ）。**

**In scope:**

- `pyproject.toml:7` の `version = "0.6.3"` → `"0.6.4"`（実測上これが唯一の版リテラル。
  `typsphinx/__init__.py` は `importlib.metadata` 由来なので対象外）+ `uv.lock` 追随
- `README.md:317` の `**Status**: Stable (v0.6.3)` → `v0.6.4`
  （`tests/test_readme_version_sync.py` が両者一致を assert — 片方だけ変えるとスイートが赤）
- `CHANGELOG.md` の `## [0.6.4]` エントリ新設（構成は D-01〜D-04）+ 末尾リンクブロックの
  `[0.6.4]` 行追加 + `[Unreleased]` compare の `v0.6.4...HEAD` への繰り上げ（SC#2 明記、
  release-prep 自身の仕事）
- `pyproject.toml` `Documentation` メタデータの実 HTTP 確認（実測: 既に
  `https://typsphinx.readthedocs.io/` — Phase 31 で書き換え済み。本フェーズは再検証のみ）
- マイルストーン不変量の全差分断定（SC#4）: `git diff` を main..HEAD（実測 254 コミット、
  merge-base `771ec56`）に対して取り、新規ランタイム依存ゼロ / `@preview` 未バンプ /
  4 同期面の版文字列未変更 / `typsphinx/` 配下変更ゼロを証跡付きで記録
- **トップレベル planning 4 ファイルの完全英語化**（D-05、公開前提の整備）
- SC#5 のハンドオフチェックリスト作成（publish + オーナー手動ステップの明示的な引き渡し）

**Out of scope:**

- **publish 一切**（`git tag v0.6.4`、`release.yml` 起動、PyPI、GitHub Release、PR #124 の
  ready 化・マージ）→ `/gsd-complete-milestone`（SC#5 のスコープ柵は絶対）
- `typsphinx/` 配下の変更（マイルストーン不変量 #3）
- `.planning/phases/`・`.planning/milestones/` 配下の履歴アーカイブの英語化（D-05 対象外）
- Issue #119 のクローズ（Phase 31 D-15 で post-merge ハンドオフ済み、返信ドラフト
  `31-ISSUE-119-REPLY-DRAFT.md` 作成済み）
- CHANGELOG の過去バージョンエントリの改変（履歴）
- 版番号そのものの見直し（0.6.4 は ROADMAP SC#1 固定）

</domain>

<decisions>
## Implementation Decisions

### CHANGELOG `[0.6.4]` の構成と BREAKING 判定

- **D-01: BREAKING ラベルは立てない。** 従来の BREAKING（Phase 23 D-05 / 28 D-01〜02）は
  `conf.py` 設定・パッケージ挙動の破壊に立ててきた。本マイルストーンはパッケージを一行も
  触っておらず、壊れるのは旧 github.io URL（wheel 外）とリポジトリ内ツールのみ。旧 URL の
  消滅は Removed のホスティング撤去項目の本文に「旧 github.io URL はリダイレクトなしに 404」
  と目立つ但し書きで記す（オーナー受諾済みコスト、2026-07-25 決定）。

- **D-02: ja サイト告知に翻訳カバレッジの但し書きは付けない。**「日本語ドキュメントサイトを
  公開」とだけ書く。24.3% という数値も「部分的に翻訳済み」という定性文も入れない
  （オーナー選択 — 推奨の定性的但し書き案より簡潔を優先）。

- **D-03: `### Verified` 節は git diff で機械的に証明可能な不変量のみ。** 新規ランタイム
  依存ゼロ / `@preview` 未バンプ / `typsphinx/` 変更ゼロ。前例（Phase 23/28）のコーパス系
  3 点（fatal-free / `%PDF` / `unknown_visit`）は translator を触ったマイルストーン固有の
  ものであり、今回は対象の変更が存在しないので載せない。RTD 配信状態の実 HTTP 観測は
  時点依存のため CHANGELOG には載せない（検証機構を持てない事実は残さない原則）。

- **D-04: セクション割りは Added / Changed / Removed / Fixed / Verified の 5 節。死リンク
  修正は `### Fixed`。** オーナー承認済みの骨子:
  - **Added**: 日本語ドキュメントサイト `/ja/latest/`（RTD 翻訳プロジェクト、別リポジトリ
    `typsphinx-doc-translations` から構築）(I18N-01, I18N-03) / リポジトリ全域の advisory
    リンクチェック CI (CI-05)
  - **Changed**: ドキュメントホスティング GitHub Pages → Read the Docs、PDF は RTD の
    ダウンロードメニューから（typstpdf 自身の出力）(RTD-01..RTD-04)
  - **Removed**: 手製 multilang 機構一式 + orphan docs (I18N-02, DOC-08) / GitHub Pages
    サイト + `gh-pages` ブランチ — 旧 URL は 404（リダイレクトなし）、ブラウザ言語自動
    リダイレクトの廃止も明記 (CI-04)
  - **Fixed**: README/PyPI の死リンク 7 本を RTD URL への書き換えで解消
    (DOC-09, DOC-10, Issue #119)
  - **Verified**: D-03 のとおり不変量のみ
  - 粒度は D-09 前例（ユーザー可視の変化単位で束ね、要件 ID は末尾括弧）を踏襲。

### 公開前の planning ドキュメント英語化

- **D-05: トップレベル planning 4 ファイルを完全英語化する。** マージで `main` に載り
  GitHub 上で公開されるため。対象と実測の日本語含有行数: `.planning/PROJECT.md`（108 行）、
  `.planning/ROADMAP.md`（12 行 — Phase 22.4 / 27 / 27.1 の日本語フェーズ名・CONF-06 行等）、
  `.planning/MILESTONES.md`（11 行）、`.planning/STATE.md`（1 行）。
  `.planning/phases/`・`.planning/milestones/` 配下の履歴アーカイブは**対象外**。
  意味を変えない翻訳のみ（内容の書き換え・要約はしない）。STATE.md / ROADMAP.md への編集は
  内容不変の翻訳であることを明記してコミットする（構造・handler 管理フィールドを壊さない）。

### 前例から引き継ぐ既決事項（再導出しない）

- prep / publish 分離は絶対（`branching_strategy: milestone`、v0.5.0 Phase 10 /
  v0.6.2 Phase 23 / v0.6.3 Phase 28 前例）。
- `## [0.6.4]` の日付はプラン実行日（Phase 23 D-15）。`## [Unreleased]` 節は
  Keep a Changelog 標準どおり `[0.6.4]` の上に残す。
- リード段落は前例の体裁（マイルストーンの軸 + 不変量一行）。今回の軸は
  「ホスティングを GitHub Pages → Read the Docs に移行 + ランタイム変更ゼロ」。
- 検証機構を持てない数値（ページ数等）は CHANGELOG に載せない（Phase 22.4 / 23 D-11）。

### Claude's Discretion

以下はプラン/実行時に Claude 裁量で決めてよい:

- **SC#4 の証拠セットの範囲**（討議領域として提示、オーナー未選択）。最低限は SC#1 の
  版同期ガードテスト群の緑 + SC#4 の `git diff` 断定。フル pytest スイート /
  `tox -e docs-html` / `docs-pdf` の実走をどこまで証跡に足すかはプラン時判断。
  参考: 本マイルストーンは `typsphinx/` 変更ゼロなのでコーパスゲート実走の必然性は
  Phase 28 より弱い（Phase 28 D-05 の 3 点セットは translator 変更が根拠だった）。
- **SC#5 ハンドオフチェックリストの形式・置き場所**（討議領域として提示、オーナー未選択）。
  収載すべき既知項目は `<specifics>` 参照。
- 各 CHANGELOG 項目の具体的文面、`uv.lock` 再生成手順（受入は `uv sync --locked` 緑）、
  フェーズ内のプラン分割。
- 英語化（D-05）の訳文の文体・用語統一。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 変更対象ファイル

- `pyproject.toml` §`[project]` `:7` — `version = "0.6.3"`（唯一の版リテラル）;
  `:54-58` `[project.urls]` — `Documentation` は既に RTD URL（SC#3 は再検証のみ）
- `CHANGELOG.md` — `## [Unreleased]` の下に `## [0.6.4]` 新設。`## [0.6.3]` エントリが
  リード段落 + 節構成の直接の見本。末尾リンクブロック（`[0.6.3]: …/releases/tag/v0.6.3`
  以下 + `[Unreleased]: …/compare/v0.6.3...HEAD`）の更新も本フェーズの仕事
- `README.md:317` — `**Status**: Stable (v0.6.3) - Production ready`
- `uv.lock` — 版バンプに追随して再生成（`:1378-1379` に `typsphinx` / `version = "0.6.3"`）
- `.planning/PROJECT.md` / `.planning/ROADMAP.md` / `.planning/MILESTONES.md` /
  `.planning/STATE.md` — D-05 英語化の対象 4 ファイル

### ゲートと不変量

- `tests/test_readme_version_sync.py` — README Status 行と `pyproject.toml` version の
  一致を assert（版バンプで README を忘れると赤）
- `tests/test_preview_version_sync.py` — `@preview` 4 面同期（`writer.py` /
  `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`）の担保（SC#1/SC#4）
- `.planning/REQUIREMENTS.md` — REL-02 本文（2 リポジトリタグの standing cost 含む）、
  § Milestone Invariants #1〜#7、§ Owner-Manual Steps #4〜#5（ja 版アクティベーション
  再確認 + Default Version flip）、§ Traceability の REL-02 注記（半分しか満たせない構造）
- `.planning/ROADMAP.md` §Phase 33 — SC#1〜SC#5。**SC#5 のスコープ柵（tag / publish なし）
  は絶対**

### 前フェーズの決定・申し送り（ハンドオフ素材）

- `.planning/STATE.md` §Current Position / §Blockers — Phase 30.1 carry-forwards:
  **3 つの post-merge flip**（親 RTD Default branch → `main`、ja RTD Default branch →
  `main`、`.gitmodules` `branch` → `main`）、30.1 レビューの 3 Warnings、
  §Operator Next Steps の milestone-close owed 項目一覧
- `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ISSUE-119-REPLY-DRAFT.md`
  — Issue #119 クローズ用ドラフト（post-merge、Phase 31 D-15）
- `.planning/phases/32-github-pages-teardown-irreversible/32-CONTEXT.md` §議論外のハザード —
  gh-pages 復活ハザード（マージ前の main への push で peaceiris が再作成し得る）。
  `/gsd-complete-milestone` での `git ls-remote` 再確認を推奨としてチェックリストに載せる
- `.planning/milestones/v0.6.3-phases/28-v0-6-3-release-prep-regression-gate-close/28-CONTEXT.md`
  — 同型フェーズの直接の先例（D-04 ファイル最小主義 / D-15 日付 / 検証証跡の集約先）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`CHANGELOG.md` の `## [0.6.3]` エントリ** — リード段落 + 節構成 + 文体の見本。
- **`tests/test_readme_version_sync.py` / `test_preview_version_sync.py`** — SC#1 の判定
  本体。追加実装不要、実行と証跡採取のみ。
- **逐語のコマンド + 出力転記**（Phase 29 D-15 形式）— SC#3 の実 HTTP 確認と SC#4 の
  `git diff` 証跡の記録形式。

### Established Patterns

- **prep と publish の分離** — 最終フェーズは版バンプ + CHANGELOG まで。不可逆な publish は
  `/gsd-complete-milestone`。
- **触るファイルを最小に保つ**（Phase 28 D-04 — 4 ファイル主義）。本フェーズは D-05 の
  planning 4 ファイルが加わる分だけ広いが、`docs/` は触らない（触ると翻訳リポジトリの
  gettext 追従が付随する）。
- **honest-verifier 規約** — 直接証拠なしに真を断定せず、満たせない基準は満たせないと書く
  （SC#5 はその成文化）。

### Integration Points

- **`/gsd-complete-milestone`** — 本フェーズの `[0.6.4]` エントリが GitHub Release body の
  単一ソース。tag / PyPI / Release / PR #124 ready 化・マージ / Issue #119 クローズ /
  todo 整理（解決済み 2 件の pending/ からの移動）はすべて向こう側。
- **`release.yml`** — tag `v0.6.4` push で発火。本フェーズでは触れないし起動しない。
- **RTD（オーナー手動、post-tag）** — en Default Version `latest` → `stable`、ja 側の
  独立バージョンアクティベーション再確認、翻訳リポジトリへの同時タグ（REL-02 standing
  cost D-07: 以後すべてのリリースで 2 リポジトリにタグを打つ）。

</code_context>

<specifics>
## Specific Ideas

### 討議中に実測した事実（プランはこれを前提にしてよい）

| 主張 | 実測結果 | 影響 |
|---|---|---|
| 版リテラルの所在 | `pyproject.toml:7` のみ（`version = "0.6.3"`） | バンプ対象は 1 箇所 + README:317 + uv.lock |
| `Documentation` メタデータ | 既に `https://typsphinx.readthedocs.io/`（Phase 31 で書き換え済み） | SC#3 は実 HTTP 再検証のみ、編集不要 |
| CHANGELOG 末尾 | `[0.6.3]` 行まで存在、`[Unreleased]: …/compare/v0.6.3...HEAD` | `[0.6.4]` 行追加 + compare 繰り上げ |
| マイルストーン差分 | main..HEAD 254 コミット、merge-base `771ec56` | SC#4 の diff 範囲 |
| planning 日本語行数 | PROJECT.md 108 / ROADMAP.md 12 / MILESTONES.md 11 / STATE.md 1 | D-05 の作業量の実測 |

### SC#5 ハンドオフチェックリストに収載すべき既知項目（形式は Claude 裁量）

1. PR #124 ready 化 → マージ（`/gsd-complete-milestone`）
2. tag `v0.6.4` push → `release.yml` → PyPI + GitHub Release
3. **翻訳リポジトリ `typsphinx-doc-translations` にも submodule バンプ + タグ**（REL-02
   standing cost、D-07 — `/ja/stable/` はこちらのタグに解決）
4. 3 つの post-merge flip: 親 RTD Default branch → `main` / ja RTD Default branch →
   `main` / `.gitmodules` `branch` → `main`
5. tag ビルド緑の後: en Default Version `latest` → `stable` flip + ja プロジェクトの独立
   バージョンアクティベーション再確認（`/ja/stable/` が `/en/stable/` と同一タグを指すこと）
6. Issue #119 クローズ（`31-ISSUE-119-REPLY-DRAFT.md` 使用、オーナーレビュー後）
7. `git ls-remote` で `origin/gh-pages` 不在の再確認（Phase 32 の復活ハザード緩和、推奨）
8. 解決済み todo 2 件（github.io 404 / orphan クラス）の pending/ からの整理

</specifics>

<deferred>
## Deferred Ideas

- **30.1 レビューの 3 Warnings** — 討議領域として提示したがオーナー未選択。
  `docs/source/_typst/custom_template.typ` が `@preview` 同期ガード外の第 4 サイト /
  `contributing.rst` Translations 節のツールチェーン導入手順欠落 / 翻訳リポジトリ
  manifest のテスト未カバー。プランが拾うかは planner 判断（テスト変更のみで済む同期
  ガード拡張は不変量 #3 に抵触しないが、スコープ最小主義とのトレードオフ）。拾わない
  場合は STATE.md の carry-forward のまま残る。

### Reviewed Todos (not folded)

`todo.match-phase 33` の 7 件はいずれも折り込まない（オーナー選択 2026-07-28）:

- **`2026-07-22-github-io-doc-links-404-missing-en-prefix.md`**（score 0.9）— Phase 31 で
  解決済み（frontmatter `status: resolved`）。pending/ からの整理はマイルストーン close 側
  （ハンドオフ項目 8）。
- **`2026-07-25-docs-usage-installation-orphan-class.md`**（score 0.9）— Phase 30 で解決済み
  （`resolves_phase: 30`）。同上。
- **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`** /
  **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`** /
  **`2026-07-22-citation-node-support-untracked.md`** /
  **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`** — いずれもソース変更を
  要し、マイルストーン不変量 #3 で対象外（Phase 28 と同じ裁定）。
- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — Future LNK-01 として据え置き
  （オーナー決定 2026-07-25）。

</deferred>

---

*Phase: 33-v0.6.4 Release Prep*
*Context gathered: 2026-07-28*
