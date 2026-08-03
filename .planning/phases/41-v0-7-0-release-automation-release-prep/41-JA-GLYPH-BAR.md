# Phase 41 SC#3 — the `ja` Four-Check Glyph Bar

**Purpose (restated from `41-CONTEXT.md`):** Typst's font fallback is silent — no warning, no
error — so a PDF with substituted glyphs builds clean, downloads clean, and extracts the correct
characters. This milestone never names a font family, but it added 24 new `raw(` call sites, and
`raw()` resolves to Typst's default monospace family, which has no CJK coverage. The four checks
(Phase 29 D-12 / Phase 30.1 D-03) are: (1) page count, (2) extracted text and CJK density, (3)
embedded `/BaseFont` enumeration, (4) owner visual confirmation.

**Comparison design (D-15):** both PDFs are built locally, on this same machine, with the same
toolchain and font environment — one from `main`, one from this milestone's post-bump HEAD — so the
only difference between them is v0.7.0's own changes.

---

## Provenance

### `typsphinx-doc-translations` clone (D-17)

| Item | Value |
|---|---|
| Clone location | `.planning/phases/41-v0-7-0-release-automation-release-prep/translations-repo/` (never committed — `git status --short` shows it `??`) |
| Clone command | `git clone --quiet --recurse-submodules https://github.com/YuSabo90002/typsphinx-doc-translations.git .planning/phases/41-v0-7-0-release-automation-release-prep/translations-repo` |
| Clone HEAD SHA | `4a1142cd351c28681f6d4c764854d2a741daad2b` |
| Submodule pin (`git submodule status`) | `5888ee024d836002cb920ceff9e5df5889b4762c typsphinx (v0.6.5-6-g5888ee0)` |
| `.gitmodules` | `[submodule "typsphinx"]` / `path = typsphinx` / `url = https://github.com/YuSabo90002/typsphinx.git` / `branch = main` |

### Pin freshness check (Pitfall 5)

```
$ git ls-remote https://github.com/YuSabo90002/typsphinx.git main
5888ee024d836002cb920ceff9e5df5889b4762c	refs/heads/main
```

**Verdict: the clone's submodule pin (`5888ee0...`) is byte-identical to real `main`'s live tip at
the moment of this measurement.** The pin is fresh — no re-clone or re-checkout of the submodule
was needed. Per the plan's own instruction, this determines only which SHA the clone's submodule
is labelled with; the actual "before" build (below) uses a local worktree of THIS repository
pinned at its own `main` ref, not the clone's submodule checkout.

### The two comparison trees

| Tree | Role | HEAD SHA | Provisioning |
|---|---|---|---|
| `/tmp/p41-main-tree` (`git worktree add /tmp/p41-main-tree main`) | "before" | `51e02b6b61b314c99740883fb4bee7ce7b9be76b` | Own `uv sync --extra dev --extra docs` run, own `.venv` |
| this plan's worktree (HEAD) | "after" | `aa9d2f06ad854f6f96d285d669ba4bb91b053f31` | Own `uv sync --extra dev --extra docs` run, own `.venv` (already provisioned at plan start) |

Note: this repository's local `main` branch (`51e02b6`) sits 6 commits behind the live GitHub
`main` tip measured above (`5888ee0`) — the milestone branched off `main` before those 6 commits
landed. Per the plan's own design, the "before" build deliberately uses this repository's local
`main` ref (the milestone's actual merge-base), not a freshly re-fetched GitHub tip, so the
comparison isolates v0.7.0's own changes rather than picking up unrelated upstream commits that
never shared a working tree with this milestone.

### Import-provenance proof (T-41-14 mitigation)

```
$ cd /tmp/p41-main-tree && uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
/tmp/p41-main-tree/typsphinx/__init__.py

$ uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a07298901969db601/typsphinx/__init__.py
```

**Verdict: each build's `import typsphinx` resolves to a path under its OWN tree** — the "before"
build cannot be silently importing HEAD's translator through a shared editable-install finder.

### `docs/` identity check (Step 4)

```
$ git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- docs/
(empty)
```

**Verdict: zero lines changed under `docs/` this milestone.** This is what makes the PDF
comparison attributable to translator changes alone, not to any change in the source `.rst`/
locale content.

### Locale catalog installation (Step 5)

`docs/locale/` is untracked in this repository (confirmed: absent before this plan, `git status
--short` shows it `??` afterward). In BOTH trees:

```
rm -rf docs/locale   # (was already absent in both trees; no-op)
mkdir -p docs/locale
cp -a <translations-repo>/locale/. docs/locale/
```

`translations-repo/locale/ja/LC_MESSAGES/` carries 8 entries (the project's `.po` catalogs:
`api/`, `changelog.po`, `contributing.po`, `examples/`, `index.po`, plus the remaining
`user_guide`/`installation`/`quickstart` catalogs) — copied identically into both trees.

### The two builds (Step 6)

Both builds set `SPHINX_LANGUAGE=ja` explicitly in the environment (RESEARCH.md Assumption A1's
unconditional hedge — set regardless of whatever the `ja` RTD project does at the project-settings
level), and both were invoked as `uv run python -m sphinx -b typstpdf` (not a bare `sphinx-build`
binary), per this project's NixOS guidance.

**"Before" (main) build:**

```
$ SPHINX_LANGUAGE=ja uv run python -m sphinx -b typstpdf \
    -d /tmp/p41-main-doctrees \
    /tmp/p41-main-tree/docs/source \
    /tmp/p41-main-out
CWD: /tmp/p41-main-tree
EXIT: 0

Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [ja]... 完了
...
writing output... [api/index] done
...
Compiling 1 master document(s) to PDF...
Generated PDF: /tmp/p41-main-out/typsphinx.pdf
build succeeded, 5 warnings.

stderr (5 warnings, verbatim):
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/tmp/p41-main-tree/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/tmp/p41-main-tree/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
/tmp/p41-main-tree/docs/source/quickstart.rst:9:<translated>:1: WARNING: Inline strong start-string without end-string. [docutils]
/tmp/p41-main-tree/docs/source/quickstart.rst:9:<translated>:1: WARNING: Inline strong start-string without end-string. [docutils]
WARNING: unknown node type: <problematic ids="id2" refid="id1">**</problematic>
```

**"After" (HEAD) build:**

```
$ SPHINX_LANGUAGE=ja uv run python -m sphinx -b typstpdf \
    -d /tmp/p41-head-doctrees \
    /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a07298901969db601/docs/source \
    /tmp/p41-head-out
CWD: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a07298901969db601
EXIT: 0

Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [ja]... 完了
...
writing output... [api/index] done
...
Compiling 1 master document(s) to PDF...
Generated PDF: /tmp/p41-head-out/typsphinx.pdf
build succeeded, 5 warnings.

stderr (5 warnings, verbatim — identical set to the "before" build):
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a07298901969db601/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a07298901969db601/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a07298901969db601/docs/source/quickstart.rst:9:<translated>:1: WARNING: Inline strong start-string without end-string. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a07298901969db601/docs/source/quickstart.rst:9:<translated>:1: WARNING: Inline strong start-string without end-string. [docutils]
WARNING: unknown node type: <problematic ids="id2" refid="id1">**</problematic>
```

**Both builds' log lines confirm `[ja]` catalog loading** (`翻訳カタログをロードしています
[ja]... 完了`), so neither silently produced an English PDF. **Both exited 0.** The `visit_toctree`
docstring indentation defect (unrelated to D-12's `visit_desc_sig_name` fix) and the
`quickstart.rst` translated-string unbalanced-`**` defect are PRE-EXISTING on both `main` and
HEAD (identical on both sides, confirmed by re-running both builds from completely clean
doctree/output directories after an initial run showed a false asymmetry caused by Sphinx's
incremental-build environment cache suppressing re-parse warnings on a doctree-dir reuse — the
numbers recorded here are from the clean, non-incremental rebuild of both trees). Neither defect
is in this plan's scope to fix (D-12 fixed only `visit_desc_sig_name`'s unbalanced asterisk;
`visit_toctree`'s own docstring is unchanged by this milestone — confirmed: `git diff
51e02b6..HEAD -- typsphinx/translator.py | grep visit_toctree` is empty).

### Built PDFs

| Build | Path | Size | SHA-256 |
|---|---|---|---|
| "before" (`main`, `51e02b6`) | `/tmp/p41-main-out/typsphinx.pdf` | 1,942,905 bytes | `495ced3ea21651c3301d6d4eda819ebf35a2f1c7c66b80d704cdb7115df27187` |
| "after" (HEAD, `aa9d2f0`) | `/tmp/p41-head-out/typsphinx.pdf` | 2,206,751 bytes | `b64cf3563c04be2052eede5a629250a7c829db1118fdf44a82804746494f605f` |

(Both PDFs retained under `/tmp` for the remainder of the phase per the plan's Task 4 instruction —
neither is committed to this repository; `git ls-files '*.pdf'` is unaffected.)

### Fence check (this plan takes no irreversible action)

```
$ git tag -l v0.7.0
(empty)
$ git ls-remote --tags origin v0.7.0
(empty)
$ git -C .planning/phases/41-v0-7-0-release-automation-release-prep/translations-repo reflog | grep -i push
(no output -- no push occurred against the clone's remote)
```

---

## Check 1 — Page Count

```python
import pypdf
for label, path in [("before/main", "/tmp/p41-main-out/typsphinx.pdf"),
                     ("after/head", "/tmp/p41-head-out/typsphinx.pdf")]:
    r = pypdf.PdfReader(path)
    print(f"{label}: {path} -> {len(r.pages)} pages")
```

```
before/main: /tmp/p41-main-out/typsphinx.pdf -> 94 pages
after/head: /tmp/p41-head-out/typsphinx.pdf -> 94 pages
```

**Delta: 0.** As a sanity cross-check, page 1's extracted text reads `typsphinx / YuSabo / 0.6.5 /
1` on the "before" PDF and `typsphinx / YuSabo / 0.7.0 / 1` on the "after" PDF — confirming each
build's title page carries its own tree's version string, as expected, without changing the total
page count.

**Verdict:** a zero-page-count delta despite this milestone's substantial typography changes
(signature typesetting, structural indentation, admonition/rubric redesign, citations) indicates
the overall pagination/column-width envelope was not shifted by the redesign — consistent with
`STATE.md`'s own SIG-07 measurement that the production column width (453.54pt) comfortably
contains the corpus's worst-case signature widths. This is not itself evidence about glyph
fidelity (see "What these checks cannot prove" below) — it only rules out gross reflow/overflow
differences between the two builds.

---

## Check 2 — Extracted Text and CJK Density

Every extracted-text string below has had U+200B (ZWSP, introduced by SIG-07's hanging-indent
mechanism per `STATE.md`'s risk note) stripped BEFORE any character count or comparison, using
`text.replace("​", "")`.

CJK-density regex (Phase 30.1's exact method): `[぀-ゟ゠-ヿ一-鿿㐀-䶿＀-￯]` (Hiragana / Katakana /
CJK Unified Ideographs / CJK Ext-A / Halfwidth-Fullwidth Forms), applied per-page via `pypdf`'s
`extract_text()`.

```
=== before/main: /tmp/p41-main-out/typsphinx.pdf ===
pages: 94
total CJK chars (ZWSP-stripped): 6050
title page (1-idx 1): density=0
per-third best pages (1-idx): [5, 32, 74] -> densities [400, 127, 60]
overall best page (1-idx 5): density=400

=== after/head: /tmp/p41-head-out/typsphinx.pdf ===
pages: 94
total CJK chars (ZWSP-stripped): 6084
title page (1-idx 1): density=0
per-third best pages (1-idx): [5, 32, 63] -> densities [400, 127, 60]
overall best page (1-idx 5): density=400

=== DELTA ===
page count delta: 0
CJK total delta: +34
```

**Verdict:** the document-total CJK character count is essentially unchanged (+34 out of ~6,050,
a 0.56% increase, not a drop). This is the opposite of the failure signature the check is looking
for (a LARGE unexplained DROP on the HEAD side, indicating characters that no longer extract
because they were rendered from a substituting font) — the total moved slightly UP, plausibly
from minor content/whitespace-segmentation differences in how `pypdf` tokenizes the reflowed
layout, not from any lost glyphs. **This check is necessary but NOT sufficient**: a substituted
glyph very often still extracts as the correct Unicode character even when rendered in a font
with no CJK coverage (the glyph LOOKS wrong but the underlying character codepoint in the PDF's
text layer is unaffected) — which is precisely why check 4 (the owner's visual confirmation)
exists and cannot be replaced by this check passing.

The two builds' third-segment density peaks land on different absolute pages (main: page 74,
head: page 63) despite identical total page counts — both are legitimate API-reference pages
within the "Writer and Translator" section (pages 38-80 per the PDF outline/bookmarks), and the
11-page shift reflects internal reflow within that large section (some sub-sections got shorter,
others longer, without changing the section's or the document's overall page count). Both pages
are included in the check-4 sample below so nothing from either build's density profile is missed.

---

## Check 3 — Embedded Font Enumeration

PDF font-subsetting prepends a 6-uppercase-letter tag (e.g. `DAXSNV+`) to each embedded subset's
`/BaseFont` name, and this tag is regenerated randomly on every compile — even for an unchanged
font family. The raw `/BaseFont` names are listed first, followed by the subset-tag-stripped
family names actually compared (`re.sub(r'^(/?)[A-Z]{6}\+', r'\1', name)`).

```
before/main: /tmp/p41-main-out/typsphinx.pdf
  raw /BaseFont entries:
    /DAXSNV+NotoSerifCJKjp-ExtraLight
    /ECZKXT+LibertinusSerif-Semibold-Identity-H
    /GSKXSA+LibertinusSerif-Italic-Identity-H
    /MPJEAQ+NotoSerifCJKjp-ExtraLight
    /OSEFKB+NotoSerifCJKjp-ExtraLight
    /OYQRGH+DejaVuSansMono
    /PJTDIO+LibertinusSerif-Bold-Identity-H
    /SVGCJT+Unifont-Identity-H
    /VBUZID+LibertinusSerif-Regular-Identity-H
    /VOIDKS+DejaVuSansMono-Bold
  stripped font families (8 distinct):
    /DejaVuSansMono
    /DejaVuSansMono-Bold
    /LibertinusSerif-Bold-Identity-H
    /LibertinusSerif-Italic-Identity-H
    /LibertinusSerif-Regular-Identity-H
    /LibertinusSerif-Semibold-Identity-H
    /NotoSerifCJKjp-ExtraLight
    /Unifont-Identity-H

after/head: /tmp/p41-head-out/typsphinx.pdf
  raw /BaseFont entries:
    /DAXSNV+NotoSerifCJKjp-ExtraLight
    /GHXZPS+DejaVuSansMono-Bold
    /HUGOQZ+DejaVuSansMono-Oblique
    /IIDQTY+LibertinusSerif-Bold-Identity-H
    /MNLOER+LibertinusSerif-Regular-Identity-H
    /OSEFKB+NotoSerifCJKjp-ExtraLight
    /OXAESH+LibertinusSerif-Italic-Identity-H
    /SVGCJT+Unifont-Identity-H
    /SXDUOA+DejaVuSansMono
    /UFIGDA+NotoSerifCJKjp-ExtraLight
  stripped font families (8 distinct):
    /DejaVuSansMono
    /DejaVuSansMono-Bold
    /DejaVuSansMono-Oblique
    /LibertinusSerif-Bold-Identity-H
    /LibertinusSerif-Italic-Identity-H
    /LibertinusSerif-Regular-Identity-H
    /NotoSerifCJKjp-ExtraLight
    /Unifont-Identity-H

Intersection (7 families):
  /DejaVuSansMono
  /DejaVuSansMono-Bold
  /LibertinusSerif-Bold-Identity-H
  /LibertinusSerif-Italic-Identity-H
  /LibertinusSerif-Regular-Identity-H
  /NotoSerifCJKjp-ExtraLight
  /Unifont-Identity-H

Symmetric difference (2 families):
  /DejaVuSansMono-Oblique  [head only]
  /LibertinusSerif-Semibold-Identity-H  [main only]
```

**Which families carry CJK coverage:** `NotoSerifCJKjp-ExtraLight` is the only CJK-coverage font
embedded in either PDF (fc-list confirms this machine has `Noto Serif CJK JP:style=Light`
installed). `LibertinusSerif-*` (the proportional body/heading serif), `DejaVuSansMono*` (the
`raw()` monospace family), and `Unifont-Identity-H` (a narrow glyph-coverage fallback Typst pulls
in automatically, present on both sides) carry no CJK coverage.

**Verdict:** `NotoSerifCJKjp-ExtraLight` — the one CJK-coverage font — is present on BOTH builds,
identically (no subset-tag-stripped difference). Neither symmetric-difference entry introduces a
NEW font FAMILY: `DejaVuSansMono-Oblique` (head-only) is an additional STYLE VARIANT of the
`DejaVuSansMono` family already embedded on both sides (plausibly from newly-italicized
monospace-styled content, e.g. an optional-parameter or type-hint run, among this milestone's
signature-typography changes); `LibertinusSerif-Semibold-Identity-H` (main-only) is a serif WEIGHT
variant that is no longer emitted on HEAD (consistent with SIG typography changing which
class/style weight some previously-semibold serif text now uses). **Neither disappearing nor
appearing font is the CJK-coverage font, and no new non-CJK monospace FAMILY (as opposed to an
existing family's style variant) appears only on HEAD** — the specific failure signature Pitfall 6
warns about (a brand-new monospace family shadowing the CJK fallback) is not observed. This is a
necessary-but-not-sufficient finding in the same sense as Check 2: font-set matching does NOT by
itself prove no glyph was rendered from the wrong font at the GLYPH level within an existing font
resource (D-16 explicitly rejects treating a matching `/BaseFont` set as a substitute for the
owner's visual look).

---

## Check 4 — Owner Visual Confirmation

**status: MET — see `41-JA-GLYPHBAR-SIGNOFF.md` for the owner's verbatim answer and grounds.**

Both mechanical checks (1-3) show no failure signature: page count unchanged, CJK text total
essentially unchanged (no drop), and the one CJK-coverage font (`NotoSerifCJKjp-ExtraLight`)
present identically on both sides. **None of this substitutes for the owner's visual look (D-16)**
— Typst's font fallback is silent, and a substituted glyph very often still extracts as the
correct character even when it visually renders wrong.

### Pages to inspect (same absolute page numbers on both PDFs — page counts are identical at 94)

| Page (1-indexed) | Why selected | What to look for |
|---|---|---|
| 1 | Title page | Confirm each PDF's own version string (`0.6.5` before / `0.7.0` after) and that the title page itself renders without garbled characters |
| 5 | Single highest CJK-density page overall (both builds, density 400) | The page with the heaviest concentration of Japanese prose in the whole document — the highest-leverage page for spotting any substituted/missing glyph in body text |
| 32 | Highest-density page in the document's 2nd third (both builds, density 127); also the "12 API Reference" section-opening page | Transition point between prose-heavy and signature-heavy content |
| 33 | The first `raw()`-styled API signature content (`class typsphinx.builder.TypstBuilder(app, env)`), located by searching the extracted text (restricted to the API Reference section, page ≥32) for a fully-qualified dotted signature pattern | Japanese text sitting directly adjacent to/inside monospace-styled signature runs — the specific exposure the 24 new `raw(` call sites create |
| 63 (head) | Highest-density page in the document's 3rd third on the "after" build (density 60) | Japanese prose inside the "Writer and Translator" API section on HEAD's reflowed layout |
| 74 (main) | Highest-density page in the document's 3rd third on the "before" build (density 60) | The corresponding section on the "before" build, at the page where main's own reflow placed its 3rd-third density peak |

**Absolute PDF paths for the owner's side-by-side comparison:**
- Before (`main`): `/tmp/p41-main-out/typsphinx.pdf` (SHA-256 `495ced3ea21651c3301d6d4eda819ebf35a2f1c7c66b80d704cdb7115df27187`)
- After (HEAD): `/tmp/p41-head-out/typsphinx.pdf` (SHA-256 `b64cf3563c04be2052eede5a629250a7c829db1118fdf44a82804746494f605f`)

Owner's verdict and verbatim words are recorded in `41-JA-GLYPHBAR-SIGNOFF.md`.

---

## What These Checks Cannot Prove

Typst's font fallback is silent: it emits no warning and no error when a character is rendered
from a substituting font that lacks proper coverage for that glyph. A substituted CJK glyph very
often STILL extracts as the correct Unicode character in `pypdf`'s text layer — the codepoint in
the PDF's content stream is unaffected by which font was used to draw it. This means:

- Check 1 (page count matching) says nothing about whether individual glyphs rendered correctly —
  it only rules out gross reflow differences.
- Check 2 (CJK character count matching, no drop) says nothing about whether the counted
  characters are drawn in a font with real CJK glyph outlines versus a fallback/notdef box — a
  page could have its full expected CJK character COUNT while still rendering every one of them
  as a missing-glyph box.
- Check 3 (font-set matching) says nothing about which SPECIFIC glyphs on a page were drawn using
  which SPECIFIC embedded font — two PDFs could share an identical `/BaseFont` set while one of
  them still routes some Japanese text through a font in that set that has no CJK outlines for
  those particular codepoints.

**Checks 1-3 passing does not close the question.** This is exactly why check 4 — the owner's own
eyes on the rendered pages — is a Phase 41 close condition (D-16), and why no automated
glyph-coverage score, per-page image diff, or font-similarity metric is offered anywhere in this
file as a stand-in for that look.

## Commands Not Run

None. All checks specified by this plan (page count, CJK density, font enumeration, and the
provenance/freshness/import checks) were run against both real, freshly-built PDFs. Check 4 (owner
visual confirmation) was not a check this file could discharge itself — it is recorded in full in
`41-JA-GLYPHBAR-SIGNOFF.md`, MET on the owner's verbatim "approved".
