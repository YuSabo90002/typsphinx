# Phase 74 — Base Evidence (PHASE_BASE_SHA, base build, QUA-14 census)

PHASE_BASE_SHA = 8ea10273265e3966b6e650bad43cf90c9598ed65
MILESTONE_BASE = 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b
SCRATCH_74_01 = /tmp/tmp.JkJbjLa7hI
PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
SPHINX_VERSION = 9.1.0
DOCUTILS_VERSION = 0.22.4
TYPST_PY_VERSION = 0.15.0
AUTODOC_TYPEHINTS_VERSION = 3.13.6
MYST_PARSER_VERSION = 5.1.0
BASE_TRANSLATOR_DOCTEST_MENTIONS = 0
BASE_WARNING_COUNT = 5
BASE_DOCTEST_UNKNOWN_COUNT = 2
BASE_API_COLLAPSED_RUNS = 2
BASE_API_EXAMPLE_LINE = 811
BASE_API_PYTHON_FENCES = 0
BASE_API_TERMS_ITEM_COUNT = 0

## Head check and provisioning

- `date -u +%FT%TZ` -> `2026-09-19T22:04:18Z`
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf` (under
  `/home/yuta/Documents/typsphinx/.claude/worktrees/`)
- `test -f .git; echo "exit:$?"` -> `exit:0` (worktree confirmed — `.git` is a file)
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`

Provisioning line (`<worktree_provisioning>`, `CLAUDE.md` § "Worktree-isolated execution" plus the
`--extra docs --python 3.13.13` additions):

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```

Exit status: `0`. `typsphinx==0.9.2` installed editable from this worktree's own checkout path,
`sphinx==9.1.0`, `sphinx-autodoc-typehints==3.13.6`, `myst-parser==5.1.0` all resolved.

- `sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg` ->
  `PYVENV_HOME` = `/nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin`,
  `PYVENV_VERSION_INFO` = `3.13.13` — same interpreter version as the main checkout and
  74-RESEARCH.md's own measurements.
- `uv run python -c "..."` (importlib.metadata.version) ->
  `SPHINX_VERSION` = `9.1.0`, `DOCUTILS_VERSION` = `0.22.4`, `TYPST_PY_VERSION` = `0.15.0`,
  `AUTODOC_TYPEHINTS_VERSION` = `3.13.6`, `MYST_PARSER_VERSION` = `5.1.0`.
- `printenv SPHINX_LANGUAGE READTHEDOCS_LANGUAGE; echo "exit:$?"` -> printed nothing but `exit:1`.
  Neither variable is set; the docs language is not overridden.
- Before any commit: `PHASE_BASE_SHA` = `git rev-parse HEAD` =
  `8ea10273265e3966b6e650bad43cf90c9598ed65`. `SCRATCH_74_01` = `mktemp -d` =
  `/tmp/tmp.JkJbjLa7hI`.

## Base identity

- `MILESTONE_BASE` = `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b`.
- `git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b 8ea10273265e3966b6e650bad43cf90c9598ed65 -- . ':(exclude).planning'`
  printed nothing. `PHASE_BASE_SHA`'s product tree outside `.planning/` equals the milestone base.
- `grep -c doctest typsphinx/translator.py || true` -> `0`, recorded as
  `BASE_TRANSLATOR_DOCTEST_MENTIONS`. No `doctest_block` handler exists on the base, as expected.

## Base Typst build

### Build command

```
rm -rf "$S/base-typst"
LANG=C LC_ALL=C uv run python -m sphinx -b typst docs/source "$S/base-typst" > "$S/p7401_base-typst.log" 2>&1
```

Run from this worktree's root, with `$S` = `SCRATCH_74_01` (`/tmp/tmp.JkJbjLa7hI`). No `-q` flag.
`echo "exit:$?"` -> `exit:0`.

The English summary line, `LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7401_base-typst.log"`,
verbatim:

```
build succeeded, 5 warnings.
```

`BASE_WARNING_COUNT` = `5`, the integer in `build succeeded, 5 warnings.`.

### Counted warnings

Every `WARNING:`/`ERROR:` line of the log, verbatim (`LANG=C LC_ALL=C grep -nE 'ERROR:|WARNING:' "$S/p7401_base-typst.log"`):

```
33:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
34:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
35:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:21: ERROR: Unexpected indentation. [docutils]
40:writing output... [api/index]WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
46:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

### Doctest block warnings

`BASE_DOCTEST_UNKNOWN_COUNT` = `2`
(`LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$S/p7401_base-typst.log" | wc -l`).

Each such warning's first line (`grep -n 'unknown node type: .doctest_block' "$S/p7401_base-typst.log"`), verbatim:

```
40:writing output... [api/index]WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
46:WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_template_import_path("typst", "base.typ")
```

**Positive control (constraints 4 and 5):** `BASE_DOCTEST_UNKNOWN_COUNT` (`2`) is at least 1, and the
English `build succeeded` line is present. Positive control passes.

### api/index.typ example region

Using `$S/base-typst/api/index.typ`:

- `BASE_API_COLLAPSED_RUNS` = `2` (`grep -c 'text(">>> ' "$S/base-typst/api/index.typ"`), at least 1.
- `BASE_API_EXAMPLE_LINE` = `811`, the line containing
  `text(">>> compute_content_include_path("`.

`grep -n -B3 'text(">>> ' "$S/base-typst/api/index.typ"` verbatim:

```
808-
809-strong({text("Examples")})
810-linebreak()
811:text(">>> compute_content_include_path(\"\", \"index.typ\") 'index.typ' >>> compute_content_include_path(\"manuals\", \"guide/index.typ\") '../guide/index.typ' >>> compute_content_include_path(\"guide\", \"guide/index.typ\") 'index.typ'")})
--
864-
865-strong({text("Examples")})
866-linebreak()
867:text(">>> compute_template_import_path(\"typst\", \"base.typ\") '/_template/typst/base.typ' >>> compute_template_import_path(\"report\", \"custom.typ\") '/_template/report/custom.typ'")})
```

This is the verbatim collapsed region SC1 names: the three prompts, their continuations and their
outputs on one physical `.typ` line each.

- `BASE_API_PYTHON_FENCES` = `0` (count of lines exactly three backticks followed by `python`, via
  `grep -cx`, or 0). No fenced code blocks exist yet — the base collapses doctest examples to
  `text("...")` runs, not fences.
- `BASE_API_TERMS_ITEM_COUNT` = `0` (`grep -c 'terms\.item' "$S/base-typst/api/index.typ" || true`).
  This confirms the D-06 amendment's measurement: this project's own `api/index.typ` carries no
  `terms.item(...)` doctest shape at the base. Recorded as context; it gates nothing here.
