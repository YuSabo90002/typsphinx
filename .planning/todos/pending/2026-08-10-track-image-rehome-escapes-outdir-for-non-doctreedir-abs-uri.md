---
created: 2026-08-10T10:41:00+09:00
title: doctreedir 配下でない絶対 URI で `_track_image()` の rehome が outdir 外へ escape する
area: builder
severity: minor
files:
  - typsphinx/builder.py  # TypstBuilder._track_image()
  - typsphinx/builder.py  # TypstBuilder.copy_image_files()
---

## Problem

PR #131（Issue #130 の修正、2026-08-10 マージ）で導入された
`TypstBuilder._track_image()` は、絶対 URI を無条件に

    rel_uri = path.relpath(resolved_uri, self.doctreedir)

で rehome する。`resolved_uri` が `doctreedir` **配下**にある前提が置かれているが、
`relpath` はその前提が崩れると `../` 付きのパスを返す。`copy_image_files()` の
`dest = path.join(self.outdir, imguri)` はそれをそのまま結合するため、
**outdir の外へ書き込む**。

2026-08-10 のレビューで rehome 演算を直接実測:

```
/proj/_build/.doctrees/images/ok.png → images/ok.png          → dest /proj/_build/images/ok.png   OK
/proj/_build/_images/plot.png        → ../_images/plot.png    → dest /proj/_images/plot.png       ESCAPES
/tmp/generated/chart.png             → ../../../tmp/...       → dest /tmp/generated/chart.png     ESCAPES
```

3ケース目は `src == dest` に戻るため、**Issue #130 の "are the same file" が再現する**
（その形状に対しては修正が効いていない）。2ケース目はユーザーのプロジェクト領域へ
ファイルを書き出す。さらに emit される `image("../_images/plot.png")` は outdir の外を
指すので、Typst の root 制約に引っかかる可能性が高い。

**到達性は低い。** Sphinx 標準の3つの post-transform（`ImageConverter` /
`ImageDownloader` / `DataURIExtractor`）はすべて `<doctreedir>/images/` 配下に書くので、
素の Sphinx 経由では踏まない。絶対 URI を別の場所（outdir 配下や一時ディレクトリ）に
置くサードパーティ拡張を使った場合にのみ顕在化する。そのため severity は minor。

付随して、Windows でドライブを跨いだ場合 `path.relpath` は `ValueError` を送出し
ビルドがクラッシュするが、`doctreedir` と画像が別ドライブになる状況は実質到達不能。

## Solution

`_track_image()` に安価なガードを足す。rehome 結果が `doctreedir` の外を指す場合
（`rel_uri` が `..` で始まる、または `os.pardir` を含む）は:

- `logger.warning()` で「絶対画像 URI が doctreedir 配下にないため rehome できない」と
  明示し、
- basename へのフォールバック（例 `_typst_converted/<basename>` へ退避）とするか、
  少なくとも outdir 外への書き込みは行わない

`path.relpath` の `ValueError` も併せて捕捉しておくと Windows のクラッシュ経路も塞げる。

同じ `_track_image()` を触るので、[[2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir]]
と**まとめて1つの変更として直すのが自然**。単体で phase を切るほどの規模ではない。
