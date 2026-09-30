---
created: 2026-07-25T00:00:00+09:00
title: examples/advanced の typst_elements が allowlist 外キーを持ち ExtensionError でビルド不能
area: examples, docs
source: .planning/phases/27.1-typst-text-lang-from-sphinx-language-config/27.1-02-SUMMARY.md (repo-wide sweep 所見) — オーケストレータが 2026-07-25 に実測で再現
files:
  - examples/advanced/conf.py (52-63 行、`typst_elements` 辞書)
  - README.md (206 行、`typst_elements`: "Template parameters (paper size, fonts, etc.)")
---

## 経緯

Phase 27.1 Plan 02 のリポジトリ全域スイープが所見として記録し、同フェーズのスコープ外
として明示的に据え置いたもの。Phase 26 (CONF-04) が `typst_elements` の未知キーを
fail-loud にした際の相互作用で、その時点で `examples/` が取りこぼされている。
**記録のみ。ここでは直さない。**

なお `examples/` の取りこぼしは Phase 27 でも同型で発生している（docs 系 SC の
「anywhere」は要件が名指しするファイルだけでなく全域 grep で確認すべき、という
既知の再発パターン）。

## 症状（実測で再現済み・推測ではない）

`examples/advanced/conf.py` は `typst_elements` に 5 つの allowlist 外キーを設定している:

```python
typst_elements = {
    "author": "Sphinx-Typst Contributors",   # 非 allowlist
    "date": "October 2024",                  # 非 allowlist
    "papersize": "a4",                       # OK
    "fontsize": "11pt",                      # OK
    "margin": "2.5cm",                       # 非 allowlist
    "primary_color": "rgb(0, 102, 204)",     # 非 allowlist
    "code_font": "Fira Code",                # 非 allowlist
}
```

`ELEMENTS_ALLOWLIST` は Phase 27.1 時点で `papersize` / `fontsize` / `lang` の 3 キーのみ。
`TemplateEngine.map_parameters()` を実際に呼ぶと最初の非 allowlist キーで停止する:

```
ExtensionError: typst_elements: unknown key 'author' -- supported keys: fontsize, lang, papersize
```

つまり **同梱している advanced サンプルは現状そのままではビルドできない**。ユーザーが
コピーして使うことを前提にしたファイルなので、影響はドキュメントの不正確さに留まらない。

## 判断が必要な点

単に非 allowlist キーを削るだけで済むかは自明でない:

- `examples/advanced` は独自テンプレートを同梱している (`conf.py` のコメント参照)。
  そのテンプレートが `margin` / `primary_color` / `code_font` を宣言しているなら、
  allowlist を広げる話 (= CONF-06 の残余候補) になる。宣言していないなら、そもそも
  Phase 26 以前から機能していなかった飾りなので削除でよい。
- `author` / `date` は `DEFAULT_PARAMETER_MAPPING` 経由の Sphinx メタデータと二重管理に
  なっており、`typst_elements` に置く必然性が薄い。
- README 206 行の説明文 ("paper size, fonts, etc.") も 3 キー体制の実態に合っていない。

先に同梱テンプレートの `project()` シグネチャを実測してから方針を決めること。

## 関連

- CONF-06 (将来要件): `papersize`/`fontsize`/`lang` を超える `typst_elements` キーの追加。
  allowlist を広げる方向で解くならこの要件の一部になる。
- Phase 26 (CONF-04): 未知キーの fail-loud 化。この todo の直接の原因。

---

## 解決 (2026-07-25, /gsd-complete-milestone の割り込み修理)

**実測の結論:** 同梱テンプレート `_templates/custom.typ` の `project()` は
`papersize`/`fontsize` を**どちらも宣言していなかった**（宣言は title / authors /
date / toctree_* のみ）。したがって非 allowlist キー 5 つを削るだけでは不足で、
残した `papersize` が `TypstError: unexpected argument: papersize` を引き起こす。

さらに切り分けの過程で**第 2 の破損**が判明: `custom.typ` の `@preview` ピンが
v0.5.0 Phase 7 の bump を取りこぼしており（`codly-languages:0.1.1` /
`mitex:0.2.4` / `gentle-clues:1.2.0`）、`typst_elements` を空にしても
`TypstError: unknown variable: kai` で落ちた。3 マイルストーン分の
サイレントドリフトで、`tests/test_preview_version_sync.py` が 3 面
（writer / template_engine / base.typ）しか見ていなかったことが原因。

**適用した修理（オーナー選択: 「custom.typ で 3 キーを受ける」+「監視面を拡張」）:**

1. `custom.typ` — `@preview` 4 ピンを canonical に揃え、`project()` に
   `papersize` / `fontsize` / `lang` を宣言。module scope の
   `#set page` / `#set text` を `project()` 内へ移し、宣言した引数で駆動。
2. `conf.py` — `typst_elements` を allowlist 3 キーに縮小し、
   「テンプレート側も同名パラメータを宣言していなければ Typst 側で fatal」
   という制約をコメントで明記。allowlist 外を渡したい場合の逃げ道
   （`typst_template_function` の `params`）も併記。
3. `README.md` — 同じ `typst_elements` ブロックと、stale だった
   `typst_package_imports` のコメント例（`codly:0.1.0` /
   `gentle-clues:0.3.0`）を現行版に更新。
4. `tests/test_preview_version_sync.py` — 新規
   `test_example_templates_match_canonical_versions` が `examples/**/*.typ`
   を走査し、4 パッケージのいずれかをピンしている場合に `base.typ` との
   一致を強制。修理前の `custom.typ` で赤になることを実測確認済み
   （3 件の divergence を列挙して FAIL）。charged-ieee のように
   4 パッケージ外を使う例は対象外（ドリフト検出であって統一強制ではない）。

**検証:** `sphinx-build -b typstpdf examples/advanced` が build succeeded、
PDF 248,214 bytes 生成。全スイート 657 passed / 1 skipped、
black・ruff・mypy いずれもクリーン。

CONF-06（allowlist 拡張）は未着手のまま将来要件として残る。
