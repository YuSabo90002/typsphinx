# Phase 57: v0.9.0 Release Prep (prep-only) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-16
**Phase:** 57-v0-9-0-release-prep-prep-only
**Areas discussed:** BREAKING の本数と束ね方, 0.8.x→0.9.0 移行ガイド, 未修正欠陥の開示方針, `### Verified` の項目構成

Four gray areas were offered; the owner selected all four. Two areas that would otherwise have been
offered were withheld as already decided: the lead paragraph's headline axis (fixed by ROADMAP SC#2,
"names the registry as the headline") and the diff anchor (measured to coincide, so no choice
exists).

---

## BREAKING の本数と束ね方

### Q1 — `## [0.9.0]` の BREAKING マークは何本にしますか

| Option | Description | Selected |
|--------|-------------|----------|
| 4本すべてに打つ | SC#2 の2件を追加し、既存の OUT-04 / WR-01・CR-01 のマークも残す。SC#2 の "exactly the two" を、記載が無い2件に対する下限と読む | ✓ |
| 2軸に束ねて2本にする | ROADMAP goal 文の "two independent axes" に literal に合わせ、shadow-route 移動と pre-write refusal を子として畳む | |
| SC#2 の2件だけに打つ | 既存2本から `**Breaking:**` を外し通常の `### Changed` 箇条書きに降格 | |

**User's choice:** 4本すべてに打つ
**Notes:** 実測の裏付け — SC#2 が名指しする2件は `CHANGELOG.md` のどこにも書かれておらず、既に Breaking
マークが付いている2件はそれとは別系統。既存2本は「移行しないと無警告で既定テンプレートに落ちる」
「従来成功していた build が停止する」で、どちらも降格すると過小申告になる。

### Q2 — 既に書かれている `## [Unreleased]` の7本をどう扱いますか

| Option | Description | Selected |
|--------|-------------|----------|
| 昇格して不足分を足す | 既存7本を実質そのまま `## [0.9.0]` へ移し、不足の3本を同じ粒度で新規執筆 | ✓ |
| 0.8.0 の尺度に圧縮する | 1本10行以内に圧縮し、詳細は published documentation へのリンクに逃がす | |
| 全面的に書き直す | 既存本文を下書き扱いとし、26件の要件から 0.8.0 と同じ手順で起こし直す | |

**User's choice:** 昇格して不足分を足す
**Notes:** 実測 — 既存の `### Changed` 2本は12行と18行で、`## [0.8.0]` の最長10行より長い。長さの不揃いより
情報の保全を優先。GitHub Release 本文は `scripts/extract_changelog_section.py` でこの節をそのまま使うため、
リンク先に逃がすと届かない読者が出る。

### Q3 — `typst_template_assets` 削除の箇条書きをどのセクションに置きますか

| Option | Description | Selected |
|--------|-------------|----------|
| `### Removed` に置く | 0.7.1 の `typst_authors` 前例と Keep a Changelog の標準セクションに従う。警告 shim の有無も明記 | ✓ |
| `### Changed` に並べる | 4本の Breaking を1セクションに集め、出力再配置の直後に置いて因果を隣接させる | |
| 両方に書く | `### Removed` に本体、`### Changed` に一文の参照 | |

**User's choice:** `### Removed` に置く
**Notes:** 実測 — `## [0.8.0]` に `### Removed` が無いのは候補ゼロだったため。今マイルストーンで削除された
config 値は `typst_template_assets` の1件のみ（`typst_authors` は v0.7.1、`typst_toctree_defaults` は v0.6.3）。

**Area close:** 「次の領域へ」。文面・箇条書きの切り分け・要件ID の付け方は Claude 裁量として記録。

---

## 0.8.x→0.9.0 移行ガイドを書くか

### Q1 — `docs/source/changelog.rst` の「Migrating from 0.8.x to 0.9.0」節を Phase 57 で書きますか

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 57 で書く | 4本の Breaking に対応する節を 0.7.x→0.8.0 と同形式（before/after の code-block 付き）で執筆 | ✓ |
| 誘導文を落とす | ガイドは書かず、`## [0.9.0]` 冒頭から移行ガイドへの誘導文を削る | |
| 短い節だけ書く | code-block なしで、4つの破壊的変更と当たり先ページへのリンクだけの10行程度 | |

**User's choice:** Phase 57 で書く
**Notes:** 実測 — `docs/source/changelog.rst` に `0.9.0` の文字列がゼロ。0.8.0 の分は Phase 51 が書いたが、
Phase 56 は書いていない。0.7.1 / 0.8.0 の冒頭はどちらも published documentation の移行ガイドへ誘導している。

### Q2 — 新しい移行ガイドをテストで拘束しますか

| Option | Description | Selected |
|--------|-------------|----------|
| 実ビルドに縛る | after 側の主張を `two_key_selection_gate` の実測出力パスに紐づけるゲートを追加 | |
| ガイドは縛らない | 0.7.x→0.8.0 ガイドと同じ扱い。移行ガイドは「その版で何が真だったか」を記す履歴文書 | ✓ |
| Claude 裁量 | 拘束の形式をプランナーに任せる | |

**User's choice:** ガイドは縛らない
**Notes:** 反対論として提示した内容 — Phase 56 の一貫方針は「published claim は必ずゲートで縛る」であり、
検証は3件の falsification test で硬化された。実測では `grep -rn "Migrating" tests/*.py` は0件なので、この
決定は現状を変えない。56-CONTEXT の DOC-17 が「履歴リリースノートは書き換えない — その版で真だったことを
記しているのだから」で歴史を除外した線引きの継承として採用。

### Q3 — 移行ガイドの before 側はどこから取りますか

| Option | Description | Selected |
|--------|-------------|----------|
| v0.8.0 タグを実ビルド | worktree を `v0.8.0` (d9523ea) に出し、同じフィクスチャを `-b typst` でビルドして before のファイル木を実測 | ✓ |
| `.planning/` の既存記録から書く | Phase 54 の RED 証跡と書き換えられた32ファイル分の旧アサーションを根拠にする | |
| Claude 裁量 | 内訳をプランナーに任せる | |

**User's choice:** v0.8.0 タグを実ビルド
**Notes:** Q2 でゲートを置かないと決めた以上、精度保証は「書いた時点の実測」だけになる、という筋で選択。
transcript はフェーズの証跡ファイルに残す。

**Area close:** 「次の領域へ」。節の見出し・code-block の内訳・4本の並べ順は Claude 裁量。

---

## 未修正で出す欠陥の開示方針

### Q1 — 54.1-REVIEW WR-02（confdir≠srcdir で republication hole が残る）を CHANGELOG でどう扱いますか

| Option | Description | Selected |
|--------|-------------|----------|
| 主張を条件付きに絞る | pre-write validation の箇条書きに `templates_path` は srcdir 基準であること、`-c`/`--confdir` は対象外であることを一文入れる。レビュアーの推奨最小対応 | |
| v0.8.0 と同じく沈黙 | D-01 の形を繰り返す。記録は todo 台帳と `57-HANDOFF.md` にのみ残し、CHANGELOG には何も書かない | ✓ |
| `### Known Limitations` 節を立てる | 未修正件を CHANGELOG の新規節にまとめて公開 | |

**User's choice:** v0.8.0 と同じく沈黙
**Notes:** 選択肢の説明に反対論を明示した上でのオーナー判断 — (a) レビュアー自身の推奨最小対応が
「CHANGELOG の breaking エントリで carve-out に触れよ」でまさにこのフェーズの仕事であること、(b) v0.8.0 の
4件と違い、今回の沈黙は「言わない」ではなく「広すぎる主張（"template layout is now validated before
anything is written"）をそのまま出す」になること。両方をテーブルに乗せた上で沈黙を選択。

### Q2 — 残り3件の処遇をどうしますか

| Option | Description | Selected |
|--------|-------------|----------|
| docs 2件は直す | 56-REVIEW の2件（404 リンクと stale prerequisites、`docs/source/installation.rst` を含む）を Phase 57 で修正。54.1 WR-01 はコード変更なので todo に残す | ✓ |
| 全部 todo に残す | v0.8.0 D-03 の形。3件すべてを台帳に記録し `57-HANDOFF.md` に列挙、修繕は入れない | |
| 3件とも直す | 54.1 WR-01 の三重警告も含めて閉じる | |

**User's choice:** docs 2件は直す
**Notes:** 決め手 — stale prerequisites は `examples/**/README.md` だけでなく `docs/source/installation.rst:7-8`
にもあり、v0.9.0 を出す瞬間に公開ユーザー文書が `Python 3.9 or higher` / `Sphinx 5.0 or higher` と言うことになる
（`pyproject.toml` は `>=3.12` / `sphinx>=9.1,<10`）。54.1 WR-01 は `typsphinx/builder.py` を触るので prep-only の柵に当たる。

### Q3 — 前提条件（Python / Sphinx の最低版）の文面をゲートで縛りますか

| Option | Description | Selected |
|--------|-------------|----------|
| ゲートを追加する | `test_readme_version_sync.py` と同型のモジュールを追加し、`pyproject.toml` を真値に repo-wide 発見で走査 | |
| 文面を直すだけ | 3ファイルを書き換え、ゲートは作らない | ✓ |
| Claude 裁量 | 実装形式をプランナーに任せる | |

**User's choice:** 文面を直すだけ
**Notes:** 再発リスク（この drift は 0.7.x 時代から3ファイルに残っていた）を提示した上で、prep-only フェーズに
新規テストモジュールを入れない側を選択。発見自体は repo-wide grep（不変式 #4/#11）のまま。

**Area close:** 「次の領域へ」。pending 9件の台帳処遇と `57-HANDOFF.md` への列挙は v0.8.0 D-03 の踏襲として導出決定。

---

## `### Verified` の項目構成

### Q1 — 3項目のままか、wheel 検証を4項目目に追加するか

| Option | Description | Selected |
|--------|-------------|----------|
| 3項目のまま | 0.7.0 / 0.7.1 / 0.8.0 と完全に同じ三項目を維持。wheel 検証は証跡ファイル側に記録 | ✓ |
| wheel 検証を4項目目に追加 | 「実ビルドした wheel がテンプレートバンドルを同梱していることを確認済み」を足す | |
| Claude 裁量 | プランナーに任せる | |

**User's choice:** 3項目のまま
**Notes:** 実測 — 三項目とも今回も成立する（`pyproject.toml` の依存行は1行も動いておらず、動いたのは
`[tool.setuptools.package-data]` の glob のみ。`templates/base.typ` の `@preview` は4本）。この節の性格は
「何が変わらなかったか」であり、リリース間で比較可能であること自体に価値がある、という理由で維持。

### Q2 — CI dispatch は何回にしますか

| Option | Description | Selected |
|--------|-------------|----------|
| 2回に分ける | バンプ前に1回（Phase 54/54.1/55/56 を Windows/macOS レーンに通す）、バンプ後にもう1回を SC#3 の authority に | ✓ |
| 1回だけ | バンプ後のコミットを push して一回 dispatch し authority にする（Phase 52 と同形） | |
| Claude 裁量 | 回数とタイミングをプランナーに任せる | |

**User's choice:** 2回に分ける
**Notes:** 実測 — このブランチの最後のフル CI は `31884774067`（2026-08-15、Phase 53 期）で、Phase 54 / 54.1 /
55 / 56 は Windows/macOS レーンを一度も通っていない。同レーンは v0.7.0 の close で cp1252 欠陥、v0.7.1 の
close でパス区切り欠陥を実際に捕まえている。加えて CI 全ジョブが `uv sync --extra dev --locked` で始まる
（`--locked` は4ワークフロー11ステップ）ため、`uv.lock` 再生成が dispatch より先でないと1件もテストが走らない。

**Area close:** 「CONTEXT.md を書いてよい」。

---

## Claude's Discretion

- `## [0.9.0]` の文面全般、lead paragraph の言い回し、D-02 の昇格後に7本がどう編集されるか、新規3本の
  `### Added` / `### Changed` への振り分け、要件ID の付け方
- 新しい移行ガイドの見出し構成、`code-block:: text` の対の数、4本の破壊的変更の並べ順
- プラン分割と順序、`uv.lock` 再生成の手順（受け入れ: `uv sync --extra dev --locked` green）
- D-15 のマイルストーン差分スイープの機械的手法と、`pyproject.toml` が空 diff でなくなった今
  「新 runtime 依存ゼロ」をどう論証するか
- `tests/test_changelog_page_gate.py:50-64` の `RELEASE_VERSIONS` に `"0.9.0"` をこのフェーズで足すか
- `57-HANDOFF.md` の書式と証跡ファイルの命名（予約名 `57-VERIFICATION.md` は使用禁止）
- 消えた 56-REVIEW の todo 記録を何件に分けて再作成するか、`REQUIREMENTS.md` チェックサムの粒度

## Deferred Ideas

- 54.1-REVIEW WR-02（`templates_path` を `confdir` 基準で解決する修正）— D-09 と prep-only の柵で却下
- 54.1-REVIEW WR-01（三重の "Custom template not found" 警告）— D-10 で却下、`typsphinx/builder.py` 変更が必要
- 前提条件の version-sync ゲート — D-11 で却下、再発リスクを承知の上
- 移行ガイドを縛るテストゲート — D-07 で却下
- `### Known Limitations` 節と公開 GitHub issue — D-09 で却下（3リリース連続）
- 未修正項目の ROADMAP backlog への昇格 — todo 台帳を維持（52-CONTEXT D-03 の実測理由）
