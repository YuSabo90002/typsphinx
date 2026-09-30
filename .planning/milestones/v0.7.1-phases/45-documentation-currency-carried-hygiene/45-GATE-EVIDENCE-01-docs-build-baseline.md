# Phase 45 Plan 01 — Pre-Phase Docs-Build Warning Baseline

Captured against the untouched tree, before any edit to `docs/`, `pyproject.toml`, or `uv.lock`.

- baseline_sha: 8c74b853f81eaac0c9233a9628928528d16f2d18
- html_warning_count: 1
- pdf_warning_count: 1
- changelog_attributable_warning_count: 0

## Method

Ran both builds directly against the untouched tree (no `-W`, no `-q`, no `-n` — a normal build):

```
uv run python -m sphinx -b html docs/source <scratch>/html
uv run python -m sphinx -b typstpdf docs/source <scratch>/pdf
```

Counts are the number of lines matching `WARNING:` in each build's combined stdout+stderr output
(this literal string, not docutils' `ERROR/3` console-report notation, and not Sphinx's own
end-of-build tally which also counts docutils `ERROR`-severity messages routed through its warning
stream). The changelog-attributable count is the subset of those `WARNING:` lines whose text
mentions `changelog` (case-insensitive grep, none found).

## HTML build

Exit code: 0 (`sphinx-build -b html docs/source <scratch>/html`)

Sphinx's own summary line: `build succeeded, 3 warnings.` (this tally includes two
docutils `ERROR/3` messages emitted through the same warning stream — see Reading below — plus the
one line matching literal `WARNING:`.)

Verbatim `WARNING:` line:

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa28c5bacb7657e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:15: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

For completeness, the two `ERROR:`-severity lines Sphinx's tally also counts (not `WARNING:`, so not
included in `html_warning_count` per the literal-string definition above):

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa28c5bacb7657e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa28c5bacb7657e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:20: ERROR: Unexpected indentation. [docutils]
```

Also present (informational, not counted — these are Python `DeprecationWarning`-family messages
from `sphinx_autodoc_typehints`, not Sphinx build `WARNING:` lines, and five
`document is referenced in multiple toctrees` consistency notices that this Sphinx version prints
without a `WARNING:` prefix and does not fold into its own "N warnings" tally):

- Many repeated `RemovedInSphinx10Warning: 'sphinx_autodoc_typehints._parser._RstSnippetParser.set_application' is deprecated.` lines (a pre-existing upstream deprecation warning, unrelated to this phase, out of fence per the deviation-rules scope boundary).
- Five `document is referenced in multiple toctrees` consistency-check notices (pre-existing, `examples/advanced`, `examples/basic`, `user_guide/builders`, `user_guide/configuration`, `user_guide/templates`).

None of the above mention `changelog`.

## typstpdf build

Exit code: 0 (`sphinx-build -b typstpdf docs/source <scratch>/pdf`)

Sphinx's own summary line: `build succeeded, 3 warnings.`

Verbatim `WARNING:` line (identical source/cause to the HTML build's — both builders share the same
docutils autodoc-docstring parse):

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa28c5bacb7657e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:15: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

The same two `ERROR:`-severity docutils lines as the HTML build also appear (not counted in
`pdf_warning_count` for the same literal-string reason).

## Reading

This phase's own bar is `changelog_attributable_warning_count == 0` after the changes land, and
`html_warning_count` / `pdf_warning_count` must not exceed the baseline values recorded above (1 and
1 respectively). Per RESEARCH.md Pitfall 2, neither `tox -e docs-html` nor `tox -e docs-pdf` passes
`-W`, so a build exiting 0 does not by itself mean zero warnings — the delta must be measured against
this baseline, not against an assumed-zero starting point.

The pre-existing `visit_toctree` docstring `WARNING:`/`ERROR:` trio is a known, out-of-fence defect
(a malformed docstring in `typsphinx/translator.py`, unrelated to DOC-12's changelog delegation) —
carried forward unchanged, not fixed by this plan (scope boundary: only issues directly caused by
this plan's own changes are in scope for auto-fix).
