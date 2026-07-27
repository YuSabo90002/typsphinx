# Phase 32 Plan 01: Pre-Teardown Evidence Gate

**Gathered:** 2026-07-27 (Phase 32 execution, Plan 01)

Every observation recorded in this file was fetched live, over real HTTP, during Phase 32
execution. No observation is carried over, cited, or paraphrased from Phase 29, Phase 30,
Phase 30.1, or Phase 31 evidence — this satisfies SC#1 and milestone invariant #4 (fresh
evidence at execution time).

## Gate check 1 — RTD HTML liveness and Japanese content (D-01)

### (a) English HTML liveness

```
$ curl -sS -L -o /dev/null -w "%{http_code} %{url_effective}\n" https://typsphinx.readthedocs.io/en/latest/
200 https://typsphinx.readthedocs.io/en/latest/
```

### (b) Documentation root resolution

```
$ curl -sS -L -o /dev/null -w "%{http_code} %{url_effective}\n" https://typsphinx.readthedocs.io/
200 https://typsphinx.readthedocs.io/en/latest/
```

The bare root returns `200` and its effective URL resolves to the versioned path
`https://typsphinx.readthedocs.io/en/latest/` — RTD-04 root resolution still holds.

### (c) Japanese HTML content proof

```
$ curl -sS -L -w "\nHTTP_STATUS:%{http_code}\n" https://typsphinx.readthedocs.io/ja/latest/user_guide/builders.html -o /tmp/scratch/ja_builders.html
HTTP_STATUS:200
```

```
$ grep -o 'ビルダー' /tmp/scratch/ja_builders.html | head -1
ビルダー
```

```
$ python3 -c "
import re
with open('/tmp/scratch/ja_builders.html', encoding='utf-8') as f:
    text = f.read()
count = len(re.findall(r'[぀-ヿ一-鿿]', text))
print(count)
"
1038
```

The ja page returns HTTP `200`, contains the literal string `ビルダー`, and its CJK
character count (Hiragana + Katakana + CJK Unified Ideographs) is **1038**.

### (d) English same-docname control

```
$ curl -sS -L -w "\nHTTP_STATUS:%{http_code}\n" https://typsphinx.readthedocs.io/en/latest/user_guide/builders.html -o /tmp/scratch/en_builders.html
HTTP_STATUS:200
```

```
$ python3 -c "
import re
with open('/tmp/scratch/en_builders.html', encoding='utf-8') as f:
    text = f.read()
count = len(re.findall(r'[぀-ヿ一-鿿]', text))
print(count)
"
0
```

The English control page's CJK count is **0**.

### Verdict — Gate check 1

- en HTML status: `200` — PASS
- root resolution status: `200`, effective URL versioned (`/en/latest/`) — PASS
- ja HTML status: `200` — PASS
- `ビルダー` match present in ja body: yes — PASS
- ja CJK count: **1038** (>= 200 required) — PASS
- ja CJK count vs en CJK count: ja=**1038**, en=**0** — 1038 >= 10 * 0 holds trivially, and
  the en control's zero count is itself corroborating evidence: the English `user_guide/builders`
  page carries no incidental CJK text on this docname, so the ja page's 1038 CJK characters are
  not an artifact of shared boilerplate — they are genuine translated content. PASS.

**Gate check 1: PASS** (all five sub-checks pass; ja content is verified translated, not
English-under-a-ja-URL, per D-01/I18N-01's failure mode).
