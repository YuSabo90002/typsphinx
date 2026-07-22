# Phase 23: v0.6.2 Release Prep + Regression-Gate Close - Context

**Gathered:** 2026-07-23
**Status:** Ready for planning

<domain>
## Phase Boundary

v0.6.2 のリリース**準備**と、フルコーパス回帰ゲートによるマイルストーンの締め。
版バンプ、`CHANGELOG.md` の `[0.6.2]` エントリのキュレーション、`README.md` の Status 行同期、
既存コーパスゲートの実走とその証跡記録まで。**publish は行わない。**

**In scope:**
- `pyproject.toml:7` の `version = "0.6.1"` → `"0.6.2"`（実測上これが唯一の版リテラル）
- `uv.lock` の再生成（`uv sync --locked` が緑になること）
- `CHANGELOG.md` の `## [0.6.2]` エントリ新設
- `README.md:316` の `**Status**: Stable (v0.6.1)` → `Stable (v0.6.2)`（22.4 D-11 の申し送り）
- README:316 と `pyproject.toml` の版一致を assert する同期テストの新設（D-13）
- `tests/test_corpus_gate.py` のフルコーパス実走と、証跡の `23-VERIFICATION.md` への記録
- マイルストーン不変量 SC#4 の確認（新規ランタイム依存ゼロ / `@preview` 未バンプ / 3-way 版同期面 未変更）

**Out of scope:**
- **publish 一切**（`git tag v0.6.2`、`release.yml` 起動、PyPI、GitHub Release）→ `/gsd-complete-milestone`
- `typsphinx/` 配下の振る舞い変更（本フェーズはリリース準備であり、機能修正は 19〜22.4 で完了済み）
- `CHANGELOG.md` の過去バージョンエントリの改変（履歴）
- README の他の記述の再検証（22.4 で完了済み。github.io リンク 404 は 22.4 D-17 でオーナー裁定済みの据え置き）
- 版番号そのものの見直し（0.7.0 案）— ROADMAP SC#1 が 0.6.2 に固定（D-08 で明示的に不採用）

</domain>

<decisions>
## Implementation Decisions

### CHANGELOG `[0.6.2]` の粒度と構成

- **D-01: `[0.6.2]` エントリは根本原因クラスタ単位で束ねる。** FID-02..FID-14 を 13 行に個別列挙せず、
  監査クラスタ A–F 相当の単位で 1 項目にまとめ、末尾の括弧に要件 ID レンジ（例
  `(FID-02–FID-06)`）を並べて追跡性を保つ。読み手はユーザーであり FID 番号を知らないため、
  「何が見た目で直ったか」を単位にする。全体で 10–12 項目前後を目安とする。書式の見本:

  ```markdown
  - **Lost block separation across five constructs (FID-02–FID-06)** —
    paragraphs inside list items, sibling signatures, rubric/option headings,
    definition terms, and back-to-back confvals all rendered run-together…
  ```

- **D-02: `### Verified` 節を置く（`[0.6.1]` / `[0.6.0]` 踏襲）。** コーパスゲートの結果
  （fatal-free、`%PDF` マジック有効、`unknown_visit` カタログがクリーン）と SC#4 不変量の確認を
  ここに書く。Keep a Changelog 標準外の節だが、このプロジェクトで 2 リリース分確立済みの形式。

- **D-03: Phase 22.4（README/CLAUDE.md の実測乖離解消、DOC-01..05）を CHANGELOG に載せる。**
  単なる誤字修正ではなく「誤った情報の訂正」だから — citation 対応という虚偽の機能主張の撤回、
  `typst_template_mapping` コード例のキーと値が逆（そのまま使うとサイレントに無視される）、
  存在しないドキュメントへのリンク。README を追っていたユーザーには可視。

- **D-04: D-03 の項目は `### Fixed` に 1 項目として置く。** `### Documentation` 節は新設しない。
  「誤った情報の訂正」は Fixed の意味に合い、`[0.6.1]` と同じ節構成を保てる。

### user-visible な破壊的変更の見せ方

- **D-05: `typst_output_dir` / `typst_author_params` の削除（22.2 CONF-01）は `### Removed` に置き、
  BREAKING ラベルを立てる**（オーナー裁定 2026-07-23）。公開されていた設定名の削除は仕様上
  破壊的であり、実害の有無に関わらず明示する。
  **実測の但し書き（討議中に測定、2026-07-23）:** 削除後もこの 2 つが `conf.py` に残っていると
  Sphinx は**警告すら出さず完全に無音で無視し `build succeeded` する**。かつ両者は削除前から
  出力に一切反映されていなかった dead config なので、実際の振る舞いは変わらない。この事実を
  BREAKING 項目の本文にどう織り込むかはプラン時の文面判断に委ねる（オーナーは「実害なしを
  明記して BREAKING を立てない」案を明示的に**不採用**とした点に注意 — BREAKING ラベルは必ず立てる）。

- **D-06: Issue #117 の出力ファイル名変更は before/after の具体例付きで提示する。**
  `typst_documents = [("index", "mydoc", ...)]` に対し `index.pdf` → `mydoc.pdf` という実例を示し、
  項目先頭を太字見出しにして他の修正に埋もれないようにする（ROADMAP SC#2 の要求）。
  実測で確認済み: 現行ビルドの出力は `mydoc.typ`（ターゲット名由来）。

- **D-07: #117 は BREAKING 扱いにしない — バグ修正として書く**（オーナー裁定）。
  「そもそも `typst_documents` のターゲット名を使うべきだったのに docname を使っていた」という
  バグの修正であり、仕様の破壊的変更ではない。D-06 の before/after 例で十分に可視化される。

- **D-08: SemVer に関する注記は一切入れない**（オーナー裁定）。BREAKING を立てつつ版が 0.6.2
  （パッチ）である点について、「1.0.0 未満では〜」といった説明行は付けない。版番号の見直し
  （0.7.0 案）も採らない — ROADMAP SC#1 が 0.6.2 に固定している。

### 回帰ゲート（SC#3）の実行と証跡

- **D-09: 既存の `tests/test_corpus_gate.py` を `pytest -m slow` で回す。** 手動 `sphinx-build` は
  行わない。`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` が
  タグ解決 → shallow clone → `-b typstpdf` → `%PDF` 検査 → `unknown_visit` カタログ抽出まで
  実装済みで、判定が機械的・再現可能。追加コードゼロ。

- **D-10: 証跡は `23-VERIFICATION.md` に集約する。** 専用の `23-GATE.md` は作らない
  （Phase 18 = v0.6.1 GATE-03 と同じ形）。`/gsd-complete-milestone` が `MILESTONES.md` に要約する。

- **D-11: ページ数は CHANGELOG に載せない。** `[0.6.1]` は「689-page `index.pdf`」と書いていたが、
  テストはページ数を assert しないため、載せるには手動採取が必要になる。22.4 で確立した原則
  「検証機構を持てない数値はドキュメントに置かない」（22.4 D-01/D-02/D-04）を CHANGELOG にも適用する。
  テストが assert する事実（fatal-free / `%PDF` マジック有効 / `unknown_visit` カタログがクリーン）
  はそのまま書いてよい。

- **D-12: ゲートが skip ではなく実際に pass したことを明示的に確認する。**
  `test_corpus_gate.py` はコーパスが入手できないと `pytest.skip` する仕様（15-CONTEXT D-05）なので、
  「緑」が「スキップされた」を意味し得る。`pytest -m slow -rs`（skip 理由を強制表示）で実行し、
  `1 passed`（`skipped` ではない）と読める生ログを `23-VERIFICATION.md` に貼る。
  **テスト側にコードを追加してリリース時 skip を失敗にする案は不採用** — 本フェーズはリリース準備であり
  テスト基盤の拡張はスコープ外。

### 版バンプの同期範囲と日付

- **D-13: `README.md:316` の Status 行を `Stable (v0.6.2)` に更新し、あわせて
  `README.md:316` と `pyproject.toml` の `version` の一致を assert する同期テストを新設する。**
  雛形は `tests/test_preview_version_sync.py`（22.4 の `code_context` が明示的にそう指名している）。
  理由: この行は v0.5.0 のまま 2 リリース分 stale した実績があり、人間の注意力ではなく仕組みで止める。

- **D-14: 同期テストのスコープは Status 行のリリース版のみ。** `README.md:37-39`（Requirements 節）と
  `README.md:317`（`**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+` フッタ）の依存下限
  3 種は対象外。実測で `pyproject.toml` の `requires-python` / `dependencies` と一致しており
  （22.4 D-03 で確認済み）、実際に乖離したのは Status 行だけ。パーサを複雑にせず、
  実害のあった 1 点だけを封じる。

- **D-15: `## [0.6.2] - 2026-07-23`（prep 実行日）で日付を確定させる。** `- Unreleased` のまま
  残して `/gsd-complete-milestone` で確定する案は不採用。`[0.6.1]` も tag 日（07-19）とエントリ日付
  （07-20）が 1 日ずれており先例として許容されている。complete-milestone 側の手順を増やさない。
  *(プラン実行日が 2026-07-23 でない場合は、その実行日を使う。)*

### Claude's Discretion

以下はプラン/実行時に Claude 裁量で決めてよい（オーナー確認済み）:

- **`uv.lock` の再生成手順** — `uv lock` か `uv sync` か。SC#1 の受入は `uv sync --locked` が緑になること。
- **`## [Unreleased]` 節の保持** — Keep a Changelog 標準どおり `[0.6.2]` の上に空の `[Unreleased]` を残す想定。
- **`[0.6.2]` 冒頭のリード文（マイルストーン要約段落）の文面** — `[0.6.0]`/`[0.6.1]` が持っている 3–5 行の
  段落。今回も置く想定で、文面はプラン時に確定してよい。
- **D-05 の BREAKING 項目の具体的な文面**（ラベル表記の形式、実測の但し書きをどこまで織り込むか）。
- **SC#4 不変量の確認手段** — `git diff` による依存 / `@preview` 3-way 同期面の差分ゼロ確認と、
  既存 `tests/test_preview_version_sync.py` の緑をもって足りる想定。
- **フェーズ内の作業分割と順序**（版バンプ → CHANGELOG → 同期テスト → ゲート実走 の順が自然）。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 変更対象ファイル

- `pyproject.toml` §`[project]` `:7` — `version = "0.6.1"`。**実測上これが唯一の版リテラル**
  （`typsphinx/__init__.py:20` は `importlib.metadata.version("typsphinx")` からの動的取得なので対象外）
- `CHANGELOG.md` — `## [Unreleased]`（`:8`）の下に `## [0.6.2]` を新設。`## [0.6.1]`（`:10`〜）が
  節構成（Added / Changed / Fixed / Verified）と文体の直接の見本
- `README.md:316` — `**Status**: Stable (v0.6.1) - Production ready`（D-13 の更新対象）
- `uv.lock` — 版バンプに追随して再生成（SC#1）

### 回帰ゲート

- `tests/test_corpus_gate.py` — GATE-02 実体。モジュール docstring に D-01..D-05 の仕様が明記されている。
  `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`（`:284`、`@pytest.mark.slow`）が
  SC#3 の判定本体。`resolve_corpus_tag()` / `get_or_clone_corpus()` はコーパス入手不能時に
  `pytest.skip` する（D-12 の背景）
- `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0` — キャッシュ済みコーパス（実在を確認済み）

### 同期テストの雛形と不変量

- `tests/test_preview_version_sync.py` — 「ドキュメント/複数ソース間の値の一致をテストで担保する」
  既存パターン。D-13 の新規テストの雛形であり、同時に SC#4 の `@preview` 3-way 同期面の担保でもある
- `typsphinx/writer.py:151-154` / `typsphinx/template_engine.py` / `typsphinx/templates/base.typ` —
  SC#4 が「未変更」を要求する 3-way 版同期面

### 前フェーズの決定・申し送り

- `.planning/phases/22.4-readme-status-configuration-options-known-limitations-docs/22.4-CONTEXT.md` —
  **D-11 の申し送り（README Status 行を版バンプと同時に更新すること）の一次記録**。
  加えて「検証機構を持てない数値はドキュメントに置かない」原則（D-01/D-02/D-04）と、
  「将来 README に検証付き数値を戻すなら `test_preview_version_sync.py` が雛形」という
  `code_context` の記述 — 本フェーズの D-11/D-13 の根拠
- `.planning/phases/22.2-dead-config-value-sweep/22.2-CONTEXT.md` — `typst_output_dir` /
  `typst_author_params` が「登録だけで出力に効かない dead config」だった経緯（D-05 の背景）
- `.planning/phases/22-typstpdf-target-name-pdf-fix-issue-117/22-CONTEXT.md` §D-09 —
  Issue #117 を user-visible な出力ファイル名変更として提示せよという Phase 23 への申し送り（D-06 の根拠）
- `.planning/milestones/v0.6.1-phases/18-*/18-VERIFICATION.md` — v0.6.1 GATE-03 の証跡の置き方の先例（D-10）
- `.planning/ROADMAP.md` §Phase 23 — SC#1〜SC#5。**SC#5 のスコープ柵（tag / PyPI / GitHub Release なし）は絶対**
- `.planning/MILESTONES.md` §v0.6.1 — マイルストーン締めの記録形式（`/gsd-complete-milestone` の入力先）

### 要件台帳（CHANGELOG に載せる対象の全量）

- `.planning/REQUIREMENTS.md` — FID-02..FID-14 / PDF-01, PDF-02 / CONF-01..CONF-03 / WR-01, WR-02 /
  DOC-01..DOC-05 の全 23 件。D-01 のクラスタ束ねはこの台帳を漏れなくカバーすること
- `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` —
  FID 各件のクラスタ A–F 帰属の source of record（D-01 の束ね方の根拠）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`tests/test_corpus_gate.py`** — SC#3 をそのまま満たす既存資産。追加実装は不要で、
  実行と証跡採取のみ（D-09）。Phase 22 の `aedd607` でターゲット名由来 PDF への
  assertion 修正が既に入っているので、#117 の変更とも整合済み。
- **`tests/test_preview_version_sync.py`** — D-13 の新規同期テストの直接の雛形。
  「複数の場所に散った同じ値の一致を assert する」という形が既にプロジェクトの慣行として存在する。
- **`CHANGELOG.md` の `## [0.6.1]` / `## [0.6.0]` エントリ** — リード段落 + Added/Changed/Fixed/Verified
  という節構成の見本。D-01/D-02/D-04 はこの形を踏襲する。

### Established Patterns

- **prep と publish の分離** — v0.5.0 Phase 10 / v0.6.1 と同じ。最終フェーズは版バンプ + CHANGELOG まで、
  不可逆な publish は `/gsd-complete-milestone`。SC#5 のスコープ柵はこの慣行の明文化。
- **検証機構を持てない数値はドキュメントに置かない** — 22.4 で確立（D-01/D-02/D-04）。
  本フェーズでは D-11（ページ数を載せない）と D-13/D-14（載せる数値には同期テストを付ける）の両面で適用。
- **証跡はフェーズの VERIFICATION.md に集約し、専用レポートは作らない** — Phase 18 の先例（D-10）。

### Integration Points

- **`/gsd-complete-milestone`** — 本フェーズの出力（`[0.6.2]` エントリ）がそのまま GitHub Release body の
  単一ソースになる（ROADMAP SC#2）。tag / PyPI / Release はすべて向こう側。
- **`.github/workflows/release.yml`** — tag `v0.6.2` の push で発火する。**本フェーズでは触れないし起動しない。**
- **`README.md:316` ↔ `pyproject.toml:7`** — D-13 の新規テストが作る新しい結合点。
  以降の全リリースで版バンプ時に README も同時に触る必要が生じる（意図した拘束）。

</code_context>

<specifics>
## Specific Ideas

### 討議中に実測した事実（プランはこれを前提にしてよい）

| 主張 | 実測結果 | 影響 |
|---|---|---|
| 版リテラルの所在 | `pyproject.toml:7` のみ。`typsphinx/__init__.py:20` は `importlib.metadata` 由来 | バンプ対象は 1 箇所 + README:316 |
| 削除済み設定を `conf.py` に残した場合 | **警告ゼロ・完全に無音で無視・`build succeeded`**（`-b typst` 実走で確認） | D-05 の文面の前提 |
| 削除済み設定の実害 | 削除前から出力に反映されていない dead config なので振る舞い不変 | D-05 の文面の前提 |
| #117 の現行出力 | `typst_documents = [("index","mydoc",…)]` → `mydoc.typ` が出る（ターゲット名由来） | D-06 の before/after 例 |
| README の版記述 | `:37-39`（Requirements）、`:316`（Status）、`:317`（フッタ）の 3 箇所。stale だったのは `:316` のみ | D-14 のスコープ限定 |
| コーパスゲート | `tests/test_corpus_gate.py` に実装済み・`@pytest.mark.slow`・入手不能時は skip | D-09 / D-12 |
| ROADMAP 表の Phase 22.3 の "In Progress" | **stale**。`22.3-VERIFICATION.md` は SC 5 件すべて直接証拠つきで確認済み（`human_needed` は pytest-xdist 不在による非ブロッキング 1 件のみ） | Phase 23 の依存は満たされている |

### 文面上の注意

- **D-05 と D-07 の非対称性は意図的** — オーナー裁定により、実害のない設定削除には BREAKING を立て、
  実際にファイル名が変わる #117 には立てない。「警告の重みが実害と逆転する」という指摘は提示済みで、
  その上でこの配分が選ばれている。プランはこの配分を維持すること（勝手に揃えない）。
- **ROADMAP の "~684-page" 表記** — SC#3 の文言。CHANGELOG には持ち込まない（D-11）。

</specifics>

<deferred>
## Deferred Ideas

- **README の依存下限 3 行（`:37-39` / `:317`）の同期テスト** — D-14 で今回のスコープ外とした。
  将来 Sphinx / typst-py の下限を上げる作業が発生したときに、同型のテストを足すのが自然な場所。
- **リリースゲートで `pytest.skip` を失敗として扱う仕組み** — D-12 で不採用。テスト基盤の拡張であり
  リリース準備フェーズのスコープ外。将来コーパスゲートを CI に載せるときに再検討する。
- **版番号を 0.7.0 に見直す案** — D-08 で不採用。ROADMAP SC#1 が 0.6.2 を固定しており、
  変更するには ROADMAP 側の修正が先に必要。

### Reviewed Todos (not folded)

`todo.match-phase 23` が返した 9 件はすべてキーワード一致による誤検出で、いずれも折り込まない。
本フェーズはリリース準備であり、ソースの振る舞いを変える todo は定義上すべて対象外。

- **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`**（score 0.9, area: source）—
  `pyproject.toml` というキーワードだけで一致した誤検出。`Dict`/`List` の modernize はソース変更であり、
  22.4 D-15 で明示的に別フェーズへ退避済み。
- **`2026-07-22-github-io-doc-links-404-missing-en-prefix.md`** — README の 7 本のリンクが 404
  （`/en/` プレフィックス欠落）。README を触るフェーズなので候補にはなるが、**22.4 D-17 でオーナーが
  「リンクの一括変更は RTD 移行作業側に委ねる」と裁定済み**。本フェーズは Status 行のみに触れる。
- **`2026-07-21-move-documentation-hosting-to-read-the-docs.md`** — 上記の前提となる移行作業。未着手。
- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — CI 拡張。22.4 で「それ自体が 1 フェーズ級」と判断済み。
- **`2026-07-22-citation-node-support-untracked.md`** — `visit_citation` 実装。ソース変更。
- **`2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`** — 22.2 と同型の第三・第四の
  dead config。ソース変更であり、v0.6.2 には含まれない（CHANGELOG に書くことも無い）。
- **`2026-07-22-delete-orphan-docs-configuration-rst.md`** / **`2026-07-22-user-guide-configuration-phantom-config-names.md`** —
  `docs/` の再編作業。22.4 D-16 / D-21 で退避済み。
- **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`** — 22.3 D-06 で明示的に先送り済み。

</deferred>

---

*Phase: 23-v0.6.2 Release Prep + Regression-Gate Close*
*Context gathered: 2026-07-23*
