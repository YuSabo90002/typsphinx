# Phase 23: v0.6.2 Release Prep + Regression-Gate Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-23
**Phase:** 23-v0.6.2 Release Prep + Regression-Gate Close
**Areas discussed:** CHANGELOG の粒度と構成 / user-visible な破壊的変更の見せ方 / 回帰ゲートの実行と証跡 / 版バンプの同期範囲と日付

---

## 領域選択

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG の粒度と構成 | 23 要件をどの粒度で書くか、節をどう割るか | ✓ |
| user-visible な破壊的変更の見せ方 | 設定削除の Removed、#117 のファイル名変更 | ✓ |
| 回帰ゲートの実行方法と証跡 | SC#3 の回し方と証跡の置き場 | ✓ |
| 版バンプの同期範囲と日付 | README Status 行、uv.lock、CHANGELOG 日付 | ✓ |

**User's choice:** 4 領域すべて

---

## CHANGELOG の粒度と構成

### Q1: `[0.6.2]` エントリの粒度

| Option | Description | Selected |
|--------|-------------|----------|
| クラスタ単位で束ねる | 監査クラスタ A–F ごとに 1 項目、全体で 10–12 項目。要件 ID は括弧で追跡性を保つ | ✓ |
| 要件番号ごとに個別列挙 | FID-02..14 を 13 行、全体 23 項目。追跡性は最高だが重要変更が埋もれる | |
| ハイブリッド | user-visible 影響の大きいものを厚く、FID 系を薄く束ねる | |

**User's choice:** クラスタ単位で束ねる → **D-01**

### Q2: `### Verified` 節（Keep a Changelog 標準外）

| Option | Description | Selected |
|--------|-------------|----------|
| 置く | `[0.6.1]`/`[0.6.0]` 踏襲。ゲート結果と SC#4 不変量を記載 | ✓ |
| 置かない | 標準 6 節に揃え、証跡は `.planning/` にのみ残す | |

**User's choice:** 置く → **D-02**

### Q3: Phase 22.4（DOC-01..05）を載せるか

| Option | Description | Selected |
|--------|-------------|----------|
| 載せる—内容の誤り訂正として | 虚偽の citation 対応主張の撤回、キーと値が逆のコード例、存在しないドキュメントへのリンク | ✓ |
| 載せない | ビルド成果物の振る舞いは不変なのでノイズ | |

**User's choice:** 載せる → **D-03**

### Q4: 22.4 の置き場

| Option | Description | Selected |
|--------|-------------|----------|
| `### Fixed` に 1 項目として | 「誤った情報の訂正」は Fixed の意味に合う。節構成を増やさない | ✓ |
| `### Documentation` 節を新設 | ドキュメント変更を分離。既に Verified で標準外を使っているので一貫性は崩れない | |

**User's choice:** `### Fixed` に 1 項目 → **D-04**

---

## user-visible な破壊的変更の見せ方

**討議前の実測（Claude が測定）:** 削除済みの `typst_output_dir` / `typst_author_params` が
`conf.py` に残っていても Sphinx は警告ゼロで無音無視し `build succeeded` する。かつ両者は
削除前から出力に効いていない dead config なので実際の振る舞いは変わらない。

### Q1: `### Removed` の提示

| Option | Description | Selected |
|--------|-------------|----------|
| 実害なしを明記して添える | BREAKING は立てず「残っていても壊れない」と明記。実測に忠実 | |
| BREAKING ラベルを立てる | 公開設定の削除は仕様上破壊的。実害の有無に関わらず明示 | ✓ |
| 削除事実だけ簡潔に | 設定名と 1 行の理由のみ | |

**User's choice:** BREAKING ラベルを立てる → **D-05**
**Notes:** Claude の推奨（実害なしを明記して BREAKING を立てない）は明示的に不採用。
プランはこの裁定を維持すること。

### Q2: Issue #117 の提示の厚さ

| Option | Description | Selected |
|--------|-------------|----------|
| before/after の具体例付き | `index.pdf` → `mydoc.pdf` の実例、太字見出しで埋没を防ぐ | ✓ |
| 例＋CI 移行ノート | さらに「ハードコードしたパスは更新を」という行動指示を付ける | |
| 1 行の修正記述のみ | SC#2 が避けよとしている「内部修正に埋もれる」状態に近づく | |

**User's choice:** before/after の具体例付き → **D-06**

### Q3: #117 も BREAKING 扱いにするか（Q1 の答えからの波及）

| Option | Description | Selected |
|--------|-------------|----------|
| する—影響はこちらが大きい | 設定削除は何も壊れないが #117 は CI が実際に壊れる。逆転を避ける | |
| しない—#117 はバグ修正 | ターゲット名を使うべきだった箇所の修正であり仕様の破壊ではない | ✓ |

**User's choice:** しない → **D-07**
**Notes:** 「警告の重みが実害と逆転する」という指摘は提示済みで、その上でこの配分が選ばれた。
D-05 と D-07 の非対称性は意図的。

### Q4: SemVer との不整合（BREAKING なのにパッチ番号）

| Option | Description | Selected |
|--------|-------------|----------|
| 0.x の旨を注記する | 「1.0.0 未満はパッチでも破壊的変更が入りうる」と一行添える | |
| 何も注記しない | BREAKING ラベルだけ立て、版番号との関係には触れない | ✓ |
| 版番号の見直しを検討 | 0.7.0 案。ROADMAP SC#1 の修正が先に必要 | |

**User's choice:** 何も注記しない → **D-08**

---

## 回帰ゲートの実行と証跡

**討議前の実測:** `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`
が `@pytest.mark.slow` で既に存在し、タグ解決 → shallow clone → `-b typstpdf` → `%PDF` 検査 →
`unknown_visit` カタログ抽出まで実装済み。Phase 18（v0.6.1 GATE-03）は専用レポートを作らず
`18-VERIFICATION.md` に証跡を置いていた。

### Q1: ゲートの回し方

| Option | Description | Selected |
|--------|-------------|----------|
| 既存テストを `-m slow` で回す | 追加コードゼロ、判定が機械的・再現可能 | ✓ |
| 手動 `sphinx-build` で回す | 数値を自由に拾えるが判定が人間依存 | |
| 両方 | 判定はテスト、数値は手動採取 | |

**User's choice:** 既存テストを `-m slow` で回す → **D-09**

### Q2: 証跡の置き場

| Option | Description | Selected |
|--------|-------------|----------|
| `23-VERIFICATION.md` に集約 | Phase 18 と同じ形。成果物の種類を増やさない | ✓ |
| 専用の `23-GATE.md` を作る | ゲートの生ログ・カタログ全文・ページ数を独立ファイルに | |

**User's choice:** `23-VERIFICATION.md` に集約 → **D-10**

### Q3: ページ数を CHANGELOG に載せるか

| Option | Description | Selected |
|--------|-------------|----------|
| 載せない | 22.4 の「検証機構を持てない数値は置かない」原則を CHANGELOG にも適用 | ✓ |
| 載せる—手動で採る | `[0.6.1]` の「689-page」との一貫性を優先 | |
| 近似表現にする | 「~684-page」。精度を主張しないが依然として未検証の数値 | |

**User's choice:** 載せない → **D-11**

### Q4: `pytest.skip` が「緑」に見える問題

| Option | Description | Selected |
|--------|-------------|----------|
| 実行されたことを明示的に確認 | `-rs` で skip 理由を強制表示し `1 passed` の生ログを記録。コード変更不要 | ✓ |
| リリース時は skip を失敗にする | テスト側にフラグ/環境変数を追加。堅いがテスト基盤の拡張 | |

**User's choice:** 実行されたことを明示的に確認 → **D-12**

---

## 版バンプの同期範囲と日付

**討議前の実測:** 版リテラルは `pyproject.toml:7` のみ（`typsphinx/__init__.py:20` は
`importlib.metadata` 由来）。README の版記述は `:37-39`（Requirements）、`:316`（Status）、
`:317`（フッタ）の 3 箇所で、stale だったのは `:316` のみ。

### Q1: README:316 Status 行の扱い

| Option | Description | Selected |
|--------|-------------|----------|
| 0.6.2 に更新し、同期テストを追加 | `test_preview_version_sync.py` と同型。v0.5.0 で 2 リリース分 stale した再発を仕組みで止める | ✓ |
| 0.6.2 に更新するだけ | 22.4 D-11 の申し送りをそのまま実行。同じ stale が再発しうる | |
| Status 行から版番号を落とす | 22.4 の原則を徹底。乖離は原理的に起きないが読み手が現行版を知れない | |

**User's choice:** 0.6.2 に更新し、同期テストを追加 → **D-13**

### Q2: `## [0.6.2]` の日付

| Option | Description | Selected |
|--------|-------------|----------|
| prep 実行日を置く | `[0.6.1]` も tag 日と 1 日ずれており先例あり。complete-milestone の手順を増やさない | ✓ |
| Unreleased のまま残す | 日付の正確さは上がるが手順が増え、忘れるリスクが残る | |

**User's choice:** prep 実行日を置く → **D-15**

### Q3: 同期テストのスコープ

| Option | Description | Selected |
|--------|-------------|----------|
| Status 行のリリース版のみ | 実際に乖離したのはこの行だけ。テスト 1 つで実害を封じる | ✓ |
| 依存下限 3 行も含める | 将来の依存バンプ時の乖離も封じるがパーサが複雑化 | |

**User's choice:** Status 行のリリース版のみ → **D-14**

---

## Claude's Discretion

オーナーが「CONTEXT.md を書いてよい」と判断した時点で、以下は Claude 裁量として記録:

- `uv.lock` の再生成手順（`uv lock` か `uv sync` か）— 受入は `uv sync --locked` が緑
- `## [Unreleased]` 節の保持（Keep a Changelog 標準どおり残す想定）
- `[0.6.2]` 冒頭のリード段落の文面
- D-05 の BREAKING 項目の具体的な文面（ラベル表記、実測の但し書きの織り込み方）
- SC#4 不変量の確認手段（`git diff` + 既存 `test_preview_version_sync.py` の緑）
- フェーズ内の作業分割と順序

## Deferred Ideas

- README の依存下限 3 行（`:37-39` / `:317`）の同期テスト — D-14 で今回は対象外
- リリースゲートで `pytest.skip` を失敗として扱う仕組み — D-12 で不採用
- 版番号を 0.7.0 に見直す案 — D-08 で不採用（ROADMAP SC#1 が固定）

## 討議中に判明した副次的事実

- **ROADMAP.md の Progress 表で Phase 22.3 が "In Progress" と表示されているのは stale。**
  `22.3-VERIFICATION.md` は SC 5 件すべてを直接証拠つきで確認済み（`status: human_needed` は
  pytest-xdist 不在による非ブロッキング 1 件のみ）。Phase 23 の依存関係は満たされている。
  表の更新は本フェーズの計画時に併せて行うのが自然。
