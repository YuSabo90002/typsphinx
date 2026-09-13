# Phase 71 — CHANGELOG Evidence (D-01..D-04, SC#2)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-13T08:27:54Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1002cdd91840430e

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning line and its tail:
```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
Using CPython 3.13.13 interpreter at: /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin/python3.13
Creating virtual environment at: .venv
Resolved 91 packages in 0.63ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1002cdd91840430e
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1002cdd91840430e
Prepared 1 package in 474ms
Installed 90 packages in 56ms
 + ... (90 packages, including tox-uv==1.36.0, tox-uv-bare==1.36.0, uv==0.12.13, myst-parser==5.1.0,
       furo==2025.12.19, sphinx-intl==2.4.0, sphinx-autodoc-typehints==3.0.1)
```

Before any commit:

BASE_71_01 = f1f7d54a61d74c3972f1df0508ac994c001dda7e

`.venv/pyvenv.cfg`:
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

PYVENV_HOME_71_01 = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_71_01 = 3.13.13
SCRATCH_71_01 = /tmp/tmp.tTox2TTxsS

## Pre-edit measurements

```
$ grep -cE '^## \[' CHANGELOG.md
23
```
HEADINGS_BEFORE = 23

```
$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
23
```
LINKREFS_BEFORE = 23

```
$ awk '/^## \[0\.9\.2\]/{exit} f; /^## \[Unreleased\]/{f=1}' CHANGELOG.md | grep -cE '^- \*\*'
3
```
UNRELEASED_BOLD_BEFORE = 3

```
$ grep -cE '0\.9\.[34]' CHANGELOG.md
0
```
VERSION_LITERALS_BEFORE = 0

```
$ awk '/^### Planned for Future Releases$/{f=1} /^## \[0\.9\.2\]/{exit} f' CHANGELOG.md | sha256sum
a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02  -
```
PLANNED_SHA_BEFORE = a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02

Verbatim `tail -n 1 CHANGELOG.md` (pre-edit):
```
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```

## What this file is NOT

`scripts/extract_changelog_section.py` is not run in this plan, because no versioned section
exists yet for it to extract from — the new bullet lands under the existing `## [Unreleased]`
heading, not under a new `## [X.Y.Z]` heading. This phase writes no `### Verified` subsection and
no lead paragraph under `## [Unreleased]` (D-04, following Phase 69's own D-04). The next
release-prep phase promotes all four bullets currently under `## [Unreleased]` (the three from
v0.9.3 plus this plan's own) into its versioned section when that milestone scopes a release
(D-08).

## Phase 70 figures the bullet cites

```
$ grep -n '^CORPUS_PROJECT_COUNT = ' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-CORPUS-DOCS-BASE-EVIDENCE.md
45:CORPUS_PROJECT_COUNT = 167
```

```
$ grep -n '^LEG_D_VERDICT = ' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-RUNTIME-EVIDENCE.md
360:LEG_D_VERDICT = MET
```

```
$ grep -n '^CORPUS_MANIFEST_SHA256_AFTER = ' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-AFTER-RUNTIME-EVIDENCE.md
174:CORPUS_MANIFEST_SHA256_AFTER = 4c87a31da016b85f260915f6a0690c3fcf1602f17a0e2aa6a21725846d07464d
```

```
$ grep -n 'map_parameters' .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOCS-DIFF-EVIDENCE.md
515:| H-018 | html | _modules/typsphinx/template_engine.html | 766,3 | sphinx_metadata: Dict[str, Any]; typst_elements: Dict[str, Any] \| None; -> Dict[str, Any]: | sphinx_metadata: dict[str, Any]; typst_elements: dict[str, Any] \| None; -> dict[str, Any]: | typsphinx/template_engine.py:468-470 (`map_parameters` params/return) | TRACED |
553:| H-056 | html | api/index.html | 5371 | typing.Dict[str, Any] (sphinx_metadata) | stdtypes.dict[str, Any] | typsphinx/template_engine.py:468 (`map_parameters` param); docstring template_engine.py:475 | TRACED |
554:| H-057 | html | api/index.html | 5373 | typing.Optional[typing.Dict[str, Any]] (typst_elements) | stdtypes.dict[str, Any] \| None | typsphinx/template_engine.py:469 (`map_parameters` param); docstring template_engine.py:477 (Pitfall 9 shape change: Optional[Dict[str,Any]] -> dict[str,Any] \| None) | TRACED |
555:| H-058 | html | api/index.html | 5384 | typing.Dict[str, Any] (return type) | stdtypes.dict[str, Any] | typsphinx/template_engine.py:470 (`map_parameters` return, same function as two rows above) | TRACED |
556:| H-059 | html | api/index.html | 5401,2 | typing.Dict[str, Any] (sphinx_metadata); typing.Dict[str,Any]\|None (typst_elements) [2nd compact rendering] | stdtypes.dict[str, Any]; stdtypes.dict[str,Any]\|None | typsphinx/template_engine.py:468-469 (`map_parameters`, second/compact field-list rendering of the same params) | TRACED |
557:| H-060 | html | api/index.html | 5406 | typing.Dict[str, Any] (return type) [2nd compact rendering] | stdtypes.dict[str, Any] | typsphinx/template_engine.py:470 (`map_parameters` return, second/compact rendering) | TRACED |
572:| H-075 | typ | api/index.typ | 5858 | typing.Dict link (sphinx_metadata, map_parameters 1st rendering) | stdtypes.dict link | typsphinx/template_engine.py:468 (`map_parameters` param); docstring template_engine.py:475 | TRACED |
573:| H-076 | typ | api/index.typ | 5872,3 | typing.Optional[typing.Dict[... (typst_elements, part 1) | stdtypes.dict[... (typst_elements, part 1) | typsphinx/template_engine.py:469 (`map_parameters` param) (Pitfall 9 shape change, part 1 of 2) | TRACED |
574:| H-077 | typ | api/index.typ | 5879 | text("]]") (typst_elements, part 2) | text("] \| ") + link(None) (typst_elements, part 2) | typsphinx/template_engine.py:469 (`map_parameters` param, continuation of previous row) (Pitfall 9 shape change, part 2 of 2) | TRACED |
575:| H-078 | typ | api/index.typ | 5899 | typing.Dict link (return type, map_parameters 1st rendering) | stdtypes.dict link | typsphinx/template_engine.py:470 (`map_parameters` return) | TRACED |
576:| H-079 | typ | api/index.typ | 5917 | typing.Dict link (sphinx_metadata, map_parameters 2nd rendering) | stdtypes.dict link | typsphinx/template_engine.py:468 (`map_parameters` param, second/compact rendering) | TRACED |
577:| H-080 | typ | api/index.typ | 5929 | typing.Dict link (typst_elements, map_parameters 2nd rendering) | stdtypes.dict link | typsphinx/template_engine.py:469 (`map_parameters` param, second/compact rendering) | TRACED |
578:| H-081 | typ | api/index.typ | 5942 | typing.Dict link (return type, map_parameters 2nd rendering) | stdtypes.dict link | typsphinx/template_engine.py:470 (`map_parameters` return, second/compact rendering) | TRACED |
```

CORPUS_PROJECT_COUNT_70 = 167
LEG_D_VERDICT_70 = MET

Under D-03, the bullet's only number (167) is transcribed from this section, not from this plan's
own census and not from RESEARCH.md.

## Docs baseline — pre-edit, clean builds

`rm -rf docs/_build`, then `LC_ALL=C uv run tox -e docs-html`, in the foreground, on the pre-edit
tree:

~~~text docs-html-base-warnings
22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1002cdd91840430e/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
~~~

~~~text docs-html-base-log-tail
モジュールコードをハイライトしています...[100%] typsphinx.writer

追加のページを出力中... search 完了
English (code: en) の検索インデックスを出力... 完了
オブジェクト インベントリを出力... 完了
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (4.01=setup[0.10]+cmd[3.91] seconds)
  congratulations :) (4.04 seconds)
~~~

DOCS_HTML_WARN_BASE = 3

Repeated for `docs-pdf`, again with `rm -rf docs/_build` immediately before it:

~~~text docs-pdf-base-warnings
22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1002cdd91840430e/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
'index.typ'
>>> compute_content_include_path("manuals", "guide/index.typ")
'../guide/index.typ'
>>> compute_content_include_path("guide", "guide/index.typ")
'index.typ'</doctest_block>
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
'/_template/typst/base.typ'
>>> compute_template_import_path("report", "custom.typ")
'/_template/report/custom.typ'</doctest_block>
~~~

~~~text docs-pdf-base-log-tail
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1002cdd91840430e/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.21=setup[0.09]+cmd[4.12] seconds)
  congratulations :) (4.23 seconds)
~~~

DOCS_PDF_WARN_BASE = 5

`head -c 5 docs/_build/pdf/typsphinx.pdf`:
```
%PDF-
```

An incremental rebuild under-reports warnings, which is why each counted build starts from an
empty `docs/_build`.

## The bullet (tracer slice)

Inserted after the last line of the `flake.nix` bullet, one blank line, then the new bullet. The
blank line that already preceded `### Planned for Future Releases` stays the single separator
after the new bullet (edge: adjacency). Nothing else in the file changed (D-04).

Bullet as landed:

```markdown
- **Type annotations in typsphinx's source now use builtin generics (QUA-09, QUA-11, QUA-12,
  DOC-22, DOC-23).** `typsphinx/` and `tests/` moved off the `typing` aliases `Dict`, `List`,
  `Set` and `Tuple` onto the builtin `dict`, `list`, `set` and `tuple`, with `Iterator` now
  imported from `collections.abc` instead; the linter now enforces this style, and the
  contributor notes in `CLAUDE.md` describe it. The visible effect is in the API reference: it
  now shows, for example, `dict[str, Any]` where it showed `Dict[str, Any]`. This has no effect
  on installing or using typsphinx. The Typst output typsphinx generates and its runtime
  behaviour are unchanged: the `.typ` output is byte-identical across the test-fixture corpus of
  167 projects.
```

The lead sentence carries a verb ("...now use builtin generics...") rather than a bare noun
phrase, matching the `tox-uv` bullet's shape and avoiding the `69-REVIEW.md` WR-01 defect. The
sole evidence sentence cites `167`, transcribed live from `CORPUS_PROJECT_COUNT_70` above. No
version number, no Japanese-site wording, no pytest/mypy figures, no QUA-12 leg enumeration.

## Accuracy basis

| Claim in the bullet | Evidence file and section |
|---|---|
| Converted annotations (`typing` aliases -> builtin generics, `Iterator` from `collections.abc`) | `70-AFTER-STATIC-EVIDENCE.md` § "Changed-file set" and § "Leg (a) — every converted file" |
| The linter now enforces this style | `70-FLIP-EVIDENCE.md` |
| The contributor notes in `CLAUDE.md` describe it | `70-DOC22-EVIDENCE.md` |
| The API-reference example `Dict[str, Any]` -> `dict[str, Any]` | `70-DOCS-DIFF-EVIDENCE.md` row H-018 |
| Output and runtime behaviour unchanged, byte-identical across 167 projects | `70-AFTER-RUNTIME-EVIDENCE.md` § "Post-flip manifest" (`LEG_D_VERDICT = MET`) and § "Leg (b) — pytest after"; `70-CORPUS-DOCS-BASE-EVIDENCE.md` (`CORPUS_PROJECT_COUNT = 167`) |

Why "byte-identical" rather than "every project compiles": the leg (d) manifest includes 21
projects whose non-zero exit is by design (error-path fixtures), identical on both sides of the
conversion — so "every project compiles" would be false, while "byte-identical" (comparing the
manifest, including those same non-zero-exit projects on both sides) is the claim the evidence
actually supports.

## Docs render — tracer slice

`rm -rf docs/_build`, then `LC_ALL=C uv run tox -e docs-html` in the foreground, on the post-edit
tree:

~~~text docs-html-tracer-warnings
21::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
43::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
417::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a1002cdd91840430e/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
~~~

~~~text docs-html-tracer-log-tail
モジュールコードをハイライトしています...[100%] typsphinx.writer

追加のページを出力中... search 完了
English (code: en) の検索インデックスを出力... 完了
オブジェクト インベントリを出力... 完了
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (2.88=setup[0.01]+cmd[2.87] seconds)
  congratulations :) (2.90 seconds)
~~~

DOCS_HTML_WARN_TRACER = 3

`DOCS_HTML_WARN_TRACER` equals `DOCS_HTML_WARN_BASE` (3 = 3), and the set of `WARNING` message
lines is identical between the base and tracer builds (`diff` of the message text, ignoring log
line numbers, exit 0). The line-number shifts inside the raw log (22/44/418/445 -> 21/43/417/444)
are from the CHANGELOG.md-driven `changelog` page rebuild output length changing by one line
elsewhere in the log, not from a new or moved warning. No new warning names the changelog page or
any other page.
