---
created: 2026-08-14T19:55:48+09:00
title: "`derive_master_edge_keys`'s recursive `walk()` has no depth guard — a deep include chain crashes the build with a raw RecursionError"
area: translator
resolves_phase: null
source: .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-REVIEW.md (WR-02), 49-VERIFICATION.md (human_verification item 2)
severity: minor
files:
  - typsphinx/translator.py:280-297  # derive_master_edge_keys() の入れ子 walk()
  - typsphinx/builder.py  # _build_include_edge_map() — 呼び出し側。ExtensionError に包むならここも候補
  - tests/test_include_edge_derivation_unit.py  # 深い連鎖の RED を置く先
---

## Problem

Phase 49 が新設した `derive_master_edge_keys()` の入れ子関数 `walk()` は、深度ガードなしの Python
再帰で toctree グラフを辿る。十分に深い（あるいは長い直線状の）include 連鎖に当たると
**キャッチされない `RecursionError` が上がり、Sphinx ビルド全体が raw traceback で落ちる** —
どの docname のどの連鎖で落ちたのかを名指しする `ExtensionError` にはならない。

Phase 49 のコードレビュー (WR-02) が発見。再帰は「LIFO ワークスタックだと兄弟順が反転する」という
COMP-05 の要請から**意図的に**選ばれた形なので、再帰そのものが誤りなのではなく、境界が無いことが
問題である。

Python の既定再帰上限は 1000 で、実在のドキュメントツリーがそこまで深い直線連鎖を持つことはまず
無い（Sphinx 自身の `doc/` コーパス 154 文書でも到達しない）。Phase 49 の success criteria と要件
COMP-05..COMP-12 のいずれも上限付近の連鎖を検査していないため、これは Phase 49 の未達ではない。
ship 前に**追跡だけして先送りする**というのがオーナー判断（2026-08-14、49-UAT.md item 2）。

## Solution

いずれか一つ:

- **明示的な深度ガード** — `walk()` に深度カウンタを持たせ、閾値超過で `sphinx.errors.ExtensionError`
  を上げる。メッセージには到達した連鎖（少なくとも先頭と末尾の docname）を含め、`RecursionError` の
  traceback ではなく「このツリーのここが深すぎる」と読める形にする。閾値は Python の
  `sys.getrecursionlimit()` を直接読むのではなく、独自の定数にして根拠をコメントで残すこと。
- **反復化** — 明示スタックに書き換える。ただし **LIFO ワークスタックは兄弟順を反転させ、しかも
  コンパイルエラーを出さない**（`49-EXPECTED-STRUCTURE.md` が forbidden shape として名指ししている）。
  反復化するなら順序を保つ形（子を逆順に push する等）にし、`state_guard_mirror_pair_gate` と
  `state_guard_glob_gate` が兄弟順を守っていることを再確認すること。

どちらでも、ROADMAP binding constraint #4 に従い**先に RED を立てる** — 上限を超える深さの
`toctree_includes` を合成して現状の挙動（`RecursionError`）を記録してから直す。単体レベルで足りる
ので `tests/test_include_edge_derivation_unit.py` が置き場所。実 fixture を 1000 段作る必要は無い。

## References

- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-REVIEW.md` — WR-02 の原文
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-VERIFICATION.md` — `human_verification` item 2
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EXPECTED-STRUCTURE.md` — 走査規則と、LIFO ワークスタックを forbidden shape として名指しした箇所
- 併走する Phase 49 由来の todo: [[2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide]]
