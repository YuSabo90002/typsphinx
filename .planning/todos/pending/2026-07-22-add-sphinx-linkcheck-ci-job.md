---
created: 2026-07-22T23:55:07+09:00
title: `sphinx-build -b linkcheck` の CI ジョブを追加する
area: ci, docs
files:
  - .github/workflows/ci.yml (既存の py312/py313 + lint/type/cov マトリクスに新ジョブを追加する候補先)
  - .github/workflows/docs.yml (ドキュメント系ワークフロー。linkcheck をここに追加する案もあり得る)
  - tox.ini (新 `[testenv:linkcheck]` の追加先)
  - docs/source/conf.py (`linkcheck_ignore` 等の Sphinx linkcheck 設定を書く先)
---

## Problem

Phase 22.4 の RESEARCH.md 全文監査（discovery #3、Task F）で発見した README:278-284 の github.io リンク
7 本の 404（詳細は隣接 pending todo
`2026-07-22-github-io-doc-links-404-missing-en-prefix.md` を参照）は、公開から数か月にわたり誰にも
気づかれずに残っていた。これを自動検出できたはずの仕組みが本リポジトリには存在しない — CI には
lint/type/coverage/build/integration の各ジョブはあるが、公開ドキュメントのリンク到達性を検証する
ジョブは無い。

Phase 22.4 は grep ベースの手動検証（`curl` による実測）で発見に至ったが、これは誠実な到達点であって
持続可能な仕組みではない。RESEARCH.md Task F の結論どおり、リンク到達性の自動化は本フェーズの
プロース修正とは別に必要な作業である。

## Solution

- `tox.ini` に `[testenv:linkcheck]` を追加し（`sphinx-build -b linkcheck docs/source build/linkcheck`
  相当）、CI から呼ぶ。
- レート制限や外部サイトの一時障害でジョブが不安定にならないよう、
  `docs/source/conf.py` に `linkcheck_ignore` を設定し、外部ドメイン（github.io 以外の外部サイトへの
  リンクなど）を必要に応じて除外する。
- 導入初期は「失敗しても `main` をブロックしない」扱い（advisory ジョブ、必須チェックにしない）から
  始め、安定性を見てから required 化を検討する — `drift.yml` が advisory ジョブとして運用されている
  前例（`.planning/PROJECT.md` の D-07「drift ジョブは常に advisory」）に倣う。
