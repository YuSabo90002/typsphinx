---
created: 2026-07-25T00:00:00+09:00
title: docs/usage.rst と docs/installation.rst が Phase 27 で削除した orphan と同じクラス
area: docs
source: .planning/phases/27.1-typst-text-lang-from-sphinx-language-config/27.1-02-SUMMARY.md (repo-wide sweep 所見)
files:
  - docs/usage.rst
  - docs/installation.rst
---

## 経緯

Phase 27.1 Plan 02 のリポジトリ全域スイープが所見として記録し、同フェーズのスコープ外
として据え置いたもの。**記録のみ。ここでは直さない。**

## 症状

Phase 27 は `docs/configuration.rst` を「どの toctree からも参照されていない orphan で、
実体は `docs/source/user_guide/configuration.rst` にある」という理由で削除した。
`docs/usage.rst` と `docs/installation.rst` は同じクラスに見える — `docs/source/` 配下の
正規ツリーの外に置かれた、参照されていない可能性のある重複ファイル。

## 確認すべきこと

- 実際にどの toctree からも参照されていないか（`docs/source/index.rst` と
  `docs/source/**/index.rst` を実測）。
- `docs/source/` 配下に同等の内容が存在するか。存在するなら削除、しないなら移設。
- 内容が古びていないか。Phase 27 が閉じた「実測との乖離」と同じドリフトを抱えている
  可能性がある。

Phase 27 と同じく、削除を含む変更は `worktree.cleanup-wave` の削除ガードに当たるため、
スコープを実測してから実行方式を決めること。
