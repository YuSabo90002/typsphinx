# Phase 28: v0.6.3 Release Prep + Regression-Gate Close - Context

**Gathered:** 2026-07-25
**Status:** Ready for planning

<domain>
## Phase Boundary

v0.6.3 のリリース**準備**と、フルコーパス回帰ゲートによるマイルストーンの締め。
版バンプ、`CHANGELOG.md` の `[0.6.3]` エントリのキュレーション、`README.md` の Status 行同期、
既存ゲートの実走とその証跡記録まで。**publish は行わない。**

**In scope:**

- `pyproject.toml:7` の `version = "0.6.2"` → `"0.6.3"`（実測上これが唯一の版リテラル。
  `typsphinx/__init__.py` は `importlib.metadata` 由来なので対象外）
- `uv.lock` の再生成（`uv sync --locked` が緑になること）
- `README.md:315` の `**Status**: Stable (v0.6.2) - Production ready` → `v0.6.3`
  （Phase 23 D-13 で新設した `tests/test_readme_version_sync.py` が両者の一致を assert するので、
  片方だけ変えるとスイートが赤くなる）
- `CHANGELOG.md` の `## [0.6.3]` エントリ新設 + `## [Unreleased]` compare リンクの繰り上げ +
  `[0.6.3]` の releases/tag リンク行の追加（ROADMAP SC#2 が release-prep 自身の仕事として明記）
- `tests/test_corpus_gate.py` のフルコーパス実走と証跡の `28-VERIFICATION.md` への記録
- フル pytest スイートと docs ビルド（`docs-multilang` / `docs-pdf`）の緑の記録（D-05）
- マイルストーン不変量 SC#4（改訂版）の確認 — 新規ランタイム依存ゼロ / `@preview` 未バンプ /
  `base.typ` の差分が `lang` パラメータとその配線に限定されていること

**Out of scope:**

- **publish 一切**（`git tag v0.6.3`、`release.yml` 起動、PyPI、GitHub Release、マージ）
  → `/gsd-complete-milestone`（ROADMAP SC#5 のスコープ柵は絶対）
- `typsphinx/` 配下の振る舞い変更（機能修正は Phase 24〜27.1 で完了済み。本フェーズは
  `typsphinx/` を一行も触らない）
- `docs/` の記述変更（D-04 — アップグレード手順は CHANGELOG 本文に留め、docs は触らない。
  触ると ja `.po` の gettext 追従が付随するため）
- `examples/` の修正（討議領域として提示したがオーナー未選択。Deferred 参照）
- 版番号そのものの見直し（0.7.0 案）— ROADMAP SC#1 が 0.6.3 に固定。Phase 23 D-08 で
  同型の提案が明示的に不採用済み
- `CHANGELOG.md` の過去バージョンエントリの改変（履歴）

</domain>

<decisions>
## Implementation Decisions

### CHANGELOG `[0.6.3]` の BREAKING 判定

- **D-01: CONF-05（`typst_toctree_defaults` 削除）は `### Removed` に置き BREAKING ラベルを立てる。**
  Phase 23 D-05（オーナー裁定 2026-07-23、「公開されていた設定名の削除は実害の有無に関わらず
  仕様上破壊的」）の踏襲。本文には v0.6.2 の CONF-01 項目と同じ形で実測の但し書きを添える —
  削除後も `conf.py` に残っていれば Sphinx は**警告すら出さず無音で無視して `build succeeded`**、
  かつ削除前から出力に一切効いていない dead config なので実際の振る舞いは変わらない。

- **D-02: CONF-04 の未知キー fail-loud にも BREAKING ラベルを立て、`### Changed` に置く。**
  こちらは実害のある本物の破壊的変更 — Phase 26 以前は `map_parameters()` が
  `DEFAULT_PARAMETER_MAPPING` の 3 キー（project/author/release）以外の `typst_elements` キーを
  黙って捨てていたのに対し、現在は `ELEMENTS_ALLOWLIST`（`papersize`/`fontsize`/`lang`）外の
  キーが 1 つでもあれば `ExtensionError: typst_elements: unknown key ...` でビルドが中断する。
  飾りのキーを入れていたユーザーは `conf.py` を一切触らずに緑→硬失敗に変わる。
  本文に対処手順を書く（D-04）。

- **D-03: CONF-07（lang 連動）は `### Fixed` に置き、BREAKING は立てない。**
  「`base.typ` が組版言語を `lang: "en"` でハードコードしていたバグの修正」という位置づけで、
  Phase 23 D-07（Issue #117 の出力ファイル名変更を「本来そうすべきだったものの修正」として
  BREAKING にしなかった裁定）と同じ基準。本文で before/after を示す — `language = "ja"` の
  プロジェクトが既定テンプレートで "Table 1"/"Figure 1" →「表 1」「図 1」になる。
  適用範囲も本文に書くこと（自動導出は既定テンプレート経路のみ。カスタムテンプレート /
  `typst_package` / srcdir シャドウの 3 経路には注入されない）。

- **D-04: アップグレード対処手順は CHANGELOG 本文にのみ書く。docs は触らない。**
  D-02 の BREAKING 項目内に 1〜2 行で「allowlist 外のキーは削除する。値を渡し続けたい場合は
  `typst_template_function.params` を使う」と書く。`docs/source/user_guide/configuration.rst` は
  Phase 27/27.1 で既に 3 キー体制と `typst_template_function.params` の逃げ道を記述済みであり、
  アップグレード向けの追記のためだけに docs を開くと ja `.po` の gettext 追従と docs ビルドの
  再確認が付随する。本フェーズが触るファイルは `pyproject.toml` / `uv.lock` / `CHANGELOG.md` /
  `README.md` の 4 つに留める（Phase 23 と同じ形）。

### 回帰ゲートと証跡の範囲

- **D-05: SC#3 の証跡は「コーパスゲート + フル pytest スイート + docs ビルド」の 3 点を `28-VERIFICATION.md` に記録する。**
  Phase 23 D-09/D-12 のコーパスゲート単独から範囲を広げる。
  根拠: 本マイルストーンは `base.typ` の `project()` 署名・テンプレート解決経路・docs を触っており、
  Phase 27.1 では executor が worktree 内から docs ビルド警告を観測できず、マージ後に警告 5 行の
  増加が発覚して後追い修正した実績がある（現在はフェーズ前ベースラインの 4 行に復帰済み）。
  - コーパスゲート: `pytest -m slow -rs`（skip 理由を強制表示）で `tests/test_corpus_gate.py` を
    実走し、`1 passed`（`skipped` ではない）と読める生ログを貼る — Phase 23 D-12 の踏襲。
    コーパス入手不能時に `pytest.skip` する仕様なので「緑」が「スキップ」を意味し得る。
  - フルスイート: 実 `typst.compile()` の GATE-01 フィクスチャ群を含む全体の緑
    （Phase 27.1 時点で 656 passed / 1 skipped / 0 failed）。
  - docs ビルド: `tox -e docs-multilang` と `tox -e docs-pdf`。

- **D-06: docs ビルドの合否基準は Claude 裁量。** 既定は「フェーズ前ベースライン（既知の 4 行、
  既存 `translator.py` 由来警告を含む。ゼロではない）から警告が増えていないこと」で、実際の
  警告行を `28-VERIFICATION.md` にそのまま貼る。行数の厳密一致を assert するテストは作らない
  （テスト基盤の拡張はリリース準備のスコープ外 — Phase 23 D-12 と同じ判断）。ベースラインを
  どのコミットで測るかもプラン時に決めてよい。

- **D-07: SC#4 の確認は `git diff` の実出力を `28-VERIFICATION.md` に貼り、既存テストの緑をもって足りるとする。**
  実測済み: `git diff main..HEAD -- typsphinx/templates/base.typ` は正確に 2 行
  （`project()` への `lang: "en",` 追加と `set text(size: fontsize, lang: lang)` への変更）だけ、
  `@preview` 4 パッケージの版文字列は未変更、`pyproject.toml` の依存も差分ゼロ。
  `tests/test_preview_version_sync.py` の緑が 3-way 同期面の担保。追加実装ゼロ。
  `base.typ` の sha256 を新しい基準値として記録する案は採らない（以降のフェーズが `base.typ` を
  意図的に変えるたび更新が必要になるため）。

- **D-08: ja の PDF での目視確認は行わない。** 実測: `tox -e docs-pdf` が作る PDF は英語
  （`docs/source` の conf に `language` 設定なし）、`docs-multilang` は en/ja とも **HTML のみ**。
  つまり「ja の PDF で『表 N』が出る」はどの tox 環境でも目に見えない。Phase 27.1 の GATE-01
  フィクスチャ（ja の `.typ` ソース証明 + de の PDF 抽出、計 21 テスト）がこれを機械的に固めており、
  それがフルスイート（D-05）の一部として回る。手作業の目視確認は再現性が低く、「検証機構を
  持てない事実は残さない」という Phase 22.4 以来の原則にも合わない。

### CHANGELOG の粒度と構成

- **D-09: 項目化の単位はユーザー可視の変化。** 7 要件を 1 対 1 で列挙せず、Phase 23 D-01 の原則
  （読み手はユーザーで要件 ID を知らない。末尾の括弧に ID を並べて追跡性を保つ）を適用する。
  TBL-01/TBL-02 は「キャプション付きテーブルが番号付き Table N になり相互参照できる」として
  1 項目に束ねる。CONF-04 / CONF-05 / CONF-07 はそれぞれ節が違うので別項目。結果は 5 項目前後。

- **D-10: docs 系は DOC-07 のみ載せる。DOC-06 は載せない。** 可視性が非対称であるため —
  DOC-07（`user_guide/configuration.rst` の phantom 設定名 5 個の削除・`typst_elements` の動く例への
  書き換え、`api/index.rst` の重複表の削除）は公開ドキュメントサイトの記述が変わるのでユーザーに
  可視で、Phase 23 D-03/D-04 の「誤情報の訂正は `### Fixed` に載せる」に該当する。
  DOC-06（孤児 `docs/configuration.rst` の削除）はどの toctree からも到達不能で、ユーザーの目には
  元々入っていない内部整理。**結果として台帳 7 件のうち DOC-06 だけが CHANGELOG に現れない** —
  これは意図的な選択であり、プランが「全要件を漏れなく列挙」を理由に足し戻さないこと。

- **D-11: `### Verified` 節は先例と同じ 4 点に留める。** fatal-free / `%PDF` マジック有効 /
  `unknown_visit` カタログがクリーン / SC#4 不変量（新規ランタイム依存ゼロ・`@preview` 未バンプ・
  `base.typ` の差分は `lang` の 2 行のみ）。D-05 で証拠に加えるフル pytest スイートと docs ビルドは
  `28-VERIFICATION.md` 側の証跡に留め、CHANGELOG には書かない。ページ数など検証機構を持てない
  数値は載せない（Phase 23 D-11）。

- **D-12: リード段落は 3 トラック軸で書く。** 「ドキュメントに書いた設定が実際に出力へ効くように
  なった / キャプション付きテーブルを番号付き figure として出力するようにした / docs の記述を
  実装と一致させた」の 3 軸 + 不変量の一行。`[0.6.2]` のリード文と同じ体裁。BREAKING をリード文の
  冒頭で先出しする案は不採用（既存の体裁を保つ）。BREAKING の可視化は D-01/D-02 の項目本体が担う。

### Claude's Discretion

以下はプラン/実行時に Claude 裁量で決めてよい（オーナー確認済み）:

- **docs ビルドの合否基準とベースラインの取り方**（D-06）。
- **`uv.lock` の再生成手順** — `uv lock` か `uv sync` か。SC#1 の受入は `uv sync --locked` が緑になること。
- **`## [0.6.3]` の日付** — プラン実行日を使う（Phase 23 D-15 の確立済みルール。`- Unreleased` の
  まま残して `/gsd-complete-milestone` で確定する案は不採用）。
- **各項目の具体的な文面** — BREAKING ラベルの表記形式、実測の但し書きをどこまで織り込むか、
  before/after 例の書き方。
- **フェーズ内の作業分割とプラン数**（版バンプ → CHANGELOG → ゲート実走 の順が自然）。
- **`## [Unreleased]` 節の保持** — Keep a Changelog 標準どおり `[0.6.3]` の上に残す想定。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 変更対象ファイル

- `pyproject.toml` §`[project]` `:7` — `version = "0.6.2"`。**実測上これが唯一の版リテラル**
  （`typsphinx/__init__.py` は `importlib.metadata.version("typsphinx")` からの動的取得なので対象外）
- `CHANGELOG.md` — `## [Unreleased]`（`:8`）の下に `## [0.6.3]` を新設。`## [0.6.2]`（`:10`〜）が
  リード段落 + `### Removed` / `### Fixed` / `### Verified` の節構成と文体の直接の見本。
  ファイル末尾の releases/tag リンクブロック（`[0.6.2]: …/releases/tag/v0.6.2` 以下）と
  `[Unreleased]: …/compare/v0.6.2...HEAD` の更新も本フェーズの仕事（ROADMAP SC#2）
- `README.md:315` — `**Status**: Stable (v0.6.2) - Production ready`
- `uv.lock` — 版バンプに追随して再生成（SC#1）

### ゲートと不変量

- `tests/test_corpus_gate.py` — SC#3 の判定本体。`@pytest.mark.slow`。コーパス入手不能時は
  `pytest.skip` する（D-05 の `-rs` 指定の背景）
- `tests/test_readme_version_sync.py` — Phase 23 D-13 で新設。`README.md` の Status 行と
  `pyproject.toml` の `version` の一致を assert する。**版バンプで README を忘れると赤くなる**
- `tests/test_preview_version_sync.py` — `@preview` 3-way 版同期面の担保（SC#4 / D-07）
- `typsphinx/templates/base.typ` — SC#4 が「差分は `lang` パラメータとその配線のみ」を要求する対象。
  実測で `git diff main..HEAD` は 2 行

### 要件台帳（CHANGELOG に載せる対象の全量）

- `.planning/REQUIREMENTS.md` — v1 要件 7 件（CONF-04 / CONF-05 / CONF-07 / TBL-01 / TBL-02 /
  DOC-06 / DOC-07）。D-09 の束ね方はこの台帳をカバーすること（ただし D-10 により DOC-06 は
  意図的に CHANGELOG へ載せない）
- `.planning/PROJECT.md` §Requirements ▸ Validated — 各フェーズが何を出荷したかの一次記録。
  CHANGELOG 文面の素材はここから取る（Phase 24〜27.1 の項目）

### 前フェーズの決定・申し送り

- `.planning/milestones/v0.6.2-phases/23-v0-6-2-release-prep-regression-gate-close/23-CONTEXT.md` —
  **同型フェーズの直接の先例。D-01（BREAKING の裁定基準 = D-05）/ D-07（バグ修正は BREAKING に
  しない）/ D-09・D-12（ゲートの回し方と skip 誤読の防止）/ D-11（検証機構を持てない数値は
  載せない）/ D-13（README 同期テスト）/ D-15（日付の確定）の一次記録**
- `.planning/ROADMAP.md` §Phase 28 — SC#1〜SC#5。**SC#5 のスコープ柵（tag / PyPI / GitHub Release /
  マージなし）は絶対**。SC#4 は 2026-07-25 の不変量改訂込みで読むこと
- `.planning/ROADMAP.md` §v0.6.3 冒頭「Invariant amendment (2026-07-25, owner decision)」 —
  `base.typ` byte-unchanged が Phase 27.1 に限り解除された経緯
- `.planning/phases/27.1-typst-text-lang-from-sphinx-language-config/27.1-CONTEXT.md` —
  CONF-07 の適用範囲（既定テンプレート経路のみ）と precedence の一次記録。D-03 の本文の根拠
- `.planning/MILESTONES.md` — マイルストーン締めの記録形式（`/gsd-complete-milestone` の入力先）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`tests/test_corpus_gate.py`** — SC#3 をそのまま満たす既存資産。追加実装は不要で、実行と
  証跡採取のみ。
- **`tests/test_readme_version_sync.py`** — Phase 23 で新設された結合点。README:315 と
  `pyproject.toml:7` を同時に触らないとスイートが赤くなる（意図した拘束）。
- **`CHANGELOG.md` の `## [0.6.2]` エントリ** — リード段落 + Removed/Fixed/Verified の節構成と
  文体の見本。D-09〜D-12 はこの形を踏襲する。
- **`tox -e docs-multilang` / `docs-pdf`** — D-05 の docs 証拠の実行手段。`docs-multilang` は
  `docs/build_multilang.py` 経由で en/ja の **HTML のみ**、`docs-pdf` は英語 PDF（D-08 の根拠）。

### Established Patterns

- **prep と publish の分離** — v0.5.0 Phase 10 / v0.6.1 / v0.6.2 Phase 23 と同じ。最終フェーズは
  版バンプ + CHANGELOG まで、不可逆な publish は `/gsd-complete-milestone`。
- **検証機構を持てない数値はドキュメントに置かない** — Phase 22.4 で確立。本フェーズでは
  D-08（ja 目視確認を採らない）と D-11（ページ数を載せない）に適用。
- **証跡はフェーズの VERIFICATION.md に集約し、専用レポートは作らない** — Phase 18 / 23 の先例。

### Integration Points

- **`/gsd-complete-milestone`** — 本フェーズの出力（`[0.6.3]` エントリ）がそのまま GitHub Release
  body の単一ソースになる。tag / PyPI / Release / マージはすべて向こう側。
- **`.github/workflows/release.yml`** — tag `v0.6.3` の push で発火する。**本フェーズでは触れないし
  起動しない。**
- **pending todo `2026-07-25-close-pr98-after-v063-release.md`** — PR#98 のクローズは
  **publish 後**（`/gsd-complete-milestone` 直後）に実施するとオーナーが 2026-07-25 に決定済み。
  本フェーズでは何もしない。

</code_context>

<specifics>
## Specific Ideas

### 討議中に実測した事実（プランはこれを前提にしてよい）

| 主張 | 実測結果 | 影響 |
|---|---|---|
| 版リテラルの所在 | `pyproject.toml:7` のみ（`version = "0.6.2"`） | バンプ対象は 1 箇所 + `README.md:315` |
| README Status 行 | `README.md:315` `**Status**: Stable (v0.6.2) - Production ready` | `test_readme_version_sync.py` が一致を assert |
| `base.typ` の差分 | `git diff main..HEAD` は正確に 2 行（`lang: "en",` 追加 / `set text(size: fontsize, lang: lang)`） | D-07 の SC#4 確認はこの diff の貼付で足りる |
| 依存の差分 | `git diff main..HEAD -- pyproject.toml` は空（ランタイム依存に変更なし） | SC#4 の「新規ランタイム依存ゼロ」は自明 |
| CHANGELOG リンクブロック | 末尾に `[0.6.2]: …/releases/tag/v0.6.2` 以下の一覧と `[Unreleased]: …/compare/v0.6.2...HEAD` が存在 | `[0.6.3]` 行の追加と compare の繰り上げが必要 |
| CONF-04 の破壊性 | allowlist 外キー 1 つで `ExtensionError: typst_elements: unknown key ...` → ビルド中断。Phase 26 以前は無音で破棄 | D-02 の BREAKING と対処手順の前提 |
| CONF-05 の破壊性 | 削除済み設定が `conf.py` に残っても Sphinx は警告ゼロで無視し `build succeeded` | D-01 の但し書きの前提 |
| CONF-07 の適用範囲 | 自動導出は既定テンプレート経路のみ。カスタムテンプレート / `typst_package` / srcdir シャドウには注入されない | D-03 の本文に書く適用範囲 |
| ja PDF の可視性 | `docs-pdf` は英語 PDF、`docs-multilang` は en/ja とも HTML のみ | D-08 の根拠 |
| docs 警告のベースライン | Phase 27.1 完了時点でフェーズ前ベースラインの 4 行に復帰済み（ゼロではない） | D-06 の判定基準の前提 |

### 文面上の注意

- **D-01 と D-03 の非対称性は意図的** — 実害のない設定削除（CONF-05）には BREAKING を立て、
  実際に出力が変わる lang 連動（CONF-07）には立てない。これは Phase 23 の D-05／D-07 の配分と
  同じ構造であり、オーナーが両フェーズで一貫して選んでいる。プランはこの配分を維持すること
  （勝手に揃えない）。
- **D-10 により台帳 7 件のうち DOC-06 だけが CHANGELOG に現れない** — 意図的。網羅性を理由に
  足し戻さないこと。

</specifics>

<deferred>
## Deferred Ideas

- **`examples/advanced` が現状ビルド不能** — 討議で領域として提示したがオーナーは選択せず、
  pending todo `.planning/todos/pending/2026-07-25-examples-advanced-non-allowlisted-typst-elements-keys.md`
  のまま据え置き。**討議中に追加で実測した事実（todo 本文より一歩進んだ情報。将来この todo を
  拾うフェーズはここから始めてよい）:** `examples/advanced/_templates/custom.typ` の `project()` は
  `title` / `authors` / `date` / `toctree_maxdepth` / `toctree_numbered` / `toctree_caption` / `body`
  しか宣言しておらず、`papersize` / `fontsize` すら受け取らない。したがって非 allowlist の 5 キー
  （`author` / `date` / `margin` / `primary_color` / `code_font`）を削除しても、残る `papersize` /
  `fontsize` が今度は Typst 側で `unexpected argument` の hard fatal になる。実測上の修正は
  `typst_elements` を空にすること。同型の記述は `examples/advanced/README.md:224` と
  `README.md:206`（"Template parameters (paper size, fonts, etc.)" — 3 キー体制と不整合）にもある。
  `examples/` はホイールに含まれない（`pyproject.toml` の `include = ["typsphinx*"]`）ので、
  影響を受けるのは GitHub からコピーするユーザー。
- **`docs/usage.rst` / `docs/installation.rst` の orphan クラス** — pending todo
  `2026-07-25-docs-usage-installation-orphan-class.md`。Phase 27 が削除した孤児と同じクラス。
  なお `docs/usage.rst` には `typst_elements` の古い例が 2 箇所（`:91`, `:428`）残っている。
- **`derive_typst_lang()` の警告ブロック重複** — pending todo
  `2026-07-25-derive-typst-lang-duplicated-warning-block.md`（27.1 コードレビュー IN-01、Info）。
- **README の依存下限 3 行の同期テスト** — Phase 23 D-14 でスコープ外とした案。Sphinx / typst-py の
  下限を上げる作業が発生したときが自然な場所。
- **リリースゲートで `pytest.skip` を失敗として扱う仕組み** — Phase 23 D-12 で不採用。コーパスゲートを
  CI に載せるときに再検討。

### Reviewed Todos (not folded)

`todo.match-phase 28` が返した 10 件はいずれも折り込まない。本フェーズは `typsphinx/` を一行も
触らないリリース準備であり、ソースの振る舞いを変える todo は定義上すべて対象外。

- **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`**（score 0.9）— `pyproject.toml`
  というキーワードだけの誤検出。ソース変更。CLAUDE.md も「この todo が landing するまで typing
  imports を modernize しない」と明記している。
- **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`**（score 0.9）— `template_engine.py` の
  リファクタ。ソース変更。
- **`2026-07-25-examples-advanced-non-allowlisted-typst-elements-keys.md`** — 討議領域として提示したが
  オーナー未選択（上記 Deferred 参照）。
- **`2026-07-25-docs-usage-installation-orphan-class.md`** — docs の再編。削除を含むため
  `worktree.cleanup-wave` の削除ガードにも当たる。
- **`2026-07-25-close-pr98-after-v063-release.md`** — オーナー判断で **publish 後**に実施。
  Phase 28 ではなく `/gsd-complete-milestone` 直後のトリガ。
- **`2026-07-21-move-documentation-hosting-to-read-the-docs.md`** / **`2026-07-22-github-io-doc-links-404-missing-en-prefix.md`**
  — RTD 移行とそこに畳み込まれた 404 修正。オーナー裁定で据え置き済み。
- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — CI 拡張。それ自体が 1 フェーズ級。
- **`2026-07-22-citation-node-support-untracked.md`** — `visit_citation` 実装。ソース変更。
- **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`** — Phase 22.3 D-06 で先送り済み。

</deferred>

---

*Phase: 28-v0.6.3 Release Prep + Regression-Gate Close*
*Context gathered: 2026-07-25*
