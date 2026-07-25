# Phase 28: v0.6.3 Release Prep + Regression-Gate Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-25
**Phase:** 28-v0.6.3 Release Prep + Regression-Gate Close
**Areas discussed:** BREAKING の立て方, ゲート証拠の範囲, CHANGELOG の粒度

**提示したが選択されなかった領域:** examples の破損対応（`examples/advanced` が
`ExtensionError` でビルド不能）→ Deferred へ

---

## 領域選択

| Option | Description | Selected |
|--------|-------------|----------|
| BREAKING の立て方 | CONF-05 削除 / CONF-04 fail-loud / CONF-07 lang 自動導出のどれに BREAKING を立てるか | ✓ |
| examples の破損対応 | `examples/advanced` のビルド不能をリリース前に直すか | |
| ゲート証拠の範囲 | コーパスゲート単独か、docs ビルド・フルスイートも含めるか | ✓ |
| CHANGELOG の粒度 | 7 要件の束ね方、節配置、Verified の内容、リード文の軸 | ✓ |

**Notes:** Phase 23（v0.6.2 の同型フェーズ）で決着済みの事項 — prep only / publish は
complete-milestone / 版リテラルは `pyproject.toml:7` のみ / README Status 行は同期テスト済み /
CHANGELOG 日付は実行日 / ページ数は載せない / ゲートは `pytest -m slow -rs` — は再質問しなかった。

---

## BREAKING の立て方

### Q1: CONF-05（`typst_toctree_defaults` の削除）の書き方

| Option | Description | Selected |
|--------|-------------|----------|
| D-05 先例を踏襲 | `### Removed` + BREAKING ラベル。「残っていても無音で無視される・振る舞い不変」の実測但し書きを添える | ✓ |
| Removed だがラベル無し | 他に本物の挙動変更（CONF-04）があるので警告の重みを揃える案 | |
| Claude 裁量 | 先例踏襲を既定に文面は実行時判断 | |

**User's choice:** D-05 先例を踏襲
**Notes:** 実測（削除済み設定が `conf.py` に残っても Sphinx は警告ゼロで無視し `build succeeded`、
かつ削除前から出力に効いていない dead config）を提示したうえでの選択。

### Q2: CONF-04 の未知キー fail-loud の扱い

| Option | Description | Selected |
|--------|-------------|----------|
| BREAKING を立てる | `### Changed` + BREAKING ラベル + 対処手順（余分なキーは削除／残すなら `typst_template_function.params`） | ✓ |
| Changed に置くがラベル無し | 「無音で捨てていた欠陥の修正の副作用」として位置づける | |
| Fixed に置く | CONF-04 本体とまとめ、fail-loud は本文で触れるだけ | |

**User's choice:** BREAKING を立てる
**Notes:** 実測 — Phase 26 以前は `DEFAULT_PARAMETER_MAPPING` の 3 キー以外を黙って破棄。現在は
allowlist 外キー 1 つで `ExtensionError` → ビルド中断。同梱 `examples/advanced` がその実例。

### Q3: CONF-07（lang 連動）の CHANGELOG での位置づけ

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed（バグ修正） | `base.typ` の `lang: "en"` ハードコードの修正。BREAKING は立てない（Phase 23 D-07 と同じ基準）。before/after を示す | ✓ |
| Added（新機能） | `typst_elements` に `lang` キーが加わった点を主軸に `### Added` | |
| Changed + 影響範囲明記 | `### Changed` に置き、適用範囲（既定テンプレート経路のみ）を明示 | |

**User's choice:** Fixed（バグ修正）
**Notes:** 影響を受けるのは「既定テンプレート × `language` 設定済み」のユーザーのみで、
カスタムテンプレート／`typst_package`／srcdir シャドウの 3 経路には注入されない、という実測を提示済み。

### Q4: アップグレード対処手順の置き場所

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG 本文のみ | BREAKING 項目内に 1–2 行。docs は触らない。触るファイルは pyproject / uv.lock / CHANGELOG / README の 4 つ | ✓ |
| docs にも 1 段落追加 | `user_guide/configuration.rst` に「0.6.3 以前は未知キーが無視されていた」旨を追記（ja `.po` 追従が付随） | |
| Claude 裁量 | CHANGELOG を既定に、必要ならプラン時に docs を追加 | |

**User's choice:** CHANGELOG 本文のみ

---

## ゲート証拠の範囲

### Q1: Phase 28 で収める証拠の範囲

| Option | Description | Selected |
|--------|-------------|----------|
| コーパス + フルスイート + docs | コーパスゲート（`-m slow -rs` で `1 passed`）+ フル pytest + `docs-multilang`/`docs-pdf` の緑を 28-VERIFICATION.md に記録 | ✓ |
| コーパス + フルスイート | docs ビルドは CI の `docs.yml` に委ねる | |
| コーパスゲートのみ | Phase 23 D-09/D-12 と完全に同じ形。先例との差分ゼロ | |

**User's choice:** コーパス + フルスイート + docs
**Notes:** Phase 27.1 で executor が worktree 内から docs ビルド警告を観測できず、マージ後に
警告 5 行の増加が発覚して後追い修正した実績を踏まえての選択。

### Q2: docs ビルドの合否判定基準

| Option | Description | Selected |
|--------|-------------|----------|
| 増えていないこと | ベースライン 4 行から増えていないことを基準に、実際の警告行を VERIFICATION.md に貼る。assert するテストは作らない | |
| ビルド成功のみ | exit 0 で完走すれば足りる | |
| Claude 裁量 | 「増えていないこと」を既定に、ベースラインの取り方はプラン時に決める | ✓ |

**User's choice:** Claude 裁量

### Q3: SC#4（不変量）の確認手段

| Option | Description | Selected |
|--------|-------------|----------|
| git diff の実出力を貼る + 既存テスト | `git diff main..HEAD` の出力（base.typ の 2 行、依存の差分ゼロ）を VERIFICATION.md に貼り、`test_preview_version_sync.py` の緑で 3-way 同期面を担保。追加実装ゼロ | ✓ |
| base.typ のハッシュ固定 | 新しい sha256 を記録して以降のフェーズの基準値にする | |
| Claude 裁量 | diff 貼付を既定に実行時判断 | |

**User's choice:** git diff の実出力を貼る + 既存テスト

### Q4: ja の目視確認

| Option | Description | Selected |
|--------|-------------|----------|
| 不要（フィクスチャで十分） | Phase 27.1 の GATE-01 21 テスト（ja ソース証明 + de の PDF 抽出）がフルスイートの一部として回る。手作業の目視は再現性が低い | ✓ |
| 1 回だけ目視確認 | `sphinx-build -b typstpdf -D language=ja` を手実行して「表 N」を目視記録 | |
| Claude 裁量 | プラン時に決める | |

**User's choice:** 不要（フィクスチャで十分）
**Notes:** 実測 — `docs-pdf` は英語 PDF、`docs-multilang` は en/ja とも HTML のみ。ja の PDF は
どの tox 環境でも目に見えない。

---

## CHANGELOG の粒度

### Q1: 項目化の単位

| Option | Description | Selected |
|--------|-------------|----------|
| ユーザー可視単位で束ねる | TBL-01/02 を 1 項目、docs 系をまとめ、CONF 系は節ごとに分ける。5 項目前後 | ✓ |
| 要件 1 件 = 1 項目 | 7 件を一対一で列挙。台帳との対応は明快だが機能単位が割れる | |
| Claude 裁量 | 可視単位を既定にプラン時に分割 | |

**User's choice:** ユーザー可視単位で束ねる

### Q2: docs 系 2 件の扱い

| Option | Description | Selected |
|--------|-------------|----------|
| DOC-07 のみ載せる | 公開ドキュメントの記述変更は可視なので `### Fixed` に 1 項目。到達不能だった孤児削除（DOC-06）は載せない | ✓ |
| 2 件を 1 項目に | DOC-06/07 をまとめて 1 項目。台帳 7 件が全部 CHANGELOG に現れる | |
| docs 系は載せない | リリースノートはコードの振る舞い変化に限る | |

**User's choice:** DOC-07 のみ載せる
**Notes:** 結果として台帳 7 件のうち DOC-06 だけが CHANGELOG に現れない（意図的）。

### Q3: `### Verified` 節の内容

| Option | Description | Selected |
|--------|-------------|----------|
| 先例と同じ 4 点 | fatal-free / `%PDF` マジック有効 / `unknown_visit` カタログがクリーン / SC#4 不変量。フルスイートと docs は VERIFICATION.md 側に留める | ✓ |
| スイートと docs も記載 | 上記 4 点に加えフルスイート緑・docs ビルド緑も CHANGELOG に書く | |
| Claude 裁量 | 先例踏襲を既定に文面はプラン時 | |

**User's choice:** 先例と同じ 4 点

### Q4: リード段落の軸

| Option | Description | Selected |
|--------|-------------|----------|
| 3 トラック軸 | 設定が効くようになった／captioned table／docs 実測整合 の 3 軸 + 不変量の一行。`[0.6.2]` と同じ体裁 | ✓ |
| アップグレード影響を先出し | 冒頭で 2 件の BREAKING を予告してから 3 トラック要約 | |
| Claude 裁量 | 3 トラック軸を既定に文面はプラン時 | |

**User's choice:** 3 トラック軸

---

## Claude's Discretion

- docs ビルドの合否基準とベースラインの取り方（領域 2 Q2 で明示的に委任）
- `uv.lock` の再生成手順（`uv lock` か `uv sync` か）
- `## [0.6.3]` の日付 = プラン実行日（Phase 23 D-15 の確立済みルール）
- 各項目の具体的な文面（BREAKING ラベルの表記、実測但し書きの織り込み方、before/after 例）
- フェーズ内の作業分割とプラン数
- `## [Unreleased]` 節の保持

## Deferred Ideas

- **`examples/advanced` のビルド不能** — 領域として提示したが未選択。討議中の追加実測:
  同梱 `custom.typ` の `project()` は `papersize`/`fontsize` すら宣言しておらず、非 allowlist の
  5 キーを消しても今度は Typst の `unexpected argument` で落ちる。実測上の修正は `typst_elements`
  を空にすること。pending todo のまま据え置き。
- `docs/usage.rst` / `docs/installation.rst` の orphan クラス（pending todo）
- `derive_typst_lang()` の警告ブロック重複（pending todo、27.1 レビュー IN-01）
- README の依存下限 3 行の同期テスト（Phase 23 D-14 で保留）
- リリースゲートで `pytest.skip` を失敗として扱う仕組み（Phase 23 D-12 で不採用）
