# Phase 33: v0.6.4 Release Prep - Research

**Researched:** 2026-07-28
**Domain:** リリースエンジニアリング / CHANGELOG キュレーション / planning ドキュメント英語化（ソース振る舞い変更なし）
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**CHANGELOG `[0.6.4]` の構成と BREAKING 判定**

- **D-01: BREAKING ラベルは立てない。** 従来の BREAKING（Phase 23 D-05 / 28 D-01〜02）は `conf.py` 設定・パッケージ挙動の破壊に立ててきた。本マイルストーンはパッケージを一行も触っておらず、壊れるのは旧 github.io URL（wheel 外）とリポジトリ内ツールのみ。旧 URL の消滅は Removed のホスティング撤去項目の本文に「旧 github.io URL はリダイレクトなしに 404」と目立つ但し書きで記す（オーナー受諾済みコスト、2026-07-25 決定）。
- **D-02: ja サイト告知に翻訳カバレッジの但し書きは付けない。**「日本語ドキュメントサイトを公開」とだけ書く。24.3% という数値も「部分的に翻訳済み」という定性文も入れない（オーナー選択 — 推奨の定性的但し書き案より簡潔を優先）。
- **D-03: `### Verified` 節は git diff で機械的に証明可能な不変量のみ。** 新規ランタイム依存ゼロ / `@preview` 未バンプ / `typsphinx/` 変更ゼロ。前例（Phase 23/28）のコーパス系 3 点（fatal-free / `%PDF` / `unknown_visit`）は translator を触ったマイルストーン固有のものであり、今回は対象の変更が存在しないので載せない。RTD 配信状態の実 HTTP 観測は時点依存のため CHANGELOG には載せない（検証機構を持てない事実は残さない原則）。
- **D-04: セクション割りは Added / Changed / Removed / Fixed / Verified の 5 節。死リンク修正は `### Fixed`。** オーナー承認済みの骨子:
  - **Added**: 日本語ドキュメントサイト `/ja/latest/`（RTD 翻訳プロジェクト、別リポジトリ `typsphinx-doc-translations` から構築）(I18N-01, I18N-03) / リポジトリ全域の advisory リンクチェック CI (CI-05)
  - **Changed**: ドキュメントホスティング GitHub Pages → Read the Docs、PDF は RTD のダウンロードメニューから（typstpdf 自身の出力）(RTD-01..RTD-04)
  - **Removed**: 手製 multilang 機構一式 + orphan docs (I18N-02, DOC-08) / GitHub Pages サイト + `gh-pages` ブランチ — 旧 URL は 404（リダイレクトなし）、ブラウザ言語自動リダイレクトの廃止も明記 (CI-04)
  - **Fixed**: README/PyPI の死リンク 7 本を RTD URL への書き換えで解消 (DOC-09, DOC-10, Issue #119)
  - **Verified**: D-03 のとおり不変量のみ
  - 粒度は D-09 前例（ユーザー可視の変化単位で束ね、要件 ID は末尾括弧）を踏襲。

**公開前の planning ドキュメント英語化**

- **D-05: トップレベル planning 4 ファイルを完全英語化する。** マージで `main` に載り GitHub 上で公開されるため。対象と実測の日本語含有行数: `.planning/PROJECT.md`（108 行）、`.planning/ROADMAP.md`（12 行 — Phase 22.4 / 27 / 27.1 の日本語フェーズ名・CONF-06 行等）、`.planning/MILESTONES.md`（11 行）、`.planning/STATE.md`（1 行）。`.planning/phases/`・`.planning/milestones/` 配下の履歴アーカイブは**対象外**。意味を変えない翻訳のみ（内容の書き換え・要約はしない）。STATE.md / ROADMAP.md への編集は内容不変の翻訳であることを明記してコミットする（構造・handler 管理フィールドを壊さない）。
  - **本セッションで再実測した結果、CONTEXT.md の行数の一部は現時点で乖離している**（詳細は下記「Specific Facts / D-05 の実測再確認」節）。プランは CONTEXT.md の数字ではなく、実行時に自分で取った grep の実測値を根拠にすること（milestone invariant #4「discovery-time grep」の精神をそのまま適用）。

**前例から引き継ぐ既決事項（再導出しない）**

- prep / publish 分離は絶対（`branching_strategy: milestone`、v0.5.0 Phase 10 / v0.6.2 Phase 23 / v0.6.3 Phase 28 前例）。
- `## [0.6.4]` の日付はプラン実行日（Phase 23 D-15）。`## [Unreleased]` 節は Keep a Changelog 標準どおり `[0.6.4]` の上に残す。
- リード段落は前例の体裁（マイルストーンの軸 + 不変量一行）。今回の軸は「ホスティングを GitHub Pages → Read the Docs に移行 + ランタイム変更ゼロ」。
- 検証機構を持てない数値（ページ数等）は CHANGELOG に載せない（Phase 22.4 / 23 D-11）。

### Claude's Discretion

- **SC#4 の証拠セットの範囲**（討議領域として提示、オーナー未選択）。最低限は SC#1 の版同期ガードテスト群の緑 + SC#4 の `git diff` 断定。フル pytest スイート / `tox -e docs-html` / `docs-pdf` の実走をどこまで証跡に足すかはプラン時判断。参考: 本マイルストーンは `typsphinx/` 変更ゼロなのでコーパスゲート実走の必然性は Phase 28 より弱い（Phase 28 D-05 の 3 点セットは translator 変更が根拠だった）。
- **SC#5 ハンドオフチェックリストの形式・置き場所**（討議領域として提示、オーナー未選択）。収載すべき既知項目は下記「Specific Facts」参照。
- 各 CHANGELOG 項目の具体的文面、`uv.lock` 再生成手順（受入は `uv sync --locked` 緑）、フェーズ内のプラン分割。
- 英語化（D-05）の訳文の文体・用語統一。

### Deferred Ideas (OUT OF SCOPE)

- **30.1 レビューの 3 Warnings** — 討議領域として提示したがオーナー未選択。`docs/source/_typst/custom_template.typ` が `@preview` 同期ガード外の第 4 サイト / `contributing.rst` Translations 節のツールチェーン導入手順欠落 / 翻訳リポジトリ manifest のテスト未カバー。プランが拾うかは planner 判断（テスト変更のみで済む同期ガード拡張は不変量 #3 に抵触しないが、スコープ最小主義とのトレードオフ）。拾わない場合は STATE.md の carry-forward のまま残る。
- Todo 7 件はいずれも折り込まない（オーナー選択 2026-07-28、詳細は元 CONTEXT.md 参照）。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-02 | `typsphinx 0.6.4` published to PyPI, `Documentation` metadata resolves, `/en/stable/` + `/ja/stable/` both serve the released version | 本フェーズが満たせるのは版バンプ・CHANGELOG・`Documentation` URL 再検証（SC#1〜3）のみ。PyPI 公開と `/en|ja/stable/` の実配信は publish 後の owner-manual 手順であり、SC#5 で明示的ハンドオフとして記録する（下記「REL-02 の半分性」節）。CHANGELOG の `## [0.6.4]` エントリは D-04 の骨子どおり REL-02 以外の 12 件（RTD-01..04, I18N-01..03, DOC-08..10, CI-04/CI-05）を集約したユーザー可視サマリになる。 |

**注記:** ROADMAP/STATE 上、Phase 33 自身は「none（release/close phase）」に近いが、REL-02 が唯一の直接紐付け要件。CHANGELOG `[0.6.4]` エントリは de-facto でマイルストーン全 13 要件（REL-02 除く）のカバレッジ対象になる（Phase 28 D-09/D-10 と同型の位置づけ）。
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Worktree 分離実行がこのプロジェクトの標準実行モード**（`workflow.use_worktrees: true`、`.claude/settings.local.json` の `worktree.baseRef: "head"`）。ただし本研究セッションはメインツリー（`.git` がディレクトリ）で実行しており、すべての実測コマンドはメインツリー上で直接動作確認済み。executor がワークツリーで実行する場合は必ず `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` を最初に実行し、以後すべて `uv run` 経由で実行すること（低並列フェーズでも逐次実行に落とさない、CLAUDE.md 明記）。
- **CI と一致させる**: `black --check .`、`ruff check .`、`mypy typsphinx/`。本フェーズは `typsphinx/` を一行も触らないので `mypy` は実質 no-op。`black`/`ruff` も対象ファイルなし（変更対象はすべて markdown/TOML/lock）。
- **`tox.ini` の `tox-uv~=1.35` ピンは意図的** — このフェーズで触らない。
- **`UP006`/`UP035` の ruff ignore は維持** — pending todo が着地するまで typing import を modernize しない。本フェーズは Python コードを触らないため無関係。
- Line length 88（black 管理）、`E501` は ruff で ignore — 本フェーズが触るファイルに Python はない。
- 本フェーズが触るファイルは `pyproject.toml` / `uv.lock` / `CHANGELOG.md` / `README.md` の 4 つ + D-05 の planning 4 ファイル（`PROJECT.md`/`ROADMAP.md`/`MILESTONES.md`/`STATE.md`）の計 8 つ。`typsphinx/`・`docs/`・`examples/`・`.planning/phases/`・`.planning/milestones/` はすべて対象外。

## Summary

Phase 33 は**ソース振る舞い変更ゼロ**のリリース準備フェーズで、Phase 28（v0.6.3 release prep）とほぼ同型だが 2 点で拡張がある: (1) CHANGELOG が今回はホスティング移行という非コード変更のマイルストームを要約する、(2) **D-05 として新設された「トップレベル planning 4 ファイルの英語化」** が今回固有の作業として加わる。必要な事実はすべてリポジトリ内（git 履歴、既存テスト、`.planning/PROJECT.md` の Key Decisions 英語プロース、直前フェーズの CONTEXT/VERIFICATION）にあり、外部ライブラリや Web ドキュメントへの依存はない。

**このセッションで実機測定した最重要事実:**

1. **`git diff main..HEAD -- typsphinx/`（milestone 全体）は完全に空** — milestone invariant #3（`typsphinx/` 変更ゼロ）は既に自明に成立している。`pyproject.toml` の diff は `Documentation` メタデータの 1 行変更のみ（Phase 31 で実施済み）、`dependencies` 配列・`@preview` 版文字列はいずれも未変更。`uv.lock` の diff は本セッション時点で空。
2. **`main..HEAD` のコミット数は 256（CONTEXT.md 記載の 254 から +2）** — 2026-07-28 の CONTEXT 討議後に Phase 32 完了記録の 2 コミット（`d9923e5`, `32c11b3`）が積まれたため。merge-base は変わらず `771ec56`。**プランは実行時に自分で `git log --oneline main..HEAD | wc -l` を再測ること**（discovery-time 原則）。
3. **D-05 の行数は CONTEXT.md の実測値と 2 ファイルで乖離している**（詳細下記）— `MILESTONES.md` は CONTEXT.md の「11 行」に対し**実測 1 行のみ**（唯一の該当行はマイルストーン見出し `## v0.6.3 config & docs 実測整合 + captioned tables`）。`ROADMAP.md` も「12 行」に対し**実測 10 行**。`PROJECT.md`（108 行）と `STATE.md`（1 行）は CONTEXT.md の数値と完全一致。D-05 の作業量は MILESTONES.md について想定よりはるかに小さい（1 行の見出し翻訳のみ）。
4. **`typsphinx.__version__` の版更新には `pyproject.toml` 編集だけでは不十分** — editable install のメタデータ（`typsphinx.egg-info/`、`.venv/lib/.../__editable__.typsphinx-0.6.3.pth`、`typsphinx-0.6.3.dist-info/`）が版番号をファイル名/内容に埋め込んでおり、`uv sync`（または `pip install -e .` の再実行）で再生成しない限り `importlib.metadata` は古い版を返し続ける。Phase 28（v0.6.3）でも「editable-dist install metadata refreshed」という同じ手順が明記されていた（MILESTONES.md 実測）。SC#1 の `typsphinx.__version__` が `0.6.4` を報告する、という基準は**この再同期ステップをタスクとして明示しないと満たせない**。
5. **`pyproject.toml`'s `Documentation` URL は既に実 HTTP 到達可能** — `https://typsphinx.readthedocs.io/` は `302` で `https://typsphinx.readthedocs.io/en/latest/`（`200`）にリダイレクトする（本セッションで `curl` 実測）。SC#3 は編集不要、この結果をそのまま証跡として記録するだけでよい。
6. **フル pytest スイートは現時点で 647 passed / 1 skipped**（本セッション実測、`uv run python -m pytest -q -rs`、55.76s）。version-sync ガード 2 テスト（`test_readme_version_sync.py` / `test_preview_version_sync.py`、計 4 assert）は個別実行でも green。STATE.md に記録された過去のフルスイート数（656, 661）はこのマイルストーン中の削除/追加を経て変動しており、647 が Phase 33 着手時点の正しいベースライン。

**Primary recommendation:** 実行順序は Phase 28 の型紙を踏襲 — 版バンプ（`pyproject.toml` → `uv sync` によるロック/メタデータ再生成）→ CHANGELOG → D-05 英語化 → SC#4 不変量の `git diff` 断定 + 証跡記録 → SC#5 ハンドオフチェックリスト作成。CHANGELOG 本文は下記「Code Examples」のドラフトをほぼそのまま使える。

## Architectural Responsibility Map

本フェーズはアプリケーション層のコードを一切触らないため、ブラウザ/API/DB 等の標準ティアは適用外。リリース準備フェーズ向けに読み替える:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 版リテラルのバンプ | ビルド/パッケージメタデータ（`pyproject.toml`） | ロックファイル + editable install メタデータ（`uv.lock`、`typsphinx.egg-info/`） | `pyproject.toml:7` が唯一の版リテラル。`uv.lock` の自己エントリと `.venv` の editable install メタデータも追随させないと `typsphinx.__version__` が古いまま（Pitfall 参照） |
| CHANGELOG キュレーション | ドキュメント（リポジトリ直下） | — | 純粋なプローズ。どのコードパスも `CHANGELOG.md` を読まない |
| README Status 同期 | ドキュメント（リポジトリ直下） | テスト/CI（`tests/test_readme_version_sync.py`、既存） | 既存の同期ガードを再利用するのみ |
| **planning ドキュメント英語化（D-05）** | ドキュメント（`.planning/` 直下 4 ファイル） | — | 意味不変の翻訳のみ。構造フィールド（YAML frontmatter、進捗テーブル、handler 管理欄）は非対象 |
| マイルストーン不変量の確認 | テスト/CI（`tests/test_preview_version_sync.py`）+ `git diff` | ビルド/パッケージメタデータ | `@preview` 4-surface 同期面・`typsphinx/` 変更ゼロが `main` から未変更であることを確認 |
| SC#3 `Documentation` メタデータの実 HTTP 再検証 | ビルド/パッケージメタデータ（`pyproject.toml`） | 外部サービス（Read the Docs） | 編集不要、`curl` での再検証のみ |
| SC#5 ハンドオフチェックリスト | ドキュメント（本フェーズの成果物、置き場所は Claude 裁量） | — | publish + owner-manual ステップの明示的な引き渡し。実行はしない |

## Package Legitimacy Audit

**該当なし — 本フェーズは外部パッケージを一切インストールしない。** `git diff main..HEAD -- pyproject.toml` は `Documentation` メタデータ 1 行のみで `dependencies`/`optional-dependencies` は完全に未変更（本セッションで実測確認済み）。`uv.lock` の再生成は `typsphinx` 自身の版リテラル更新のみで依存変更ではない。Package Legitimacy Gate はそのトリガー条件（外部パッケージをインストールするフェーズ）に該当しないためスキップする。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| README/pyproject の版ドリフト防止 | 新しい ad-hoc 文字列チェック | `tests/test_readme_version_sync.py`（既存） | 既に存在する自己比較アサーション。両ファイルの版を揃えるだけで自動的に検証対象になる |
| `@preview` 4 面同期の確認 | 新しい CI チェック | `tests/test_preview_version_sync.py`（3 サイト同期 + `examples/**/*.typ` の 4 面目、既存） | SC#1 が明示的に「now-four-surface」と呼ぶこのテストが既にすべてを担保する。追加実装ゼロ |
| SC#4 不変量の確認 | 新しい CI ジョブ | `git diff main..HEAD` の該当パスへの絞り込み + 既存テストの緑 | Claude's Discretion がこれで十分としている |
| D-05 の日本語含有行の発見 | 目視スキャンや CONTEXT.md の数字への盲信 | `grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' <file>` を対象 4 ファイルそれぞれに実行 | 本セッションで CONTEXT.md の数字が 2 ファイルで乖離していたことを実測済み（Summary #3）。milestone invariant #4 の discovery-time grep 原則そのもの |
| バージョンメタデータの再同期 | 手動で `.venv` 内の egg-info/dist-info を編集 | `uv sync`（または `uv sync --extra dev --locked` 前に `uv lock`） | `pyproject.toml` バンプ後の editable install メタデータ再生成は uv の標準手順、手動ファイル編集は壊れやすく非再現的 |

**Key insight:** 本フェーズの「Don't Hand-Roll」は Phase 28 と同じ一貫したパターン — 「新しい仕組みを作るな、既にこの形の precedent がプロジェクトにある」。唯一の新規要素（D-05 の英語化）も、既存の `git diff`/`grep` ベースの検証習慣をそのまま転用できる。

## Specific Facts / D-05 の実測再確認

**実行したコマンド（再現可能）:**

```bash
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/PROJECT.md    # → 108 行（CONTEXT.md と一致）
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/ROADMAP.md    # → 10 行（CONTEXT.md「12 行」と乖離）
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/MILESTONES.md # → 1 行（CONTEXT.md「11 行」と大きく乖離）
grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' .planning/STATE.md      # → 1 行（CONTEXT.md と一致）
```

（CJK 記号・句読点・全角形まで含めた広域レンジ `[\x{3000}-\x{303f}\x{3040}-\x{30ff}\x{4e00}-\x{9fff}\x{ff00}-\x{ffef}]` でも同じ件数 — 範囲の広さが原因の乖離ではない。）

- **`.planning/MILESTONES.md`（174 行）:** 該当は 3 行目 `## v0.6.3 config & docs 実測整合 + captioned tables (Shipped: 2026-07-25)` の見出し**1 行のみ**。CONTEXT.md の「11 行」は誤り、または討議時と異なる断面（ファイルが後で編集された形跡はなし — おそらく討議時の grep がノイズを含んでいた）。D-05 の MILESTONES.md 対応は**この 1 行の見出し翻訳のみ**で完了する、想定よりはるかに軽い作業。
- **`.planning/ROADMAP.md`（887 行）:** 該当 10 行 — `:10`（v0.6.3 サマリ行）、`:141`（Phase 22.4 の名前）、`:147`（summary タグ内の見出し）、`:155`/`:158`（v0.6.3 詳細プローズ内の日本語混在文）、`:168`/`:169`（Phase 27/27.1 の名前）、`:841`/`:846`/`:847`（Progress テーブルの Phase 名列）。過去マイルストーンのフェーズ名・要約プローズが対象で、`ROADMAP.md` 自体は英語主体のファイルにこの 10 行だけ日本語が混在している。
- **`.planning/PROJECT.md`（379 行）:** 108 行は 3 つのまとまりに大別される — (a) `:19-101` あたり: v0.6.4 マイルストーンの Goal/scoping 記述（ほぼ全文日本語、最も分量が多い）、(b) `:107-134` あたり: v0.6.3 セクションの見出し・箇条書き（日本語プローズ + 英語技術語の混在）、(c) `:223-224`, `:341-360`: Key Decisions の一部箇条書きと `<!-- Prior: ... -->` 形式の履歴フッターコメント（HTML コメントも git 上は生テキストなので grep に掛かる — D-05 のスコープに含まれる）。
- **`.planning/STATE.md`（322 行）:** 該当 1 行のみ、`:292`（`CONF-06` の説明に日本語の但し書きが混在）。

**プランへの示唆:** D-05 のタスク粒度は「ファイル単位で 1 タスク」よりも「実測した行範囲ごとに読み替え」の方が正確な見積りになる。特に MILESTONES.md は 1 行しかないため、独立タスクにすると過剰、PROJECT.md 側の作業とまとめても支障はない。

## Architecture Patterns

### CHANGELOG Structural Template（実測: `CHANGELOG.md` 全文読了）

- `## [Unreleased]` が 8 行目、空行を挟んで `## [0.6.3] - 2026-07-25` が続く。**`## [0.6.4]` はこの間に挿入する。**
- `[0.6.3]` の節構成: リード段落（8 行）→ `### Added`（1 件、TBL-01/02 束ね）→ `### Changed`（BREAKING 1 件、CONF-04）→ `### Removed`（BREAKING 1 件、CONF-05）→ `### Fixed`（2 件）。これが Phase 33 が Keep a Changelog 語彙順（Added, Changed, Removed, Fixed, Verified）に最も忠実な直近の precedent。**D-04 のセクション割り（Added/Changed/Removed/Fixed/Verified の 5 節）はこの並びと完全に一致するので追加調整不要。**
- **BREAKING の書式**: バレット先頭ボールド型（`- **BREAKING: ...**`）。**D-01 により本フェーズは BREAKING ラベルを一切立てない** — 該当形式を使う箇所はない。
- **要件 ID の引用スタイル**: 各バレットの太字見出し直後、閉じ括弧の直前に要件 ID（例 `(RTD-01..RTD-04)`）。
- **リンクブロック（ファイル末尾、実測）:**
  ```
  [0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3
  [0.6.2]: ...
  ...
  [Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.3...HEAD
  ```
  **Before → After（本フェーズが作る差分）:**
  - 追加: `[0.6.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4` を `[0.6.3]:` 行の直前に挿入。
  - 変更: `[Unreleased]: .../compare/v0.6.3...HEAD` → `.../compare/v0.6.4...HEAD`。
  - `v0.6.4` タグはこのフェーズでは存在しないため、このリンクは `/gsd-complete-milestone` がタグを打つまで 404 になる — v0.6.1〜v0.6.3 いずれの release-prep でも同じ状態を経ており、project convention として許容されている。

### Recommended Project Structure（本フェーズが触るファイルのみ）

```
pyproject.toml           # version = "0.6.3" -> "0.6.4"（唯一の版リテラル）、Documentation は既に RTD URL（無編集）
uv.lock                  # typsphinx self-entry version 追随（`uv lock` または `uv sync`）
README.md                # :317 Status 行の (v0.6.3) -> (v0.6.4)
CHANGELOG.md             # ## [0.6.4] 新設 + 末尾リンクブロック更新
.planning/PROJECT.md     # D-05: 日本語 108 行を意味不変で英訳
.planning/ROADMAP.md     # D-05: 日本語 10 行を意味不変で英訳
.planning/MILESTONES.md  # D-05: 日本語 1 行（見出し）を意味不変で英訳
.planning/STATE.md       # D-05: 日本語 1 行を意味不変で英訳
```

### Pattern 1: 版バンプ後の editable install メタデータ再同期

**What:** `pyproject.toml` の `version` を書き換えるだけでは `typsphinx.__version__`（`importlib.metadata` 経由）は更新されない。
**When to use:** SC#1 の `typsphinx.__version__` reports `0.6.4` を満たす直前。
**Example:**
```bash
# Source: このセッションで実測（uv 0.11.25 相当）
# pyproject.toml の version を編集した直後に実行
uv lock                              # uv.lock の typsphinx self-entry を "0.6.4" に更新
uv sync --extra dev --locked         # editable install メタデータ (.egg-info/.dist-info/.pth) を再生成
uv run python -c "import typsphinx; print(typsphinx.__version__)"  # -> 0.6.4 になっていることを確認
```

### Anti-Patterns to Avoid

- **CONTEXT.md の実測値を再検証なしに証跡として使う:** D-05 の行数のように、討議時点から実行時点の間に他コミットが積まれて数字がずれることがある（本フェーズ自身、コミット数が 254→256 にずれた実例あり）。証跡には必ず実行時点の生コマンド出力を貼る。

## Common Pitfalls

### Pitfall 1: `pyproject.toml` の版バンプだけで `typsphinx.__version__` が更新されると思い込む

**何が起きるか:** `version = "0.6.4"` に編集した直後に `typsphinx.__version__` を確認すると `0.6.3` のまま残っている。
**なぜ起きるか:** editable install（`uv sync` / `pip install -e .`）が生成した `typsphinx.egg-info/`・`.venv/lib/.../__editable__.typsphinx-0.6.3.pth`・`typsphinx-0.6.3.dist-info/` に版番号がファイル名・内容として埋め込まれており、`importlib.metadata` はこれらの静的メタデータを読む。`pyproject.toml` の変更だけでは自動的に再生成されない。
**どう防ぐか:** `pyproject.toml` 編集の直後に `uv lock && uv sync --extra dev --locked` を実行し、その後で `typsphinx.__version__` を確認する（Phase 28 の precedent — MILESTONES.md に「editable-dist install metadata refreshed」と明記されている、同じ手順が必要）。
**警告サイン:** `import typsphinx; print(typsphinx.__version__)` が古い版を返す。

### Pitfall 2: D-05 の行数を CONTEXT.md の数字のまま信じてタスクを見積もる

**何が起きるか:** MILESTONES.md を「11 行の翻訳作業」として見積もり、実測が 1 行しかないのに過剰なタスク配分をする（逆に ROADMAP.md も 12 行想定で 10 行しか無い軽微なズレがある）。
**なぜ起きるか:** CONTEXT.md の実測は討議セッション時点のものであり、本セッションで再実行した結果 2 ファイルで乖離が確認された（原因不明 — ファイル自体に差分は無いので討議時の grep 方法の違いが疑われる）。
**どう防ぐか:** プランは着手時に自分で `grep -nP '[\x{3040}-\x{30ff}\x{4e00}-\x{9fff}]' <file>` を対象 4 ファイルに再実行し、その出力を根拠にする。milestone invariant #4（discovery-time grep）の精神をそのまま適用。
**警告サイン:** タスクの見積り工数が実際の該当行数と大きく食い違う。

### Pitfall 3: `uv.lock` 自身の埋め込み版リテラルを忘れる

**何が起きるか:** `pyproject.toml:7` をバンプした後、`uv.lock` に埋め込まれた `typsphinx` 自己エントリの `version`（実測: `:1379` に `version = "0.6.3"`）も自動更新されると思い込み、`uv lock` 実行を省略する。
**なぜ起きるか:** 通常の依存バンプは `pyproject.toml` だけを触ればよいため、自己参照パッケージの自己ピンという特殊ケースを見落としやすい（Phase 23/28 と同型の pitfall）。
**どう防ぐか:** `pyproject.toml` 編集の直後、`uv sync --locked` を試す前に必ず `uv lock` を実行する。

### Pitfall 4: `main..HEAD` のコミット数・diff 範囲を CONTEXT.md の断面のまま固定する

**何が起きるか:** SC#4 の `git diff main..HEAD` 証跡に「254 コミット」という CONTEXT.md の数字をそのまま記載するが、実行時点では既に 256 になっている（Phase 32 完了記録の 2 コミットが後から積まれた）。
**なぜ起きるか:** CONTEXT.md 討議から本フェーズのプラン/実行までの間にも STATE.md 更新等のコミットが積まれ得る。merge-base（`771ec56`）自体は変わらないが、コミット数は変わる。
**どう防ぐか:** 証跡採取時に `git log --oneline main..HEAD | wc -l` と `git merge-base main HEAD` を都度再実行し、その場の生の値を記録する。

### Pitfall 5: D-05 の英語化で HTML コメント形式の履歴フッター（`<!-- Prior: ... -->`）を見落とす

**何が起きるか:** `.planning/PROJECT.md` の日本語含有行を Markdown としてレンダリングされる箇所だけスキャンし、`<!-- Prior: *Last updated: ... 実測整合 ... -->` のような HTML コメント内の日本語プローズ（`:341` 以降に複数箇所）を翻訳対象から漏らす。
**なぜ起きるか:** HTML コメントは GitHub 上でレンダリングされず見えないため、目視スキャンでは見落としやすい。
**どう防ぐか:** grep はコメント内テキストも生テキストとして拾う（本セッションで実測確認済み — `:341`, `:356`, `:360` はすべて `<!-- ... -->` 内）。プランはこれらの行も D-05 の対象として扱う（CONTEXT.md は「意味を変えない翻訳のみ」と明記しており、レンダリング可視性は除外条件にしていない）。

### Pitfall 6（Phase 28 由来、引き続き有効）: `docs` extras なしで docs ビルド証跡を採ろうとして失敗する

**何が起きるか:** `uv sync --extra dev`（`docs` extras なし）の状態で `tox -e docs-html`/`docs-pdf` 以外の直接 `sphinx-build` を実行し、`furo` テーマ等が欠けてビルドが失敗する。
**どう防ぐか:** SC#4 の証跡セット（Claude's Discretion）に docs ビルドを含める場合は `tox -e docs-html`/`docs-pdf` 経由で実行する（`extras = docs` を自動解決）。ただし本フェーズは `typsphinx/`/`docs/` を一切変更しないため、Phase 28 と異なり docs ビルド警告のベースライン再測定の必然性は薄い（討議領域として提示済み、Claude's Discretion）。

## Code Examples

### 推奨 `[0.6.4]` CHANGELOG エントリ（ドラフト）

技術的事実の裏取りは `.planning/PROJECT.md` の Phase 29〜32 Key Decisions プローズ（英語、本セッションで直接読了）に基づく。

```markdown
## [0.6.4] - 2026-07-28

Moves documentation hosting from GitHub Pages to Read the Docs: every published URL now resolves
against a Read the Docs project, a Japanese documentation site is live for the first time, and the
PDF a reader downloads from either site is the one typsphinx's own `typstpdf` builder produced — not
a LaTeX pipeline this project doesn't dogfood. The hand-rolled multi-language publishing machinery
this migration made obsolete is gone from the repository. Zero new runtime dependencies; the bundled
`@preview` version-sync surface (now covering four declaration sites) is untouched, and no line under
`typsphinx/` changed in this milestone.

### Added

- **Japanese documentation site at `/ja/latest/` (I18N-01, I18N-03)** — built from a separate
  `typsphinx-doc-translations` repository (a git submodule of this repository plus the relocated
  `ja` gettext catalogs) with its own Read the Docs project, linked under the English parent's
  Translations settings. The Japanese site is also downloadable as a PDF with its CJK glyphs
  correctly rendered.
- **Repository-wide link-check CI (CI-05)** — an advisory `links.yml` workflow now checks every
  published link across the whole repository (not just `docs/source/`, which is where Sphinx's own
  `linkcheck` cannot see the README/`pyproject.toml` links that motivated this).

### Changed

- **Documentation hosting moved from GitHub Pages to Read the Docs (RTD-01..RTD-04)** — built from a
  `.readthedocs.yaml` in the repository, with typsphinx itself installed from the in-repo commit
  (never a stale PyPI wheel). The downloadable PDF is produced by this project's own `typstpdf`
  builder via `build.jobs.build.pdf`, not Read the Docs' LaTeX pipeline.

### Removed

- **Hand-rolled multi-language publishing machinery and orphan documentation (I18N-02, DOC-08)** —
  `docs/build_multilang.py`, the custom language-switcher template, the `docs-multilang` tox
  environment, and the unreachable `docs/usage.rst`/`docs/installation.rst` orphan pair are gone.
  Language switching now works through Read the Docs' own flyout.
- **GitHub Pages hosting and the `gh-pages` branch (CI-04)** — the `peaceiris/actions-gh-pages` deploy
  step is removed from CI; the tag-time PDF Release attachment is unaffected. **Old
  `github.io` URLs now return 404 with no redirect** — an accepted cost of the immediate cutover.
  Automatic browser-language redirection at the documentation root is also gone: Read the Docs
  redirects to a *version*, never to a visitor's detected *language*; restoring that behavior would
  mean re-adding the custom template code this migration removes.

### Fixed

- **Seven dead documentation links in README/PyPI metadata resolved (DOC-09, DOC-10, Issue #119)** —
  every published documentation URL (README badges, deep links, `pyproject.toml`'s `Documentation`
  metadata) now points at `https://typsphinx.readthedocs.io/` and was confirmed live over real HTTP.

### Verified

- Milestone invariant held: zero new runtime dependencies, no `@preview` package version bump, the
  four-surface version-sync guard (`writer.py` / `template_engine.py` / `templates/base.typ` /
  `examples/**/*.typ`) untouched, and zero changes under `typsphinx/` across the full milestone diff.
```

*(D-03 により、フル pytest スイート等の証跡は本フェーズの `33-VERIFICATION.md` 側に置き、CHANGELOG 本文には書かない。)*

### `pyproject.toml`/`README.md` の版バンプ（差分イメージ）

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@
 [project]
 name = "typsphinx"
-version = "0.6.3"
+version = "0.6.4"
```

```diff
--- a/README.md
+++ b/README.md
@@ -314,7 +314,7 @@
-**Status**: Stable (v0.6.3) - Production ready
+**Status**: Stable (v0.6.4) - Production ready
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Phase 28（v0.6.3）は BREAKING ラベルを CONF-04/CONF-05 の 2 件に立てた | Phase 33（v0.6.4）は BREAKING ラベルをゼロにする（D-01） | 本フェーズの CONTEXT 討議 | パッケージ挙動の変化が皆無なマイルストームでは、CHANGELOG が「ユーザーの `conf.py` に影響する変更」と「ホスティング/リポジトリ運用の変更」を明確に区別できる |
| `test_preview_version_sync.py` は Phase 28 時点で既に 4 面（`examples/**/*.typ` 含む）をカバー | 変更なし、そのまま SC#1 の "now-four-surface" 表現が指すテストとして再利用 | Phase 28 で既に実装済み | 本フェーズに追加実装は不要 — SC#1 の文言だけが「新規に 4 面になった」かのように読めるが、実際にはこの milestone より前から 4 面 |

既存の project convention から外れた/非推奨のツールは特定されなかった。

## Assumptions Log

本セッションのすべての主張はリポジトリ内ファイルの直接読み取り（`grep`/`Read`）、実際に実行したコマンドの出力（`git diff`, `git log`, `curl`, `pytest`, `python -c`）で直接確認済み。`[ASSUMED]` タグの付いた主張はない。

**このテーブルは空 — プラン前のユーザー確認は不要。**

## Open Questions

1. **D-05 の MILESTONES.md 実測値（1 行）が CONTEXT.md の記載（11 行）と大きく異なる原因**
   - What we know: 本セッションで 2 種類の Unicode レンジ（狭域/広域）両方で再測定し、いずれも 1 行という結果が一致した。ファイル自体に討議後の変更履歴は見当たらない。
   - What's unclear: CONTEXT.md 討議時にどのようなコマンド/レンジで「11 行」を得たのかは不明。
   - Recommendation: プランは実行時の自己実測（上記コマンド）を根拠にする。MILESTONES.md の D-05 対応は 1 行の見出し翻訳のみで完了するとして計画してよい。過剰なタスク配分をしない。

2. **SC#4 の証拠セット範囲（Claude's Discretion、CONTEXT.md 明記の討議領域）**
   - What we know: 最低限は version-sync ガード 2 テスト（4 assert）の緑 + `git diff main..HEAD` の該当パス確認。`typsphinx/` を一切変更しないマイルストームなのでコーパスゲート実走の必然性は Phase 28 より弱い。
   - What's unclear: フル pytest スイート・`tox -e docs-html`/`docs-pdf` の実走をどこまで証跡に追加するか。
   - Recommendation: 本セッションで測定した「647 passed / 1 skipped」をベースラインとして `33-VERIFICATION.md` に記録し、フェーズ完了時に再実行して一致（またはそれ以上）を確認する軽量な証跡セットを推奨。docs ビルドはコード変更がないため必須ではない。

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+（実測: pytest-9.1.1、`pyproject.toml` `dev` extras `pytest>=8.4,<10`） |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`（`addopts = "-v --strict-markers"`、`slow`/`integration` マーカー登録済み） |
| Quick run command | `uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v`（サブ秒） |
| Full suite command | `uv run python -m pytest -q -rs`（実測 647 passed, 1 skipped in 55.76s） |

### Phase Requirements → Test Map

本フェーズ自身は要件 ID を持たない release/close phase のため、成果物とテストの対応で示す:

| Deliverable | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| `pyproject.toml`/`README.md` 版同期 | 両ファイルが同じ版を名乗る | unit | `uv run python -m pytest tests/test_readme_version_sync.py -v` | ✅ 既存 |
| `@preview` 4 面同期 | 未変更のまま維持 | unit | `uv run python -m pytest tests/test_preview_version_sync.py -v` | ✅ 既存 |
| `typsphinx.__version__` の更新（SC#1） | editable install メタデータ再同期後に `0.6.4` を報告 | manual/CLI | `uv run python -c "import typsphinx; print(typsphinx.__version__)"` | N/A — pytest テストではない |
| SC#3 `Documentation` メタデータの実 HTTP 到達性 | RTD ルートが 302→200 で解決 | other（`curl`） | `curl -sI https://typsphinx.readthedocs.io/`（追って `-L` でリダイレクト先も確認） | N/A |
| SC#4 マイルストーン不変量（`typsphinx/` 変更ゼロ） | `git diff main..HEAD -- typsphinx/` が空 | other（`git diff`、手動） | `git diff main..HEAD --stat -- typsphinx/` | N/A |
| SC#4 マイルストーン不変量（新規ランタイム依存ゼロ） | `pyproject.toml` の `dependencies` が版バンプ以外未変更 | other（`git diff`、手動） | `git diff main..HEAD -- pyproject.toml`（版バンプ行以外に差分が無いことを目視） | N/A |

### Sampling Rate

- **タスクコミットごと:** `uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v`（サブ秒）。
- **wave マージ / フェーズゲートごと:** フル pytest スイート（実測 ~56s）+ SC#4 の `git diff` 確認。
- **フェーズゲート:** version-sync ガード green、フルスイートが 647 passed（またはそれ以上）/ 0 failed、`git diff main..HEAD -- typsphinx/` が空であることを `/gsd-verify-work` の前に確認する。

### Wave 0 Gaps

**なし。** 本フェーズが必要とするすべてのテスト資産（`tests/test_readme_version_sync.py`、`tests/test_preview_version_sync.py`）は既に存在し、このセッションで green であることを直接確認済み。新規フィクスチャ・新規フレームワークインストールは不要。

## Security Domain

**`security_enforcement` は on（`.planning/config.json`）だが、本フェーズには評価すべき攻撃面の変化がない。** 触るのは版リテラルの文字列、CHANGELOG/README/planning markdown、ロックファイルの再生成のみ — ユーザー入力なし、新規ネットワーク呼び出しなし（`Documentation` URL の実 HTTP 確認は読み取り専用の `curl`）、認証/セッション/アクセス制御面なし、暗号なし。

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No（リポジトリローカルの固定パスファイルを読むだけ） | N/A |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| `uv lock` によるピン外の transitive 依存の混入 | Tampering（低関連度） | `pyproject.toml` の直接依存は既存の `>=X,<Y` レンジピンで保護されており、本フェーズはそのレンジを変更しない。`uv.lock` の diff を目視確認する（上記 Pitfall 3）ことが対応する検証手段 |

本フェーズが新規に導入する脅威はない。Security Domain セクションは config デフォルトにより含めているが、意味のあるリスク面ではない。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | 版バンプ / ロックファイル再生成 / editable install 再同期（SC#1） | ✓ | このセッションで動作確認済み | — |
| `git` ブランチ `main` | SC#4 不変量 diff の base ref | ✓ | `main` = `771ec56`（実測: `git merge-base main HEAD` = `main` 自身） | — |
| ネットワークアクセス（`curl` → readthedocs.io） | SC#3 の実 HTTP 確認 | ✓（本セッションで 302→200 を実測確認済み） | — | — |
| `tomllib`（stdlib） | 既存の版同期テスト | ✓ | Python 3.13.13（このセッションの venv 実測）、stdlib since 3.12 | — |

**フォールバックのない欠落依存:** なし。

**フォールバックのある欠落依存:** なし — 本フェーズが必要とするすべての依存は、このセッションで存在・動作を確認済み。

## Sources

### Primary (HIGH confidence — このセッションで直接読み取り/実行)

- `.planning/phases/33-v0-6-4-release-prep/33-CONTEXT.md` — 全ロック決定（D-01〜D-05）、canonical references、実測事実テーブル
- `.planning/REQUIREMENTS.md` — REL-02 全文、Milestone Invariants #1〜#7、Owner-Manual Steps、Traceability
- `.planning/STATE.md` — ロードマップ要約、carry-forward、Operator Next Steps
- `.planning/PROJECT.md` — Phase 29〜32 の Key Decisions 英語プローズ（CHANGELOG ドラフトの技術的裏取り）
- `.planning/ROADMAP.md` §Phase 33 — SC#1〜SC#5 全文
- `.planning/milestones/v0.6.3-phases/28-v0-6-3-release-prep-regression-gate-close/28-RESEARCH.md`、`MILESTONES.md`（v0.6.3 節） — 同型フェーズの直接の先例
- `CHANGELOG.md` — 全文読了。構造テンプレート、`[0.6.3]` の節構成、末尾リンクブロックの現状
- `README.md` — Status 行の位置確認
- `pyproject.toml` — 版リテラル位置、`[project.urls]` 実測（`Documentation` は既に RTD URL）
- `uv.lock` — `typsphinx` セルフエントリの直接確認
- `tests/test_readme_version_sync.py`、`tests/test_preview_version_sync.py` — 全文読了
- `git diff main..HEAD -- pyproject.toml/uv.lock/typsphinx/`、`git log --oneline main..HEAD | wc -l`、`git merge-base main HEAD`、`git tag -l` — すべてこのセッションで実行
- `curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" [-L] https://typsphinx.readthedocs.io/` — このセッションで実行、302→200 を確認
- `uv run python -m pytest -q -rs`、`uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` — このセッションで実行
- `uv run python -c "import typsphinx; print(typsphinx.__version__)"` + `find . .venv -iname "*typsphinx*"` — このセッションで実行、editable install メタデータの版埋め込みを確認
- `.planning/config.json` — `nyquist_validation: true`、`security_enforcement: true`、`use_worktrees: true` を確認

### Secondary (MEDIUM confidence)

なし — 本セッションのすべての主張はリポジトリまたはローカル実行コマンドで直接検証可能であり、Web 検索は不要だった（本フェーズはリポジトリ内で完結するリリース準備フェーズ）。

### Tertiary (LOW confidence)

なし。

## Metadata

**Confidence breakdown:**

- CHANGELOG 構造テンプレート・要件カバレッジマッピング: HIGH — ファイル全文読了 + `.planning/PROJECT.md` の英語 Key Decisions プローズと直接突き合わせ。
- D-05 の行数実測: HIGH — 4 ファイルすべてを狭域/広域 2 種類の Unicode レンジで再測定し一致を確認。CONTEXT.md との乖離自体もこのセッションで実測した事実。
- SC#4 不変量確認コマンド: HIGH — base ref（`main`）の存在と merge-base 関係、`typsphinx/` diff の空性を直接確認済み。
- editable install メタデータ再同期の必要性: HIGH — `.venv` 内の実ファイルを直接確認し、版番号がファイル名に埋め込まれていることを実測。
- SC#3 の実 HTTP 確認: HIGH — `curl` を実際に実行し 302→200 を確認済み。

**Research date:** 2026-07-28
**Valid until:** 構造的な主張（CHANGELOG テンプレート、要件マッピング）は実質無期限有効。環境依存の主張（`main..HEAD` のコミット数、`uv`/Python バージョン、RTD の実配信状態）はセッション断面のものなので、計画が数日以上遅延する場合は再確認を推奨（標準的な 7〜30 日ガイダンスに従う）。特に「main..HEAD のコミット数」は本フェーズ自身の実行中にも増減し得るため、証跡採取のたびに再実行すること。
