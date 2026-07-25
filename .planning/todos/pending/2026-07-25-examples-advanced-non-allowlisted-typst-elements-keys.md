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
