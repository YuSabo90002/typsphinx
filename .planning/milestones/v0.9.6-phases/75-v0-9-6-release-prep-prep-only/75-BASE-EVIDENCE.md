# Phase 75 — Base Evidence (clean documentation ledger at the phase base)

This ledger is the number 75-04 compares the bumped tip against (ROADMAP constraints 4 and 5).
Taken at the unbumped tree — `pyproject.toml` still reads `version = "0.9.2"`.

## Head check and provisioning

- `date -u +%FT%TZ` -> `2026-09-20T08:37:10Z`
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac09f823902b6b804`
- `test -f .git; echo "exit:$?"` -> `exit:0`
- `command -v uv` -> `/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv`
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`
- `git rev-parse HEAD` (before this task's commit) -> `6dbe70242e0d67f6bdc28636724eca7be0b3de07`
- `SCRATCH_75_01` reused from Task 1: `/tmp/tmp.Ea8hUnFA4z`

Key lines:

```
BASE_75_02 = 6dbe70242e0d67f6bdc28636724eca7be0b3de07
```

## Base identity

`PHASE_BASE_SHA` (from `75-CLOSEOUT-GUARD.md`) = `526a21d352696cb65c570d07d75ef8c7e3aa96a1`.
`MILESTONE_BASE` (from `75-CLOSEOUT-GUARD.md`) = `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b`.

```
$ git show HEAD:pyproject.toml | grep -m1 '^version = '
version = "0.9.2"
```

This ledger is taken on the unbumped tree, confirmed.

## Base docs-html

```
$ rm -rf docs/_build
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html > "$S/p7501_html.log" 2>&1; echo "exit:$?"
exit:0
```

`docs/_build` — the whole output tree — was removed before the build, because an incremental
rebuild under-reports warnings and is how this project once manufactured a false baseline match.

Verbatim `build succeeded` line
(`LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7501_html.log"`):

```
build succeeded.
```

Exactly `build succeeded.` with no warning count, so `BASE_HTML_WARNINGS = 0`.

Attributed-message count in this log
(`LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$S/p7501_html.log"`):

```
0
```

Key lines:

```
BASE_HTML_EXIT = 0
BASE_HTML_WARNINGS = 0
BASE_HTML_DOCSTRING_REST = 0
```

## Base docs-pdf

```
$ rm -rf docs/_build
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-pdf > "$S/p7501_pdf.log" 2>&1; echo "exit:$?"
exit:0
```

`tox.ini`'s `docs-pdf` environment runs `sphinx-build -b typstpdf source _build/pdf` from `docs/`,
so this is the build carrying the translator's own node-handler messages.

Verbatim `build succeeded` line
(`LANG=C LC_ALL=C grep -E '^build succeeded' "$S/p7501_pdf.log"`):

```
build succeeded.
```

Exactly `build succeeded.` with no warning count, so `BASE_PDF_WARNINGS = 0`.

Key lines:

```
BASE_PDF_EXIT = 0
BASE_PDF_WARNINGS = 0
```

## Base message-class census

Against `$S/p7501_pdf.log` (`$L`) — the `-b typstpdf` run, the build the `doctest_block` message
originates in. All commands run `LANG=C LC_ALL=C`, `|| true` used where the count may be 0.

```
$ LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$L" | wc -l
0

$ LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$L" || true
0

$ LANG=C LC_ALL=C grep -cE 'Unexpected indentation|Block quote ends without a blank line' "$L" || true
0
```

Both message classes are expected to be 0 on this tree, since Phase 74 closed them (TRN-01, TRN-02,
QUA-14). They are — recorded here, falsified against the two positive controls below rather than
just asserted.

Key lines:

```
BASE_DOCTEST_UNKNOWN = 0
BASE_DOCSTRING_REST = 0
BASE_RAW_REST = 0
```

## Positive controls

Two, both required because a zero is otherwise unfalsifiable.

### Synthetic

`$S/p7501_control.txt` written with three lines: one carrying the literal
`unknown node type: <doctest_block ...>`, one carrying a
`.py:docstring of x.y:5: ERROR: Unexpected indentation.` shape, and one carrying a
`.py:docstring of x.y:6: WARNING: Block quote ends without a blank line` shape:

```
writing output... [api/index]WARNING: unknown node type: <doctest_block classes="doctest" xml:space="preserve">>>> compute_content_include_path("", "index.typ")
/home/example/fakepkg/module.py:docstring of fakepkg.module.x.y:5: ERROR: Unexpected indentation. [docutils]
/home/example/fakepkg/module.py:docstring of fakepkg.module.x.y:6: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

Each of the three census commands from § "Base message-class census" run against this file:

```
$ LANG=C LC_ALL=C grep -o 'unknown node type: .doctest_block' "$CT" | wc -l
1

$ LANG=C LC_ALL=C grep -cE '\.py:docstring of [A-Za-z0-9_.]+:[0-9]+: (ERROR|WARNING): (Unexpected indentation|Block quote ends without a blank line)' "$CT"
2

$ LANG=C LC_ALL=C grep -cE 'Unexpected indentation|Block quote ends without a blank line' "$CT"
2
```

All three at least 1. This proves the patterns and the C locale are not the reason for the
base's zeros.

Key lines:

```
CONTROL_DOCTEST_HITS = 1
CONTROL_DOCSTRING_HITS = 2
CONTROL_RAW_HITS = 2
```

### Real build, cited

Quoted from `74-BASE-EVIDENCE.md`, the pre-fix tree `6cc44f22` (milestone base, before Phase 74's
`doctest_block` handler and QUA-14 fix landed):

```
BASE_WARNING_COUNT = 5
BASE_DOCTEST_UNKNOWN_COUNT = 2
```

One verbatim attributed hit line from that file:

```
33:/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac2d204a5bc5e0bdf/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:5: ERROR: Unexpected indentation. [docutils]
```

`P74_BASE_DOCTEST_UNKNOWN` (2) is at least 1, so `P74_CONTROL_NONZERO = yes`.

Key lines:

```
P74_BASE_WARNINGS = 5
P74_BASE_DOCTEST_UNKNOWN = 2
P74_CONTROL_NONZERO = yes
```

## Base ledger

| Key | Value |
|---|---|
| `BASE_HTML_EXIT` | 0 |
| `BASE_HTML_WARNINGS` | 0 |
| `BASE_HTML_DOCSTRING_REST` | 0 |
| `BASE_PDF_EXIT` | 0 |
| `BASE_PDF_WARNINGS` | 0 |
| `BASE_DOCTEST_UNKNOWN` | 0 |
| `BASE_DOCSTRING_REST` | 0 |
| `BASE_RAW_REST` | 0 |
| `CONTROL_DOCTEST_HITS` | 1 |
| `CONTROL_DOCSTRING_HITS` | 2 |
| `CONTROL_RAW_HITS` | 2 |
| `P74_BASE_WARNINGS` (pre-fix, `6cc44f22`) | 5 |
| `P74_BASE_DOCTEST_UNKNOWN` (pre-fix, `6cc44f22`) | 2 |

75-04 re-measures all of these on the bumped tip. SC4 requires the tip's warning integers not to
have risen above these (0 and 0) and both message-class counts to still be 0.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Plan: 01*
