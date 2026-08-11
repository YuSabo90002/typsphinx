# Phase 45 Plan 01 — Include-Shape Evidence

Records the final `.. include::` directive shape chosen for `docs/source/changelog.rst`, the ladder
rung that produced it, and the measured answers to RESEARCH.md's two open questions.

## Final directive (verbatim)

`docs/source/changelog.rst` in full:

```rst
.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_

Migration Guides
----------------

...
```

(the page's only two lines before `Migration Guides` are the include directive itself — no
hand-authored rST title, no hand-authored framing paragraphs; see "Ladder rung actually used"
below for why).

## Ladder rung actually used: none of the three planned rungs — a fourth, root-caused shape

The plan's action text specified an ordered ladder: (i) `:start-line: 7` under a `Release History`
H2, keeping the rST-native title/framing; (ii) nest the include one section deeper; (iii) add
`:end-before:` at the tail link-definition block. All three were tried or analyzed; none clears the
bar. A fourth shape — omitting `:start-line:` entirely and dropping the hand-authored title/framing
— is what ships. The full investigation, in order:

### Rung (i): `:start-line: 7` under a `Release History` H2 (the plan's literal instruction)

```rst
Changelog
=========

All notable changes to typsphinx are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

Release History
----------------

.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_
   :start-line: 7
```

**Measured:** `sphinx-build -b html` exits 0, but emits **19** `WARNING: Document headings start at
H2, not H1 [myst.header]` lines, all attributed to `docs/source/changelog.rst` (one per `##`-level
release heading in the included fragment — 18 release headings + 1 for the very first). Every one of
these lines contains the literal substring `changelog` (from the file path in the warning text), so
all 19 count as changelog-attributable under this phase's own delta check — the bar is
`changelog_attributable_warning_count == 0`, so **19 fails outright** (baseline was 0).

### Root cause (read from the installed myst-parser source, not guessed)

`myst_parser/mdit_to_docutils/base.py::DocutilsRenderer.update_section_level_state()` tracks heading
levels in `self._level_to_section`, seeded once per parse as `{0: <root>}`. For a new heading at
`level`, it computes `parent_level = max(l for l in self._level_to_section if level > l)` — a
**strict** `<` comparison. For a flat sequence of same-level (`##`) headings with no preceding `#`,
every single one computes `parent_level == 0` (since no level `< 2` other than `0` is ever
registered), and the check `if parent_level == 0: msg = f"Document headings start at H{level}, not
H1"` fires — **once per heading**, not once per document. This is intrinsic to the *fragment's own*
first-seen heading sequence; it has nothing to do with where the include is spliced into the host
document.

Separately, `docutils/parsers/rst/directives/misc.py::Include.custom_parse()` (the code path
`:parser:` invokes) parses the included text into a **brand-new, isolated `document`**
(`document = utils.new_document(...)`) and only returns `document.children` to be grafted onto the
host tree afterward. The renderer's `_level_to_section` state is seeded fresh for that temporary
document and is never informed by the host rST document's own ambient section nesting.

**Consequence, confirmed empirically below:** nesting the include deeper in the *host* rST document
cannot fix a "no H1 in the fragment" warning, because the fragment's internal consistency check runs
in total isolation from the host's section structure.

### Rung (ii): nest the include one section deeper (empirically falsified)

Tried this exact shape:

```rst
Release History
----------------

Full History
~~~~~~~~~~~~

.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_
   :start-line: 7
```

**Measured:** `grep -c 'WARNING:.*myst.header'` on the HTML build's stderr — **19**, identical to
rung (i). Confirms the root-cause analysis: ambient rST nesting depth has zero effect on this
warning family. Rung (ii), as literally specified in the plan, does not clear the bar.

### Rung (iii): `:end-before:` bounded at the tail link-definition block (analyzed, not tried)

`:end-before:` only trims the *end* of the included range; the warning fires because of the
*missing H1 at the start*, so bounding the tail cannot address it. Not empirically run — analysis
alone rules it out, since it cannot change anything about the first heading encountered.

### The shape that actually works — proven both by source analysis and a real build

The only way to satisfy myst-parser's own internal consistency check is for the fragment's **first**
heading to be H1. `CHANGELOG.md`'s own H1 (`# Changelog`, line 1) is the only H1 in the file, and
this plan does not edit `CHANGELOG.md` (explicit `<prohibitions>` in the PLAN.md frontmatter), so the
only way to include that H1 is to **not** clip it via `:start-line:`. Doing so, and having the
composite page's title come from the included content's own H1 rather than a hand-authored rST
title, is the shape that ships:

```rst
.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_

Migration Guides
----------------
...
```

**Measured (HTML):** `sphinx-build -b html docs/source <out>` exits 0. `grep -n 'WARNING:'` on
combined stdout+stderr returns exactly **1** line — the pre-existing, out-of-fence `visit_toctree`
docstring defect recorded in `45-GATE-EVIDENCE-01-docs-build-baseline.md` (`html_warning_count=1` at
baseline). **Zero** `myst.header` warnings. Zero lines matching both `WARNING` and `changelog`
(case-sensitive, matching the plan's own verify script) —
`changelog_attributable_warning_count = 0`.

**Measured (typstpdf):** `sphinx-build -b typstpdf docs/source <out>` exits 0, same single
pre-existing `WARNING:` line, zero changelog-attributable warnings, `typsphinx.pdf` produced with a
valid `%PDF` header (`pdf_warning_count = 1`, matching baseline).

**Delta against the Task 1 baseline** (`45-GATE-EVIDENCE-01-docs-build-baseline.md`:
`html_warning_count=1`, `pdf_warning_count=1`, `changelog_attributable_warning_count=0`): both counts
are equal to baseline (not exceeding it), and the changelog-attributable count is 0 both before and
after — the phase's own bar (`changelog_attributable_warning_count == 0` post-change,
`html_warning_count`/`pdf_warning_count` not exceeding baseline) is met exactly.

**Plan's own automated `<verify>` script, run verbatim against this shape:** `OK both builders`
(all four assertions passed: HTML exit 0 with zero changelog-attributable warnings, all 11 named
versions present in `changelog.html`, exactly one `<hN>Changelog` heading found, typstpdf exit 0 with
a valid `%PDF`-prefixed output file).

## Deviation from the plan's literal shape instruction (documented per deviation Rule 1)

The plan's `<action>` text explicitly instructed keeping "the page title `Changelog` and its two
framing paragraphs" and using `:start-line: 7` to skip `CHANGELOG.md`'s own H1 and preamble. That
exact shape (rung i) produces 19 changelog-attributable warnings — a real defect, root-caused above
— and the plan's own escalation ladder (rungs ii/iii) does not clear it either (ii empirically
falsified; iii ruled out by analysis, since it only bounds the *end* of the range). Per this task's
own instruction ("iterate on the include's shape within this task ... stop at the first rung that
produces zero changelog-attributable warnings") and deviation Rule 1 (auto-fix a defect blocking the
task's own acceptance bar), the shape was changed to omit `:start-line:` entirely, letting the page's
title and its two framing paragraphs come from `CHANGELOG.md`'s own H1 and preamble instead of a
duplicated hand-authored rST copy — this is the only shape, of the four considered, that is provably
warning-clean without editing `CHANGELOG.md` (prohibited) or suppressing warnings (prohibited).

**Consequence recorded, not hidden:** `docs/source/changelog.rst` no longer has a single overarching
`Changelog` title wrapping `Migration Guides` / `Deprecation Policy` / `Upcoming Features` /
`Versioning` / `Release Process` / `See Also` as H2 subsections. Because the document's direct
children are now multiple top-level sections (the included `Changelog` H1 subtree, plus six more
top-level sections from the retained framing content) rather than exactly one, docutils' "promote the
lone top-level section to the document title" heuristic does not apply, and **all seven sections
render as sibling `<h1>` elements** rather than one `<h1>` with six `<h2>` children. This is a
measured, non-hidden side effect — HTML confirmed via `grep -n '<h1'` on the built page: `Changelog`,
`Migration Guides`, `Deprecation Policy`, `Upcoming Features`, `Versioning`, `Release Process`,
`See Also`, all `<h1>`. It does not violate any `must_haves.truths` or `acceptance_criteria` in this
plan (still exactly one heading whose text is `Changelog`; all sections still present, unedited in
content, per "keep ... in place for now"). Flagged here for Plan 45-02, which owns correcting these
sections' *contents* (D-06) and should be aware the *heading level* also changed as an unavoidable
consequence of this fix.

## Two research open questions — measured answers

**(a) Does the included fragment's heading depth nest sanely under Phase 44.1's relative
`depth:`/`offset:` mechanism, once combined with a real `-b typstpdf` compile?** Yes, with no
compile-fatal and no visibly incorrect nesting in the HTML render, which shares the same doctree
node types the Typst translator consumes: `Changelog` (H1) → per-release `## [x.y.z]` (H2) →
per-category `### Added`/`### Fixed`/etc. (H3), a strictly consecutive 1→2→3 sequence throughout —
inspected via `grep -n '<h[1-6]' changelog.html`, first ~30 entries confirmed strictly ordered with
no skipped or out-of-sequence levels. The `-b typstpdf` build compiled to a valid `%PDF`-prefixed
file with zero changelog-attributable warnings, so Phase 44.1's toctree-relative offset mechanism did
not choke on the deeper nesting.

**(b) Does CommonMark's shortcut-reference resolution of the bracketed version headings against
CHANGELOG.md's own tail link-definition block render acceptably as linked headings?** Yes — confirmed
in the rendered HTML: e.g. `<h2><a class="reference external"
href="https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.0">0.7.0</a> -
2026-08-04...</h2>`. Every numbered-version heading resolves to a working external GitHub release-tag
link; the `[Unreleased]` heading resolves to the compare-view link. No ladder rung (iii) fallback
(`:end-before:` losing the linked headings) was needed — the CommonMark link resolution renders
correctly with the chosen shape.

## Backstop truth measured live (not merely trusted)

Confirmed by temporarily moving `CHANGELOG.md` aside and re-running `sphinx-build -b html`: the build
does not raise a Python exception or a nonzero process exit (Sphinx's per-document error recovery
continues the rest of the build), but docutils itself reports the include failure loudly, at
`CRITICAL` severity:

```
docs/source/changelog.rst:1: CRITICAL: Problems with "include" directive path:
InputError: [Errno 2] No such file or directory: 'CHANGELOG.md'. [docutils]
```

The resulting `changelog.html` page silently drops the `Changelog` heading and all release content
(the page's *first* section becomes `Migration Guides` instead), confirming the include mechanism
does not paper over a missing source file with a blank-but-successful page — the failure is visible
in the build log at the highest docutils severity level, immediately and unambiguously attributable
to the `include` directive. `CHANGELOG.md` was restored immediately after this check;
`git status --short -- CHANGELOG.md` shows no diff.

## Two carried consequences (recorded per the plan's instruction, not resolved here)

- **Japanese (`ja`) site translations.** Every line the include newly surfaces on the published
  changelog page (`CHANGELOG.md`'s full content, now rendered on both `en` and `ja` builds since
  `docs/source/changelog.rst` is shared byte-for-byte between the `typsphinx` and
  `typsphinx-doc-translations` repositories) renders untranslated on the `ja` site until the separate
  `typsphinx-doc-translations` repository's gettext catalogs are regenerated. This is out of this
  repository's scope; flag at milestone close.
- **Read the Docs.** `.readthedocs.yaml`'s `python.install` step is `method: uv` / `command: sync` /
  `extras: [docs]` (confirmed, read verbatim this session) — `myst-parser` is picked up automatically
  by the next RTD build with no RTD-side configuration change needed.

## Environment note (unrelated to the include shape, recorded for completeness)

This worktree's `uv sync`-installed `.venv/bin/ruff` is a generic-linux ELF that the NixOS host
cannot execute directly (`Could not start dynamically linked executable`) — the same class of issue
PROJECT.md's Phase 39/40 footers record for `.venv/bin/uv`. Resolved the same way: symlinked a
Nix-store `ruff` (`nix-shell -p ruff`, resolved version `0.15.14`, inside this repo's
`ruff>=0.15,<0.16` pin) over `.venv/bin/ruff`. `uv run ruff check .` then passed clean. This is a
local-environment fix only (the symlink lives inside the gitignored `.venv/`), not a repository
change.
