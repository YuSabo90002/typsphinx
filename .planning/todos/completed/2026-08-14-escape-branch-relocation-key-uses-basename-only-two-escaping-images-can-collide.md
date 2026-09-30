---
created: 2026-08-14T22:05:00+09:00
title: "`_track_image()`'s escape branch keys the relocation on `basename` alone — two escaping absolute URIs sharing a basename collide onto one `_typst_converted/<basename>` key"
area: builder
resolves_phase: 55
source: .planning/phases/50-pr-131-image-path-defects/50-REVIEW.md (CR-01), 50-VERIFICATION.md (human_verification item 1, owner-dispositioned 2026-08-14)
severity: minor
files:
  - typsphinx/builder.py:938  # _track_image() escape branch — `f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"`
  - typsphinx/builder.py:951  # _track_image() collision branch — keeps the full `rel_uri`, the asymmetry
  - tests/test_builder.py  # where a RED for this belongs, beside the phase-50 relocation unit tests
---

## Problem

Phase 50 が `TypstBuilder._track_image()` の absolute-URI 分岐を 3 経路に広げたとき、
2 つの relocation 分岐でキーの組み立て方が非対称になった。

```python
# エスケープ／クロスドライブ分岐 (builder.py:938) — ディレクトリ情報を捨てる
key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"

# 衝突分岐 (builder.py:951) — 意図的に rel_uri 全体を保つ
key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"
```

そのため、**別ディレクトリにある同名 basename の絶対 URI が 2 つとも escape すると**、
両者が同一キーに潰れる:

```
/opt/ext-cache/setA/chart.png  → _typst_converted/chart.png
/opt/ext-cache/setB/chart.png  → _typst_converted/chart.png   ← 同じキー
```

`_track_image()` の `if key not in self.images` により先に track された方が勝ち、
`write()` は `sorted(docnames)` を回すので**どちらが勝つかは docname のアルファベット順**で決まる。
負けた側の文書は誤った画像を埋め込む。警告は 2 本出るが、どちらも単体では無害に見えるため、
「別々の画像が 1 つに潰れた」という事実はログから読み取れない。

これは **Phase 50 が IMG-01 で潰したのとまったく同じ失敗形状**（沈黙の誤出力）が、
同じフェーズで新設された分岐に一段深く入り込んでいる、という指摘である。

なお basename への平坦化そのものは恣意的な選択ではない。escape 分岐は定義上 `rel_uri` が
`..` を含む（それが escape の定義）ので、`rel_uri` をそのままキーにすると SC#2 の
「すべての宛先が outdir 配下」が壊れる。何らかの平坦化は必須で、basename は最も単純だが
情報を捨てる選択だった。

## Reachability

低い。二重の稀少条件が要る:

1. サードパーティ拡張が `doctreedir` 配下でない場所に絶対画像 URI を書く
   — Sphinx 標準の 3 つの post-transform（`ImageConverter` / `ImageDownloader` /
   `DataURIExtractor`）はすべて `<doctreedir>/images/` 配下に書くので、素の Sphinx では踏まない
   （Phase 50 CONTEXT の D-06 がこの分岐を「anomalous」と位置づけている理由）
2. さらに、そうして escape した画像が **2 つ以上**あり、かつ**別ディレクトリで basename が一致**する

## Solution

T-50-03 が「measured to occur したときの escape hatch」として既に文書化している
hashed-key 案をそのまま採る:

```python
key = f"{RESERVED_IMAGE_NAMESPACE}/{sha1(resolved_uri)[:8]}-{path.basename(resolved_uri)}"
```

`resolved_uri` の純粋関数なので **write-order 非依存**という D-02 の性質を保ったまま、
ディレクトリの違いをキーに反映できる。`..` を含まないので SC#2 の outdir 封じ込めも保たれる。

着手する場合は Phase 50 の作法に従い、**先に RED を記録すること**:
`tests/test_builder.py` の phase-50 relocation ユニットテスト群の隣に、
別ディレクトリの同名 basename が 2 つとも escape するケースを組み、
修正前の builder に対して失敗することを観測・記録してから直す。

## Disposition history

- Phase 50 の脅威モデル（T-50-03, `50-01-PLAN.md:414` / `50-02-PLAN.md:321`）は、レビュー前から
  この形状を **severity: low / disposition: accept** と評価し、hashed-key 代替を
  「measured to occur したときの documented escape」として記録していた。FA-02 も同じ残存リスクを開示済み。
- Phase 50 のコードレビュー（`50-REVIEW.md` CR-01）は同じ形状を **Critical** と評価し、
  重大度の見解が割れた。
- `50-VERIFICATION.md` はこれをコード正当性の問題ではなく製品判断として `human_verification` に回した。
- **2026-08-14、オーナー判断: follow-up todo 化。** Phase 50 のスコープ内では直さない
  — 無計画な本番コード変更は 50-02 の D-11 前後計測（diff 空）を無効化するため。

## Related

- [[2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir]] — IMG-01。
  Phase 50 で解決済み。本 todo はその修正が新設した分岐の中の同型残存。
- [[2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri]] — IMG-02。
  Phase 50 で解決済み。本 todo が指すのはまさにその escape 分岐。
