# Phase 77 — Base Evidence (clean documentation ledger and linkcheck URI set at the phase base)

## Head check and provisioning

- `date -u +%FT%TZ` -> `2026-09-28T13:07:46Z` (same head check as `77-CLOSEOUT-GUARD.md`)
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a008a40c849ef1103`
- `test -f .git; echo "exit:$?"` -> `exit:0`
- `command -v uv` -> `/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv`
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`

Provisioning was already done for this plan (see `77-CLOSEOUT-GUARD.md` § "Head check and
provisioning"); this task reuses the same venv, quoting `SCRATCH_77_01` from that file.

```
SCRATCH_77_01 = /tmp/p7701.p8Y5y6
```

`git rev-parse HEAD` before this task's own commit (Task 1's commit has already landed):

```
BASE_LEDGER_SHA = 19afca8799a8c714988fbc599b15110a886e9f0b
```

## Base identity

```
PHASE_BASE_SHA = 3984b231e30fbb76ba156d2f9b2abe475231bccf
```

(Quoted from `77-CLOSEOUT-GUARD.md`.)

```
$ git show HEAD:pyproject.toml | grep -m1 '^version = '
version = "0.9.6"
```

This ledger is taken on the unbumped tree — `77-02` performs the bump in this same wave, and `77-04`
re-measures on the bumped tip.

## Base docs-html

`rm -rf docs/_build` run first (the whole output tree, since an incremental rebuild under-reports
warnings), then:

```
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html > "$S/p7701_html.log" 2>&1; echo "exit:$?"
exit:0
```

```
BASE_HTML_EXIT = 0
```

Verbatim `build succeeded` line from `$S/p7701_html.log`:

```
$ LC_ALL=C grep -E '^build succeeded' "$S/p7701_html.log"
build succeeded.
```

`sed -n 's/^build succeeded, \([0-9]*\) warnings\{0,1\}\.$/\1/p'` does not match the exact-zero form
`build succeeded.`, so the warning count is taken as `0` per the plan's own rule.

```
BASE_HTML_WARNINGS = 0
```

## Base docs-pdf

`rm -rf docs/_build` run again, then:

```
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-pdf > "$S/p7701_pdf.log" 2>&1; echo "exit:$?"
exit:0
```

```
BASE_PDF_EXIT = 0
```

Verbatim `build succeeded` line from `$S/p7701_pdf.log`:

```
$ LC_ALL=C grep -E '^build succeeded' "$S/p7701_pdf.log"
build succeeded.
```

```
BASE_PDF_WARNINGS = 0
```

## Base linkcheck

`rm -rf docs/_build` run again, then:

```
$ LANG=C LANGUAGE=C LC_ALL=C uv run tox -e linkcheck > "$S/p7701_lc1.log" 2>&1; echo "exit:$?"
exit:0
```

The first attempt came back clean — no retry was needed.

```
BASE_LINKCHECK_RUNS = 1
BASE_LINKCHECK_RUN_1_EXIT = 0
```

`docs/_build/linkcheck/output.json` copied to `$S/p7701_linkcheck_base.json`.

```
$ jq -s length "$S/p7701_linkcheck_base.json"
96

$ jq -s '[.[] | select(.status == "working")] | length' "$S/p7701_linkcheck_base.json"
96
```

Total equals working count — every record resolved `working`.

```
BASE_LINKCHECK_TOTAL = 96
BASE_LINKCHECK_WORKING = 96
BASE_LINKCHECK_CLEAN = yes
```

No non-`working` records to transcribe.

**Unique `(status, uri)` pairs**, `LC_ALL=C sort -u`, each as a tab-separated `LCBASE<TAB>status<TAB>uri`
line (96 lines total, all `status` = `working`, matching the 96 unique URIs above):

```
LCBASE	working	https://docs.python.org/3/builtins/constants.html#Ellipsis
LCBASE	working	https://docs.python.org/3/builtins/constants.html#None
LCBASE	working	https://docs.python.org/3/builtins/exceptions.html#Exception
LCBASE	working	https://docs.python.org/3/builtins/exceptions.html#ImportError
LCBASE	working	https://docs.python.org/3/builtins/functions.html#bool
LCBASE	working	https://docs.python.org/3/builtins/functions.html#int
LCBASE	working	https://docs.python.org/3/builtins/functions.html#object
LCBASE	working	https://docs.python.org/3/builtins/stdtypes.html#bytes
LCBASE	working	https://docs.python.org/3/builtins/stdtypes.html#dict
LCBASE	working	https://docs.python.org/3/builtins/stdtypes.html#list
LCBASE	working	https://docs.python.org/3/builtins/stdtypes.html#set
LCBASE	working	https://docs.python.org/3/builtins/stdtypes.html#str
LCBASE	working	https://docs.python.org/3/builtins/stdtypes.html#tuple
LCBASE	working	https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator
LCBASE	working	https://docs.python.org/3/library/pathlib.html#pathlib.Path
LCBASE	working	https://docs.python.org/3/library/typing.html#typing.Any
LCBASE	working	https://docs.python.org/3/library/typing.html#typing.ClassVar
LCBASE	working	https://github.com/YuSabo90002/typsphinx
LCBASE	working	https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/13
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/19
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/20
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/21
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/25
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/28
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/31
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/36
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/38
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/39
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/4
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/40
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/61
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/62
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/68
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/69
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/75
LCBASE	working	https://github.com/YuSabo90002/typsphinx/issues/77
LCBASE	working	https://github.com/YuSabo90002/typsphinx/pull/33
LCBASE	working	https://github.com/YuSabo90002/typsphinx/pull/65
LCBASE	working	https://github.com/YuSabo90002/typsphinx/pull/70
LCBASE	working	https://github.com/YuSabo90002/typsphinx/pull/72
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.1.0b1
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.1
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.2
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.3.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.1
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.2
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.3
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.4
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.1
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.5
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.0
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.2
LCBASE	working	https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6
LCBASE	working	https://keepachangelog.com/en/1.0.0/
LCBASE	working	https://pypi.org/project/typsphinx/
LCBASE	working	https://pypi.org/project/typsphinx/#history
LCBASE	working	https://semver.org/spec/v2.0.0.html
LCBASE	working	https://typsphinx.readthedocs.io/ja/latest/
LCBASE	working	https://typst.app/docs
LCBASE	working	https://typst.app/universe
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.errors.ExtensionError
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/builderapi.html#sphinx.builders.Builder
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_addname
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_annotation
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_content
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_inline
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_name
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_optional
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_parameter
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_parameterlist
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_returns
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_sig_keyword
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_sig_name
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_sig_operator
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_sig_punctuation
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_sig_space
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_signature
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.desc_signature_line
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.glossary
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.index
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.seealso
LCBASE	working	https://www.sphinx-doc.org/en/master/extdev/nodes.html#sphinx.addnodes.versionmodified
```

This inline transcript reproduces the sorted, deduplicated `(status, uri)` pair set exactly as
extracted from `$S/p7701_linkcheck_base.json` at generation time — the full 96-line set is recorded
here in file order; the digest below is computed from the complete set, not a truncated sample.

```
$ jq -rs '[.[].uri] | unique | .[]' "$S/p7701_linkcheck_base.json" | LC_ALL=C sort -u | sha256sum
918f7d0135a6fc047aa88583db7e7da6378638618d16a8a1e36b4af9151b63c1  -
```

```
BASE_LINKCHECK_URISET_SHA256 = 918f7d0135a6fc047aa88583db7e7da6378638618d16a8a1e36b4af9151b63c1
```

**The two Class A controls** (`75-GREEN-TREE-EVIDENCE.md` § "AMENDED 2026-09-20" precedent): on the
phase base, `v0.9.6` is already tagged and published, so both tag-referencing changelog links
resolve — unlike the bumped tip, which will carry the same link shapes pointed at the not-yet-existing
`v0.9.7` tag.

```
$ curl -s -o /dev/null -w '%{http_code}' https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD
200

$ curl -s -o /dev/null -w '%{http_code}' https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6
200
```

Both confirmed `working` directly in the linkcheck JSON above as well.

```
BASE_V096_COMPARE_STATUS = working
BASE_V096_RELEASE_STATUS = working
```

These are the same link shapes the bumped tip will carry for `v0.9.7` — their resolving here shows
the tip's expected pre-tag failures come from the missing tag, not from the link shape itself.

## Base ledger

| Key | Value |
|---|---|
| `BASE_LEDGER_SHA` | `19afca8799a8c714988fbc599b15110a886e9f0b` |
| `BASE_HTML_EXIT` | `0` |
| `BASE_HTML_WARNINGS` | `0` |
| `BASE_PDF_EXIT` | `0` |
| `BASE_PDF_WARNINGS` | `0` |
| `BASE_LINKCHECK_RUNS` | `1` |
| `BASE_LINKCHECK_TOTAL` | `96` |
| `BASE_LINKCHECK_WORKING` | `96` |
| `BASE_LINKCHECK_CLEAN` | `yes` |
| `BASE_LINKCHECK_URISET_SHA256` | `918f7d0135a6fc047aa88583db7e7da6378638618d16a8a1e36b4af9151b63c1` |
| `BASE_V096_COMPARE_STATUS` | `working` |
| `BASE_V096_RELEASE_STATUS` | `working` |

`77-04` re-measures the three builds on the bumped tip. SC#3 requires the tip's warning integers
not to have risen above these (both 0 here, so the tip must also read 0 for a clean comparison), and
the tip's linkcheck is read against this URI set — the two `v0.9.6` tag-referencing records recorded
`working` here are expected to read differently on the bumped, not-yet-tagged tip (the Class A shape
carried from Phase 75, per `77-01-PLAN.md` § "Other flagged assumptions").

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Plan: 01*
