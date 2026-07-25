# Phase 29 — Live Evidence Record

This file is created by Plan 02 and **appended to** by Plans 03/04/05/06. Every later writer adds a new
`##` section after the existing ones and must never rewrite or reorder what is already here.

## SC#1 — /en/latest/ serves real content

**Command:**

```
curl -sS -o /tmp/p29-en-latest.html -w 'code=%{http_code} url=%{url_effective} size=%{size_download}\n' -L https://typsphinx.readthedocs.io/en/latest/
```

**Fetched:** 2026-07-25T14:00:05Z (UTC)

**Output:**

```
code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
```

**Matched phrase (from the captured body, with surrounding context):**

```
<h2>Key Features<a class="headerlink" href="#key-features" title="Link to this heading">¶</a></h2>
<ul class="simple">
<li><p><strong>Sphinx to Typst Conversion</strong>: Convert reStructuredText/Markdown to Typst format</p></li>
<li><p><strong>Dual Builder Integration</strong>:</p>
<ul>
```

**Proves:** `https://typsphinx.readthedocs.io/en/latest/` returns HTTP 200 and serves typsphinx's own
rendered `docs/source/index.rst` content — the distinctive "Sphinx to Typst Conversion" feature bullet
appears in the response body, not an RTD placeholder or a 404 page (SC#1, serving half).

## SC#4 — documentation root resolves

**Command (full redirect chain, headers + final status):**

```
curl -sS -D - -o /tmp/p29-root-body.html -L https://typsphinx.readthedocs.io/ -w 'FINAL: code=%{http_code} url=%{url_effective} size=%{size_download}\n' | grep -E '^(HTTP/|location:|FINAL)' -i
```

**Fetched:** 2026-07-25T14:00:13Z (UTC)

**Output (redirect chain — status code of each hop plus final effective URL):**

```
HTTP/2 302
location: https://typsphinx.readthedocs.io/en/latest/
HTTP/2 200
FINAL: code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
```

**Body content-match command and output:**

```
grep -q "Sphinx to Typst Conversion" /tmp/p29-root-body.html && echo BODY_MATCH_OK
```
```
BODY_MATCH_OK
```

**Proves:** `https://typsphinx.readthedocs.io/` issues a single HTTP 302 whose `Location` header names
`https://typsphinx.readthedocs.io/en/latest/`, and following that redirect lands on HTTP 200 with the
same distinctive index-page phrase present in the body. The final effective URL contains `latest` — the
documentation root resolves to an existing, content-serving version (RTD Default Version = `latest`),
not to a `stable` version that has no build yet (SC#4, RTD-04).

**Combined plan-prescribed verify command (both fetches, both content assertions, re-run for the record):**

```
curl -sS -o /tmp/p29-en-latest.html -w 'code=%{http_code} url=%{url_effective} size=%{size_download}\n' -L https://typsphinx.readthedocs.io/en/latest/ && curl -sS -o /tmp/p29-root.html -w 'code=%{http_code} url=%{url_effective} size=%{size_download}\n' -L https://typsphinx.readthedocs.io/ && grep -q 'Sphinx to Typst Conversion' /tmp/p29-en-latest.html && grep -q 'Sphinx to Typst Conversion' /tmp/p29-root.html && echo LIVE_FETCH_OK
```
```
code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
code=200 url=https://typsphinx.readthedocs.io/en/latest/ size=30451
LIVE_FETCH_OK
```

## Owner-Manual Steps (human_needed)

The following RTD web-UI actions have **no** `.readthedocs.yaml` representation and no API this phase is
authorized to script. They are recorded here exactly as the owner reported them in Task 1
(`checkpoint:human-action`, gate `blocking-human`) — **owner-reported, NOT machine-verified.** No command
in this repository can assert that these dashboard clicks happened; only their *outcome* (the fetches
above) is machine-verified.

1. **Slug confirmation** — `human_needed`. The owner confirmed on RTD's import screen that the slug
   `typsphinx` was unclaimed (it had been measured unclaimed on 2026-07-25 via a 404 at
   `https://typsphinx.readthedocs.io/`, but RTD's import screen is the authoritative check). The
   `SLUG TAKEN` stop condition did **not** fire.
2. **Project creation + GitHub connection** — `human_needed`. Owner-reported: `slug=typsphinx`, created
   from the GitHub repository `YuSabo90002/typsphinx`, with GitHub connected so pushes trigger builds.
3. **Admin Language = English** — `human_needed`. Owner-reported: `admin_language=English`.
4. **Default Version left at `latest`** — `human_needed`. Owner-reported: `default_version=latest`. Not
   set to `stable` (confirmed independently below by the SC#4 root-fetch, which is machine-verified).

**Fifth owner-manual action, beyond the plan's original four** (recorded per explicit executor
instruction — see reasoning in the next section and in `## Phase 33 Handoff Precondition`):

5. **RTD Default Branch set to the milestone branch** — `human_needed`. The plan assumed the branch
   carrying Plan 01's commits would already be buildable by RTD; it was not, because the milestone
   branch (`gsd/v0.6.4-read-the-docs-migration`) was unpushed at the time and RTD's `latest` version
   tracks the repository's default branch, which was `main`. The orchestrator surfaced this to the
   owner, who chose: push the milestone branch (performed by the orchestrator, commit `2d6ff27`), and
   set **RTD Admin → Advanced settings → Default branch = `gsd/v0.6.4-read-the-docs-migration`** so that
   `latest` tracks the milestone branch for the duration of the milestone (performed by the owner in the
   RTD dashboard — `human_needed`, not machine-verifiable from this repository). This step's reversal is
   recorded as a second, separate precondition in `## Phase 33 Handoff Precondition` below.

**Owner-reported build identity carried forward from Task 1** (used again in the next section):

```
slug=typsphinx
admin_language=English
default_version=latest
build_url=https://app.readthedocs.org/projects/typsphinx/builds/33756675/
build_status=Build succeeded
built_commit=2d6ff27bea2ae205a3f686b1cc53f8d81f9c5ab7
```

## SC#1 — install provenance from the raw build log

**Build identity** (owner-reported, Task 1):

- Build-detail URL: `https://app.readthedocs.org/projects/typsphinx/builds/33756675/`
- Build status: `Build succeeded`
- Built commit: `2d6ff27bea2ae205a3f686b1cc53f8d81f9c5ab7`

**Raw-log HTTP fetch (strengthening step, attempted and successful):**

```
curl -sS -o /tmp/p29-buildlog-33756675.txt -w 'code=%{http_code} type=%{content_type} size=%{size_download}\n' https://app.readthedocs.org/api/v2/build/33756675.txt
```

```
code=200 type=text/plain; charset=utf-8 size=81479
```

The raw log **is** retrievable over public HTTP — no fallback to owner-paste-only was needed for this
build. (`https://readthedocs.org/api/v2/build/33756675.txt` was also confirmed to return the identical
body during discovery; the `app.readthedocs.org` host above is the one recorded as the command of
record.)

**Decisive install-provenance excerpt, read directly from the fetched log at line 164** (confirmed
present in the fetched copy at `/tmp/p29-buildlog-33756675.txt`):

```
 + typsphinx==0.6.3 (from file:///home/docs/checkouts/readthedocs.org/user_builds/typsphinx/checkouts/latest)
```

Supporting context, lines 116 and 127 of the same log:

```
   Building typsphinx @ file:///home/docs/checkouts/readthedocs.org/user_builds/typsphinx/checkouts/latest
      Built typsphinx @ file:///home/docs/checkouts/readthedocs.org/user_builds/typsphinx/checkouts/latest
```

**Reading:** the decisive token is `(from file:///home/docs/checkouts/readthedocs.org/user_builds/typsphinx/checkouts/latest)` —
`uv sync` reports `typsphinx` as installed **`from file://...`**, an absolute filesystem path into RTD's
own checkout of this repository's working tree, not from a package index. A PyPI-index resolve would
instead have printed a registry/hash-based provenance token — the familiar `+ typsphinx==0.6.3` line
followed by a wheel filename and a `--hash=sha256:...` (or, in `uv`'s own resolver output, a
`(index: https://pypi.org/simple)` — style annotation) with no `file://` path at all, and no `Building
typsphinx @ ...` / `Built typsphinx @ ...` compile-from-source lines, since a PyPI wheel is fetched
pre-built and never locally "Built". The presence of the `file://...checkouts/latest` path, plus the
paired `Building`/`Built` lines naming that same path, is what evidences a checked-out-commit install
rather than a stale published wheel shadowing the working tree (T-29-05).

This fetched copy of the log agrees with the excerpt supplied in the orchestrator's brief; no divergence
was found.

**Strengthening scan — `latexmk`, `pdflatex`, `.tex` (Plan 04 pre-observation only; Plan 04 owns the
SC#2 verdict):**

```
grep -o -E 'latexmk|pdflatex|\.tex' /tmp/p29-buildlog-33756675.txt | wc -l
```

```
0
```

This build predates any PDF-compile step in `.readthedocs.yaml` (Plan 01 was HTML-only), so a count of
zero is the expected pre-observation, not a verdict on RTD-03/SC#2 — that verdict belongs to Plan 04
once a PDF build step exists.

## Phase 33 Handoff Precondition

RTD's **Default Version** is deliberately left at `latest` for the entire duration of the v0.6.4
milestone. `stable` cannot exist until the `v0.6.4` tag itself builds green, because Read the Docs has
refused builds lacking a `.readthedocs.yaml` since 2023-09-25 and no tag earlier than `v0.6.4` contains
one. Therefore:

**Precondition A — Default Version flip (`latest` → `stable`):** an owner-manual step handed to
**Phase 33**, to be performed only **after** the `v0.6.4` tag has been pushed and has built green.
**Not yet done. `human_needed`.**

**Precondition B — Default Branch reversal (milestone branch → `main`):** a second, separate
owner-manual step, also handed to **Phase 33** (or later, once the milestone merges to `main`). RTD's
**Admin → Advanced settings → Default branch** is currently set to
`gsd/v0.6.4-read-the-docs-migration` (see item 5 in `## Owner-Manual Steps (human_needed)` above) so
that `latest` tracks the milestone branch while it is unmerged. Once the milestone branch merges into
`main`, this setting must be reversed: **Default branch `gsd/v0.6.4-read-the-docs-migration` → `main`**,
so that `latest` resumes tracking the repository's real default branch. This is distinct from
Precondition A and must not be merged into it — one governs which *version* is default (`latest` vs.
`stable`), the other governs which *branch* the `latest` version itself tracks.
**Not yet done. `human_needed`.**

Both preconditions stand alongside the standing invariant that Phases 30, 31 and 32 each re-fetch the
documentation root as part of their own verification, so RTD-04 remains a checked invariant across the
whole migration window rather than a one-time check performed only here.

## Pre-RTD Local Simulation of build.jobs.build.pdf

This section is Plan 03, Task 3. `.readthedocs.yaml`'s `build.jobs.build.pdf` override (landed in commit
`38c7157`) is run locally, command-for-command, with `$READTHEDOCS_OUTPUT` substituted by a fresh temp
root and the sandbox-compatible `uv run python -m sphinx` invocation substituted for the `sphinx-build`
console script (CLAUDE.md's documented NixOS workaround — the builder and its arguments are identical).
This is a one-off, hand-run sequence; **no comparison script is committed** (D-15) — the commands and
their output below are pasted verbatim for the record.

**Commands (logically identical to the four `build.jobs.build.pdf` entries):**

```
rm -rf /tmp/p29-03-sim
mkdir -p /tmp/p29-03-sim/doctrees
uv run python -m sphinx -b typstpdf -d /tmp/p29-03-sim/doctrees docs/source /tmp/p29-03-sim/out
mkdir -p /tmp/p29-03-sim/_readthedocs/pdf/
cp /tmp/p29-03-sim/out/*.pdf /tmp/p29-03-sim/_readthedocs/pdf/
```

**Build output (tail — full log confirms `build succeeded, 2 warnings`, matching the 2026-07-25
measurement recorded in 29-CONTEXT.md):**

```
ビルド中 [typstpdf]: 更新された 13 件のソースファイル
...
writing output... [api/index] done
writing output... [changelog] done
writing output... [contributing] done
writing output... [examples/advanced] done
writing output... [examples/basic] done
writing output... [examples/index] done
writing output... [index] done
writing output... [installation] done
writing output... [quickstart] done
writing output... [user_guide/builders] done
writing output... [user_guide/configuration] done
writing output... [user_guide/index] done
writing output... [user_guide/templates] done
Compiling 1 master document(s) to PDF...
Generated PDF: /tmp/p29-03-sim/out/typsphinx.pdf
build succeeded, 2 warnings.
```

Two pre-existing docutils warnings (`Unexpected indentation` / `Block quote ends without a blank line`
in `typsphinx/translator.py`'s `visit_toctree` docstring) are unrelated to this plan's `.readthedocs.yaml`
change — they are a Sphinx autodoc parsing note on this repository's own source, out of scope here.

**Builder's own output directory — full listing (10 entries; more than one, confirming the `*.pdf`
filter below is load-bearing, not decorative):**

```
_template.typ
api
changelog.typ
contributing.typ
examples
installation.typ
quickstart.typ
typsphinx.pdf
typsphinx.typ
user_guide
```

**Simulated RTD download directory — full listing (exactly one file):**

```
typsphinx.pdf
```

**Verification command and output, run a second time on a fresh temp root to confirm reproducibility
(the exact automated command this plan's task specifies):**

```
rm -rf /tmp/p29-03-sim2 && mkdir -p /tmp/p29-03-sim2/doctrees && uv run python -m sphinx -b typstpdf -q -d /tmp/p29-03-sim2/doctrees docs/source /tmp/p29-03-sim2/out && mkdir -p /tmp/p29-03-sim2/_readthedocs/pdf/ && cp /tmp/p29-03-sim2/out/*.pdf /tmp/p29-03-sim2/_readthedocs/pdf/ && test "$(ls -1 /tmp/p29-03-sim2/_readthedocs/pdf/)" = "typsphinx.pdf" && test "$(ls -1 /tmp/p29-03-sim2/out | wc -l)" -gt 1 && echo SIM_OK
```

```
SIM_OK
```

**Proves:** the manifest's exact `build.jobs.build.pdf` command sequence is syntactically and
semantically sound — it builds, the mkdir-before-copy ordering works, and the `*.pdf` glob correctly
admits exactly `typsphinx.pdf` into the simulated download directory while leaving the builder's other
9 output entries (the `.typ` sources, `_template.typ`, and the `api`/`examples`/`user_guide`
subdirectories) behind — before any RTD build cycle is spent proving the same thing live.

## D-12 Baseline (local, this commit)

This section is Plan 03, Task 3's dated, per-commit D-12 baseline, captured via `pypdf` (already
declared in the `dev` extra — no new dependency) against the PDF produced by the simulation above.

**Command:**

```
python -c "
import pypdf, os
r = pypdf.PdfReader('/tmp/p29-03-sim/_readthedocs/pdf/typsphinx.pdf')
print('pages', len(r.pages))
fonts = set()
for page in r.pages:
    res = page.get('/Resources')
    if res is None:
        continue
    fontdict = res.get('/Font')
    if fontdict is None:
        continue
    for k, v in fontdict.items():
        obj = v.get_object()
        bf = obj.get('/BaseFont')
        if bf:
            fonts.add(str(bf))
for f in sorted(fonts):
    print('/BaseFont', f)
print('bytes', os.path.getsize('/tmp/p29-03-sim/_readthedocs/pdf/typsphinx.pdf'))
"
```

**Output:**

```
pages 93
/BaseFont /BLJSKO+IPAexGothic
/BaseFont /JWAONO+NotoSansCJKjp-Thin
/BaseFont /LFIBAF+LibertinusSerif-Italic-Identity-H
/BaseFont /OYQRGH+DejaVuSansMono
/BaseFont /PEKEPN+LibertinusSerif-Bold-Identity-H
/BaseFont /SEPNHW+LibertinusSerif-Semibold-Identity-H
/BaseFont /SVGCJT+Unifont-Identity-H
/BaseFont /UOQBSW+LibertinusSerif-Regular-Identity-H
/BaseFont /VOIDKS+DejaVuSansMono-Bold
bytes 1693967
```

**Baseline summary (this commit):**

| Field | Value |
|-------|-------|
| Page count | **93** |
| Byte size | **1,693,967 bytes** |
| Embedded `/BaseFont` list (9 fonts, sorted) | `BLJSKO+IPAexGothic`, `JWAONO+NotoSansCJKjp-Thin`, `LFIBAF+LibertinusSerif-Italic-Identity-H`, `OYQRGH+DejaVuSansMono`, `PEKEPN+LibertinusSerif-Bold-Identity-H`, `SEPNHW+LibertinusSerif-Semibold-Identity-H`, `SVGCJT+Unifont-Identity-H`, `UOQBSW+LibertinusSerif-Regular-Identity-H`, `VOIDKS+DejaVuSansMono-Bold` |
| Commit SHA (the `.readthedocs.yaml` state simulated — Task 2's commit) | `38c71579053ecb1fc4b4b157eef1a45414a8cb1a` |
| Local interpreter version | Python 3.13.13 (CPython) |
| `.readthedocs.yaml` `build.tools.python` | `"3.12"` |

**Notes:**

- **Interpreter-minor caveat:** the local interpreter used for this baseline is Python 3.13.13, while
  `.readthedocs.yaml`'s `build.tools.python` provisions `"3.12"` on RTD. This is expected — the worktree's
  `uv sync` resolved the newer minor available on this host, not `3.12` specifically. The D-12 bar (page
  count and extracted text) is not expected to be interpreter-minor sensitive; if Plan 05's RTD-built PDF
  comparison observes a mismatch attributable to this difference, it must be recorded verbatim rather
  than explained away.
- **D-13 caveat:** per D-13, an exact embedded-font-list match is **not** the bar for Plan 05's
  comparison. Several fonts in the list above (`IPAexGothic`, `NotoSansCJKjp-Thin`, `DejaVuSansMono`,
  `DejaVuSansMono-Bold`, `Unifont`) are host-provided, not typst-py-embedded — a perfectly healthy RTD
  build cannot be expected to reproduce this exact list. Only CJK *coverage* (at least one font with CJK
  glyph support) is asserted in Plan 05.
- This baseline's page count (93), font count (9), and byte size are consistent with the 2026-07-25
  measurement recorded in `29-CONTEXT.md` § "CJK fonts — a new risk found by measurement", re-taken here
  for this exact commit rather than reused from memory.
