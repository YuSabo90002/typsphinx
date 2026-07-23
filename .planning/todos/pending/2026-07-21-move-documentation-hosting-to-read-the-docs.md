---
created: 2026-07-21T21:05:49+09:00
title: マニュアルドキュメントのホスティング先を Read the Docs に変更する
area: docs
files:
  - .github/workflows/docs.yml:57-62 (GitHub Pages デプロイステップ)
  - docs/build_multilang.py:80 (canonical URL が github.io 固定)
  - tox.ini:78-84 (docs-multilang env)
  - README.md:8,12,274-284 (github.io リンク 9 箇所)
  - CHANGELOG.md
  - pyproject.toml:55-56 (project URLs)
  - .planning/codebase/INTEGRATIONS.md
---

## Problem

現在ドキュメントは **GitHub Pages** でホストしている
(`https://yusabo90002.github.io/typsphinx/`)。
`.github/workflows/docs.yml` が main への push で `peaceiris/actions-gh-pages@v4`
を使ってデプロイする構成。これを **Read the Docs** に移したい。

移行の動機は未記録（capture 時点で未確認）。RTD を選ぶ一般的な理由は
バージョン別ドキュメント（v0.6.1 / v0.6.2 / latest の並存）、PR プレビュー、
検索、そして多言語の言語切り替えが標準機能で用意されている点。
現状の Pages 構成はこれらを自前スクリプトで賄っている。

### 現状構成で移行時に効いてくる点

- **多言語ビルドが自前実装。** `docs/build_multilang.py`（tox env `docs-multilang`）が
  en/ja を 1 ディレクトリツリーにまとめて出力している。`docs/locale/ja/` に翻訳あり。
  RTD は「1 プロジェクト = 1 言語 + translation project をリンク」という別モデルなので、
  自前スクリプトをそのまま持ち込めない。ここが移行の最大の判断ポイント。
- **canonical URL がハードコード。** `build_multilang.py:80` に
  `https://yusabo90002.github.io/typsphinx/en/index.html` が直書き。
- **PDF を同じ workflow で作っている。** `tox -e docs-pdf`（このプロジェクト自身の
  `typstpdf` ビルダーのドッグフーディング）で PDF を生成し、
  (a) multilang ツリーの `en/` にコピー、(b) タグ push 時に GitHub Release へ添付。
  RTD にも PDF 出力機能はあるが LaTeX 経由なので、**typstpdf ドッグフーディングを
  維持するなら PDF 生成は CI 側に残す**判断が要る。RTD の PDF は使わない方が自然。
- **`typst-py` が RTD のビルド環境で入るか未確認。** wheel 配布なので通るはずだが、
  `docs-pdf` を RTD 側で回さないなら RTD には `docs` extra だけで足り、問題にならない。
- **URL 参照が散在。** `github.io` の言及は 13 箇所 / 4 ファイル
  （README.md, CHANGELOG.md, docs/build_multilang.py, .planning/codebase/INTEGRATIONS.md）。
  `pyproject.toml:56` の `Documentation` URL は現状 GitHub README を指しており、
  これも RTD に向け直すのが自然。

### 追記（2026-07-22、Phase 22.4 RESEARCH.md 全文監査より）

本 todo 検討時の前提「実測上リンクは全て有効（対応ページが `docs/source/` に実在する）」は **誤りで
あったことが実測で判明した**。2026-07-22 の実測（`curl`）で、README の github.io サブページ直リンク
7 本（README.md:278-284）は**すべて 404** であることを確認した。「ソースファイルが `docs/source/` に
存在する」ことと「ビルド後の公開 URL が実際に到達可能である」ことは別の話であり、当時の前提は
この区別を見落としていた。

原因は `docs/build_multilang.py` の en/ja 分割公開構成で、ルート直下 (`/`) が JS 言語判定リダイレクト
ページのみであり、サブページには `/en/` プレフィックスが必要なため（例:
`.../installation.html` は404だが `.../en/installation.html` は200）。

詳細な実測表・原因・対応方針は新規 pending todo
`2026-07-22-github-io-doc-links-404-missing-en-prefix.md` を参照。当該 todo は「RTD 移行を待たず
`/en/` を足して即座に404を解消する」案と「RTD 移行時に一括で張り替える」案の二択を記録しており、
本 todo（RTD 移行）とどちらを先に着手するかは事前にオーナー判断が必要。

## Solution

TBD（方針未決定）。着手前に決める必要がある論点：

1. **多言語をどう扱うか** — RTD の translation-project モデルに載せ替える
   （ja 用に別 RTD プロジェクトを作って親にリンク）か、単一プロジェクトのまま
   en のみ RTD に出して ja は諦める / 別扱いにするか。
   `build_multilang.py` の廃止・改修範囲がここで決まる。
2. **PDF をどうするか** — 上記の通り、typstpdf ドッグフーディングは CI に残し、
   Release 添付も維持するのが有力。RTD 側の PDF 生成は無効化。
3. **GitHub Pages を残すか** — 一定期間は併存させてリダイレクトを置くか、
   即座に切るか。既存の github.io リンクは外部から参照されている可能性がある。

作業自体は概ね：

- `.readthedocs.yaml` を追加（build.os / python version / `docs` extra のインストール
  / `sphinx.configuration: docs/source/conf.py`）
- RTD 側でプロジェクト作成 + GitHub 連携（**要ユーザー操作**、自動化不可）
- `.github/workflows/docs.yml` から Pages デプロイステップを除去
  （PDF ビルドと Release 添付は残す）
- `build_multilang.py:80` の canonical URL、README / CHANGELOG /
  `pyproject.toml` / `.planning/codebase/INTEGRATIONS.md` の URL 更新
- ja `.po` に URL が埋まっていないか確認

規模的には 1 フェーズ相当。v0.6.2 のスコープ（rendering fidelity）外なので、
v0.6.2 出荷後に扱うのが素直。
