# Phase 23: v0.6.2 Release Prep + Regression-Gate Close - Research

**Researched:** 2026-07-23
**Domain:** Release engineering / CHANGELOG curation / regression-gate execution (no source-behavior change)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**CHANGELOG `[0.6.2]` の粒度と構成**

- **D-01: `[0.6.2]` エントリは根本原因クラスタ単位で束ねる.** FID-02..FID-14 を 13 行に個別列挙せず、監査クラスタ A–F 相当の単位で 1 項目にまとめ、末尾の括弧に要件 ID レンジ（例 `(FID-02–FID-06)`）を並べて追跡性を保つ。読み手はユーザーであり FID 番号を知らないため、「何が見た目で直ったか」を単位にする。全体で 10–12 項目前後を目安とする。
- **D-02: `### Verified` 節を置く（`[0.6.1]` / `[0.6.0]` 踏襲）.** コーパスゲートの結果（fatal-free、`%PDF` マジック有効、`unknown_visit` カタログがクリーン）と SC#4 不変量の確認をここに書く。
- **D-03: Phase 22.4（README/CLAUDE.md の実測乖離解消、DOC-01..05）を CHANGELOG に載せる.** 単なる誤字修正ではなく「誤った情報の訂正」だから。
- **D-04: D-03 の項目は `### Fixed` に 1 項目として置く.** `### Documentation` 節は新設しない。

**user-visible な破壊的変更の見せ方**

- **D-05: `typst_output_dir` / `typst_author_params` の削除（22.2 CONF-01）は `### Removed` に置き、BREAKING ラベルを立てる**（オーナー裁定 2026-07-23）。実測の但し書き: 削除後もこの 2 つが `conf.py` に残っていると Sphinx は警告すら出さず完全に無音で無視し `build succeeded` する。かつ両者は削除前から出力に一切反映されていなかった dead config なので実際の振る舞いは変わらない。この事実を BREAKING 項目の本文にどう織り込むかはプラン時の文面判断に委ねるが、BREAKING ラベルは必ず立てる。
- **D-06: Issue #117 の出力ファイル名変更は before/after の具体例付きで提示する.** `typst_documents = [("index", "mydoc", ...)]` に対し `index.pdf` → `mydoc.pdf` という実例を示し、項目先頭を太字見出しにして他の修正に埋もれないようにする。
- **D-07: #117 は BREAKING 扱いにしない — バグ修正として書く**（オーナー裁定）。
- **D-08: SemVer に関する注記は一切入れない**（オーナー裁定）。BREAKING を立てつつ版が 0.6.2（パッチ）である点について説明行を付けない。版番号の見直し（0.7.0 案）も採らない。

**回帰ゲート（SC#3）の実行と証跡**

- **D-09: 既存の `tests/test_corpus_gate.py` を `pytest -m slow` で回す.** 手動 `sphinx-build` は行わない。追加コードゼロ。
- **D-10: 証跡は `23-VERIFICATION.md` に集約する.** 専用の `23-GATE.md` は作らない。
- **D-11: ページ数は CHANGELOG に載せない.** 検証機構を持てない数値はドキュメントに置かない原則を CHANGELOG にも適用する。テストが assert する事実（fatal-free / `%PDF` マジック有効 / `unknown_visit` カタログがクリーン）はそのまま書いてよい。
- **D-12: ゲートが skip ではなく実際に pass したことを明示的に確認する.** `pytest -m slow -rs` で実行し、`1 passed`（`skipped` ではない）と読める生ログを `23-VERIFICATION.md` に貼る。テスト側にコードを追加してリリース時 skip を失敗にする案は不採用。

**版バンプの同期範囲と日付**

- **D-13: `README.md:316` の Status 行を `Stable (v0.6.2)` に更新し、あわせて `README.md:316` と `pyproject.toml` の `version` の一致を assert する同期テストを新設する.** 雛形は `tests/test_preview_version_sync.py`。
- **D-14: 同期テストのスコープは Status 行のリリース版のみ.** `README.md:37-39`（Requirements 節）と `README.md:317`（フッタ）の依存下限 3 種は対象外 — 実測で pyproject.toml と一致しており、乖離したのは Status 行だけ。
- **D-15: `## [0.6.2] - 2026-07-23`（プラン実行日）で日付を確定させる.** `- Unreleased` のまま残す案は不採用。*(プラン実行日が 2026-07-23 でない場合は、その実行日を使う。)*

### Claude's Discretion

- `uv.lock` の再生成手順 — `uv lock` か `uv sync` か。SC#1 の受入は `uv sync --locked` が緑になること。
- `## [Unreleased]` 節の保持 — Keep a Changelog 標準どおり `[0.6.2]` の上に空の `[Unreleased]` を残す想定。
- `[0.6.2]` 冒頭のリード文（マイルストーン要約段落）の文面 — `[0.6.0]`/`[0.6.1]` が持っている 3–5 行の段落。今回も置く想定で、文面はプラン時に確定してよい。
- D-05 の BREAKING 項目の具体的な文面（ラベル表記の形式、実測の但し書きをどこまで織り込むか）。
- SC#4 不変量の確認手段 — `git diff` による依存 / `@preview` 3-way 同期面の差分ゼロ確認と、既存 `tests/test_preview_version_sync.py` の緑をもって足りる想定。
- フェーズ内の作業分割と順序（版バンプ → CHANGELOG → 同期テスト → ゲート実走 の順が自然）。

### Deferred Ideas (OUT OF SCOPE)

- README の依存下限 3 行（`:37-39` / `:317`）の同期テスト — 将来 Sphinx / typst-py の下限を上げる作業が発生したときに、同型のテストを足すのが自然な場所。
- リリースゲートで `pytest.skip` を失敗として扱う仕組み — テスト基盤の拡張でありリリース準備フェーズのスコープ外。
- 版番号を 0.7.0 に見直す案 — ROADMAP SC#1 が 0.6.2 を固定している。
- 9 件の候補 todo はすべて誤検出（キーワード一致）— 本フェーズはリリース準備でありソース変更を伴う todo は対象外。
</user_constraints>

<phase_requirements>
## Phase Requirements

No requirement IDs are mapped to Phase 23 in `.planning/ROADMAP.md`/`STATE.md` — it is the prep-only
release/close phase. However, D-01 (locked) makes the **entire v0.6.2 requirement ledger** (23 items in
`.planning/REQUIREMENTS.md`) this phase's de-facto requirement surface: the `[0.6.2]` CHANGELOG entry must
give every one of these 25 IDs complete, traceable coverage with zero silent drops. See the
"Requirement-Ledger → Cluster Mapping" table below for the full ID-to-bullet mapping this research
produced to satisfy that surface.

| ID | Description (one-line, user-visible) | Research Support |
|----|---------------------------------------|------------------|
| FID-02 | Consecutive paragraphs inside a list item no longer run together | Bundled into Cluster A bullet, see mapping table |
| FID-03 | Multiple sibling signatures (overloads) render on separate lines | Bundled into Cluster A bullet |
| FID-04 | Option-group `rubric` heading no longer merges into the first option | Bundled into Cluster A bullet |
| FID-05 | Definition-list term no longer merges onto its definition | Bundled into Cluster A bullet |
| FID-06 | Back-to-back body-less `confval` entries no longer concatenate | Bundled into Cluster A bullet |
| FID-07 | `class `/`exception ` keyword keeps its trailing space | Bundled into Cluster B bullet |
| FID-08 | C/C++ signatures preserve all inter-token spaces | Bundled into Cluster B bullet |
| FID-09 | `:type:`/`:default:` fields render with colon-space and boundaries | Bundled into Cluster B bullet |
| FID-10 | Long inline-literal runs wrap instead of clipping at the margin | Own bullet (Cluster C) |
| FID-11 | Soft/semantic line breaks reflow instead of forcing hard breaks | Own bullet (Cluster D) |
| FID-12 | Codly config wrapper no longer leaks as visible text | Own bullet (Cluster E) |
| FID-13 | External hyperlinks render with distinguishing styling | Bundled into Cluster F bullet |
| FID-14 | `*`/`/` PEP 3102/570 separators no longer inject hover-title text | Bundled into Cluster F bullet |
| PDF-01 | `typstpdf` PDF filename matches the configured target, not the docname | Own bullet, before/after example (D-06/D-07) |
| PDF-02 | Nested-master `#include()`/`image()` paths resolve correctly | Own bullet |
| CONF-01 | `typst_output_dir`/`typst_author_params` removed (dead config) | `### Removed`, BREAKING (D-05) |
| CONF-02 | `typst_package`-alone path fixed end-to-end (4 sub-bugs) | Own bullet |
| CONF-03 | Config→output regression fixture (GATE-01) | Folded into CONF-02's bullet as a parenthetical |
| WR-01 | `typstpdf` no longer reports success while silently skipping a master | Own bullet (with WR-02) |
| WR-02 | Nested-master render gate decoupled from `typst-py` error strings | Folded into WR-01's bullet as a parenthetical |
| DOC-01 | Unverifiable numeric claims removed from README | Bundled into DOC bullet |
| DOC-02 | Configuration Options reworded as explicitly partial, links to real docs | Bundled into DOC bullet |
| DOC-03 | Feature/limitation/Status/methodology claims corrected | Bundled into DOC bullet |
| DOC-04 | CLAUDE.md Python-version claims corrected (3.10+ → 3.12+) | Bundled into DOC bullet |
| DOC-05 | Full-text README pass, not ledger-only | Bundled into DOC bullet |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Worktree-isolated execution is the standing mode** for this project (owner decision, 2026-07-20;
  `workflow.use_worktrees: true`, `.claude/settings.local.json` `worktree.baseRef: "head"`). Every executor
  — including for this low-parallelism, mostly-sequential release-prep phase — must provision its own
  worktree venv before running anything: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`,
  then run all subsequent commands via `uv run`. Do not fall back to sequential main-tree execution merely
  because this phase has few parallelizable tasks.
- **Match CI exactly for lint/format/type commands:** `black --check .`, `ruff check .`, `mypy typsphinx/`
  (this phase touches no `typsphinx/` source, so `mypy` is a no-op check, but `black`/`ruff` should still be
  run against the new `tests/test_readme_version_sync.py` file).
- **`tox.ini` pins `tox-uv~=1.35`** deliberately (not `>=1.35,<2`) — do not "fix" this during the version
  bump; it is an intentional workaround for tox's ini-list comma-splitting, unrelated to this phase's scope.
- **`UP006`/`UP035` ruff ignores stay in place** — do not modernize typing imports as a side effect of
  touching any file in this phase; that is explicitly deferred to
  `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`.
- **Line length 88 (black-owned), `E501` ignored in ruff** — applies to the new test file.
- No other CLAUDE.md directive is implicated: this phase touches no `typsphinx/` package code, so the
  builder/writer/translator architecture notes and the `@preview` version-sync hazard section are
  informational context (used to verify SC#4, not to guide new code) rather than constraints on new work.

## Summary

Phase 23 is a release-prep and regression-gate-close phase with **zero source-behavior changes** — every
fact needed to plan it lives in this repository (git history, existing tests, prior phases' CONTEXT/SUMMARY
files) rather than in external libraries or web documentation, matching the research-focus instruction to
ground everything locally. Four concrete artifacts change: `pyproject.toml:7` (version literal), `uv.lock`
(regenerated), `CHANGELOG.md` (new `## [0.6.2]` entry), and `README.md:316` (Status line) — plus one new
test file for the README/pyproject version-sync guard (D-13). A fifth "artifact" is behavioral: running the
existing `tests/test_corpus_gate.py` slow gate and recording its output as `23-VERIFICATION.md` evidence.

The highest-value research output is the **requirement-ledger → CHANGELOG-cluster mapping**: all 25 v0.6.2
requirement IDs map cleanly onto the six audit clusters (A–F) from `17-AUDIT-CATALOGUE.md` plus three
independent fix-groups (Issue #117, dead-config sweep, builder-warning hardening) and one documentation
group — yielding exactly **11 CHANGELOG bullets**, inside D-01's 10–12 target. No requirement ID resists
clean clustering; two IDs (CONF-03, WR-02) are test-infrastructure-only and are folded as parentheticals
into their sibling bullet rather than getting independent bullets, since neither is independently
user-visible.

**Primary recommendation:** Execute in the order D-16 (Claude's Discretion) already suggests — version bump
→ CHANGELOG → new sync test → corpus gate — and use the CHANGELOG outline in "Code Examples" below nearly
verbatim; it already satisfies D-01 through D-15 and the full 23-item ledger.

## Architectural Responsibility Map

This phase does not touch application-tier code; the standard browser/API/DB tiers from other project
types don't apply. Adapted for a release-prep phase:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version literal bump | Build/Package metadata (`pyproject.toml`) | Lockfile (`uv.lock`) | `pyproject.toml:7` is the sole version literal (verified); `uv.lock`'s own `typsphinx` self-entry (line ~1379) must follow in lockstep or `uv sync --locked` drifts |
| CHANGELOG curation | Documentation (repo root) | — | Pure prose; no code path reads `CHANGELOG.md` |
| README Status sync | Documentation (repo root) | Test/CI (new sync test) | The new test in `tests/` is the only "code" tier this phase adds, and it exists purely to keep two documentation artifacts from drifting |
| Regression gate execution | Test/CI (`tests/test_corpus_gate.py`) | — | Existing test asset; this phase runs it and records evidence, adds no code |
| Milestone-invariant verification | Test/CI (`tests/test_preview_version_sync.py`) + `git diff` | Build/Package metadata | Confirms the @preview 3-way surface and dependency set are untouched relative to the `v0.6.1` tag |

## Requirement-Ledger → Cluster Mapping (D-01 deliverable)

Source of record for FID cluster membership: `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`
(finding numbers F1–F15; F12/FID-01a is v0.6.1-already-shipped and does NOT appear in v0.6.2's ledger).
Confirmed against `.planning/REQUIREMENTS.md`'s own cluster headings (Block Separation / Signature Spacing /
Margin Overflow / Paragraph Reflow / Codly Config Leak / Inline Styling), which already state the FID↔cluster
mapping explicitly — this table adds the F-number cross-reference and the concrete bundling.

| Cluster / Group | Requirement IDs | Audit F-# | User-visible one-liner | → CHANGELOG bullet |
|---|---|---|---|---|
| A — Block Separation | FID-02, FID-03, FID-04, FID-05, FID-06 | F1, F7, F13, F14, F15 | Paragraphs-in-list-items, sibling signatures, rubric/option headings, definition-list terms, and back-to-back confvals now render with visible separation instead of concatenating | Bullet 1 |
| B — Signature Token Spacing | FID-07, FID-08, FID-09 | F2, F3, F5 | `class `/`exception ` keyword prefix, C/C++ signature tokens, and `:type:`/`:default:` fields keep their spaces and boundaries | Bullet 2 |
| C — Margin Overflow | FID-10 | F6 | Long inline-literal runs wrap within the margin instead of clipping | Bullet 3 |
| D — Paragraph Reflow | FID-11 | F9 | Soft/semantic source line breaks reflow into a justified paragraph instead of forcing ragged hard breaks | Bullet 4 |
| E — Codly Config Leak | FID-12 | F11 | A captioned code block nested in a list item no longer leaks its codly config wrapper as visible text | Bullet 5 |
| F — Inline Styling | FID-13, FID-14 | F8, F10 | External hyperlinks render with distinguishing styling; `*`/`/` PEP 3102/570 separators no longer inject their hover-title text inline | Bullet 6 |
| Issue #117 | PDF-01 | — (not an audit finding; builder bug) | Output PDF is now named after the `typst_documents` target, not the source docname | Bullet 7 |
| Nested-master compile root | PDF-02 | — | `#include()`/`image()` paths resolve correctly for a master at a nested docname | Bullet 8 |
| Dead Config Removal | CONF-01 | — | `typst_output_dir`/`typst_author_params` removed (dead, never read) | `### Removed` bullet (BREAKING) |
| `typst_package` Repair | CONF-02, CONF-03 | — | The Typst-Universe-template-only path now builds and compiles with zero errors (4 sub-bugs fixed); a new regression fixture (CONF-03) proves config changes actually affect output | Bullet 9 |
| Builder Warning Hardening | WR-01, WR-02 | — | `typstpdf` no longer reports success while silently skipping a configured master; the nested-master test no longer couples to `typst-py`'s internal error wording | Bullet 10 |
| README/CLAUDE.md Accuracy | DOC-01, DOC-02, DOC-03, DOC-04, DOC-05 | — | Unverifiable numbers removed, Configuration Options reworded as partial, feature/limitation/Status/methodology claims corrected, CLAUDE.md Python floor corrected | Bullet 11 |

**Every requirement ID fits cleanly into a cluster — none resists bundling.** The only judgment calls are
CONF-03 and WR-02, which are test-infrastructure-only (a regression fixture and a test de-coupling,
respectively) with no independently observable user-facing behavior; folding them as parentheticals into
their sibling bullet (CONF-02, WR-01) keeps the ledger fully covered without inflating the bullet count or
implying they are separate user-visible changes.

**Total: 11 bullets** (6 fidelity-cluster bullets + #117 + PDF-02 + dead-config-removal + typst_package-repair
+ builder-warning-hardening + README/CLAUDE.md), inside D-01's 10–12 target, covering all 25 ledger IDs with
zero drops.

## CHANGELOG Structural Template (measured from `CHANGELOG.md`)

- **`## [Unreleased]` is present** at line 8, immediately followed by a blank line 9, then `## [0.6.1] -
  2026-07-20` at line 10. **`## [0.6.2]` must be inserted between lines 9 and 10** (i.e., right after the
  blank line following `## [Unreleased]`, right before `## [0.6.1]`).
- **Section order used by `[0.6.1]`** (the direct template, per D-02/D-04): a 3-5 line lead paragraph, then
  `### Added`, `### Changed`, `### Fixed`, `### Verified` — in that order. `[0.6.0]` uses the same set minus
  `### Changed`/`### Verified` variance (it has `### Fixed` then `### Added` only, no lead-in `### Changed`
  section, but the lead paragraph + heading-level-3 pattern is identical). **Heading level for the version
  header is `##`; sub-sections are `###`.**
- **`### Removed` has never been used in this file before** (confirmed: `grep -n "^### "` over the whole
  file returns Added/Changed/Fixed/Verified/Improved/Documentation/Known Limitations/Technical
  Details/Development Tools/Requirements Status/Testing/Planned for Future Releases/Dependencies — no
  `Removed`). D-05 introduces the first use of this heading in the project's history; Keep a Changelog's
  standard vocabulary (`Added`/`Changed`/`Deprecated`/`Removed`/`Fixed`/`Security`) already includes it, so
  it fits the declared standard (line 5: "based on Keep a Changelog") even though it's a first use here.
- **`BREAKING` has been used exactly twice, in two different formats — neither is a section-only label
  matching D-05's exact need:**
  1. `## [0.4.0]` §"Changed (from v0.3.0)" — a **section-header suffix**: `### Changed (Breaking)`.
  2. `## [0.3.0]` §"Changed (Breaking)" — same section-header-suffix style, is actually the SAME entry
     restated (v0.4.0's changelog duplicates the v0.3.0 entry under its own heading — this project's
     changelog has a known duplication quirk between those two versions, not a new pattern to copy).
  3. `## [0.4.0]` also has a **bullet-level bold prefix**: `- **BREAKING: Unified Code Mode Architecture**
     ([#4](...))`.
  Since D-05's BREAKING item is a single bullet inside a `### Removed` section (not an entire section being
  breaking), the **bullet-level bold-prefix style (`- **BREAKING: ...** — ...`) is the correct precedent to
  follow**, not the section-header-suffix style.
- **Lead-paragraph length/tone:** `[0.6.1]`'s lead is 4 lines, present tense, states the milestone's overall
  before→after framing ("move `typstpdf` output from 'compiles fatal-free' ... to 'renders faithfully to
  the source'") ending with the standing zero-new-deps/version-sync-untouched sentence. `[0.6.0]`'s lead is
  3 lines with the same closing sentence. **Recommend a 4-5 line lead for `[0.6.2]`** following this exact
  template: state the release's overall theme (13 fidelity fixes + PDF/config/builder hardening + release
  close), then close with the same standing zero-new-deps sentence (verified true this phase, see SC#4
  section below).
- **Link-reference style at the bottom of the file:** lines 651-663, one `[X.Y.Z]:
  https://github.com/YuSabo90002/typsphinx/releases/tag/vX.Y.Z` line per released version (oldest at
  bottom), plus a special `[Unreleased]:
  https://github.com/YuSabo90002/typsphinx/compare/vLATEST...HEAD` line. **This phase does NOT add a
  `[0.6.2]:` link line** — that tag does not exist yet (SC#5 scope fence: no tag in this phase). Per the
  existing pattern, the `[Unreleased]` compare-link line should be left as-is (still pointing at
  `v0.6.1...HEAD`) since Phase 23 does not tag; `/gsd-complete-milestone` is the natural place to both cut
  the tag and update this link line to `[0.6.2]:` + advance `[Unreleased]` to `v0.6.2...HEAD`. Flagging this
  as an Open Question below in case the planner wants it addressed now instead.

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** No new runtime or dev dependency is added;
`uv.lock`'s regeneration is a version-literal-only self-entry update (see "`uv.lock` Regeneration" below),
not a dependency change. The Package Legitimacy Gate protocol is skipped per its own trigger condition
("every phase that installs external packages").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Full-corpus regression proof | A new corpus-gate test or manual `sphinx-build` invocation | `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` (existing, `@pytest.mark.slow`) | D-09 is explicit: zero new test code. The existing gate already does tag-resolve → cached-clone → `-b typstpdf` → `%PDF` check → `unknown_visit` catalogue extraction. |
| README/pyproject version-drift guard | A bespoke ad-hoc string check in CI or a pre-commit hook | A new pytest module following `tests/test_preview_version_sync.py`'s exact shape (raw-text/tomllib parse of each file, compare, assert) | D-13 names this file as the explicit template. The project's established convention for "two files must agree on a value" is a dedicated small pytest module, not a script or hook. |
| `pyproject.toml` version parsing in a test | A custom regex over the TOML text | `tomllib.load()` (stdlib, Python 3.12+) | Already proven working in `tests/test_extension.py::test_version_matches_pyproject_toml` — this project's requires-python floor (`>=3.12`) guarantees `tomllib` is always available with zero new dependency. |
| SC#4 invariant confirmation | A new automated CI check | `git diff v0.6.1..HEAD` against the 3-way version-sync files + the already-green `tests/test_preview_version_sync.py` | Claude's Discretion explicitly names this as sufficient; no new tooling needed. |

**Key insight:** every "don't hand-roll" item in this phase is "don't build a new mechanism — this project
already has the exact-shaped precedent, reuse it verbatim." This is a hallmark of a mature, several-releases-in
project; the research value here is entirely in *locating* the precedent, not in evaluating alternatives.

## Version-Sync Test (D-13) — Design

### Template: `tests/test_preview_version_sync.py` structure (read in full)

- **Location convention:** repo-root-relative paths computed via `Path(__file__).resolve().parents[1]`
  (one level up from `tests/`), then joined to each target file. New test should use the identical pattern.
- **Parsing style:** a dedicated `_extract_..._version(s)` helper per file that does a targeted regex match
  on the file's raw text (`path.read_text()`), returning parsed value(s) — never relies on
  `importlib.metadata` or any installed-package introspection.
- **Assertion style:** compare the parsed values directly against each other (not against a hardcoded
  expected literal) so the test only fails on a genuine *divergence*, and stays correct if both values are
  intentionally bumped together. A second guard test confirms neither file is silently missing/empty (so
  two empty results don't vacuously "agree").
- **Naming convention:** module `test_preview_version_sync.py`; test functions
  `test_preview_versions_identical_across_declaration_sites` and `test_all_four_packages_declared` (plain
  functions, no test class, descriptive full-sentence names, no `Test*` class wrapper).

### Concrete parsing targets (verified this session)

| File | Exact current text | Recommended parse |
|------|---------------------|--------------------|
| `README.md:316` | `**Status**: Stable (v0.6.1) - Production ready` | Regex: `r'\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)'` on raw text, capture group `version` |
| `pyproject.toml:7` | `version = "0.6.1"` | `tomllib.load(open(path, "rb"))["project"]["version"]` — **not** a regex; this is the same field `tests/test_extension.py::test_version_matches_pyproject_toml` already parses, so reuse the identical `tomllib` call rather than inventing a new regex for a value that already has a proven stdlib parser |

### Recommendation: new file, not appended to the existing one

**Location: new file `tests/test_readme_version_sync.py`**, not appended to
`tests/test_preview_version_sync.py`. Justification from project convention:

1. `test_preview_version_sync.py`'s own module docstring frames its scope narrowly ("typsphinx declares the
   same four Typst Universe `@preview` package versions... in three separate places") — it is purpose-built
   for the `@preview` 4-package/3-file hazard, not a general "any two files must agree" utility module.
2. The project's existing naming pattern is one small, single-purpose module per drift hazard (e.g.
   `test_builder_output_stem.py`, `test_target_name_render_gate.py` — narrow, descriptively-named files
   rather than a shared "misc sync tests" module).
3. A new `test_readme_version_sync.py` mirrors the naming shape `test_<subject>_version_sync.py`, keeping
   the existing file's `EXPECTED_PACKAGES`/`_PREVIEW_IMPORT_RE` module-level constants uncontaminated by an
   unrelated concern.

### `tomllib` availability confirmed — no new dependency

`tomllib` is **already used** in `tests/test_extension.py:86` (`import tomllib`, stdlib since Python 3.12).
Since `requires-python = ">=3.12"` (verified, `pyproject.toml`), this is available with zero new dependency
in every supported environment. The new sync test can import it directly.

## Corpus Gate Execution Mechanics (D-09/D-12)

### Exact invocation

```bash
pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v
```

- `-m slow` selects the `@pytest.mark.slow`-decorated class (redundant with the explicit node-id but keeps
  the invocation self-documenting and matches D-09's literal wording).
- `-rs` forces pytest to print the skip reason string in the summary — this is what distinguishes a
  genuine `1 passed` from a `1 skipped (Sphinx doc/ corpus unavailable...)` in the captured log (D-12's
  exact concern).
- `-v` gives per-test verbose output (`PASSED`/`SKIPPED` next to the full node id) in addition to the `-rs`
  summary line.

### Conditions under which it calls `pytest.skip`

Exactly one skip path, in the session-scoped `corpus_doc_dir` fixture (`tests/test_corpus_gate.py:102-116`):
`get_or_clone_corpus()` returns `None` (no network, git clone failure, or an unresolvable tag for the
installed Sphinx version) → `pytest.skip("Sphinx doc/ corpus unavailable (no network or clone failure) --
D-05")`. There is also a class-level `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` guard, but `typst` is a
core runtime dependency (`pyproject.toml` `dependencies`), so this never fires in a correctly-provisioned
environment.

### Cached corpus confirmed present and offline-usable

```
$ ls ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc | head -5
Makefile
_static
_templates
_themes
authors.rst
```

**Verified this session:** the cache exists at exactly the path `get_or_clone_corpus()` checks
(`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc`, with `conf.py` present), so `get_or_clone_corpus()`'s
existence check short-circuits and the test runs **fully offline** — no network round-trip needed this
phase.

### Plausible duration

`.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`'s own mechanical
check #5 recorded, for the identical test against the identical cached corpus: `pytest
tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` → **`1 passed in 13.67s`**. Expect a similar
~10-25s runtime this phase (real `sphinx-build` + real `typst.compile()` over ~684 pages, cached corpus, no
clone).

### Distinguishing `1 passed` from `1 skipped` under `-rs`

- **Pass:** `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error
  PASSED` line, plus a `======= 1 passed in N.NNs =======` summary line. No `SKIPPED` line appears anywhere.
- **Skip:** the same node id shows `SKIPPED (Sphinx doc/ corpus unavailable (no network or clone failure) --
  D-05)` (the reason string appears inline because of `-rs`), and the summary reads `======= 1 skipped in
  N.NNs =======`. **The distinguishing text to look for and paste into `23-VERIFICATION.md` is the literal
  word "passed" (not "skipped") in the final summary line, plus the absence of any `SKIPPED` line.**

### Reconciling with the NixOS sandbox constraints (memory file read in full)

**No blocker — the corpus gate is expected to run cleanly regardless of sandbox mode.** The memory file's
documented ELF-exec limitation applies specifically to invoking a **compiled binary entry point via `uv
run`** (e.g., `uv run sphinx-build`, `uv run ruff`) — NixOS can't exec those generic-linux ELF wrapper
scripts directly. `tests/test_corpus_gate.py`'s `_run_corpus_sphinx_build()` helper deliberately avoids this
exact hazard by construction: it invokes `[sys.executable, "-m", "sphinx", "-b", builder, ...]` — the
*already-running* Python interpreter's own `-m sphinx` module form, not a separate `uv run <binary>`
subprocess — and `typst.compile()` runs as a Python C-extension import inside that same interpreter, not as
a subprocess of a compiled binary. This is the identical pattern the memory file explicitly confirms
**does** work in sandbox-on mode: "`uv run python -m pytest tests/test_pdf_render_gate.py -q` is the
authoritative correctness signal (real `sphinx-build → typst.compile() → pypdf`)" and the render-gate
docstring instructs future fixtures to "follow that pattern, never `[\"uv\",\"run\",...]`" — which
`test_corpus_gate.py` already does. Corroborating evidence: the 2026-07-19 audit-catalogue session and the
2026-07-13 memory note both report a full corpus `-b typstpdf` re-run succeeding with 0 fatal errors,
including once explicitly "no outside-sandbox fallback needed."

**Recommended working invocation for the executor** (matches CLAUDE.md's worktree-isolated-execution
convention, if run inside a worktree):

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v
```

If run on the main tree (not a worktree), drop the `uv sync`/`env -u` provisioning step and just run the
`uv run pytest ...` line directly (or `pytest ...` if already inside an activated venv).

## SC#4 Invariant Verification Commands (Claude's Discretion)

**Base ref: the `v0.6.1` git tag** (confirmed present: `git tag -l "v0.6*"` → `v0.6.0`, `v0.6.1`). 301 commits
exist between `v0.6.1` and current `HEAD` (`git log --oneline v0.6.1..HEAD | wc -l` → `301`), spanning
Phases 19 through 22.4.

### 1. Zero new runtime dependencies

```bash
git diff v0.6.1..HEAD -- pyproject.toml
```

Inspect the `dependencies = [...]` array specifically — expect it to be **byte-identical** to `v0.6.1`
(`sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16`) except for the one `version = "0.6.1"` →
`"0.6.2"` line this phase itself changes. Any other line added under `dependencies` is a milestone-invariant
violation.

### 2. No `@preview` version bump

```bash
git diff v0.6.1..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ | grep -E '^[+-].*@preview'
```

Expect **empty output**. Note this command intentionally does NOT require the three files to be
byte-identical overall — `typsphinx/writer.py` legitimately changed during Phase 22.1 (the
`_compute_template_import_path` fix, unrelated to `@preview` versions) — it isolates only lines touching an
`@preview/...` string. Cross-check with the always-green existing test:

```bash
pytest tests/test_preview_version_sync.py -v
```

### 3. 3-way version-sync surface untouched (in the sense that matters)

The phrase "untouched" in `STATE.md`/`REQUIREMENTS.md` means "the `@preview` version declarations stay in
lockstep," not "these three files have zero diff" — confirmed by the fact that `writer.py` legitimately
changed in Phase 22.1 without being flagged as an invariant violation anywhere in that phase's
CONTEXT/VERIFICATION. Command #2 above plus the passing `test_preview_version_sync.py` together constitute
sufficient proof; no additional tooling is needed (matches Claude's Discretion's own text).

## `uv.lock` Regeneration (Claude's Discretion)

### `uv.lock` has its own version-literal self-entry that must be bumped too

```
[[package]]
name = "typsphinx"
version = "0.6.1"          # <- line ~1379, must become "0.6.2"
source = { editable = "." }
dependencies = [
    { name = "docutils" },
    { name = "sphinx" },
    { name = "typst" },
]
```

This is **not** auto-derived from `pyproject.toml` at read time — `uv.lock` is a resolved snapshot, so
bumping `pyproject.toml:7` alone does NOT update this line. It requires an explicit `uv lock` (or `uv sync`,
which calls lock internally when the lock is stale) run.

### `uv lock` vs `uv sync` — recommendation

**Run `uv lock` first (updates only `uv.lock`, no environment mutation), then verify with `uv sync
--locked`** (SC#1's literal acceptance criterion) as a separate step:

```bash
uv lock
uv sync --extra dev --locked
```

Rationale: `uv lock` is the minimal, single-purpose command that produces exactly the artifact SC#1 needs
regenerated; running `uv sync` (without `--locked`) would ALSO perform first-run environment installation
work, which is unnecessary noise for a version-bump-only change and conflates "did the lock regenerate
correctly" with "did the venv install correctly." Using `--locked` on the verification step additionally
fails loudly (rather than silently re-locking) if `uv lock` in step 1 did not fully resolve the drift — a
tighter check than a bare `uv sync`.

### Expected diff shape

For a **pure version bump of the project's own package** with no dependency-range changes, expect `uv.lock`
to show a small, focused diff:

- The `typsphinx` self-entry's `version = "0.6.1"` → `"0.6.2"` (required).
- Possibly the lockfile's own `revision` counter incrementing (uv.lock's internal format metadata, not a
  dependency change) — **cosmetic, not a milestone-invariant concern.**
- **Watch for (and flag if seen):** any *transitive* dependency's resolved version changing due to a newer
  compatible release having appeared on PyPI since the last lock (e.g. a patch-level Sphinx/docutils/pytest
  release within the pinned range). This is incidental upstream drift, not something this phase intends to
  cause — if it appears, note it but do not treat it as blocking; it's outside SC#4's stated invariant
  (SC#4 is about typsphinx's OWN runtime deps and `@preview` versions, not transitive resolution drift).

**NixOS environment note:** `uv lock`/`uv sync` perform dependency resolution and metadata I/O only — no
compiled-binary execution — so neither the ELF-exec sandbox constraint nor the worktree-isolation editable-
install hazard documented elsewhere in this project's memory apply to this step.

## Common Pitfalls

### Pitfall 1: Treating a corpus-gate `SKIPPED` as acceptable evidence

**What goes wrong:** Pasting a `pytest -m slow` run's output into `23-VERIFICATION.md` without checking
whether the single test actually ran or silently skipped (D-05's skip condition: corpus unavailable).
**Why it happens:** Both outcomes exit 0 and both print `1 <passed|skipped> in N.NNs` — easy to eyeball-scan
past the word.
**How to avoid:** Always run with `-rs` (forces the skip reason into the summary) and grep the summary line
for the literal word `passed` before recording it as evidence (D-12).
**Warning signs:** A suspiciously fast run (a skip is near-instant; a real corpus build takes ~10-25s).

### Pitfall 2: Forgetting `uv.lock`'s own embedded version literal

**What goes wrong:** Bumping `pyproject.toml:7` and assuming `uv sync --locked` will pass unchanged,
without realizing `uv.lock` independently pins `typsphinx`'s own version at line ~1379 and will report the
lock as stale/out-of-sync until `uv lock` regenerates it.
**Why it happens:** Most dependency bumps only touch `pyproject.toml`; a self-referencing editable package's
own version pin inside its own lockfile is an easy-to-miss special case.
**How to avoid:** Always run `uv lock` immediately after the `pyproject.toml` edit, before attempting the
`uv sync --locked` verification step.

### Pitfall 3: Re-litigating the BREAKING-vs-not-BREAKING asymmetry (D-05 vs D-07)

**What goes wrong:** An executor "fixing" the apparent inconsistency — a dead-config removal with zero real
impact gets BREAKING, while an actual filename-changing bug fix (#117) does not — by flattening both to the
same treatment.
**Why it happens:** The asymmetry looks like an error at first glance; CONTEXT.md's own `<specifics>`
section explicitly flags that this was pointed out to the owner and the owner chose to keep it anyway.
**How to avoid:** Treat D-05/D-07 as a locked, deliberate pair — do not harmonize them. The CONTEXT.md
already states: "プランはこの配分を維持すること（勝手に揃えない）."

### Pitfall 4: Adding a `[0.6.2]:` link-reference line prematurely

**What goes wrong:** Copying the bottom-of-file link-reference block's pattern mechanically and adding a
`[0.6.2]: https://github.com/.../releases/tag/v0.6.2` line — but that tag does not exist yet (SC#5's scope
fence: no tag in this phase).
**Why it happens:** Every prior version entry has a matching link line, so it looks structurally incomplete
without one.
**How to avoid:** Leave the link-reference block exactly as-is in this phase (still ending at `[0.6.1]:` +
the `[Unreleased]: .../compare/v0.6.1...HEAD` line). This is a job for `/gsd-complete-milestone`, which owns
the tag creation. See "Open Questions" if the planner wants to address this explicitly rather than silently.

### Pitfall 5: Parsing the README Status line the same way as the `@preview` sync test

**What goes wrong:** Copy-pasting `test_preview_version_sync.py`'s `_PREVIEW_IMPORT_RE` pattern style
(matching `#import "@preview/<name>:<version>"`) verbatim without adapting the regex to README's actual
prose format (`**Status**: Stable (vX.Y.Z) - ...`), which has different delimiters (parens, not colon) and a
leading `v` prefix on the version.
**Why it happens:** The template file's regex is very specific to its own use case; naive copy-paste
produces a regex that never matches.
**How to avoid:** Use the concrete regex given in "Version-Sync Test Design" above, verified against the
exact current text of `README.md:316`.

## Code Examples

### Recommended `[0.6.2]` CHANGELOG entry outline (near-final, ready for the planner/executor to fill in exact
evidence numbers from the corpus-gate run)

```markdown
## [0.6.2] - 2026-07-23

Rendering-fidelity round 2: closes out the remaining 13 medium/low findings from the v0.6.1 audit
(`17-AUDIT-CATALOGUE.md`) across six root-cause clusters, fixes the typstpdf output-filename bug
(Issue #117) and a nested-master compile-root defect, repairs the Typst Universe (`typst_package`)
template path end-to-end, hardens the builder against silent partial-success, removes two long-dead
config values, and corrects several stale README/CLAUDE.md claims. Zero new runtime dependencies; the
bundled `@preview` version-sync surface is untouched.

### Fixed

- **Lost block separation across five constructs (FID-02–FID-06)** — paragraphs inside list items,
  sibling signatures, rubric/option headings, definition-list terms, and back-to-back body-less
  confvals all rendered run-together with no visible break; each now renders with its own separation.
- **Lost intra-signature token spacing (FID-07–FID-09)** — the `class `/`exception ` keyword prefix,
  C/C++ signature/expression tokens (around `*`/`&`, type↔identifier), and object-description
  `:type:`/`:default:` fields all lost their spaces or boundaries; all now render correctly spaced.
- **Long inline-literal runs no longer clip at the right margin (FID-10)** — a long run of inline
  `:role:` literals now wraps within the text block instead of overflowing and clipping mid-token.
- **Soft/semantic paragraph line breaks now reflow (FID-11)** — a paragraph written with one clause
  per source line previously forced a hard break at every line; it now reflows into a justified
  paragraph like every other builder produces.
- **Codly config wrapper no longer leaks as visible text (FID-12)** — a captioned code block nested in
  a list item no longer prints its internal `{ codly(...) }` config wrapper as literal prose.
- **Meaning-bearing inline styling restored (FID-13–FID-14)** — external hyperlinks render with
  distinguishing link styling again, and Python `*`/`/` (PEP 3102/570) signature separators no longer
  inject their internal hover-title text inline.
- **`sphinx-build -b typstpdf` names the output PDF after your configured target, not the source
  docname (Issue #117)** — e.g. with `typst_documents = [("index", "mydoc", "My Manual",
  "Author")]`, the compiled PDF is now `mydoc.pdf` (previously `index.pdf`). If your CI or release
  pipeline references the old docname-based filename, update it.
- **Nested master documents compile with their includes and images intact** — a master at a nested
  docname (e.g. `api/index`) now resolves `#include()`/`image()` paths on the same basis the
  translator emits them, matching what `-b typst` plus a manual `typst compile` already produced.
- **`typst_package` (Typst Universe template) configured alone now builds and compiles with zero
  Typst errors** — fixes a missing `_template.typ` write, unconditional `title`/`authors`/`date`
  injection into templates that don't accept them, and `typst_authors`/`typst_author_params` being
  silently ignored. A new config→output regression fixture now asserts that a config value actually
  changes the compiled output, not merely that it's registered.
- **`sphinx-build -b typstpdf` no longer reports success while silently skipping a configured
  master** — a missing `.typ` file or an unknown docname now fails the build with an aggregated error
  listing every failed master, instead of a bare warning and a `build succeeded` exit. (The
  nested-master render-gate test was also decoupled from `typst-py`'s internal error-message wording,
  so an unrelated upstream wording change can no longer turn CI red.)
- **README.md and CLAUDE.md corrected to match measured behavior** — removed unverifiable test-count
  and coverage numbers with no enforced gate, reworded "Configuration Options" as an explicitly
  partial list linking to the real built documentation, dropped a false citation-support claim (added
  Citations to Known Limitations instead), removed a stale Glossary limitation, and corrected
  CLAUDE.md's Python-version floor (3.10+ → 3.12+) throughout.

### Removed

- **BREAKING: `typst_output_dir` and `typst_author_params` config values removed** — both were
  registered but never read: `outdir` is controlled by the `sphinx-build` CLI argument, not a config
  value, and `typst_author_params` was silently ignored by the author-formatting code path. Neither
  ever affected compiled output, so removal changes no build's result; a `conf.py` still setting
  either is silently ignored by Sphinx (unregistered config values produce no warning), not an error.
  No deprecation period.

### Verified

- Closing full-corpus regression gate: the ~684-page Sphinx `doc/` v9.1.0 corpus, re-run through
  `-b typstpdf`, remains fatal-free (valid `%PDF` output) with the `unknown_visit` catalogue still
  empty.
- Milestone invariant held: zero new runtime dependencies, no `@preview` package version bump, the
  3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) untouched.
```

*(The planner/executor fills in the exact pass/skip evidence line from the D-12 corpus-gate run into
`23-VERIFICATION.md`, not into the CHANGELOG itself — per D-11, no unverified numbers go into the
CHANGELOG.)*

### New sync test skeleton (`tests/test_readme_version_sync.py`)

```python
"""
Test guarding the README/pyproject.toml version-sync hazard (D-13).

README.md's Status line (`**Status**: Stable (vX.Y.Z) - Production ready`) has drifted stale
relative to `pyproject.toml`'s `version` field across two prior releases (stayed at v0.5.0 through
v0.6.0 and v0.6.1). This module asserts the two stay in lockstep, mirroring the existing
`test_preview_version_sync.py` pattern: parse each file's raw text/structured data directly (never
via `importlib.metadata`), and compare the two parsed values against each other.
"""

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

_STATUS_LINE_RE = re.compile(r"\*\*Status\*\*:\s*Stable \(v(?P<version>\d+\.\d+\.\d+)\)")


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


def test_readme_status_version_matches_pyproject():
    """README.md's Status line must always name the same version as pyproject.toml."""
    readme_version = _extract_readme_status_version()
    pyproject_version = _extract_pyproject_version()
    assert readme_version == pyproject_version, (
        f"README.md Status line says v{readme_version} but pyproject.toml says "
        f"{pyproject_version} -- update README.md:316 in lockstep with any version bump."
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| README Status line updated ad hoc, by memory | A dedicated sync test asserts it against `pyproject.toml` | This phase (D-13) | Prevents the exact 2-release staleness that already happened (v0.5.0 → stayed stale through v0.6.0, v0.6.1) |
| `[0.6.1]`'s CHANGELOG entry lists page counts (`689-page index.pdf`) | This phase's `[0.6.2]` entry omits page counts (D-11) | This phase, extending 22.4's "no unverifiable numbers" principle to CHANGELOG | Keeps the CHANGELOG's numeric claims all test-backed |

No deprecated/outdated tooling identified — this phase reuses established project conventions throughout.

## Assumptions Log

No claims in this research are tagged `[ASSUMED]`. Every factual claim was either directly read from the
repository (`git log`, `git tag`, `grep`, file reads) or executed as a command in this session (`ls`,
`uv --version`, cache-path existence checks). The one interpretive judgment call — that "3-way version-sync
surface untouched" means "the `@preview` version lines agree," not "byte-identical files" — is derived
directly from observing that `writer.py` legitimately changed in Phase 22.1 without any phase treating that
as an SC#4 violation, so it is treated as CITED (from project history) rather than ASSUMED.

**This table is empty — no user confirmation is needed before planning.**

## Open Questions

1. **Should this phase also update the bottom-of-file `[Unreleased]` compare-link line, or leave it
   untouched?**
   - What we know: the link-reference block's convention is one `[X.Y.Z]:` line per released tag, plus an
     `[Unreleased]:` line comparing the latest tag to `HEAD`. This phase creates no tag (SC#5), so a
     `[0.6.2]:` link line would 404 until `/gsd-complete-milestone` cuts the tag.
   - What's unclear: whether leaving `[Unreleased]: .../compare/v0.6.1...HEAD` unchanged (now technically
     stale relative to the new `[0.6.2]` heading above it) is acceptable for the prep-only phase, or whether
     it should be left as an explicit todo/note for `/gsd-complete-milestone`.
   - Recommendation: leave it untouched in this phase (matches SC#5's spirit — anything tag-dependent is
     out of scope) and let `/gsd-complete-milestone` update both the link line and add the new `[0.6.2]:`
     line when it cuts the tag, exactly as it already must do for the tag itself. No new decision needed;
     this follows the existing v0.5.0/v0.6.1 precedent (their `[Unreleased]` link lines were similarly only
     updated at tag-cut time based on the git history pattern).

2. **Exact wording of the CONF-01 BREAKING bullet's "no real impact" caveat (D-05's explicit discretion
   item).**
   - What we know: the owner explicitly rejected "state no-real-impact and skip BREAKING" but did not
     specify exactly how much of the no-impact nuance to include in the bullet text.
   - What's unclear: whether to include the "Sphinx silently ignores it, no warning" detail (this research's
     draft above includes one sentence of it) or keep the BREAKING bullet terser.
   - Recommendation: the draft in "Code Examples" above is a reasonable middle ground — states the BREAKING
     fact plainly, then one clause on the practical consequence (silent ignore, no error) without diluting
     the BREAKING signal. Final wording is explicitly Claude's Discretion per CONTEXT.md; the planner may
     adjust the exact phrasing without needing a new decision.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ (`pyproject.toml` `dev` extras: `pytest>=8.4,<10`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`rootdir` implied; `addopts = "-v --strict-markers"`; markers `slow`, `integration` registered) |
| Quick run command | `pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` (fast, offline, no network/compile) |
| Full suite / phase gate command | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v` (the one slow, real-compile gate this phase closes on) |

### Phase Requirements → Test Map

Phase 23 carries no FID/PDF/CONF/WR/DOC requirement IDs (release/close phase), so there is no
requirement-to-test map in the usual sense. Instead, this phase's own deliverables map to tests as follows:

| Deliverable | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| `pyproject.toml`/`README.md` version sync | Both files name the same version | unit | `pytest tests/test_readme_version_sync.py -v` | ❌ Wave 0 — new file, this phase creates it |
| `uv.lock` regenerated correctly | `uv sync --locked` succeeds after the bump | other (CLI invocation, not pytest) | `uv sync --extra dev --locked` | N/A — SC#1's own acceptance check, not a pytest test |
| SC#3 full-corpus regression gate | Corpus compiles fatal-free, empty `unknown_visit` | integration (slow, real-compile) | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v` | ✅ pre-existing (`tests/test_corpus_gate.py:284`) |
| SC#4 milestone invariant (no `@preview` bump) | The 4-package/3-file version agreement still holds | unit | `pytest tests/test_preview_version_sync.py -v` | ✅ pre-existing |
| SC#4 milestone invariant (no new runtime dep) | `pyproject.toml` `dependencies` array unchanged except version | other (`git diff`, not pytest) | `git diff v0.6.1..HEAD -- pyproject.toml` (manual inspection) | N/A — no test asserts this; manual diff read is the verification |

### Sampling Rate

- **Per task commit:** `pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v`
  (sub-second, no network, no compile).
- **Per wave merge / phase gate:** the full corpus-gate command above (`~10-25s`, real compile, cached
  corpus, offline).
- **Phase gate:** Full corpus gate green (`1 passed`, not `1 skipped`) before `/gsd-verify-work`, per D-12.

### Wave 0 Gaps

- [ ] `tests/test_readme_version_sync.py` — does not exist yet; this phase's D-13 deliverable creates it.
      No shared fixture needed (module is self-contained, mirrors `test_preview_version_sync.py`'s
      zero-fixture design).
- [ ] No framework install needed — `pytest`, `tomllib` (stdlib), and `re` (stdlib) are all already
      available in the `dev` extras / Python 3.12+ floor.

## Security Domain

**`security_enforcement` is on (`.planning/config.json`), but this phase has no attack-surface-relevant
change to evaluate.** Phase 23 touches only: a version-literal string, a CHANGELOG markdown file, a README
markdown line, a lockfile regeneration, and one new pytest module that reads two local repo files via
`Path.read_text()`/`tomllib.load()` — no user input, no network call beyond the corpus-gate's already-cached
git clone check, no new parsing of untrusted external data, no authentication/session/access-control
surface, no cryptography.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A — no auth surface touched |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No (new test reads only trusted, repo-local files at fixed paths — not user/network input) | N/A |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Supply-chain drift via `uv lock` picking up an unpinned transitive dependency bump | Tampering (low relevance) | Already mitigated by `pyproject.toml`'s existing `>=X,<Y` range pins on direct dependencies (unrelated to this phase); this phase does not alter those ranges. Reviewing the `uv.lock` diff for unexpected transitive changes (per "Expected diff shape" above) is the relevant check, not a new security control. |

No new threats are introduced by this phase; the Security Domain section is included per config default but
is not a meaningful risk surface here.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | Version bump / lockfile regeneration (SC#1) | ✓ | 0.11.25 | — |
| `git` tag `v0.6.1` | SC#4 invariant diff base ref | ✓ | (tag exists, confirmed via `git tag -l`) | — |
| Cached Sphinx `doc/` corpus | SC#3 regression gate (D-09) | ✓ | `sphinx-v9.1.0` cached at `~/.cache/typsphinx-corpus-gate/` | Falls back to a fresh shallow clone if cache were absent (network required); not needed this phase since cache is confirmed present |
| `typst` (typst-py) | Real-compile corpus gate | ✓ (core runtime dependency, `pyproject.toml`) | `>=0.15.0,<0.16` per constraint | — |
| `tomllib` (stdlib) | New version-sync test | ✓ | stdlib since Python 3.12; floor already `>=3.12` | — |
| Network access (GitHub) | Only if the corpus cache were missing | Not needed this session (cache hit confirmed) | — | Re-clone would require it; already ruled out as a concern |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** none — every dependency this phase needs is already present and
verified.

## Sources

### Primary (HIGH confidence — read/executed directly in this repository this session)

- `.planning/phases/23-v0-6-2-release-prep-regression-gate-close/23-CONTEXT.md` — all 15 locked decisions,
  canonical references, measured-facts table
- `.planning/REQUIREMENTS.md` — full 23-item v1 ledger, traceability table
- `.planning/STATE.md` — roadmap summary, milestone invariant statement, Phase 22.4 handoff note (D-11's
  origin)
- `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` — F1–F15 finding
  descriptions, severity rubric, root-cause groups, mechanical-check evidence (corpus gate runtime, PDF
  provenance)
- `CHANGELOG.md` — full file read; structural template, prior BREAKING/Removed usage, link-reference block
- `tests/test_preview_version_sync.py` — full file read; template for the new sync test
- `tests/test_corpus_gate.py` — full file read; gate mechanics, skip conditions, fixture caching
- `tests/test_extension.py:79-95` — `tomllib`-based `pyproject.toml` version parsing precedent
- `pyproject.toml` — version literal location, dependency ranges, pytest markers/addopts
- `uv.lock` — confirmed `typsphinx` self-entry with its own `version` field
- `README.md` — exact current text at lines 37-39, 203-211, 316-317
- `.planning/phases/22.2-dead-config-value-sweep/22.2-CONTEXT.md`,
  `.planning/phases/22.2-dead-config-value-sweep/22.2-06-SUMMARY.md` — CONF-01/CONF-02 fix details
- `.planning/phases/22.3-typstpdf-builder-warning-hardening/22.3-01-SUMMARY.md`,
  `22.3-02-SUMMARY.md`, `22.3-03-SUMMARY.md` — WR-01/WR-02 fix details
- `.planning/phases/22-typstpdf-target-name-pdf-fix-issue-117/22-VERIFICATION.md`,
  `.planning/phases/22.1-typstpdf-compile-root-alignment-for-nested-masters/22.1-04-SUMMARY.md` —
  PDF-01/PDF-02 fix details
- `typsphinx/builder.py` — `TypstPDFBuilder.finish()` current source (WR-01's `failures` aggregation)
- `git tag -l`, `git log --oneline v0.6.1..HEAD`, `git diff` probes — all executed live this session
- `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` — existence confirmed via `ls`
- `/home/yuta/.claude/projects/-home-yuta-Documents-typsphinx/memory/nixos-sandbox-test-env.md` — full file
  read; reconciled with corpus-gate mechanics

### Secondary (MEDIUM confidence)

None — every claim in this research was directly verifiable against the repository or a locally-executed
command; no web search was needed or used, per the research-focus instruction to ground this phase in the
repository rather than external sources.

### Tertiary (LOW confidence)

None.

## Metadata

**Confidence breakdown:**

- Requirement-ledger → cluster mapping: HIGH — every ID cross-checked against both
  `.planning/REQUIREMENTS.md`'s own cluster headings and `17-AUDIT-CATALOGUE.md`'s F-number source of
  record; zero unmapped IDs.
- CHANGELOG structural template: HIGH — read the full file; heading levels, section order, and
  `BREAKING`/`Removed` prior-usage all directly observed via `grep`/full read, not inferred.
- Version-sync test design: HIGH — template file read in full; parsing targets verified against current
  exact file text this session.
- Corpus gate mechanics: HIGH — test file read in full; cache existence and prior-run duration confirmed
  via direct commands and a cross-referenced prior session's mechanical-check log.
- SC#4 invariant commands: HIGH — base tag confirmed to exist; commands are direct `git diff`/`pytest`
  invocations against files already read in full.
- `uv.lock` regeneration: HIGH — the self-entry version literal directly observed in the lockfile.

**Research date:** 2026-07-23
**Valid until:** Effectively unbounded for the historical/structural claims (CHANGELOG template, F-number
mapping) since this is a closed, already-shipped-fixes phase describing the project's own past work.
The environment-availability claims (corpus cache, `uv` version, tag presence) should be re-verified if
planning is deferred more than a few days, per the standard 7-30 day guidance for anything environment-state
dependent.
