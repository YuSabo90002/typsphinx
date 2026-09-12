# Phase 69 Plan 01 — CHANGELOG Evidence

Measured shape: executor worktree, Phase 64 shims inherited from the session PATH; no `nix
develop`, no `direnv exec`, never the main checkout.

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T22:32:19Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a

$ test -f .git; echo "exit:$?"
exit:0

$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

Provisioning:

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.58ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a
Prepared 1 package in 456ms
Installed 90 packages in 53ms
 ... (90 packages, including tox-uv==1.36.0, tox-uv-bare==1.36.0, uv==0.12.13, myst-parser==5.1.0,
      furo==2025.12.19, sphinx-intl==2.3.2, sphinx-autodoc-typehints==3.0.1)
```

Both extras synced without error.

```
BASE_69_01 = 2db4e803d36d5f7a5db0a92b08cac4988fa88957

$ cat .venv/pyvenv.cfg
home = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
implementation = CPython
uv = 0.11.25
version_info = 3.14
include-system-site-packages = false
prompt = typsphinx
```

PYVENV_HOME_69_01 = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_69_01 = 3.14

## Pre-edit measurements

Taken before touching `CHANGELOG.md`.

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
0
```
UNRELEASED_BOLD_BEFORE = 0

```
$ grep -c '0\.9\.3' CHANGELOG.md
0
```
V093_BEFORE = 0

```
$ awk '/^### Planned for Future Releases$/{f=1} /^## \[0\.9\.2\]/{exit} f' CHANGELOG.md | sha256sum
a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02  -
```
PLANNED_SHA_BEFORE = a3436143cc65050f0aa709bbdc02b8fa31ab6d8f58c2c4aa198cbc10e0911f02

Verbatim final line:
```
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```

All five pre-edit measurements match the planning-time census in `69-01-PLAN.md`'s planning-time
table (23 release headings, 23 link-reference lines, 0 real change bullets under
`## [Unreleased]`, 0 hits for `0.9.3`, and the tail line ending `v0.9.2...HEAD`) — confirming
D-03's premise that this is authoring from scratch, not promotion.

## What this file is NOT

`scripts/extract_changelog_section.py` is deliberately NOT invoked in this phase. There is no
versioned `## [0.9.3]` (or any other new) section for it to extract — SC#2 and D-03 keep this
milestone's bullets under `## [Unreleased]`, unpromoted. D-11 records that the next release-prep
phase runs the extractor and promotes these bullets into a versioned section when it closes,
exactly as Phase 61's `## [Unreleased]` bullets were promoted by Phase 63.

## Docs baseline — pre-edit, clean builds

Both baselines were taken BEFORE touching `CHANGELOG.md`, each preceded by `rm -rf docs/_build`
so the count reflects a full rebuild, not an incremental one.

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-html
```

Verbatim tail:
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.46=setup[0.10]+cmd[3.37] seconds)
  congratulations :) (3.49 seconds)
```

`WARNING` lines (all four are the pre-existing `visit_toctree` docstring rendering, unrelated to
`CHANGELOG.md`):
```
22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
445:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

DOCS_HTML_WARN_BASE = 3

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-pdf
```

Verbatim tail:
```
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (3.82=setup[0.10]+cmd[3.72] seconds)
  congratulations :) (3.84 seconds)
```

`WARNING` lines (the same four docstring warnings, plus two `doctest_block` unknown-node-type
warnings pre-existing in the PDF builder path):
```
22::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
44::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
418::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
445:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
456:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
462:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

DOCS_PDF_WARN_BASE = 5

```
$ head -c 5 docs/_build/pdf/typsphinx.pdf
%PDF-
```

Both counts (3 / 5) match the historical cross-check cited in the plan's planning-time census
(Phase 61 and Phase 63 closes). An incremental rebuild under-reports warnings, which is why both
counted builds start from an empty `docs/_build`.

## The TOX bullet (tracer slice)

Inserted immediately below `## [Unreleased]`, one blank line on each side of the new `### Changed`
heading, above the existing `### Planned for Future Releases` (left untouched):

```markdown
### Changed

- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
  dispatched against the branch carrying this change was green across the Linux, Windows and
  macOS test lanes.
```

No lead paragraph and no `### Verified` subsection were written (D-04). `tox-uv-bare` is named
only as the previous state — this bullet is a dated record, not one of the toolchain-pin sync
points `CLAUDE.md` lists, so no other file changes with it.

## Accuracy basis

| Claim in the TOX bullet | Evidence file / section |
|---|---|
| `dev` extra and `tox.ini`'s `requires` line name `tox-uv` again, in place of `tox-uv-bare` | `65-REVERT-EVIDENCE.md` § "TOX-01 lock regeneration" (the one-token pin swap in both files) |
| `uv.lock` regenerated in the same change | `65-REVERT-EVIDENCE.md` § "TOX-01 lock regeneration" (`uv lock` output: `Added tox-uv v1.36.0` / `Updated tox-uv-bare v1.35.2 -> v1.36.0` / `Added uv v0.12.13`) and § "Revert commit" (all four files — `pyproject.toml`, `tox.ini`, `uv.lock`, `tests/test_toolchain_config_gate.py` — landed in one commit) |
| No effect on installing or using typsphinx | This is a `dev`-extra / tox-runner change only; `typsphinx`'s own runtime dependencies are untouched by either file (`65-REVERT-EVIDENCE.md`'s diff touches only the `dev` extra line and the tox requires line) |
| CI run dispatched against the branch was green across Linux, Windows and macOS | `65-CI-EVIDENCE.md` § "Job census" (all twelve jobs `success`), § "windows-latest lanes" and § "macos-latest lanes" (both OS's two Python lanes each `success`), run `34681968010`, conclusion `success` |

## Docs render — tracer slice

Command:
```
$ rm -rf docs/_build && uv run tox -e docs-html
```

Verbatim tail:
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (2.41=setup[0.01]+cmd[2.40] seconds)
  congratulations :) (2.43 seconds)
```

`WARNING` lines (identical set to the baseline, only the docstring line-numbers within the
CHANGELOG-including `changelog` page's own upstream file shifted by the 8-line insertion — no new
warning, no warning naming the `changelog` page):
```
21::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
43::21: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
417::6: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
444:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab4c25ec1378d6a2a/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

DOCS_HTML_WARN_TRACER = 3

`DOCS_HTML_WARN_TRACER` (3) equals `DOCS_HTML_WARN_BASE` (3), and the set of `WARNING` lines is
the same four pre-existing `visit_toctree` docstring warnings — none names the `changelog` page.
The TOX bullet's MyST renders through `docs/source/changelog.rst`'s
`.. include:: ../../CHANGELOG.md` with `:parser: myst_parser.sphinx_` without introducing any new
warning.

## Pure-addition check (Task 1 slice)

```
$ git diff BASE_69_01 -- CHANGELOG.md
```

Verbatim output:
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5d8266cd..02661407 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,14 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Changed
+
+- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
+  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
+  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
+  dispatched against the branch carrying this change was green across the Linux, Windows and
+  macOS test lanes.
+
 ### Planned for Future Releases
 - BibTeX/bibliography support
 - Glossary generation
```

Zero lines in this diff begin with a single `-` followed by a non-`-` character — no source line
was removed. `### Planned for Future Releases` and every historical release section survive
byte-identical, and the tail link-reference block is untouched (confirmed above:
`PLANNED_SHA_BEFORE` recorded before this edit; re-confirmed equal in Task 2's evidence after the
remaining two bullets land).

This evidence file continues in Task 2 with the DEP and NIX bullets, the full pure-addition proof
over both tasks' combined diff, the fence assertions, and both docs environments rebuilt clean a
final time against this baseline.
