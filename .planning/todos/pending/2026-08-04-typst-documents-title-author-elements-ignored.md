---
created: 2026-08-04T00:00:00+09:00
title: "`typst_documents` の entry[2] (title) / entry[3] (author) が一切読まれていない — LaTeX は読む"
area: builder, writer, template_engine, docs
source: .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-CONTEXT.md (D-02)
files:
  - typsphinx/writer.py (`_is_master_document` L41-71 — entry[0] のみ参照)
  - typsphinx/builder.py (L118 `entry[0]`, L165-166 `entry[0]`/`entry[1]`, L928 `doc_tuple[0]`)
  - typsphinx/template_engine.py (title/authors の実際の供給元 — L200 `"project": "title"`, L445-463 `typst_authors`)
  - docs/source/user_guide/configuration.rst (L30 付近の 5 要素契約)
---

## 症状

`docs/source/user_guide/configuration.rst` は `typst_documents` の 5 要素契約を公表している:

1. Source file / 2. Output filename stem / 3. **Document title** / 4. **Author** / 5. Document class

しかし **[2] title / [3] author / [4] class は typsphinx のコードから一度も読まれていない**。
2026-08-04 に repo 全域を実測した結果、`typst_documents` エントリへの添字アクセスは以下が全例:

```
typsphinx/writer.py:68   if doc_tuple and doc_tuple[0] == docname:
typsphinx/builder.py:118 masters = [entry[0] for entry in typst_documents if entry]
typsphinx/builder.py:165 if entry and len(entry) >= 2 and entry[0] == docname:
typsphinx/builder.py:166     target = entry[1]
typsphinx/builder.py:928 docname = doc_tuple[0]
```

実際のタイトルと著者は `template_engine.py` が `config.project` / `config.author`
（および `typst_authors`）から直接取っている。つまりユーザーが
`typst_documents = [("index", "manual.typ", "My Handbook", "Jane Doe")]` と書いても、
出力 PDF のタイトルは `project` のまま、著者は `author` / `typst_authors` のままになる。

これは PROJECT.md のコアバリュー「ドキュメントされた設定が実際に効く — ドキュメント通りの
`conf.py` をコピーしたユーザーが、docs が約束したものを得る」に直接抵触する。

## 参照実装 — Sphinx の LaTeX ビルダは読んでいる（2026-08-04 実測, Sphinx 9.1.0）

`sphinx/builders/latex/__init__.py` の `LaTeXBuilder.write_documents()`:

```python
for entry in self.document_data:
    docname, targetname, title, author, themename = entry[:5]
    ...
    self.update_doc_context(title, author, theme)
    ...
    docsettings._author = author
    docsettings._title = title
```

さらに `init_document_data()` は `self.titles.append((docname, entry[2]))` としてタイトルを保持する。
つまり LaTeX では **明示エントリの title/author が `config.project` / `config.author` より優先**する。
typsphinx を LaTeX と同じ仕様に合わせるなら、この配線が必要。

## 実測した影響範囲（着手時の見積もり用）

リポジトリ内の `conf.py` にある `typst_documents` エントリ **104 件のうち、`entry[2]` が
`project` と異なるのは 5 件だけ**:

| ファイル | entry[2] | project |
|---|---|---|
| `examples/advanced/conf.py` | `Advanced Sphinx-Typst Features` | `Advanced Sphinx-Typst Example` |
| `tests/fixtures/integration_basic/conf.py` | `Integration Test` | `Integration Test Project` |
| `tests/fixtures/integration_sibling/conf.py` | `Sibling Directory Test` | `Sibling Directory Toctree Test` |
| `tests/fixtures/template_named_dir_master/conf.py` | `Template Named Dir Master (nested)` | `Template Named Dir Master` |
| `tests/roots/test-basic/conf.py` | `Test Document` | `Test Project` |

残り 99 件は `entry[2] == project` なので出力は変わらない。

## Phase 44 のスコープ外である理由

CONF-08（デフォルト導出）と BLD-01（非 str docname の堅牢化）のどちらの文面にもない
**新しい振る舞い**であり、v0.7.1 というパッチリリースに 2 件目の user-visible 変更
（CONF-08 の出力ファイル名リネームに加えてタイトル/著者の変化）を並べることになるため。
オーナー判断 2026-08-04（Phase 44 discussion, D-02）: 今フェーズは**導出エントリの「形」だけ
LaTeX に揃え**（5 要素 `(root_doc, "<project>.typ", project, author, "typst")`）、
**消費側の配線はここに落として v0.7.1 の外**とする。

## 着手時に決めること

- `entry[2]`/`entry[3]` が空文字/None のときのフォールバック先（`config.project` / `config.author`）。
- `typst_authors`（dict 形式・構造化著者情報）と `entry[3]`（単一文字列）の優先順位。
  現在 `template_engine.py` L445 の D-07 は「`typst_authors` が `authors` を上書きする」と決めている。
- 5 要素目（docs 上「Document class (usually 'typst')」）に意味を与えるか、無意味なまま残すか。
- `docs/source/user_guide/configuration.rst` の 5 要素契約の記述更新（配線後は実際に効くので、
  「効かない」旨の但し書きが不要になる）。
