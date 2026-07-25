# Phase 28: v0.6.3 Release Prep + Regression-Gate Close - Pattern Map

**Mapped:** 2026-07-25
**Files analyzed:** 5（CONTEXT.md 実測の「唯一の変更対象」）
**Analogs found:** 5 / 5（すべて同型フェーズ Phase 23 の同ファイルが直接の先例）

## 前提（この phase 固有の事情）

本フェーズは `typsphinx/` を一行も変更しない release-prep フェーズであり、新規モジュール・クラス・
関数は存在しない。したがって「role/data-flow 別にコード analog を探す」という通常の手順は適用でき
ない。**5 つの変更対象ファイルそれぞれについて、最も濃い analog は 1 マイルストーン前の同型フェーズ
`23-v0-6-2-release-prep-regression-gate-close` が実際に生成・変更した同一ファイルそのもの**である。
そのため以下では「role」を通常のコード役割ではなく「リリース成果物の種別」として分類する。

## File Classification

| New/Modified File | Role（成果物種別） | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml` | config（version literal） | batch（1 行の値更新） | `.planning/milestones/v0.6.2-phases/23-.../23-01-PLAN.md` が実施した `pyproject.toml:7` の版バンプ | exact |
| `uv.lock` | config（lockfile regeneration） | batch | 同上 23-01-PLAN.md の `uv lock` → self-entry 更新 | exact |
| `README.md` | doc（Status 行） | batch | 同上 23-01-PLAN.md の `README.md:316` Status 行更新 + `tests/test_readme_version_sync.py` による結合 | exact |
| `CHANGELOG.md` | doc（release notes curation） | batch | 現行 `CHANGELOG.md` の `## [0.6.2]` エントリ（構成・文体）＋ `## [0.6.1]` エントリ（節順序）＋ファイル末尾リンクブロック | exact |
| `28-VERIFICATION.md` | test/evidence-record | batch | `23-VERIFICATION.md`（Phase 23 の同型検証レポート） | exact |

## Pattern Assignments

### `pyproject.toml`（config, batch）

**Analog:** `pyproject.toml:7` 自身の直前の版（`0.6.2`）と、Phase 23 が同じ操作を行った記録
（`23-01-PLAN.md` の `must_haves.artifacts`）。

**現状（実測）**（`pyproject.toml:1-10`）:
```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "typsphinx"
version = "0.6.2"
description = "Sphinx extension for Typst output"
readme = "README.md"
requires-python = ">=3.12"
```

**コピーすべきパターン:** `version = "0.6.2"` の 1 行だけを `version = "0.6.3"` に書き換える。
CONTEXT.md/RESEARCH.md が実測済みの通り、これがファイル内唯一の版リテラル（`[tool.ruff]`/`[tool.mypy]`
の `target-version`/`python_version` は無関係な別物なので触らない）。

**23-01-PLAN.md の must_haves（そのまま踏襲すべき受入形）:**
```
- "pyproject.toml [project].version reads exactly 0.6.2 and remains the sole version literal in the file (SC#1)"
- "uv.lock's typsphinx self-entry reads version = \"0.6.2\" and `uv sync --extra dev --locked` exits 0 (SC#1)"
- "README.md line 316 reads `**Status**: Stable (v0.6.2) - Production ready` (SC#1, D-13)"
```
（Phase 28 では文字列を `0.6.2`→`0.6.3`、行番号を `README.md:315`→実測に置き換えるだけで良い型紙）

**Prohibitions パターン（そのまま踏襲）:** 同プランは「`[tool.ruff]` ignore list に触れない」
「`tox.ini` の `tox-uv~=1.35` ピンに触れない」という禁止事項を明示していた。Phase 28 でも
`pyproject.toml` を開く際は同じ禁止を維持する（CLAUDE.md の modernize-typing-imports todo 未着地の
制約と一致）。

---

### `uv.lock`（config, batch — lockfile regeneration）

**Analog:** Phase 23 の同一操作（`23-01-PLAN.md` "uv.lock's typsphinx self-entry" 要件）。
RESEARCH.md が実測した現状の self-entry:
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

**コピーすべき手順（Phase 23 と同じ判断、RESEARCH.md で再確認済み）:**
```bash
uv lock
uv sync --extra dev --locked
```
`uv lock` は lockfile のみを書き換える最小コマンド。`uv sync --extra dev --locked` が SC#1 の受入
基準そのもの（ドリフトがあれば黙って再ロードせず失敗する）。`pyproject.toml` の版バンプ後、
`uv lock` を明示的に実行しないと self-entry は自動追随しない —— これは Phase 23 の pitfall と同一
構造（Pitfall 2、RESEARCH.md）。

**期待される diff の形（Phase 23 と同じ判断基準）:** `typsphinx` self-entry の
`version = "0.6.2"` → `"0.6.3"` のみが必須。lockfile の `revision` メタデータの化粧的増分は許容。
直接依存（`sphinx`/`docutils`/`typst` の範囲指定）が変わっていたら SC#4 違反の兆候として停止。

---

### `README.md`（doc, batch — Status 行）

**Analog:** `README.md:315`（実測、CONTEXT.md 記載の `:315` と現物 grep 結果 `:315` の食い違いに注意
—— 実行前に `grep -n '\*\*Status\*\*' README.md` で行番号を再実測すること）。

**現状（実測）**（`README.md:310-318`）:
```markdown
See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Status**: Stable (v0.6.2) - Production ready
**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+
```

**コピーすべきパターン:** `Stable (v0.6.2)` → `Stable (v0.6.3)` の 1 語のみ変更。他の行（Python/Sphinx
/Typst のバージョン下限表記）には触れない（README の依存下限同期テストは Phase 23 D-14 でスコープ外
と裁定済み、Deferred 参照）。

**結合テスト（このファイルを pyproject.toml と同時に触らないとスイートが赤くなる拘束）:**
`tests/test_readme_version_sync.py`（Phase 23 D-13 新設、そのまま流用）の核心アサーション:
```python
_STATUS_LINE_RE = re.compile(
    r"\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)"
)

def _extract_readme_status_version() -> str:
    text = README_PATH.read_text(encoding="utf-8")
    match = _STATUS_LINE_RE.search(text)
    assert match, (
        "Could not find a '**Status**: Stable (vX.Y.Z)' line in README.md -- "
        "has the Status line's wording changed?"
    )
    return match.group("version")

def _extract_pyproject_version() -> str:
    with open(PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]
```
（この 2 つの parse 結果を突き合わせて一致を assert する — README と pyproject を分割タスクにすると
その間スイートが赤くなるので、両方を同じ単位で編集すること。）

---

### `CHANGELOG.md`（doc, batch — release notes curation）

**Analog（節構成・文体）:** 現行 `CHANGELOG.md` の `## [0.6.2] - 2026-07-23` エントリ。

**リード段落パターン**（`CHANGELOG.md:10-16`、引用）:
```markdown
## [0.6.2] - 2026-07-23

Rendering-fidelity round 2: closes out the remaining 13 medium/low findings from the v0.6.1 audit
across six root-cause clusters, fixes the typstpdf output-filename bug (Issue #117) and a
nested-master compile-root defect, repairs the Typst Universe (`typst_package`) template path
end-to-end, hardens the builder against silent partial-success, removes two long-dead config
values, and corrects several stale README/CLAUDE.md claims. Zero new runtime dependencies; the
bundled `@preview` version-sync surface is untouched.
```
Phase 28 は D-12 で「3 トラック軸 + 不変量の一行」という同じ体裁を指定済み（RESEARCH.md の
Code Examples ドラフトに完成形あり）。

**BREAKING バレットの書式パターン**（`CHANGELOG.md:18-24`、`## [0.6.2]` の `### Removed`）:
```markdown
### Removed

- **BREAKING: `typst_output_dir` and `typst_author_params` config values removed (CONF-01)** —
  both were registered but never read: ...
  path. Neither ever affected compiled output, so removal changes no build's result; a `conf.py`
  still setting either is silently ignored by Sphinx (unregistered config values produce no
  warning), not an error. No deprecation period.
```
D-01（CONF-05 削除）はこのバレット先頭ボールド型 `- **BREAKING: ... (ID)** — ...` をそのまま踏襲する
（RESEARCH.md 実測: 過去にはセクション見出しサフィックス型もあったが `[0.6.2]` が採用したのはこの型）。

**要件 ID 引用位置パターン:** 太字見出しの直後・閉じ括弧の直前（例 `(CONF-01)`、`(FID-02–FID-06)`）。
D-09 が指示する「読み手はユーザー、ID は末尾の括弧に並べるだけ」という原則と一致。

**節順序の analog 選択（分岐点）:** `[0.6.2]` 自体は Removed → Fixed → Verified の順（KaC 語彙順その
ものではない）。一方 `[0.6.1]`（未読だが RESEARCH.md 実測記載）は Added → Changed → Fixed → Verified
という KaC 語彙順に近い並び。Phase 28 は Added/Changed/Removed/Fixed が全部揃うため、RESEARCH.md は
`[0.6.1]` に近い KaC 語彙順（Added → Changed → Removed → Fixed → Verified）を推奨している —— **analog
として `[0.6.1]` の節順序を優先し、`[0.6.2]` からはバレット書式のみを借りる**、という 2 段構えの
参照になる点に注意。

**リンクブロック analog（ファイル末尾、実測）:**
```
[0.6.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
[0.6.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.1
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.6.2...HEAD
```
Before → After（本フェーズが作る差分、CONTEXT.md/RESEARCH.md 一致）:
- `[0.6.2]:` 行の直前に `[0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3` を挿入。
- `[Unreleased]: .../compare/v0.6.2...HEAD` → `.../compare/v0.6.3...HEAD` に変更。
このリンクブロック更新は Phase 23 では当初スコープ外とし後追い override（`23-VERIFICATION.md` の
`overrides` 参照）で追加されたが、Phase 28 の ROADMAP SC#2 は最初からこれを本フェーズの仕事として
明記しているため、override を経由せず最初のプランに含めてよい。

**RESEARCH.md が用意した完成形ドラフト**（この phase の CHANGELOG エントリはこれをほぼそのまま使える
—— PATTERNS.md では再掲せず、`28-RESEARCH.md` の「Code Examples」節「推奨 `[0.6.3]` CHANGELOG エント
リ」を参照。D-01〜D-12・7 要件中 6 件のカバレッジ済み）。

---

### `28-VERIFICATION.md`（evidence-record, batch）

**Analog:** `.planning/milestones/v0.6.2-phases/23-v0-6-2-release-prep-regression-gate-close/23-VERIFICATION.md`
（読了・構造抽出済み）。

**フロントマター構造パターン**（`23-VERIFICATION.md:1-13`）:
```yaml
---
phase: 23-v0-6-2-release-prep-regression-gate-close
verified: 2026-07-23T00:00:00Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "..."
    reason: "..."
    accepted_by: "yuta (project owner) — via commit ..., matching established v0.6.1 precedent (...)"
    accepted_at: "2026-07-23T07:35:59+09:00"
---
```
Phase 28 でも SC#2（リンクブロック更新）が最初からスコープ内である点が異なるため override は生じない
見込み —— ただし override が発生した場合はこの形式を踏襲する。

**Observable Truths 表の形式パターン**（`23-VERIFICATION.md` 本文の表、抜粋）:
```markdown
| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1 — ... | ✓ VERIFIED | `grep 'version = ' pyproject.toml` → line 7 `version = "0.6.2"` ... |
| 3 | SC#3 — Full Sphinx `doc/` v9.1.0 corpus ... | ✓ VERIFIED | **Re-ran the gate myself** ...
    `uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s`
    → `Corpus tag: v9.1.0` / `Unknown Visit Catalogue: []` / `PASSED` / `1 passed in 13.99s`.
    Zero `SKIPPED` lines; elapsed time (13.99s) is in the plausible real-build range, not sub-second. |
```
**「skip 誤読を防ぐ」証跡の書き方**（D-05/D-12 が要求する形、23 の実例をそのまま踏襲）: コマンド全文
＋生の summary 行（`1 passed in N.NNs`、`SKIPPED` 行の有無）＋所要時間による妥当性チェック（skip は
瞬時、実ビルドは十数秒）をセットで貼る。Phase 28 では加えて RESEARCH.md Pitfall 1 の「フルスイート
実行時に出る `1 skipped` は `test_empty_url_before_after`（`TYPSPHINX_CORPUS_REPORT` env-gated）由来
であり `TestCorpusRenderGate` とは無関係」という区別を明記すること（Phase 23 時点にはこの区別が存在
しなかった、新規に必要な記述）。

**SC#4 diff 貼付パターン**（`23-VERIFICATION.md` 該当行、要約）: `git diff v0.6.1..HEAD -- pyproject.toml`
のような base-ref 限定 diff をそのまま貼り、「`dependencies = [...]` array is byte-identical」のように
自然文で結論を添える。Phase 28 では base ref が `main`（`v0.6.2` タグではない）である点に注意
（RESEARCH.md 実測、`git merge-base main HEAD` = `main`）。

**docs ビルド警告の証跡（Phase 28 固有の追加項目、D-05 で新設・23 に analog なし）:**
23-VERIFICATION.md には docs ビルド証跡の前例がない（D-05 で本フェーズが初めて要求）。この部分は
`28-RESEARCH.md` の「Docs Build Baseline (D-06)」節が実測した生ログをそのまま `28-VERIFICATION.md` に
転記する形になる —— `docs-pdf` は 2 行、`docs-multilang` は 4 行という別々のベースラインを個別に貼る
こと（Pitfall 3 を踏まないため）。

## Shared Patterns

### 「検証機構を持てない数値は載せない」原則
**Source:** Phase 22.4 で確立、`23-CONTEXT.md`/`28-CONTEXT.md` D-11 が踏襲。
**Apply to:** `CHANGELOG.md` の `### Verified` 節、`28-VERIFICATION.md` 全体。
ページ数・ja PDF 目視確認など再現可能なコマンドで裏付けられない主張は書かない。

### prep と publish の分離
**Source:** v0.5.0 Phase 10 / v0.6.1 / v0.6.2 Phase 23 の一貫したパターン。
**Apply to:** すべての 5 ファイル。`git tag` / `.github/workflows/release.yml` 起動 / PyPI / GitHub
Release / マージは一切行わない。Phase 23 の prohibitions 型（`23-01-PLAN.md` の `prohibitions` セクシ
ョン）をそのまま流用できる：
```yaml
prohibitions:
  - statement: "No git tag named v0.6.3 (or any other tag) is created or pushed by this plan"
    verification: "`git tag --list 'v0.6.3'` returns empty"
  - statement: "No PyPI upload, no GitHub Release creation, no manual or scripted trigger of .github/workflows/release.yml"
    verification: "`git diff main..HEAD -- .github/workflows/release.yml` is empty; no `gh release`, `twine`, `uv publish`, or `git push --tags` command is run"
  - statement: "No behavior change under typsphinx/ — this plan touches no package source file"
    verification: "`git diff --name-only` for this plan's commits lists no path under typsphinx/"
```

### コーパスゲート実行コマンド
**Source:** `tests/test_corpus_gate.py`（既存資産、変更不要）。
**Apply to:** `28-VERIFICATION.md` の SC#3 証跡。
```bash
uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s
```
`-rs` が skip 理由を summary に強制表示 —— skip とのすり替わりを防ぐ核心（D-12）。

## No Analog Found

該当なし。5 ファイルすべてに Phase 23 の同名ファイルという直接の analog がある。CONTEXT.md/RESEARCH.md
自身が「`typsphinx/` 配下・`docs/` 配下・`examples/` 配下は本フェーズの対象外」と明記しており、これら
のディレクトリに analog を探すこと自体がスコープ逸脱のシグナルになる（プロンプトの "What NOT to do" と
一致）。

## Metadata

**Analog search scope:** リポジトリ直下の 4 ファイル（`pyproject.toml`/`uv.lock`/`README.md`/
`CHANGELOG.md`）＋ `.planning/milestones/v0.6.2-phases/23-v0-6-2-release-prep-regression-gate-close/`
配下の `23-01-PLAN.md` / `23-VERIFICATION.md`。`typsphinx/` 配下・`docs/` 配下・`examples/` 配下は
CONTEXT.md D-04 のフェンスにより検索対象外。
**Files scanned:** 7（変更対象 5 + analog 元 2: `23-01-PLAN.md`, `23-VERIFICATION.md`）
**Pattern extraction date:** 2026-07-25
</content>
