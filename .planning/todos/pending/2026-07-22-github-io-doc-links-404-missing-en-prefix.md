---
created: 2026-07-22T23:55:07+09:00
title: README の github.io ドキュメントリンク 7 本が 404（`/en/` プレフィックス欠落）
area: docs
files:
  - README.md:278-284 (Documentation 節の github.io サブページ直リンク 7 本 — Installation Guide / Quick Start / User Guide / Configuration Reference / Examples / API Reference / Contributing Guide。実測 404、`/en/` 追加で 200)
  - README.md:8,12,274 (トップページへのリンク3箇所 — `.../typsphinx/` はルート直下の JS リダイレクトページを指すため 200 で動作。修正対象外)
  - docs/build_multilang.py:74-115 (`create_redirect_page()` — en/ja を分けた `/en/`・`/ja/` ツリーとして公開し、ルート直下は JS 言語判定リダイレクトのみである構成の正解源。:80 に canonical URL `https://yusabo90002.github.io/typsphinx/en/index.html` がハードコード)
  - tox.ini:78-84 (`[testenv:docs-multilang]` — en/ja 分割ツリーを生成する `build_multilang.py` を呼ぶ env)
  - .github/workflows/docs.yml:57-59 (`peaceiris/actions-gh-pages@v4` による GitHub Pages デプロイステップ)
---

## Problem

Phase 22.4 の RESEARCH.md 全文監査（discovery #3）で、README:278-284 の github.io サブページ直リンク
7 本すべてが実測で 404 であることが判明した。

| README のリンク (:278-284) | 実測 HTTP ステータス | 実際に到達可能な URL |
|---|---|---|
| `.../installation.html` | **404** | `.../en/installation.html`（200） |
| `.../quickstart.html` | **404** | `.../en/quickstart.html`（200） |
| `.../user_guide/` | **404** | `.../en/user_guide/`（200） |
| `.../user_guide/configuration.html` | **404** | `.../en/user_guide/configuration.html`（200） |
| `.../examples/` | **404** | `.../en/examples/`（200） |
| `.../api/` | **404** | `.../en/api/`（200） |
| `.../contributing.html` | **404** | `.../en/contributing.html`（200） |

原因は `docs/build_multilang.py` が en/ja を分けた `/en/`・`/ja/` ツリーとして公開しており、ルート直下
(`/`) には JS 言語判定つきのリダイレクトページ（`create_redirect_page()`, :74-115）しか存在しないため。
README:8/:12/:274 の「ドキュメントトップ」リンクはこのルートを指しているため 200 で動作するが、
:278-284 の**サブページへの直リンク 7 本は全て `/en/` プレフィックスが欠落しており実際に 404** になる。

**既存 todo `2026-07-21-move-documentation-hosting-to-read-the-docs.md` の前提が誤りだった点:** 当該 todo
は「移行が未着手でリンクは実測上全て有効（対応ページが `docs/source/` に実在する）」という前提のもとで
折り込みを見送っていた。しかし「ソースファイルが `docs/source/` に存在する」ことと「ビルド後の公開 URL
が実際に到達可能である」ことは別の話であり、その前提は成立していなかった — 404 の実測事実がこれを覆す。
当該 todo ファイルには本 todo からの相互参照を追記済み（`## Problem` 節末尾）。

**Phase 22.4 のオーナー裁定（README 側の対応）:** README のリンク自体は現状維持とした
（Phase 22.4 D-17。リンクの一括変更は RTD 移行作業側に委ねる方針）。本 todo は 404 の実測事実と
対応方針の記録が目的。

## Solution

二択:

- **(A)** RTD 移行を待たず、README:278-284 の7リンクに `/en/` を足して即座に404を解消する。
  同一ホスト（github.io）内でのパス修正でありホスティング移行そのものではないため、
  RTD 移行 todo のスコープとは矛盾しない純粋なバグ修正として独立に実施できる。
- **(B)** RTD 移行時（`2026-07-21-move-documentation-hosting-to-read-the-docs.md`）に、
  移行先 URL へ一括で張り替える。

どちらを採るにせよ、本件は RTD 移行 todo の着手順と同時に判断すべき — (A) を先に着手すると
RTD 移行時に再度 URL を全面書き換えることになるため、着手順の決定自体をオーナーに委ねる。
