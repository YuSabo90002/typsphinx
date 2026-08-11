---
created: 2026-08-10T10:40:00+09:00
title: rehome された変換画像が `<srcdir>/images/` の実画像とキー衝突し、別の画像を無言で描画する
area: builder
severity: major
files:
  - typsphinx/builder.py  # TypstBuilder._track_image()
  - typsphinx/builder.py  # TypstBuilder.copy_image_files()
  - tests/test_absolute_image_render_gate.py
---

## Problem

PR #131（Issue #130 の修正、2026-08-10 にレビューのうえマージ）で導入された
`TypstBuilder._track_image()` は、Sphinx の `ImageConverter` / `ImageDownloader` /
`DataURIExtractor` が書き換えた**絶対** URI を `doctreedir` 相対に rehome する。

Sphinx 9.1.0 の `ImageConverter.handle()` の出力先は

    <doctreedir>/images/<basename>.<converted-ext>

なので、rehome 後のキーは **`images/diagram.png`** になる。ところが `<srcdir>/images/`
は Sphinx で最も一般的なアセット配置であり、通常画像 `.. image:: images/diagram.png` も
**まったく同じキー** `images/diagram.png` として `self.images` に登録される。

`_track_image()` / `post_process_images()` はどちらも `if <key> not in self.images` で
ガードしているため、**先に追跡された方が勝ち、もう片方は完全に捨てられる**。勝敗は
文書の書き込み順（`write_doc` の呼ばれる順＝概ね docname のアルファベット順）に依存する。

結果として:

- 負けた側の画像ファイルは `outdir` に**一度もコピーされない**
- 両方の `.typ` が**同一の** `image("images/diagram.png")` を emit する
- したがって片方の文書は**まったく別の画像を描画する**
- ビルドは成功し、**警告は一切出ない**

2026-08-10 のレビューで probe により実測（73 byte の実ソース画像と 68 byte の変換画像を
用意）:

```
Copying 1 image file(s)...          ← 2枚あるのに1枚しか追跡されない
outdir/images/diagram.png = 68 byte ← 変換画像が勝った
index.typ:29  image("images/diagram.png")
index.typ:37  image("images/diagram.png")   ← 同一パス
build succeeded.                            ← 警告なし
```

**failure mode の後退でもある点に注意。** 同じ probe を PR 前の `main` で走らせると
`Copying 2 image file(s)` でキーは衝突せず、ビルドは Issue #130 として**明示的に落ちる**。
つまり PR #131 は、この形状に限り「うるさく失敗する」を「黙って間違った画像を出す」に
変えた。#130 の修正価値の方が圧倒的に大きいのでマージは妥当だが、silent wrong output は
それ自体として塞ぐ価値がある。

到達性は高い: `images/` という srcdir 配下のディレクトリ名と、変換元画像の basename が
一致するだけで踏む。画像変換拡張（`sphinxcontrib.rsvgconverter` /
`sphinxcontrib.inkscapeconverter` / `sphinx.ext.imgconverter`）を使うプロジェクトが対象。

## Solution

`_track_image()` の rehome 先を、srcdir 相対 URI が構造的に生成し得ない名前空間にするか、
衝突を検出して一意化する。どちらか:

1. **専用名前空間**（推奨・単純）— 絶対 URI は `images/...` ではなく
   `_typst_converted/...` のような予約プレフィックス配下に rehome する。srcdir 側が
   同名ディレクトリを持つ可能性は残るが、`images/` に比べて桁違いに低い。
   `copy_image_files()` の dest 計算はそのままで済む。

2. **衝突検出＋一意化** — `rel_uri` が既に `self.images` にあり、かつ記録済みのソースが
   異なる場合に限り、接尾辞（`diagram-1.png` 等）で一意化して両方を追跡する。設計は
   保つが分岐が増える。Sphinx 自身が `env.images` の一意名生成でやっているのと同じ発想。

いずれの場合も **衝突ケースの回帰テストを1本追加すること**。`<srcdir>/images/x.png`
（通常画像）と `<doctreedir>/images/x.png`（変換画像）を同一プロジェクトに置き、
**2枚とも別々に outdir へコピーされ、2つの `image()` 呼び出しが異なるパスを指す**ことを
アサートする。既存の `tests/fixtures/absolute_image_render_gate/` を拡張するのが早い。

関連: [[2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri]]（同じ
`_track_image()` の別の穴。まとめて直すのが自然）
