# Phase 73 — CHANGELOG Evidence (D-01..D-05, D-14, SC#2)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-16T09:53:50Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af4a9f698bf799c4a

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
...
 + typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-af4a9f698bf799c4a)
 + typst==0.15.0
 + uv==0.12.13
 + virtualenv==21.5.1
```
(90 packages installed, including tox-uv==1.36.0, tox-uv-bare==1.36.0, sphinx==9.1.0,
sphinx-autodoc-typehints==3.0.1, myst-parser is bundled by the `docs` extra chain via furo/sphinx)

Before any commit:

BASE_73_01 = c6bc641aa1745e6413b4f33c4d0c572a962da430

`.venv/pyvenv.cfg`:
```
home = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
implementation = CPython
uv = 0.11.25
version_info = 3.13.13
include-system-site-packages = false
prompt = typsphinx
```

PYVENV_HOME_73_01 = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_73_01 = 3.13.13
SCRATCH_73_01 = /tmp/tmp.2asMC1a3EM

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
4
```
UNRELEASED_BOLD_BEFORE = 4

```
$ grep -cE '0\.9\.[345]' CHANGELOG.md
0
```
VERSION_LITERALS_BEFORE = 0

```
$ awk '/^### Changed$/{f=1;print;next} f && /^### /{exit} f' CHANGELOG.md | sha256sum
cf0e3e029ee4ea3d6f7df10c312f13ecddd09cd2d62854c526c1190c509dc970  -
```
CHANGED_SHA_BEFORE = cf0e3e029ee4ea3d6f7df10c312f13ecddd09cd2d62854c526c1190c509dc970

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
exists yet for it to extract from — both new bullets land under the existing `## [Unreleased]`
heading, not under a new `## [X.Y.Z]` heading. This phase writes no `### Verified` subsection and
no lead paragraph under `## [Unreleased]`, no versioned heading and no tail link (D-05). The next
release-prep phase promotes all six bullets currently under `## [Unreleased]` (the four carried
from v0.9.3/v0.9.4 plus this plan's own two) into its versioned section when that milestone scopes
a release (D-11).

## Docs baseline — pre-edit, clean builds

`rm -rf docs/_build`, then `LANG=C LC_ALL=C uv run tox -e docs-html` in the foreground, on the
pre-edit tree, logged to `p7301_html-base.log`:

```
$ rm -rf docs/_build && LANG=C LC_ALL=C uv run tox -e docs-html
Running Sphinx v9.1.0
```

~~~text docs-html-base-warnings
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af4a9f698bf799c4a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
~~~

```
build succeeded, 3 warnings.
```
DOCS_HTML_WARN_BASE = 3
MULTI_TOCTREE_HTML_BASE = 0

Repeated for `docs-pdf`, again with `rm -rf docs/_build` immediately before it, logged to
`p7301_pdf-base.log`:

~~~text docs-pdf-base-warnings
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af4a9f698bf799c4a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
~~~

```
build succeeded, 5 warnings.
```
DOCS_PDF_WARN_BASE = 5
MULTI_TOCTREE_PDF_BASE = 0

`head -c 5` of the copied PDF (`p7301_base.pdf`):
```
%PDF-
```
PDF_MAGIC_BASE = %PDF-

**Positive control.**
```
$ grep -n 'BASE_MULTI_TOCTREE_COUNT' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-BASE-EVIDENCE.md
15:BASE_MULTI_TOCTREE_COUNT = 5
```
MULTI_TOCTREE_POSITIVE_CONTROL_72 = 5

The same `LANG=C LC_ALL=C grep -c 'document is referenced in multiple toctrees'` found 5 such
messages on Phase 72's pre-fix base, so a zero here is a real absence produced by DOC-18's fix
carrying through to this phase base, not a localised or broken grep. The English `build succeeded,
N warnings.` line found by the same C-locale grep in both of this plan's logs proves the console
text on this run is English, exactly as Phase 72's log was.

Neither base multiple-toctrees count is non-zero, so no `## HALT` is written here.

An incremental rebuild under-reports warnings, which is why each counted build starts from an
empty `docs/_build`.

## The two subsections (tracer slice)

Inserted as two pure insertions into the `## [Unreleased]` region: `### Added` right before the
existing `### Changed` heading (after the blank line that follows `## [Unreleased]`), and
`### Fixed` right before `### Planned for Future Releases` (after the blank line ending the last
`### Changed` bullet). Nothing else in the file changed at this step.

Bullets as landed:

```markdown
### Added

- **A `tox -e linkcheck` environment checks the documentation's external links, including
  their `#anchor` targets (QUA-13, DOC-24).** It runs Sphinx's link-check builder over the
  documentation sources; because it needs the network, it is not part of a plain `tox` run,
  and it is contributor tooling, listed alongside `docs-html` and `docs-pdf`. This has no
  effect on installing or using typsphinx.
```

```markdown
### Fixed

- **The HTML documentation's sidebar now lists each User Guide and Examples page exactly
  once, nested under its section (DOC-18).** Previously each of those pages was also listed
  a second time beside its section, so Sphinx no longer reports them as referenced in
  multiple toctrees. This has no effect on installing or using typsphinx.
```

Both lead sentences carry a verb ("checks", "now lists") rather than a bare noun phrase, matching
the register of the four `### Changed` bullets and avoiding the Phase 69 house-style defect
(bare-noun-phrase bold lead, `71-CHANGELOG-EVIDENCE.md` § "Discretion exercised").

## Accuracy basis

| Claim in a new bullet | Evidence file and section |
|---|---|
| The `linkcheck` environment exists, runs the linkcheck builder over `docs/source`, and is not in `env_list` (so it is not part of a plain `tox` run) | `72-LINKCHECK-EVIDENCE.md` § "tox.ini diff" |
| It checks external links including `#anchor` targets, and it needs the network | `72-LINKCHECK-EVIDENCE.md` § "Run 1"; `tox.ini`'s own `linkcheck` environment description |
| It is listed beside `docs-html` and `docs-pdf` in the contributor notes | `72-DOC24-EVIDENCE.md` § "Surfaces" |
| Each User Guide and Examples page appears once in the sidebar, under its section | `72-TOCTREE-EVIDENCE.md` § "Sidebar" |
| No multiple-toctrees report | `72-TOCTREE-EVIDENCE.md` § "SC#3 verdict" |
| Each page still reaches the PDF exactly once | `72-TOCTREE-EVIDENCE.md` § "Typst pair" |

## Docs render — tracer slice

`rm -rf docs/_build`, then `LANG=C LC_ALL=C uv run tox -e docs-html` in the foreground, on the
post-edit tree, logged to `p7301_html-tracer.log`:

~~~text docs-html-tracer-warnings
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
:6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af4a9f698bf799c4a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
~~~

```
build succeeded, 3 warnings.
```
DOCS_HTML_WARN_TRACER = 3
MULTI_TOCTREE_HTML_TRACER = 0

`DOCS_HTML_WARN_TRACER` equals `DOCS_HTML_WARN_BASE` (3 = 3), and the set of `WARNING` message
lines is identical between the base and tracer builds. The rendered `changelog.html` page includes
both new bullets' text verbatim (confirmed by grepping the built HTML for "link-check builder"
and "sidebar now lists each User Guide"), and no new warning names the changelog page or any
other page — the halt rule of this step does not fire.
