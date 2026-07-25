# Phase 28: v0.6.3 Release Prep + Regression-Gate Close - Research

**Researched:** 2026-07-25
**Domain:** リリースエンジニアリング / CHANGELOG キュレーション / 回帰ゲート実走（ソース振る舞い変更なし）
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**CHANGELOG `[0.6.3]` の BREAKING 判定**

- **D-01: CONF-05（`typst_toctree_defaults` 削除）は `### Removed` に置き BREAKING ラベルを立てる。** Phase 23 D-05（オーナー裁定 2026-07-23、「公開されていた設定名の削除は実害の有無に関わらず仕様上破壊的」）の踏襲。本文には v0.6.2 の CONF-01 項目と同じ形で実測の但し書きを添える — 削除後も `conf.py` に残っていれば Sphinx は**警告すら出さず無音で無視して `build succeeded`**、かつ削除前から出力に一切効いていない dead config なので実際の振る舞いは変わらない。
- **D-02: CONF-04 の未知キー fail-loud にも BREAKING ラベルを立て、`### Changed` に置く。** こちらは実害のある本物の破壊的変更 — Phase 26 以前は `map_parameters()` が `DEFAULT_PARAMETER_MAPPING` の 3 キー（project/author/release）以外の `typst_elements` キーを黙って捨てていたのに対し、現在は `ELEMENTS_ALLOWLIST`（`papersize`/`fontsize`/`lang`）外のキーが 1 つでもあれば `ExtensionError: typst_elements: unknown key ...` でビルドが中断する。飾りのキーを入れていたユーザーは `conf.py` を一切触らずに緑→硬失敗に変わる。本文に対処手順を書く（D-04）。
- **D-03: CONF-07（lang 連動）は `### Fixed` に置き、BREAKING は立てない。** 「`base.typ` が組版言語を `lang: "en"` でハードコードしていたバグの修正」という位置づけで、Phase 23 D-07（Issue #117 の出力ファイル名変更を「本来そうすべきだったものの修正」として BREAKING にしなかった裁定）と同じ基準。本文で before/after を示す — `language = "ja"` のプロジェクトが既定テンプレートで "Table 1"/"Figure 1" →「表 1」「図 1」になる。適用範囲も本文に書くこと（自動導出は既定テンプレート経路のみ。カスタムテンプレート / `typst_package` / srcdir シャドウの 3 経路には注入されない）。
- **D-04: アップグレード対処手順は CHANGELOG 本文にのみ書く。docs は触らない。** D-02 の BREAKING 項目内に 1〜2 行で「allowlist 外のキーは削除する。値を渡し続けたい場合は `typst_template_function.params` を使う」と書く。本フェーズが触るファイルは `pyproject.toml` / `uv.lock` / `CHANGELOG.md` / `README.md` の 4 つに留める。

**回帰ゲートと証跡の範囲**

- **D-05: SC#3 の証跡は「コーパスゲート + フル pytest スイート + docs ビルド」の 3 点を `28-VERIFICATION.md` に記録する。** Phase 23 D-09/D-12 のコーパスゲート単独から範囲を広げる。根拠: 本マイルストーンは `base.typ` の `project()` 署名・テンプレート解決経路・docs を触っており、Phase 27.1 では executor が worktree 内から docs ビルド警告を観測できず、マージ後に警告 5 行の増加が発覚して後追い修正した実績がある（現在はフェーズ前ベースラインの 4 行に復帰済み）。
  - コーパスゲート: `pytest -m slow -rs`（skip 理由を強制表示）で `tests/test_corpus_gate.py` を実走し、`1 passed`（`skipped` ではない）と読める生ログを貼る — Phase 23 D-12 の踏襲。コーパス入手不能時に `pytest.skip` する仕様なので「緑」が「スキップ」を意味し得る。
  - フルスイート: 実 `typst.compile()` の GATE-01 フィクスチャ群を含む全体の緑（Phase 27.1 時点で 656 passed / 1 skipped / 0 failed）。
  - docs ビルド: `tox -e docs-multilang` と `tox -e docs-pdf`。
- **D-06: docs ビルドの合否基準は Claude 裁量。** 既定は「フェーズ前ベースライン（既知の 4 行、既存 `translator.py` 由来警告を含む。ゼロではない）から警告が増えていないこと」で、実際の警告行を `28-VERIFICATION.md` にそのまま貼る。行数の厳密一致を assert するテストは作らない（テスト基盤の拡張はリリース準備のスコープ外 — Phase 23 D-12 と同じ判断）。ベースラインをどのコミットで測るかもプラン時に決めてよい。
- **D-07: SC#4 の確認は `git diff` の実出力を `28-VERIFICATION.md` に貼り、既存テストの緑をもって足りるとする。** 実測済み: `git diff main..HEAD -- typsphinx/templates/base.typ` は正確に 2 行（`project()` への `lang: "en",` 追加と `set text(size: fontsize, lang: lang)` への変更）だけ、`@preview` 4 パッケージの版文字列は未変更、`pyproject.toml` の依存も差分ゼロ。`tests/test_preview_version_sync.py` の緑が 3-way 同期面の担保。追加実装ゼロ。`base.typ` の sha256 を新しい基準値として記録する案は採らない（以降のフェーズが `base.typ` を意図的に変えるたび更新が必要になるため）。
- **D-08: ja の PDF での目視確認は行わない。** 実測: `tox -e docs-pdf` が作る PDF は英語（`docs/source` の conf に `language` 設定なし）、`docs-multilang` は en/ja とも **HTML のみ**。つまり「ja の PDF で『表 N』が出る」はどの tox 環境でも目に見えない。Phase 27.1 の GATE-01 フィクスチャ（ja の `.typ` ソース証明 + de の PDF 抽出、計 21 テスト）がこれを機械的に固めており、それがフルスイート（D-05）の一部として回る。手作業の目視確認は再現性が低く、「検証機構を持てない事実は残さない」という Phase 22.4 以来の原則にも合わない。

**CHANGELOG の粒度と構成**

- **D-09: 項目化の単位はユーザー可視の変化。** 7 要件を 1 対 1 で列挙せず、Phase 23 D-01 の原則（読み手はユーザーで要件 ID を知らない。末尾の括弧に ID を並べて追跡性を保つ）を適用する。TBL-01/TBL-02 は「キャプション付きテーブルが番号付き Table N になり相互参照できる」として 1 項目に束ねる。CONF-04 / CONF-05 / CONF-07 はそれぞれ節が違うので別項目。結果は 5 項目前後。
- **D-10: docs 系は DOC-07 のみ載せる。DOC-06 は載せない。** 可視性が非対称であるため — DOC-07（`user_guide/configuration.rst` の phantom 設定名 5 個の削除・`typst_elements` の動く例への書き換え、`api/index.rst` の重複表の削除）は公開ドキュメントサイトの記述が変わるのでユーザーに可視で、Phase 23 D-03/D-04 の「誤情報の訂正は `### Fixed` に載せる」に該当する。DOC-06（孤児 `docs/configuration.rst` の削除）はどの toctree からも到達不能で、ユーザーの目には元々入っていない内部整理。**結果として台帳 7 件のうち DOC-06 だけが CHANGELOG に現れない** — これは意図的な選択であり、プランが「全要件を漏れなく列挙」を理由に足し戻さないこと。
- **D-11: `### Verified` 節は先例と同じ 4 点に留める。** fatal-free / `%PDF` マジック有効 / `unknown_visit` カタログがクリーン / SC#4 不変量（新規ランタイム依存ゼロ・`@preview` 未バンプ・`base.typ` の差分は `lang` の 2 行のみ）。D-05 で証拠に加えるフル pytest スイートと docs ビルドは `28-VERIFICATION.md` 側の証跡に留め、CHANGELOG には書かない。ページ数など検証機構を持てない数値は載せない（Phase 23 D-11）。
- **D-12: リード段落は 3 トラック軸で書く。** 「ドキュメントに書いた設定が実際に出力へ効くようになった / キャプション付きテーブルを番号付き figure として出力するようにした / docs の記述を実装と一致させた」の 3 軸 + 不変量の一行。`[0.6.2]` のリード文と同じ体裁。BREAKING をリード文の冒頭で先出しする案は不採用（既存の体裁を保つ）。BREAKING の可視化は D-01/D-02 の項目本体が担う。

### Claude's Discretion

- docs ビルドの合否基準とベースラインの取り方（D-06）。
- `uv.lock` の再生成手順 — `uv lock` か `uv sync` か。SC#1 の受入は `uv sync --locked` が緑になること。
- `## [0.6.3]` の日付 — プラン実行日を使う（Phase 23 D-15 の確立済みルール。`- Unreleased` のまま残して `/gsd-complete-milestone` で確定する案は不採用）。
- 各項目の具体的な文面 — BREAKING ラベルの表記形式、実測の但し書きをどこまで織り込むか、before/after 例の書き方。
- フェーズ内の作業分割とプラン数（版バンプ → CHANGELOG → ゲート実走 の順が自然）。
- `## [Unreleased]` 節の保持 — Keep a Changelog 標準どおり `[0.6.3]` の上に残す想定。

### Deferred Ideas (OUT OF SCOPE)

- `examples/advanced` が現状ビルド不能 — 討議で領域として提示したがオーナーは選択せず、pending todo `.planning/todos/pending/2026-07-25-examples-advanced-non-allowlisted-typst-elements-keys.md` のまま据え置き。
- `docs/usage.rst` / `docs/installation.rst` の orphan クラス — pending todo `2026-07-25-docs-usage-installation-orphan-class.md`。
- `derive_typst_lang()` の警告ブロック重複 — pending todo `2026-07-25-derive-typst-lang-duplicated-warning-block.md`。
- README の依存下限 3 行の同期テスト — Phase 23 D-14 でスコープ外とした案。
- リリースゲートで `pytest.skip` を失敗として扱う仕組み — Phase 23 D-12 で不採用。
- `todo.match-phase 28` が返した 10 件はいずれも折り込まない（本フェーズは `typsphinx/` を一行も触らないリリース準備）。
</user_constraints>

<phase_requirements>
## Phase Requirements

ROADMAP/STATE 上、Phase 28 に紐づく要件 ID は「none（release/close phase）」— しかし D-09 が「v1 要件台帳 7 件」を本フェーズの de-facto カバレッジ対象にしている（Phase 23 D-01 と同型の位置づけ）。CHANGELOG `[0.6.3]` エントリはこの 7 件のうち 6 件（DOC-06 を除く、D-10 により意図的）を漏れなく引用する。

| ID | 内容（ユーザー可視の一言） | → CHANGELOG 上の扱い |
|----|---------------------------|------------------------|
| CONF-04 | `typst_elements` の `papersize`/`fontsize` が `project()` に届く。allowlist 外キーは fail-loud | `### Changed`、BREAKING（D-02） |
| CONF-05 | 死んでいた `typst_toctree_defaults` を削除 | `### Removed`、BREAKING（D-01） |
| CONF-07 | Typst 組版言語が Sphinx `language` に連動 | `### Fixed`、BREAKING なし（D-03） |
| TBL-01 | キャプション付きテーブルが `figure(..., kind: table)` で "Table N" 番号付き | `### Added`（TBL-02 と 1 項目に束ねる、D-09） |
| TBL-02 | `:numref:`/`:ref:` がキャプション付きテーブルに解決する | `### Added`（TBL-01 と同一項目） |
| DOC-06 | 孤児 `docs/configuration.rst` を削除 | **載せない**（D-10、意図的） |
| DOC-07 | `user_guide/configuration.rst` / `api/index.rst` の phantom 設定名を修正 | `### Fixed`（D-10） |

**結果: 5 ブレット**（Added 1 / Changed 1 / Removed 1 / Fixed 2）。D-09 の「5 項目前後」に厳密に一致する。
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Worktree 分離実行がこのプロジェクトの標準実行モード**（オーナー判断 2026-07-20、`workflow.use_worktrees: true`）。ただし本フェーズの研究セッション自体はメインツリー（`.git` がディレクトリ）で実行しており、以下の実測コマンドはすべてメインツリー上で直接動作を確認した。executor がワークツリーで実行する場合は、他フェーズと同じく `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` を最初に実行し、以後すべて `uv run` 経由で実行すること。
- **CI と一致させる**: `black --check .`、`ruff check .`、`mypy typsphinx/`。本フェーズは `typsphinx/` を一行も触らないので `mypy` は実質 no-op。`black`/`ruff` は新規ファイルを作らない本フェーズでは対象ファイルなし（4 ファイルはいずれも markdown/TOML/lock）。
- **`tox.ini` の `tox-uv~=1.35` ピンは意図的** — このフェーズで触らない。
- **`UP006`/`UP035` の ruff ignore は維持** — pending todo が着地するまで typing import を modernize しない。このフェーズは `pyproject.toml` を開くが `[tool.ruff]` の ignore リストには触れない。
- Line length 88（black 管理）、`E501` は ruff で ignore — 本フェーズが触るファイルに Python はない。
- 本フェーズが触るファイルは `pyproject.toml` / `uv.lock` / `CHANGELOG.md` / `README.md` の 4 つのみ（28-CONTEXT.md の明示的な柵）。`typsphinx/` 配下・`docs/` 配下・`examples/` 配下はすべて対象外。

## Summary

Phase 28 は**ソース振る舞い変更ゼロ**のリリース準備 + 回帰ゲート締めフェーズであり、必要な事実はすべて本リポジトリ内（git 履歴、既存テスト、直前フェーズの CONTEXT/PROJECT.md）にあり、外部ライブラリや Web ドキュメントへの依存はない。変更対象の実体は 4 ファイル: `pyproject.toml:7`（版リテラル）、`uv.lock`（再生成）、`CHANGELOG.md`（新規 `## [0.6.3]` セクション + リンクブロック更新）、`README.md:315`（Status 行）。5 つ目の「成果物」は挙動そのもの — `tests/test_corpus_gate.py` のフル回帰ゲート、フル pytest スイート、`tox -e docs-multilang`/`docs-pdf` の実走とその証跡採取。

**このセッションで実機測定した最重要事実（詳細は各節）:**

1. 現在のブランチ（main の 1 コミット先）で `git diff main..HEAD -- pyproject.toml` / `uv.lock` は**完全に空**、`git diff main..HEAD -- typsphinx/templates/base.typ` は正確に 2 行 — CONTEXT.md の実測記述をこのセッションで再確認・再現できた。SC#4 は既に自明に成立している状態からスタートする。
2. フル pytest スイート（`uv run python -m pytest -q -rs`、slow マーカー込み）は **656 passed, 1 skipped in 56.64s** — CONTEXT.md の「656 passed / 1 skipped」を寸分違わず再現。NixOS サンドボックスの環境依存失敗（従来 45 件と記録されていたもの）は**このセッションでは発生しなかった**（メインツリー・サンドボックス lifted 状態）。
3. コーパスゲート単体（`pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s`）は **`1 passed in 13.08s`**、`Unknown Visit Catalogue: []` — 実際に PASS（SKIP ではない）ことを確認済み。
4. **`docs-pdf` と `docs-multilang` はベースライン警告行数が別物** — `tox -e docs-pdf`（英語のみ）は **2 行**（`translator.py` の `visit_toctree` docstring 由来の ERROR 1 + WARNING 1）、`tox -e docs-multilang`（en+ja の 2 言語ビルド）は同じ 2 行が**言語ごとに出るため合計 4 行**。CONTEXT.md D-06 の「4 行」は `docs-multilang` の値であり、`docs-pdf` に同じ基準（4 行以下）を適用すると常に「2 行しか出ない」ため無意味な基準になる。プランは**2 つの tox 環境それぞれに個別のベースラインを持たせる**必要がある。
5. `tests/test_corpus_gate.py` には SC#3 のゲート本体（`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`）とは**別の**、`TYPSPHINX_CORPUS_REPORT=1` で条件付き実行される計測用テスト（`test_empty_url_before_after`）が存在し、これがフルスイート実行時に "1 skipped" として現れる。この skip は SC#3 の合否とは無関係で、Phase 23 の "corpus gate skip" とは別の pitfall（下記 Common Pitfalls）。

**Primary recommendation:** 実行順序は D-16（Claude's Discretion）が示唆する通り — 版バンプ → CHANGELOG → ゲート実走・証跡記録。CHANGELOG 本文は下記「Code Examples」のドラフトをほぼそのまま使える（D-01〜D-12・7 要件のカバレッジをすべて満たしている）。

## Architectural Responsibility Map

本フェーズはアプリケーション層のコードを一切触らないため、ブラウザ/API/DB 等の標準ティアは適用外。リリース準備フェーズ向けに読み替える:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 版リテラルのバンプ | ビルド/パッケージメタデータ（`pyproject.toml`） | ロックファイル（`uv.lock`） | `pyproject.toml:7` が唯一の版リテラル（実測確認済み）。`uv.lock` の `typsphinx` 自己エントリ（~1379 行目）も追随させないと `uv sync --locked` が乖離する |
| CHANGELOG キュレーション | ドキュメント（リポジトリ直下） | — | 純粋なプローズ。どのコードパスも `CHANGELOG.md` を読まない |
| README Status 同期 | ドキュメント（リポジトリ直下） | テスト/CI（`tests/test_readme_version_sync.py`、Phase 23 で新設・既存） | 既に存在する同期ガードを再利用するのみ。新規コードは不要 |
| 回帰ゲート実走 | テスト/CI（`tests/test_corpus_gate.py`） | — | 既存資産の実走と証跡採取。追加実装ゼロ |
| マイルストーン不変量の確認 | テスト/CI（`tests/test_preview_version_sync.py`）+ `git diff` | ビルド/パッケージメタデータ | `@preview` 3-way 同期面と依存集合が `main` から未変更であることを確認 |
| docs ビルド警告のベースライン確認 | ドキュメントビルド（tox: `docs-pdf`/`docs-multilang`） | — | Phase 27.1 で executor がワークツリー内から観測できず後追い修正した実績があるための D-05 の追加証跡 |

## CHANGELOG Structural Template（実測: `CHANGELOG.md` 全文読了）

- **`## [Unreleased]`** が 8 行目にあり、空行（9 行目）を挟んで **`## [0.6.2] - 2026-07-23`** が 10 行目から続く。**`## [0.6.3]` はこの 9 行目と 10 行目の間に挿入する**（`## [Unreleased]` の直後、`## [0.6.2]` の直前）。
- **`[0.6.2]` の節構成**（実測、これが直接の型紙）: リード段落（4 行）→ `### Removed`（BREAKING 1 件）→ `### Fixed`（11 件、末尾に要件 ID を括弧で列挙するスタイル、例 `(FID-02–FID-06)` `(PDF-01, Issue #117)`）→ `### Verified`（2 件）。この順序（Removed → Fixed → Verified）は Keep a Changelog の語彙順（Added, Changed, Deprecated, Removed, Fixed, Security）そのものではなく、[0.6.2] 固有の並び。一方 `[0.6.1]` は `### Added` → `### Changed` → `### Fixed` → `### Verified` という KaC 語彙順に近い並びを使っている。**本フェーズは Added/Changed/Removed/Fixed が全部揃うため、KaC の語彙順（Added → Changed → Removed → Fixed → Verified）を推奨** — `[0.6.1]` の precedent に近い。
- **BREAKING の書式**: 過去の使用例はセクション見出しサフィックス型（`### Changed (Breaking)`、v0.3.0/v0.4.0）とバレット先頭ボールド型（`- **BREAKING: Unified Code Mode Architecture** (...)`、v0.4.0）の 2 種類があるが、`[0.6.2]` の CONF-01 項目が採用したのは**バレット先頭ボールド型**（`- **BREAKING: typst_output_dir and typst_author_params config values removed (CONF-01)** — ...`）。本フェーズの D-01/D-02 も同じ形式で踏襲する。
- **要件 ID の引用スタイル**: `[0.6.2]` の各バレットは太字見出しの直後、閉じ括弧の直前に要件 ID を挿入している（例: `**Lost block separation across five constructs (FID-02–FID-06)**`、`**typst_package (...) now builds ... (CONF-02, CONF-03)**`）。本フェーズも同じ位置に ID を書く。
- **リンクブロック（ファイル末尾、実測）:**
  ```
  [0.6.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
  [0.6.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.1
  ...(以下省略、古い順に続く)...
  [Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.2...HEAD
  ```
  **ROADMAP SC#2 は「`[0.6.3]` の releases/tag リンク行の追加」と「`[Unreleased]` compare リンクの繰り上げ」を明示的に本フェーズの仕事としている**（Phase 23 のように「タグがまだ無いので追加しない」という判断は今回は取らない — 実際 Phase 23 でも最終的にはレビュー指摘を受けて同じ形で追加された。これは v0.6.1 リリース準備コミット（`eba914c`）から続く確立済みの project convention）。
  - **Before → After（正確な変更）:**
    - 追加: `[0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3` を `[0.6.2]:` 行の**直前**に挿入（新しい順で並んでいるため）。
    - 変更: `[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.2...HEAD` → `[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.3...HEAD`。
  - `v0.6.3` タグはこのフェーズでは存在しない（SC#5 のスコープ柵）ため、このリンクは `/gsd-complete-milestone` がタグを打つまで 404 になる — これは v0.6.1/v0.6.2 いずれの release-prep でも同じ状態を経ており、project convention として許容されている（GitHub の releases/tag URL はタグが存在しないと 404 だが、タグ作成と同時に解決する）。

## Package Legitimacy Audit

**該当なし — 本フェーズは外部パッケージを一切インストールしない。** 新規ランタイム依存・開発依存の追加はゼロ（`git diff main..HEAD -- pyproject.toml` が空であることを実測確認済み）。`uv.lock` の再生成は `typsphinx` 自身の版リテラルのみを更新するセルフエントリ更新であり、依存変更ではない。Package Legitimacy Gate はそのトリガー条件（「外部パッケージをインストールするフェーズ」）に該当しないためスキップする。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| フルコーパス回帰の証明 | 新しいコーパスゲートテストや手動 `sphinx-build` 実行 | `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`（既存、`@pytest.mark.slow`） | D-05 は既存資産の実走と証跡採取のみを求める。既存ゲートが tag-resolve → キャッシュ済みクローン → `-b typstpdf` → `%PDF` チェック → `unknown_visit` カタログ抽出まで全部やる |
| README/pyproject の版ドリフト防止 | 新しい ad-hoc 文字列チェックや pre-commit フック | `tests/test_readme_version_sync.py`（Phase 23 で既に新設・既に存在） | 既に SC#1/D-13 を満たす資産がリポジトリにある。バージョンを両方バンプするだけで自動的に検証対象になる |
| SC#4 不変量の確認 | 新しい CI チェック | `git diff main..HEAD` の該当ファイルへの絞り込み + 既存 `tests/test_preview_version_sync.py` の緑 | Claude's Discretion がこれで十分としている。新しいツール不要 |
| docs ビルド警告の記録 | 警告数を assert する新しいテスト | `tox -e docs-multilang` / `tox -e docs-pdf` の生ログをそのまま `28-VERIFICATION.md` に貼る | D-06 が明示的に「行数の厳密一致を assert するテストは作らない」としている |

**Key insight:** 本フェーズの「Don't Hand-Roll」はすべて「新しい仕組みを作るな — 既にこの形の precedent がプロジェクトにある、それを再利用しろ」という一貫したパターン。研究の価値は代替案の評価ではなく、precedent の**特定**そのものにある。

## Corpus Gate Execution Mechanics（D-05/D-12、このセッションで実行・再測定）

### 実行コマンド（実測動作確認済み）

```bash
uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s
```

- `-m slow` が `@pytest.mark.slow` クラスを選択（node id と重複するが D-05 の文言どおり明示しておく）。
- `-rs` が skip 理由文字列を summary に強制表示する — これが genuine `1 passed` と `1 skipped (...)` を区別する手段（D-12 の核心）。
- `-v -s` で per-test の詳細出力（`print()` されるコーパスタグ・コミット SHA・`Unknown Visit Catalogue` の内容）も見える。

### このセッションでの実測結果

```
tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error Corpus tag: v9.1.0
Corpus commit SHA: cc7c6f435ad37bb12264f8118c8461b230e6830c
Unknown Visit Catalogue: []
PASSED

1 passed in 13.08s
```

`SKIPPED` 行なし、summary が `1 passed`（`1 skipped` ではない）。13.08 秒という所要時間も実コンパイルの妥当な範囲（skip なら瞬時に終わる）。Phase 23 の実測（13.67s/13.99s）とほぼ同一の所要時間で、コーパスキャッシュがオフラインで再利用できていることを裏付ける。

### skip 条件（変更なし、Phase 23 と同一クラス構造）

`corpus_doc_dir` フィクスチャの `get_or_clone_corpus()` がネットワーク不能・クローン失敗・対応タグ不明のいずれかで `None` を返した場合のみ `pytest.skip("Sphinx doc/ corpus unavailable ...")`。このセッションではキャッシュ済みコーパスが存在し、オフラインで実行できた（`~/.cache/typsphinx-corpus-gate/` 相当のパスに存在、Phase 23 と同じ仕組み）。

### 重要な新規発見: `test_corpus_gate.py` には SC#3 とは無関係な env-gated テストが追加されている

Phase 23 時点では `TestCorpusRenderGate` クラスの skip 条件が唯一の skip パスだった。**このセッションで確認したところ、同ファイルには Phase 27.1 由来と思われる別のテスト `test_empty_url_before_after`（270 行台の `@pytest.mark.slow` デコレータ付き、独立関数）が存在し、`TYPSPHINX_CORPUS_REPORT` 環境変数が `"1"` でない限り常に `pytest.skip(...)` する。** フルスイート実行（`uv run python -m pytest -q -rs`）でこの skip が単独で `1 skipped` として summary に現れる:

```
SKIPPED [1] tests/test_corpus_gate.py:529: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
656 passed, 1 skipped in 56.64s
```

**これは SC#3 の合否には一切影響しない**（このテストは別の計測用フィクスチャであり、`TestCorpusRenderGate` の合否とは独立）。しかし executor/verifier がこの `1 skipped` を見て「コーパスゲートがまた skip した」と誤読するリスクがある（Common Pitfalls 参照）。CONTEXT.md の「656 passed / 1 skipped」という基準値は、まさにこの `test_empty_url_before_after` の skip を含んだ数字であり、`TestCorpusRenderGate` 自体は別途 `-m slow` 明示実行で PASS を確認する必要がある。

## Full-Suite Baseline（D-05、このセッションで再測定）

```bash
uv run python -m pytest -q -rs
```

**結果: `656 passed, 1 skipped in 56.64s`** — CONTEXT.md/STATE.md が記録する「Phase 27.1 時点で 656 passed / 1 skipped / 0 failed」と完全に一致。このコミット（Phase 28 着手時点の HEAD）で再現できることを実機確認済み。

**NixOS サンドボックス環境依存失敗（従来 45 件と記録）はこのセッションでは発生しなかった** — メインツリー（`.git` がディレクトリ、worktree ではない）で `uv run` 経由で実行し、`tests/test_integration_*.py`（4 ファイル）・`tests/test_examples_basic.py` を含め全テストが green。プロジェクトメモリ（`nixos-sandbox-test-env.md`）の 2026-07-22 更新が指摘する「サンドボックスが lifted されている場合はこの除外が不要」という状態に現在該当すると判断できる（ただし executor が worktree 内で実行する場合はメモリファイルの警告どおり別の結果になり得るため、以下の Common Pitfalls で明記する）。

`-m "not slow"` を付けた場合は `628 passed, 29 deselected`（slow マーカー付きテストがデセレクトされ、コーパスゲートも含め実行されない）。**D-05 の「フルスイート」証跡には `-m "not slow"` を付けない**（`-m slow` のテストも含めた 656 件の合計を証跡にする）。

## Docs Build Baseline (D-06) — 実測、tox 経由で確認

### 実行コマンド（実測動作確認済み、`uv run tox` 経由）

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
uv run tox -e docs-pdf
uv run tox -e docs-multilang
```

両方とも `uv-venv-lock-runner`（`extras = docs`）で `furo`/`sphinx-autodoc-typehints`/`sphinx-intl` を含む `docs` extras を自動でインストールする。`docs` extras なしの `uv sync --extra dev` だけでは `sphinx-build` 自体は動くが `furo` テーマなどが欠けて docs ビルドが失敗するため、事前に `--extra docs` を含めた sync が必要（tox 経由なら自動）。

### `tox -e docs-pdf`（英語のみ）— 実測: 2 行

```
docs-pdf: OK (3.03=setup[0.52]+cmd[2.52] seconds)
congratulations :) (3.06 seconds)
```
ビルド末尾ログ: `build succeeded, 2 warnings.`

生ログの該当行（`typsphinx/translator.py` の `visit_toctree` docstring に起因、pre-existing）:
```
/home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```
根本原因: `visit_toctree()` の docstring がインデント付きの箇条書き相当のテキストを含み、Napoleon/autodoc が RST として解析する際にブロッククォートとして誤認する（本フェーズのスコープ外、docs/typsphinx いずれも触らない）。

### `tox -e docs-multilang`（en + ja の 2 言語 HTML ビルド）— 実測: 4 行

```
docs-multilang: OK (6.11=setup[0.50]+cmd[5.61] seconds)
congratulations :) (6.13 seconds)
```
英語ビルドと日本語ビルドそれぞれで**同じ 2 行**（上記と同一の ERROR+WARNING ペア、`visit_toctree` docstring 由来）が出るため、合計 **4 行**:
```
(English build)
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
[.../translator.py:docstring of ...visit_toctree:7: ERROR: Unexpected indentation. [docutils]]
[.../translator.py:docstring of ...visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]]

(Japanese build)
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
[.../translator.py:docstring of ...visit_toctree:7: ERROR: Unexpected indentation. [docutils]]
[.../translator.py:docstring of ...visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]]
```
（`build_multilang.py` は言語ごとの警告のみを標準出力に流すよう `-D language=<lang>` で 2 回 `sphinx-build -b html` を呼ぶ実装。ソースは同一なので警告内容は言語間で同一）。

### 具体的で再現可能な合否基準（プランへの推奨）

CONTEXT.md の「4 行」は **`docs-multilang` 固有の値**であり、`docs-pdf`（英語のみ、単一言語ビルド）にそのまま適用すると誤り — `docs-pdf` は構造上 2 行までしか出ない。プランの Acceptance Criteria は**環境ごとに個別のベースライン**を持つべき:

- `tox -e docs-pdf` の合否基準: `build succeeded, 2 warnings.`（またはそれ以下）— 現状の 2 行（`translator.py` の `visit_toctree` ERROR+WARNING）を超えて増えていないこと。
- `tox -e docs-multilang` の合否基準: 英語・日本語それぞれの警告出力が現状の 2 行ずつ（合計 4 行）を超えて増えていないこと。

この基準はテストコード化しない（D-06 の明示的な判断）が、`28-VERIFICATION.md` にこのセッションで採取した生ログをベースラインとして貼り、フェーズ完了時に再実行した結果と目視で比較する。

## SC#4 Invariant Verification Commands（D-07、このセッションで実行・出力確認済み）

**Base ref: `main` ブランチ**（`v0.6.2` タグではない）。`git merge-base main HEAD` = `main` そのもの（`9f8e07531555ae5c20647ee204c73fbf57a8eda8`）— つまり HEAD は `main` から分岐したフェーズブランチであり、`main` は `v0.6.2` タグより 3 コミット先（依存更新 + STATE.md 整理のみ、`typsphinx/` は無関係）。`main..HEAD` には Phase 24〜27.1 の全 114 コミットが含まれる。28-CONTEXT.md の canonical_refs も `git diff main..HEAD` を指示しており、これに一致する。

### 1. 新規ランタイム依存ゼロ

```bash
git diff main..HEAD -- pyproject.toml
```
**実測: 出力なし（完全に空）。** `dependencies = [...]` を含むファイル全体が `main` とバイト同一。

### 2. `@preview` 未バンプ

```bash
git diff main..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ | grep -E '^[+-].*@preview'
```
**実測: 出力なし（exit 1 = マッチなし）。** `@preview` 4 パッケージの版文字列（`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`）は `writer.py` と `template_engine.py` と `base.typ` の 3 箇所すべてで一致・未変更。

```bash
uv run python -m pytest tests/test_preview_version_sync.py -v
```
フルスイート実行（上記）に含まれ green を確認済み。

### 3. `base.typ` の差分が `lang` パラメータとその配線に限定されていること

```bash
git diff main..HEAD -- typsphinx/templates/base.typ
```
**実測、完全な出力（2 行の差分のみ）:**
```diff
diff --git a/typsphinx/templates/base.typ b/typsphinx/templates/base.typ
index fd39a5a..1442ad5 100644
--- a/typsphinx/templates/base.typ
+++ b/typsphinx/templates/base.typ
@@ -45,6 +45,7 @@
   toctree_caption: "Contents",
   papersize: "a4",
   fontsize: 11pt,
+  lang: "en",
   body
 ) = {
   // Document metadata
@@ -58,7 +59,7 @@
   )
 
   // Text setup
-  set text(size: fontsize, lang: "en")
+  set text(size: fontsize, lang: lang)
   // Heading setup
```
ROADMAP の「2026-07-25 の不変量改訂」の記述と完全一致。追加行 1 行・変更行 1 行のみで、SC#4 が要求する「`lang` パラメータとその配線に限定」を満たしている。

### 4. `uv.lock` の差分

```bash
git diff main..HEAD -- uv.lock
```
**実測: 出力なし（完全に空)。** 版バンプ前の現時点で既に `uv.lock` は `main` とバイト同一 — 依存の transitive drift も一切ない、クリーンな状態からの版バンプ作業になる。

## `uv.lock` Regeneration（Claude's Discretion）

### 現在の状態（実測）

`uv.lock` の `typsphinx` 自己エントリ:
```
[[package]]
name = "typsphinx"
version = "0.6.2"
source = { editable = "." }
dependencies = [
    { name = "docutils" },
    { name = "sphinx" },
    { name = "typst" },
]
```
`pyproject.toml:7` を `0.6.3` に変更しても、このセルフエントリは自動追随しない（`uv.lock` は解決済みスナップショットのため、明示的な `uv lock` 実行が必要）— Phase 23 の pitfall と同一構造。

### `uv lock` vs `uv sync` — 推奨（Phase 23 と同じ判断、このセッションで再確認）

```bash
uv lock
uv sync --extra dev --locked
```

- `uv lock` は `uv.lock` のみを書き換える最小限のコマンド（環境の変更はしない）。
- `uv sync --extra dev --locked` は SC#1 が要求する受入基準そのもの — ドリフトがあれば黙って再ロックせず、失敗で知らせる。
- **実測: `uv sync --extra dev --locked` は現時点（版バンプ前）で既に exit 0。** `--extra docs` を付けずに実行すると `furo`/`sphinx-autodoc-typehints`/`sphinx-intl`/`accessible-pygments`/`beautifulsoup4`/`soupsieve`/`sphinx-basic-ng` の 7 パッケージがアンインストールされる副作用が観測された（`docs` extras が `--extra` 指定されないため）。**これは SC#1 の合否には影響しない**（SC#1 は `--locked` の exit code のみを見る）が、docs ビルド証跡（D-05）を同じセッションで採取する executor は `--extra docs` も付けて sync するか、docs ビルド証跡採取を `uv sync --extra dev --extra docs` の直後に行う順序に注意すること。
- `uv` バージョン: `0.11.25`（このセッションで確認）。ネットワークアクセスの要否: このセッションでは `pyproject.toml` を実際に変更していないため `uv lock` 自体は未実行だが、依存範囲に変更がない単純な自己バージョン更新であれば `uv lock` はローカルの既存解決結果を再利用でき、新規にネットワークへ問い合わせる必要は薄い（Phase 23 でも同種の操作がオフライン相当で完了した記録がある）。ネットワークが使えない場合の代替として `uv lock --offline` が候補になるが、`typsphinx` の自己エントリのバージョン更新のみであれば通常の `uv lock` で十分と見込まれる。

### 期待される diff の形

「版バンプのみ」という単純な変更なので、`uv.lock` の diff は次の形が期待値:
- `typsphinx` セルフエントリの `version = "0.6.2"` → `"0.6.3"`（必須）。
- lockfile 自体の `revision` メタデータカウンタの化粧的な増分（あれば、依存変更ではない）。
- **もし transitive 依存の解決バージョンが変わっていたら**（PyPI 上の互換パッチリリースの出現による偶発的なドリフト）、それは SC#4 の対象外（SC#4 は typsphinx 自身の宣言済みランタイム依存と `@preview` 版のみを問題にする）— SUMMARY に記録はするが、ブロッキングとしては扱わない。もし直接依存（`sphinx`/`docutils`/`typst` の範囲指定）が変わっていたら、それは SC#4 違反として停止すべき兆候。

## Common Pitfalls

### Pitfall 1: コーパスゲートの `SKIPPED` を許容できる証跡として貼ってしまう

**何が起きるか:** `pytest -m slow` の実行結果を、実際に走ったか静かに skip したかを確認せずに `28-VERIFICATION.md` に貼ってしまう。
**なぜ起きるか:** 両方とも exit 0 で `1 <passed|skipped> in N.NNs` と表示され、目視でうっかり見過ごしやすい。
**どう防ぐか:** 必ず `-rs`（skip 理由を summary に強制表示）付きで実行し、summary 行に文字どおり `passed` があることを確認してから記録する（D-12）。**さらに本フェーズ固有の注意:** フルスイート実行時に出る `1 skipped` は `tests/test_corpus_gate.py` の**別のテスト**（`test_empty_url_before_after`、`TYPSPHINX_CORPUS_REPORT` env-gated）由来であり、SC#3 のコーパスゲート本体（`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`）とは無関係。この 2 つを混同して「コーパスゲートがまた skip した」と誤読しないこと — SC#3 の証跡には `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` を単独で `-m slow -rs -v` 実行した結果を使う。
**警告サイン:** 不自然に速い実行（skip は瞬時、実ビルドは十数秒かかる）。

### Pitfall 2: `uv.lock` 自身の埋め込み版リテラルを忘れる

**何が起きるか:** `pyproject.toml:7` をバンプした後、`uv.lock` に埋め込まれた `typsphinx` 自己エントリの `version` も自動更新されると思い込み、`uv lock` 実行を省略する。
**なぜ起きるか:** 通常の依存バンプは `pyproject.toml` だけを触ればよいため、自己参照パッケージの自己ピンという特殊ケースを見落としやすい。
**どう防ぐか:** `pyproject.toml` 編集の直後、`uv sync --locked` を試す前に必ず `uv lock` を実行する。

### Pitfall 3: `docs-multilang` の 4 行基準を `docs-pdf` にもそのまま適用してしまう

**何が起きるか:** D-06 の「4 行」を両方の tox 環境の共通基準だと誤解し、`docs-pdf`（英語のみ）の 2 行という実測値を「規定より少ないから問題」あるいは逆に「4 行まで許容範囲」と誤判定する。
**なぜ起きるか:** CONTEXT.md の「4 行」という単一の数字だけが引用されており、どちらの tox 環境の値かが明示されていない。
**どう防ぐか:** 本 RESEARCH.md の「Docs Build Baseline」節が実測した通り、`docs-pdf` は 2 行、`docs-multilang` は 4 行（2 言語 × 2 行）という**別々の基準**を使う。

### Pitfall 4: D-01/D-02/D-03 の BREAKING 非対称性を「整合させよう」としてしまう

**何が起きるか:** CONF-05（実害なしの設定削除）と CONF-04（実害ありの fail-loud 化）の両方に BREAKING を立て、CONF-07（実際に出力が変わる lang 連動バグ修正）には立てないという配分を、executor が「一貫性がない」と感じて揃えようとする。
**なぜ起きるか:** 一見すると CONF-07 の方が実際の出力変化が大きいのに BREAKING が立たない逆転に見える。
**どう防ぐか:** これは Phase 23 の D-05（CONF-01）/D-07（Issue #117）と同じ構造の、オーナーが意図的に選んだ非対称性。CONTEXT.md 自身が「プランはこの配分を維持すること（勝手に揃えない）」と明記している。「設定名の削除・破壊的な fail-loud 化 = 公開 API の変化としての BREAKING」対「バグ修正としての振る舞い訂正 = BREAKING ではない」という一貫した基準で読む。

### Pitfall 5: `docs` extras なしで docs ビルド証跡を採ろうとして失敗する

**何が起きるか:** `uv sync --extra dev`（`docs` extras なし）の状態で直接 `sphinx-build -b typstpdf ...` を実行し、`furo` テーマ等が欠けてビルドが失敗する。
**なぜ起きるか:** `pyproject.toml` の `docs` extras（`furo`/`sphinx-autodoc-typehints`/`sphinx-intl`）は `dev` extras とは独立したグループであり、`--extra dev` だけでは入らない。
**どう防ぐか:** `tox -e docs-pdf` / `tox -e docs-multilang` は `extras = docs` を宣言しているため tox 経由なら自動解決される（このセッションで実測動作確認済み）。手動で `sphinx-build` を叩く場合は事前に `uv sync --extra dev --extra docs` を実行すること。

### Pitfall 6: `build_multilang.py` が `subprocess.run(["sphinx-build", ...])` を直接呼ぶことによる NixOS ELF 実行ハザード

**何が起きるか:** `docs/build_multilang.py` は `sys.executable -m sphinx` パターンではなく、PATH 上の `sphinx-build` バイナリを直接 `subprocess.run` で呼ぶ実装になっている。NixOS サンドボックスが「on」の状態でこのスクリプトを `uv run python build_multilang.py` 経由以外（例えば worktree 内で venv の activate が不完全な状態）で呼ぶと、プロジェクトメモリが記録する「コンパイル済みバイナリの ELF 実行に失敗する」ハザードに当たる可能性がある。
**なぜ起きるか:** `sys.executable -m sphinx` の形（このプロジェクトの他のテストヘルパーが採用している回避パターン）ではなく、PATH 解決に依存した `subprocess.run(["sphinx-build", ...])` になっている。
**どう防ぐか:** このセッションでは `uv run tox -e docs-multilang` 経由で実行し、問題なく完走した（サンドボックスが lifted されている、またはこの呼び出し形が現在の環境では問題にならない状態）。executor は実行前にサンドボックス状態を確認し、もし ELF 実行エラーに遭遇したら `nix-shell` 経由の代替手段を検討する（本フェーズのスコープでは `build_multilang.py` 自体の書き換えは対象外 — 発見事項として記録するに留める）。

## Code Examples

### 推奨 `[0.6.3]` CHANGELOG エントリ（ドラフト、ほぼそのまま使用可能）

```markdown
## [0.6.3] - 2026-07-25

Closes out the config & docs fidelity milestone: configuration values documented in `typst_elements`
now reliably reach the compiled Typst output (an unrecognized key now fails the build loudly instead
of being silently dropped, and a second long-dead config value is removed), captioned tables render
as native Typst figures with "Table N" numbering and resolvable cross-references, and the Typst
typesetting language of every auto-generated label now follows Sphinx's own `language` setting
instead of being hardcoded to English. The user-facing configuration docs were also corrected to
match the registered config surface. Zero new runtime dependencies; the bundled `@preview`
version-sync surface is untouched.

### Added

- **Captioned tables render as numbered, cross-referenceable figures (TBL-01, TBL-02)** — a
  `.. table:: Caption` (or a captioned `csv-table`/`list-table`) now emits
  `figure(table(...), caption: {...}, kind: table)` with Typst's native "Table N" numbering, instead
  of a bare `table()` with no numbering and a stray preceding heading. A `:numref:`/`:ref:` to a
  captioned table now resolves to a working cross-reference in the compiled PDF. A table without a
  caption still renders as a plain `table()` (never speculatively figure-wrapped).

### Changed

- **BREAKING: An unrecognized `typst_elements` key now fails the build (CONF-04)** — previously, any
  `typst_elements` key outside `papersize`/`fontsize`/`lang` was silently dropped with no effect on
  the build; it now aborts with `ExtensionError: typst_elements: unknown key ...`. If your `conf.py`
  sets a key outside this allowlist, remove it; to keep passing a custom value through to a custom
  template, use `typst_template_function.params` instead. `papersize` and `fontsize` set via
  `typst_elements` now also reach the compiled `.typ`/PDF (previously silently dropped regardless of
  the allowlist).

### Removed

- **BREAKING: `typst_toctree_defaults` config value removed (CONF-05)** — it was registered but never
  consumed by any code path. A `conf.py` still setting it is silently ignored by Sphinx (unregistered
  config values produce no warning), and removal changes no build's output since the value never
  affected one. No deprecation period.

### Fixed

- **Typst's typesetting language now follows Sphinx's `language` config (CONF-07)** —
  `templates/base.typ` previously hardcoded `lang: "en"`, so a `language = "ja"` project's body text
  was already translated (Sphinx's own i18n transform) but Typst-generated labels stayed English —
  e.g. a captioned table showed "Table 1" instead of "表 1". The default template now derives `lang`
  from `config.language`; an explicit `typst_elements = {"lang": ...}` still overrides it on every
  path. Applies to the default-template path only — a custom template, `typst_package`, or a
  source-directory `base.typ` shadow is unaffected and must still declare its own `lang`.
- **User-facing configuration docs corrected to match the registered config surface (DOC-07)** —
  `docs/source/user_guide/configuration.rst`'s `typst_author` renamed to the real `typst_authors`, the
  non-existent `typst_use_codly`/`typst_code_line_numbers` removed, and `typst_papersize`/
  `typst_fontsize` rewritten as working `typst_elements` examples; `docs/source/api/index.rst`'s
  redundant, drifted "Available Configuration Values" table removed in favor of a single canonical
  `:doc:` pointer.

### Verified

- Closing full-corpus regression gate: the Sphinx `doc/` v9.1.0 corpus, re-run through `-b typstpdf`,
  remains fatal-free, produces a valid `%PDF`-magic-byte output, and the `unknown_visit` catalogue
  remains empty.
- Milestone invariant held (as amended 2026-07-25): zero new runtime dependencies, no `@preview`
  package version bump, the 3-way version-sync surface (`writer.py` / `template_engine.py` /
  `templates/base.typ`) untouched by version string; `templates/base.typ`'s only diff from `main` is
  the 2-line `lang` parameter added in Phase 27.1.
```

*(D-11 により、フル pytest スイートと docs ビルドの証跡は `28-VERIFICATION.md` 側に置き、CHANGELOG 本文には書かない。)*

### リンクブロックの Before → After（ファイル末尾）

**Before（実測、現状）:**
```
[0.6.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
[0.6.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.1
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.2...HEAD
```

**After（本フェーズが作る差分）:**
```
[0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3
[0.6.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
[0.6.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.1
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.3...HEAD
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Phase 23 は `[Unreleased]` リンクブロックの繰り上げを当初スコープ外とし、レビュー指摘を受けて後追いで追加した（override 扱い） | Phase 28 の ROADMAP SC#2 はこれを最初から本フェーズの仕事として明記している | 本フェーズの計画時点 | プランは最初のプランからリンクブロック更新を含めてよく、Phase 23 のような「後追い override」を経由する必要がない |
| `[0.6.2]` の CHANGELOG 節順は Removed → Fixed → Verified（KaC 語彙順そのものではない） | 本フェーズは Added/Changed/Removed/Fixed が全部揃うため、KaC 語彙順（Added → Changed → Removed → Fixed → Verified）に近い並びを推奨 | 本フェーズの CHANGELOG ドラフト | `[0.6.1]` の並びにより近い形になる（Claude's Discretion の範囲内） |

既存の project convention から外れた/非推奨のツールは特定されなかった — 本フェーズはプロジェクトの確立済みパターンを一貫して再利用する。

## Assumptions Log

本セッションのすべての事実は次のいずれかで直接確認済み: リポジトリ内ファイルの直接読み取り（`grep`/`Read`）、実際に実行したコマンドの出力（`git diff`, `git log`, `uv sync`, `uv run pytest`, `uv run tox`）。`[ASSUMED]` タグの付いた主張はない。

**このテーブルは空 — プラン前のユーザー確認は不要。**

## Open Questions

1. **CHANGELOG のセクション順序（Added を先頭に置くか、[0.6.2] と同じ Removed 先頭にするか）**
   - What we know: CONTEXT.md はセクション順序を明示的にロックしていない（Claude's Discretion の一部として「各項目の具体的な文面」は裁量とされているが、セクションの並び順自体への直接の言及はない）。
   - What's unclear: `[0.6.1]` の Added→Changed→Fixed→Verified 順と `[0.6.2]` の Removed→Fixed→Verified 順、どちらの precedent により忠実であるべきか。
   - Recommendation: 本フェーズは Added/Changed/Removed/Fixed の 4 種すべてが揃う最初のケースなので、Keep a Changelog の標準語彙順（Added, Changed, Deprecated, Removed, Fixed, Security）にもっとも忠実な `[0.6.1]` 型（Added→Changed→Removed→Fixed→Verified）を推奨する。最終判断は Claude's Discretion の範囲内でプランナーが決めてよい。

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+（実測: pytest-9.1.1 がこのセッションで動作、`pyproject.toml` `dev` extras `pytest>=8.4,<10`） |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`（`addopts = "-v --strict-markers"`、`slow`/`integration` マーカー登録済み） |
| Quick run command | `uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v`（サブ秒、ネットワーク/実コンパイル無し） |
| Full suite / phase gate command | `uv run python -m pytest -q -rs`（実測 656 passed, 1 skipped in 56.64s、slow マーカー込み） |

### Phase Requirements → Test Map

本フェーズは要件 ID を持たない（release/close phase）ため、通常の要件→テスト対応表の代わりに、本フェーズ自身の成果物とテストの対応を示す:

| Deliverable | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| `pyproject.toml`/`README.md` 版同期 | 両ファイルが同じ版を名乗る | unit | `uv run python -m pytest tests/test_readme_version_sync.py -v` | ✅ 既存（Phase 23 で新設済み） |
| `uv.lock` の正しい再生成 | バンプ後に `uv sync --locked` が成功する | other（CLI 実行、pytest ではない） | `uv sync --extra dev --locked` | N/A — SC#1 自体の受入基準、pytest テストではない |
| SC#3 フルコーパス回帰ゲート | コーパスが fatal-free でコンパイルされ、`unknown_visit` が空 | integration（slow, 実コンパイル） | `uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s` | ✅ 既存（`tests/test_corpus_gate.py`） |
| SC#4 マイルストーン不変量（`@preview` 未バンプ） | 4 パッケージ/3 ファイルの版一致が引き続き成立 | unit | `uv run python -m pytest tests/test_preview_version_sync.py -v` | ✅ 既存 |
| SC#4 マイルストーン不変量（新規ランタイム依存ゼロ） | `pyproject.toml` の `dependencies` 配列が版リテラル以外で未変更 | other（`git diff`、pytest ではない） | `git diff main..HEAD -- pyproject.toml`（手動目視） | N/A — assert するテストは存在しない。手動 diff 読みが検証手段 |
| docs ビルド警告のベースライン維持（D-05/D-06） | フェーズ前ベースラインから警告が増えていない | other（tox 実行、pytest ではない） | `uv run tox -e docs-pdf` / `uv run tox -e docs-multilang`（生ログを目視比較） | N/A — D-06 により行数を assert するテストは意図的に作らない |

### Sampling Rate

- **タスクコミットごと:** `uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v`（サブ秒、ネットワーク不要）。
- **wave マージ / フェーズゲートごと:** 上記フルコーパスゲートコマンド（実測 ~13s、実コンパイル、キャッシュ済みコーパスでオフライン）+ フル pytest スイート（実測 ~57s）+ 2 つの tox docs ビルド（実測、docs-pdf ~3s、docs-multilang ~6s）。
- **フェーズゲート:** フルコーパスゲートが green（`1 passed`、`1 skipped` ではない）であり、フルスイートが `656 passed（またはそれ以上）/ 0 failed` であり、docs ビルド警告がそれぞれのベースライン（2 行/4 行）を超えて増えていないことを `/gsd-verify-work` の前に確認する。

### Wave 0 Gaps

**なし。** 本フェーズが必要とするすべてのテスト資産（`tests/test_readme_version_sync.py`、`tests/test_preview_version_sync.py`、`tests/test_corpus_gate.py`）は既に存在し、このセッションで green であることを直接確認済み。新規フィクスチャ・新規フレームワークインストールは不要。

## Security Domain

**`security_enforcement` は on（`.planning/config.json`）だが、本フェーズには評価すべき攻撃面の変化がない。** 触るのは版リテラルの文字列、CHANGELOG の markdown、README の 1 行、ロックファイルの再生成のみ — ユーザー入力なし、新規ネットワーク呼び出しなし（コーパスゲートの既にキャッシュ済みクローンチェックのみ）、認証/セッション/アクセス制御面なし、暗号なし。新規のテストコードも本フェーズでは作成しない（既存テスト資産の再利用のみ）。

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A — 認証面に触れない |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No（リポジトリローカルの固定パスファイルを読むだけ、ユーザー/ネットワーク入力ではない） | N/A |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| `uv lock` によるピン外の transitive 依存バンプの混入 | Tampering（低関連度） | `pyproject.toml` の直接依存は既存の `>=X,<Y` レンジピンで保護されており、本フェーズはそのレンジを変更しない。`uv.lock` の diff を目視確認する（上記「期待される diff の形」）ことが対応する検証手段であり、新しいセキュリティ管理は不要 |

本フェーズが新規に導入する脅威はない。Security Domain セクションは config デフォルトにより含めているが、意味のあるリスク面ではない。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | 版バンプ / ロックファイル再生成（SC#1） | ✓ | 0.11.25（実測） | — |
| `git` ブランチ `main` | SC#4 不変量 diff の base ref | ✓ | `main` = `9f8e075`、実測で merge-base(main, HEAD) = main と確認済み | — |
| キャッシュ済み Sphinx `doc/` コーパス | SC#3 回帰ゲート（D-05） | ✓ | `sphinx-v9.1.0`（実測、`1 passed in 13.08s` でオフライン実行確認済み） | キャッシュが無ければネットワーク経由の浅いクローンにフォールバック（今回は不要、キャッシュヒット確認済み） |
| `typst`（typst-py） | 実コンパイルのコーパスゲート | ✓ | コアランタイム依存、`pyproject.toml` 制約 `>=0.15.0,<0.16` | — |
| `tomllib`（stdlib） | 既存の版同期テスト | ✓ | Python 3.13.13（このセッションの venv 実測）、stdlib since 3.12、フロアは既に `>=3.12` | — |
| `docs` extras（`furo`/`sphinx-autodoc-typehints`/`sphinx-intl` 等） | docs ビルド証跡（D-05） | ✓（`uv sync --extra dev --extra docs` で確認済み） | `furo==2025.12.19` ほか（実測） | `tox -e docs-pdf`/`docs-multilang` は `extras = docs` を自動解決するため手動 sync 不要 |
| ネットワークアクセス（GitHub） | コーパスキャッシュが無い場合のみ | 今回のセッションでは不要（キャッシュヒット確認済み） | — | 再クローンが必要な場合のみ要求される。今回は懸念不要と確認済み |

**フォールバックのない欠落依存:** なし。

**フォールバックのある欠落依存:** なし — 本フェーズが必要とするすべての依存は、このセッションで存在・動作を確認済み。

## Sources

### Primary (HIGH confidence — このセッションで直接読み取り/実行)

- `.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-CONTEXT.md` — 全 12 ロック決定（D-01〜D-12）、canonical references、実測事実テーブル
- `.planning/REQUIREMENTS.md` — v1 要件 7 件全量、トレーサビリティ表
- `.planning/STATE.md` — ロードマップ要約、マイルストーン不変量、フェーズ完了記録
- `.planning/PROJECT.md` — Phase 24〜27.1 の Validated エントリ（CHANGELOG 素材の一次記録）
- `.planning/ROADMAP.md` §Phase 28 — SC#1〜SC#5、`Invariant amendment (2026-07-25, owner decision)`
- `.planning/milestones/v0.6.2-phases/23-v0-6-2-release-prep-regression-gate-close/23-RESEARCH.md`、`23-01-PLAN.md`、`23-VERIFICATION.md` — 同型フェーズの直接の先例（型紙・実行順序・pitfall・verify 手法すべて）
- `CHANGELOG.md` — 全文読了。構造テンプレート、`[0.6.2]` の節構成、BREAKING 書式、末尾リンクブロックの現状
- `README.md` — 305〜317 行目の直接読み取り。Status 行、フッタ、依存下限の位置
- `tests/test_readme_version_sync.py` — 全文読了。README↔pyproject 同期ガードの実装と対象範囲
- `tests/test_corpus_gate.py` — `grep` で構造確認（`TestCorpusRenderGate` クラスと独立の env-gated `test_empty_url_before_after` の存在）
- `pyproject.toml` — 版リテラル位置、`dependencies`/`optional-dependencies`（`dev`/`docs`）の内容
- `uv.lock` — `typsphinx` セルフエントリの直接確認
- `tox.ini` — `docs-pdf`/`docs-multilang`/`docs-html`/`docs` env の定義（`extras = docs`）
- `typsphinx/translator.py` — `visit_toctree` docstring 内容（docs ビルド警告の根本原因確認）
- `docs/build_multilang.py` — `subprocess.run(["sphinx-build", ...])` の実装確認
- `/home/yuta/.claude/projects/-home-yuta-Documents-typsphinx/memory/nixos-sandbox-test-env.md` — 全文読了、環境依存失敗パターンとの照合
- `git diff main..HEAD -- pyproject.toml/uv.lock/typsphinx/templates/base.typ/typsphinx/writer.py/typsphinx/template_engine.py`、`git log --oneline`、`git merge-base`、`git tag -l` — すべてこのセッションで実行
- `uv sync --extra dev [--extra docs] [--locked]`、`uv --version` — すべてこのセッションで実行
- `uv run python -m pytest -q -rs`、`uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s` — すべてこのセッションで実行、生ログをそのまま引用
- `uv run tox -e docs-pdf`、`uv run tox -e docs-multilang` — すべてこのセッションで実行、生ログをそのまま引用

### Secondary (MEDIUM confidence)

なし — 本セッションのすべての主張はリポジトリまたはローカル実行コマンドで直接検証可能であり、Web 検索は不要だった（research-focus の指示どおり、本フェーズはリポジトリ内で完結する）。

### Tertiary (LOW confidence)

なし。

## Metadata

**Confidence breakdown:**

- CHANGELOG 要件カバレッジマッピング（D-09/D-10）: HIGH — 7 要件それぞれを `.planning/REQUIREMENTS.md` と `.planning/PROJECT.md` の一次記録に突き合わせ、5 ブレットへの束ね方を確認。ゼロドロップ。
- CHANGELOG 構造テンプレート: HIGH — ファイル全文読了。見出しレベル、節順序、BREAKING/Removed の過去使用例はすべて直接観測（推測ではない）。
- コーパスゲート実行機構: HIGH — このセッションで実際にコマンドを実行し、`1 passed in 13.08s` の生ログを直接取得。
- docs ビルドベースライン（D-06）: HIGH — `docs-pdf`/`docs-multilang` 両方を `uv run tox` 経由でこのセッションで実際に実行し、2 行/4 行という別々の基準を実測で確認（CONTEXT.md の「4 行」という単一値の曖昧さを解消した独自の研究成果）。
- SC#4 不変量確認コマンド: HIGH — base ref（`main`）の存在と merge-base 関係を直接確認済み。すべてのコマンドが実際に実行され、出力（空・2 行）をそのまま引用。
- `uv.lock` 再生成: HIGH — セルフエントリの版リテラルを直接観測。`uv sync --extra dev --locked` の現状 exit 0 と副作用（docs extras のアンインストール）を実測確認。

**Research date:** 2026-07-25
**Valid until:** 構造的な主張（CHANGELOG テンプレート、要件マッピング）は実質無期限有効（本フェーズは既に出荷済みの過去の変更をドキュメント化するクローズドなフェーズのため）。環境依存の主張（コーパスキャッシュ、`uv` バージョン、`main` の位置、NixOS サンドボックスの lifted 状態）は、計画が数日以上遅延する場合は再確認を推奨（環境状態依存の主張に対する標準的な 7〜30 日ガイダンスに従う）。特に NixOS サンドボックスの lifted/on 状態は過去のセッション間で変動が記録されているため、executor は実行前に自分のセッションでの状態を確認すること。
