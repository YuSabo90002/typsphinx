---
gsd_state_version: 1.0
milestone: v0.6.3
milestone_name: config & docs 実測整合 + captioned tables
current_phase: 27.1
current_phase_name: Typst 組版 lang の Sphinx language 連動 (INSERTED)
status: planning
stopped_at: Phase 27.1 context gathered
last_updated: "2026-07-25T03:57:37.905Z"
last_activity: 2026-07-25
last_activity_desc: Phase 28 の discuss を中断し、CONF-07 を切り出して Phase 27.1 を挿入
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 6
  completed_plans: 6
  percent: 67
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-23 at v0.6.3 milestone start)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise.
**Current focus:** Phase 27.1 — Typst 組版 lang の Sphinx `language` 連動 (CONF-07, INSERTED)

## Current Position

Phase: 27.1 — Typst 組版 lang の Sphinx `language` 連動 (INSERTED)
Plan: Not started
Status: Ready to discuss/plan
Last activity: 2026-07-25 — Phase 28 の discuss を中断し、CONF-07 を切り出して Phase 27.1 を挿入

Progress: [░░░░░░░░░░] 0%

## Roadmap Summary (v0.6.3 — Phases 24–28, +27.1 inserted)

| Phase | Goal | Requirements |
|-------|------|--------------|
| 24 — Delete `typst_toctree_defaults` (dead-config sweep round 2, part B) | Remove the inert `typst_toctree_defaults` from every surface (registration, docs, examples, README, its test file) — pure grep-zero removal, 0-risk | CONF-05 |
| 25 — Captioned Table Figure Wrap + Cross-References (reimplement PR#98) | `.. table:: Caption` → `figure(table, caption, kind: table)` "Table N" + `:numref:`/`:ref:` `<label>`; caption-less stays plain; caption+width compose; 2nd-table stale-buffer fix | TBL-01, TBL-02 |
| 26 — `typst_elements` papersize/fontsize Pass-Through (dead-config sweep round 2, part A) | `typst_elements` `papersize`/`fontsize` reach `project()` (string vs. unquoted length); unknown key fails loud; copyright never leaks; `base.typ` byte-unchanged (Python-side fix only) | CONF-04 |
| 27 — Docs 実測整合 — Orphan Delete + Phantom Config Names | Delete orphan `docs/configuration.rst`; correct the 5 phantom config names in `user_guide/configuration.rst` (papersize/fontsize → working `typst_elements` examples) | DOC-06, DOC-07 |
| 27.1 — Typst 組版 lang の Sphinx `language` 連動 (INSERTED 2026-07-25) | `base.typ` の `project()` に `lang` を追加し、既定テンプレート経路のみ `config.language` から自動導出、`typst_elements["lang"]` が全経路で優先。ja ドキュメントの PDF で "Table N"/"Figure N" が「表 N」「図 N」になる | CONF-07 |
| 28 — v0.6.3 Release Prep + Regression-Gate Close | Prep-only: bump `pyproject.toml` → 0.6.3 (sole literal) + `uv.lock` + `CHANGELOG` `[0.6.3]` + README Status; close on the full-corpus regression gate. Publish at `/gsd-complete-milestone` | (release/close — none) |

**Coverage:** 7/7 v1 requirements mapped (CONF-04, CONF-05, CONF-07, TBL-01, TBL-02, DOC-06, DOC-07) — no orphans, no duplicates, each to exactly one phase. Phase 28 carries no requirement (release/close).

**Ordering (research-driven, honored):** 24 (trivial 0-risk deletion) → 25 (translator captioned-table work, own state-machine risk) → 26 (`typst_elements` pass-through, own type-mismatch risk — **separate** phase from the table work per instruction) → 27 (docs cleanup — **must** follow 26 so phantom `papersize`/`fontsize` become *working* examples, not fatal ones) → 27.1 (CONF-07; 26 の `ELEMENTS_ALLOWLIST`/`map_parameters` 経路を土台にするので 26 の後) → 28 (release). TBL-01 before TBL-02 within Phase 25 (figure must exist to be labeled).

**Standing bar (GATE-01):** node-handler change (Phase 25) and config→output change (Phase 26) each ship a fail-pre-fix real `typst.compile()` regression fixture. Phase 25 MUST test a 2+-table document (stale-buffer bug invisible with one table) + caption+width + `:numref:`-resolves. Phase 26 MUST test papersize AND fontsize separately + a negative unknown-key case + a copyright-non-leak case. Pure-removal Phase 24 and docs-only Phase 27 carry no config→output change → grep-zero / grep-cross-check + green suite is the honest bar (no fixture).

**Milestone invariant (every phase):** zero new runtime deps, no `@preview` version bump — the 3-way version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) の**版文字列**は未変更のまま。**2026-07-25 改訂（オーナー判断）:** 「`base.typ` byte-unchanged」は **Phase 27.1 に限り解除** — 変更は `project()` への `lang` パラメータ追加とその `set text()` 配線のみ。他フェーズは従来どおり byte-unchanged で、`tests/test_preview_version_sync.py` は全フェーズ緑。

**Ship unit = milestone** (`branching_strategy: milestone`): Phase 28 is prep-only; the irreversible publish (tag `v0.6.3` → `release.yml` → PyPI + GitHub Release) executes at `/gsd-complete-milestone`.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 55 (through v0.6.2)
- v0.6.3 plans completed: 0 (roadmap just created)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Recent decisions affecting current work (full log in PROJECT.md Key Decisions):

- 2026-07-23: v0.6.3 roadmap created — Phases 24–28, derived from 6 v1 requirements (CONF-04/05, TBL-01/02, DOC-06/07). Numbering continues from v0.6.2's Phase 23. Shape follows research's dependency order: trivial deletion → captioned tables → `typst_elements` pass-through → docs cleanup → release. CONF-04 and TBL-01/02 kept in SEPARATE phases (distinct state-machine/type risks); docs phase strictly after CONF-04 (Pitfall 11).
- 2026-07-20: `branching_strategy: milestone` — ship unit is the milestone; the final phase is a prep-only Release phase, publish deferred to `/gsd-complete-milestone`. Push `main` to `origin` at every milestone close.
- 2026-07-22 [Phase 22.2]: dead-config sweep round 1 pattern — a config→output real-compile regression fixture (template `tests/test_package_only_config_gate.py`) is the bar so registration-only asserts can't hide a dead feature. CONF-04/CONF-05 are the round-2 (5th/6th) instances of the same defect class.

### Pending Todos

Backlog (`.planning/todos/pending/`) after v0.6.3 scoping — the dead-config sweep, PR#98 reimplementation, orphan-doc deletion, and phantom-config-name items were promoted into this milestone (Phases 24–27). Remaining pending:

- **move-documentation-hosting-to-read-the-docs** (docs) — RTD migration, out of this milestone; the github.io 404 doc-link fix is folded into it.
- **add-sphinx-linkcheck-ci-job** (ci, docs) — automate `sphinx-build -b linkcheck`; own ~1-phase task.
- **citation-node-support-untracked** (translator, examples) — `visit_citation` handler absent; surfaced in Phase 22.2, permanent fix unplanned.
- **non-str-docname-typeerror-in-typstpdf-finish** (builder) — input-validation hardening, deferred from Phase 22.3 (D-06).
- **modernize-typing-imports-drop-up006-up035-ignore** (typing) — deferred; do not "modernize" typing imports until this lands.
- **github-io-doc-links-404-missing-en-prefix** (docs) — folded into the RTD migration (owner decision 2026-07-23), not interim-fixed.

- **close-pr98-after-v063-release** (planning) — PR#98 のクローズ。ギャップ無しは実測確認済み（下記）。オーナー判断 2026-07-25 でタイミングは **v0.6.3 publish 後**（`/gsd-complete-milestone` 直後）。文面はオーナー確認のうえ投稿。

Closed 2026-07-25: **verify-no-gap-between-pr98-and-phase25** — ギャップ無しを実測確認（PR#98 の 4 テストを verbatim 移植して 4/4 PASS、現行実装は厳密な上位集合）。テスト厳密さの差分 4 点を `tests/test_translator.py` に補強済み。残りの PR クローズは上記 todo に分離。

### Blockers/Concerns

None open. UI note: v0.6.3 phases are Typst PDF typesetting / config / docs work, NOT frontend UI — no `### UI hint` annotations added (the project's `ui.plan-gate` false-positives on PDF/rendering phases; use `--skip-ui` if it flags them). GATE-01 note (from v0.6.2): the honest-verifier rule — abstain to `human_needed` rather than assert a truth without direct evidence.

### Roadmap Evolution

- Phase 27.1 inserted after Phase 27: Typst 組版 lang の Sphinx language 連動 (CONF-07, carved out of future CONF-06). Amends the milestone base.typ byte-unchanged invariant for this phase only. (URGENT)

## Deferred Items

Items acknowledged and carried forward from previous milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |
| Config | CONF-06: `typst_elements` keys beyond papersize/fontsize/**lang** (needs `base.typ` `project()` params) — `lang` は 2026-07-25 に CONF-07 として切り出し v1 昇格（Phase 27.1）、残りは据え置き | Deferred to future milestone | v0.6.3 scoping |
| Todo (docs) | move-documentation-hosting-to-read-the-docs (+ github.io 404 links folded in) | Pending backlog | v0.6.2 close |
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Pending backlog | v0.6.2 close |
| Todo (translator, examples) | citation-node-support-untracked | Pending backlog | v0.6.2 close |
| Todo (builder) | non-str-docname-typeerror-in-typstpdf-finish | Pending backlog | v0.6.2 close |
| Todo (typing) | modernize-typing-imports-drop-up006-up035-ignore | Pending backlog | v0.6.2 close |

## Session Continuity

**Resume file:** .planning/phases/27.1-typst-text-lang-from-sphinx-language-config/27.1-CONTEXT.md

Last session: 2026-07-25T03:57:37.899Z
Stopped at: Phase 27.1 context gathered
Resume: `/gsd-discuss-phase 27.1`

## Operator Next Steps

- `/gsd-discuss-phase 27.1` — CONF-07 の実装決定を CONTEXT.md に落とす。討議で実測済みの決定（下記）を引き継ぐこと
- Phase 28 は 27.1 完了後に再開。`28-CONTEXT.md` は未作成（討議は 4 領域を選択した直後で中断）

**Phase 27.1 で実測済み・決定済み（2026-07-25、discuss 28 の中断中に確定）:**

- `base.typ:61` が `set text(size: fontsize, lang: "en")` と組版言語をハードコード。`config.language` は typsphinx のどこからも読まれていない（`grep config.language typsphinx/*.py` = 0 件）
- **`.po` 参照は既に動いている** — `sphinx-build -b typst -D language=ja docs/source` で本文は翻訳される（`user_guide/configuration.typ` に CJK 58 行）。Sphinx の i18n は doctree transform なので builder 側の対応不要。組版 `lang` とは別レイヤー
- 実害の実測: `lang: "en"` → `Table 1` / `Figure 1`、`lang: "ja"` → `表 1` / `図 1`。Phase 25 の captioned table が ja ドキュメントで英語ラベルになる
- Sphinx LaTeX ビルダーの precedence（`builders/latex/__init__.py::init_context()`）: `DEFAULT_SETTINGS` → `ADDITIONAL_SETTINGS[engine]` → `ADDITIONAL_SETTINGS[(engine, language[:2])]` → `config.latex_elements`。250 行目に `# 'babel' key is public and user setting must be obeyed`
- 決定: 自動導出は**既定テンプレート経路のみ**（`template_path is None and typst_package is None`）。明示 `typst_elements["lang"]` は既存 CONF-04 経路に乗るので全経路で渡る（新規挙動ではない）
- カスタムテンプレートの逃げ道は実測済み: 既定の適用関数名は `project`（`template_engine.py:479` の `self.typst_template_function_name or "project"`）。`typst_template_function = {"name": "project", "params": {"lang": "ja"}}` で `lang: "ja",` が出力され PDF は「表 1」。未宣言なら `TypstError: unexpected argument: lang`
- リポジトリ内のカスタムテンプレート 2 件（`examples/advanced/_templates/custom.typ`、`examples/charged-ieee/approach2/source/_templates/_template.typ`）はどちらも `lang` 未宣言 → 常時渡す設計なら両方 fatal。これが「既定テンプレート経路のみ」の根拠
- research/plan 送り: Sphinx の言語コード（`zh_CN` 等）→ Typst `lang`/`region` の変換規則、未知値の扱い（LaTeX は `no Babel option known for language %r` で警告して続行）
