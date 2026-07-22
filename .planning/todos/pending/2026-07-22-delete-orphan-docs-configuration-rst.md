---
created: 2026-07-22T23:55:07+09:00
title: 孤児の `docs/configuration.rst` を削除する
area: docs
files:
  - docs/configuration.rst (526 行、`docs/source/` の外にありどの toctree からも参照されない孤児。誤パッケージ名 `sphinxcontrib.typst` を :20 と :330 に含み、誤ったパス言及 `sphinxcontrib/typst/templates/base.typ` を :486 に含む)
  - docs/source/user_guide/configuration.rst (253 行。README からの参照先として Phase 22.4 Plan 01 (D-12) が張り替え先に採用した、実際にビルドされ toctree からも到達可能な正解ファイル)
  - README.md:205 (Phase 22.4 Plan 01 (D-12) で `docs/configuration.rst` への参照を `docs/source/user_guide/configuration.rst` へ張り替え済み — 本 todo 起票時点で参照元がゼロになったことの前提)
---

## Problem

`docs/configuration.rst`（526 行）は `docs/source/` 配下でも、いかなる toctree 配下でもない孤児ファイルで、
Sphinx のビルドに一切含まれない。`grep -rln toctree docs/source/` の結果にこのファイルを指すエントリは無く、
Sphinx が生成する HTML/PDF のどこからも到達できない。

本文には誤ったパッケージ名 `extensions = ['sphinxcontrib.typst']`（:20, :330。正しくは `typsphinx`）と、
誤ったテンプレートパス言及 `sphinxcontrib/typst/templates/base.typ`（:486）を含む — 読者がコピーしても
壊れる内容である。

README からの参照は Phase 22.4 Plan 01 の D-12 判断により `docs/source/user_guide/configuration.rst`
（実際にビルドされ toctree からも到達可能）へ張り替え済みで、`docs/configuration.rst` への参照元は
README からはゼロになった。ただしファイル実体の削除自体は「`docs/` 配下を削除・再編しない」という
Phase 22.4 のスコープフェンス外であるため、本 todo として退避する。

## Solution

1. 削除前に、現行の `docs/source/user_guide/configuration.rst`（253 行）に無い有用な内容が
   孤児側の `docs/configuration.rst`（526 行）に残っていないか差分確認する。
2. 参照元が本当にゼロであることを再確認する: `grep -rn 'docs/configuration' . --exclude-dir=.git`
   （README.md からの参照は張り替え済みのため消えている想定。`CHANGELOG.md` と `.planning/` 配下の
   過去記述は履歴/計画メモなので対象外として無視してよい）。
3. `docs/configuration.rst` を削除する。
