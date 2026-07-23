---
created: 2026-07-22T00:00:00+09:00
title: 非 str の docname が TypstPDFBuilder.finish() で raw TypeError を起こす
area: builder, tests
source: .planning/phases/22.3-typstpdf-builder-warning-hardening/22.3-RESEARCH.md (Pitfall 4)
files:
  - typsphinx/builder.py (`finish()` — `_directory_preserving_relpath` 呼び出し, `try:` ブロックより前)
  - typsphinx/builder.py (`_directory_preserving_relpath`, `path.dirname(docname)` の呼び出し箇所)
---

## 経緯

Phase 22.3 (WR-01) 計画中の RESEARCH で再現・確認された、D-06 により本フェーズの
スコープ外に据え置かれた欠陥。**記録のみ。ここでは直さない。**

## 症状

`typst_documents` に非 `str` の docname が混入すると（例:
`typst_documents = [(123, "manual.typ", "T", "A")]`）、`TypstPDFBuilder.finish()` は
既存の `try`/`except` による集約 `ExtensionError` を経由せず、生の `TypeError` で
クラッシュする。typsphinx 独自の診断メッセージは一切出ず、Python の素のトレースバック
だけが表示される。

## 検証済みの呼び出しチェーン

```
Traceback (most recent call last):
  File ".../typsphinx/builder.py", line 919, in finish
    relative_path = self._directory_preserving_relpath(docname, stem)
  File ".../typsphinx/builder.py", line 264, in _directory_preserving_relpath
    directory = path.dirname(docname)
TypeError: expected str, bytes or os.PathLike object, not int
```

`finish()` は `self._directory_preserving_relpath(docname, stem)` を呼び、
`_directory_preserving_relpath`（`builder.py:239-267`）内の `path.dirname(docname)`
（`builder.py:264` 相当）で例外が発生する。この呼び出しは `finish()` 内の
`try:` ブロック（コンパイル呼び出しを囲む方）より**前**にあるため、
`failures` への集約を一切経由せずに build プロセス全体をクラッシュさせる。

`_resolve_output_stem(docname)` 自体は非 str の docname を渡されても例外を出さない
(`entry[0] == docname` の比較や `target`/`stem` の文字列処理が `docname` の型に
直接触れないため)。クラッシュ地点はあくまで `_directory_preserving_relpath` の
`path.dirname(docname)` 呼び出しである。

## Phase 22.3 のスコープ外である理由 (D-06)

D-06 は malformed-entry guard の検出条件を既存の `if not doc_tuple:` のまま
広げないことを明示的に定めている。WR-01 が問題にしていたのは「検出された
スキップが `failures` に届いていない」ことであり、「一部の不正な入力が
検出されないこと」ではない。今回のケースは非 str docname という**別種の
入力型バリデーション欠陥**であり、WR-01 の診断ロジック拡張とは異なるスコープ。

## 併走する未解決兄弟項目

`22.3-CONTEXT.md` の `<deferred>` に記録されている、以下の 2 件と同じ並びの
先送り事項:

- `typst_documents` の形状に対する網羅的なバリデーション
- 未知の docname に対する `difflib` ベースの "did you mean" サジェスト

## Not now — 破壊力についての注記

この欠陥は**黙って失敗する**ものではない — `sphinx-build` は非ゼロ終了し、
フルスタックトレースが出力される。したがって WR-01（サイレント成功の再発防止）
を再び壊すものではなく、単に「typsphinx 独自の診断ではなく生のトレースバックで
落ちる」という UX 上の粗さの問題である。

着手は将来のバックログ昇格時（`/gsd-review-backlog`）。
