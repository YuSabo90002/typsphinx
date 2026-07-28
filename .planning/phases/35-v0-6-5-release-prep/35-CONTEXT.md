# Phase 35: v0.6.5 Release Prep - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

<domain>
## Phase Boundary

v0.6.5 の prep-only リリース準備。**Requirements: REL-03（publish 半分を除く前半のみ）。**

**In scope:**

- `pyproject.toml:7` の `version = "0.6.4"` → `"0.6.5"`（実測上これが唯一の版リテラル。
  `typsphinx/__init__.py` は `importlib.metadata` 由来なので対象外）+ `uv.lock:1379` 追随
  （受入は `uv sync --extra dev --locked` 緑）
- `README.md:317` の `**Status**: Stable (v0.6.4) - Production ready` → `v0.6.5`
  （`tests/test_readme_version_sync.py` が両者一致を assert — 片方だけ変えるとスイートが赤）
- `CHANGELOG.md` の `## [0.6.5]` エントリ新設（構成は D-01〜D-04）+ 末尾リンクブロックの
  `[0.6.5]` 行追加 + `[Unreleased]` compare の `v0.6.5...HEAD` への繰り上げ（ROADMAP SC#2 明記、
  release-prep 自身の仕事）
- **Phase 34 レビューのテスト系 Warning 3 件（WR-02 / WR-03 / WR-04）のクローズ**（D-05〜D-07）。
  `typsphinx/` は 1 行も触らない — fixture と gate テストのみの追加なので不変量 #3 に抵触しない
- マイルストーン不変量の全差分断定（ROADMAP SC#4）: `git diff` を merge-base `eb696bb`..HEAD
  （実測 33 コミット）に対して取り、新規ランタイム依存ゼロ / `@preview` 未バンプ /
  4 同期面の版文字列未変更を証跡付きで記録
- 実走証跡（ROADMAP SC#3 + D-12）: フル pytest / `black`・`ruff`・`mypy` / フルコーパス
  `-b typstpdf` ゲート + **docs ドッグフーディングビルド 2 種**（`tox -e docs-html` / `docs-pdf`）
- `/gsd-complete-milestone` 向けハンドオフ文書 `35-HANDOFF.md` の作成（D-09）
- 拾わない指摘の todo 化（D-10, D-11）: WR-01 と `release.yml` のリリース本文改修

**Out of scope:**

- **publish 一切**（`git tag v0.6.5`、`release.yml` 起動、PyPI、GitHub Release、PR 作成・マージ）
  → `/gsd-complete-milestone`（ROADMAP の prep/publish 柵は絶対）
- `typsphinx/` 配下の変更（マイルストーン不変量 #3）。WR-01 の修正は translator 変更を伴うので
  ここに落ちる（D-05）
- `.github/workflows/release.yml` の改修（D-11 — todo 化して v0.6.6+）
- `docs/` の記述変更（触ると翻訳リポジトリの gettext 追従が付随する。Phase 28 D-04 / 33 と同じ）
- `.planning/REQUIREMENTS.md` の REL-03 チェックボックス・traceability 反転（D-10 — close 側）
- 5 件の pending todo と v2 要件（`.planning/REQUIREMENTS.md` § Out of Scope で既決）
- 30.1 レビューの 3 Warnings（同 § Out of Scope で既決）
- 版番号そのものの見直し（0.6.5 は ROADMAP SC#1 固定）
- CHANGELOG の過去バージョンエントリの改変（履歴）

</domain>

<decisions>
## Implementation Decisions

### CHANGELOG `## [0.6.5]` の構成

- **D-01: `### Fixed` 本文は一般文＋括弧で代表例を添える形にする。** 実測では報告(999.1)が
  挙げた「トップレベル段落で text の直後に inline math」の形（空白なし形を含む）は修正前から
  緑で、赤だったのは箇条書き項目 / field body（`confval` の `:type:` / `:default:`）/
  定義リストの term / list item 内の display math / inline math 単独の list item。
  「テキストの直後の inline math（箇条書き項目や定義リストの用語など）」の形で 1 行に収め、
  文脈の全列挙はしない。**BREAKING ラベルは立てない**（純粋なバグ修正。壊れる利用者はいない）。

- **D-02: display math（list item 内の `.. math::`）は inline math と同じ bullet に含める。**
  ユーザーから見れば「リスト項目内の数式でビルドが落ちる」という同一の変化なので束ねる
  （前例 Phase 33 D-09 の粒度規則: ユーザー可視の変化単位で束ね、要件 ID は末尾括弧）。
  `visit_math` と `visit_math_block` という実装上の 2 ハンドラ分割は CHANGELOG に出さない。

- **D-03: 節構成はリード段落 + `### Fixed` + `### Verified` の 2 節。** 0.6.1 / 0.6.3 / 0.6.4 の
  いずれもリード段落 + Verified を持つ前例に揃える。リードの軸は「inline/display math の
  セパレータ欠落によるコンパイル中断の修正 + ランタイム変更は translator の 1 箇所のみ」。

- **D-04: `### Verified` は不変量 2 点 + フルコーパスゲートの 3 点。** 新規ランタイム依存ゼロ /
  `@preview` 4 面の版文字列未変更 / フルコーパス（Sphinx v9.1.0 `doc/`）の `-b typstpdf`
  再走が fatal-free。今回は translator を触っているので Phase 23/28 のコーパス系を載せる根拠が
  立つ（Phase 33 D-03 が載せなかったのは `typsphinx/` 変更ゼロだったため）。
  GATE-01 fixture の RED→GREEN 記録は Verified に**載せない**（テストの話はユーザー可視でない）。

### Phase 34 レビュー 4 Warning の扱い

- **D-05: テスト系 3 件（WR-02 / WR-03 / WR-04）のみ Phase 35 で閉じ、WR-01 は todo 化する。**
  WR-02〜04 は fixture / gate テストの追加だけで `typsphinx/` 無変更なので不変量 #3 に抵触
  しない。WR-01（`visit_math_block` の既存の無条件 `"\n\n"` と新規フラグの二重分離で空行が
  1 本余分）は Typst 上は無害な冗長性だが translator 変更を伴い、GATE-01 fixture の期待文字列と
  フルコーパスゲートの再走が必要になる — リリース直前に出力形状を変えるリスクを取らない。

- **D-06: WR-02 は既存 fixture に Construct G を追加して閉じる。**
  `tests/fixtures/inline_math_after_text_render_gate/index.rst` に「list item 内の `:label:`
  付き `.. math::`」を追加し、mitex / native 両テストに assertion を足す。別 fixture を新設すると
  `sphinx-build` の実走が 2 回分増えるため、既存の 6 構成（A〜F）と同じ場所に集約する。

- **D-07: テスト 3 件は版バンプの前の独立プランとして実行し、ROADMAP の SC は増やさない。**
  Phase 35 の SC#1〜#4 はいずれもテスト追加に言及していないので、REL-03 スコープ外の付随作業と
  して本 CONTEXT に明記した上で先に緑にし、その後の版バンプ / CHANGELOG / SC#3 実走証跡が
  最終的な緑を一度で担保する。ROADMAP に SC#5 を追加してフェーズ境界を公式に広げることはしない。

### `/gsd-complete-milestone` への申し送り

- **D-08: 2 リポジトリタグ（v0.6.4 D-07 の standing cost）は v0.6.5 でも守る。** 実測で翻訳
  リポジトリ `typsphinx-doc-translations` のタグは `v0.6.4` のみ、RTD の en `stable` も tag
  `v0.6.4`（identifier `2bf6ef3`）。今回 `docs/` は 1 行も変わっていないので翻訳側の内容は同一
  だが、タグを打たないと `/ja/stable/` のサイト上の版表示が `/en/stable/` とずれる。例外を
  作らず、submodule バンプ + `v0.6.5` タグを打つ。

- **D-09: 専用の `35-HANDOFF.md` を作る。** Phase 33 の `33-HANDOFF.md` 前例を踏襲。Phase 35 の
  SC にハンドオフ項目はないが、`/gsd-complete-milestone` がそれ 1 枚を読めば済むチェックリストと
  して独立ファイルにする。収載すべき既知項目は `<specifics>` 参照。

- **D-10: WR-01 の todo ファイルは Phase 35 で作成し、REL-03 のチェックボックス反転は close 側に
  残す。** 拾わない決定をその場で記録して落とさないため todo は今書く。`.planning/REQUIREMENTS.md`
  の REL-03 は実測で `[ ]` / traceability「Pending」だが、prep 完了時点ではまだ publish して
  いないので従来どおり ship/complete-milestone で反転させる。

- **D-11: `release.yml` のリリース本文改修は v0.6.5 では行わず、todo に落とす。** 実測: v0.6.4 の
  リリース本文は 308 行で、うち 1〜296 行が `release.yml` の "Generate release notes" ステップの
  `git log $PREV_TAG..$TAG --pretty="- %s (%h)"` によるコミット羅列（`docs(33-04): …` のような
  planning コミットを含む）。297〜303 行が Installation、304〜308 行が `generate_release_notes:
  true` による GitHub 自動生成分（What's Changed の PR 1 行 + Full Changelog リンク）——
  **自動生成は既にコンパクトで、肥大の原因は自前の `git log` ブロック**。
  todo に記録する設計方針: `git log` ブロックを廃し、`CHANGELOG.md` から `## [X.Y.Z]` 節だけを
  抽出して本文にし、Installation と `generate_release_notes: true` は残す。
  あわせて記録すべき実測事実: **`release.yml` は `CHANGELOG.md` を一度も読んでいない** —
  Phase 33 CONTEXT の「`[0.6.4]` エントリが GitHub Release body の単一ソース」という記述は
  実態と食い違っている（この todo が解消して初めて成立する）。

### 実走証跡の範囲

- **D-12: SC#3 名指しの 3 種に docs ドッグフーディングビルド 2 種を足す。** フル pytest /
  `black`・`ruff`・`mypy` / フルコーパス `-b typstpdf` ゲート に加えて `tox -e docs-html` と
  `tox -e docs-pdf` を実走する（Phase 28 D-05 と同じ 3 点セット + docs の前例）。translator を
  触ったマイルストーンなので、自分の docs が `typstpdf` で実際にビルドできることまで確認する。

### Claude's Discretion

以下はプラン/実行時に Claude 裁量で決めてよい:

- CHANGELOG `[0.6.5]` の具体的な文面・リード段落の言い回し・要件 ID の付け方
- WR-02/03/04 の assertion の具体的な文字列（レビューの Fix 欄に候補あり）と Construct G の
  reST の書き方
- フェーズ内のプラン分割（D-07 は「テスト → 版バンプ/CHANGELOG → 証跡」の順序だけを固定する）
- `35-HANDOFF.md` の形式・見出し構成
- `uv.lock` の再生成手順（受入は `uv sync --extra dev --locked` 緑）
- 2 件の todo ファイル（WR-01 / `release.yml`）の文面・frontmatter・ファイル名
- 実走証跡の記録先（`35-VERIFICATION.md` は verify の予約名なので、プランが証跡を積むなら
  別名にするか、事前バックアップ + 事後再結合を計画すること）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 変更対象ファイル

- `pyproject.toml` §`[project]` `:7` — `version = "0.6.4"`（実測: 唯一の版リテラル）
- `uv.lock` `:1379` — `typsphinx` の `version = "0.6.4"`。版バンプに追随して再生成
- `README.md:317` — `**Status**: Stable (v0.6.4) - Production ready`
- `CHANGELOG.md` — `## [Unreleased]` の下に `## [0.6.5]` 新設。`## [0.6.4]`（リード段落 +
  Added/Changed/Removed/Fixed/Verified）と `## [0.6.1]`（小規模リリースのリード + Fixed +
  Verified）が体裁の直接の見本。末尾リンクブロック（`[0.6.4]: …/releases/tag/v0.6.4` 以下 +
  `[Unreleased]: …/compare/v0.6.4...HEAD`）の更新も本フェーズの仕事
- `tests/fixtures/inline_math_after_text_render_gate/index.rst` — Construct A〜F（D-06 で G 追加）
- `tests/test_inline_math_after_text_render_gate.py` — 345 行、mitex / native の 2 テスト
  （D-06 で両方に assertion 追加、WR-03 / WR-04 も同ファイル）

### ゲートと不変量

- `tests/test_readme_version_sync.py` — README Status 行と `pyproject.toml` version の一致を
  assert（版バンプで README を忘れると赤）
- `tests/test_preview_version_sync.py` — `@preview` 4 面同期（`typsphinx/writer.py` /
  `typsphinx/template_engine.py` / `typsphinx/templates/base.typ` / `examples/**/*.typ`）
- `tests/test_corpus_gate.py` — フルコーパス `-b typstpdf` ゲート（`-m slow`）
- `.planning/REQUIREMENTS.md` — REL-03 本文（2 リポジトリタグの standing cost 含む）、
  § Out of Scope（5 todo / v2 要件 / 30.1 Warnings が既決で対象外）、§ Traceability
- `.planning/ROADMAP.md` §Phase 35 — SC#1〜SC#4 と prep/publish 柵（`git rev-parse` で
  merge-base `eb696bb`、実測 33 コミット）

### 前フェーズの決定・申し送り（ハンドオフ素材）

- `.planning/phases/34-inline-math-after-text-separator-fix/34-REVIEW.md` §Warnings —
  WR-01（`translator.py:4079-4088`）/ WR-02（`:4046-4055`）/ WR-03 / WR-04。各節の **Fix** 欄に
  具体的な assertion 候補まで書かれている（D-05〜D-07 の実装素材）
- `.planning/phases/34-inline-math-after-text-separator-fix/34-VERIFICATION.md` —
  5/5 SC 検証済み。SC#3/SC#4 の証跡の書き方（逐語コマンド + 出力転記）の見本
- `.planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md` —
  RED→GREEN の記録形式
- `.planning/milestones/v0.6.4-phases/33-v0-6-4-release-prep/33-CONTEXT.md` — 同型フェーズの
  直近の先例（CHANGELOG 構成の決め方 / Verified の線引き / ハンドオフ項目の並べ方）
- `.planning/milestones/v0.6.3-phases/28-v0-6-3-release-prep-regression-gate-close/28-CONTEXT.md`
  — D-04 のファイル最小主義、D-05 の証跡 3 点セット（D-12 の前例）
- `.planning/STATE.md` §Accumulated Context / §Deferred Items — standing decisions と
  据え置き項目の一覧

### リリース機構（D-11 の todo 素材、本フェーズでは変更しない）

- `.github/workflows/release.yml` §`create-release` / "Generate release notes" ステップ —
  肥大の原因である `git log` ブロックと `generate_release_notes: true` の併用箇所

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`CHANGELOG.md` の `## [0.6.1]` エントリ** — 小規模リリース（リード段落 + Fixed + Verified）の
  体裁として今回の最も近い見本。`## [0.6.4]` は節数が多い側の見本。
- **`tests/test_readme_version_sync.py` / `test_preview_version_sync.py` / `test_corpus_gate.py`**
  — SC#1 / SC#3 / SC#4 の判定本体。追加実装は不要、実走と証跡採取のみ。
- **34-REVIEW.md の Fix 欄** — WR-02/03/04 それぞれに具体的な assertion 文字列の候補が書かれて
  いる。ゼロから設計する必要はない。
- **逐語のコマンド + 出力転記**（Phase 29 D-15 形式）— SC#3 / SC#4 の証跡の記録形式。

### Established Patterns

- **prep と publish の分離** — 最終フェーズは版バンプ + CHANGELOG まで。不可逆な publish は
  `/gsd-complete-milestone`。
- **触るファイルを最小に保つ**（Phase 28 D-04 の 4 ファイル主義）。今回はテスト 2 ファイル +
  HANDOFF + todo 2 件が加わる分だけ広いが、`docs/` と `typsphinx/` は触らない。
- **GATE-01 の標準**（v0.6.0 以降）— ノードハンドラ変更は実コンパイル回帰 fixture を伴う。
  本フェーズは translator を触らないので新規 GATE-01 は不要、既存 fixture の穴埋めのみ。
- **honest-verifier 規約** — 直接証拠なしに真を断定せず、満たせない基準は満たせないと書く。

### Integration Points

- **`/gsd-complete-milestone`** — 本フェーズの `[0.6.5]` エントリと `35-HANDOFF.md` が向こう側の
  入力。tag / PyPI / GitHub Release / PR マージ / 翻訳リポジトリの第 2 タグ / REQUIREMENTS の
  帳簿はすべて向こう側。
- **`release.yml`** — tag `v0.6.5` push で発火。本フェーズでは触れないし起動しない。
  実測: 現状このワークフローは `CHANGELOG.md` を読まず、リリース本文は `git log` から作られる。
- **RTD（オーナー手動、post-tag）** — 親 / 翻訳リポジトリの両プロジェクトで `stable` が
  `v0.6.5` に再ビルドされることの確認。Default Version は v0.6.4 close 時に両方 `stable` へ
  flip 済み（STATE.md 実測）なので、今回 flip 作業は発生しない見込み。

</code_context>

<specifics>
## Specific Ideas

### 討議中に実測した事実（プランはこれを前提にしてよい）

| 主張 | 実測結果 | 影響 |
|---|---|---|
| 版リテラルの所在 | `pyproject.toml:7` のみ | バンプ対象は 1 箇所 + `README.md:317` + `uv.lock:1379` |
| CHANGELOG 末尾 | `[0.6.4]` 行まで存在、`[Unreleased]: …/compare/v0.6.4...HEAD` | `[0.6.5]` 行追加 + compare 繰り上げ |
| マイルストーン差分 | merge-base `eb696bb`、実測 33 コミット。非 planning の変更は `typsphinx/translator.py` +45 行 / `tests/test_inline_math_after_text_render_gate.py` 345 行 / fixture 2 ファイル（計 473 挿入・0 削除） | SC#4 の diff 範囲。削除ゼロなので不変量の断定は容易 |
| 修正前から緑だった形 | fixture Construct A（トップレベル段落、`text\ :math:`x`\ text` を含む） | D-01 の文面の根拠 |
| 赤だった形 | Construct B（箇条書き項目）/ C（confval の field body）/ D（定義リストの term）/ E（list item 内の display math）/ F（inline math 単独の list item） | D-01 / D-02 |
| Phase 34 レビュー | critical 0 / warning 4、`status: issues_found` のまま未対応 | D-05 |
| 翻訳リポジトリのタグ | `typsphinx-doc-translations` は `v0.6.4` のみ | D-08 |
| RTD の版 | en `stable` = tag `v0.6.4`（identifier `2bf6ef3`）、`/en/stable/` `/ja/stable/` とも 200 | D-08 |
| 今回の `docs/` 差分 | ゼロ（`git diff --name-only … -- docs/` が空） | D-08 の「内容は同一」判断の根拠 |
| v0.6.4 リリース本文 | 308 行。1〜296 行 = `release.yml` の `git log` 羅列、297〜303 = Installation、304〜308 = GitHub 自動生成（PR 1 行 + Full Changelog） | D-11 |
| REQUIREMENTS の状態 | MATH-01 は `[x]` / traceability「Complete」、REL-03 は `[ ]` /「Pending」 | D-10 |

### `35-HANDOFF.md` に収載すべき既知項目（形式は Claude 裁量）

1. PR 作成 → マージ（`/gsd-complete-milestone`）
2. tag `v0.6.5` push → `release.yml` → PyPI + GitHub Release
3. **翻訳リポジトリ `typsphinx-doc-translations` にも submodule バンプ + `v0.6.5` タグ**
   （D-08 / v0.6.4 D-07 standing cost — `/ja/stable/` はこちらのタグに解決）
4. tag ビルド後、両プロジェクトの `stable` が `v0.6.5` で緑になっていることの確認
   （RTD の公開 API は認証不要。Default Version の flip は v0.6.4 close で済んでいる見込み）
5. `.planning/REQUIREMENTS.md` の REL-03 チェックボックス + traceability の反転（D-10）
6. 本フェーズで新設する 2 件の todo（WR-01 / `release.yml` リリース本文）が
   `.planning/todos/pending/` に残っていることの確認 — v0.6.6 のスコープ候補

</specifics>

<deferred>
## Deferred Ideas

- **WR-01: `visit_math_block` の余分な空行**（`typsphinx/translator.py:4079-4088`）— 既存の
  無条件 `"\n\n"` と新規の `list_item_needs_separator` フラグが二重に分離し、block math の後に
  空行が 1 本余分に出る。Typst 上は無害だが、他のブロック系ハンドラと形が違い、今後の
  emitted-`.typ` の差分にノイズとして残り続ける。D-05 により Phase 35 では拾わず todo 化。
  修正案はレビューの Fix 欄にある 2 通り（新規ブロックを落とす / 既存 `"\n\n"` を
  `not self.in_list_item` で条件化する）。

- **`release.yml` のリリース本文改修**（D-11）— `git log` ブロックを廃し `CHANGELOG.md` の
  `## [X.Y.Z]` 節を抽出して本文にする。Installation と `generate_release_notes: true` は残す。
  v0.6.5 では見送り、todo 化して v0.6.6+ へ。

### Reviewed Todos (not folded)

`todo.match-phase 35` は 5 件を返したが、いずれも `.planning/REQUIREMENTS.md` § Out of Scope で
**既に対象外と決まっている**ため、今回改めて折り込みの可否は問わなかった:

- `2026-07-22-add-sphinx-linkcheck-ci-job.md`（score 0.6）— Future LNK-01 として据え置き
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`（0.6）— ソース変更を要し不変量 #3 で対象外
- `2026-07-22-citation-node-support-untracked.md`（0.4）— 同上
- `2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`（0.4）— 同上
- `2026-07-25-derive-typst-lang-duplicated-warning-block.md`（0.4）— 同上

- **30.1 レビューの 3 Warnings**（`contributing.rst` のツールチェーン導入手順欠落 /
  `docs/source/_typst/custom_template.typ` が `@preview` 同期ガード外の第 4 サイト /
  翻訳リポジトリ manifest のテスト未カバー）— REQUIREMENTS § Out of Scope で v0.6.5 対象外。

</deferred>

---

*Phase: 35-v0.6.5 Release Prep*
*Context gathered: 2026-07-28*
