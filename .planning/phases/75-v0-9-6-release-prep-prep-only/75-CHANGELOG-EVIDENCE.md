# Phase 75 — CHANGELOG Evidence (SC2, SC3)

## Base census

Before editing, from `git show "$B:CHANGELOG.md"` where `B = BASE_75_03 =
526a21d352696cb65c570d07d75ef8c7e3aa96a1`:

```
$ git show 526a21d352696cb65c570d07d75ef8c7e3aa96a1:CHANGELOG.md | wc -l
1349
```

The base `## [Unreleased]` section body (from `^## \[Unreleased\]$` to the line before the next
`^## \[`) was extracted with:

```
awk '/^## \[/{if(f)exit} f; /^## \[Unreleased\]$/{f=1}' <base CHANGELOG.md>
```

giving 60 lines, holding `### Added` (1 bullet), `### Changed` (4 bullets), `### Fixed`
(1 bullet), and `### Planned for Future Releases` (5 items, no bold-lead bullet).

```
$ awk '...' | grep -cE '^- \*\*'
6
```

CARRIED_BULLETS_BASE = 6

BASE_SUBSECTIONS = `### Added|### Changed|### Fixed|### Planned for Future Releases|`

```
$ grep -cE '^## \[' <base CHANGELOG.md>
23

$ grep -cE '^\[[^]]+\]: https' <base CHANGELOG.md>
23
```

HEADINGS_BEFORE = 23
LINKREFS_BEFORE = 23

```
$ grep -c '^### Known Limitations' <base CHANGELOG.md>
1
```

KNOWN_LIMITATIONS_BEFORE = 1. The base file's only anchored `^### Known Limitations` hit is the
`[0.1.0b1]` section (`:1205` in the base file's own numbering). The unanchored form,
`grep -c 'Known Limitations'`, would additionally count a prose mention elsewhere in the file
(the `[0.9.0]` section's discussion text), which is why every check in this evidence file uses
the anchored `^` form.

Per-subsection SHA-256 digests of the carried base bodies, blank lines dropped
(`awk -v h="### X" '$0==h{f=1;next} f&&/^### /{exit} f' | grep -v '^$' | sha256sum`):

CARRIED_ADDED_SHA = c630d24f43fddf5c82efd09f8d3675a75fab078a344e7fa4e1186a48c1b3492d
CARRIED_CHANGED_SHA = 6dac1ebd5e08cf5ef33d82673597cfb30d5dc59e217c04d82842fa2237abc7df
CARRIED_FIXED_SHA = ec38c5cbdfae8b4c32c95864e43f0cb658f06776f9f0f482f40143962c309f20

## Curation

`CHANGELOG.md` was edited to:

1. Insert a fresh `## [Unreleased]` heading holding only the existing `### Planned for Future
   Releases` block (5 items, unchanged, not promoted).
2. Insert `## [0.9.6] - 2026-09-20` (RELEASE_HEADING_DATE, `date -u +%F` at execution), with:
   - A lead paragraph naming the doctest rendering fix as the release's subject, the
     `expected semicolon or line break` compile abort as the pre-fix failure's severity, an
     explicit upgrade recommendation against 0.9.2, and the contributor tooling acknowledged in
     one side-note sentence.
   - The carried `### Added` (1 bullet) and `### Changed` (4 bullets) bodies, copied
     byte-identically from the base `## [Unreleased]` section — no re-wrap, re-word, re-order or
     re-assignment.
   - `### Fixed` with two new bullets first (the doctest bullet trailing `(TRN-01, TRN-02)`, then
     the QUA-14 bullet trailing `(QUA-14)`), followed by the carried `### Fixed` bullet as a
     byte-identical tail.
   - `### Known Limitations`, holding exactly one bold-lead entry naming NUM-01, adapted (not
     copied verbatim) from `75-RESEARCH.md` Pattern 4's draft shape and the NUM-01 todo's
     precondition, both symptoms and workaround.
   - `### Verified`, four bullets: no new runtime/dev dependency other than the `dev` extra's
     `tox-uv` return; the four `@preview` packages unchanged across the three declaration sites;
     the GATE-01 real-`typst.compile()` coverage behind the new `doctest_block` handler; and the
     QUA-14 clean-build warning reading (zero, down from a measured baseline of five).
3. Move the tail link block: `[0.9.6]: .../releases/tag/v0.9.6` inserted immediately above
   `[0.9.2]`, and `[Unreleased]`'s compare base re-pointed from `v0.9.2` to `v0.9.6`.

`tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` tuple gained `"0.9.6"`, appended
immediately after the existing `"0.9.2"` entry, reordering nothing.

## New section census

```
$ awk '/^## \[/{if(f)exit} f; /^## \[0\.9\.6\]/{f=1}' CHANGELOG.md | grep -E '^### ' | tr '\n' '|'
### Added|### Changed|### Fixed|### Known Limitations|### Verified|
```

Per-subsection bullet counts (`grep -cE '^- \*\*'`): Added 1, Changed 4, Fixed 3.

```
$ grep -cE '^## \['CHANGELOG.md
24

$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
24
```

HEADINGS_AFTER = 24
LINKREFS_AFTER = 24

Each is the base count plus exactly one: `HEADINGS_AFTER` gains the new `## [0.9.6]` heading, and
`LINKREFS_AFTER` gains the new `[0.9.6]` tail link.

```
$ grep -n '^## \[0\.9\.6\]' CHANGELOG.md
17:## [0.9.6] - 2026-09-20

$ grep -n '^## \[Unreleased\]$' CHANGELOG.md
8:## [Unreleased]
```

The `## [0.9.6]` heading (line 17) sits below the `## [Unreleased]` heading (line 8).

RELEASE_HEADING_DATE = 2026-09-20

```
$ grep -n '^\[0\.9\.6\]:' CHANGELOG.md
1378:[0.9.6]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6

$ grep -n '^\[0\.9\.2\]:' CHANGELOG.md
1379:[0.9.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.2

$ grep -n '^\[Unreleased\]:' CHANGELOG.md
1401:[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD
```

The `[0.9.6]` tail link (1378) sits immediately above `[0.9.2]` (1379).

Recomputed carried digests, compared against the base ones recorded above — all three match:

| Subsection | Base digest | Recomputed digest |
|---|---|---|
| `### Added` | `c630d24f…` | `c630d24f…` (identical) |
| `### Changed` | `6dac1ebd…` | `6dac1ebd…` (identical) |
| `### Fixed` (carried tail) | `ec38c5cb…` | `ec38c5cb…` (identical) |

`### Known Limitations` anchored count:

```
$ grep -c '^### Known Limitations$' CHANGELOG.md
2
```

KNOWN_LIMITATIONS_AFTER = 2

That count is the pre-existing `[0.1.0b1]` heading plus the new one added this phase.

## REL-16: which branch was taken

The branch taken is the `### Known Limitations` section, not the declination — SC3 and D-10/D-11
require a genuine disclosure entry, not silence.

Its candidate set is **NUM-01 alone**. REL-16's literal text names three defects; two of them were
measured closed before this phase:

- **The converted-image rehome collision** closed in v0.8.0. `typsphinx/builder.py` carries a
  reserved image namespace constant closing this collision, and its tracking todo is in
  `.planning/todos/completed/` — measured, not assumed.
- **The `typst_documents` duplicate-target cluster** also closed in v0.8.0, via the pre-write
  output-path collision validator landed the same release.

Both closures are recorded in the same v0.8.0 milestone that also delivered the two-layer output
split; their todos are archived under `.planning/todos/completed/`, not `.planning/todos/pending/`.

WR-02 and WR-03 are genuinely open defects in this codebase, but REL-16's text does not name
either one, so neither is added to this section — adding them would exceed what this requirement
actually asks for.

D-12's anchored grep expects exactly two `### Known Limitations` headings after this phase (the
pre-existing `[0.1.0b1]` one plus this phase's new one), confirmed above: `KNOWN_LIMITATIONS_AFTER
= 2`.

REL16_BRANCH = known-limitations-section

## Zero-skip changelog page gate

```
$ uv run pytest tests/test_changelog_page_gate.py -q -rs -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a64ee11a04ac3c9ef
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests/test_changelog_page_gate.py ......                                 [100%]

============================== 6 passed in 4.21s ===============================
```

No `SKIPPED` lines were reported. The `docs` extra (installing `myst-parser`) is present in this
worktree's environment per this plan's `<worktree_provisioning>`, so the content-coverage classes
ran rather than skipped.

CHANGELOG_GATE_EXIT = 0
CHANGELOG_GATE_SKIPS = 0

## Commit discipline

`CHANGELOG.md` and `tests/test_changelog_page_gate.py` were left uncommitted at Task 2's own
close, per this plan's worktree provisioning instructions. Only this evidence file
(`75-CHANGELOG-EVIDENCE.md`) was staged and committed for Task 2; the product edits landed in
Task 3's single five-file commit (`75-BUMP-EVIDENCE.md` § "The one commit",
`BUMP_COMMIT_SHA = 84edd348b52f1f7e95073d2b3ebcbcd36417bc15`).

## Extractor transcript

```
$ uv run python scripts/extract_changelog_section.py 0.9.6 > "$S/p7503_release_notes.md" 2>"$S/p7503_extract.err"; echo "exit:$?"
exit:0
```

EXTRACT_EXIT = 0

```
$ wc -c "$S/p7503_release_notes.md"
7104
```

EXTRACT_BYTES = 7104

The extractor's stdout, verbatim — this is the text that becomes the GitHub Release body:

```markdown
This release's headline fix is doctest block rendering: a `>>>` example in your documentation now
renders correctly, and — where it previously sat next to other content in the same container — no
longer aborts the Typst compile with `expected semicolon or line break`. That earlier failure was
not merely cosmetic, so 0.9.2 users with any doctest block in their sources should upgrade to this
release. As a side note, this release also carries the contributor-tooling and dependency-workflow
work accumulated since 0.9.2. Zero new runtime dependencies.

### Added

- **A `tox -e linkcheck` environment checks the documentation's external links, including
  their `#anchor` targets (QUA-13, DOC-24).** It runs Sphinx's link-check builder over the
  documentation sources; because it needs the network, it is not part of a plain `tox` run,
  and it is contributor tooling, listed alongside `docs-html` and `docs-pdf`. This has no
  effect on installing or using typsphinx.

### Changed

- **Contributor tooling returns to `tox-uv` from `tox-uv-bare` (TOX-01, TOX-02, TOX-03, TOX-04).**
  The `dev` extra and `tox.ini`'s `requires` line once again name `tox-uv`, with `uv.lock`
  regenerated in the same change. This has no effect on installing or using typsphinx. A CI run
  dispatched against the branch carrying this change was green across the Linux, Windows and
  macOS test lanes.

- **Dependabot's Python dependency updates now use the `uv` ecosystem instead of `pip` (DEP-01,
  DEP-02, DEP-03, DEP-04, DEP-05).** Each dependency pull request now updates `pyproject.toml` and
  `uv.lock` in the same commit, so CI's `uv sync --locked` step succeeds and the test, lint and
  type jobs actually run against the updated dependencies; before the switch, every such pull
  request stopped at that step before any test ran. Labels and the pull-request limit behave as
  before. The `sphinx-typst-stack` grouping is kept as configured, but no grouped pull request has
  opened under `uv` yet: the group's `docutils` update cannot currently resolve against Sphinx's
  own `docutils` cap. The switch was proven on the pull request that also carried a routine `ruff`
  version bump. This has no effect on installing or using typsphinx.

- **`flake.nix` now provides a NixOS development shell (NIX-01, NIX-02, NIX-03, NIX-04, NIX-05,
  NIX-06, NIX-07, NIX-08, DOC-19, DOC-20, DOC-21).** The shell puts command shims for `uv`, `tox`,
  `ruff`, `black`, `mypy`, `pytest` and `sphinx-build` on `PATH`; each one runs the checkout's own
  `.venv` tools inside an FHS sandbox, so the versions `uv.lock` pins run on NixOS without any
  manual step. This applies only to contributors who enter that shell on NixOS; CI and every other
  platform are unchanged, and this has no effect on installing or using typsphinx. The `darwin`
  systems evaluate under this shell but remain unverified. `CLAUDE.md`'s contributor notes, the
  `tox.ini` comment and the `flake.nix` header now describe the mechanism.

- **Type annotations in typsphinx's source now use builtin generics (QUA-09, QUA-11, QUA-12,
  DOC-22, DOC-23).** `typsphinx/` and `tests/` moved off the `typing` aliases `Dict`, `List`,
  `Set` and `Tuple` onto the builtin `dict`, `list`, `set` and `tuple`, with `Iterator` now
  imported from `collections.abc` instead; the linter now enforces this style, and the
  contributor notes in `CLAUDE.md` describe it. The visible effect is in the API reference: it
  now shows, for example, `dict[str, Any]` where it showed `Dict[str, Any]`. This has no effect
  on installing or using typsphinx. The Typst output typsphinx generates and its runtime
  behaviour are unchanged: the `.typ` output is byte-identical across the test-fixture corpus of
  167 projects.

### Fixed

- **A `>>>` doctest example now renders as a Typst code block with its line structure intact
  (TRN-01, TRN-02).** Previously `doctest_block` nodes had no translator handler at all. Where a
  doctest block was followed by further content inside the same container, the missing handler
  left the emission malformed and the PDF compile itself failed. The whole block is highlighted as
  Python, so output lines are coloured as Python source rather than as plain console output — a
  known, accepted trade-off. typsphinx's own published API reference, whose docstrings carry
  several `>>>` examples, is the worked example for this fix.

- **typsphinx's own docstrings no longer raise docutils `Unexpected indentation` or `Block quote
  ends without a blank line` errors when the package is autodoc'd (QUA-14).** The docstring
  formatting defects responsible for those errors during this project's own documentation build
  have been corrected.

- **The HTML documentation's sidebar now lists each User Guide and Examples page exactly
  once, nested under its section (DOC-18).** Previously each of those pages was also listed
  a second time beside its section, so Sphinx no longer reports them as referenced in
  multiple toctrees. This has no effect on installing or using typsphinx.

### Known Limitations

- **A multi-master `typst_documents` configuration can produce a diverging or missing `:numref:`
  reference number (NUM-01).** A single-master project is entirely unaffected. When the same
  figure is reachable from two masters, Sphinx bakes one project-wide number into the `:numref:`
  reference text, but each compiled Typst wrapper counts its own captions independently — so the
  reference reads correctly in one master's PDF and points at the wrong number in the other, with
  no diagnostic reporting the mismatch. When a figure is reachable only from a non-root master, it
  never enters Sphinx's root-document figure-numbering scan, so its `:numref:` reference falls
  back to the raw label text instead of a number; Sphinx does emit one warning naming the label,
  so the build log carries a diagnostic even though the compiled PDF gives the reader none.
  **Workaround:** use a single-master `typst_documents` configuration, or replace `:numref:` with
  `:ref:` for the affected figures.

### Verified

- No new runtime dependency and no new dev dependency were added across this milestone's diff
  (`v0.9.2..HEAD`); the one change to that surface is the `dev` extra's return to `tox-uv`
  (TOX-01, TOX-02, TOX-03, TOX-04) — a contributor-tooling change with no effect on installing or
  using typsphinx.
- The four bundled `@preview` package version strings are unchanged across all three declaration
  sites (`typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`).
- The new `doctest_block` handler is bound by a real `typst.compile()` gate
  (`tests/test_doctest_block_render_gate.py`, GATE-01) covering multiple containment shapes,
  including a master document that failed to compile at all before the fix.
- A clean, C-locale rebuild of `docs/source` reports zero docutils `Unexpected indentation` /
  `Block quote ends without a blank line` diagnostics attributable to typsphinx's own docstrings
  (QUA-14), down from a measured baseline of five such warnings before the fix.
```

```
$ grep -c '^### Planned for Future Releases' "$S/p7503_release_notes.md"
0

$ grep -cE '^## \[' "$S/p7503_release_notes.md"
0
```

EXTRACT_PLANNED_BLOCK = 0
EXTRACT_VERSION_HEADINGS = 0

The extractor emits the body only, terminated at the next `## [` heading (or end of file), exactly
as its own docstring describes.

Digest comparison — the extractor's stdout against the `## [0.9.6]` section body read straight out
of the committed `CHANGELOG.md` with leading and trailing blank lines stripped:

```
$ awk '/^## \[/{if(f)exit} f; /^## \[0\.9\.6\]/{f=1}' CHANGELOG.md \
    | sed -e '/./,$!d' | tac | sed -e '/./,$!d' | tac | sha256sum
f9a52e3de808bd49981658a1169e96e761fd409432c45fa2f350c5acad0f59be

$ sha256sum "$S/p7503_release_notes.md"
f9a52e3de808bd49981658a1169e96e761fd409432c45fa2f350c5acad0f59be
```

Both digests are `f9a52e3de808bd49981658a1169e96e761fd409432c45fa2f350c5acad0f59be`.

EXTRACT_MATCHES_SECTION = yes

```
$ uv run pytest tests/test_changelog_extraction.py -q -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a64ee11a04ac3c9ef
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests/test_changelog_extraction.py ......                                [100%]

============================== 6 passed in 0.24s ===============================
```

EXTRACTION_TESTS_EXIT = 0

The committed `scripts/extract_changelog_section.py` is the one under test — it was executed via
`uv run python scripts/...`, never reimplemented or hand-copied.

## Second commit

Both evidence files (`75-BUMP-EVIDENCE.md` and this file) are committed together in a second,
`.planning`-only commit, after the five-file product commit above.
