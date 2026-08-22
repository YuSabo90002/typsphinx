# Phase 57 — CHANGELOG Evidence (SC#2)

## SC#2 — the release body, in both directions

Command: `uv run python scripts/extract_changelog_section.py 0.9.0`

Exit code: `0`

stdout (verbatim — this is exactly what the GitHub Release body will be for `v0.9.0`, byte for
byte, through `scripts/extract_changelog_section.py`):

```
This release lets every `typst_documents` entry choose its own template, Typst Universe package,
and template-function arguments through the validated `typst_document_templates` registry, instead
of one globally-configured template being applied to every master document. **This minor release
breaks two independent things** — read the `### Changed` and `### Removed` sections below, and see
the "Migrating from 0.8.x to 0.9.0" guide in the published documentation for the exact rewrite each
breaking change needs. What does **not** break: the registry itself is additive — a `conf.py` that
declares no `typst_document_templates` and no fifth `typst_documents` element keeps producing the
same PDF, because the built-in `"typst"` key resolves to exactly the same global configuration
(`typst_template` / `typst_package` / `typst_template_function` / `typst_template_mapping`) it
always did.

### Added

- **A `conf.py` can now declare per-document templates through the `typst_document_templates`
  registry (TPL-01, TPL-02, TPL-03, TPL-04, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17,
  CONF-18).** Each entry carries `template` (a local `.typ` path) **xor** `package` (a Typst
  Universe spec), plus an optional `template_function`; a `typst_documents` entry's fifth element
  now names the registry key to use, several entries can share one key, and a four-element entry
  behaves identically to one whose fifth element is `"typst"`. The built-in `"typst"` key is
  resolved by the same rule as any declared key rather than being special-cased: it falls back to
  today's global `typst_template` / `typst_package` / `typst_template_function` /
  `typst_template_mapping` configuration, or the bundled default template when none of those is
  set — so a `conf.py` that declares no registry keeps working unchanged.

### Changed

- **Breaking: the `<srcdir>/base.typ` shadow-template route moved to
  `<srcdir>/_typst/base.typ` (OUT-04).** The reason, in one clause: the resolved template's
  parent directory is now copied wholesale to the output as that registry key's bundle, so it
  must be a real bundle directory and not the whole source tree. If your project still has a
  `<srcdir>/base.typ`, move it to `<srcdir>/_typst/base.typ`. If you do nothing, the build
  silently typesets with the bundled default template instead of your file — there is **no
  build-time warning** for this relocation, so this changelog entry is the only place it is
  announced.

- **Breaking: template layout is now validated before anything is written (WR-01, CR-01).** The
  reason, in one clause: the resolved template's parent directory is copied wholesale to the
  output as that registry key's bundle, so a template inside a directory Sphinx already treats
  as its own would republish that directory into public build output. Three configurations now
  stop the build: (a) a used registry key whose resolved template bundle directory is, contains,
  or is contained by any entry of Sphinx's `templates_path`; (b) a resolved template whose parent
  directory is the source directory itself or an ancestor of it — now caught before any file is
  written rather than at the end of the build; (c) a declared registry key differing from the
  built-in key only by case. Move the Typst template into a directory that is not on
  `templates_path` — this project uses `_typst/` — and update `typst_template` /
  `typst_document_templates` to match; Sphinx's own `templates_path` directory keeps its own
  meaning and can stay in place, which is what this repository's own documentation build does. If
  you do nothing, the build fails with a message naming the offending registry key, its resolved
  bundle directory, and the colliding entry — this is a hard failure by design: the rejected
  alternative, warning and skipping that key's bundle copy, leaves the wrapper importing a
  template file that was never written, so the emitted `.typ` tree cannot compile while the build
  reports success.

- **Breaking: every used template's bundle is now copied to its own directory under the output
  tree, and an explicit asset list no longer decides what reaches it (OUT-04, OUT-05, OUT-06,
  OUT-07, BLD-05, BLD-06).** v0.8.x wrote one shared template file, `_template.typ`, at the
  output root; v0.9.0 copies each used registry key's whole template bundle — the resolved
  template's parent directory — wholesale to `<outdir>/_template/<key>/<file>`, with the
  built-in `"typst"` key copied by the identical rule. If your template references an asset by a
  relative path (an `#image("logo.png")`, a partial `#import`), that asset must now live inside
  the template's own bundle directory — anywhere else, it will not reach the output.

### Fixed

- **A cross-reference to an absent target no longer links to a same-spelled decoy (XREF-05).**
  Two docnames that sanitized to the same Typst label used to let a reference whose real target
  document was absent from the compiling master resolve to the other, wrong document instead of
  degrading to plain text as an absent target always should. Note in passing: the fix makes label
  sanitization injective by re-escaping a literal occurrence of the sanitizer's own `_u<hex>_`
  escape token, so the emitted label name changes for an identifier that literally spells that
  token — the only such name in this repository is one test fixture's docname. PDF appearance is
  otherwise unchanged; only the label name in the emitted `.typ` output and the corresponding link
  destination name in the PDF move. Not a breaking change.

- **A document name containing `#` or `>` can no longer collide two include-edge keys (BLD-07).**
  Two structurally different include edges whose docnames contained one of those characters could
  previously derive the identical key, letting a state guard that should have stayed dark fire and
  duplicate or substitute a document's content in the compiled output. Document names without
  either character produce byte-identical keys, so nothing changes for an ordinary project.

- **An include chain deeper than this project's own bound now stops the build with a named error
  instead of a raw Python traceback (BLD-08).** An include chain deeper than the module's bound
  (500 — two orders of magnitude beyond any real documentation tree) now raises a
  `sphinx.errors.ExtensionError` naming the depth reached and the offending chain, instead of
  escaping as an uncaught interpreter `RecursionError`.

- **A driveless-absolute Windows image URI is classified like its sibling (BLD-09).** An absolute
  image URI written by a third-party extension in the driveless Windows shape (or the UNC shape)
  now reaches the relocate-and-warn path on Python 3.13, where it was previously left untouched —
  which mattered because an untouched rooted URI reached the image copy step, whose platform-native
  destination join discards the output directory for a rooted path.

- **Two escaping images sharing a basename no longer collapse onto one file (IMG-03).** Two
  absolute image URIs in different directories that share a filename and both fall outside the
  doctree directory used to collide onto one relocated file, so one image silently replaced the
  other. The user-visible consequence: the relocated file's emitted name now carries a short
  digest prefix ahead of the original filename, so the two images keep separate files.

### Removed

- **Breaking:** the `typst_template_assets` config value is removed (CONF-19) — every used
  template's bundle directory is now copied wholesale to the output, so an explicit asset list is
  no longer needed to select what reaches it; see the `### Changed` bundle-relocation entry above
  for what replaces it. Delete `typst_template_assets` from your `conf.py`; if you leave it set, a
  `config-inited` warning names the value and explains the wholesale copy, rather than the list
  being silently ignored — unlike v0.7.1's `typst_authors` removal, this one ships with a warning
  shim.

### Verified

- No new **runtime** dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.
```

Command: `uv run python scripts/extract_changelog_section.py 9.9.9`

Exit code: `1`

stdout: (empty)

stderr (verbatim):

```
No '## [9.9.9]' section found in the CHANGELOG. Add a curated entry for this version before releasing.
```

**This is the empty-input edge case (category: empty, REL-08) the phase resolves explicitly.**
`release.yml`'s `validate` job runs the first form (`extract_changelog_section.py 0.9.0`) and fails
the whole release before `build` or `publish-pypi` if the section is missing or its body is empty;
the second form, run here against `9.9.9` — a version with no CHANGELOG section — is the control
proving the extractor really does reject that state with a non-zero exit and a named-version stderr
message, rather than silently returning an empty string that a shell pipeline might swallow.

## Breaking-mark census (D-01)

Command:

```
awk '/^## \[0\.9\.0\]/{f=1;next} /^## \[0\.8\.0\]/{f=0} f' CHANGELOG.md | grep -n '\*\*Breaking'
```

Output:

```
28:- **Breaking: the `<srcdir>/base.typ` shadow-template route moved to
37:- **Breaking: template layout is now validated before anything is written (WR-01, CR-01).** The
55:- **Breaking: every used template's bundle is now copied to its own directory under the output
102:- **Breaking:** the `typst_template_assets` config value is removed (CONF-19) — every used
```

Four bullets, identified:

1. **Line 28 — the promoted OUT-04 relocation.** The `<srcdir>/base.typ` shadow-template route
   moved to `<srcdir>/_typst/base.typ`, promoted substantially as written from `## [Unreleased]`.
   Migration sentence: "If your project still has a `<srcdir>/base.typ`, move it to
   `<srcdir>/_typst/base.typ`."

2. **Line 37 — the promoted WR-01/CR-01 pre-write validation.** Three configurations now stop the
   build before any file is written, promoted substantially as written from `## [Unreleased]`.
   Migration sentence: "Move the Typst template into a directory that is not on `templates_path`
   — this project uses `_typst/` — and update `typst_template` / `typst_document_templates` to
   match."

3. **Line 55 — the newly authored output relocation.** The `_template.typ` → per-key bundle
   directory move — one of the two ROADMAP SC#2-named changes, absent from the file entirely
   before this plan. Migration sentence: "If your template references an asset by a relative path
   (an `#image("logo.png")`, a partial `#import`), that asset must now live inside the template's
   own bundle directory — anywhere else, it will not reach the output."

4. **Line 102 — the newly authored `typst_template_assets` removal.** The second ROADMAP
   SC#2-named change, authored as a `### Removed` bullet per D-03. Migration sentence: "Delete
   `typst_template_assets` from your `conf.py`; if you leave it set, a `config-inited` warning
   names the value and explains the wholesale copy, rather than the list being silently ignored."

## Section census (D-02, D-03, D-05)

Command (the `## [0.9.0]` section):

```
awk '/^## \[0\.9\.0\]/{f=1;next} /^## \[0\.8\.0\]/{f=0} f' CHANGELOG.md | grep -n '^### '
```

Output:

```
13:### Added
26:### Changed
64:### Fixed
100:### Removed
110:### Verified
```

`### Removed` exists (D-03) and `### Verified` carries its standing three items with wording
unchanged from `## [0.8.0]` / `## [0.7.1]` / `## [0.7.0]` (D-05).

Command (the residual `## [Unreleased]` block):

```
awk '/^## \[Unreleased\]/{f=1;next} /^## \[0\.9\.0\]/{f=0} f' CHANGELOG.md | grep -n '^### '
```

Output:

```
2:### Planned for Future Releases
```

`## [Unreleased]` now holds exactly one heading — `### Planned for Future Releases` — with its
seven prior `### Changed` / `### Fixed` bullets promoted into `## [0.9.0]` (D-02).

## Tail link block

Command: `tail -25 CHANGELOG.md`

Output:

```
---

[0.9.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.0
[0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
[0.7.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.0
[0.6.5]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.5
[0.6.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4
[0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3
[0.6.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
[0.6.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.1
[0.6.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.0
[0.5.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0
[0.4.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.4
[0.4.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.3
[0.4.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.2
[0.4.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.1
[0.4.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.0
[0.3.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.3.0
[0.2.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.2
[0.2.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.1
[0.2.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.0
[0.1.0b1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.1.0b1
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD
```

The block was already complete before this plan ran — no historical release line was missing and
none was repaired (the earlier CONTEXT claim to that effect was retracted at planning time, per
`57-CONTEXT.md`); the change made here is the routine insert-plus-advance described in Task 2 and
nothing more: one `[0.9.0]:` line inserted immediately above the previous topmost `[0.8.0]:` line,
and `[Unreleased]`'s compare base advanced from `v0.8.0...HEAD` to `v0.9.0...HEAD`, with
`[Unreleased]` staying the last line of the block.

## Published-page gate

Command: `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v`

Transcript:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7c8226c607f8f053/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7c8226c607f8f053
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 6 items

tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_delegates_to_changelog_md PASSED [ 16%]
tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_carries_no_hand_maintained_release_history PASSED [ 33%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_carries_every_release PASSED [ 50%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_has_one_changelog_heading PASSED [ 66%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_build_emits_no_changelog_warnings PASSED [ 83%]
tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf PASSED [100%]

============================== 6 passed in 3.83s ===============================
```

JUnit `testsuite` element attributes (from a separate `--junit-xml` run of the same command):

```
<testsuite name="pytest" errors="0" failures="0" skipped="0" tests="6" time="3.777" timestamp="2026-08-17T00:41:06.858311+09:00" hostname="Yuta-PC">
```

`skipped="0"`, `failures="0"`, `errors="0"`. The skip count is explicitly `0` because
`TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf` are marked
`@pytest.mark.slow` and gated on `myst_parser` (docs extra) / `typst` (typst-py) availability — a
`dev`-only environment would silently skip both build-driving classes and report a green run that
proved nothing about the published page actually carrying the new release. Running with
`--extra dev --extra docs` (both installed in this worktree, see `pdf.py`'s `typst-py` dependency
in the `dev` extra) forces both classes to execute for real.

## D-09 — what is deliberately NOT in this section

`54.1-REVIEW.md` WR-02 measured that the pre-write template-layout validation resolves
`templates_path` against the source directory (`self.srcdir`) rather than the config directory
(`confdir`), so a project using `-c`/`--confdir` still walks into the republication hole the
validation is meant to close. The promoted `## [0.9.0]` bullet's claim that "template layout is
now validated before anything is written" therefore reads as unconditional even though it is not
true for that one narrow project shape. The owner decided, with the reviewer's own recommended
minimum remediation (a CHANGELOG carve-out sentence) explicitly on the table, that this section
ships with no scoping clause and no `### Known Limitations` section — the wording is left exactly
as promoted. The decline is recorded here and carried forward into `57-HANDOFF.md` (plan 57-09),
which is the artifact of record for it; this evidence file does not restate it as a defect of this
plan's own execution, since the plan's job was to leave the wording alone, not to fix WR-02.

## Human check owed

The editorial quality of the `## [0.9.0]` section — that it reads as curated prose rather than a
generated dump — is listed as a Manual-Only verification in `57-VALIDATION.md` and is discharged at
end-of-phase UAT against the pasted extractor output in `## SC#2` above, not by any assertion in
this phase.
