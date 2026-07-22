---
created: 2026-07-22T21:07:11+09:00
title: README の記述を全体的に見直す（実測値との乖離を解消）
area: docs
files:
  - README.md (324 行・全体)
  - README.md:223,243 (テスト数 413 の主張)
  - README.md:203-211 (Configuration Options — 5 件しか挙げていない)
  - README.md:265-270 (Known Limitations)
  - README.md:322 (Status: Stable (v0.5.0))
  - README.md:8,12,274-284 (github.io リンク)
  - typsphinx/__init__.py:44-62 (登録済み config 12 件 — 設定表の source of truth)
  - pyproject.toml:7,10,28,30,55-58
  - CLAUDE.md (Python バージョン記述が README と矛盾)
---

## Problem

README.md を全体的に読み直して、実装・実測との乖離を洗い出したい。ユーザー要望
（2026-07-22 capture）。README は v0.5.0 期に書かれた記述がそのまま残っている箇所が
複数あり、新規ユーザーが最初に読む文書としての正確性が落ちている。

capture 時点で **実測して確認できた乖離** は以下。着手時にはこれらを起点にしつつ、
全文を通しで再検証すること（下記は網羅的な一覧ではない）。

### 1. テスト数が古い（確度：高）

README は 2 箇所でテスト数を主張している:

- `README.md:223` — `# Run tests (413 tests)`
- `README.md:243` — `- **Unit tests**: 413 tests covering all major components`

実測（2026-07-22）: `grep -rhoE "^\s*def test_" tests/ --include=*.py | wc -l` → **577**、
テストファイル 78 件。413 は大きくずれている。

そもそも「テスト数を README に数値で書く」こと自体が継続的にずれる作りなので、
数値を消すか、CI で生成するか、「400+」のような幅を持たせた表現にするかを含めて
判断したい。単に 577 へ書き換えるだけだと次のフェーズでまた古くなる。

### 2. Status 行が v0.5.0 のまま（確度：高）

`README.md:322`:

```
**Status**: Stable (v0.5.0) - Production ready
**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+
```

`pyproject.toml:7` は `version = "0.6.1"`。さらに現在 v0.6.2 が進行中
（Phase 22.x）。バージョン番号を README に直書きしている限り毎リリースで
更新漏れが起きるので、Status 行からバージョンを落とす方向も検討する。

なお 2 行目の `Python: 3.12+ | Sphinx: 9.1+ | Typst: 0.15+` は
`pyproject.toml:10,28,30`（`requires-python = ">=3.12"`, `sphinx>=9.1,<10`,
`typst>=0.15.0,<0.16`）と **一致しており正しい**。

### 3. Configuration Options が実態の半分以下（確度：高）

`README.md:203-211` は 5 件しか列挙していない:

`typst_use_mitex` / `typst_template` / `typst_elements` /
`typst_template_mapping` / `typst_toctree_defaults`

一方 `typsphinx/__init__.py:44-62` は **12 件** を登録している。README に
出てこないのは:

`typst_documents`, `typst_package`, `typst_package_imports`,
`typst_template_function`, `typst_authors`, `typst_debug`,
`typst_template_assets`

特に `typst_documents` はマスタードキュメントを定義する **最も基本的な設定**
なのに README の設定一覧に無い（Quick Start 側には出てくる）。

このセクションは `docs/configuration.rst` への導線であって全列挙が目的では
ない、という立て付けもありうる。その場合でも「主要なもの」の選定が現状ずれて
いるので、何を README に出すかの方針から決める。

**注意:** Phase 22.2 で `typst_output_dir` と旧 author-params 設定を削除済み。
README には元々どちらも出てこないので、この削除に伴う修正は README には不要
（確認済み）。

### 4. Known Limitations の鮮度（確度：中）

`README.md:265-270` は Bibliography (BibTeX) と Glossary の 2 件のみ。
`.planning/todos/pending/2026-07-22-citation-node-support-untracked.md` が
translator の citation / label ハンドラ欠落を別途記録しており、内容としては
矛盾しないが、v0.6.x で判明した他の制約が反映されているかは要確認。

### 5. ドキュメントリンクの正しさ（確度：低・要検証）

`README.md:8,12,274-284` の `yusabo90002.github.io/typsphinx/...` 系リンクは、
フラットなパス（例 `/installation.html`）を指している。しかし
`docs/build_multilang.py` は en/ja を分けたツリーを出力するため、実 URL は
`/en/installation.html` の可能性がある。**実際に踏んで 404 を確認すること。**

## Solution

TBD。ただし着手前に決めるべき論点が 2 つある。

1. **「継続的にずれる数値」をどう扱うか** — テスト数・バージョン番号は書けば必ず
   古くなる。(a) 消す、(b) CI で自動更新、(c) 幅を持たせる、のいずれか。
   個人的には (a) が最も維持コストが低い（テスト数は CI バッジ、バージョンは
   PyPI バッジが既にあり、README 本文で重複して主張する必要が薄い）。

2. **Configuration Options セクションの役割** — 全列挙するのか、
   `docs/configuration.rst` への導線に徹して代表例だけ出すのか。後者なら
   `typst_documents` を必ず含める。

### 他 todo との関係（重要）

`.planning/todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md`
（Read the Docs への移行）が **README の github.io リンク 9 箇所を書き換える**
と明記している。上記 5 の URL 修正はそちらと衝突するので、

- RTD 移行を先にやるなら、URL 系は触らず本 todo から外す
- 本 todo を先にやるなら、URL は現状維持のまま 404 だけ直す

のどちらかに決めてから着手すること。両方を同時に触ると競合する。

### 隣接して見つかった別件（README ではない）

README の Python バージョン記述を検証する過程で、**`CLAUDE.md` の方が古い**
ことが判明した:

- `CLAUDE.md` — 「Python 3.10+ compatibility is required」「ruff は `UP006`/`UP035`
  を 3.10 サポートのため無視」「tox env_list: py310..py313」「CI は py310–py313 の
  マトリクス」と記述
- 実測 — `pyproject.toml:10` は `>=3.12`、`tox.ini:2` の `env_list` は
  `py312, py313, lint, type, cov, docs`、`.github/workflows/ci.yml:18` の
  マトリクスは `['3.12', '3.13']`、classifiers も 3.12/3.13 のみ

つまり README 側が正しく CLAUDE.md 側が stale。CLAUDE.md は Claude の作業指針
なので、「3.10 互換を保て」という誤った制約が残り続けると typing の書き方などで
不要な遠慮が発生する。**本 todo とは別に修正が必要**（別 todo に切るか、
README 見直しのついでに直すかは着手時に判断）。
